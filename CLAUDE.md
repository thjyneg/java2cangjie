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
python <PLUGIN_ROOT>/scripts/cjpm-build <output_dir>/<module>  # 编译（自动创建占位文件 + cjpm build）
cd <output_dir>/<module> && cjpm test             # 运行测试
cd <output_dir>/<module> && cjpm clean             # 清理构建产物
```

安装文档：`docs/README.claude-code.md`（Claude Code）、`.opencode/INSTALL.md`（OpenCode）

## Architecture

```
.claude-plugin/plugin.json          # Claude Code 清单
.opencode/plugins/java2cangjie.js   # OpenCode 插件（工具 + 配置 + bootstrap）
scripts/analyze_deps.py             # 依赖分析脚本（Python）
scripts/cjpm-build                  # 编译 wrapper（自动创建占位文件 + cjpm build）
hooks/                              # Claude Code SessionStart bootstrap 注入
skills/                             # 10 个技能
agents/                             # 3 个代理
```

### Skills (10)

**翻译工作流** (4): `using-java2cangjie` (bootstrap), `java2cangjie-translate` (映射规则), `java2cangjie-fix` (错误修复), `java2cangjie-report` (报告生成)

**仓颉文档** (6): `cangjie-lang-features`, `cangjie-std`, `cangjie-stdx`, `cangjie-toolchains`, `cangjie-regulations`, `cangjie-original-docs`

### Agents (2)
- `cangjie-translate-engineer` — 翻译工程师（Java→仓颉翻译 + 编译错误修复）
- `translation-reviewer` — 翻译质量审查（只读）

## Translation Workflow

1. **Analyze** — 构建依赖 DAG，规划批次（1-3 文件）
2. **Mock** — 为无仓颉对应的三方 API 创建 stub（`_mock/` 目录，方法抛出"未实现"异常）
3. **Translate** — AI 读 Java，查仓颉文档，写仓颉代码
4. **Compile** — 每批翻译后必须 `python <PLUGIN_ROOT>/scripts/cjpm-build <module>`（不可跳过）
5. **Fix** — 编译失败：查文档修复，最多 3 次，之后暂停询问用户
6. **Report** — 生成翻译报告

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
`close()` 属于 `Resource` 接口，不是流方法。且 `as` 返回 Option，需要 if-let 解包：
```cj
if (let Some(r) <- (stream as Resource)) { r.close() }
```

### Type Mappings
| Java | Cangjie |
|------|---------|
| `byte[]` | `Array<Byte>`（不是 `Byte[]`） |
| `long` | `Int64` |
| `int` | `Int` |
| `byte` | `UInt8` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try { } catch(e: Exception) { }`（用 `catch`，不是 `except`） |
| `synchronized` | `std.sync.ReentrantMutex`（显式 lock/unlock + try/finally） |
| `~value` (bitwise NOT) | `(-1) ^ value`（仓颉没有 `~` 运算符） |

### Class Inheritance Rules (CRITICAL — from 259-error learning)
- `redef` **只能用于静态方法**，绝对不能用于实例方法覆写
- 实例方法覆写**不需要任何关键字**（去掉 Java 的 `@Override`）
- 父类方法必须标记 `open` 才能被子类覆写，整个继承链都需要
- 需要被继承的类必须标记 `open class`
- `abstract` 方法 → `open func` 不提供实现体（去掉 `abstract`）
- `abstract class` 构造函数不能调用 `open` 方法 — 用延迟初始化或子类传参
- `public` 类的父类也必须 `public`（可见性传播）
- 构造函数 `init` 不能有返回类型（去掉 `: Unit`）

### Option Type Rules
- 不能用 `==` 比较 Option，必须用 `match` 或 `if-let`
- `as` 类型转换返回 `Option<T>`，需要 `if-let` 解包
- `None` 是泛型的，声明时需要类型参数

### Array Initialization
- `Array<Byte>()` 不合法，必须指定大小和初始值：`Array<Byte>(0, repeat: 0)`

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
