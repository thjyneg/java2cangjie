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

## TodoWrite Task Management

Use TodoWrite to track translation progress and enable session resumption.

### Creating the TODO List

When starting translation, create a TODO list based on the translation mode:

**Module Mode:**
```javascript
TodoWrite({
  "todos": [
    {"content": "Prepare module translation environment", "status": "pending", "activeForm": "Preparing module environment"},
    {"content": "Generate classpath from project dependencies", "status": "pending", "activeForm": "Generating classpath"},
    {"content": "Execute j2cj translation command", "status": "pending", "activeForm": "Executing j2cj translation"},
    {"content": "Verify generated Cangjie files", "status": "pending", "activeForm": "Verifying output files"}
  ]
})
```

**Project Mode:**
```javascript
TodoWrite({
  "todos": [
    {"content": "Parse pom.xml for module list", "status": "pending", "activeForm": "Parsing pom.xml"},
    {"content": "Prepare all modules for translation", "status": "pending", "activeForm": "Preparing modules"},
    {"content": "Translate modules sequentially", "status": "pending", "activeForm": "Translating modules"},
    {"content": "Verify all translation results", "status": "pending", "activeForm": "Verifying results"}
  ]
})
```

**Domain Mode:**
```javascript
TodoWrite({
  "todos": [
    {"content": "Scan domain directory for projects", "status": "pending", "activeForm": "Scanning domain directory"},
    {"content": "Prepare all projects for translation", "status": "pending", "activeForm": "Preparing projects"},
    {"content": "Translate all projects", "status": "pending", "activeForm": "Translating projects"},
    {"content": "Generate translation summary", "status": "pending", "activeForm": "Generating summary"}
  ]
})
```

### Updating Status During Execution

Update the TODO status as each step progresses. Only ONE task should be `in_progress` at any time.

```javascript
// Mark step as in_progress before executing
TodoWrite({
  "todos": [
    {"activeForm": "Preparing module environment", "content": "Prepare module translation environment", "status": "in_progress"},
    {"activeForm": "Generating classpath", "content": "Generate classpath from project dependencies", "status": "pending"},
    // ...
  ]
})

// After successful completion, mark as completed
TodoWrite({
  "todos": [
    {"activeForm": "Preparing module environment", "content": "Prepare module translation environment", "status": "completed"},
    {"activeForm": "Generating classpath", "content": "Generate classpath from project dependencies", "status": "in_progress"},
    // ...
  ]
})
```

### Tracking Module Progress (Project/Domain Mode)

For multiple modules, expand the TODO list with sub-tasks:

```javascript
// After identifying modules
TodoWrite({
  "todos": [
    {"activeForm": "Parsing pom.xml", "content": "Parse pom.xml for module list", "status": "completed"},
    {"activeForm": "Preparing modules", "content": "Prepare all modules for translation", "status": "completed"},
    {"activeForm": "Translating common module", "content": "Translate module: common", "status": "in_progress"},
    {"activeForm": "Translating service module", "content": "Translate module: service", "status": "pending"},
    {"activeForm": "Translating web module", "content": "Translate module: web", "status": "pending"},
    {"activeForm": "Verifying results", "content": "Verify all translation results", "status": "pending"}
  ]
})
```

### Session Resumption

To resume an interrupted translation:

1. Check `<output_dir>/.java2cangjie_checkpoint.md` for saved progress
2. Read the checkpoint file to determine which steps are completed
3. Create TodoWrite with appropriate statuses based on checkpoint
4. Continue from the first non-completed step

```javascript
// Example: Resuming mid-translation
TodoWrite({
  "todos": [
    {"activeForm": "Preparing module environment", "content": "Prepare module translation environment", "status": "completed"},
    {"activeForm": "Generating classpath", "content": "Generate classpath from project dependencies", "status": "completed"},
    {"activeForm": "Executing j2cj translation", "content": "Execute j2cj translation command", "status": "in_progress"},
    {"activeForm": "Verifying output files", "content": "Verify generated Cangjie files", "status": "pending"}
  ]
})
```

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup (prerequisite)
- **java2cangjie-analyze** - Analyze translation errors (next step)
- **java2cangjie-confirm** - Confirm modifications
- **java2cangjie-fix** - Fix translation errors
- **java2cangjie-test** - Test Cangjie code
- **java2cangjie-report** - Generate translation report
