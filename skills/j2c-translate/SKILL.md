---
name: j2c-translate
description: "This skill provides the detailed reference workflow for the /j2c-translate command. It is loaded automatically when the j2c-translate command executes or when the user needs in-depth guidance on the Java-to-Cangjie translation process including dependency analysis, batch planning, state management, and error recovery."
---

# Java to Cangjie Translation - Reference Workflow

Detailed reference for the `/j2c-translate` command execution. This skill provides the in-depth workflow, state schema, and error recovery patterns used during translation.

**Core Principle:** Follow the dependency DAG from leaf nodes upward. Compile after every batch. Query cangjie-* skills for automated fixes. After 3 failed fix attempts, pause and ask user for guidance.

## Dependency Analysis

The `/j2c-translate` command calls `scripts/analyze_deps.py` to build a dependency DAG:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze_deps.py" --java-path <path> [--output-dir <dir>] [--max-batch-size <n>]
```

Output format:

```json
{
  "projectInfo": {"type": "single|multi", "modules": [...], "baseDir": "..."},
  "totalFiles": 42,
  "totalBatches": 15,
  "batches": [
    {
      "id": "batch-1",
      "files": [{"className": "Utils", "path": "...", "size": 1200, "lines": 45}],
      "dependencies": []
    }
  ],
  "dagSummary": "[Utils]\n[Utils] → [Service]",
  "outputDir": "/path/to/j2cjgenerated"
}
```

## State File Schema

Maintained at `<output-dir>/.java2cangjie_state.json`:

```json
{
  "projectPath": "/path/to/java",
  "outputDir": "/path/to/output",
  "totalFiles": 42,
  "batches": {
    "batch-1": {
      "status": "completed|in_progress|blocked|pending",
      "files": [{"className": "Utils", "path": "...", "lines": 45}],
      "dependencies": [],
      "outputFiles": ["/path/to/output/src/com/example/Utils.cj"],
      "startedAt": "2026-04-02T10:00:00Z",
      "completedAt": "2026-04-02T10:02:30Z",
      "retries": 0,
      "blockReason": ""
    }
  },
  "createdAt": "2026-04-02T09:55:00Z"
}
```

## Error Recovery Strategy

Fix order follows dependency DAG: leaf nodes first, dependent files later.

| Attempt | Action |
|---------|--------|
| 1st | Load `java2cangjie-fix` skill, apply error pattern fixes, retry `cjpm build` |
| 2nd | Look up exact syntax in `cangjie-lang-features` or `cangjie-original-docs`, targeted fix |
| 3rd | Simplify code, use explicit types or workarounds |
| After 3 | Mark batch `blocked`, **PAUSE and ask user for guidance** |

When paused, present user with options:
- a) Provide manual fix
- b) Skip and continue with next batch
- c) Stop translation

## Resume Workflow

When `--resume` flag is used:

1. Read state file from `<output-dir>/.java2cangjie_state.json`
2. Determine progress: completed / in-progress / blocked / pending batches
3. Show progress summary to user
4. Continue from first non-completed batch respecting dependencies
5. If blocked batches have unblocked (dependencies now completed), retry them

## Output Structure

```
<output-dir>/
├── .java2cangjie_state.json
├── <module>/
│   ├── cjpm.toml
│   └── src/
│       └── <package_path>/
│           └── *.cj
```

**Critical:** Cangjie uses `src/<package>/` directly, NOT `src/main/java/<package>/`.

## Multi-Module Projects

When `analyze_deps.py` detects a multi-module project:

1. Each module gets its own output directory and `cjpm.toml`
2. Translate modules in dependency order
3. Each module's batches follow the same leaf-upward strategy

## Compilation Notes

`cjpm build` requires at least one `.cj` file in each directory to scan subdirectories.

If seeing:
```
Warning: there is no '.cj' file in directory './src'
```

Create a placeholder:
```bash
echo '// placeholder for cjpm directory scanning' > src/_pkg.cj
```

## Related Skills

- `java2cangjie-translate` - Detailed translation mapping rules and type conversions
- `java2cangjie-fix` - Error fixing workflow and error patterns
- `java2cangjie-report` - Report generation
- `cangjie-std` / `cangjie-lang-features` / `cangjie-stdx` - Cangjie documentation

## Reference Files

- **`references/workflow-details.md`** - Detailed workflow examples with sample output
