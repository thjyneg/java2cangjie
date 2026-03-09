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

## TODO管理和断点续传

本skill支持TODO列表管理和断点续传功能，确保测试过程可以追踪和恢复。

### 使用TODO管理器

```python
from skills.java2cangjie_common import SkillTodoManager

# 初始化TODO管理器
manager = SkillTodoManager(
    skill_name="java2cangjie-test",
    session_id="unique_session_id"
)

# 定义测试工作流
test_workflow = [
    {"id": "compile_check", "content": "编译检查"},
    {"id": "run_tests", "content": "运行测试"},
    {"id": "code_review", "content": "代码审查"},
    {"id": "quality_assessment", "content": "质量评估"},
    {"id": "generate_report", "content": "生成测试报告"}
]

# 尝试恢复之前的进度
if manager.can_resume():
    print("从上次中断点继续测试...")
    manager.print_status()
else:
    # 创建新的TODO列表
    manager.create_workflow_todos(test_workflow)

# 执行测试步骤
while True:
    next_step = manager.get_next_pending_step()
    if not next_step:
        break

    # 开始执行步骤
    manager.start_step(next_step.id)
    try:
        # 执行步骤逻辑
        result = execute_test_step(next_step.id)

        # 完成步骤
        manager.complete_step(next_step.id, result)
    except Exception as e:
        # 失败处理
        manager.fail_step(next_step.id, str(e))
        raise

# 打印最终状态
manager.print_status()
```

### 跟踪测试执行

记录每个测试阶段的详细结果：

```python
# 在compile_check步骤中
manager.start_step("compile_check")

# 执行编译
compile_result = compile_code()

# 记录编译结果
manager.manager.create_todo(
    todo_id="compile_result",
    content=f"编译结果: {'成功' if compile_result.success else '失败'}",
    status="completed",
    metadata={
        "exit_code": compile_result.exit_code,
        "error_count": compile_result.error_count,
        "warning_count": compile_result.warning_count,
        "duration": compile_result.duration
    }
)

if compile_result.success:
    manager.manager.complete_step("compile_check", "编译成功")
else:
    # 记录每个错误
    for i, error in enumerate(compile_result.errors):
        manager.manager.create_todo(
            todo_id=f"compile_error_{i}",
            content=f"编译错误: {error['file']}:{error['line']}",
            status="pending",
            metadata=error
        )
    manager.manager.fail_step("compile_check", f"编译失败，{len(compile_result.errors)} 个错误")
```

### 跟踪测试用例

如果有多个测试用例，可以逐个跟踪：

```python
# 在run_tests步骤中
manager.start_step("run_tests")
test_cases = get_test_cases()

for i, test_case in enumerate(test_cases):
    test_id = f"test_{i}"
    manager.manager.create_todo(
        todo_id=test_id,
        content=f"测试用例: {test_case['name']}",
        status="pending",
        metadata={"test_name": test_case["name"]}
    )

    # 运行测试
    manager.manager.start_step(test_id)
    try:
        result = run_test(test_case)

        if result.passed:
            manager.manager.complete_step(test_id, "测试通过")
        else:
            manager.manager.fail_step(test_id, f"测试失败: {result.error}")

    except Exception as e:
        manager.manager.fail_step(test_id, str(e))

    # 显示进度
    if (i + 1) % 10 == 0:
        manager.print_status()

manager.complete_step("run_tests", f"完成 {len(test_cases)} 个测试用例")
```

### TODO状态跟踪

测试过程中的关键检查点：

1. **compile_check** - 编译检查，验证代码无错误
2. **run_tests** - 运行测试，验证功能正确性
3. **code_review** - 代码审查，对比Java原始代码
4. **quality_assessment** - 质量评估，评估代码质量
5. **generate_report** - 生成测试报告

每个步骤完成后会自动保存状态，支持断点续传。

### 断点续传示例

如果测试过程中断（如编译失败、测试异常等），下次启动时自动恢复：

```python
def main():
    manager = SkillTodoManager("java2cangjie-test", "session_123")

    # 检查是否有未完成的测试
    if manager.can_resume():
        print("检测到未完成的测试任务")
        manager.print_status()

        # 获取已完成和待处理的步骤
        completed = manager.manager.get_completed_todos()
        failed = manager.manager.get_failed_todos()

        if failed:
            print(f"发现 {len(failed)} 个失败的步骤")
            # 决定是否继续或重新开始
            response = ask_user("是否继续测试？(y/n)")
            if response.lower() == 'n':
                manager.clear_state()
                start_new_test(manager)
                return

        # 恢复执行
        resume_test(manager)
    else:
        # 全新开始
        start_new_test(manager)

    # 完成后清理状态
    manager.clear_state()
```

### 测试结果汇总

生成详细的测试结果汇总：

```python
# 在generate_report步骤中
manager.start_step("generate_report")

# 收集所有测试结果
compile_result = manager.manager.get_todo("compile_result")
test_results = manager.manager.get_todos_by_status("completed")
failed_tests = manager.manager.get_todos_by_status("failed")

# 生成报告
report = {
    "compilation": {
        "success": compile_result.metadata.get("exit_code") == 0,
        "errors": compile_result.metadata.get("error_count", 0),
        "warnings": compile_result.metadata.get("warning_count", 0)
    },
    "tests": {
        "total": len(test_results),
        "passed": len([t for t in test_results if "测试通过" in t.metadata.get("result", "")]),
        "failed": len(failed_tests)
    },
    "quality": {
        "readability": "Good",
        "maintainability": "Good",
        "correctness": "Verified"
    }
}

manager.manager.complete_step("generate_report", "测试报告已生成")
```

## Related Skills

- **java2cangjie** - Main translation skill
- **java2cangjie-setup** - Environment setup
- **java2cangjie-translate** - Execute translation
- **java2cangjie-analyze** - Analyze errors
- **java2cangjie-confirm** - Confirm modifications
- **java2cangjie-fix** - Fix translation errors (prerequisite)
- **java2cangjie-report** - Generate translation report (next step)
