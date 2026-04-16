# Common Java-to-Cangjie Error Patterns

Living document of error patterns encountered during translation. Each pattern includes symptom, cause, fix, and documentation reference.

## 1. Missing Import Errors

### 1.1 Collection Types Not Found

**Symptom:**
```
error: Type 'ArrayList' not found
error: Type 'HashMap' not found
error: Type 'HashSet' not found
```

**Cause:** Java's `java.util` types need explicit imports in Cangjie.

**Fix:**
```cj
import std.collection.ArrayList
import std.collection.HashMap
import std.collection.HashSet
```

**Docs:** See `cangjie-std` skill → collections; or `cangjie-lang-features` skill → collections

### 1.2 IO Types Not Found

**Symptom:**
```
error: Type 'File' not found
error: Type 'BufferedReader' not found
```

**Fix:**
```cj
import std.fs.File
import std.io.BufferedStream
```

**Docs:** See `cangjie-std` skill → fs / io sections

## 2. Type Mismatch Errors

### 2.1 Nullable Assignment

**Symptom:**
```
error: Cannot assign nullable value to non-nullable type
```

**Cause:** Cangjie distinguishes nullable and non-nullable types strictly.

**Fix:**
```cj
// Option 1: Use ?? operator for default
let result: String = getNullable() ?? "default"

// Option 2: Use Option type explicitly
let result: Option<String> = getNullable()
match (result) {
  case Some(v) => { /* use v */ }
  case None => { /* handle null */ }
}
```

**Docs:** See `cangjie-lang-features` skill → Option 类型

### 2.2 Generic Type Mismatch

**Symptom:**
```
error: Generic parameter mismatch
```

**Cause:** Cangjie generics syntax differs from Java.

**Fix:**
```cj
// Java: <T extends Comparable<T>>
// Cangjie: <T <: Comparable<T>>
```

**Docs:** See `cangjie-lang-features` skill → 泛型/generic

## 3. Method Not Found Errors

### 3.1 System Methods

**Symptom:**
```
error: Method 'currentTimeMillis' not found
error: Method 'arraycopy' not found
```

**Fix:**
```cj
// System.currentTimeMillis() →
import std.time.Time
let time = Time.now()

// System.arraycopy() →
// Use Array.copyTo() or slice operations
```

### 3.2 String Methods

**Symptom:**
```
error: Method 'substring' not found
error: Method 'format' not found
```

**Fix:**
```cj
// str.substring(start, end) →
str[start..end]  // or str.subString(start, end - start)

// String.format("%s %d", name, age) →
"${name} ${age}"
```

**Docs:** See `cangjie-lang-features` skill → 字符串/String

### 3.3 Collection Methods

**Symptom:**
```
error: Method 'add' not found (on Array)
error: Method 'size' not found
```

**Fix:**
```cj
// ArrayList.add() →
list.append(element)

// list.size() →
list.size

// map.get(key) →
map.get(key)  // returns Option<V>
map.getOrDefault(key, defaultValue)
```

**Docs:** See `cangjie-std` skill → collections; `cangjie-lang-features` skill → collections

## 4. Syntax Errors

### 4.1 Synchronized Keyword

**Symptom:**
```
// <-- Java keyword 'synchronized' not supported -->
```

**Fix:**
```cj
import std.sync.Mutex

class MyClass {
  private let lock = Mutex()

  func criticalSection() {
    lock.lock()
    try {
      // critical section
    } finally {
      lock.unlock()
    }
  }
}
```

### 4.2 Instanceof

**Symptom:**
```
// <-- Java keyword 'instanceof' not supported -->
```

**Fix:**
```cj
// Java: if (obj instanceof String)
// Cangjie:
if (obj is String) { ... }
// or with match:
match (obj) {
  case s: String => { /* use s */ }
  case _ => { /* other */ }
}
```

### 4.3 For-Each Loop

**Symptom:**
```
error: Unexpected token in for loop
```

**Fix:**
```cj
// Java: for (String item : list)
// Cangjie:
for (item in list) {
  // item is already typed
}
```

### 4.4 Try-With-Resources

**Symptom:**
```
// <-- Java try-with-resources not supported -->
```

**Fix:**
```cj
// Java: try (FileReader fr = new FileReader(path)) { ... }
// Cangjie:
try {
  let fr = FileReader(path)
  // use fr
} catch (e: Exception) {
  // handle error
}
// Cangjie has RAII - resources auto-cleanup when scope ends
```

## 5. Cangjie Keyword Collision Errors

### 5.1 `init` Used as Method Name

**Symptom:**
```
error: unexpected token 'init'
error: 'init' is a keyword and cannot be used as identifier
```

**Cause:** `init` is a Cangjie constructor keyword. Java interface/class methods named `init()` are illegal in Cangjie.

**Fix:**
```cj
// Java: void init()
// Cangjie: rename to initialize()
func initialize() { ... }

// Update all call sites: obj.init() → obj.initialize()
```

**Docs:** See `cangjie-lang-features` skill → 类/class → init 构造函数

### 5.2 `type` Used as Field/Parameter Name

**Symptom:**
```
error: unexpected token 'type'
error: 'type' is a keyword and cannot be used as identifier
```

**Cause:** `type` is a Cangjie keyword (for type aliases). Java fields/params named `type` must be escaped or renamed.

**Fix:**
```cj
// Option 1: Backtick escaping (for fields/params)
var `type`: String = ""

// Option 2: Rename (preferred for clarity)
var kind: String = ""
```

**Docs:** See `cangjie-lang-features` skill → 基本概念 → 关键字

## 6. Enum Nesting Errors

### 6.1 Inner Enum Not Allowed

**Symptom:**
```
error: enum cannot be defined inside class
error: nested enum definition is not supported
```

**Cause:** Cangjie does NOT support enums nested inside classes. Java inner enums must be extracted to top-level.

**Fix:**
```cj
// Java: class Foo { enum Bar { A, B } }
// Cangjie: extract enum to top level
enum FooBar {
    A
    | B
}

class Foo {
    var bar: FooBar = FooBar.A
}
```

**IMPORTANT:** After extracting, update ALL references from `Foo.Bar` to `FooBar`.

## 7. Operator and Type Conversion Errors

### 7.1 Bitwise NOT Operator

**Symptom:**
```
error: '~' operator not supported
error: unexpected token '~'
```

**Cause:** Cangjie has NO bitwise NOT operator (`~` or `!`). Must use XOR.

**Fix:**
```cj
// Java: int result = ~value;
// Cangjie:
let result = (-1) ^ value
```

### 7.2 Int() Constructor Does Not Exist

**Symptom:**
```
error: 'Int' does not have a constructor
error: cannot find matching function Int()
```

**Cause:** Cangjie has no `Int()` constructor. Use `Int64()` or `Int32()` for string-to-int conversion.

**Fix:**
```cj
// Java: new Integer("123") or Integer.parseInt("123")
// Cangjie:
let value = Int64("123")
// or
let value = Int32("123")
```

### 7.3 Byte() Type Conversion from Int

**Symptom:**
```
error: no matching function for Byte(Int64)
error: cannot convert Int64 to Byte
```

**Cause:** `Byte` in Cangjie is `UInt8`. `Byte()` / `UInt8()` cannot accept `Int64` directly.

**Fix:**
```cj
// Java: byte b = (byte) intValue;
// Cangjie:
let b = UInt8(Int32(intValue))
// Or if value is small enough:
let b: UInt8 = UInt8(intValue.toInt32())
```

### 7.4 Thread.sleep() Does Not Exist

**Symptom:**
```
error: 'Thread' not found
error: 'sleep' is not a member of Thread
```

**Cause:** Cangjie's `sleep()` is a top-level function taking nanoseconds (Int64), not `Thread.sleep(ms)`.

**Fix:**
```cj
// Java: Thread.sleep(1000);
// Cangjie:
sleep(1000 * 1000000)  // 1000ms = 1_000_000_000ns
// Or more readable:
sleep(Duration.second * 1000)
```

**Docs:** See `cangjie-lang-features` skill → 并发编程 → sleep

### 7.5 String.isEmpty Needs Parentheses

**Symptom:**
```
error: 'isEmpty' is not a property of String
error: expected '()' for function call
```

**Cause:** In Cangjie, `isEmpty` is a function, not a property. Must call with parentheses.

**Fix:**
```cj
// Java: str.isEmpty()
// Cangjie:
str.isEmpty()  // WITH parentheses, not str.isEmpty
```

### 7.6 InputStream.close() Not Found

**Symptom:**
```
error: 'close' is not a member of InputStream
```

**Cause:** `close()` belongs to the `Resource` interface, not `InputStream`. Need to cast.

**Fix:**
```cj
import std.fs.Resource

// WRONG:
stream.close()

// CORRECT:
(stream as Resource).close()
```

**Docs:** See `cangjie-std` skill → io / fs sections

## 8. Inheritance Override Errors (HIGH FREQUENCY)

### 8.1 `redef` Used on Instance Methods

**Symptom:**
```
error: 'redef' cannot be used here
error: redef can only be used in open class
```

**Cause:** `redef` is ONLY for static methods in Cangjie. This was the #1 error source in log4j-core (259 errors).

**Fix:**
```cj
// WRONG: redef on instance method
public class Derived <: Base {
    public redef func format(...): String { ... }  // ❌ NEVER
}

// CORRECT: no keyword needed for instance method override
public class Derived <: Base {
    public func format(...): String { ... }  // ✅
}

// CORRECT: redef ONLY for static methods
public class Derived <: Base {
    public redef static func create(...): Derived { ... }  // ✅
}
```

**Docs:** See `cangjie-lang-features` skill → 类/class → 继承

### 8.2 Parent Method Not Marked `open`

**Symptom:**
```
error: cannot override function 'xxx' because it is not marked 'open'
```

**Cause:** In Cangjie, parent methods must be explicitly marked `open` for subclasses to override. This must propagate through the ENTIRE inheritance chain.

**Fix:**
```cj
// WRONG: parent method not open
public class Base {
    public func doWork(): Unit { ... }  // child CANNOT override
}

// CORRECT: add open to parent
public class Base {
    public open func doWork(): Unit { ... }  // now child can override
}
```

**IMPORTANT:** If the inheritance chain is GrandParent → Parent → Child, BOTH GrandParent and Parent must have `open` on the overridden method.

### 8.3 Class Not Marked `open` for Inheritance

**Symptom:**
```
error: class 'X' is not open and cannot be inherited
```

**Fix:**
```cj
// WRONG:
public class Base { ... }

// CORRECT:
public open class Base { ... }
```

### 8.4 `abstract` Methods Need `open` (Not `abstract` Keyword)

**Symptom:**
```
error: unexpected modifier 'abstract'
```

**Cause:** Cangjie uses `open func` without implementation body instead of Java's `abstract` keyword.

**Fix:**
```cj
// Java: public abstract void doWork();
// Cangjie:
public open func doWork(): Unit  // no body, no abstract keyword
```

## 9. UInt8/Byte Overflow Errors

### 9.1 UInt8 Constructor Overflow

**Symptom:**
```
error: no matching function for UInt8(Int64)
warning: implicit conversion may lose precision
```

**Cause:** Java `byte` is signed (-128 to 127), Cangjie `UInt8` is unsigned (0 to 255). Direct conversion from `Int64` to `UInt8` can overflow silently or fail.

**Fix:**
```cj
// Java: byte b = (byte) intValue;
// Cangjie: always mask with 0xFF
let b = UInt8(value & 0xFF)

// For Base64/Hex decoding: add bounds check
if (ch < 128) {
    let decoded = decodeMap[Int64(ch)]
    // ...
}
```

**Docs:** See `cangjie-lang-features` skill → 基本数据类型 → UInt8

### 9.2 String Index Returns UInt8 (Not Char)

**Symptom:**
```
error: cannot compare UInt8 with Int64
error: type mismatch: expected Rune, got UInt8
```

**Cause:** `String.toArray()` returns `Array<UInt8>` (bytes), `String[i]` returns `UInt8`. Character comparison needs Rune or ASCII code.

**Fix:**
```cj
// Java: if (str.charAt(i) == ';')
// Cangjie:
let bytes = str.toArray()
if (bytes[i] == 59) { ... }  // 59 = ASCII ';'

// Or use Rune for character iteration:
for (r in str) {
    if (UInt32(r) == 37) { ... }  // Rune → UInt32 comparison
}
```

## 10. Name Collision with Standard Library

### 10.1 `Configuration` Conflicts with std.core

**Symptom:**
```
error: reference to 'Configuration' is ambiguous
error: 'Configuration' is defined in multiple packages
```

**Cause:** Custom types like `Configuration` collide with `std.core.Configuration`. This happens when test files import both the translated package and stdlib.

**Fix:**
```cj
// WRONG: wildcard import brings in conflicting names
import logging_log4j_core.*

// CORRECT: use selective imports
import logging_log4j_core.{PatternLayout, MessageLayout, LoggerConfig}
// Or use alias:
import logging_log4j_core.{DefaultConfiguration as Log4jDefaultConfig}
```

**Best practice:** Put test files in an independent `tests/` package with selective imports. See `java2cangjie-translate` skill → Independent Test Directory Pattern.

### 10.2 `match` Keyword in Method Names

**Symptom:**
```
error: unexpected token 'match'
```

**Cause:** `match` is a Cangjie keyword. Java methods like `MimeType.match()` must be escaped.

**Fix:**
```cj
// Java: mt.match(otherType)
// Cangjie:
mt.`match`(otherType)
```

## 11. Collection Method Name Differences

### 11.1 `append` vs `add` / `put` vs Subscript

**Symptom:**
```
error: method 'append' not found on ArrayList
error: method 'put' not found on HashMap
error: method 'size' not found (expects parentheses)
```

**Fix:**
```cj
// Java: list.append(item)  →  Cangjie: list.add(item)
// Java: map.put(key, val)  →  Cangjie: map[key] = val
// Java: list.size()        →  Cangjie: list.size  (property, not method)
// Java: arr.length         →  Cangjie: arr.size   (property name differs)
// Java: list.removeAt(i)   →  Cangjie: list.remove(at: i)
// Java: sb.clear()         →  Cangjie: sb.reset()
```

**Docs:** See `cangjie-std` skill → collections; `cangjie-lang-features` → collections

When encountering new patterns not listed here:
1. Document the error (symptom)
2. Identify the root cause
3. Find the fix via documentation lookup
4. Add the pattern to this file

This file grows with real-world translation experience.
