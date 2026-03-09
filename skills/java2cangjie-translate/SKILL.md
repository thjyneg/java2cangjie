---
name: java2cangjie-translate
description: "Use when executing j2cj translation in module, project, or domain mode after environment setup is complete"
---

# Java to Cangjie Translation - Step 2: Execute Translation

## Overview

This skill executes the Java to Cangjie translation using the j2cj tool. The translation generates Cangjie code that may contain errors requiring manual correction in subsequent steps.

## Prerequisites

Before using this skill, ensure:

- Environment is configured (use `java2cangjie-setup` skill)
- Java source code is ready for translation
- Output directory is accessible

## Mandatory Requirement

**🔴 IMPORTANT: Always use the stable translation script `j2cj_module_translate_execute.py` instead of directly calling j2cj commands.**

The stable script provides:
- Automatic classpath generation
- Error handling and logging
- Multi-module support
- Status tracking

## Translation Modes

The system supports three translation modes:

### 1. Module Mode

Translate a single module or directory.

**Usage:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --module-path <module_path>
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path>
```

**Example:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --module-path ./src/main/java/com/example
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m ./src/main/java/com/example
```

**When to Use:**
- Translating a specific module
- Testing translation on a small subset
- Incremental translation

### 2. Project Mode

Translate an entire Java project with all modules (must contain pom.xml).

**Usage:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --project-path <project_path>
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -p <project_path>
```

**Example:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --project-path ./my-java-project
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -p ./my-java-project
```

**When to Use:**
- Translating a complete Maven project
- Projects with multiple modules
- Standard Maven projects with pom.xml

### 3. Domain Mode

Translate multiple projects in a domain directory.

**Usage:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --domain-path <domain_path>
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -d <domain_path>
```

**Example:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py --domain-path ./workspace
# or
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -d ./workspace
```

**When to Use:**
- Translating multiple related projects
- Batch translation
- Enterprise-scale translation
- Directory containing multiple Maven projects

## Script Features

The stable translation script provides:

- **Automatic classpath generation** - Analyzes project dependencies
- **Multi-module support** - Handles complex project structures
- **Error handling** - Comprehensive error logging
- **Progress tracking** - Real-time translation status
- **Skip mechanism** - Skips already translated modules
- **Result summary** - Detailed translation report

## Output Directory Structure

Translation output is organized as follows:

```
<output_dir>/
├── <module_name>/
│   ├── src/
│   │   └── main/
│   │       └── cangjie/
│   │           ├── <package_path>/
│   │           │   └── *.cj         # Translated Cangjie files
│   │           └── adapters/        # Adapter files for unsupported features
│   └── build.cjpm                   # Cangjie build configuration
```

## Translation Modes (j2cj Options)

### codestyle Mode (Recommended)

Preserves code structure and style.

**Advantages:**
- More readable output
- Preserves original formatting
- Easier to review

**Usage:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path> --mode codestyle
```

### semantic Mode

Focuses on semantic translation rather than style.

**Advantages:**
- More idiomatic Cangjie code
- Better performance characteristics
- May require more manual fixes

**Usage:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path> --mode semantic
```

## Advanced Options

### Classpath Configuration

**Automatic:**
The script automatically generates classpath from project structure.

**Manual:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path> --classpath <custom_classpath>
```

### Output Directory

**Default:** `./output`

**Custom:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path> --output <output_dir>
```

### Verbosity

**Detailed output:**
```bash
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path> --verbose
```

## Example Workflows

### Translate a Single Module

```bash
# 1. Setup environment (done once)
Use java2cangjie-setup skill

# 2. Translate module
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m ./src/main/java/com/example

# 3. Analyze errors
Use java2cangjie-analyze skill

# Continue with remaining steps...
```

### Translate a Complete Project

```bash
# 1. Setup environment
Use java2cangjie-setup skill

# 2. Translate project
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -p ./my-java-project

# 3. Analyze errors
Use java2cangjie-analyze skill

# Continue with remaining steps...
```

### Translate Multiple Projects

```bash
# 1. Setup environment
Use java2cangjie-setup skill

# 2. Translate domain
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -d ./workspace

# 3. Analyze errors
Use java2cangjie-analyze skill

# Continue with remaining steps...
```

## Expected Output

### Successful Translation

```
[INFO] Starting translation...
[INFO] Module: com.example
[INFO] Processing 15 Java files...
[INFO] Translation completed successfully
[INFO] Output: ./output/com.example/
[INFO] Statistics:
[INFO]   Java files: 15
[INFO]   Cangjie files: 15
[INFO]   Success rate: 100%
```

### Translation with Warnings

```
[INFO] Starting translation...
[INFO] Module: com.example
[INFO] Processing 15 Java files...
[WARNING] 3 files have unsupported features
[WARNING] See output files for details
[INFO] Translation completed with warnings
[INFO] Output: ./output/com.example/
```

## Common Issues and Solutions

### Issue: "Java file not found"

**Cause:** Incorrect module path

**Solution:**
1. Verify module path exists: `ls <module_path>`
2. Use absolute path if relative path fails
3. Check for typos in path

### Issue: "Cannot generate classpath"

**Cause:** Project structure not recognized

**Solution:**
1. Ensure project has standard structure (Maven/Gradle)
2. Provide custom classpath: `--classpath <path>`
3. Check if pom.xml or build.gradle exists

### Issue: "j2cj tool not found"

**Cause:** j2cj tool cannot be located

**🔴 MANDATORY: j2cj Tool Lookup Priority**

The system follows this strict priority order:

1. **First: Check Environment Variable `J2CJ_TOOL_PATH`**
   - If set and valid, use this location
   - Verify: `ls $J2CJ_TOOL_PATH/j2cj.jar`

2. **Second: Search in Skill Directory**
   - If environment variable not found or invalid, search in:
     - `./skills/java2cangjie-translate/j2cj_tool/` (relative to project root)
   - Verify: `ls ./skills/java2cangjie-translate/j2cj_tool/j2cj.jar`

3. **Third: Stop Execution**
   - If j2cj tool is not found in either location, **STOP immediately**
   - Do not proceed with translation

**Solution:**
1. Use `java2cangjie-setup` skill to configure environment
2. Verify j2cj.jar exists in one of these locations:
   - `$J2CJ_TOOL_PATH/j2cj.jar` (if environment variable is set)
   - `./skills/java2cangjie-translate/j2cj_tool/j2cj.jar` (default location)
3. If not found, either:
   - Set `J2CJ_TOOL_PATH` environment variable to correct location
   - Place `j2cj.jar` in `./skills/java2cangjie-translate/j2cj_tool/` directory

### Issue: "Insufficient memory"

**Cause:** Large project exceeds JVM memory

**Solution:**
1. Increase JVM heap size in script
2. Translate modules individually instead of entire project
3. Close other applications to free memory

## Post-Translation Steps

After translation completes:

1. **Review output directory** - Check generated files
2. **Analyze errors** - Use `java2cangjie-analyze` skill
3. **Fix errors** - Use `java2cangjie-fix` skill
4. **Test code** - Use `java2cangjie-test` skill
5. **Generate report** - Use `java2cangjie-report` skill

## Next Steps

After completing translation:

1. Use `java2cangjie-analyze` skill to identify and analyze translation errors
2. Use `java2cangjie-confirm` skill to review modification plan
3. Use `java2cangjie-fix` skill to fix errors
4. Use `java2cangjie-test` skill to compile and test
5. Use `java2cangjie-report` skill to generate final report

## TODO管理和断点续传

本skill支持TODO列表管理和断点续传功能，确保翻译过程可以追踪和恢复。

### 使用TODO管理器

```python
from skills.java2cangjie_common import SkillTodoManager

# 初始化TODO管理器
manager = SkillTodoManager(
    skill_name="java2cangjie-translate",
    session_id="unique_session_id"
)

# 定义翻译工作流（根据模式动态生成）
if translation_mode == "module":
    translate_workflow = [
        {"id": "prepare_module", "content": "准备模块翻译"},
        {"id": "generate_classpath", "content": "生成classpath"},
        {"id": "execute_translation", "content": "执行j2cj翻译"},
        {"id": "verify_output", "content": "验证翻译输出"}
    ]
elif translation_mode == "project":
    translate_workflow = [
        {"id": "parse_pom", "content": "解析pom.xml"},
        {"id": "prepare_modules", "content": "准备模块列表"},
        {"id": "translate_modules", "content": "翻译所有模块"},
        {"id": "verify_results", "content": "验证翻译结果"}
    ]
else:  # domain mode
    translate_workflow = [
        {"id": "scan_domain", "content": "扫描域目录"},
        {"id": "prepare_projects", "content": "准备项目列表"},
        {"id": "translate_projects", "content": "翻译所有项目"},
        {"id": "generate_summary", "content": "生成翻译摘要"}
    ]

# 尝试恢复之前的进度
if manager.can_resume():
    print("从上次中断点继续翻译...")
    manager.print_status()
else:
    # 创建新的TODO列表
    manager.create_workflow_todos(translate_workflow)

# 执行翻译步骤
while True:
    next_step = manager.get_next_pending_step()
    if not next_step:
        break

    # 开始执行步骤
    manager.start_step(next_step.id)
    try:
        # 执行步骤逻辑
        result = execute_translate_step(next_step.id, translation_mode)

        # 完成步骤
        manager.complete_step(next_step.id, result)
    except Exception as e:
        # 失败处理
        manager.fail_step(next_step.id, str(e))
        raise

# 打印最终状态
manager.print_status()
```

### 断点续传示例

翻译大型项目时可能需要很长时间，支持断点续传非常重要：

```python
def main():
    manager = SkillTodoManager("java2cangjie-translate", "session_123")

    # 检查是否有未完成的翻译
    if manager.can_resume():
        print("检测到未完成的翻译任务")
        manager.print_status()
        print("从上次中断点继续...")

        # 恢复执行
        resume_translation(manager)
    else:
        # 全新翻译
        start_new_translation(manager)

    # 完成后清理状态
    manager.clear_state()
```

### 跟踪模块翻译进度

对于项目模式和域模式，可以跟踪每个模块的翻译进度：

```python
# 在translate_modules步骤中
manager.start_step("translate_modules")
modules = get_module_list()

for i, module in enumerate(modules):
    module_id = f"module_{i}"
    manager.manager.create_todo(
        todo_id=module_id,
        content=f"翻译模块: {module['name']}",
        status="pending",
        metadata={"module_path": module["path"]}
    )

    # 翻译模块
    manager.manager.start_step(module_id)
    try:
        result = translate_single_module(module)
        manager.manager.complete_step(module_id, f"成功翻译 {result['file_count']} 个文件")
    except Exception as e:
        manager.manager.fail_step(module_id, str(e))

    # 显示进度
    if (i + 1) % 10 == 0:
        manager.print_status()

manager.complete_step("translate_modules", f"完成 {len(modules)} 个模块翻译")
```

### TODO状态跟踪

翻译过程中的关键检查点：

**模块模式:**
1. **prepare_module** - 准备模块翻译环境
2. **generate_classpath** - 生成项目依赖classpath
3. **execute_translation** - 执行j2cj翻译命令
4. **verify_output** - 验证生成的Cangjie文件

**项目模式:**
1. **parse_pom** - 解析Maven pom.xml文件
2. **prepare_modules** - 准备所有待翻译模块
3. **translate_modules** - 逐个翻译模块
4. **verify_results** - 验证所有翻译结果

**域模式:**
1. **scan_domain** - 扫描域目录中的项目
2. **prepare_projects** - 准备所有待翻译项目
3. **translate_projects** - 逐个翻译项目
4. **generate_summary** - 生成翻译摘要报告

每个步骤完成后会自动保存状态，支持断点续传。

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup (prerequisite)
- **java2cangjie-analyze** - Analyze translation errors (next step)
- **java2cangjie-confirm** - Confirm modifications
- **java2cangjie-fix** - Fix translation errors
- **java2cangjie-test** - Test Cangjie code
- **java2cangjie-report** - Generate translation report
