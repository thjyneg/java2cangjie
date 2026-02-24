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

### Step 1: Prepare Java Source

1. 确保Java源码可以正常编译
2. 收集依赖的classpath
3. 确定输出目录

### Step 2: Run j2cj Translation

使用 `scripts/j2cj_runner.py` 执行翻译。

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

### Step 3: Review Translation Errors

脚本会收集所有错误和警告，并在结束时输出：

```
Translation completed with errors

Errors (3):
  - MyClass.java:15: error: Type 'ArrayList' not found
  - MyClass.java:23: error: Method 'toString' not found in type 'Object'
  - MyClass.java:45: warning: Unknown annotation '@SuppressWarnings'
```

### Step 4: Fix Translation Errors

根据错误信息，使用Cangjie文档查找正确的API和语法，然后修正生成的Cangjie代码。

**错误修正流程**:
1. 识别错误类型（类型未找到、方法未找到、语法错误等）
2. 在Cangjie文档中查找对应的类型/方法
3. 参考示例代码编写正确的Cangjie代码
4. 应用修正到生成的文件

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
