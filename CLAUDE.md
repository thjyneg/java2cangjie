# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言规则

**所有交流必须使用简体中文。** 包括对话、注释说明、提交信息、文档等一切输出内容。代码标识符和命令保持英文。

## Project Overview

A dual-platform plugin for translating Java projects to Cangjie (仓颉) language using AI with incremental dependency-driven strategy.

## Platform Architecture

**OpenCode**: `.opencode/plugins/java2cangjie.js` 提供插件工具（`analyze_project`、`next_batch`、`compile_batch` 等）+ skills + bootstrap 注入
**Claude Code**: hooks（SessionStart 注入）+ Python 脚本（`scripts/analyze_deps.py`）+ skills

两个平台共享同一套 skills 和 agents。OpenCode 插件内含 JS 依赖分析器；Claude Code 使用独立的 Python 实现。两者产生等价的 DAG 输出。

## Key Commands

```bash
cd <output_dir>/<module> && cjpm build 2>&1   # 编译（优先于 cjc -p）
cd <output_dir>/<module> && cjpm test           # 运行测试
cd <output_dir>/<module> && cjpm clean           # 清理构建产物
```

安装文档：`docs/README.claude-code.md`（Claude Code）、`.opencode/INSTALL.md`（OpenCode）

## Architecture

```
.claude-plugin/plugin.json          # Claude Code 清单
.opencode/plugins/java2cangjie.js   # OpenCode 插件（工具 + 配置 + bootstrap）
scripts/analyze_deps.py             # 依赖分析脚本（Python）
hooks/                              # Claude Code SessionStart bootstrap 注入
skills/                             # 10 个技能
agents/                             # 3 个代理
```

### Skills (10)

**翻译工作流** (4): `using-java2cangjie` (bootstrap), `java2cangjie-translate` (映射规则), `java2cangjie-fix` (错误修复), `java2cangjie-report` (报告生成)

**仓颉文档** (6): `cangjie-lang-features`, `cangjie-std`, `cangjie-stdx`, `cangjie-toolchains`, `cangjie-regulations`, `cangjie-original-docs`

### Agents (3)
- `cangjie-engineer` — 仓颉开发专家（全访问）
- `translation-reviewer` — 翻译质量审查（只读）
- `error-fixer` — 错误修复执行（写访问）

## Translation Workflow

1. **Analyze** — 构建依赖 DAG，规划批次（1-3 文件）
2. **Translate** — AI 读 Java，查仓颉文档，写仓颉代码
3. **Compile** — 每批翻译后必须 `cjpm build`（不可跳过）
4. **Fix** — 编译失败：查文档修复，最多 3 次，之后暂停询问用户
5. **Report** — 生成翻译报告

翻译顺序遵循 DAG 从叶子节点向上。状态保存在 `<output_dir>/.java2cangjie_state.json`。

## Critical Translation Rules

### Keyword Collisions
- `init` → rename to `initialize()`（仓颉构造器关键字）
- `type` → 用反引号包裹 `` `type` `` 或重命名
- 其他仓颉关键字：`prop`、`redef`、`let`、`var`、`func`、`open`、`sealed`、`macro`、`spawn`

### Inner Enums
必须提取到顶层，用组合名：`class Foo { enum Bar { A, B } }` → `enum FooBar { A | B }`

### Directory Structure
- Java Maven: `src/main/java/com/example/`
- Cangjie: `src/com/example/`（不要 `main/java` 或 `main/cj`）

### InputStream.close()
先转为 `Resource`：`(stream as Resource).close()`

### Type Mappings
| Java | Cangjie |
|------|---------|
| `byte[]` | `Array<Byte>`（不是 `Byte[]`） |
| `long` | `Int64` |
| `int` | `Int` |
| `byte` | `UInt8` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `synchronized` | `std.sync.Mutex` |

### No Int() Constructor
用 `Int64()` 或 `Int32()` 做字符串转整数。仓颉没有 `Int()` 构造器。

## Output Convention

所有翻译代码输出到 `<java_project>/j2cjgenerated/`，保持原始包结构。每个模块有自己的 `cjpm.toml`。

## Documentation Lookup Priority

1. `cangjie-std` / `cangjie-lang-features` — 标准库和语言特性
2. `cangjie-stdx` — 扩展库（JSON、编码、配置）
3. `cangjie-original-docs` — 完整原始文档 fallback
4. `cangjie-toolchains` — 构建工具（cjc、cjpm、cjfmt、cjlint）
5. `cangjie-regulations` — 编码规范和最佳实践
