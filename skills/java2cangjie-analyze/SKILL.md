---
name: java2cangjie-analyze
description: "Use when analyzing j2cj translation errors, creating modification plans, or researching Cangjie APIs and syntax after translation completes"
---

# Java to Cangjie Translation - Step 3: Analyze Errors

## Overview

This skill analyzes errors and warnings in j2cj translation results, researches Cangjie documentation, and creates a detailed modification plan. All research must be based on Cangjie API documentation and sample code.

## Prerequisites

Before using this skill, ensure:

- Translation has been completed (use `java2cangjie-translate` skill)
- Output directory contains generated Cangjie files
- Cangjie documentation is accessible in `skills/java2cangjie-fix/docs/` directory

## First Step: Find j2cj-Marked Issues

### Find all j2cj-marked issues

Search for all files with j2cj error markers:

```bash
# Find all files with <-- markers
Grep: pattern="<--" path="<output_dir>" glob="*.cj"
```

### View specific marker content

Read files to understand the error context:

```bash
# Read file with line numbers
Read: file_path="<output_dir>/path/to/file.cj"
```

## Analysis Process

### 1. Categorize Errors

Auto-classify errors based on actual error patterns found. Different projects will have different error types and distributions.

**Process:**
1. Extract all unique error types from the failed compilation results
2. Group errors by type automatically (do not assume a fixed set of categories)
3. Create categories dynamically based on error patterns

**Example categories (actual categories will vary by project):**
- **Type not found** - Missing or incorrect type definitions
- **Method not found** - Missing or incorrect method calls
- **Syntax errors** - Invalid Cangjie syntax
- **Unsupported features** - Java features not supported by j2cj
- **Nullability issues** - Incorrect null handling
- **Import errors** - Missing or incorrect import statements
- **Package mapping** - Java package to Cangjie package conversion issues
- **API changes** - Cangjie API differs from Java equivalent
- **Type conversion** - Automatic type conversion failures
- **Access control** - Visibility modifier issues
- **Missing implementations** - Abstract class or interface implementations

**IMPORTANT:** The actual error categories depend on the project's specific code and dependencies. Always analyze the actual errors first, then create categories dynamically.

Prioritize based on:

- **Critical** - Blocks compilation (must fix first)
- **High** - Affects core functionality
- **Medium** - Affects non-critical features
- **Low** - Cosmetic or can be deferred

### 3. Document Findings

Create a detailed error list with:

- File path and line number
- Error type
- Error message
- Context code
- Suggested fix (if apparent)

## Mandatory Documentation Lookup Process

**🔴 MANDATORY: All error fixes must be based on Cangjie documentation. Never guess or assume.**

### Lookup Priority Order

Follow this 5-step process for each error:

#### Step 1: Search in Basic Type Documentation

Search in `skills/java2cangjie-fix/docs/extra/` for basic types.

**Example: Searching for ArrayList**

```bash
# Search for ArrayList type
Grep: pattern="ArrayList" path="skills/java2cangjie-fix/docs/extra/" glob="*.md"
```

**What to look for:**
- Type definition and usage
- Constructor signatures
- Common methods
- Code examples

#### Step 2: Search in Standard Library API Documentation

Search in `skills/java2cangjie-fix/docs/libs/std/` for standard library APIs.

**Example: Searching for ArrayList type**

```bash
# Search for ArrayList type
Grep: pattern="class ArrayList" path="skills/java2cangjie-fix/docs/libs/std/collection/"

# Search for add method
Grep: pattern="func add" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_api/"
```

**What to look for:**
- Complete API documentation
- Method signatures
- Parameter descriptions
- Return types
- Usage examples

#### Step 3: Search Sample Code

Find practical examples in sample documentation.

**Example: Searching for ArrayList usage**

```bash
# List all sample files
Glob: pattern="sample_*.md" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_samples/"

# Search for ArrayList in samples
Grep: pattern="ArrayList" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_samples/"
```

**What to look for:**
- Real-world usage patterns
- Best practices
- Common pitfalls
- Complete working examples

#### Step 4: Search in Language Manual

Search in `skills/java2cangjie-fix/docs/manual/` for language concepts.

**Example: Searching for generic syntax**

```bash
# Search for generic syntax
Grep: pattern="generic|<T>" path="skills/java2cangjie-fix/docs/manual/"
```

**What to look for:**
- Language syntax rules
- Type system details
- Best practices
- Design patterns

#### Step 5: Search Package Overview

Review package overview for context.

**Example: Collection package overview**

```bash
# Find package overview
Glob: pattern="*package_overview.md" path="skills/java2cangjie-fix/docs/libs/std/collection/"
```

**What to look for:**
- Package purpose and design
- Common use cases
- Related types and functions
- Design decisions

## Modification Plan Creation

### Plan Structure

Create a modification plan with:

1. **Error Summary**
   - Total error count
   - Error type distribution
   - Critical errors list

2. **Modification List**
   For each error:
   - File path and line number
   - Error description
   - Documentation reference
   - Proposed fix
   - Dependencies

3. **Execution Order**
   - List fixes in dependency order
   - Bottom-up approach (dependencies first)
   - Group related fixes

### Example Modification Plan

```markdown
# Modification Plan

## Error Summary
- Total errors: 42
- Type not found: 18
- Method not found: 12
- Nullability: 8
- Syntax: 4

## Critical Errors (Fix First)

1. **common/Constants.cj:15** - Type ArrayList not found
   - Documentation: skills/java2cangjie-fix/docs/extra/ArrayList.md
   - Fix: Add `import std.collection.ArrayList`
   - Dependencies: None

2. **service/UserService.cj:42** - Method currentTimeMillis not found
   - Documentation: skills/java2cangjie-fix/docs/libs/std/time/time_package_api/
   - Fix: Replace with `std.time.Time.now()`
   - Dependencies: None

## High Priority Errors

[... continue with remaining errors ...]

## Execution Order
1. Fix all import statements
2. Fix type definitions
3. Fix method calls
4. Fix nullability issues
5. Fix syntax errors
```

## Common Error Types and Solutions

### Type Not Found

**Error:**
```
error: Type 'ArrayList' not found
```

**Lookup Process:**
1. Search `skills/java2cangjie-fix/docs/extra/` for ArrayList
2. Search `skills/java2cangjie-fix/docs/libs/std/collection/` for ArrayList API
3. Find sample code using ArrayList

**Typical Solution:**
```cj
// Add import
import std.collection.ArrayList

// Or use full path
let list: std.collection.ArrayList<String> = std.collection.ArrayList<String>()
```

### Method Not Found

**Error:**
```
error: Method 'toString' not found in type 'Object'
```

**Lookup Process:**
1. Search documentation for target type
2. Find available methods in API docs
3. Check sample code for patterns

**Typical Solution:**
```cj
// Use String.valueOf
let str = String.valueOf(obj)

// Or implement custom toString
public override func toString(): String {
    return "custom string"
}
```

### Nullability Issues

**Error:**
```
error: Cannot assign nullable value to non-nullable type
```

**Lookup Process:**
1. Search `skills/java2cangjie-fix/docs/extra/Option.md` for Option type
2. Find sample code with null handling
3. Review language manual for null safety

**Typical Solution:**
```cj
// Use ?? operator
let result: String = getNullableString() ?? "default"

// Or use Option type
let result: Option<String> = getNullableString()
match (result) {
    case Some(value) => { /* use value */ }
    case None => { /* handle null */ }
}
```

### Unsupported Java Features

**Error Markers:**
```
// <-- Java keyword 'synchronized' not supported -->
// <-- Generic wildcard '? extends T' not supported -->
// <-- Java keyword 'instanceof' not supported -->
```

**Lookup Process:**
1. Search language manual for equivalent Cangjie features
2. Find sample code for similar patterns
3. Review package overview for alternatives

**Typical Solutions:**
- `synchronized` → Use `std.sync.Mutex`
- `instanceof` → Use `match` pattern matching
- Wildcards → Use specific types or constraints

## Next Steps

After completing analysis:

1. Use `java2cangjie-confirm` skill to present modification plan and get approval
2. Use `java2cangjie-fix` skill to execute modifications
3. Use `java2cangjie-test` skill to compile and test
4. Use `java2cangjie-report` skill to generate final report

## TODO管理和断点续传

本skill支持TODO列表管理和断点续传功能，确保错误分析过程可以追踪和恢复。

### 使用TODO管理器

```python
from skills.java2cangjie_common import SkillTodoManager

# 初始化TODO管理器
manager = SkillTodoManager(
    skill_name="java2cangjie-analyze",
    session_id="unique_session_id"
)

# 定义错误分析工作流
analyze_workflow = [
    {"id": "find_j2cj_markers", "content": "查找j2cj标记的错误"},
    {"id": "categorize_errors", "content": "分类错误类型"},
    {"id": "prioritize_errors", "content": "确定错误优先级"},
    {"id": "lookup_documentation", "content": "查找Cangjie文档"},
    {"id": "create_fix_plan", "content": "创建修复计划"}
]

# 尝试恢复之前的进度
if manager.can_resume():
    print("从上次中断点继续错误分析...")
    manager.print_status()
else:
    # 创建新的TODO列表
    manager.create_workflow_todos(analyze_workflow)

# 执行分析步骤
while True:
    next_step = manager.get_next_pending_step()
    if not next_step:
        break

    # 开始执行步骤
    manager.start_step(next_step.id)
    try:
        # 执行步骤逻辑
        result = execute_analyze_step(next_step.id)

        # 完成步骤
        manager.complete_step(next_step.id, result)
    except Exception as e:
        # 失败处理
        manager.fail_step(next_step.id, str(e))
        raise

# 打印最终状态
manager.print_status()
```

### 跟踪错误分析进度

对于大量错误，可以跟踪每个错误的分析进度：

```python
# 在categorize_errors步骤中
manager.start_step("categorize_errors")
errors = get_all_errors()

# 按类型分组
error_types = categorize_errors_by_type(errors)

for error_type, error_list in error_types.items():
    type_id = f"analyze_{error_type}"
    manager.manager.create_todo(
        todo_id=type_id,
        content=f"分析{error_type}类型错误 ({len(error_list)}个)",
        status="pending",
        metadata={"error_count": len(error_list)}
    )

    # 分析该类型错误
    manager.manager.start_step(type_id)
    try:
        analyzed = analyze_error_type(error_type, error_list)
        manager.manager.complete_step(type_id, f"完成 {len(analyzed)} 个错误分析")
    except Exception as e:
        manager.manager.fail_step(type_id, str(e))

manager.complete_step("categorize_errors", f"完成 {len(error_types)} 类错误分析")
```

### TODO状态跟踪

错误分析过程中的关键检查点：

1. **find_j2cj_markers** - 查找所有j2cj标记的错误
2. **categorize_errors** - 按类型分类错误
3. **prioritize_errors** - 确定错误优先级
4. **lookup_documentation** - 查找Cangjie文档和API
5. **create_fix_plan** - 创建详细的修复计划

每个步骤完成后会自动保存状态，支持断点续传。

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup
- **java2cangjie-translate** - Execute translation (prerequisite)
- **java2cangjie-confirm** - Confirm modifications (next step)
- **java2cangjie-fix** - Fix translation errors
- **java2cangjie-test** - Test Cangjie code
- **java2cangjie-report** - Generate translation report
