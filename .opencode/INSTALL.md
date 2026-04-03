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

Restart OpenCode. The plugin auto-installs and registers all skills and tools.

Verify by asking: "列出你的 java2cangjie 技能"

> **Pin a version**: Append `#<tag>` to the URL, e.g. `#v3.2.0`.

## Local Installation (alternative)

If you prefer not to use git-based auto-install, place the plugin file in OpenCode's auto-scan directory:

### Project-level

OpenCode auto-loads JS files from `.opencode/plugins/`:

```bash
git clone https://github.com/thjyneg/java2cangjie.git .java2cangjie
mkdir -p .opencode/plugins
ln -s ../../.java2cangjie/.opencode/plugins/java2cangjie.js .opencode/plugins/java2cangjie.js
```

### Global

```bash
git clone https://github.com/thjyneg/java2cangjie.git ~/.config/opencode/java2cangjie
ln -s ../java2cangjie/.opencode/plugins/java2cangjie.js ~/.config/opencode/plugins/java2cangjie.js
```

## Plugin Tools

| Tool | Description |
|------|-------------|
| `analyze_project` | Scan Java project, build dependency DAG, return batch plan |
| `next_batch` | Get next batch of files ready for translation |
| `compile_batch` | Run `cjpm build`, auto-complete on success, return errors on failure |
| `mark_complete` | Mark batch as completed successfully |
| `mark_blocked` | Mark batch as failed after max retries |
| `translation_status` | Get current progress |

## Skills (10)

| Skill | Description |
|-------|-------------|
| `using-java2cangjie` | Bootstrap skill (auto-injected on session start) |
| `java2cangjie-translate` | Translation mapping rules and patterns |
| `java2cangjie-fix` | Compilation error fixing with doc lookup |
| `java2cangjie-report` | Translation report generation |
| `cangjie-lang-features` | Core language features: syntax, generics, concurrency |
| `cangjie-std` | Standard library quick reference |
| `cangjie-stdx` | Extended library: JSON, config, encoding |
| `cangjie-toolchains` | Toolchain docs: cjc, cjpm, cjfmt, cjlint |
| `cangjie-regulations` | Coding conventions and best practices |
| `cangjie-original-docs` | Full original documentation fallback |

## Tool Mapping

When skills reference Claude Code tools:

- `TodoWrite` → `todowrite`
- `Skill` tool → OpenCode's native `skill` tool
- `Read`, `Write`, `Edit`, `Bash` → Your native tools
- Plugin tools: `analyze_project`, `next_batch`, `compile_batch`, `mark_complete`, `mark_blocked`, `translation_status`

## Claude Code Users

See project root [README.md](../README.md) for Claude Code installation.
