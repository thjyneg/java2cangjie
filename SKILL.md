---
name: java2cangjie
description: "Java to Cangjie code translation using j2cj tool with post-translation error correction. Use when Claude needs to: (1) Translate Java projects/directories to Cangjie, (2) Configure j2cj translation options (mode, classpath, etc.), (3) Fix translation errors using Cangjie language docs, (4) Understand Cangjie syntax and APIs for code corrections"
---

# Java2Cangjie Translation

Java到Cangjie代码翻译技能，集成j2cj工具和仓颉语言文档，提供完整的翻译流程和错误修正能力。

## Quick Start

### 翻译Java项目

```bash
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d <output_dir> [options] <java_source_files>
```

**示例**:
```bash
# 基本翻译（单个文件）
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output --mode codestyle ./java/src/Main.java

# 翻译多个文件
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output --mode codestyle ./java/src/*.java

# 带classpath的翻译
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output -cp ./lib/* --mode codestyle ./java/src/*.java

# 详细输出
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output -verbose --mode codestyle ./java/src/*.java
```

## Translation Workflow

**重要：此工作流程必须严格执行，不可跳过任何步骤。**

### Step 1: j2cj转换

使用 j2cj.jar 执行初始翻译。

**命令格式**:
```bash
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main [options] <source_files>
```

**Translation Modes**:
- **codestyle**: 生成符合Cangjie习惯的代码（推荐）
- **semantic**: 保持Java原有语义

**Options**:
| Option | Description |
|--------|-------------|
| `-d <dir>, --dest <dir>` | 目标目录，放置生成的文件（默认: 当前目录） |
| `-s <path>, --sourcepath <path>` | Java源码路径 |
| `-cp <path>, --classpath <path>` | Java classpath |
| `-mp <path>, --module-path <path>` | Java module path |
| `-m <mode>, --mode <mode>` | 翻译模式: codestyle 或 semantic |
| `-encoding <enc>` | 源文件编码 |
| `-verbose` | 详细输出 |

**输出目录说明**:
- 生成的Cangjie代码默认输出到当前目录
- 生成的文件会按照原Java源码的目录结构存放
- 使用 `-d` 参数指定自定义输出目录

**示例**:
```bash
# 翻译单个文件
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output --mode codestyle ./java/src/Main.java

# 翻译目录下所有Java文件
java --patch-module jdk.compiler=j2cj_tool/j2cj.jar -m jdk.compiler/com.excelsior.j2cj.main.Main -d ./cangjie_output -s ./java/src --mode codestyle ./java/src/**/*.java
```

### Step 2: 分析错误并输出修改方案

分析j2cj翻译结果中的错误和警告，**必须**基于skill中的Cangjie API文档和示例文档来制定修改方案。

**分析流程**:
1. 识别所有错误类型（类型未找到、方法未找到、语法错误、空值问题等）
2. **必须**在`docs/`目录中查找对应的类型/方法/语法
3. **必须**参考`docs/libs/*/samples/`中的示例代码
4. 为每个错误提供详细的修改方案，包括：
   - 问题分析
   - 对应的Cangjie API/语法
   - 参考的文档路径和示例代码
   - 具体的修改代码

**强制性文档查找流程**（必须严格执行）：

对于每个需要查找的类型/方法/语法，必须按以下顺序执行查找：

**查找优先级顺序**：

1. **第一步：在基础类型文档中查找**
   - 使用 Grep 在 `docs/extra/` 目录搜索
   - 命令：`Grep: pattern="<TypeName>" path="docs/extra/"`
   - 适用于：ArrayList、HashMap、String、Option、Array 等基础类型

2. **第二步：在标准库API文档中查找**
   - 使用 Grep 在 `docs/libs/std/` 目录搜索
   - 命令：`Grep: pattern="<TypeName>" path="docs/libs/std/"`
   - 如未找到，尝试搜索方法名：`Grep: pattern="func <MethodName>|prop <MethodName>" path="docs/libs/std/"`

3. **第三步：查找示例代码**
   - 使用 Glob 查找相关包的 samples 目录
   - 命令：`Glob: pattern="**/*samples/sample_<TypeName>*.md" path="docs/libs/"`
   - 或使用 Grep 搜索所有 samples：`Grep: pattern="<TypeName>" path="docs/libs/*/*/samples/"`

4. **第四步：在语言手册中查找**
   - 使用 Grep 在 `docs/manual/` 目录搜索语言概念
   - 命令：`Grep: pattern="<keyword>" path="docs/manual/"`
   - 适用于：泛型、并发、错误处理、match 等语言特性

5. **第五步：查找包概览文档**
   - 定位到具体包的概览文档
   - 文件路径：`docs/libs/std/<package>/<package>_package_overview.md`
   - 例如：`docs/libs/std/collection/collection_package_overview.md`

**查找结果记录要求**：

每次查找必须记录以下信息：
- 查找的关键词/类型名
- 使用的工具（Grep/Glob/Read）
- 查找的路径
- 找到的文件列表（如果有）
- 未找到时的警告信息

**查找失败处理策略**：

如果在上述所有步骤中都未找到相关文档：
1. 记录警告："未找到 <类型/方法> 的官方文档"
2. 尝试在 references/ 目录的索引文件中查找：
   - `references/extra_index.md`（基础类型索引）
   - `references/packages_index.md`（标准库包索引）
   - `references/manual_index.md`（语言手册索引）
3. 如仍无法找到，在修改方案中明确说明："基于Cangjie语言通用规则推断，缺少官方文档参考"

### Step 3: 用户确认

将Step 2中的修改方案展示给用户，**必须**等待用户确认后才能进行修改。

**确认内容**:
- 显示所有修改方案
- 每个方案的改动原因
- 让用户确认是否继续修改

**示例确认格式**:
```
发现了以下错误，建议修改方案：

1. Type 'ArrayList' not found
   - 问题：Java的ArrayList需要映射到Cangjie标准库
   - 解决方案：使用 std.collection.ArrayList
   - 文档：docs/libs/std/collection/collection_package_api/...

2. Method 'toString' not found
   - 问题：Cangjie中没有直接对应的toString方法
   - 解决方案：使用工具函数或重写
   - 文档：docs/extra/String.md

是否确认执行以上修改？(y/n)
```

### Step 4: 编译并修正错误（最多20轮）

用户确认后，执行修改并尝试编译。如有错误，继续修正，最多进行20轮迭代。

**编译和修正流程**（必须严格执行）:

1. **分析文件依赖关系**（详见下方"依赖分析"章节）
2. **生成自下而上的TODO清单**（从叶子节点到根节点）
3. **识别`<!-- -->`标记的不支持代码**（详见下方"识别j2cj不支持的代码"）
4. **创建adapters文件夹**，为外部依赖API创建mock接口
5. **按照TODO清单自下而上依次修复和编译**：
   - 从第1层（无依赖）开始
   - **每次修改后必须立即执行 `cjpm build` 进行编译**
   - 确认当前层编译通过
   - 再处理下一层
6. **收集编译错误和警告信息**：
   - **必须记录每次编译的完整输出**
   - **必须记录编译是否成功（exit code）**
7. **分析新错误**，回到Step 2重新分析
8. **重复Step 2-4**，直到：
   - 所有错误修复成功
   - 达到20轮上限

**重要：修改-编译迭代规则（强制执行）**：

- **每次修改代码后，必须立即执行编译**
  - 使用命令：`Bash: command="cd <output_dir> && cjpm build"`
  - 检查编译结果：`echo $?`（0表示成功）

- **编译成功的处理**：
  - 记录："编译成功 ✓"
  - 继续处理下一层或下一个错误

- **编译失败的处理**：
  - 记录完整的错误信息
  - 分析错误原因
  - 回到 Step 2 查找相关文档
  - 修正错误后再次编译
  - 重复此过程直到编译成功

- **迭代记录格式**：
  ```
  === 第N轮修复 ===

  【修改文件】: service/UserService.cj
  【修改内容】: 将 ArrayList<String> 改为 ArrayList<String>
  【修改原因】: Cangjie 泛型语法要求

  【执行编译】:
  命令: cd cangjie_output && cjpm build
  结果: 失败 ✗

  【编译错误】:
  error: Type 'ArrayList' not found
  --> service/UserService.cj:15:10

  【下一步】: 查找 ArrayList 文档，添加正确的 import
  ```

**依赖分析**:
在修复错误前，必须先分析Cangjie文件之间的依赖关系，确定修复顺序。

**依赖分析方法**:
```bash
# 方法1: 通过import语句分析依赖
grep -r "^import" <output_dir> --include="*.cj" | sort | uniq

# 方法2: 分析目录结构和包关系
find <output_dir> -name "*.cj" -type f | xargs grep "^import"
```

**生成依赖图**:
1. 遍历所有.cj文件，提取import语句
2. 建立文件依赖图：A imports B 表示 A依赖B
3. 识别叶子节点：没有依赖其他本地文件的文件
4. 拓扑排序：确定从叶子到根的修复顺序

**TODO清单格式**:
```
=== 依赖分析和TODO清单 ===

【第1层 - 无依赖文件】（优先修复）
  - common/utils/Helper.cj
  - common/Constants.cj

【第2层 - 依赖第1层】
  - service/BaseService.cj (依赖: common/utils/Helper.cj)

【第3层 - 依赖第2层】
  - service/UserService.cj (依赖: service/BaseService.cj)
  - service/DataService.cj (依赖: common/utils/Helper.cj, service/BaseService.cj)

【第4层 - 依赖第3层】
  - main/Main.cj (依赖: service/UserService.cj, service/DataService.cj)

修复顺序建议: 按层级从低到高依次修复
```

**依赖分析示例**:
假设有以下文件结构：
```
cangjie_output/
├── common/
│   ├── Constants.cj        # 无依赖
│   └── utils/
│       └── Helper.cj       # 无依赖
└── service/
    ├── BaseService.cj      # import common.utils.Helper
    ├── UserService.cj      # import service.BaseService
    └── DataService.cj      # import common.utils.Helper, service.BaseService
```

生成的TODO清单（自下而上）：
1. 第1层: Constants.cj, Helper.cj
2. 第2层: BaseService.cj
3. 第3层: UserService.cj, DataService.cj

**识别j2cj不支持的代码**:
j2cj转换工具对于无法直接转换的Java代码，会用`<!-- -->`注释包裹，需要AI识别并修复。

**查找待修复代码**:
```bash
# 查找所有包含 <!-- --> 标记的文件
grep -r "<!-- " <output_dir> --include="*.cj" -l

# 查看具体的标记内容
grep -r "<!-- " <output_dir> --include="*.cj" -A 2 -B 2
```

**标记示例和处理**:
```cj
// 示例1: 不支持的Java API
// <!-- TODO: Java方法 'System.currentTimeMillis()' 无直接对应，需要替换 -->
// 原代码: let time = System.currentTimeMillis()

// 示例2: 不支持的语法结构
// <!-- TODO: Java的synchronized关键字需要改用Cangjie的并发机制 -->
// synchronized(this) { ... }

// 示例3: 复杂泛型
// <!-- TODO: Java泛型通配符 '? extends T' 在Cangjie中需要特殊处理 -->
```

**外部依赖Mock策略**:
对于项目依赖的外部库API，创建`adapters`文件夹进行mock，保证编译通过。

**adapters目录结构**:
```
<output_dir>/
├── adapters/                    # 外部依赖mock目录
│   ├── AndroidAdapter.cj       # Android API mock
│   ├── ThirdPartyLib.cj        # 第三方库mock
│   └── JvmApi.cj               # JVM特有API mock
├── common/
└── service/
```

**创建Mock接口**:
```cj
// adapters/ThirdPartyLib.cj
// Mock第三方库接口，仅保证编译通过

public class ThirdPartyLib {
    // TODO: 实现真实的第三方库调用逻辑
    public static func getInstance(): ThirdPartyLib {
        // 占位实现
        return ThirdPartyLib()
    }

    public func doSomething(input: String): String {
        // 占位实现
        return input
    }
}
```

**自下而上编译流程**（强制执行）:

编译也必须按照依赖顺序自下而上进行，下层编译通过后再处理上层。

**编译顺序（必须严格执行）**:
```
1. 【第1层】编译无依赖文件
   Bash: command="cd cangjie_output && cjpm build common/Constants.cj common/utils/Helper.cj"
   ↓ 检查编译结果: echo $?
   ↓ 确认编译通过（exit code = 0）

2. 【第2层】编译依赖第1层的文件
   Bash: command="cd cangjie_output && cjpm build service/BaseService.cj"
   ↓ 检查编译结果: echo $?
   ↓ 确认编译通过（exit code = 0）

3. 【第3层】编译依赖第2层的文件
   Bash: command="cd cangjie_output && cjpm build service/UserService.cj service/DataService.cj"
   ↓ 检查编译结果: echo $?
   ↓ 确认编译通过（exit code = 0）

4. 【最终】整体编译
   Bash: command="cd cangjie_output && cjpm build"
   ↓ 检查编译结果: echo $?
   ↓ 确认编译通过（exit code = 0）
```

**编译检查规则（强制执行）**:

- 每次编译后必须检查 exit code：
  - `echo $?` 返回 0 → 编译成功 ✓
  - `echo $?` 返回非0 → 编译失败 ✗

- 编译失败时必须：
  1. 记录完整的错误输出
  2. 分析错误原因
  3. 修正代码
  4. 重新编译
  5. 重复直到成功

- **禁止跳过编译步骤**：
  - 修改代码后必须立即编译
  - 不得假设修改正确
  - 不得批量修改后统一编译

**单层编译命令**:
```bash
# 编译单个文件及其依赖
cjpm build <file.cj>

# 编译某个包
cjpm build <package_name>

# 检查编译是否成功
echo $?  # 0表示成功
```

**编译失败处理策略**:
1. **当前层编译失败**: 仅修复当前层的错误，不要修改下层代码
2. **缺少外部依赖**: 在`adapters/`中创建mock接口
3. **类型不匹配**: 检查下层API返回类型，调整上层调用代码
4. **包导入失败**: 确认下层已编译成功，检查import路径

**迭代修复模板**（强制执行）:
```
=== 第N轮修复 ===

【当前层】: 第2层 - service/BaseService.cj

【编译结果】: 失败 ✗
  error: Type 'Helper' not found in service/BaseService.cj:15

【依赖检查】:
  ✗ common/utils/Helper.cj 未编译通过
  → 先修复第1层

【修复动作】:
  1. 回退到第1层修复 Helper.cj
  2. 修正 Helper.cj 代码
  3. **执行编译**: Bash: command="cd cangjie_output && cjpm build common/utils/Helper.cj"
  4. **检查结果**: echo $?
  5. 确认编译通过后，重新处理第2层
  6. **执行编译**: Bash: command="cd cangjie_output && cjpm build service/BaseService.cj"
  7. **检查结果**: echo $?
  8. 如失败，重复步骤2-7

【修改记录】:
  - 文件: common/utils/Helper.cj
  - 修改: 添加了正确的 import 语句
  - 编译: 成功 ✓
```

**cjpm build 详细步骤**:
```bash
# 1. 确定输出目录（默认为 cangjie_output）
cd <output_dir>

# 2. 确认 cjpm.toml 存在
ls cjpm.toml

# 3. 执行编译
cjpm build

# 4. 如果有依赖问题，先更新依赖
cjpm update

# 5. 重新编译
cjpm build
```

**常见编译问题处理**:
- **cjpm.toml 不存在**: 检查输出目录是否正确，或手动创建 cjpm.toml
- **依赖下载失败**: 运行 `cjpm update` 更新依赖
- **编译缓存问题**: 运行 `cjpm clean` 清理后重新编译

**第N轮迭代格式**（强制执行）:
```
--- 迭代轮次: 3/20 ---

修改应用：
- [文件] 错误位置 -> 修正代码

执行编译：
- 命令: Bash: command="cd cangjie_output && cjpm build"
- 检查: echo $?

编译结果：
- 成功/失败
- 新错误: (列出错误)

下一步：
- [如成功] 继续处理下一层/下一个错误
- [如失败] 分析错误，重新修正，再次编译

是否继续下一轮？
```

### Step 5: 输出转换报告

所有修正完成后，生成并输出完整的转换报告。

**报告内容**:
1. **翻译统计**
   - Java文件数量
   - 生成的Cangjie文件数量
   - 代码行数对比

2. **错误修正统计**
   - 初始错误数量
   - 修正轮次
   - 每轮修正的错误数
   - 最终未解决错误（如有）

3. **修改记录**
   - 每个文件的修改点列表
   - 修改前后的代码对比

4. **最终状态**
   - 翻译是否成功完成
   - 剩余问题和建议
   - Cangjie代码质量评估

**报告格式示例**:
```
========================================
      Java to Cangjie 转换报告
========================================

翻译统计:
  Java文件: 15
  Cangjie文件: 15
  Java代码行: 2,456
  Cangjie代码行: 2,102

错误修正统计:
  初始错误: 42
  修正轮次: 5
  总计修正: 38
  未解决错误: 4

修改记录:
  [文件名]
    - 错误1: 修正说明
    - 错误2: 修正说明

最终状态:
  翻译状态: 部分成功
  剩余问题: [列出未解决的错误]
  建议: [给出改进建议]

========================================
```

## Error Correction Guide

### Common Translation Errors

#### 1. Type Not Found

**错误示例**:
```
error: Type 'ArrayList' not found
```

**修正步骤**:
1. 在Cangjie文档中查找ArrayList对应的类型
2. 通常 `ArrayList` 映射到 `std.collection.ArrayList` 或 `Array`
3. 更新import和类型声明

**查找文档**:
```
Grep: pattern="ArrayList" path="docs/libs/std/collection/"
```

#### 2. Method Not Found

**错误示例**:
```
error: Method 'toString' not found in type 'Object'
```

**修正步骤**:
1. 查找目标类型的API文档
2. 确认方法名称和参数
3. 如无直接对应，使用工具函数或改写逻辑

**查找文档**:
```
Grep: pattern="func toString|prop toString" path="docs/"
```

#### 3. Nullability Issues

**错误示例**:
```
error: Cannot assign nullable value to non-nullable type
```

**修正步骤**:
1. 检查Cangjie的Option类型使用
2. 使用 `??` 提供默认值或正确处理空值

**查找文档**:
```
Grep: pattern="Option" path="docs/extra/Option.md"
```

## Cangjie Documentation Lookup

### Quick Lookup

**基础类型**: 见 [extra_index.md](references/extra_index.md) - Array, ArrayList, HashMap, String, Option, Tuple等

**标准库包**: 见 [packages_index.md](references/packages_index.md) - collection, io, net, sync, time等

**语言手册**: 见 [manual_index.md](references/manual_index.md) - 基础概念、类接口、泛型、并发、错误处理等

### Search Patterns（强制性执行）

**重要：以下查找模式必须严格执行，不得跳过任何步骤。**

根据查询类型使用相应搜索模式：

#### 查找特定类型的API（必须执行）

**第一步：在基础类型文档中查找**
```
Grep: pattern="<TypeName>" path="docs/extra/"
```

**第二步：在标准库中查找**
```
Grep: pattern="<TypeName>" path="docs/libs/std/"
```

**例如**：查找 "ArrayList" 或 "HashMap"
```bash
# 先在基础类型中查找
Grep: pattern="ArrayList" path="docs/extra/"

# 如未找到，在标准库中查找
Grep: pattern="ArrayList" path="docs/libs/std/"
```

#### 查找函数或方法（必须执行）

**第一步：在标准库中查找函数定义**
```
Grep: pattern="func <MethodName>|prop <MethodName>" path="docs/libs/std/"
```

**第二步：在所有文档中查找**
```
Grep: pattern="func <MethodName>|prop <MethodName>|init\(" path="docs/"
```

**例如**：查找 "add" 方法
```bash
# 先在标准库中查找
Grep: pattern="func add|prop add" path="docs/libs/std/"

# 如未找到，在所有文档中查找
Grep: pattern="func add|prop add|init\(" path="docs/"
```

#### 查找示例代码（必须执行）

**第一步：使用 Glob 查找所有示例文件**
```
Glob: pattern="**/*samples/*.md" path="docs/libs/"
```

**第二步：使用 Grep 在 samples 目录中搜索特定类型**
```
Grep: pattern="<TypeName>" path="docs/libs/*/*/samples/"
```

**例如**：查找 ArrayList 的示例
```bash
# 方法1：列出所有示例文件
Glob: pattern="**/*samples/*.md" path="docs/libs/"

# 方法2：在 samples 中搜索 ArrayList
Grep: pattern="ArrayList" path="docs/libs/*/*/samples/"
```

#### 查找语言概念（必须执行）

**第一步：在语言手册中查找**
```
Grep: pattern="<keyword>" path="docs/manual/"
```

**第二步：如果手册中未找到，在所有文档中搜索**
```
Grep: pattern="<keyword>" path="docs/"
```

**例如**：查找 "match", "泛型", "Option"
```bash
# 先在语言手册中查找
Grep: pattern="match" path="docs/manual/"

# 如未找到，在所有文档中搜索
Grep: pattern="match" path="docs/"
```

#### 查找特定包的概览（必须执行）

**直接读取包概览文档**
```
Read: file_path="docs/libs/std/<package>/<package>_package_overview.md"
```

**例如**：查找 collection 包的概览
```bash
Read: file_path="docs/libs/std/collection/collection_package_overview.md"
```

**查找包的API文档**
```
Read: file_path="docs/libs/std/<package>/<package>_package_api/<package>_package_class.md"
```

**查找包的示例**
```
Glob: pattern="**/<package>_package_samples/*.md" path="docs/libs/std/"
```

### Documentation Structure

```
docs/
├── extra/              # 基础类型和工具（Array.md, ArrayList.md, HashMap.md, String.md, Option.md等）
├── libs/               # 标准库
│   ├── std/            # 标准库包（collection, io, net, sync, time等）
│   │   └── <package>/
│   │       ├── <package>_package_overview.md      # 包概览
│   │       ├── <package>_package_api/            # API文档目录
│   │       │   ├── <package>_package_class.md
│   │       │   ├── <package>_package_function.md
│   │       │   └── <package>_package_interface.md
│   │       └── <package>_package_samples/        # 示例代码目录
│   │           └── sample_*.md                   # 示例文件（如sample_arraylist_add.md）
│   └── stdx/           # 扩展库
└── manual/
    └── source_zh_cn/   # 语言手册（中文版）
```

**重要说明**：
- 示例文件命名格式为 `sample_*.md`（如 `sample_arraylist_add.md`），不是 `*_package_*.md` 格式
- 所有API文档都在 `<package>_package_api/` 目录下
- 每个包都有独立的概览文档和示例目录

## Post-Translation Verification

翻译完成后，建议进行以下验证：

1. **编译检查**: 使用cjc编译生成的Cangjie代码
2. **测试运行**: 如果可能，运行测试验证功能
3. **代码审查**: 对照Java原始代码检查逻辑一致性

## Resources

### j2cj_tool/
Bundled j2cj translation tool:

- **j2cj.jar**: Java to Cangjie translation tool (J2CJ 1.7.99)
- **j2cjlib/**: Cangjie library dependencies
- **j2cjlib_android/**: Android-specific library dependencies
- **j2cj-user-guide-en.pdf**: J2CJ user guide documentation

### references/
Cangjie documentation indices:

- **packages_index.md**: Standard library and extension library package index
- **extra_index.md**: Basic types index
- **manual_index.md**: Language manual topic index

### docs/
Complete Cangjie documentation corpus including:

- **extra/**: Basic types (Array, ArrayList, HashMap, String, Option, Tuple, etc.)
- **libs/std/**: Standard library APIs with examples
- **libs/stdx/**: Extension library
- **manual/**: Language manual (syntax, types, generics, concurrency, etc.)
