---
name: j2c-translate
description: "Use when translating Java source code to Cangjie (仓颉) language, starting a new Java-to-Cangjie translation project, resuming an interrupted translation, or converting Java files to Cangjie. Trigger on phrases like 'translate Java to Cangjie', 'port this Java project', 'convert Java code to 仓颉', or any Java-to-Cangjie migration task"
argument-hint: "[--java-path <path>] [--output-dir <dir>] [--max-batch-size <n>] [--resume]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Skill", "Grep", "Glob"]
---

# Java to Cangjie Translation Command

## Overview

Coordinate the Java-to-Cangjie translation workflow using dependency-driven incremental strategy.

**Core Principle:** Follow the dependency DAG from leaf nodes upward. Compile after every batch. Query cangjie-* skills for automated fixes. After 3 failed fix attempts, pause and ask user for guidance.

## Arguments

- `--java-path <path>`: Required. Path(s) to Java source root. Comma-separated for multiple.
- `--output-dir <dir>`: Optional. Output directory. Default: `<java-path>/../j2cjgenerated/`
- `--max-batch-size <n>`: Optional. Max files per batch. Default: 3.
- `--resume`: Optional. Resume from existing state file.

## Workflow

### Step 1: Initialize and Analyze

If `--resume` and state file exists at `<output-dir>/.java2cangjie_state.json`:
- Read state file, determine completed/in-progress/blocked/pending batches
- Continue from first non-completed batch

Otherwise, run dependency analysis:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze_deps.py" --java-path <path> [--output-dir <dir>] [--max-batch-size <n>]
```

Parse JSON output containing `totalFiles`, `batches` (with dependencies and file lists), `dagSummary`, and `outputDir`.

### Step 2: Initialize Output Structure

Create output directory and `cjpm.toml`:

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

Directory: `<output-dir>/<module>/src/<package_path>/*.cj`

**Critical:** Cangjie uses `src/<package>/` directly, NOT `src/main/java/<package>/`.

### Step 3: Translation Loop

For each batch in dependency order:

1. **Read Java source** - Understand class structure, methods, imports
2. **Lookup Cangjie docs** - Load `cangjie-std`, `cangjie-lang-features`, `cangjie-stdx`, `cangjie-regulations` via Skill tool BEFORE translating
3. **Translate** - Apply mapping rules from `java2cangjie-translate` skill
4. **Write output** - Preserve package structure, use `.cj` extension
5. **Compile** - `cd <output-dir>/<module> && cjpm build 2>&1`
6. **Update state** - Mark batch completed or handle errors

### Step 4: Error Handling Strategy

When compilation fails, follow the DAG-based error resolution:

| Attempt | Action |
|---------|--------|
| 1st | Load `java2cangjie-fix` skill, apply error pattern fixes, retry |
| 2nd | Look up exact syntax in `cangjie-lang-features` or `cangjie-original-docs`, targeted fix |
| 3rd | Simplify code, use explicit types or workarounds |
| After 3 | Mark batch `blocked`, **PAUSE and ask user for guidance** |

Fix order follows dependency DAG: leaf nodes first, dependent files later.

### Step 5: Track State

Maintain `<output-dir>/.java2cangjie_state.json`:

```json
{
  "projectPath": "/path/to/java",
  "outputDir": "/path/to/output",
  "totalFiles": 42,
  "batches": {
    "batch-1": {
      "status": "completed|in_progress|blocked|pending",
      "files": [...],
      "dependencies": [],
      "retries": 0
    }
  }
}
```

Use Read/Write tools to manage state file. Save after every batch.

### Step 6: Generate Report

After all batches complete or user stops:
- Invoke `java2cangjie-report` skill
- Provide: total files, files translated, batches completed/blocked, compilation success rate

## Key Translation Rules

- **Keyword collision:** Rename `init` to `initialize`, escape `type` with backticks
- **Inner enums:** Extract to top-level with compound names (e.g., `OuterClassEnumName`)
- **InputStream.close():** Cast to `Resource` first: `(stream as Resource).close()`
- **Never skip compilation:** Always compile after each batch
- **Follow dependency order:** Translate leaves first

## Important Notes

- **Never skip compilation:** Always compile after each batch
- **Follow dependency order:** Translate leaves first, dependent files later
- **Use Cangjie skills:** Load relevant skills before fixing errors
- **Ask user when stuck:** After 3 failed attempts, pause and ask for guidance
- **Preserve state:** Always save state after each batch

## Tools Required

- `Bash`: Run `analyze_deps.py` and `cjpm build`
- `Read`: Read Java files, state file, Cangjie skills
- `Write`: Write Cangjie files, update state
- `Edit`: Modify Cangjie files for fixes
- `Skill`: Load Cangjie documentation skills
- `Grep`: Search for error patterns
- `Glob`: Find Java files
