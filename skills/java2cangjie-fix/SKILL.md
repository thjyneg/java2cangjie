---
name: java2cangjie-fix
description: "Use when executing modifications, fixing translation errors iteratively, or implementing modify-compile loop after user confirmation"
---

# Java to Cangjie Translation - Step 5: Fix Errors

## Overview

This skill executes the approved modifications and attempts compilation. If errors occur, continue fixing iteratively with a maximum of 20 iteration rounds. The process uses dependency analysis to fix errors in the correct order.

## Prerequisites

Before using this skill, ensure:

- User has approved modification plan (use `java2cangjie-confirm` skill)
- All fixes are documented with references
- Output directory is accessible
- cjpm is available for compilation

## Core Process: Dependency Analysis → TodoWrite List → Sequential Loop

The fixing process follows this workflow:

1. **Analyze file dependencies** - Determine which files depend on which
2. **Create TODO list** - Use TodoWrite tool to track all fixes
3. **Execute fixes sequentially** - Fix in dependency order
4. **Compile after each fix** - Verify the fix works
5. **Iterate if needed** - Continue until all errors are resolved

## Core Principle: Modify-Compile Loop (Mandatory Execution)

**🔴 IRON RULE: Every modification must be immediately followed by compilation.**

Never batch multiple fixes without compiling. The modify-compile loop is mandatory:

```
Modify → Compile → Check → (if error) → Modify → Compile → ...
```

### Loop Rules (Cannot Be Violated)

1. **One fix at a time** - Fix one error, then compile
2. **Always compile** - Never skip compilation after a fix
3. **Check results** - Verify the fix resolved the error
4. **Max 20 iterations** - Stop after 20 rounds to prevent infinite loops
5. **Document everything** - Record every fix and result

## Compilation and Fixing Process

### 1. Analyze File Dependencies

Determine the correct order to fix files.

**Method 1: Analyze dependencies via import statements**

```bash
# Find all import statements
Grep: pattern="^import " path="<output_dir>" glob="*.cj"

# Example output:
# src/main/cangjie/com/example/Service.cj: import com.example.Model
# src/main/cangjie/com/example/Controller.cj: import com.example.Service
```

**Dependency graph:**
```
Controller.cj depends on Service.cj
Service.cj depends on Model.cj
Model.cj has no dependencies
```

**Fix order (bottom-up):**
1. Fix Model.cj first (no dependencies)
2. Fix Service.cj (depends on Model)
3. Fix Controller.cj (depends on Service)

**Method 2: Find all local package imports**

```bash
# Find local package imports
Grep: pattern="^import com\." path="<output_dir>" glob="*.cj"
```

### 2. Use TodoWrite Tool to Create TODO List

Create a comprehensive TODO list for all fixes:

```javascript
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "pending"
    },
    {
      "content": "Fix Service.cj: Replace currentTimeMillis",
      "id": "fix_2",
      "status": "pending"
    },
    {
      "content": "Fix Controller.cj: Handle nullable value",
      "id": "fix_3",
      "status": "pending"
    }
  ]
}
```

### 3. Identify `<--` Marked Unsupported Code

Find all files with j2cj markers for unsupported Java features:

```bash
# Find all files with <-- markers
Grep: pattern="<--" path="<output_dir>" glob="*.cj"
```

**View specific marker content:**

```bash
# Read file with context
Read: file_path="<output_dir>/path/to/file.cj"
```

### 4. Create adapters Folder

For unsupported Java features that cannot be directly translated:

```bash
# Create adapters directory
mkdir -p <output_dir>/src/main/cangjie/adapters
```

Create adapter files for unsupported features:

```cj
// adapters/JavaCollectionsAdapter.cj
package adapters

import std.collection.ArrayList

// Adapter for Java-specific collection methods
public class JavaCollectionsAdapter {
    public static func singletonList<T>(element: T): ArrayList<T> {
        let list = ArrayList<T>()
        list.add(element)
        return list
    }

    public static func emptyList<T>(): ArrayList<T> {
        return ArrayList<T>()
    }
}
```

### 5. Execute Fixes Sequentially

For each fix in the TODO list:

```javascript
// Mark fix as in_progress
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "in_progress"
    }
  ]
}
```

**Make the fix:**

```bash
# Edit the file
Edit: {
  "file_path": "<output_dir>/src/main/cangjie/com/example/Model.cj",
  "instruction": "Add import statement for ArrayList at the top of the file",
  "old_string": "package com.example

public class Model {",
  "new_string": "package com.example

import std.collection.ArrayList

public class Model {"
}
```

**Compile immediately:**

```bash
# Change to output directory
cd <output_dir>

# Compile
cjpm build

# Check exit code
echo $?
```

**Check result:**

```bash
# If exit code is 0, success
# If exit code is not 0, read error output
```

**Update TODO:**

```javascript
// If successful, mark as completed
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "completed"
    }
  ]
}

// If failed, keep as in_progress and add new task
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "in_progress"
    },
    {
      "content": "Fix new error: ...",
      "id": "fix_new_1",
      "status": "pending"
    }
  ]
}
```

### 6. Repeat Until All Fixes Complete

Continue the modify-compile loop until:

- All TODO items are completed, OR
- Maximum 20 iterations reached, OR
- User requests to stop

## Iteration Tracking

### Track Iteration Count

Keep track of iteration rounds:

```
Iteration 1: Fixed 3 errors, 39 remaining
Iteration 2: Fixed 5 errors, 34 remaining
Iteration 3: Fixed 4 errors, 30 remaining
...
Iteration 20: Fixed 2 errors, 28 remaining - MAX ITERATIONS REACHED
```

### Track Progress

After each iteration, report:

- Files modified in this iteration
- Errors fixed in this iteration
- Errors remaining
- New errors introduced (if any)

## Common Fix Patterns

### Pattern 1: Add Missing Import

**Error:**
```
error: Type 'ArrayList' not found
```

**Fix:**
```cj
// Add at top of file
import std.collection.ArrayList
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 2: Replace Method Call

**Error:**
```
error: Method 'currentTimeMillis' not found
```

**Fix:**
```cj
// Before
let time = System.currentTimeMillis()

// After
import std.time.Time
let time = Time.now()
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 3: Handle Nullability

**Error:**
```
error: Cannot assign nullable value to non-nullable type
```

**Fix:**
```cj
// Option 1: Use ?? operator
let result: String = getNullableString() ?? "default"

// Option 2: Use Option type
let result: Option<String> = getNullableString()
match (result) {
    case Some(value) => { /* use value */ }
    case None => { /* handle null */ }
}
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 4: Replace Unsupported Keyword

**Error:**
```
// <-- Java keyword 'synchronized' not supported -->
```

**Fix:**
```cj
// Before
synchronized(this) {
    // critical section
}

// After
import std.sync.Mutex

private let lock: Mutex = Mutex()

lock.lock()
try {
    // critical section
} finally {
    lock.unlock()
}
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

## Handling Compilation Errors

### Analyze Compilation Output

When compilation fails:

1. **Read the error output**
2. **Identify the error type**
3. **Locate the error in the code**
4. **Research the fix in documentation**
5. **Apply the fix**
6. **Compile again**

### Example Error Analysis

```bash
# Compilation error output
error: Type 'HashMap' not found in module 'std.collection'
  --> src/main/cangjie/com/example/Service.cj:42:15
   |
42 |     let map: HashMap<String, Int> = HashMap<String, Int>()
   |               ^^^^^^^ not found

# Analysis:
# - Error: Type 'HashMap' not found
# - Location: Service.cj:42
# - Cause: Missing import or wrong package

# Research:
# Search skills/java2cangjie-fix/docs/ for HashMap documentation

# Fix: Add import
import std.collection.HashMap

# Compile again
cjpm build
```

## When to Stop

### Success Criteria

Stop when:

- [ ] All TODO items are completed
- [ ] Compilation succeeds (exit code 0)
- [ ] No errors remain
- [ ] All tests pass (if available)

### Failure Criteria

Stop when:

- [ ] Maximum 20 iterations reached
- [ ] User requests to stop
- [ ] Cannot resolve specific errors
- [ ] Fixing one error causes more errors

## Next Steps

After fixing all errors:

1. Use `java2cangjie-test` skill to compile and test
2. Use `java2cangjie-report` skill to generate final report

## TODO管理和断点续传

本skill支持TODO列表管理和断点续传功能，确保错误修复过程可以追踪和恢复。本skill同时使用TodoWrite工具（用于实时跟踪）和SkillTodoManager（用于持久化）。

### 双重TODO管理

本skill采用双重TODO管理策略：

1. **TodoWrite工具** - 实时跟踪当前修复进度
2. **SkillTodoManager** - 持久化保存状态，支持断点续传

### 使用TODO管理器

```python
from skills.java2cangjie_common import SkillTodoManager

# 初始化TODO管理器
manager = SkillTodoManager(
    skill_name="java2cangjie-fix",
    session_id="unique_session_id"
)

# 定义错误修复工作流
fix_workflow = [
    {"id": "analyze_dependencies", "content": "分析文件依赖关系"},
    {"id": "create_fix_list", "content": "创建修复列表"},
    {"id": "execute_fixes", "content": "执行修复（修改-编译循环）"},
    {"id": "verify_compilation", "content": "验证编译结果"},
    {"id": "handle_remaining_errors", "content": "处理剩余错误"}
]

# 尝试恢复之前的进度
if manager.can_resume():
    print("从上次中断点继续错误修复...")
    manager.print_status()
    # 恢复到执行修复阶段
    manager.start_step("execute_fixes")
else:
    # 创建新的TODO列表
    manager.create_workflow_todos(fix_workflow)

# 执行修复步骤
while True:
    next_step = manager.get_next_pending_step()
    if not next_step:
        break

    # 开始执行步骤
    manager.start_step(next_step.id)
    try:
        # 执行步骤逻辑
        result = execute_fix_step(next_step.id)

        # 完成步骤
        manager.complete_step(next_step.id, result)
    except Exception as e:
        # 失败处理
        manager.fail_step(next_step.id, str(e))
        raise

# 打印最终状态
manager.print_status()
```

### 结合TodoWrite工具

在执行修复循环时，同时使用TodoWrite工具和SkillTodoManager：

```python
from skills.java2cangjie_common import SkillTodoManager

# 初始化持久化管理器
manager = SkillTodoManager("java2cangjie-fix", "session_123")

# 开始执行修复步骤
manager.start_step("execute_fixes")

# 获取修复列表（从分析阶段获取）
fixes = get_fix_list()

# 使用TodoWrite工具创建实时TODO列表
todo_list = []
for i, fix in enumerate(fixes):
    todo_list.append({
        "id": f"fix_{i}",
        "content": f"Fix {fix['file']}:{fix['line']} - {fix['description']}",
        "status": "pending"
    })

TodoWrite({"todos": todo_list})

# 执行修改-编译循环
for i, fix in enumerate(fixes):
    todo_id = f"fix_{i}"

    # 更新TodoWrite状态
    todo_list[i]["status"] = "in_progress"
    TodoWrite({"todos": todo_list})

    # 也更新持久化管理器
    manager.manager.create_todo(
        todo_id=todo_id,
        content=f"修复 {fix['file']}:{fix['line']}",
        status="in_progress",
        metadata={
            "file": fix["file"],
            "line": fix["line"],
            "error_type": fix["error_type"]
        }
    )

    # 执行修复
    try:
        apply_fix(fix)

        # 编译验证
        compile_result = compile_code()

        if compile_result.success:
            # 修复成功
            todo_list[i]["status"] = "completed"
            TodoWrite({"todos": todo_list})
            manager.manager.complete_step(todo_id, "修复成功")
        else:
            # 修复失败，记录错误
            todo_list[i]["status"] = "failed"
            TodoWrite({"todos": todo_list})
            manager.manager.fail_step(todo_id, compile_result.error)

    except Exception as e:
        # 修复异常
        todo_list[i]["status"] = "failed"
        TodoWrite({"todos": todo_list})
        manager.manager.fail_step(todo_id, str(e))

# 完成修复步骤
manager.complete_step("execute_fixes", f"完成 {len(fixes)} 个修复项")
```

### 断点续传示例

如果修复过程中断（如系统崩溃、网络问题等），下次启动时自动恢复：

```python
def main():
    manager = SkillTodoManager("java2cangjie-fix", "session_123")

    # 检查是否有未完成的修复
    if manager.can_resume():
        print("检测到未完成的错误修复")
        manager.print_status()

        # 获取已完成和待处理的修复
        completed = manager.manager.get_completed_todos()
        pending = manager.manager.get_pending_todos()
        failed = manager.manager.get_failed_todos()

        print(f"已完成: {len(completed)} 个修复")
        print(f"待处理: {len(pending)} 个修复")
        print(f"失败: {len(failed)} 个修复")

        # 从上次中断点继续
        resume_fixes(manager)
    else:
        # 全新开始
        start_new_fixes(manager)

    # 完成后清理状态
    manager.clear_state()
```

### TODO状态跟踪

错误修复过程中的关键检查点：

1. **analyze_dependencies** - 分析文件间的依赖关系
2. **create_fix_list** - 根据依赖顺序创建修复列表
3. **execute_fixes** - 执行修改-编译循环（最多20次迭代）
4. **verify_compilation** - 验证最终编译结果
5. **handle_remaining_errors** - 处理剩余的错误（如有）

每个修复项也会被单独跟踪：

- **fix_N** - 修复第N个错误
  - 状态：pending → in_progress → completed/failed
  - 元数据：文件路径、行号、错误类型、修复描述

### 迭代跟踪

记录每次修改-编译循环的迭代：

```python
# 在execute_fixes步骤中
manager.start_step("execute_fixes")
iteration = 0
max_iterations = 20

while iteration < max_iterations:
    iteration += 1

    # 记录迭代
    iteration_id = f"iteration_{iteration}"
    manager.manager.create_todo(
        todo_id=iteration_id,
        content=f"第 {iteration} 次迭代",
        status="in_progress",
        metadata={"iteration": iteration}
    )

    # 执行修复和编译
    errors = compile_and_fix()

    if not errors:
        # 所有错误已修复
        manager.manager.complete_step(iteration_id, "编译成功，无错误")
        break
    else:
        # 还有错误，继续迭代
        manager.manager.complete_step(iteration_id, f"剩余 {len(errors)} 个错误")

if iteration >= max_iterations:
    manager.manager.fail_step("execute_fixes", "达到最大迭代次数")

manager.complete_step("execute_fixes", f"完成 {iteration} 次迭代")
```

### 与TodoWrite工具的配合

| 功能 | TodoWrite工具 | SkillTodoManager |
|------|---------------|------------------|
| 实时显示 | ✅ 立即可见 | ⚠️ 需要查询 |
| 持久化 | ❌ 会话结束后丢失 | ✅ 永久保存 |
| 断点续传 | ❌ 不支持 | ✅ 支持 |
| 会话内跟踪 | ✅ 推荐 | ✅ 可选 |
| 跨会话恢复 | ❌ 不支持 | ✅ 支持 |

**最佳实践：**
- 在会话内使用TodoWrite工具实时显示进度
- 同时使用SkillTodoManager保存状态，支持断点续传
- 每次修复完成后更新两个系统

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup
- **java2cangjie-translate** - Execute translation
- **java2cangjie-analyze** - Analyze errors
- **java2cangjie-confirm** - Confirm modifications (prerequisite)
- **java2cangjie-test** - Test Cangjie code (next step)
- **java2cangjie-report** - Generate translation report
