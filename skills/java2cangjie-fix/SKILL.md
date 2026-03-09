---
name: java2cangjie-fix
description: "Use when executing modifications, fixing translation errors iteratively, or implementing modify-compile loop after user confirmation"
---

# Java to Cangjie Translation - Step 5: Fix Errors

## Overview

This skill executes the approved modifications and attempts compilation. If errors occur, continue fixing iteratively with a maximum of 20 iteration rounds. The process uses dependency analysis to fix errors in the correct order.

## Prerequisites

Before using this skill, ensure:

- User has approved modification plan (use `java2cangjie-confirm` skill)
- All fixes are documented with references
- Output directory is accessible
- cjpm is available for compilation

## Core Process: Dependency Analysis → TodoWrite List → Sequential Loop

The fixing process follows this workflow:

1. **Analyze file dependencies** - Determine which files depend on which
2. **Create TODO list** - Use TodoWrite tool to track all fixes
3. **Execute fixes sequentially** - Fix in dependency order
4. **Compile after each fix** - Verify the fix works
5. **Iterate if needed** - Continue until all errors are resolved

## Core Principle: Modify-Compile Loop (Mandatory Execution)

**🔴 IRON RULE: Every modification must be immediately followed by compilation.**

Never batch multiple fixes without compiling. The modify-compile loop is mandatory:

```
Modify → Compile → Check → (if error) → Modify → Compile → ...
```

### Loop Rules (Cannot Be Violated)

1. **One fix at a time** - Fix one error, then compile
2. **Always compile** - Never skip compilation after a fix
3. **Check results** - Verify the fix resolved the error
4. **Max 20 iterations** - Stop after 20 rounds to prevent infinite loops
5. **Document everything** - Record every fix and result

## Compilation and Fixing Process

### 1. Analyze File Dependencies

Determine the correct order to fix files.

**Method 1: Analyze dependencies via import statements**

```bash
# Find all import statements
Grep: pattern="^import " path="<output_dir>" glob="*.cj"

# Example output:
# src/main/cangjie/com/example/Service.cj: import com.example.Model
# src/main/cangjie/com/example/Controller.cj: import com.example.Service
```

**Dependency graph:**
```
Controller.cj depends on Service.cj
Service.cj depends on Model.cj
Model.cj has no dependencies
```

**Fix order (bottom-up):**
1. Fix Model.cj first (no dependencies)
2. Fix Service.cj (depends on Model)
3. Fix Controller.cj (depends on Service)

**Method 2: Find all local package imports**

```bash
# Find local package imports
Grep: pattern="^import com\." path="<output_dir>" glob="*.cj"
```

### 2. Use TodoWrite Tool to Create TODO List

Create a comprehensive TODO list for all fixes:

```javascript
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "pending"
    },
    {
      "content": "Fix Service.cj: Replace currentTimeMillis",
      "id": "fix_2",
      "status": "pending"
    },
    {
      "content": "Fix Controller.cj: Handle nullable value",
      "id": "fix_3",
      "status": "pending"
    }
  ]
}
```

### 3. Identify `<--` Marked Unsupported Code

Find all files with j2cj markers for unsupported Java features:

```bash
# Find all files with <-- markers
Grep: pattern="<--" path="<output_dir>" glob="*.cj"
```

**View specific marker content:**

```bash
# Read file with context
Read: file_path="<output_dir>/path/to/file.cj"
```

### 4. Create adapters Folder

For unsupported Java features that cannot be directly translated:

```bash
# Create adapters directory
mkdir -p <output_dir>/src/main/cangjie/adapters
```

Create adapter files for unsupported features:

```cj
// adapters/JavaCollectionsAdapter.cj
package adapters

import std.collection.ArrayList

// Adapter for Java-specific collection methods
public class JavaCollectionsAdapter {
    public static func singletonList<T>(element: T): ArrayList<T> {
        let list = ArrayList<T>()
        list.add(element)
        return list
    }

    public static func emptyList<T>(): ArrayList<T> {
        return ArrayList<T>()
    }
}
```

### 5. Execute Fixes Sequentially

For each fix in the TODO list:

```javascript
// Mark fix as in_progress
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "in_progress"
    }
  ]
}
```

**Make the fix:**

```bash
# Edit the file
Edit: {
  "file_path": "<output_dir>/src/main/cangjie/com/example/Model.cj",
  "instruction": "Add import statement for ArrayList at the top of the file",
  "old_string": "package com.example

public class Model {",
  "new_string": "package com.example

import std.collection.ArrayList

public class Model {"
}
```

**Compile immediately:**

```bash
# Change to output directory
cd <output_dir>

# Compile
cjpm build

# Check exit code
echo $?
```

**Check result:**

```bash
# If exit code is 0, success
# If exit code is not 0, read error output
```

**Update TODO:**

```javascript
// If successful, mark as completed
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "completed"
    }
  ]
}

// If failed, keep as in_progress and add new task
TodoWrite: {
  "todos": [
    {
      "content": "Fix Model.cj: Add ArrayList import",
      "id": "fix_1",
      "status": "in_progress"
    },
    {
      "content": "Fix new error: ...",
      "id": "fix_new_1",
      "status": "pending"
    }
  ]
}
```

### 6. Repeat Until All Fixes Complete

Continue the modify-compile loop until:

- All TODO items are completed, OR
- Maximum 20 iterations reached, OR
- User requests to stop

## Iteration Tracking

### Track Iteration Count

Keep track of iteration rounds:

```
Iteration 1: Fixed 3 errors, 39 remaining
Iteration 2: Fixed 5 errors, 34 remaining
Iteration 3: Fixed 4 errors, 30 remaining
...
Iteration 20: Fixed 2 errors, 28 remaining - MAX ITERATIONS REACHED
```

### Track Progress

After each iteration, report:

- Files modified in this iteration
- Errors fixed in this iteration
- Errors remaining
- New errors introduced (if any)

## Common Fix Patterns

### Pattern 1: Add Missing Import

**Error:**
```
error: Type 'ArrayList' not found
```

**Fix:**
```cj
// Add at top of file
import std.collection.ArrayList
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 2: Replace Method Call

**Error:**
```
error: Method 'currentTimeMillis' not found
```

**Fix:**
```cj
// Before
let time = System.currentTimeMillis()

// After
import std.time.Time
let time = Time.now()
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 3: Handle Nullability

**Error:**
```
error: Cannot assign nullable value to non-nullable type
```

**Fix:**
```cj
// Option 1: Use ?? operator
let result: String = getNullableString() ?? "default"

// Option 2: Use Option type
let result: Option<String> = getNullableString()
match (result) {
    case Some(value) => { /* use value */ }
    case None => { /* handle null */ }
}
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

### Pattern 4: Replace Unsupported Keyword

**Error:**
```
// <-- Java keyword 'synchronized' not supported -->
```

**Fix:**
```cj
// Before
synchronized(this) {
    // critical section
}

// After
import std.sync.Mutex

private let lock: Mutex = Mutex()

lock.lock()
try {
    // critical section
} finally {
    lock.unlock()
}
```

**Compile:**
```bash
cd <output_dir> && cjpm build
```

## Handling Compilation Errors

### Analyze Compilation Output

When compilation fails:

1. **Read the error output**
2. **Identify the error type**
3. **Locate the error in the code**
4. **Research the fix in documentation**
5. **Apply the fix**
6. **Compile again**

### Example Error Analysis

```bash
# Compilation error output
error: Type 'HashMap' not found in module 'std.collection'
  --> src/main/cangjie/com/example/Service.cj:42:15
   |
42 |     let map: HashMap<String, Int> = HashMap<String, Int>()
   |               ^^^^^^^ not found

# Analysis:
# - Error: Type 'HashMap' not found
# - Location: Service.cj:42
# - Cause: Missing import or wrong package

# Research:
# Search skills/java2cangjie-fix/docs/ for HashMap documentation

# Fix: Add import
import std.collection.HashMap

# Compile again
cjpm build
```

## When to Stop

### Success Criteria

Stop when:

- [ ] All TODO items are completed
- [ ] Compilation succeeds (exit code 0)
- [ ] No errors remain
- [ ] All tests pass (if available)

### Failure Criteria

Stop when:

- [ ] Maximum 20 iterations reached
- [ ] User requests to stop
- [ ] Cannot resolve specific errors
- [ ] Fixing one error causes more errors

## Next Steps

After fixing all errors:

1. Use `java2cangjie-test` skill to compile and test
2. Use `java2cangjie-report` skill to generate final report

## Session Resumption

To resume an interrupted fix process:

1. Check checkpoint file at `<output_dir>/.java2cangjie_checkpoint.md`
2. Read the file repair status table to determine which files are completed
3. Create TodoWrite with appropriate statuses based on checkpoint
4. Continue fixing from the first non-completed file

```javascript
// Example: Resuming mid-fix
TodoWrite({
  "todos": [
    {"activeForm": "Fixing Model.cj", "content": "Fix Model.cj: Add ArrayList import", "status": "completed"},
    {"activeForm": "Fixing Service.cj", "content": "Fix Service.cj: Replace currentTimeMillis", "status": "completed"},
    {"activeForm": "Fixing UserService.cj", "content": "Fix UserService.cj: Handle nullable value", "status": "in_progress"},
    {"activeForm": "Fixing DataService.cj", "content": "Fix DataService.cj: Add missing imports", "status": "pending"},
    {"activeForm": "Fixing Controller.cj", "content": "Fix Controller.cj: Update method signatures", "status": "pending"}
  ]
})
```

### Checkpoint Integration

Update the checkpoint file after each successful fix:

```markdown
# In .java2cangjie_checkpoint.md

#### File Repair Status
| File | Level | Status | Fix Round | Last Error |
|------|-------|--------|-----------|------------|
| common/Model.cj | 1 | completed | 1 | - |
| service/Service.cj | 2 | completed | 1 | - |
| service/UserService.cj | 3 | in_progress | 2 | Type 'ArrayList' not found:15 |
```

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup
- **java2cangjie-translate** - Execute translation
- **java2cangjie-analyze** - Analyze errors
- **java2cangjie-confirm** - Confirm modifications (prerequisite)
- **java2cangjie-test** - Test Cangjie code (next step)
- **java2cangjie-report** - Generate translation report
