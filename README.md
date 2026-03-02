# Java2Cangjie Translation Skill

Java到Cangjie代码翻译技能，集成j2cj工具和仓颉语言完整文档，提供一站式翻译解决方案。

## 特性

- **自包含**: 内置j2cj翻译工具，无需外部依赖
- **完整文档**: 包含Cangjie语言手册、标准库API和示例代码
- **错误处理**: 自动收集翻译错误，便于后续修正
- **双模式支持**: code style（代码风格优先）和 semantic（保持语义）两种翻译模式
- **自动化工作流**: 5步翻译流程，从转换到错误修正再到报告生成

## 快速开始

## 翻译工作流

本技能强制执行严格的5步翻译流程，确保翻译质量和错误处理：

### Step 1: j2cj转换

使用 `scripts/j2cj_runner.py` 执行初始翻译。

- **codestyle模式**: 生成符合Cangjie习惯的代码（推荐）
- **semantic模式**: 保持Java原有语义

输出目录说明：
- 默认输出到当前工作目录的 `cangjie_output` 目录
- 生成的文件按照原Java源码的目录结构存放

### Step 2: 分析错误并输出修改方案

分析j2cj翻译结果中的错误和警告，基于skill中的Cangjie API文档和示例文档制定修改方案：

1. 识别所有错误类型（类型未找到、方法未找到、语法错误、空值问题等）
2. 在`docs/`目录中查找对应的类型/方法/语法
3. 参考`docs/libs/*/samples/`中的示例代码
4. 为每个错误提供详细的修改方案

### Step 3: 用户确认

将修改方案展示给用户，等待用户确认后才能进行修改。

### Step 4: 编译并修正错误（最多20轮）

用户确认后，执行修改并尝试编译，如有错误继续修正，最多进行20轮迭代。

### Step 5: 输出转换报告

所有修正完成后，生成并输出完整的转换报告，包括翻译统计、错误修正统计、修改记录和最终状态。

## 翻译模式

### Code Style（代码风格优先）
- 生成符合Cangjie习惯的代码
- 自动解析可空标记
- 推荐用于新项目翻译

### Semantic（保持语义）
- 尽可能保持Java原有语义
- 可能需要j2cjlib库支持
- 适用于需要精确保持原有行为的场景

## 项目结构

```
java2cangjie/
├── SKILL.md              # Claude技能说明
├── README.md             # 项目说明（本文件）
├── scripts/
│   └── j2cj_runner.py  # j2cj执行脚本
├── j2cj_tool/           # 内置j2cj翻译工具
│   ├── j2cj.jar        # J2CJ 1.7.99
│   ├── j2cjlib/        # Cangjie库依赖
│   └── j2cjlib_android/ # Android专用库
├── docs/                # Cangjie语言文档
│   ├── extra/          # 基础类型
│   ├── libs/std/       # 标准库API
│   ├── libs/stdx/      # 扩展库
│   └── manual/         # 语言手册
└── references/           # 文档索引
```

## 错误修正

### 常见翻译错误

#### 1. Type Not Found
```
error: Type 'ArrayList' not found
```
修正：`ArrayList` 通常映射到 `std.collection.ArrayList` 或 `Array`，需要更新import和类型声明。

#### 2. Method Not Found
```
error: Method 'toString' not found in type 'Object'
```
修正：查找目标类型的API文档，确认方法名称和参数，使用工具函数或改写逻辑。

#### 3. Nullability Issues
```
error: Cannot assign nullable value to non-nullable type
```
修正：检查Cangjie的Option类型使用，使用 `??` 提供默认值或正确处理空值。

### 文档查找方法

| 查找内容 | 搜索模式 |
|---------|---------|
| 类型API | `Grep: pattern="<Type>" path="docs/libs/std/"` |
| 函数或方法 | `Grep: pattern="func <name>|prop <name>|init\(" path="docs/"` |
| 示例代码 | `Glob: pattern="**/*samples/*.md" path="docs/libs/"` |
| 语言概念 | `Grep: pattern="<keyword>" path="docs/manual/"` |

### 快速参考

- **基础类型**: `docs/extra/` - Array, ArrayList, HashMap, String, Option, Tuple, Numbers
- **标准库**: `docs/libs/std/` - collection, io, net, sync, time 等
- **扩展库**: `docs/libs/stdx/` - HTTP, 压缩, 编码, 序列化, 日志
- **语言手册**: `docs/manual/` - 语法, 类型, 泛型, 并发, 错误处理
- **索引**: `references/` - packages_index.md, extra_index.md, manual_index.md

## 环境要求

- Python 3.6+
- Java 21+（运行j2cj.jar）
- cjc（Cangjie编译器，可选，用于验证）

## Java to Cangjie 常用映射

| Java | Cangjie |
|------|---------|
| `ArrayList<E>` | `std.collection.ArrayList<E>` 或 `Array<E>` |
| `HashMap<K,V>` | `std.collection.HashMap<K,V>` |
| `HashSet<E>` | `std.collection.HashSet<E>` |
| `null` | `Option<T>` 的 `None` 或可空类型 |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `interface` | `interface` |
| `class` | `class` |
| `@Override` | 不需要注解（隐式） |

## 许可证

本项目包含以下组件：

- j2cj工具及其文档：遵循其原始许可证
- Cangjie语言文档：遵循其原始许可证

## 贡献

欢迎提交问题和改进建议！

## 相关链接

- [J2CJ官方文档](https://excelsior-usa.com/products/j2cj/)
- [Cangjie语言官网](https://www.cangjie.org/)
