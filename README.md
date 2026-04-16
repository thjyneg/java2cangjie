# Java2Cangjie Plugin

Java 到仓颉翻译插件，使用纯 AI 翻译 + 增量依赖驱动策略。支持 Claude Code 和 OpenCode。

## 特性

- **纯 AI 翻译** - 不依赖 j2cj 工具，AI 直接读取 Java 源码并翻译为仓颉代码
- **增量依赖驱动** - 解析依赖 DAG，自底向上逐批翻译（每批 1-3 文件）
- **三方 API Mock** - 自动为无仓颉对应的 Java API 生成 stub，确保编译通过
- **双平台支持** - OpenCode（插件工具 + 技能）+ Claude Code（技能 + hooks）
- **完整仓颉文档** - 包含语言特性、标准库 API、工具链和编码规范

## 安装

### 前置要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或 [OpenCode](https://opencode.ai/) 已安装
- 仓颉工具链已安装（`cjpm`、`cjc`），用于编译验证
- Python 3.8+（可选，用于依赖分析脚本）

### 方式一：Claude Code（推荐 --plugin-dir 方式）

最简方式，无需克隆或配置 hooks：

```bash
cd /path/to/your-java-project
claude --plugin-dir /path/to/java2cangjie
```

启动后直接用自然语言请求翻译即可：

```
请将这个 Java 项目翻译为仓颉语言
```

> **提示**：`--plugin-dir` 会自动加载插件的 skills、agents 和 hooks，SessionStart hook 自动注入翻译系统引导。

### 方式二：Claude Code（全局安装）

适合经常使用翻译功能的用户。

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

启动新的 Claude Code 会话，系统提示应包含 Java to Cangjie 翻译系统。

详细的 Claude Code 安装说明见 [docs/README.claude-code.md](docs/README.claude-code.md)。

### 方式二：OpenCode

告诉 OpenCode：

```
Fetch and follow instructions from https://raw.githubusercontent.com/thjyneg/java2cangjie/master/.opencode/INSTALL.md
```

OpenCode 会自动获取安装指南并执行安装。

> 详细文档见 [.opencode/INSTALL.md](.opencode/INSTALL.md)。

## 快速开始

在对话中请求翻译 Java 项目：

```
请将 /path/to/java-project 翻译为仓颉语言
```

插件会自动：
1. 分析 Java 项目结构和依赖关系
2. 为无对应的三方 API 创建 mock stub
3. 按依赖顺序分批翻译（叶子文件优先）
4. 每批翻译后编译验证
5. 编译失败时查文档修复（最多 3 次，之后暂停询问用户）
6. 生成翻译报告

翻译结果保存在 `<java_project>/j2cjgenerated/`，保持原始包结构。

## 项目结构

```
java2cangjie/
├── .claude-plugin/
│   └── plugin.json              # Claude Code 清单
├── skills/                      # 10 个技能
│   ├── using-java2cangjie/      # Bootstrap 技能
│   ├── java2cangjie-translate/  # 翻译映射规则
│   ├── java2cangjie-fix/        # 错误修复
│   ├── java2cangjie-report/     # 报告生成
│   ├── cangjie-lang-features/   # 仓颉语言特性
│   ├── cangjie-std/             # 标准库速查
│   ├── cangjie-stdx/            # 扩展标准库
│   ├── cangjie-toolchains/      # 工具链文档
│   ├── cangjie-regulations/     # 编码规范
│   └── cangjie-original-docs/   # 完整原始文档 fallback
├── agents/                      # 3 个代理
│   ├── cangjie-engineer.md      # 仓颉开发专家
│   ├── translation-reviewer.md  # 翻译质量审查
│   └── error-fixer.md           # 错误修复执行
├── hooks/                       # Claude Code hooks (SessionStart)
├── scripts/                     # Python 依赖分析脚本
└── .opencode/                   # OpenCode 插件（工具 + 配置）
```

## Java 到仓颉常用映射

| Java | 仓颉 |
|------|------|
| `ArrayList<E>` | `std.collection.ArrayList<E>` |
| `HashMap<K,V>` | `std.collection.HashMap<K,V>` |
| `null` | `None` / `?? default` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try { } catch(e: Exception) { }` |
| `synchronized` | `std.sync.ReentrantMutex` |
| `instanceof` | `if (let Some(x) <- obj as Type)` |
| `~value` (位运算 NOT) | `(-1) ^ value` |
| `byte[]` | `Array<Byte>` |

## 文档查找

| 查找内容 | 技能 |
|---------|------|
| 语言语法/特性 | `cangjie-lang-features` |
| 标准库 API | `cangjie-std` |
| 扩展库 (JSON/编码等) | `cangjie-stdx` |
| 编译器/工具链 | `cangjie-toolchains` |
| 编码规范 | `cangjie-regulations` |
| 完整原始文档 | `cangjie-original-docs` |

## 许可证

- 插件代码：Apache-2.0
- 仓颉语言文档：遵循其原始许可证
