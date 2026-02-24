# Java2Cangjie Translation Skill

Java到Cangjie代码翻译技能，集成j2cj工具和仓颉语言完整文档，提供一站式翻译解决方案。

## 特性

- **自包含**: 内置j2cj翻译工具，无需外部依赖
- **完整文档**: 包含Cangjie语言手册、标准库API和示例代码
- **错误处理**: 自动收集翻译错误，便于后续修正
- **双模式支持**: code style（代码风格优先）和 semantic（保持语义）两种翻译模式

## 快速开始

### 基本翻译

```bash
python3 scripts/j2cj_runner.py <java_source_dir> -o <output_dir>
```

### 示例

```bash
# 基本翻译
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output --mode codestyle

# 带classpath的翻译
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output -cp ./lib/* --mode codestyle

# 详细输出
python3 scripts/j2cj_runner.py ./java/src -o ./cangjie_output -v --mode codestyle --json
```

## 命令选项

| 选项 | 说明 |
|------|------|
| `-o, --output` | 输出目录（必需） |
| `--j2cj` | j2cj.jar路径（可选，默认使用内置工具） |
| `-cp, --classpath` | Java类路径 |
| `-sp, --sourcepath` | Java源代码路径 |
| `-mp, --module-path` | Java模块路径 |
| `--mode` | 翻译模式：codestyle 或 semantic |
| `-v, --verbose` | 详细输出 |
| `--encoding` | 源文件编码 |
| `--json` | 以JSON格式输出结果 |

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

翻译完成后，脚本会输出所有错误和警告。可以使用内置的Cangjie文档来查找正确的API和语法：

### 查找类型API
```bash
Grep: pattern="<Type>" path="docs/libs/std/"
```

### 查找函数或方法
```bash
Grep: pattern="func <name>|prop <name>" path="docs/"
```

### 查找示例代码
```bash
Glob: pattern="**/*samples/*.md" path="docs/libs/"
```

## 环境要求

- Python 3.6+
- Java 21+（运行j2cj.jar）

## 许可证

本项目包含以下组件：

- j2cj工具及其文档：遵循其原始许可证
- Cangjie语言文档：遵循其原始许可证

## 贡献

欢迎提交问题和改进建议！

## 相关链接

- [J2CJ官方文档](https://excelsior-usa.com/products/j2cj/)
- [Cangjie语言官网](https://www.cangjie.org/)
