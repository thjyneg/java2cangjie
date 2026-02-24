---
name: java2cangjie
description: "Java to Cangjie code translation using j2cj tool with post-translation error correction. Use when Claude needs to: (1) Translate Java projects/directories to Cangjie, (2) Configure j2cj translation options (mode, classpath, etc.), (3) Fix translation errors using Cangjie language docs, (4) Understand Cangjie syntax and APIs for code corrections"
---

# Java2Cangjie Translation

Java到Cangjie代码翻译技能，集成j2cj工具和仓颉语言文档，提供完整的翻译流程和错误修正能力。

## Quick Start

### 翻译Java项目

```bash
python3 scripts/j2cj_runner.py <java_source_dir> -o <output_dir> [options]
```

**示例**:
```bash
# 基本翻译
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output --mode codestyle

# 带classpath的翻译
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output -cp ./lib/* --mode codestyle

# 详细输出
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output -v --mode codestyle --json
```

## Translation Workflow

**重要：此工作流程必须严格执行，不可跳过任何步骤。**

### Step 1: j2cj转换

使用 `scripts/j2cj_runner.py` 执行初始翻译。

**Translation Modes**:
- **codestyle**: 生成符合Cangjie习惯的代码（推荐）
- **semantic**: 保持Java原有语义

**Options**:
| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory (required) |
| `--j2cj` | Path to j2cj.jar (optional, defaults to j2cj_tool/j2cj.jar) |
| `-cp, --classpath` | Java classpath |
| `-sp, --sourcepath` | Java source path |
| `-mp, --module-path` | Java module path |
| `--mode` | Translation mode: codestyle or semantic |
| `-v, --verbose` | Verbose output |
| `--encoding` | Source file encoding |
| `--json` | Output results as JSON |

**示例**:
```bash
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output --mode codestyle
```

### Step 2: 分析错误并输出修改方案

分析j2cj翻译结果中的错误和警告，**必须**基于skill中的Cangjie API文档和示例文档来制定修改方案。

**分析流程**:
1. 识别所有错误类型（类型未找到、方法未找到、语法错误、空值问题等）
2. **必须**在`docs/`目录中查找对应的类型/方法/语法
3. **必须**参考`docs/libs/*/samples/`中的示例代码
4. 为每个错误提供详细的修改方案，包括：
   - 问题分析
   - 对应的Cangjie API/语法
   - 参考的文档路径和示例代码
   - 具体的修改代码

### Step 3: 用户确认

将Step 2中的修改方案展示给用户，**必须**等待用户确认后才能进行修改。

**确认内容**:
- 显示所有修改方案
- 每个方案的改动原因
- 让用户确认是否继续修改

**示例确认格式**:
```
发现了以下错误，建议修改方案：

1. Type 'ArrayList' not found
   - 问题：Java的ArrayList需要映射到Cangjie标准库
   - 解决方案：使用 std.collection.ArrayList
   - 文档：docs/libs/std/collection/collection_package_api/...

2. Method 'toString' not found
   - 问题：Cangjie中没有直接对应的toString方法
   - 解决方案：使用工具函数或重写
   - 文档：docs/extra/String.md

是否确认执行以上修改？(y/n)
```

### Step 4: 编译并修正错误（最多20轮）

用户确认后，执行修改并尝试编译。如有错误，继续修正，最多进行20轮迭代。

**编译和修正流程**:
1. 应用用户确认的修改方案到生成的.cj文件
2. 尝试使用cjc编译（如果可用）
3. 收集编译错误和j2cj运行时错误
4. 分析新错误，回到Step 2重新分析
5. 重复Step 2-4，直到：
   - 所有错误修复成功
   - 达到20轮上限

**第N轮迭代格式**:
```
--- 迭代轮次: 3/20 ---

修改应用：
- [文件] 错误位置 -> 修正代码

编译结果：
- 成功/失败
- 新错误: (列出错误)

是否继续下一轮？
```

### Step 5: 输出转换报告

所有修正完成后，生成并输出完整的转换报告。

**报告内容**:
1. **翻译统计**
   - Java文件数量
   - 生成的Cangjie文件数量
   - 代码行数对比

2. **错误修正统计**
   - 初始错误数量
   - 修正轮次
   - 每轮修正的错误数
   - 最终未解决错误（如有）

3. **修改记录**
   - 每个文件的修改点列表
   - 修改前后的代码对比

4. **最终状态**
   - 翻译是否成功完成
   - 剩余问题和建议
   - Cangjie代码质量评估

**报告格式示例**:
```
========================================
      Java to Cangjie 转换报告
========================================

翻译统计:
  Java文件: 15
  Cangjie文件: 15
  Java代码行: 2,456
  Cangjie代码行: 2,102

错误修正统计:
  初始错误: 42
  修正轮次: 5
  总计修正: 38
  未解决错误: 4

修改记录:
  [文件名]
    - 错误1: 修正说明
    - 错误2: 修正说明

最终状态:
  翻译状态: 部分成功
  剩余问题: [列出未解决的错误]
  建议: [给出改进建议]

========================================
```

## Error Correction Guide

### Common Translation Errors

#### 1. Type Not Found

**错误示例**:
```
error: Type 'ArrayList' not found
```

**修正步骤**:
1. 在Cangjie文档中查找ArrayList对应的类型
2. 通常 `ArrayList` 映射到 `std.collection.ArrayList` 或 `Array`
3. 更新import和类型声明

**查找文档**:
```
Grep: pattern="ArrayList" path="docs/libs/std/collection/"
```

#### 2. Method Not Found

**错误示例**:
```
error: Method 'toString' not found in type 'Object'
```

**修正步骤**:
1. 查找目标类型的API文档
2. 确认方法名称和参数
3. 如无直接对应，使用工具函数或改写逻辑

**查找文档**:
```
Grep: pattern="func toString|prop toString" path="docs/"
```

#### 3. Nullability Issues

**错误示例**:
```
error: Cannot assign nullable value to non-nullable type
```

**修正步骤**:
1. 检查Cangjie的Option类型使用
2. 使用 `??` 提供默认值或正确处理空值

**查找文档**:
```
Grep: pattern="Option" path="docs/extra/Option.md"
```

## Cangjie Documentation Lookup

### Quick Lookup

**基础类型**: 见 [extra_index.md](references/extra_index.md) - Array, ArrayList, HashMap, String, Option, Tuple等

**标准库包**: 见 [packages_index.md](references/packages_index.md) - collection, io, net, sync, time等

**语言手册**: 见 [manual_index.md](references/manual_index.md) - 基础概念、类接口、泛型、并发、错误处理等

### Search Patterns

根据查询类型使用相应搜索模式：

#### 查找特定类型的API
```
Grep: pattern="<Type>" path="docs/libs/std/"
```
例如: 搜索 "ArrayList" 或 "HashMap"

#### 查找函数或方法
```
Grep: pattern="func <name>|prop <name>|init\(" path="docs/"
```

#### 查找示例代码
```
Glob: pattern="**/*samples/*.md" path="docs/libs/"
```

#### 查找语言概念
```
Grep: pattern="<keyword>" path="docs/manual/"
```
例如: 搜索 "match", "Option", "泛型"

#### 查找特定包的概览
```
docs/libs/std/<package>/<package>_package_overview.md
```

### Documentation Structure

```
docs/
├── extra/              # 基础类型和工具
├── libs/std/           # 标准库
│   └── <package>/
│       ├── *_package_overview.md      # 包概览
│       ├── *_package_api/            # API文档
│       │   ├── *_package_class.md
│       │   ├── *_package_function.md
│       │   └── *_package_interface.md
│       └── *_package_samples/        # 示例代码
├── libs/stdx/          # 扩展库
└── manual/source_zh_cn/  # 语言手册
```

## Post-Translation Verification

翻译完成后，建议进行以下验证：

1. **编译检查**: 使用cjc编译生成的Cangjie代码
2. **测试运行**: 如果可能，运行测试验证功能
3. **代码审查**: 对照Java原始代码检查逻辑一致性

## Resources

### scripts/
Executable code for j2cj translation:

- **j2cj_runner.py**: Main script for running j2cj with error collection

### j2cj_tool/
Bundled j2cj translation tool:

- **j2cj.jar**: Java to Cangjie translation tool (J2CJ 1.7.99)
- **j2cjlib/**: Cangjie library dependencies
- **j2cjlib_android/**: Android-specific library dependencies

### references/
Cangjie documentation indices:

- **packages_index.md**: Standard library and extension library package index
- **extra_index.md**: Basic types index
- **manual_index.md**: Language manual topic index

### docs/
Complete Cangjie documentation corpus including:

- **extra/**: Basic types (Array, ArrayList, HashMap, String, Option, Tuple, etc.)
- **libs/std/**: Standard library APIs with examples
- **libs/stdx/**: Extension library
- **manual/**: Language manual (syntax, types, generics, concurrency, etc.)
