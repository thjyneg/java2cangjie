# Java2Cangjie Plugin 修正记录

## 修正日期
2026-04-01

## 修正的文件
`/opt/codes/java2cangjie/skills/java2cangjie-translate/SKILL.md`

## 修正内容

### 1. 完善了 Java 到 Cangjie 的类型映射表
**问题**：缺少基础类型的映射
**修正**：添加了以下类型的映射
- `long` → `Int64`
- `int` → `Int`
- `byte` → `Byte`
- `byte[]` → `Array<Byte>`
- `boolean` → `Bool`
- `String` → `String`
- `float` → `Float32`
- `double` → `Float64`
- `char` → `Rune`

**重要说明**：
- `byte[]` 在 Cangjie 中是 `Array<Byte>` 而不是 `Byte[]`
- 数组初始化：`Array<Byte>(0, { 0 })`
- 使用 `Int64` 代替 Java 的 `long` 以避免溢出

### 2. 明确了目录结构差异
**问题**：未说明 Java Maven 项目与 Cangjie 项目的目录结构差异
**修正**：添加了 "Directory Structure Differences" 部分
- Java Maven: `src/main/java/包名/`
- Cangjie: `src/包名/` (直接在 src 下)
- 列出了常见错误和正确结构

### 3. 添加了 cjpm build 的扫描限制说明
**问题**：未说明 cjpm build 的已知限制
**修正**：添加了 "cjpm build Limitations" 部分
- 说明 cjpm 要求每个目录必须有 .cj 文件才能扫描子目录
- 提供了警告信息的示例
- 给出了两种解决方案：
  1. 使用 `cjc -p` 直接编译（推荐）
  2. 创建占位文件（不推荐）

### 4. 添加了编译工具选择指南
**问题**：只提到 cjpm build，未说明 cjc 的使用
**修正**：创建了工具选择对比表
- `cjc -p`：用于翻译流程，直接编译特定包
- `cjpm build`：用于最终项目构建，需要正确的目录结构
- 推荐翻译时使用 `cjc -p src/<package-path> --output-type=staticlib`

### 5. 添加了多层包名处理说明
**问题**：未说明多层包名（如 `net.lingala.zip4j`）的处理
**修正**：在目录结构部分添加了多层包名说明
- 保持相同的包结构：`package net.lingala.zip4j`
- 文件路径：`src/net/lingala/zip4j/ClassName.cj`
- cjpm.toml name 应该匹配基础模块名

### 6. 添加了项目初始化说明
**问题**：未说明如何为现有 Java 项目手动创建 Cangjie 项目结构
**修正**：添加了 "Project Initialization" 部分
- 说明不使用 `cjpm init` 进行转换
- 提供了手动创建目录结构的步骤
- 包含创建 cjpm.toml 的说明

### 7. 添加了项目清理指南
**问题**：未说明如何管理编译产生的临时文件和缓存
**修正**：添加了 "Project Cleanup" 部分
- 列出了清理命令：`cjpm clean` 或手动删除
- 列出了需要注意的目录：
  - `target/` - 构建输出目录
  - `target/release/` - 发布产物
  - `.cached/` - 编译器缓存
  - `*.a` - 静态库文件
  - `*.o` - 目标文件

### 8. 更新了 OpenCode 工作流程
**问题**：工作流程中仍建议使用 cjpm build
**修正**：更新为推荐使用 cjc -p 进行编译验证
- 在步骤 4 中添加了 "(recommended)" 标注
- 添加了关于使用 cjc 而非 cjpm 的说明

## 修正效果
- **修正前**：161 行
- **修正后**：260 行
- **新增内容**：99 行
- **新增章节**：
  - Type Notes
  - Directory Structure Differences (expanded)
  - cjpm build Limitations
  - Compilation Tool Selection
  - Multi-level package names
  - Project Initialization
  - Project Cleanup

## 验证
- 已验证编译命令 `cjc -p src/net/lingala/zip4j --output-type=staticlib` 可以正常工作
- 已成功编译 18 个文件，无错误
