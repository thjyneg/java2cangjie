---
name: java2cangjie-fix
description: "Use when fixing compilation errors in translated Cangjie (仓颉) code, analyzing cjpm build errors, resolving Cangjie API mismatches, or looking up documentation for error resolution. Trigger on 'Cangjie compile error', 'cjpm build failed', '仓颉编译失败', or any Cangjie compilation error fixing task"
---

# Java to Cangjie Translation - Fix Errors

## Overview

Systematic error fixing using dependency-aware, one-at-a-time methodology. Every fix must be followed by compilation verification.

## Error Analysis Process

### Step 1: Capture Errors

**OpenCode (with plugin tools):**

```bash
# Use compile_batch(batchId) which runs cjpm build internally
```

**Claude Code:**

```bash
cd <output_dir>/<module> && cjpm build 2>&1
```

Capture the full error output. Parse error types and locations.

**Note:** When fixing errors from `/j2c-translate` command workflow:
- The workflow handles max 3 retry attempts automatically
- After 3 failed attempts, it will PAUSE and ask you for guidance
- Fix errors during translation batches, not after project completion

### Step 2: Categorize Errors

Group errors by pattern. Common categories (see `error-patterns.md` for details):

| Category | Example | Priority |
|----------|---------|----------|
| Missing import | `Type 'ArrayList' not found` | High |
| Type mismatch | `Cannot assign X to Y` | High |
| API difference | `Method 'size' not found` | Medium |
| Syntax error | `Expected ';'` | Medium |
| Nullability | `Cannot assign nullable to non-nullable` | Medium |
| Generic type | `Generic parameter mismatch` | Low |
| Unsupported feature | `Keyword 'synchronized' not supported` | Low |

### Step 3: Documentation Lookup (MANDATORY)

**NEVER guess a fix without checking documentation first.**

Use the Cangjie skills for documentation lookup:
1. `cangjie-std` → standard library types and APIs
2. `cangjie-lang-features` → language syntax, generics, concurrency, error handling
3. `cangjie-stdx` → extended library (JSON, encoding, configuration)
4. `cangjie-original-docs` → full original documentation fallback
5. `error-patterns.md` (in this skill's directory) → known error patterns

### Step 4: Dependency Analysis

Determine fix order based on file dependencies:

```bash
# Find import dependencies
grep -rn "^import " <output_dir> --include="*.cj"
```

Fix bottom-up: dependencies before dependents. Files with no dependencies first.

### Step 5: Fix One Error at a Time

For each error:

1. **Read the error** - Understand what failed and where
2. **Lookup documentation** - Find the correct Cangjie API/syntax
3. **Apply minimal fix** - Change only what's needed
4. **Compile immediately** - `cd <output_dir> && cjpm build 2>&1` (Claude Code) or `compile_batch(batchId)` (OpenCode)
5. **Verify** - Check if the specific error is resolved
6. **If compilation fails**: revert with `git checkout -- <file>` if new errors introduced
7. **Max 3 retries** per error, then report as BLOCKED

### Step 6: DAG-Based Error Fixing (Claude Code)

When fixing errors from `/j2c-translate` workflow:

**Fix Order Follows Dependency DAG:**
1. Start with leaf nodes (files with no internal dependencies)
2. Fix dependencies first, then fix dependent files
3. Read state file to determine current batch and status

**Error Resolution Strategy:**

For each compilation error:

1. **First attempt (automated):**
   - Load relevant Cangjie skills based on error type
   - Apply fix suggested by error patterns
   - Retry `cjpm build`

2. **Second attempt (manual lookup):**
   - Parse error carefully
   - Look up exact syntax in `cangjie-lang-features` or `cangjie-original-docs`
   - Make targeted fixes
   - Retry `cjpm build`

3. **Third attempt (simplification):**
   - Try simplified approach if standard fix fails
   - Use explicit types or workarounds
   - Retry `cjpm build`

4. **After 3 failed attempts:**
   - Mark batch as `blocked` in state file
   - Document the specific error details
   - **PAUSE and ask user for guidance**
   - Wait for user confirmation on how to proceed
   - After user confirms, retry compilation

**State File Management:**
- Read `<output_dir>/.java2cangjie_state.json` to get current batch status
- Update batch status after each fix attempt
- Save state file after every compilation

### Step 7: Track Progress

Use TodoWrite to track each fix:

```
TodoWrite: [
  {"content": "Fix Model.cj: Add ArrayList import", "status": "completed"},
  {"content": "Fix Service.cj: Replace currentTimeMillis", "status": "in_progress"},
  {"content": "Fix Controller.cj: Handle nullable value", "status": "pending"}
]
```

## Protected Files

**NEVER modify these files:**

1. **cjpm.toml** - Project configuration (user-managed)
2. **emptyp.cj** - Placeholder files (may be referenced by other files)

If an error requires modifying these, document it and skip to next error.

## Common Fix Patterns

### Pattern: Missing Import

```
Error: Type 'ArrayList' not found
Fix:  Add `import std.collection.ArrayList` at top of file
```

### Pattern: Method Replacement

```
Error: Method 'currentTimeMillis' not found
Fix:  Replace System.currentTimeMillis() with Time.now()
      Add `import std.time.Time`
```

### Pattern: Nullability

```
Error: Cannot assign nullable value to non-nullable type
Fix:  Use Option<T> or ?? operator
      let result: String = getNullable() ?? "default"
```

### Pattern: Synchronized Block

```
Error: Unsupported keyword 'synchronized'
Fix:  Replace with Mutex:
      import std.sync.Mutex
      private let lock = Mutex()
      lock.lock()
      try { /* critical section */ } finally { lock.unlock() }
```

### Pattern: For-Each Loop

```
Error: Unexpected token 'for' or iterator pattern
Fix:  Replace Java for-each with Cangjie for-in:
      for (item in list) { ... }
```

See `error-patterns.md` in this directory for the complete pattern catalog.

## Rules

1. **NEVER** batch multiple fixes without compiling between them
2. **ALWAYS** check documentation before guessing
3. **ALWAYS** fix dependencies before dependents (follow DAG from leaves upward)
4. **ALWAYS** compile after every single fix
5. **NEVER** modify protected files (cjpm.toml, emptyp.cj)
6. **STOP** after max 20 iterations to prevent infinite loops
7. **DOCUMENT** every fix: file, line, error, solution, doc reference
8. **PAUSE** after 3 failed attempts and ask user for guidance before continuing
9. **UPDATE** state file after each fix attempt when using `/j2c-translate` workflow

## When to Stop

### Success
- All errors resolved
- `cjpm build` returns exit code 0
- No remaining `<--` markers
- Batch marked as `completed` in state file

### Pause for User Guidance
- Max 3 retries per single error exhausted
- Unable to resolve error after documentation lookup
- New errors introduced by fix attempts
- **After pausing, wait for user confirmation before retrying**

### Failure
- Max 20 total iterations reached
- User requests stop
- Multiple consecutive batches blocked

## Next Steps

- If all errors fixed → invoke `java2cangjie-report` skill
- If paused for user guidance → await user input, then retry compilation
- If blocked → document remaining errors in `<output_dir>/.java2cangjie_state.json`, suggest manual review
- When using `/j2c-translate` workflow → continue to next batch after current batch completes
