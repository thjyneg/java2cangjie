---
name: j2c-translate
description: "Use when translating Java source code to Cangjie (仓颉) language, starting a new Java-to-Cangjie translation project, resuming an interrupted translation, or converting Java files to Cangjie. Trigger on phrases like 'translate Java to Cangjie', 'port this Java project', 'convert Java code to 仓颉', or any Java-to-Cangjie migration task"
argument-hint: "[--java-path <path>] [--output-dir <dir>] [--max-batch-size <n>] [--resume]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Skill", "Grep", "Glob"]
---

# Java to Cangjie Translation Command

## Overview

This command coordinates the Java-to-Cangjie translation workflow using a dependency-driven approach. It guides Claude through analyzing the Java project, planning translation batches, translating code, compiling, fixing errors, and generating reports.

**Key Principle:** Translation follows the dependency graph from leaf nodes (no dependencies) upward. If compilation fails, query cangjie-* skills for automated fixes. If unable to fix automatically, pause and ask user for guidance.

## Arguments

- `--java-path <path>`: Required. Path(s) to Java source root directory. Can be a single path or comma-separated multiple paths.
- `--output-dir <dir>`: Optional. Output directory for translated Cangjie files. Default: `<java-path>/../j2cjgenerated/`
- `--max-batch-size <n>`: Optional. Maximum Java files per batch. Default: 3.
- `--resume`: Optional. Resume from existing state file if found.

## Workflow

### Step 1: Initialize and Analyze

1. Parse command arguments from user request
2. Determine Java source path(s) and output directory
3. Check for `--resume` flag

If `--resume` is NOT specified or state file doesn't exist:
- Run dependency analysis using `scripts/analyze_deps.py`
- Script produces JSON output with:
  ```json
  {
    "totalFiles": <int>,
    "batches": [
      {
        "id": "batch-1",
        "files": [
          {"className": "ClassName", "path": "/path/to/ClassName.java", "lines": 100}
        ],
        "dependencies": []
      }
    ],
    "dagSummary": "A → B → C"
  }
  ```

If `--resume` is specified and state file exists:
- Read existing state file from output directory
- Determine which batches are completed, in-progress, blocked, or pending
- Continue from first non-completed batch

### Step 2: Initialize Output Structure

1. Create output directory: `<output-dir>/`
2. Detect project type (single or multi-module):
   - Single module: Create `<output-dir>/<module>/src/` with `cjpm.toml`
   - Multi-module: Detect Maven/Gradle modules, create per-module structure
3. Create `cjpm.toml` for each module:
   ```toml
   [package]
   cjc-version = "0.53.13"
   name = "<module-name>"
   version = "0.1.0"
   description = "Java to Cangjie translation"
   authors = ["Translated from Java"]
   license = "Apache-2.0"
   output-type = "static"
   ```

### Step 3: Translation Loop

For each batch in order (following DAG from leaves upward):

#### 3.1: Get Batch Details

Read batch information:
- Files to translate (1-3 Java files)
- Dependencies (must be completed before this batch)

#### 3.2: Read Java Source

For each Java file in the batch:
- Read the Java source code
- Understand class structure, methods, fields
- Note imports and dependencies

#### 3.3: Lookup Cangjie Documentation

**CRITICAL: Always load relevant Cangjie skills BEFORE translating.**

Use Skill tool to load:
1. `cangjie-std` → Standard library APIs
2. `cangjie-lang-features` → Language syntax, generics, concurrency
3. `cangjie-stdx` → Extended library (JSON, encoding)
4. `cangjie-regulations` → Coding conventions and naming
5. `cangjie-toolchains` → Build tools (cjpm, cjc)

**Load these skills using the Skill tool to get full documentation context.**

#### 3.4: Translate Java to Cangjie

Follow the mapping rules from `java2cangjie-translate` skill:

Key mappings:
- `ArrayList<E>` → `std.collection.ArrayList<E>`
- `HashMap<K,V>` → `std.collection.HashMap<K,V>`
- `null` → `None` or `??`
- `try/catch` → `try/except`
- `synchronized` → `std.sync.Mutex`

**CRITICAL: Handle Cangjie keywords:**
- `init` → rename to `initialize()`
- `type` → escape with backticks or rename
- Extract inner enums to top-level

**CRITICAL: Directory structure:**
- Java Maven: `src/main/java/com/example/`
- Cangjie: `src/com/example/` (NO `main/java`)

#### 3.5: Write Cangjie Output

Write translated files to correct locations:
- Preserve package structure
- Use `.cj` extension
- Place in `<output-dir>/<module>/src/<package_path>/`

#### 3.6: Compile the Batch

```bash
cd <output-dir>/<module>
cjpm build 2>&1
```

If compilation passes:
- Update state: mark batch as `completed`
- Record output file paths
- Save state file
- Proceed to next batch

If compilation fails:
- Parse compilation errors
- **Load `java2cangjie-fix` skill for error guidance**
- Try to fix errors using Cangjie skills
- Retry compilation (max 3 attempts per batch)

#### 3.7: Error Handling Strategy

**When compilation fails:**

1. **First attempt:** Use `java2cangjie-fix` skill to understand error pattern
   - Load relevant cangjie-* skills based on error type
   - Apply fix suggested by error patterns
   - Retry `cjpm build`

2. **Second attempt:** If still failing, read error output carefully
   - Check for specific Cangjie compilation issues
   - Look up exact syntax in `cangjie-lang-features` or `cangjie-original-docs`
   - Make targeted fixes

3. **Third attempt:** Final automated fix attempt
   - Simplify problematic code if needed
   - Use more explicit types or workarounds

4. **After 3 failed attempts:**
   - Mark batch as `blocked` in state file
   - Record error details
   - **PAUSE and ask user for guidance**
   - Wait for user confirmation on how to proceed
   - After user confirms, retry compilation

### Step 4: Track State

Maintain state file at `<output-dir>/.java2cangjie_state.json`:

```json
{
  "projectPath": "/path/to/java",
  "outputDir": "/path/to/output",
  "totalFiles": 42,
  "batches": {
    "batch-1": {
      "status": "completed",
      "files": [...],
      "dependencies": [],
      "startedAt": "2026-04-02T...",
      "completedAt": "2026-04-02T..."
    },
    "batch-2": {
      "status": "in_progress",
      "files": [...],
      "dependencies": ["batch-1"],
      "startedAt": "2026-04-02T...",
      "retries": 1
    },
    "batch-3": {
      "status": "pending",
      "files": [...],
      "dependencies": ["batch-2"]
    }
  },
  "createdAt": "2026-04-02T..."
}
```

Use Read/Write tools to manage this file.

### Step 5: Generate Report

After all batches complete or user stops:

1. Invoke `java2cangjie-report` skill
2. Provide translation statistics:
   - Total files processed
   - Files translated successfully
   - Batches completed/blocked/pending
   - Compilation success rate

## Command Execution Pattern

When user runs `/j2c-translate`:

1. **Parse arguments**: Extract `--java-path`, `--output-dir`, `--max-batch-size`, `--resume`
2. **Show summary**: Display project analysis result
3. **Begin translation**: Start with first pending batch
4. **Loop**: For each batch:
   - Translate files
   - Compile
   - Fix errors (max 3 attempts)
   - Update state
5. **Generate report**: When complete or stopped

## Important Notes

- **Never skip compilation**: Always compile after each batch
- **Follow dependency order**: Translate leaves first, dependent files later
- **Use Cangjie skills**: Load relevant skills before fixing errors
- **Ask user when stuck**: After 3 failed attempts, pause and ask for guidance
- **Preserve state**: Always save state after each batch

## Tools Required

- `Bash`: Run `analyze_deps.py` and `cjpm build`
- `Read`: Read Java files, state file, Cangjie skills
- `Write`: Write Cangjie files, update state
- `Edit`: Modify Cangjie files for fixes
- `Skill`: Load Cangjie documentation skills
- `Grep`: Search for error patterns
- `Glob`: Find Java files
