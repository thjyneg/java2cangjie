---
name: using-java2cangjie
description: Use when translating Java projects or source files to Cangjie language, fixing translation errors, or configuring Java to Cangjie translation environment
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Java to Cangjie Translation System

Pure AI translation system with incremental dependency-driven strategy. No external tools required.

## Available Skills

- **java2cangjie-translate** - Use when translating Java source code to Cangjie language
- **java2cangjie-fix** - Use when fixing compilation errors in translated Cangjie code
- **java2cangjie-report** - Use when generating translation reports

## Claude Code Workflow (recommended)

**Primary command:** Use `/j2c-translate` slash command for full translation workflow

```
/j2c-translate --java-path /path/to/java/src --output-dir ./j2cjgenerated --max-batch-size 3
```

This command:
1. Runs `scripts/analyze_deps.py` for dependency analysis and batch planning
2. Initializes output structure with `cjpm.toml`
3. Guides through incremental translation following dependency DAG
4. Manages state file (`/.java2cangjie_state.json`)
5. Handles compilation errors with automated fix attempts
6. Generates final report

**Manual workflow:** Use `java2cangjie-translate` skill directly (slash command provides automation)

## OpenCode Plugin Tools (OpenCode only)

- `analyze_project(javaPath)` - Scan Java project, build dependency DAG, return batch plan
- `next_batch()` - Get next batch of files ready for translation
- `mark_complete(batchId, outputFiles)` - Mark batch as compiled successfully
- `mark_blocked(batchId, reason)` - Mark batch as failed after max retries
- `translation_status()` - Get current progress

## When to Use

Use when user requests:
- Translating a Java project to Cangjie
- Fixing errors in translated Cangjie code
- Analyzing Java-to-Cangjie compatibility issues
- Generating translation reports

## Quick Start

**For new translation projects (Claude Code):**
1. Run `/j2c-translate --java-path <path>` command
2. Follow the guided workflow through analysis, translation, and fixing

**For error fixing on existing translations:**
1. Run `cjpm build 2>&1` to capture errors
2. Invoke `java2cangjie-fix` skill directly

## Key Resources

- Cangjie skills (documentation): `cangjie-std`, `cangjie-lang-features`, `cangjie-stdx`, `cangjie-toolchains`, `cangjie-regulations`, `cangjie-original-docs`
- Checkpoint template: `templates/checkpoint.md`

## Available Agents

- **cangjie-engineer** - Use for writing, debugging, or building Cangjie code. Expert in Cangjie syntax, std library, and cjpm. Delegating translation output to this agent ensures idiomatic Cangjie code.
- **translation-reviewer** - Use for reviewing translated code quality against original Java source.
- **error-fixer** - Use for fixing compilation errors by looking up documentation.

## Available Cangjie Skills

- **cangjie-lang-features** - Core language features: syntax, generics, concurrency, error handling
- **cangjie-std** - Standard library quick reference: types, collections, IO, filesystem, testing
- **cangjie-stdx** - Extended standard library: JSON, configuration, encoding
- **cangjie-toolchains** - Toolchain docs: cjc, cjdb, cjfmt, cjlint, cjcov, cjprof
- **cangjie-regulations** - Project conventions: structure, naming, formatting, testing best practices
- **cangjie-original-docs** - Full original documentation fallback

## Workflow Overview

```
New project:  translate → (compile errors?) → fix → report
Resume:       check state → next batch → continue
Delegate:     Use cangjie-engineer for complex Cangjie code generation tasks
```

## Output Convention

All translated code goes to `<java_project>/j2cjgenerated/`, preserving original package structure.
