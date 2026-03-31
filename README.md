# Java2Cangjie Superpowers Plugin

基于 Superpowers 框架的 Java 到仓颉翻译插件，使用纯 AI 翻译 + 增量依赖驱动策略。

## 特性

- **纯 AI 翻译** - 不依赖 j2cj 工具，AI 直接读取 Java 源码并翻译为仓颉代码
- **增量依赖驱动** - 解析依赖 DAG，自底向上逐批翻译（每批 1-3 文件）
- **混合控制架构** - 插件工具强制工作流可靠性，技能引导翻译质量
- **双平台支持** - OpenCode（插件工具 + 技能）+ Claude Code（技能 + hooks）
- **完整仓颉文档** - 包含基础类型、标准库 API、语言手册和示例代码

## 安装

### 前置要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或 [OpenCode](https://opencode.ai/) 已安装
- 仓颉编译器 `cjpm` 已安装（用于编译验证，可选）

### 方式一：Claude Code 插件

```bash
# 1. 克隆仓库到 Claude Code 插件目录
git clone https://gitcode.com/zwcoder/java2cangjie.git ~/.claude/plugins/java2cangjie

# 2. 验证安装成功 — 启动新的 Claude Code 会话，检查系统提示包含 Java to Cangjie 翻译系统
claude

# 3.（可选）将插件添加到项目级 .claude/settings.json
# 在 "permissions" 中允许插件目录访问
```

安装后 Claude Code 会通过 `hooks/session-start` 自动注入 Bootstrap 技能到系统提示。

### 方式二：OpenCode 插件

```bash
# 1. 克隆仓库
git clone https://gitcode.com/zwcoder/java2cangjie.git ~/plugins/java2cangjie

# 2. 在项目根目录创建或编辑 .opencode/plugins/java2cangjie.js
# 内容为：
#   export { Java2CangjiePlugin } from '~/plugins/java2cangjie/.opencode/plugins/java2cangjie.js'

# 3. 或直接在 OpenCode 配置中指定插件路径
# .opencode/config.json:
# {
#   "plugins": ["~/plugins/java2cangjie/.opencode/plugins/java2cangjie.js"]
# }

# 4. 验证：启动 OpenCode，检查 skill 工具是否列出 java2cangjie-* 和 cangjie-* 技能
opencode
```

OpenCode 插件提供额外的工作流控制工具：`analyze_project`、`next_batch`、`mark_complete`、`mark_blocked`、`translation_status`。

### 验证安装

安装成功后，在新会话中输入：

```
请翻译一个 Java 项目
```

如果插件正常加载，AI 会识别翻译任务并调用相应的翻译技能。

## 快速开始

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
├── skills/                         # 10 个技能
│   ├── using-java2cangjie/         # Bootstrap 技能
│   ├── java2cangjie-translate/     # 翻译执行
│   ├── java2cangjie-fix/           # 错误修复 + error-patterns.md
│   ├── java2cangjie-report/        # 报告生成
│   ├── cangjie-lang-features/      # 仓颉语言特性
│   ├── cangjie-std/                # 标准库速查
│   ├── cangjie-stdx/               # 扩展标准库
│   ├── cangjie-toolchains/         # 工具链文档
│   ├── cangjie-regulations/        # 编码规范
│   └── cangjie-original-docs/      # 原始文档 fallback
├── agents/                         # 3 个代理
│   ├── cangjie-engineer.md         # 仓颉开发专家
│   ├── translation-reviewer.md     # 翻译质量审查
│   └── error-fixer.md              # 错误修复执行
├── .opencode/plugins/              # OpenCode 插件 (tools + config + bootstrap)
├── hooks/                          # Claude Code hooks (session-start)
├── docs/                           # 设计文档
│   └── superpowers/specs/          # 设计规范
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

| 查找内容 | 技能 |
|---------|------|
| 语言语法/特性 | `cangjie-lang-features` |
| 标准库 API | `cangjie-std` |
| 扩展库 (JSON/配置等) | `cangjie-stdx` |
| 编译器/工具链 | `cangjie-toolchains` |
| 编码规范 | `cangjie-regulations` |
| 完整原始文档 | `cangjie-original-docs` |

## 设计文档

完整设计规范：`docs/superpowers/specs/2026-03-31-java2cangjie-superpowers-design.md`

## 许可证

本项目包含以下组件：
- Superpowers 插件代码：MIT
- 仓颉语言文档：遵循其原始许可证
