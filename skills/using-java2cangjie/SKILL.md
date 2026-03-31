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

## Available Plugin Tools (OpenCode only)

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

For new translation projects:
1. Invoke `java2cangjie-translate` skill to start translation
2. The skill handles dependency analysis, batch planning, and incremental translation

For error fixing on existing translations:
1. Invoke `java2cangjie-fix` skill directly

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
