# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a skill system for translating Java projects to Cangjie (仓颉) language using the j2cj tool with post-translation error correction. The project contains modular skills for each translation step and includes comprehensive Cangjie API documentation.

## Key Commands

### Translation Execution

```bash
# Module mode - translate a single module
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -m <module_path>

# Project mode - translate an entire Maven project
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -p <project_path>

# Domain mode - translate multiple projects in a directory
python skills/java2cangjie-translate/script/j2cj_module_translate_execute.py -d <domain_path>
```

### Cangjie Compilation and Testing

```bash
cd <output_dir>
cjpm build      # Compile Cangjie code
cjpm test       # Run tests
```

### Error Analysis

```bash
# Find j2cj-marked issues in translated files
grep -r "<--" <output_dir> --include="*.cj"
```

## Environment Variables

- `J2CJ_TOOL_PATH` - Path to j2cj tool directory (containing j2cj.jar)
- `JDK_PATH_PROJECT` - JDK path for project compilation (default: system java)
- `JDK_PATH_J2CJ` - JDK 17+ path for j2cj tool (default: system java)

## Architecture

### Skill Structure

The project follows a 7-step translation workflow orchestrated by sub-skills:

```
skills/
├── using-java2cangjie/          # Main orchestrator skill
├── java2cangjie-translate/      # Step 2: Execute j2cj translation
│   ├── script/                  # Translation execution script
│   │   └── j2cj_module_translate_execute.py
│   └── j2cj_tool/               # j2cj.jar location
├── java2cangjie-analyze/        # Step 3: Analyze errors, lookup docs
│   └── docs/                    # Cangjie language documentation
├── java2cangjie-fix/            # Step 5: Fix errors iteratively
├── java2cangjie-test/           # Step 6: Compile and test
└── java2cangjie-report/         # Step 7: Generate report
```

### Translation Workflow

1. **Translate** - Execute j2cj (outputs to `j2cjgenerated/` directory)
2. **Analyze** - Find `<--` markers, categorize errors, lookup Cangjie docs
3. **Confirm** - Present modification plan for user approval
4. **Fix** - Execute modify-compile loop (max 20 iterations), fix in dependency order
5. **Test** - Compile with `cjpm build`, run tests
6. **Report** - Generate translation report

### Cangjie Documentation

Located in `skills/java2cangjie-analyze/docs/`:
- `extra/` - Basic types: Array, ArrayList, HashMap, HashSet, String, Option, etc.
- `libs/std/` - Standard library APIs: collection, io, net, sync, time, etc.
- `libs/stdx/` - Extended libraries: HTTP, compression, encoding
- `manual/` - Language manual: syntax, generics, concurrency, error handling

## Important Patterns

### Dependency-Aware Fixing

When fixing errors, analyze file dependencies first and fix bottom-up:
1. Find all import statements: `grep "^import com\." <output_dir>/*.cj`
2. Build dependency graph
3. Fix files with no dependencies first, then work up

### Modify-Compile Loop

The fix step requires compiling after EVERY modification:
```
Modify → Compile → Check → (if error) → Modify → Compile → ...
```
Never batch multiple fixes without compiling between them.

### Documentation Lookup Priority

For each error, search documentation in this order:
1. `docs/extra/` for basic types
2. `docs/libs/std/<package>/` for standard library APIs
3. `docs/libs/std/<package>/*_samples/` for code examples
4. `docs/manual/` for language concepts

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

Translation progress can be saved and resumed. Checkpoint files are stored at:
```
<output_dir>/.java2cangjie_checkpoint.md
```

Templates for checkpoints are in `templates/checkpoint.md`.
