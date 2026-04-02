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

### 方式一：Claude Code

Claude Code 通过 hooks 在会话启动时自动注入 Bootstrap 技能。

**步骤 1：克隆仓库**

```bash
git clone https://github.com/thjyneg/java2cangjie.git ~/.claude/plugins/java2cangjie
```

**步骤 2：注册 hooks**

在项目级 `.claude/settings.json`（或全局 `~/.claude/settings.json`）中添加：

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|clear|compact",
      "hooks": [{
        "type": "command",
        "command": "\"<插件目录>/hooks/run-hook.cmd\" session-start",
        "async": false
      }]
    }]
  }
}
```

将 `<插件目录>` 替换为实际路径，例如：

- **macOS/Linux**: `"/home/you/.claude/plugins/java2cangjie"`
- **Windows**: `"C:\\Users\\you\\.claude\\plugins\\java2cangjie"`

> **Windows 用户注意**：`run-hook.cmd` 是跨平台 polyglot 脚本，会自动调用 Git Bash 执行 hook，无需额外配置。

**步骤 3：验证**

启动新的 Claude Code 会话，系统提示应包含 Java to Cangjie 翻译系统。如果正常，输入：

```
请翻译一个 Java 项目
```

AI 会识别翻译任务并调用相应技能。

### 方式二：OpenCode

支持三种安装方式，详见 [.opencode/INSTALL.md](.opencode/INSTALL.md)。

#### 方式 2a：从 GitHub 自动安装（推荐）

在 `opencode.json`（全局 `~/.config/opencode/opencode.json` 或项目级）的 `plugin` 数组中添加：

```json
{
  "plugin": [
    "java2cangjie-superpowers@git+https://github.com/thjyneg/java2cangjie.git"
  ]
}
```

重启 OpenCode，插件会自动安装并注册所有技能和工具。

**验证**：使用 skill 工具列出技能，应包含 `java2cangjie-*` 和 `cangjie-*` 系列：

```bash
opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie
```

> **固定版本**：URL 后加 `#<tag>`，例如 `#v3.0.0`。

#### 方式 2b：项目级本地安装

将仓库克隆到项目中，通过符号链接加载插件：

```bash
git clone https://github.com/thjyneg/java2cangjie.git .java2cangjie
mkdir -p .opencode/plugins
ln -s ../../.java2cangjie/.opencode/plugins/java2cangjie.js .opencode/plugins/java2cangjie.js
```

#### 方式 2c：全局本地安装

```bash
git clone https://github.com/thjyneg/java2cangjie.git ~/.config/opencode/java2cangjie
ln -s ../java2cangjie/.opencode/plugins/java2cangjie.js ~/.config/opencode/plugins/java2cangjie.js
```

OpenCode 插件额外提供工作流控制工具：`analyze_project`、`next_batch`、`mark_complete`、`mark_blocked`、`translation_status`。

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

---

# Claude Code 版本

## 安装 (Claude Code)

### 前置要求

- Claude Code 已安装
- Cangjie 工具链已安装 (cjpm, cjc)
- Python 3.8+ (用于依赖分析脚本)

### 方式一：插件目录安装

```bash
# 克隆仓库
git clone https://github.com/thjyneg/java2cangjie.git ~/.claude/plugins/java2cangjie

# 或使用 --plugin-dir 标志
claude --plugin-dir /path/to/java2cangjie
```

### 验证安装

在 Claude Code 中运行 `/help` 并检查：
- `/j2c-translate` 命令
- `java2cangjie` 系列技能 (translate, fix, report, using-*)
- Cangjie 文档技能

## 快速开始 (Claude Code)

### 翻译 Java 项目

```bash
# 在项目目录中启动 Claude Code
cd /path/to/java-project

# 在 Claude Code 中：
/j2c-translate --java-path ./src/main/java
```

### 恢复中断的翻译

```bash
/j2c-translate --java-path ./src/main/java --resume
```

### 自定义输出目录

```bash
/j2c-translate --java-path ./src/main/java --output-dir ./cj-output
```

### 调整批处理大小

```bash
/j2c-translate --java-path ./src/main/java --max-batch-size 2
```

## Claude Code 工作流

1. **分析** - Python 脚本扫描 Java 文件，构建依赖 DAG，规划批处理
2. **翻译** - AI 将 Java 翻译为 Cangjie（小批次，1-3 个文件）
3. **编译** - 每批翻译后运行 `cjpm build`
4. **修复** - 如果编译失败，查询 Cangjie 技能进行修复（最多 3 次尝试）
5. **暂停并询问** - 3 次失败后暂停并询问用户如何继续
6. **报告** - 完成后生成翻译统计

## Claude Code 项目结构

```
java2cangjie/
├── .claude-plugin/
│   └── plugin.json              # Claude Code 清单
├── commands/
│   └── j2c-translate.md        # 主翻译命令
├── scripts/
│   └── analyze_deps.py         # 依赖分析脚本
├── skills/                      # Cangjie 文档技能
├── agents/                      # 已存在
└── .opencode/                   # OpenCode 插件（保持原有）
```

## 错误处理 (Claude Code)

当编译失败时：

1. 加载 `java2cangjie-fix` 技能
2. 查询相关 Cangjie 技能
3. 应用修复并重试编译
4. 3 次失败后：暂停并询问用户
