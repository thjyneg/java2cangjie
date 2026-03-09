---
name: using-java2cangjie
description: Use when translating Java projects to Cangjie language, configuring translation environment, fixing translation errors, or generating translation reports
---

# Java to Cangjie Translation System

A comprehensive skill system for translating Java projects to Cangjie language using the j2cj tool with post-translation error correction and testing.

## Overview

This skill provides a complete end-to-end workflow for Java to Cangjie translation, including:

- Environment setup and configuration
- Project translation (module/project/domain modes)
- Error analysis and documentation lookup
- Automated error fixing with dependency analysis
- Compilation and testing
- Comprehensive reporting

## Translation Workflow

The translation process follows these steps:

1. **Setup** - Configure environment variables and verify tools
2. **Translate** - Execute j2cj translation
3. **Analyze** - Analyze translation errors and create modification plan
4. **Confirm** - Get user approval for modifications
5. **Fix** - Fix errors iteratively with dependency analysis
6. **Test** - Compile and test the Cangjie code
7. **Report** - Generate comprehensive translation report

## Quick Start

### Basic Translation

To translate a Java project:

```bash
# Step 1: Setup environment
Use java2cangjie-setup skill

# Step 2: Translate project
Use java2cangjie-translate skill

# Step 3: Analyze errors
Use java2cangjie-analyze skill

# Step 4: Confirm modifications
Use java2cangjie-confirm skill

# Step 5: Fix errors
Use java2cangjie-fix skill

# Step 6: Test code
Use java2cangjie-test skill

# Step 7: Generate report
Use java2cangjie-report skill
```

### Translation Modes

The system supports three translation modes:

1. **Module Mode** - Translate a single module
2. **Project Mode** - Translate an entire project
3. **Domain Mode** - Translate multiple projects in a domain

## Environment Configuration

### Required Tools

- **JDK 8+** - For compiling Java projects
- **JDK 17+** - Required by j2cj tool
- **j2cj tool** - Java to Cangjie translator
- **cjpm** - Cangjie package manager

### Optional Environment Variables

Configure these variables in `.env` file or system environment:

1. `JDK_PATH_PROJECT` - JDK path for project compilation (default: system java)
2. `JDK_PATH_J2CJ` - JDK 17 path for j2cj tool (default: system java)
3. `J2CJ_TOOL_PATH` - j2cj tool installation path (default: ./skills/java2cangjie/translate/j2cj_tool)

### Verification

Verify your environment setup:

```bash
# Check JDK
java -version

# Check j2cj tool
ls $J2CJ_TOOL_PATH/j2cj.jar

# Check cjpm
cjpm --version
```

## Skill Orchestration

### Main Skill: using-java2cangjie

This is the entry point skill that orchestrates all translation steps.

### Sub-Skills

1. **java2cangjie-setup** - Environment setup and configuration
2. **java2cangjie-translate** - Execute j2cj translation
3. **java2cangjie-analyze** - Analyze translation errors
4. **java2cangjie-confirm** - User confirmation step
5. **java2cangjie-fix** - Fix translation errors
6. **java2cangjie-test** - Test Cangjie code
7. **java2cangjie-report** - Generate translation report

### Skill Invocation Order

The skills should be invoked in this order:

```
using-java2cangjie (main)
  ↓
java2cangjie-setup
  ↓
java2cangjie-translate
  ↓
java2cangjie-analyze
  ↓
java2cangjie-confirm
  ↓
java2cangjie-fix
  ↓
java2cangjie-test
  ↓
java2cangjie-report
```

## TodoWrite Task Management

Use TodoWrite to track the overall translation workflow progress and enable session resumption.

### Creating Workflow TODO List

When starting a new translation, create a high-level TODO list for all 7 steps:

```javascript
TodoWrite({
  "todos": [
    {"content": "Setup environment", "status": "pending", "activeForm": "Setting up environment"},
    {"content": "Execute j2cj translation", "status": "pending", "activeForm": "Executing j2cj translation"},
    {"content": "Analyze translation errors", "status": "pending", "activeForm": "Analyzing translation errors"},
    {"content": "Confirm modification plan with user", "status": "pending", "activeForm": "Confirming modification plan"},
    {"content": "Fix translation errors iteratively", "status": "pending", "activeForm": "Fixing translation errors"},
    {"content": "Compile and test Cangjie code", "status": "pending", "activeForm": "Compiling and testing code"},
    {"content": "Generate translation report", "status": "pending", "activeForm": "Generating translation report"}
  ]
})
```

### Updating Progress

Mark each step as `in_progress` when starting, and `completed` when done. Only ONE task should be `in_progress` at any time.

```javascript
// When starting a step
TodoWrite({
  "todos": [
    {"activeForm": "Setting up environment", "content": "Setup environment", "status": "in_progress"},
    {"activeForm": "Executing j2cj translation", "content": "Execute j2cj translation", "status": "pending"},
    // ... other steps remain pending
  ]
})

// When completing a step
TodoWrite({
  "todos": [
    {"activeForm": "Setting up environment", "content": "Setup environment", "status": "completed"},
    {"activeForm": "Executing j2cj translation", "content": "Execute j2cj translation", "status": "pending"},
    // ... remaining steps
  ]
})
```

### Session Resumption

When resuming from a previous session:

1. Check for checkpoint file at `<output_dir>/.java2cangjie_checkpoint.md`
2. Read the checkpoint to determine current progress
3. Create TodoWrite with appropriate statuses based on checkpoint
4. Continue from the first non-completed step

```javascript
// Example: Resuming mid-workflow
TodoWrite({
  "todos": [
    {"activeForm": "Setting up environment", "content": "Setup environment", "status": "completed"},
    {"activeForm": "Executing j2cj translation", "content": "Execute j2cj translation", "status": "completed"},
    {"activeForm": "Analyzing translation errors", "content": "Analyze translation errors", "status": "completed"},
    {"activeForm": "Confirming modification plan", "content": "Confirm modification plan with user", "status": "completed"},
    {"activeForm": "Fixing translation errors", "content": "Fix translation errors iteratively", "status": "in_progress"},
    {"activeForm": "Compiling and testing code", "content": "Compile and test Cangjie code", "status": "pending"},
    {"activeForm": "Generating translation report", "content": "Generate translation report", "status": "pending"}
  ]
})
```

## Key Features

### 1. Dependency-Aware Fixing

The system analyzes file dependencies and fixes errors in bottom-up order to ensure successful compilation.

### 2. Documentation-Driven Research

All error fixes are based on Cangjie API documentation and sample code, ensuring correctness.

### 3. Iterative Improvement

The system iteratively fixes errors until all compilation issues are resolved.

### 4. Comprehensive Reporting

The system generates detailed reports including translation statistics, error analysis, and fix recommendations.

## Documentation Resources

- Cangjie Language Documentation: `java2cangjie/fix/docs/`
- j2cj Tool Documentation: `java2cangjie/translate/j2cj_tool/`

## When to Use This Skill

Use this skill system when:

- Translating a Java project to Cangjie
- Configuring the translation environment
- Fixing translation errors
- Generating translation reports
- Testing translated Cangjie code

## Skill Invocation

To use this skill system, invoke the appropriate sub-skill based on your current task:

- **java2cangjie-setup** - Use when setting up the translation environment
- **java2cangjie-translate** - Use when translating Java code
- **java2cangjie-analyze** - Use when analyzing translation errors
- **java2cangjie-confirm** - Use when confirming modifications
- **java2cangjie-fix** - Use when fixing translation errors
- **java2cangjie-test** - Use when testing translated code
- **java2cangjie-report** - Use when generating reports

## Best Practices

1. Always run setup first to ensure environment is properly configured
2. Follow the skill invocation order for best results
3. Review the analyze output before confirming modifications
4. Run test after fixing to verify compilation
5. Generate report for documentation and review

## Example Workflow

```bash
# User: "Translate my Java project to Cangjie"
# Assistant: Invoke setup skill
# Setup: Configure environment
# Assistant: Invoke translate skill
# Translate: Execute translation
# Assistant: Invoke analyze skill
# Analyze: Analyze errors
# Assistant: Invoke confirm skill
# Confirm: Get user approval
# Assistant: Invoke fix skill
# Fix: Fix errors
# Assistant: Invoke test skill
# Test: Compile and test
# Assistant: Invoke report skill
# Report: Generate report
```

## Troubleshooting

### Common Issues

1. **JDK not found** - Ensure JDK is installed and JAVA_HOME is set
2. **j2cj tool not found** - Set J2CJ_TOOL_PATH to correct location
3. **Compilation errors** - Use fix skill to resolve errors
4. **Missing dependencies** - Check project structure and dependencies

### Getting Help

For specific issues, invoke the appropriate sub-skill for detailed guidance.
