# Installing Java2Cangjie for OpenCode

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- 仓颉工具链已安装（`cjpm`、`cjc`），用于编译验证

## Installation

Add java2cangjie to the `plugin` array in your `opencode.json` (global `~/.config/opencode/opencode.json` or project-level):

```json
{
  "plugin": ["java2cangjie@git+https://github.com/thjyneg/java2cangjie.git"]
}
```

Restart OpenCode. The plugin auto-installs via Bun and registers all skills.

Verify by asking: "列出你的 java2cangjie 技能"

> **Pin a version**: Append `#<tag>` to the URL, e.g. `#v3.3.0`.

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load java2cangjie-translate
use skill tool to load cangjie-std
```

## 验证安装

重启 OpenCode 后：

1. **检查 Skills** — 输入 "列出你的 java2cangjie 技能"，应显示 `java2cangjie-*` 和 `cangjie-*` 共 10 个技能
2. **检查 Tools** — 使用 `/tools` 命令，应包含 `analyze_project`、`next_batch`、`compile_batch` 等工具

> Skills 和 bootstrap 注入无需任何外部依赖，始终可用。Tools 需要 `@opencode-ai/plugin`（Option 2/3 通过 `bun install` 自动安装；Option 1 由 OpenCode 运行时提供）。

## Plugin Tools

| Tool | Description |
|------|-------------|
| `analyze_project` | Scan Java project, build dependency DAG, return batch plan |
| `next_batch` | Get next batch of files ready for translation (enforces one-at-a-time) |
| `compile_batch` | Run `cjpm build`, auto-complete on success, return errors on failure |
| `mark_complete` | Manual override: mark batch as completed (prefer compile_batch) |
| `mark_blocked` | Mark batch as blocked after max retries |
| `translation_status` | Get current progress |

## Skills (10)

| Skill | Description |
|-------|-------------|
| `using-java2cangjie` | Bootstrap — auto-injected on session start, introduces all skills |
| `java2cangjie-translate` | Java-to-Cangjie mapping rules, type conversions, keyword handling |
| `java2cangjie-fix` | Compilation error fixing — DAG-based, one-at-a-time, doc lookup |
| `java2cangjie-report` | Translation report generation with statistics |
| `cangjie-lang-features` | Core language: syntax, generics, concurrency, error handling |
| `cangjie-std` | Standard library: collections, IO, filesystem, string, testing |
| `cangjie-stdx` | Extended library: JSON encoding/decoding, configuration |
| `cangjie-toolchains` | Toolchain: cjc, cjdb, cjfmt, cjlint, cjprof |
| `cangjie-regulations` | Project structure, naming conventions, best practices |
| `cangjie-original-docs` | Full original Cangjie documentation fallback |

## Tool Mapping

When skills reference Claude Code tools:

- `TodoWrite` → `todowrite`
- `Skill` tool → OpenCode's native `skill` tool
- `Read`, `Write`, `Edit`, `Bash` → Your native tools
- Plugin tools: `analyze_project`, `next_batch`, `compile_batch`, `mark_complete`, `mark_blocked`, `translation_status`

## Updating

Java2Cangjie updates automatically when you restart OpenCode. The plugin is re-installed from the git repository on each launch.

To pin a specific version, use a branch or tag:

```json
{
  "plugin": ["java2cangjie@git+https://github.com/thjyneg/java2cangjie.git#v3.3.0"]
}
```

## Troubleshooting

### Skills 不显示

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Tools 不显示

1. Use `skill` tool to list discovered skills
2. Check plugin loaded (see above)
3. Each skill needs a `SKILL.md` file with valid YAML frontmatter

### Bootstrap not appearing

1. Check OpenCode version supports `experimental.chat.messages.transform` hook
2. Restart OpenCode after config changes

### Claude Code 用户

参见项目根目录 [README.md](../README.md)。
