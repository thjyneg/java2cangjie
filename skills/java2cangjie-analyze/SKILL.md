---
name: java2cangjie-analyze
description: "Use when analyzing j2cj translation errors, creating modification plans, or researching Cangjie APIs and syntax after translation completes"
---

# Java to Cangjie Translation - Step 3: Analyze Errors

## Overview

This skill analyzes errors and warnings in j2cj translation results, researches Cangjie documentation, and creates a detailed modification plan. All research must be based on Cangjie API documentation and sample code.

## Prerequisites

Before using this skill, ensure:

- Translation has been completed (use `java2cangjie-translate` skill)
- Output directory contains generated Cangjie files
- Cangjie documentation is accessible in `skills/java2cangjie-fix/docs/` directory

## First Step: Find j2cj-Marked Issues

### Find all j2cj-marked issues

Search for all files with j2cj error markers:

```bash
# Find all files with <-- markers
Grep: pattern="<--" path="<output_dir>" glob="*.cj"
```

### View specific marker content

Read files to understand the error context:

```bash
# Read file with line numbers
Read: file_path="<output_dir>/path/to/file.cj"
```

## Analysis Process

### 1. Categorize Errors

Auto-classify errors based on actual error patterns found. Different projects will have different error types and distributions.

**Process:**
1. Extract all unique error types from the failed compilation results
2. Group errors by type automatically (do not assume a fixed set of categories)
3. Create categories dynamically based on error patterns

**Example categories (actual categories will vary by project):**
- **Type not found** - Missing or incorrect type definitions
- **Method not found** - Missing or incorrect method calls
- **Syntax errors** - Invalid Cangjie syntax
- **Unsupported features** - Java features not supported by j2cj
- **Nullability issues** - Incorrect null handling
- **Import errors** - Missing or incorrect import statements
- **Package mapping** - Java package to Cangjie package conversion issues
- **API changes** - Cangjie API differs from Java equivalent
- **Type conversion** - Automatic type conversion failures
- **Access control** - Visibility modifier issues
- **Missing implementations** - Abstract class or interface implementations

**IMPORTANT:** The actual error categories depend on the project's specific code and dependencies. Always analyze the actual errors first, then create categories dynamically.

Prioritize based on:

- **Critical** - Blocks compilation (must fix first)
- **High** - Affects core functionality
- **Medium** - Affects non-critical features
- **Low** - Cosmetic or can be deferred

### 3. Document Findings

Create a detailed error list with:

- File path and line number
- Error type
- Error message
- Context code
- Suggested fix (if apparent)

## Mandatory Documentation Lookup Process

**🔴 MANDATORY: All error fixes must be based on Cangjie documentation. Never guess or assume.**

### Lookup Priority Order

Follow this 5-step process for each error:

#### Step 1: Search in Basic Type Documentation

Search in `skills/java2cangjie-fix/docs/extra/` for basic types.

**Example: Searching for ArrayList**

```bash
# Search for ArrayList type
Grep: pattern="ArrayList" path="skills/java2cangjie-fix/docs/extra/" glob="*.md"
```

**What to look for:**
- Type definition and usage
- Constructor signatures
- Common methods
- Code examples

#### Step 2: Search in Standard Library API Documentation

Search in `skills/java2cangjie-fix/docs/libs/std/` for standard library APIs.

**Example: Searching for ArrayList type**

```bash
# Search for ArrayList type
Grep: pattern="class ArrayList" path="skills/java2cangjie-fix/docs/libs/std/collection/"

# Search for add method
Grep: pattern="func add" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_api/"
```

**What to look for:**
- Complete API documentation
- Method signatures
- Parameter descriptions
- Return types
- Usage examples

#### Step 3: Search Sample Code

Find practical examples in sample documentation.

**Example: Searching for ArrayList usage**

```bash
# List all sample files
Glob: pattern="sample_*.md" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_samples/"

# Search for ArrayList in samples
Grep: pattern="ArrayList" path="skills/java2cangjie-fix/docs/libs/std/collection/collection_package_samples/"
```

**What to look for:**
- Real-world usage patterns
- Best practices
- Common pitfalls
- Complete working examples

#### Step 4: Search in Language Manual

Search in `skills/java2cangjie-fix/docs/manual/` for language concepts.

**Example: Searching for generic syntax**

```bash
# Search for generic syntax
Grep: pattern="generic|<T>" path="skills/java2cangjie-fix/docs/manual/"
```

**What to look for:**
- Language syntax rules
- Type system details
- Best practices
- Design patterns

#### Step 5: Search Package Overview

Review package overview for context.

**Example: Collection package overview**

```bash
# Find package overview
Glob: pattern="*package_overview.md" path="skills/java2cangjie-fix/docs/libs/std/collection/"
```

**What to look for:**
- Package purpose and design
- Common use cases
- Related types and functions
- Design decisions

## Modification Plan Creation

### Plan Structure

Create a modification plan with:

1. **Error Summary**
   - Total error count
   - Error type distribution
   - Critical errors list

2. **Modification List**
   For each error:
   - File path and line number
   - Error description
   - Documentation reference
   - Proposed fix
   - Dependencies

3. **Execution Order**
   - List fixes in dependency order
   - Bottom-up approach (dependencies first)
   - Group related fixes

### Example Modification Plan

```markdown
# Modification Plan

## Error Summary
- Total errors: 42
- Type not found: 18
- Method not found: 12
- Nullability: 8
- Syntax: 4

## Critical Errors (Fix First)

1. **common/Constants.cj:15** - Type ArrayList not found
   - Documentation: skills/java2cangjie-fix/docs/extra/ArrayList.md
   - Fix: Add `import std.collection.ArrayList`
   - Dependencies: None

2. **service/UserService.cj:42** - Method currentTimeMillis not found
   - Documentation: skills/java2cangjie-fix/docs/libs/std/time/time_package_api/
   - Fix: Replace with `std.time.Time.now()`
   - Dependencies: None

## High Priority Errors

[... continue with remaining errors ...]

## Execution Order
1. Fix all import statements
2. Fix type definitions
3. Fix method calls
4. Fix nullability issues
5. Fix syntax errors
```

## Common Error Types and Solutions

### Type Not Found

**Error:**
```
error: Type 'ArrayList' not found
```

**Lookup Process:**
1. Search `skills/java2cangjie-fix/docs/extra/` for ArrayList
2. Search `skills/java2cangjie-fix/docs/libs/std/collection/` for ArrayList API
3. Find sample code using ArrayList

**Typical Solution:**
```cj
// Add import
import std.collection.ArrayList

// Or use full path
let list: std.collection.ArrayList<String> = std.collection.ArrayList<String>()
```

### Method Not Found

**Error:**
```
error: Method 'toString' not found in type 'Object'
```

**Lookup Process:**
1. Search documentation for target type
2. Find available methods in API docs
3. Check sample code for patterns

**Typical Solution:**
```cj
// Use String.valueOf
let str = String.valueOf(obj)

// Or implement custom toString
public override func toString(): String {
    return "custom string"
}
```

### Nullability Issues

**Error:**
```
error: Cannot assign nullable value to non-nullable type
```

**Lookup Process:**
1. Search `skills/java2cangjie-fix/docs/extra/Option.md` for Option type
2. Find sample code with null handling
3. Review language manual for null safety

**Typical Solution:**
```cj
// Use ?? operator
let result: String = getNullableString() ?? "default"

// Or use Option type
let result: Option<String> = getNullableString()
match (result) {
    case Some(value) => { /* use value */ }
    case None => { /* handle null */ }
}
```

### Unsupported Java Features

**Error Markers:**
```
// <-- Java keyword 'synchronized' not supported -->
// <-- Generic wildcard '? extends T' not supported -->
// <-- Java keyword 'instanceof' not supported -->
```

**Lookup Process:**
1. Search language manual for equivalent Cangjie features
2. Find sample code for similar patterns
3. Review package overview for alternatives

**Typical Solutions:**
- `synchronized` → Use `std.sync.Mutex`
- `instanceof` → Use `match` pattern matching
- Wildcards → Use specific types or constraints

## Next Steps

After completing analysis:

1. Use `java2cangjie-confirm` skill to present modification plan and get approval
2. Use `java2cangjie-fix` skill to execute modifications
3. Use `java2cangjie-test` skill to compile and test
4. Use `java2cangjie-report` skill to generate final report

## TodoWrite Task Management

Use TodoWrite to track the error analysis process and enable session resumption.

### Creating the TODO List

When starting error analysis, create a TODO list for the analysis workflow:

```javascript
TodoWrite({
  "todos": [
    {"content": "Find all j2cj-marked issues (<-- markers)", "status": "pending", "activeForm": "Finding j2cj markers"},
    {"content": "Categorize errors by type", "status": "pending", "activeForm": "Categorizing errors"},
    {"content": "Prioritize errors by severity", "status": "pending", "activeForm": "Prioritizing errors"},
    {"content": "Lookup Cangjie documentation for each error type", "status": "pending", "activeForm": "Looking up documentation"},
    {"content": "Create detailed modification plan", "status": "pending", "activeForm": "Creating modification plan"}
  ]
})
```

### Tracking Individual Error Categories

For large numbers of errors, track each category:

```javascript
// After categorizing, expand with sub-tasks
TodoWrite({
  "todos": [
    {"activeForm": "Finding j2cj markers", "content": "Find all j2cj-marked issues (<-- markers)", "status": "completed"},
    {"activeForm": "Categorizing errors", "content": "Categorize errors by type", "status": "in_progress"},
    {"activeForm": "Analyzing type errors", "content": "Analyze 'Type not found' errors (18 errors)", "status": "pending"},
    {"activeForm": "Analyzing method errors", "content": "Analyze 'Method not found' errors (12 errors)", "status": "pending"},
    {"activeForm": "Analyzing nullability errors", "content": "Analyze 'Nullability' errors (8 errors)", "status": "pending"},
    {"activeForm": "Looking up documentation", "content": "Lookup Cangjie documentation for each error type", "status": "pending"},
    {"activeForm": "Creating modification plan", "content": "Create detailed modification plan", "status": "pending"}
  ]
})
```

### Updating Status

Mark each analysis step as `in_progress` when starting, `completed` when done. Only ONE task should be `in_progress` at any time.

```javascript
// When starting documentation lookup
TodoWrite({
  "todos": [
    {"activeForm": "Finding j2cj markers", "content": "Find all j2cj-marked issues (<-- markers)", "status": "completed"},
    {"activeForm": "Categorizing errors", "content": "Categorize errors by type", "status": "completed"},
    {"activeForm": "Prioritizing errors", "content": "Prioritize errors by severity", "status": "completed"},
    {"activeForm": "Looking up documentation", "content": "Lookup Cangjie documentation for each error type", "status": "in_progress"},
    {"activeForm": "Creating modification plan", "content": "Create detailed modification plan", "status": "pending"}
  ]
})
```

### Session Resumption

To resume an interrupted analysis:

1. Check `<output_dir>/.java2cangjie_checkpoint.md` for saved progress
2. Read the checkpoint to determine which errors have been analyzed
3. Create TodoWrite with appropriate statuses based on checkpoint
4. Continue from the first non-completed step

```javascript
// Example: Resuming mid-analysis
TodoWrite({
  "todos": [
    {"activeForm": "Finding j2cj markers", "content": "Find all j2cj-marked issues (<-- markers)", "status": "completed"},
    {"activeForm": "Categorizing errors", "content": "Categorize errors by type", "status": "completed"},
    {"activeForm": "Prioritizing errors", "content": "Prioritize errors by severity", "status": "in_progress"},
    {"activeForm": "Looking up documentation", "content": "Lookup Cangjie documentation for each error type", "status": "pending"},
    {"activeForm": "Creating modification plan", "content": "Create detailed modification plan", "status": "pending"}
  ]
})
```

## Related Skills

- **java2cangjie** - Main translation skill

- **java2cangjie-translate** - Execute translation (prerequisite)
- **java2cangjie-confirm** - Confirm modifications (next step)
- **java2cangjie-fix** - Fix translation errors
- **java2cangjie-test** - Test Cangjie code
- **java2cangjie-report** - Generate translation report
