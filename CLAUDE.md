# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言规则

**所有交流必须使用简体中文。** 包括对话、注释说明、提交信息、文档等一切输出内容。代码标识符和命令保持英文。

## Project Overview

A dual-platform plugin for translating Java projects to Cangjie (仓颉) language using AI with incremental dependency-driven strategy. The plugin uses a hybrid control architecture: OpenCode plugin tools enforce workflow reliability, while Markdown skills guide AI translation quality.

## Platform Architecture

**OpenCode**: Plugin tools (`analyze_project`, `next_batch`, `compile_batch`, etc.) + skills + bootstrap injection via `experimental.chat.system.transform`
**Claude Code**: `/j2c-translate` slash command + Python helper (`scripts/analyze_deps.py`) + hooks + skills

Both platforms share the same skill files and agents. The OpenCode plugin (`.opencode/plugins/java2cangjie.js`) contains a JavaScript dependency analyzer; Claude Code uses a separate Python implementation (`scripts/analyze_deps.py`). Both produce equivalent DAG output.

## Key Commands

### Cangjie Compilation
```bash
cd <output_dir>/<module> && cjpm build 2>&1   # Compile (preferred over cjc -p)
cd <output_dir>/<module> && cjpm test           # Run tests
cd <output_dir>/<module> && cjpm clean           # Clean build artifacts
```

### Dependency Analysis (Claude Code)
```bash
python scripts/analyze_deps.py --java-path <path> [--output-dir <dir>] [--max-batch-size 3]
```

### Test the Plugin
```bash
claude --plugin-dir D:/codes/java2cangjie   # Load plugin for testing
```

No automated test suite exists. Testing is manual (run translation on real Java projects, verify with `cjpm build`).

## Architecture

### Plugin Structure
```
.claude-plugin/plugin.json          # Claude Code manifest
.opencode/plugins/java2cangjie.js   # OpenCode plugin (tools + config + bootstrap)
commands/j2c-translate.md           # Claude Code slash command
scripts/analyze_deps.py             # Dependency analysis (Python)
hooks/                              # Claude Code SessionStart bootstrap injection
skills/                             # 11 skills (see below)
agents/                             # 3 agents
```

### Skills (11 total)

**Translation workflow** (4): `using-java2cangjie` (bootstrap), `java2cangjie-translate` (mapping rules reference), `java2cangjie-fix` (error patterns), `java2cangjie-report` (report generation), `j2c-translate` (workflow reference for command)

**Cangjie documentation** (6): `cangjie-lang-features`, `cangjie-std`, `cangjie-stdx`, `cangjie-toolchains`, `cangjie-regulations`, `cangjie-original-docs`

### Agents (3)
- `cangjie-engineer` - General Cangjie development (full access)
- `translation-reviewer` - Quality reviewer (read-only)
- `error-fixer` - Error fix executor (write access)

### Bootstrap Injection
SessionStart hook reads `skills/using-java2cangjie/SKILL.md` and injects into system prompt. The polyglot `hooks/run-hook.cmd` handles cross-platform execution (Windows batch + Unix bash via heredoc trick).

## Translation Workflow

1. **Analyze** - Build dependency DAG, plan batches (1-3 files each)
2. **Translate** - AI reads Java, looks up Cangjie docs, writes Cangjie code per batch
3. **Compile** - `cjpm build` after EVERY batch (never skip)
4. **Fix** - If compilation fails: lookup docs, fix, retry (max 3 attempts, then pause and ask user)
5. **Report** - Generate translation report

Translation order follows DAG from leaf nodes upward. State tracked in `<output_dir>/.java2cangjie_state.json`.

## Critical Translation Rules

### Keyword Collisions
- `init` → rename to `initialize()` (Cangjie constructor keyword)
- `type` → wrap in backticks `` `type` `` or rename
- Other Cangjie keywords: `prop`, `redef`, `let`, `var`, `func`, `open`, `sealed`, `macro`, `spawn`

### Inner Enums
Must be extracted to top-level with compound names:
```java
class Foo { enum Bar { A, B } }  →  enum FooBar { A | B }
```

### Directory Structure
- Java Maven: `src/main/java/com/example/`
- Cangjie: `src/com/example/` (NO `main/java` or `main/cj`)

### InputStream.close()
Cast to `Resource` first: `(stream as Resource).close()`

### Type Mappings
| Java | Cangjie |
|------|---------|
| `byte[]` | `Array<Byte>` (not `Byte[]`) |
| `long` | `Int64` |
| `int` | `Int` |
| `byte` | `UInt8` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `synchronized` | `std.sync.Mutex` |

### No Int() Constructor
Use `Int64()` or `Int32()` for string-to-int conversion. There is no `Int()` constructor in Cangjie.

## Output Convention

All translated code goes to `<java_project>/j2cjgenerated/`, preserving original package structure. Each module has its own `cjpm.toml`.

## Documentation Lookup Priority

1. `cangjie-std` / `cangjie-lang-features` - Standard library and language features
2. `cangjie-stdx` - Extended library (JSON, encoding, config)
3. `cangjie-original-docs` - Full original documentation fallback
4. `cangjie-toolchains` - Build tools (cjc, cjpm, cjfmt, cjlint)
5. `cangjie-regulations` - Coding conventions and best practices
