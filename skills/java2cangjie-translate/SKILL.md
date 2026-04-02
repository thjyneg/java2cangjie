---
name: java2cangjie-translate
description: "Use when translating Java source code to Cangjie (仓颉) language, starting a new Java-to-Cangjie translation project, resuming an interrupted translation, or converting Java files to Cangjie. Trigger on phrases like 'translate Java to Cangjie', 'port this Java project', 'convert Java code to 仓颉', or any Java-to-Cangjie migration task"
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
4. compile_batch(batchId)           → compile via cjpm build, auto-complete on success
5. If compile fails → fix errors → compile_batch(batchId) again (max 3 retries)
6. Repeat from step 2
```

**Note**: The `compile_batch` tool runs `cjpm build` internally and auto-manages batch status. Do NOT call `mark_complete` without compiling first.

## Claude Code Environment (no plugin tools)

Manual workflow with equivalent logic:

```bash
# Step 1: Scan Java files
find <java_dir> -name "*.java" -type f

# Step 2: Build dependency graph
grep -rn "^import " <java_dir> --include="*.java" | grep -v "java\.\|javax\.\|org\."

# Step 3: Identify leaf files (no internal dependencies)
# Files whose imports don't reference other project classes = leaf nodes

# Step 4: Track progress in state file
# Save to <output_dir>/.java2cangjie_state.json
# Format: { batches: { "batch-N": { status, files, retries } }, totalFiles, outputDir }
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
| `long` | `Int64` |
| `int` | `Int` |
| `byte` | `Byte` |
| `byte[]` | `Array<Byte>` |
| `boolean` | `Bool` |
| `String` | `String` |
| `float` | `Float32` |
| `double` | `Float64` |
| `char` | `Rune` |

**IMPORTANT - Type Notes:**
- `byte[]` in Java translates to `Array<Byte>` in Cangjie (not `Byte[]`)
- Always initialize arrays: `Array<Byte>(0, { 0 })`
- Use `Int64` for Java `long` to avoid overflow

### 4. Write Output

**IMPORTANT - Directory Structure Differences:**

Java Maven projects use `src/main/java/包名/`, but Cangjie projects require `src/包名/` directly under `src/`. 

**Correct Cangjie structure:**
```
<java_project>/j2cjgenerated/
├── <module>/
│   ├── cjpm.toml
│   └── src/
│       └── <package_path>/    # Direct under src, NOT src/main/cj
│           └── *.cj
```

**Common mistakes to avoid:**
- ❌ `src/main/cj/包名/` - This is Java Maven convention, not Cangjie
- ✅ `src/包名/` - Correct Cangjie structure

For Maven projects, create `cjpm.toml` per module:

```toml
[package]
cjc-version = "0.53.13"
name = "<module-name>"
version = "0.1.0"
description = "Description"
authors = ["Your Name <email@example.com>"]
license = "Apache-2.0"
output-type = "static"
```

**Multi-level package names (e.g., `net.lingala.zip4j`):**
- Keep the same package structure in Cangjie: `package net.lingala.zip4j`
- File path: `src/net/lingala/zip4j/ClassName.cj`
- cjpm.toml name should match the base module name (e.g., "zip4j")

### 5. Compile

**OpenCode (with plugin tools):**

Use `compile_batch(batchId)` — it handles compilation and batch status automatically.

**Claude Code (manual):**

```bash
cd <java_project>/j2cjgenerated/<module> && cjpm build 2>&1
```

`cjpm build` automatically handles dependency resolution and package linking. Prefer it over `cjc -p` which requires manually specifying dependency information.

**NOTE - cjpm build directory scanning:**

cjpm build requires at least one `.cj` file directly in each directory to scan subdirectories. If you see:
```
Warning: there is no '.cj' file in directory './src', and its subdirectories will not be scanned
```
Create a placeholder `.cj` file (e.g., `emptyp.cj`) in the directory.

**When to use each tool:**

| Tool | Use Case | Notes |
|-------|-----------|-------|
| `compile_batch()` | OpenCode translation workflow | Plugin runs `cjpm build` internally, auto-manages status |
| `cjpm build` | Claude Code translation workflow | Auto-handles dependencies, standard approach |
| `cjc -p` | Single-package quick check only | No dependency resolution, use only for isolated packages |

### 6. Track Progress

**If compilation passes:**
- Mark batch as complete
- Proceed to next batch

**If compilation fails (max 3 retries):**
- Load `java2cangjie-fix` skill to fix errors
- If still failing after 3 retries, mark batch as blocked
- Move to next available batch

## Project Initialization

For existing Java projects (not using `cjpm init`):

1. Create the output directory structure:
```bash
mkdir -p <java_project>/j2cjgenerated/<module>/src
```

2. Create `cjpm.toml` with appropriate settings (see section 4)

3. Create package directories under `src/` matching Java package structure

**Note**: Do NOT use `cjpm init` for Java-to-Cangjie translation projects. It creates unnecessary files and expects a different structure.

## File Size Control

- Single file > 200 lines: translate alone
- Small files (< 100 lines each): batch up to 3
- Always compile after each batch, never batch multiple translations without compiling

## Context Window Management

- Read relevant docs BEFORE translating each batch, not during
- Focus on one file at a time within a batch
- Use state file to resume if context fills
- If context is getting low (>80% used), save progress and suggest resuming

## Session Resumption

When resuming an interrupted translation:

1. Check for state file: `<output_dir>/.java2cangjie_state.json`
2. Determine which batches are completed/in-progress/pending
3. Call `translation_status()` (OpenCode) or read state file (Claude Code)
4. Continue from first non-completed batch

## Error Handling

If a batch consistently fails:
1. Try splitting the batch into individual files
2. Try translating a simpler version first (e.g., remove generics, use Any)
3. Mark as blocked and continue with other batches
4. Document the failure reason in state file

## Project Cleanup

Compilation generates temporary files and cache. Clean periodically:

```bash
cd <java_project>/j2cjgenerated/<module>

# Clean build artifacts
cjpm clean

# Or manually clean
rm -rf target/ .cached/
```

**Common directories to be aware of:**
- `target/` - Build output directory
- `target/release/` - Release artifacts
- `.cached/` - Cangjie compiler cache
- `*.a` - Generated static library files
- `*.o` - Object files

## Next Steps

- If all batches complete → invoke `java2cangjie-report` skill
- If errors remain → invoke `java2cangjie-fix` skill
