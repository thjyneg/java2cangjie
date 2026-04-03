# Installing Java2Cangjie for OpenCode

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- 仓颉工具链已安装（`cjpm`、`cjc`），用于编译验证

## Installation

### Option 1: Git-based auto-install (recommended)

Add to `opencode.json` (global `~/.config/opencode/opencode.json` or project-level):

```json
{
  "plugin": ["java2cangjie@git+https://github.com/thjyneg/java2cangjie.git"]
}
```

Restart OpenCode. The plugin auto-installs via Bun (cached in `~/.cache/opencode/node_modules/`).

Verify: ask "列出你的 java2cangjie 技能" — should list `java2cangjie-*` and `cangjie-*` skills.

> **Pin a version**: Append `#<tag>` to the URL, e.g. `#v3.2.0`.

### Option 2: Project-level local

OpenCode auto-loads JS files from `.opencode/plugins/`:

```bash
git clone https://github.com/thjyneg/java2cangjie.git .java2cangjie
mkdir -p .opencode/plugins
ln -s ../../.java2cangjie/.opencode/plugins/java2cangjie.js .opencode/plugins/java2cangjie.js
```

Then install dependencies:

```bash
cd .java2cangjie/.opencode && bun install
```

### Option 3: Global local

```bash
git clone https://github.com/thjyneg/java2cangjie.git ~/.config/opencode/java2cangjie
ln -s ../java2cangjie/.opencode/plugins/java2cangjie.js ~/.config/opencode/plugins/java2cangjie.js
cd ~/.config/opencode/java2cangjie/.opencode && bun install
```

## Plugin Tools

The plugin registers 6 custom tools for workflow control:

| Tool | Args | Description |
|------|------|-------------|
| `analyze_project` | `javaPath` (string or string[]), `maxBatchSize` (number), `outputDir?` (string) | Scan Java project, build dependency DAG, return batch plan |
| `next_batch` | — | Get next batch of files ready for translation |
| `compile_batch` | `batchId` (string), `outputFiles?` (string[]) | Run `cjpm build`, auto-complete on success, return errors on failure |
| `mark_complete` | `batchId` (string), `outputFiles?` (string[]) | Mark batch as completed successfully |
| `mark_blocked` | `batchId` (string), `reason` (string) | Mark batch as failed after max retries |
| `translation_status` | — | Get current progress |

## Skills (10)

| Skill | Description |
|-------|-------------|
| `using-java2cangjie` | Bootstrap skill — auto-injected on session start, introduces all skills |
| `java2cangjie-translate` | Java-to-Cangjie mapping rules, type conversions, keyword handling, mock strategy |
| `java2cangjie-fix` | Compilation error fixing — DAG-based, one-at-a-time, doc lookup mandatory |
| `java2cangjie-report` | Translation report generation with statistics |
| `cangjie-lang-features` | Core language: syntax, generics, concurrency, error handling, pattern matching |
| `cangjie-std` | Standard library: collections, IO, filesystem, string, testing |
| `cangjie-stdx` | Extended library: JSON encoding/decoding, configuration, encoding utilities |
| `cangjie-toolchains` | Toolchain tools: cjc, cjdb, cjcov, cjfmt, cjlint, cjprof |
| `cangjie-regulations` | Project structure, naming conventions, formatting, testing best practices |
| `cangjie-original-docs` | Full original Cangjie documentation fallback (kernel, std, stdx, tools) |

## Tool Mapping

When skills reference Claude Code tools:

- `TodoWrite` → `todowrite`
- `Skill` tool → OpenCode's native `skill` tool
- `Read`, `Write`, `Edit`, `Bash` → Your native tools
- Plugin tools: `analyze_project`, `next_batch`, `compile_batch`, `mark_complete`, `mark_blocked`, `translation_status`

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie`
2. Verify `package.json` exists in `.opencode/` and `bun install` was run
3. Make sure `@opencode-ai/plugin` dependency is installed

### Skills not found

1. Use `skill` tool to list discovered skills
2. Check plugin loaded (see above)
3. For local install, verify symlink points correctly

## Claude Code Users

See project root [README.md](../README.md) for Claude Code installation.
