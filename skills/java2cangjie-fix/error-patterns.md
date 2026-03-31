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

**Docs:** `docs/extra/ArrayList.md`, `docs/extra/HashMap.md`, `docs/extra/HashSet.md`

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

**Docs:** `docs/libs/std/fs/`, `docs/libs/std/io/`

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

**Docs:** `docs/extra/Option.md`

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

**Docs:** `docs/manual/` (generics section)

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

**Docs:** `docs/extra/String.md`

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

**Docs:** `docs/extra/Collection.md`

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
} except (e: Exception) {
  // handle error
}
// Cangjie has RAII - resources auto-cleanup when scope ends
```

## 5. Pattern Accumulation

When encountering new patterns not listed here:
1. Document the error (symptom)
2. Identify the root cause
3. Find the fix via documentation lookup
4. Add the pattern to this file

This file grows with real-world translation experience.
