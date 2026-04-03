# Installing Java2Cangjie for OpenCode

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- 仓颉工具链已安装（`cjpm`、`cjc`），用于编译验证

## Installation

### Option 1: Git-based auto-install (recommended)

Add to `opencode.json`（全局 `~/.config/opencode/opencode.json` 或项目级）:

```json
{
  "plugin": ["java2cangjie@git+https://github.com/thjyneg/java2cangjie.git"]
}
```

重启 OpenCode 即可。插件通过 Bun 自动安装并缓存。

> **固定版本**: 在 URL 后加 `#<tag>`，如 `#v3.3.0`。

### Option 2: 项目级本地安装

将插件文件放入项目的 `.opencode/plugins/` 目录：

```bash
# 克隆仓库到项目根目录
git clone https://github.com/thjyneg/java2cangjie.git .java2cangjie

# 创建符号链接
mkdir -p .opencode/plugins
ln -s ../../.java2cangjie/.opencode/plugins/java2cangjie.js .opencode/plugins/java2cangjie.js

# 安装依赖（自定义工具需要）
cd .java2cangjie/.opencode && bun install
```

### Option 3: 全局本地安装

```bash
git clone https://github.com/thjyneg/java2cangjie.git ~/.config/opencode/java2cangjie
ln -s ../java2cangjie/.opencode/plugins/java2cangjie.js ~/.config/opencode/plugins/java2cangjie.js
cd ~/.config/opencode/java2cangjie/.opencode && bun install
```

## 验证安装

重启 OpenCode 后：

1. **检查 Skills** — 输入 "列出你的 java2cangjie 技能"，应显示 `java2cangjie-*` 和 `cangjie-*` 共 10 个技能
2. **检查 Tools** — 使用 `/tools` 命令，应包含 `analyze_project`、`next_batch`、`compile_batch` 等工具

> Skills 和 bootstrap 注入无需任何外部依赖，始终可用。Tools 需要 `@opencode-ai/plugin`（Option 2/3 通过 `bun install` 自动安装；Option 1 由 OpenCode 运行时提供）。

## Plugin Tools

| Tool | Args | Description |
|------|------|-------------|
| `analyze_project` | `javaPath` (string), `maxBatchSize` (number), `outputDir?` (string) | Scan Java project, build dependency DAG, return batch plan |
| `next_batch` | — | Get next batch of files ready for translation |
| `compile_batch` | `batchId` (string), `outputFiles?` (string[]) | Run `cjpm build`, auto-complete on success, return errors on failure |
| `mark_complete` | `batchId` (string), `outputFiles?` (string[]) | Mark batch as completed successfully |
| `mark_blocked` | `batchId` (string), `reason` (string) | Mark batch as failed after max retries |
| `translation_status` | — | Get current progress |

## Skills (10)

| Skill | Description |
|-------|-------------|
| `using-java2cangjie` | Bootstrap skill — auto-injected on session start |
| `java2cangjie-translate` | Java-to-Cangjie mapping rules, type conversions |
| `java2cangjie-fix` | Compilation error fixing |
| `java2cangjie-report` | Translation report generation |
| `cangjie-lang-features` | Core language: syntax, generics, concurrency |
| `cangjie-std` | Standard library: collections, IO, filesystem |
| `cangjie-stdx` | Extended library: JSON, encoding, config |
| `cangjie-toolchains` | Toolchain: cjc, cjpm, cjfmt, cjlint |
| `cangjie-regulations` | Project structure, naming conventions |
| `cangjie-original-docs` | Full original Cangjie documentation fallback |

## Troubleshooting

### Skills 不显示

1. 检查插件是否加载：`opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie`
2. 确认 `skills/` 目录存在于仓库根目录
3. 本地安装时，确认符号链接指向正确

### Tools 不显示

1. 确认 `@opencode-ai/plugin` 可用：在 `.opencode/` 目录下运行 `bun install`
2. 查看启动日志是否有 `[java2cangjie] Warning` 信息
3. Tools 是可选的 — 即使没有 tools，skills 和 bootstrap 注入仍然正常工作

### Claude Code 用户

参见项目根目录 [README.md](../README.md)。
