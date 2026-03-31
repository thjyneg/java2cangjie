# Java2Cangjie Superpowers Plugin

基于 Superpowers 框架的 Java 到仓颉翻译插件，使用纯 AI 翻译 + 增量依赖驱动策略。

## 特性

- **纯 AI 翻译** - 不依赖 j2cj 工具，AI 直接读取 Java 源码并翻译为仓颉代码
- **增量依赖驱动** - 解析依赖 DAG，自底向上逐批翻译（每批 1-3 文件）
- **混合控制架构** - 插件工具强制工作流可靠性，技能引导翻译质量
- **双平台支持** - OpenCode（插件工具 + 技能）+ Claude Code（技能 + hooks）
- **完整仓颉文档** - 包含基础类型、标准库 API、语言手册和示例代码

## 快速开始

### 安装

将本项目作为 OpenCode 或 Claude Code 插件安装（详见设计文档 Phase 0）。

### 使用

在对话中请求翻译 Java 项目：

```
请将 /path/to/java-project 翻译为仓颉语言
```

插件会自动：
1. 分析 Java 项目结构和依赖关系
2. 按依赖顺序分批翻译（叶子文件优先）
3. 每批翻译后编译验证
4. 编译失败时查文档修复
5. 生成翻译报告

### 输出

翻译结果保存在 `<java_project>/j2cjgenerated/`，保持原始包结构。

## 项目结构

```
java2cangjie-superpowers/
├── skills/                         # 4 个技能
│   ├── using-java2cangjie/         # Bootstrap 技能
│   ├── java2cangjie-translate/     # 翻译执行
│   ├── java2cangjie-fix/           # 错误修复
│   └── java2cangjie-report/        # 报告生成
├── agents/                         # 2 个代理
│   ├── translation-reviewer.md     # 翻译质量审查
│   └── error-fixer.md              # 错误修复执行
├── .opencode/plugins/              # OpenCode 插件
├── hooks/                          # Claude Code hooks
├── docs/cangjie/                   # 仓颉语言文档
│   ├── extra/                      # 基础类型
│   ├── libs/std/                   # 标准库 API
│   ├── libs/stdx/                  # 扩展库
│   └── manual/                     # 语言手册
└── templates/checkpoint.md         # 检查点模板
```

## Java 到仓颉常用映射

| Java | 仓颉 |
|------|------|
| `ArrayList<E>` | `std.collection.ArrayList<E>` |
| `HashMap<K,V>` | `std.collection.HashMap<K,V>` |
| `null` | `Option<T>.None` 或 `??` |
| `try/catch` | `try/except` |
| `synchronized` | `std.sync.Mutex` |
| `instanceof` | `match` 模式匹配 |

## 文档查找

| 查找内容 | 路径 |
|---------|------|
| 基础类型 | `docs/cangjie/extra/` |
| 标准库 API | `docs/cangjie/libs/std/` |
| 示例代码 | `docs/cangjie/libs/std/*_samples/` |
| 语言手册 | `docs/cangjie/manual/` |

## 设计文档

完整设计规范：`docs/superpowers/specs/2026-03-31-java2cangjie-superpowers-design.md`

## 许可证

本项目包含以下组件：
- Superpowers 插件代码：MIT
- 仓颉语言文档：遵循其原始许可证
