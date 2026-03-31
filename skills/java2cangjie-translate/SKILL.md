---
name: java2cangjie-translate
description: Use when translating Java source code to Cangjie language, starting a new translation project, or resuming an interrupted translation
---

# Java to Cangjie Translation - Execute

## Overview

Pure AI translation with incremental dependency-driven strategy. Translate Java source to Cangjie in small batches (1-3 files), compiling after each batch.

Output goes to `<java_project>/j2cjgenerated/`.

## OpenCode Environment (has plugin tools)

Use plugin tools for deterministic workflow control:

```
1. analyze_project(javaPath)        → dependency DAG + batch plan
2. next_batch()                     → next files to translate
3. translate batch via AI
4. cjpm build                       → compile verification
5. mark_complete() / mark_blocked() → track progress
6. Repeat from step 2
```

## Claude Code Environment (no plugin tools)

Manual workflow with equivalent logic:

```bash
# Step 1: Scan Java files
find <java_dir> -name "*.java" -type f

# Step 2: Build dependency graph
grep -rn "^import " <java_dir> --include="*.java" | grep -v "java\.\|javax\.\|org\."

# Step 3: Identify leaf files (no internal dependencies)
# Files whose imports don't reference other project classes = leaf nodes

# Step 4: Track progress in checkpoint file
# Use templates/checkpoint.md format
```

## Translation Loop

For each batch (1-3 files):

### 1. Read Java Source

Read the Java files in the current batch. Understand the class structure, methods, and dependencies.

### 2. Lookup Cangjie Documentation

**MANDATORY: Read relevant docs BEFORE translating.**

Use the Cangjie skills for documentation lookup:
1. `cangjie-std` → standard library types and APIs (collections, IO, filesystem, etc.)
2. `cangjie-lang-features` → language syntax, generics, concurrency, error handling
3. `cangjie-stdx` → extended library (JSON, encoding, configuration)
4. `cangjie-original-docs` → full original documentation fallback
5. `cangjie-regulations` → naming conventions and best practices

### 3. Translate Each File

Key mapping rules:

| Java | Cangjie |
|------|---------|
| `package com.example` | `package com.example` |
| `import java.util.ArrayList` | `import std.collection.ArrayList` |
| `ArrayList<E>` | `ArrayList<E>` (from std.collection) |
| `HashMap<K,V>` | `HashMap<K,V>` (from std.collection) |
| `null` | `None` or `?? default` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `throws` | No equivalent, use `Option` or `except` |
| `synchronized` | `Mutex` from std.sync |
| `instanceof` | `is` or `match` pattern |
| `System.out.println` | `println` |
| `String.format` | String interpolation `\${expr}` |
| `this.field` | `this.field` |
| `@Override` | No annotation needed |
| `interface` | `interface` |
| `abstract class` | `abstract class` |
| `T extends Comparable` | `T <: Comparable` |
| `void` | `Unit` or omit return type |

### 4. Write Output

Write Cangjie files preserving original package structure:

```
<java_project>/j2cjgenerated/
├── <module>/
│   ├── cjpm.toml
│   └── src/
│       └── <package_path>/
│           └── *.cj
```

For Maven projects, create `cjpm.toml` per module:

```toml
[package]
name = "<module-name>"
version = "0.1.0"
```

### 5. Compile

```bash
cd <java_project>/j2cjgenerated/<module> && cjpm build 2>&1
```

### 6. Track Progress

**If compilation passes:**
- Mark batch as complete
- Proceed to next batch

**If compilation fails (max 3 retries):**
- Load `java2cangjie-fix` skill to fix errors
- If still failing after 3 retries, mark batch as blocked
- Move to next available batch

## File Size Control

- Single file > 200 lines: translate alone
- Small files (< 100 lines each): batch up to 3
- Always compile after each batch, never batch multiple translations without compiling

## Context Window Management

- Read relevant docs BEFORE translating each batch, not during
- Focus on one file at a time within a batch
- Use checkpoint/state to resume if context fills
- If context is getting low (>80% used), save progress and suggest resuming

## Session Resumption

When resuming an interrupted translation:

1. Check for state file: `<output_dir>/.java2cangjie_state.json`
2. Or check checkpoint: `<output_dir>/.java2cangjie_checkpoint.md`
3. Determine which batches are completed/in-progress/pending
4. Call `translation_status()` (OpenCode) or read checkpoint (Claude Code)
5. Continue from first non-completed batch

## Error Handling

If a batch consistently fails:
1. Try splitting the batch into individual files
2. Try translating a simpler version first (e.g., remove generics, use Any)
3. Mark as blocked and continue with other batches
4. Document the failure reason in checkpoint

## Next Steps

- If all batches complete → invoke `java2cangjie-report` skill
- If errors remain → invoke `java2cangjie-fix` skill
