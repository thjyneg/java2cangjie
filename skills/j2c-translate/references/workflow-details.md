# Workflow Details

Detailed step-by-step workflow for Java-to-Cangjie translation.

## Dependency Analysis Output Format

The `analyze_deps.py` script outputs JSON:

```json
{
  "projectInfo": {
    "type": "single|multi",
    "modules": [
      {"name": "module-name", "javaPath": "/path/to/src", "outputDir": "module-name"}
    ],
    "baseDir": "/path/to/base"
  },
  "totalFiles": 42,
  "totalBatches": 15,
  "batches": [
    {
      "id": "batch-1",
      "files": [
        {"className": "Utils", "path": "/path/to/Utils.java", "size": 1200, "lines": 45}
      ],
      "dependencies": []
    },
    {
      "id": "batch-2",
      "files": [
        {"className": "Service", "path": "/path/to/Service.java", "size": 3400, "lines": 120}
      ],
      "dependencies": ["batch-1"]
    }
  ],
  "dagSummary": "[Utils]\n[Utils] → [Service]",
  "outputDir": "/path/to/j2cjgenerated"
}
```

## Translation Execution Pattern

### Step 1: Initialize

Parse command arguments. Show project analysis summary to user:

```
Project Analysis Complete:
- Total files: 42
- Batches: 15
- Project type: single module
- Output: /path/to/j2cjgenerated

DAG Summary:
[Utils] → [Service, Model] → [Controller] → ...

Ready to translate. Starting with batch 1 (leaf files).
```

### Step 2: Per-Batch Translation

For each batch in order:

```
--- Batch 1/15: Utils.java (leaf, no dependencies) ---

1. Reading Java source...
2. Loading Cangjie documentation...
3. Translating...
4. Writing to src/com/example/Utils.cj...
5. Compiling... ✓ Success
6. State updated: batch-1 → completed
```

### Step 3: Error Recovery

When a batch fails compilation:

```
--- Batch 3/15: Service.java ---
1. Reading Java source...
2. Translating...
3. Writing to src/com/example/Service.cj...
4. Compiling... ✗ Failed (attempt 1/3)

Error: Type 'ArrayList' not found at Service.cj:15

5. Loading java2cangjie-fix skill...
6. Fix: Add `import std.collection.ArrayList`
7. Compiling... ✓ Success
8. State updated: batch-3 → completed
```

When max retries exhausted:

```
--- Batch 5/15: Controller.java ---
1. Translating...
2. Compiling... ✗ Failed (attempt 3/3)

Unable to resolve after 3 attempts. Error details:
  error: cannot infer generic type parameter

⏸ PAUSED: Marked batch-5 as blocked.
Please advise how to proceed:
  a) Provide manual fix
  b) Skip and continue with next batch
  c) Stop translation
```

### Step 4: Resume Workflow

When resuming with `--resume`:

```
Resuming translation...
State file found: /path/to/.java2cangjie_state.json

Progress: 8/15 batches completed, 1 blocked, 6 pending
Last completed: batch-8 (ControllerHelper.cj)
Blocked: batch-5 (Controller.cj)

Continuing with batch-9 (next available)...
```

## State File Schema

```json
{
  "projectPath": "/path/to/java/src",
  "outputDir": "/path/to/j2cjgenerated",
  "totalFiles": 42,
  "batches": {
    "batch-1": {
      "status": "completed",
      "files": [
        {"className": "Utils", "path": "/path/to/Utils.java", "lines": 45}
      ],
      "dependencies": [],
      "outputFiles": ["/path/to/output/src/com/example/Utils.cj"],
      "startedAt": "2026-04-02T10:00:00Z",
      "completedAt": "2026-04-02T10:02:30Z",
      "retries": 0
    },
    "batch-5": {
      "status": "blocked",
      "files": [...],
      "dependencies": ["batch-3"],
      "startedAt": "2026-04-02T10:15:00Z",
      "retries": 3,
      "blockReason": "Compilation failed after 3 attempts: cannot infer generic type parameter"
    }
  },
  "createdAt": "2026-04-02T09:55:00Z"
}
```

## Multi-Module Project Handling

When `analyze_deps.py` detects a multi-module project:

1. Each module gets its own output directory and `cjpm.toml`
2. Translate modules in dependency order (if module B depends on module A, translate A first)
3. Each module's batches follow the same leaf-upward strategy

```
Detected multi-module Maven project:
- module-common (2 files, 1 batch)
- module-core (15 files, 6 batches, depends on common)
- module-web (10 files, 4 batches, depends on core)

Order: common → core → web
```

## Compilation Directory Scanning

`cjpm build` requires at least one `.cj` file in each directory to scan subdirectories.

If seeing:
```
Warning: there is no '.cj' file in directory './src'
```

Create a placeholder file:
```bash
echo '// placeholder for cjpm directory scanning' > src/_pkg.cj
```
