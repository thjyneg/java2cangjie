---
name: java2cangjie-reference
description: "Use when looking up Cangjie API documentation, finding equivalent types/methods for Java code, or fixing specific translation errors. Keywords: ArrayList, HashMap, Option, String, 泛型"
---

# Documentation Lookup & Error Guide

## Quick Lookup

| 内容 | 路径 |
|------|------|
| 基础类型 | `docs/extra/` - Array, ArrayList, HashMap, String, Option |
| 标准库 | `docs/libs/std/` - collection, io, net, sync |
| 语言手册 | `docs/manual/` - 语法, 泛型, 并发, 错误处理 |
| 索引 | `references/` - packages_index.md, extra_index.md |

## Search Patterns

**查找类型API：**
```bash
# 1. 先在基础类型中查找
Grep: pattern="<TypeName>" path="docs/extra/"

# 2. 再在标准库中查找
Grep: pattern="<TypeName>" path="docs/libs/std/"
```

**查找方法/函数：**
```bash
Grep: pattern="func <name>|prop <name>" path="docs/libs/std/"
```

**查找示例代码：**
```bash
Glob: pattern="**/*samples/*.md" path="docs/libs/"
```

**查找语言概念：**
```bash
Grep: pattern="<keyword>" path="docs/manual/"
```

## Common Errors & Fixes

### 1. Type Not Found
```
error: Type 'ArrayList' not found
```
**修正**: 添加 `import std.collection.ArrayList`

### 2. Method Not Found
```
error: Method 'toString' not found
```
**修正**: Cangjie无通用toString，使用自定义方法或工具函数

### 3. Nullability Issues
```
error: Cannot assign nullable value to non-nullable type
```
**修正**: 使用 `Option<T>` 或 `??` 提供默认值

### 4. Generic Wildcard
```
// <-- Generic wildcard '? extends T' not supported -->
```
**修正**: 改用具体类型或泛型约束 `where T: <trait>`

### 5. synchronized Keyword
```
// <-- Java keyword 'synchronized' not supported -->
```
**修正**: 使用 `sync.Mutex` 或 `sync.ReentrantMutex`

## Java → Cangjie Mappings

| Java | Cangjie | 备注 |
|------|---------|------|
| `ArrayList<E>` | `std.collection.ArrayList<E>` | 动态数组 |
| `HashMap<K,V>` | `std.collection.HashMap<K,V>` | 哈希映射 |
| `HashSet<E>` | `std.collection.HashSet<E>` | 哈希集合 |
| `Optional<T>` | `Option<T>` | 可选值 |
| `null` | `None` | Option的None |
| `try/catch` | `try/except` | 异常处理 |
| `throw` | `throw` | 抛出异常 |
| `interface` | `interface` | 接口定义 |
| `@Override` | 不需要 | 隐式重写 |

## Documentation Structure

```
docs/
├── extra/              # 基础类型
│   ├── ArrayList.md
│   ├── HashMap.md
│   └── Option.md
├── libs/std/           # 标准库
│   └── <package>/
│       ├── *_package_overview.md
│       ├── *_package_api/
│       └── *_package_samples/
└── manual/             # 语言手册
    └── source_zh_cn/
```
