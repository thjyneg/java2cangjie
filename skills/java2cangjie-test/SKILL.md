---
name: java2cangjie-test
description: "Use when compiling Cangjie code, running tests, or performing code quality verification after fixing translation errors"
---

# Java to Cangjie Translation - Step 6: Test Code

## Overview

This skill compiles and tests the Cangjie code after all fixes are complete. It verifies that the translated code compiles successfully, runs tests if available, and performs a quality review.

## Prerequisites

Before using this skill, ensure:

- All errors are fixed (use `java2cangjie-fix` skill)
- Output directory contains Cangjie files
- cjpm is available for compilation

## Testing Process

### 1. Compilation Check

Compile the Cangjie code to ensure no errors remain.

**Change to output directory:**
```bash
cd <output_dir>
```

**Compile the project:**
```bash
cjpm build
```

**Check exit code:**
```bash
echo $?
```

**Expected result:**
- Exit code 0: Compilation successful
- Exit code non-zero: Compilation failed

**If compilation fails:**

1. **Read error output:**
```bash
cjpm build 2>&1 | tee build_errors.log
```

2. **Analyze errors:**
```bash
# Count errors
grep "^error:" build_errors.log | wc -l

# List error files
grep "^error:" build_errors.log | cut -d':' -f1 | sort -u
```

3. **Fix remaining errors:**
   - Return to `java2cangjie-fix` skill
   - Fix each error
   - Compile again

### 2. Test Execution

If tests are available, run them to verify functionality.

**Run tests:**
```bash
cd <output_dir>
cjpm test
```

**Check test results:**
```bash
echo $?
```

**Expected result:**
- Exit code 0: All tests pass
- Exit code non-zero: Some tests failed

**If tests fail:**

1. **Analyze test failures:**
```bash
# View test output
cjpm test 2>&1 | tee test_results.log

# Find failed tests
grep "FAILED\|ERROR" test_results.log
```

2. **Debug failures:**
   - Review test code
   - Check implementation
   - Compare with Java original
   - Fix issues

3. **Re-run tests:**
```bash
cjpm test
```

### 3. Code Review

Compare the Cangjie code with the Java original to verify logic correctness.

**Review Checklist:**

- [ ] **Business logic preserved**
  - Algorithms are correctly translated
  - Control flow is maintained
  - Data transformations are correct

- [ ] **Edge cases handled**
  - Null values handled properly
  - Empty collections handled
  - Boundary conditions checked

- [ ] **Error handling appropriate**
  - Exceptions are properly converted
  - Error messages are preserved
  - Error recovery logic maintained

- [ ] **Performance characteristics maintained**
  - No unnecessary allocations
  - Appropriate data structures used
  - No performance regressions

- [ ] **Security considerations addressed**
  - Input validation preserved
  - No new security vulnerabilities
  - Sensitive data handling correct

### 4. Quality Assessment

Assess the overall quality of the translated code.

**Code Quality Metrics:**

- **Readability**: Code is easy to understand
- **Maintainability**: Code is easy to modify
- **Cangjie Idioms**: Code follows Cangjie best practices
- **Performance**: Code performs equivalently to Java
- **Correctness**: Code produces correct results

**Quality Report:**

```markdown
# Code Quality Assessment

## Readability: Good
- Code structure is clear
- Variable names are meaningful
- Comments are appropriate

## Maintainability: Good
- Code is modular
- Dependencies are minimal
- Changes are localized

## Cangjie Idioms: Mostly Followed
- Uses standard library APIs
- Follows Cangjie conventions
- Some Java-style patterns remain

## Performance: Equivalent
- No performance regressions
- Appropriate data structures
- Efficient algorithms

## Correctness: Verified
- Compilation successful
- Tests pass (if available)
- Logic matches Java original
```

## Common Testing Issues

### Issue 1: Compilation Errors Remain

**Symptoms:**
- `cjpm build` exits with non-zero code
- Error messages in output

**Solutions:**
1. Review all errors
2. Return to `java2cangjie-fix` skill
3. Fix each error one by one
4. Compile after each fix

### Issue 2: Test Failures

**Symptoms:**
- `cjpm test` exits with non-zero code
- Test output shows failures

**Solutions:**
1. Analyze test failures
2. Compare with Java test results
3. Check implementation logic
4. Fix issues and re-test

### Issue 3: Logic Differences

**Symptoms:**
- Code compiles and tests pass
- But behavior differs from Java

**Solutions:**
1. Compare Java and Cangjie code
2. Identify differences
3. Research Cangjie semantics
4. Adjust implementation

### Issue 4: Performance Issues

**Symptoms:**
- Code is slower than Java
- Memory usage is higher

**Solutions:**
1. Profile the code
2. Identify bottlenecks
3. Optimize data structures
4. Use Cangjie-specific optimizations

## Testing Checklist

Before proceeding to report:

- [ ] Compilation succeeds (exit code 0)
- [ ] No compilation errors
- [ ] No compilation warnings (or warnings are reviewed)
- [ ] Tests pass (if available)
- [ ] Code review completed
- [ ] Business logic verified
- [ ] Edge cases checked
- [ ] Error handling verified
- [ ] Performance assessed
- [ ] Quality report generated

## Example Testing Workflow

```bash
# Step 1: Compile
cd <output_dir>
cjpm build

# Check result
if [ $? -eq 0 ]; then
    echo "Compilation successful"
else
    echo "Compilation failed, fixing errors..."
    # Return to java2cangjie-fix skill
fi

# Step 2: Run tests (if available)
cjpm test

# Check result
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Some tests failed, analyzing..."
    # Review test failures and fix
fi

# Step 3: Code review
# Compare with Java original
# Verify logic correctness
# Check edge cases

# Step 4: Quality assessment
# Generate quality report
# Document findings
```

## Success Criteria

Testing is successful when:

- [ ] All files compile without errors
- [ ] All tests pass (if available)
- [ ] Code review shows no critical issues
- [ ] Business logic is preserved
- [ ] Performance is acceptable
- [ ] Quality metrics are satisfactory

## Failure Criteria

Testing has failed when:

- [ ] Compilation errors remain after multiple attempts
- [ ] Critical test failures cannot be resolved
- [ ] Business logic is incorrect
- [ ] Performance is unacceptable
- [ ] Quality metrics are below threshold

## Next Steps

After successful testing:

1. Use `java2cangjie-report` skill to generate final translation report
2. Document any remaining issues
3. Provide recommendations for future work

After failed testing:

1. Return to `java2cangjie-fix` skill to address issues
2. Re-run testing after fixes
3. Escalate if issues cannot be resolved

## TodoWrite Task Management

Use TodoWrite to track the testing and verification process.

### Creating the TODO List

When starting testing, create a TODO list for the testing workflow:

```javascript
TodoWrite({
  "todos": [
    {"content": "Compile Cangjie code with cjpm build", "status": "pending", "activeForm": "Compiling Cangjie code"},
    {"content": "Run tests with cjpm test", "status": "pending", "activeForm": "Running tests"},
    {"content": "Review code and compare with Java original", "status": "pending", "activeForm": "Reviewing code"},
    {"content": "Assess code quality metrics", "status": "pending", "activeForm": "Assessing code quality"},
    {"content": "Generate quality report", "status": "pending", "activeForm": "Generating quality report"}
  ]
})
```

### Tracking Compilation Results

If compilation fails, track error resolution:

```javascript
// After compilation failure
TodoWrite({
  "todos": [
    {"activeForm": "Compiling Cangjie code", "content": "Compile Cangjie code with cjpm build", "status": "in_progress"},
    {"activeForm": "Fixing compilation error", "content": "Fix compilation error: Service.cj:15 Type not found", "status": "pending"},
    {"activeForm": "Fixing compilation error", "content": "Fix compilation error: Helper.cj:42 Method not found", "status": "pending"},
    {"activeForm": "Re-compiling code", "content": "Re-compile after fixes", "status": "pending"},
    {"activeForm": "Running tests", "content": "Run tests with cjpm test", "status": "pending"},
    {"activeForm": "Reviewing code", "content": "Review code and compare with Java original", "status": "pending"},
    {"activeForm": "Assessing code quality", "content": "Assess code quality metrics", "status": "pending"}
  ]
})
```

### Tracking Test Cases

For multiple test cases, track each one:

```javascript
// After identifying test cases
TodoWrite({
  "todos": [
    {"activeForm": "Compiling Cangjie code", "content": "Compile Cangjie code with cjpm build", "status": "completed"},
    {"activeForm": "Running UserServiceTest", "content": "Run test: UserServiceTest", "status": "in_progress"},
    {"activeForm": "Running DataServiceTest", "content": "Run test: DataServiceTest", "status": "pending"},
    {"activeForm": "Running ControllerTest", "content": "Run test: ControllerTest", "status": "pending"},
    {"activeForm": "Reviewing code", "content": "Review code and compare with Java original", "status": "pending"},
    {"activeForm": "Assessing code quality", "content": "Assess code quality metrics", "status": "pending"}
  ]
})
```

### Session Resumption

To resume an interrupted test process:

1. Check checkpoint file at `<output_dir>/.java2cangjie_checkpoint.md`
2. Read the checkpoint to determine which tests have been run
3. Create TodoWrite with appropriate statuses based on checkpoint
4. Continue from the first non-completed step

```javascript
// Example: Resuming mid-test
TodoWrite({
  "todos": [
    {"activeForm": "Compiling Cangjie code", "content": "Compile Cangjie code with cjpm build", "status": "completed"},
    {"activeForm": "Running tests", "content": "Run tests with cjpm test", "status": "in_progress"},
    {"activeForm": "Reviewing code", "content": "Review code and compare with Java original", "status": "pending"},
    {"activeForm": "Assessing code quality", "content": "Assess code quality metrics", "status": "pending"},
    {"activeForm": "Generating quality report", "content": "Generate quality report", "status": "pending"}
  ]
})
```

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup
- **java2cangjie-translate** - Execute translation
- **java2cangjie-analyze** - Analyze errors
- **java2cangjie-confirm** - Confirm modifications
- **java2cangjie-fix** - Fix translation errors (prerequisite)
- **java2cangjie-report** - Generate translation report (next step)
