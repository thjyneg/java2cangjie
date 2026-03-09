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

## Usage

Execute translation directly in the Java project directory:

```bash
cd <java_project_directory>
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py
```

The script will automatically:
- Find all Java files in the project
- Generate classpath from pom.xml if available
- Execute j2cj translation
- Output results to `<project_root>/cangjie_output/`

## j2cj Tool Lookup Priority

The system follows this strict priority order:

1. **Environment Variable `J2CJ_TOOL_PATH`**
   - If set and valid, use this location
   - Verify: `ls $J2CJ_TOOL_PATH/j2cj.jar`

2. **Skill Directory**
   - `./skills/java2cangjie-translate/j2cj_tool/` (relative to project root)
   - Verify: `ls ./skills/java2cangjie-translate/j2cj_tool/j2cj.jar`

3. **If not found**: Stop execution immediately

## Output Directory Structure

```
<project_root>/cangjie_output/
├── <module_name>/
│   ├── src/
│   │   └── main/
│   │       └── cangjie/
│   │           ├── <package_path>/
│   │           │   └── *.cj         # Translated Cangjie files
│   │           └── adapters/        # Adapter files for unsupported features
│   └── build.cjpm                   # Cangjie build configuration
```

## Next Steps

After completing translation:

1. Use `java2cangjie-analyze` skill to identify and analyze translation errors
2. Use `java2cangjie-confirm` skill to review modification plan
3. Use `java2cangjie-fix` skill to fix errors
4. Use `java2cangjie-test` skill to compile and test
5. Use `java2cangjie-report` skill to generate final report

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup (prerequisite)
- **java2cangjie-analyze** - Analyze translation errors (next step)
- **java2cangjie-confirm** - Confirm modifications
- **java2cangjie-fix** - Fix translation errors
- **java2cangjie-test** - Test Cangjie code
- **java2cangjie-report** - Generate translation report
