# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Superpowers-based plugin for translating Java projects to Cangjie (仓颉) language using pure AI translation with incremental dependency-driven strategy. The plugin uses a hybrid control architecture: OpenCode plugin tools enforce workflow reliability, while Markdown skills guide AI translation quality.

## Platform Support

- **OpenCode**: Plugin tools + skills + bootstrap injection
- **Claude Code**: Skills + hooks (no custom tools, manual workflow fallback)

## Key Commands

### Cangjie Compilation and Testing

```bash
cd <output_dir>
cjpm build      # Compile Cangjie code
cjpm test        # Run tests
```

### Error Analysis

```bash
# Compile and capture errors
cd <output_dir> && cjpm build 2>&1
```

## Architecture

### Plugin Structure

```
skills/                              # 10 skills (pure Markdown)
├── using-java2cangjie/SKILL.md      # Bootstrap (injects system prompt)
├── java2cangjie-translate/SKILL.md  # Translation guidance
├── java2cangjie-fix/SKILL.md        # Error fixing workflow
│   └── error-patterns.md            # Common error patterns reference
├── java2cangjie-report/SKILL.md     # Report generation
├── cangjie-lang-features/SKILL.md   # Cangjie language features
├── cangjie-std/SKILL.md             # Standard library reference
├── cangjie-stdx/SKILL.md            # Extended standard library
├── cangjie-toolchains/SKILL.md      # Toolchain docs (cjc, cjpm, cjfmt...)
├── cangjie-regulations/SKILL.md     # Coding conventions & best practices
└── cangjie-original-docs/SKILL.md   # Full original documentation

agents/                              # 3 agents
├── cangjie-engineer.md              # General Cangjie development expert
├── translation-reviewer.md          # Quality reviewer (read-only)
└── error-fixer.md                   # Error fix executor

.opencode/plugins/java2cangjie.js    # OpenCode plugin (tools + config + bootstrap)
hooks/                               # Claude Code hooks
```

### Translation Workflow

1. **Analyze** - Scan Java project, build dependency DAG, plan batches (1-3 files each)
2. **Translate** - AI reads Java, looks up Cangjie docs, writes Cangjie code per batch
3. **Compile** - `cjpm build` after each batch, mark complete or blocked
4. **Fix** - If compilation fails: lookup docs, fix one error, recompile, retry (max 3)
5. **Report** - Generate translation report with statistics

### Output Convention

All translated code goes to `<java_project>/j2cjgenerated/`, preserving original package structure.

## Important Patterns

### Incremental Dependency-Driven Translation

Parse Java import statements to build a dependency DAG. Translate bottom-up:
1. Start with leaf files (no internal dependencies)
2. Only proceed to dependent files after current batch compiles
3. Each batch: 1-3 files, always compile after translating

### Compile-After-Every-Batch

The translate step requires compiling after EVERY batch:
```
Translate batch → cjpm build → (if error) → Fix → cjpm build → mark complete/blocked → Next batch
```
Never batch multiple translations without compiling between them.

### Documentation Lookup Priority

For each translation or error, use the Cangjie skills:
1. `cangjie-std` / `cangjie-lang-features` - Standard library and language features
2. `cangjie-stdx` - Extended library (JSON, encoding, config)
3. `cangjie-original-docs` - Full original documentation fallback
4. `cangjie-toolchains` - Build tools (cjc, cjpm, cjfmt, cjlint)
5. `cangjie-regulations` - Coding conventions and best practices

## Common Java-to-Cangjie Mappings

| Java | Cangjie |
|------|---------|
| `ArrayList<E>` | `std.collection.ArrayList<E>` |
| `HashMap<K,V>` | `std.collection.HashMap<K,V>` |
| `HashSet<E>` | `std.collection.HashSet<E>` |
| `null` | `Option<T>.None` or `??` operator |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `synchronized` | `std.sync.Mutex` |
| `instanceof` | `match` pattern matching |

## Checkpoint System

Translation progress is tracked in `<output_dir>/.java2cangjie_state.json` (OpenCode) or checkpoint files (Claude Code). Supports session resume for interrupted translations.

## Design Document

Full design spec: `docs/superpowers/specs/2026-03-31-java2cangjie-superpowers-design.md`
