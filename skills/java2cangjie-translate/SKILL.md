---
name: java2cangjie-translate
description: "Detailed Java-to-Cangjie mapping rules and translation patterns. This skill is a reference for type conversions, keyword handling, API mappings, and directory structure conventions. Load this skill during translation batches for specific mapping guidance on individual Java-to-Cangjie file conversions."
---

# Java to Cangjie Translation - Execute

## Overview

Pure AI translation with incremental dependency-driven strategy. Translate Java source to Cangjie in small batches (1-3 files), compiling after each batch.

Output goes to `<java_project>/j2cjgenerated/`.

## OpenCode Environment (has plugin tools)

Use plugin tools for deterministic workflow control:

```
1. analyze_project(javaPath)        → dependency DAG + batch plan
2. next_batch()                     → next files to translate
3. translate batch via AI
4. compile_batch(batchId)           → compile via cjpm build, auto-complete on success
5. If compile fails → fix errors → compile_batch(batchId) again (max 3 retries)
6. Repeat from step 2
```

**Note**: The `compile_batch` tool runs `cjpm build` internally and auto-manages batch status. Do NOT call `mark_complete` without compiling first.

## Claude Code Environment (no plugin tools)

Manual workflow with equivalent logic:

```bash
# Step 1: Scan Java files
find <java_dir> -name "*.java" -type f

# Step 2: Build dependency graph
grep -rn "^import " <java_dir> --include="*.java" | grep -v "java\.\|javax\.\|org\."

# Step 3: Identify leaf files (no internal dependencies)
# Files whose imports don't reference other project classes = leaf nodes

# Step 4: Track progress in state file
# Save to <output_dir>/.java2cangjie_state.json
# Format: { batches: { "batch-N": { status, files, retries } }, totalFiles, outputDir }
```

## Third-Party API Mock Strategy

When translating Java code that depends on third-party or JDK APIs without Cangjie equivalents, create stub (mock) APIs so the project compiles.

### API Classification

| Category | Strategy | Examples |
|----------|----------|----------|
| **Cangjie std 有对应** | 直接映射 | `ArrayList`→`std.collection.ArrayList`, `HashMap`→`std.collection.HashMap`, `File`→`std.fs.File`, `InputStream`→`std.fs.InputStream` |
| **Cangjie 无对应但核心依赖** | 创建 mock stub | `java.util.zip.*`, `javax.crypto.*`, `java.nio.file.*`, `java.security.*` |
| **测试框架** | 跳过，不翻译 | `org.junit.*`, `org.mockito.*`, `org.assertj.*`, `org.powermock.*` |

### Mock Stub Generation Rules

When an import has no Cangjie equivalent:

1. **Create stub in dedicated mock package** under the output directory:

```
<output_dir>/<module>/src/_mock/<package_path>/
```

2. **Stub file naming**: match original class name, e.g. `java.util.zip.CRC32` → `src/_mock/java/util/zip/CRC32.cj`

3. **Stub content rules**:
   - Define the `class` or `interface` matching the original Java API signature
   - All methods throw `"未实现"` exception using仓颉 syntax:
     ```cj
     package _mock.java.util.zip

     class CRC32 {
         var value: UInt32 = 0

         func update(b: Array<Byte>): Unit {
             throw Exception("未实现: CRC32.update")
         }

         func getValue(): UInt32 {
             throw Exception("未实现: CRC32.getValue")
         }

         func reset(): Unit {
             this.value = 0
         }
     }
     ```
   - For interfaces, declare all methods
   - For abstract classes, declare concrete methods as stubs
   - Keep field names matching Java originals for readability
   - Use `public` visibility for all mock members

4. **When to create mock stubs**:
   - During translation, when encountering an import that cannot be mapped to Cangjie std
   - Create the stub BEFORE translating the file that depends on it
   - Add mock stubs as a separate step in the batch (before main translation)

5. **Mock stub priority** — create stubs only for APIs actually used by the project code being translated. Do not mock entire JDK.

6. **Import replacement**: In translated files, replace original Java imports with mock imports:
   ```cj
   // Before: import java.util.zip.CRC32
   // After:  import _mock.java.util.zip.CRC32
   ```

### Common Java-to-Cangjie Std Mappings (No Mock Needed)

These Java APIs have direct Cangjie equivalents — use them instead of mocking:

| Java API | Cangjie Equivalent |
|----------|-------------------|
| `java.util.ArrayList` | `std.collection.ArrayList` |
| `java.util.HashMap` | `std.collection.HashMap` |
| `java.util.HashSet` | `std.collection.HashSet` |
| `java.util.List` | `std.collection.ArrayList` (or use interface) |
| `java.util.Map` | `std.collection.HashMap` (or use interface) |
| `java.util.Set` | `std.collection.HashSet` (or use interface) |
| `java.io.File` | `std.fs.File` |
| `java.io.InputStream` | `std.io.InputStream` or `std.fs.InputStream` |
| `java.io.OutputStream` | `std.io.OutputStream` or `std.fs.OutputStream` |
| `java.io.IOException` | `Exception` or custom exception class |
| `java.nio.ByteBuffer` | `Array<Byte>` + manual position tracking |
| `java.nio.charset.Charset` | `String` (Cangjie uses UTF-8 by default) |
| `java.util.Arrays` | `std.collection.*` utility functions |
| `java.util.Collections` | `std.collection.*` utility functions |
| `java.util.Objects` | Direct `==` comparison or `Option` |

## Translation Loop

For each batch (1-3 files):

### 1. Read Java Source

Read the Java files in the current batch. Understand the class structure, methods, and dependencies.

### 2. Identify and Create Mock Stubs

Before translating, scan all imports in the batch:
- Imports with Cangjie std equivalents → map directly
- Imports without equivalents → create mock stubs in `_mock/` directory
- Test imports → skip

### 3. Lookup Cangjie Documentation

**MANDATORY: Read relevant docs BEFORE translating.**

Use the Cangjie skills for documentation lookup:
1. `cangjie-std` → standard library types and APIs (collections, IO, filesystem, etc.)
2. `cangjie-lang-features` → language syntax, generics, concurrency, error handling
3. `cangjie-stdx` → extended library (JSON, encoding, configuration)
4. `cangjie-original-docs` → full original documentation fallback
5. `cangjie-regulations` → naming conventions and best practices

### 4. Translate Each File

Key mapping rules:

| Java | Cangjie |
|------|---------|
| `package com.example` | `package com.example` |
| `import java.util.ArrayList` | `import std.collection.ArrayList` |
| `ArrayList<E>` | `ArrayList<E>` (from std.collection) |
| `HashMap<K,V>` | `HashMap<K,V>` (from std.collection) |
| `null` | `None` or `?? default` |
| `Optional<T>` | `Option<T>` |
| `try/catch` | `try/except` |
| `throws` | No equivalent, use `Option` or `except` |
| `synchronized` | `Mutex` from std.sync |
| `instanceof` | `is` or `match` pattern |
| `System.out.println` | `println` |
| `String.format` | String interpolation `\${expr}` |
| `this.field` | `this.field` |
| `@Override` | No annotation needed |
| `interface` | `interface` |
| `abstract class` | `abstract class` |
| `T extends Comparable` | `T <: Comparable` |
| `void` | `Unit` or omit return type |
| `long` | `Int64` |
| `int` | `Int` |
| `byte` | `Byte` (actually `UInt8`) |
| `byte[]` | `Array<Byte>` |
| `boolean` | `Bool` |
| `String` | `String` |
| `float` | `Float32` |
| `double` | `Float64` |
| `char` | `Rune` |
| `~value` (bitwise NOT) | `!value` |
| `Thread.sleep(ms)` | `sleep(ms * 1000000)` (top-level func, nanoseconds) |
| `str.isEmpty()` | `str.isEmpty()` (function call, not property) |
| `new Byte(intVal)` | `UInt8(intVal)` |
| `new Integer(str)` | `Int64(str)` or `Int32(str)` |

**IMPORTANT - Type Notes:**
- `byte[]` in Java translates to `Array<Byte>` in Cangjie (not `Byte[]`)
- Always initialize arrays: `Array<Byte>(0, repeat: 0)` (NOT `Array<Byte>()`)
- Use `Int64` for Java `long` to avoid overflow
- **There is no `Int()` constructor in Cangjie** — use `Int64()` or `Int32()` for string-to-int conversion
- **`Byte` in Cangjie is `UInt8`** — `Byte()` constructor does NOT accept `Int64`, use `UInt8()` instead

#### CRITICAL: Bitwise NOT Operator

Cangjie has NO `~` (bitwise NOT) operator. Replace with XOR:

```cj
// Java: ~value
// Cangjie: (-1) ^ value
let result = (-1) ^ value
```

Other bitwise operators are the same: `&`, `|`, `^`, `<<`, `>>`
For unsigned right shift `>>>`: use `>>` on unsigned types.

#### CRITICAL: Class Inheritance and Access Control

**1. `abstract class` constructor cannot call `open` methods:**

```cj
// WRONG: calling open method in constructor
abstract class Base {
    public init() {
        this.doSetup()  // error: open method in constructor
    }
    protected open func doSetup(): Unit { ... }
}

// FIX A: Lazy initialization with Option
abstract class Base {
    private var setup: ?Bool = None
    protected open func doSetup(): Unit { ... }
    private func lazySetup(): Unit {
        match (setup) {
            case None => doSetup(); setup = Some(true)
            case Some(_) => ()
        }
    }
}

// FIX B: Subclass creates and passes to superclass (recommended)
abstract class Base {
    private let config: Config
    protected init(config: Config) {
        this.config = config  // direct assignment, no open calls
    }
}
class Derived <: Base {
    public init() {
        super(Config(...))  // subclass creates config
    }
}
```

**2. `public` visibility propagation:**
- If a `public class` inherits from another class, the parent MUST also be `public`
- Fields accessed from other packages MUST have explicit `public` modifier (default is `internal`)
- Interface methods are `public` by default, but class methods are not

**3. `open` / `redef` rules:**
- `abstract class` methods can be overridden by abstract subclasses without `open`
- `public class` (non-abstract) overriding parent methods requires parent method to be `open`
- **`redef` is ONLY for `open class` subclasses**, NOT for `abstract class` subclasses

```cj
// WRONG: redef in abstract class hierarchy
public class Derived <: AbstractBase {
    public redef func doWork() { ... }  // ❌ if AbstractBase is abstract
}

// CORRECT: just override without redef
public class Derived <: AbstractBase {
    public func doWork() { ... }  // ✅
}
```

#### CRITICAL: Option Type Handling

**1. Cannot use `==` with Option:**

```cj
// WRONG:
if (decrypter == None) { ... }
if (value == Some(5)) { ... }

// CORRECT: use match
match (decrypter) {
    case None => ...
    case Some(d) => ...
}

// CORRECT: use if-let
if (let Some(d) <- decrypter) { ... }
```

**2. `as` type cast returns Option:**

```cj
// WRONG: as Resource returns Option<Resource>
(stream as Resource).close()

// CORRECT: unwrap with if-let
if (let Some(r) <- (stream as Resource)) {
    r.close()
}
```

**3. `None` requires type argument in declarations:**

```cj
// WRONG: generic type needs argument
var x: ?Decrypter = None  // may cause error

// CORRECT:
var x: Option<Decrypter> = Option<Decrypter>.None
// or
var x: ?Decrypter = None<Decrypter>
```

#### CRITICAL: Constructor Rules

**1. Constructor (`init`) must NOT have a return type:**

```cj
// WRONG:
public init(...): Unit {
// CORRECT:
public init(...) {
```

**2. Empty constructor is fine:**

```cj
public init() {}
```

#### CRITICAL: Enum Properties and Comparison

**1. Enum comparison uses `match`, not `==`:**

```cj
// WRONG:
if (method == DEFLATE(8)) { ... }

// CORRECT:
match (method) {
    case DEFLATE(_) => ...
    case _ => ()
}
```

**2. Enum values with data use `prop` for accessors:**

```cj
public enum CompressionMethod {
    | STORE(Int64)
    | DEFLATE(Int64)

    public prop code: Int64 {
        get() {
            match (this) {
                case STORE(c) => c
                case DEFLATE(c) => c
            }
        }
    }
}
```

#### CRITICAL: Cangjie Keyword Escaping

**`init` is a Cangjie constructor keyword.** Java methods/fields named `init` MUST be renamed:
- Interface method `void init()` → `func initialize()` (or `func init$()`)
- Override `@Override public void init()` → `open func initialize()`
- All call sites `obj.init()` → `obj.initialize()`

**`type` is a Cangjie keyword.** Fields/parameters named `type` MUST be escaped:
- Field `private String type` → `` private var `type`: String ``
- Parameter `void setType(String type)` → `` func setType(`type`: String) ``
- Or rename to `kind`/`category` if backticks are undesirable

**Other common Cangjie keywords that may collide with Java identifiers:**
`prop`, `redef`, `let`, `var`, `func`, `enum`, `open`, `sealed`, `macro`, `spawn`, `foreign`, `resource`

When a Java identifier collides with a Cangjie keyword, either:
1. Wrap in backticks: `` `keyword` `` (preferred for fields/params)
2. Rename to a synonym (preferred for methods, e.g., `init` → `initialize`)

#### CRITICAL: Inner Enums Must Be Extracted

Cangjie does NOT support enums nested inside classes. Java inner enums must be extracted to top-level:

```java
// Java:
public class ProgressMonitor {
    public enum State { READY, RUNNING, DONE }
}
```

```cj
// Cangjie: extract to top-level enum
enum ProgressMonitorState {
    READY
    | RUNNING
    | DONE
}

class ProgressMonitor {
    var state: ProgressMonitorState = ProgressMonitorState.READY
}
```

Rules:
- Extract the enum to top level with a compound name (OuterClass + EnumName)
- Replace all references from `OuterClass.EnumName` to `OuterClassEnumName`
- This applies to ALL inner enums, not just the example above

#### CRITICAL: InputStream.close() Requires Resource Cast

`close()` is NOT a method of `InputStream` in Cangjie — it belongs to the `Resource` interface:

```cj
// WRONG:
let stream = FileInputStream("file.txt")
stream.close()  // error: close not found on InputStream

// CORRECT:
import std.fs.{FileInputStream, Resource}
let stream = FileInputStream("file.txt")
(stream as Resource).close()
```

For try-with-resources patterns, prefer using `try` block with explicit `(stream as Resource).close()` in finally.

### 5. Write Output

**IMPORTANT - Directory Structure Differences:**

Java Maven projects use `src/main/java/包名/`, but Cangjie projects require `src/包名/` directly under `src/`. 

**Correct Cangjie structure:**
```
<java_project>/j2cjgenerated/
├── <module>/
│   ├── cjpm.toml
│   └── src/
│       └── <package_path>/    # Direct under src, NOT src/main/cj
│           └── *.cj
```

**Common mistakes to avoid:**
- ❌ `src/main/cj/包名/` - This is Java Maven convention, not Cangjie
- ✅ `src/包名/` - Correct Cangjie structure

For Maven projects, create `cjpm.toml` per module:

```toml
[package]
cjc-version = "0.53.13"
name = "<module-name>"
version = "0.1.0"
description = "Description"
authors = ["Your Name <email@example.com>"]
license = "Apache-2.0"
output-type = "static"
```

**Multi-level package names (e.g., `net.lingala.zip4j`):**
- Keep the same package structure in Cangjie: `package net.lingala.zip4j`
- File path: `src/net/lingala/zip4j/ClassName.cj`
- cjpm.toml name should match the base module name (e.g., "zip4j")

### 6. Compile

**OpenCode (with plugin tools):**

Use `compile_batch(batchId)` — it handles compilation and batch status automatically.

**Claude Code (manual):**

```bash
cd <java_project>/j2cjgenerated/<module> && cjpm build 2>&1
```

`cjpm build` automatically handles dependency resolution and package linking. Prefer it over `cjc -p` which requires manually specifying dependency information.

**NOTE - cjpm build directory scanning:**

cjpm build requires at least one `.cj` file directly in each directory to scan subdirectories. If you see:
```
Warning: there is no '.cj' file in directory './src', and its subdirectories will not be scanned
```
Create a placeholder `.cj` file (e.g., `emptyp.cj`) in the directory.

**When to use each tool:**

| Tool | Use Case | Notes |
|-------|-----------|-------|
| `compile_batch()` | OpenCode translation workflow | Plugin runs `cjpm build` internally, auto-manages status |
| `cjpm build` | Claude Code translation workflow | Auto-handles dependencies, standard approach |
| `cjc -p` | Single-package quick check only | No dependency resolution, use only for isolated packages |

### 7. Track Progress

**If compilation passes:**
- Mark batch as complete
- Proceed to next batch

**If compilation fails (max 3 retries):**
- Load `java2cangjie-fix` skill to fix errors
- If still failing after 3 retries, mark batch as blocked
- Move to next available batch

## Project Initialization

For existing Java projects (not using `cjpm init`):

1. Create the output directory structure:
```bash
mkdir -p <java_project>/j2cjgenerated/<module>/src
```

2. Create `cjpm.toml` with appropriate settings (see section 4)

3. Create package directories under `src/` matching Java package structure

**Note**: Do NOT use `cjpm init` for Java-to-Cangjie translation projects. It creates unnecessary files and expects a different structure.

## File Size Control

- Single file > 200 lines: translate alone
- Small files (< 100 lines each): batch up to 3
- Always compile after each batch, never batch multiple translations without compiling

## Context Window Management

- Read relevant docs BEFORE translating each batch, not during
- Focus on one file at a time within a batch
- Use state file to resume if context fills
- If context is getting low (>80% used), save progress and suggest resuming

## Session Resumption

When resuming an interrupted translation:

1. Check for state file: `<output_dir>/.java2cangjie_state.json`
2. Determine which batches are completed/in-progress/pending
3. Call `translation_status()` (OpenCode) or read state file (Claude Code)
4. Continue from first non-completed batch

## Error Handling

If a batch consistently fails:
1. Try splitting the batch into individual files
2. Try translating a simpler version first (e.g., remove generics, use Any)
3. Mark as blocked and continue with other batches
4. Document the failure reason in state file

## Project Cleanup

Compilation generates temporary files and cache. Clean periodically:

```bash
cd <java_project>/j2cjgenerated/<module>

# Clean build artifacts
cjpm clean

# Or manually clean
rm -rf target/ .cached/
```

**Common directories to be aware of:**
- `target/` - Build output directory
- `target/release/` - Release artifacts
- `.cached/` - Cangjie compiler cache
- `*.a` - Generated static library files
- `*.o` - Object files

## Next Steps

- If all batches complete → invoke `java2cangjie-report` skill
- If errors remain → invoke `java2cangjie-fix` skill
