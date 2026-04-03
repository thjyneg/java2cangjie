# Installing Java2Cangjie Plugin for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- 仓颉编译器 `cjpm`（可选，用于编译验证）

## Installation

### 方式一：从 GitHub 自动安装（推荐）

在 `opencode.json`（全局 `~/.config/opencode/opencode.json` 或项目级）的 `plugin` 数组中添加：

```json
{
  "plugin": ["java2cangjie-superpowers@git+https://github.com/thjyneg/java2cangjie.git"]
}
```

重启 OpenCode，插件会自动安装并注册所有技能和工具。

**验证**：使用 skill 工具列出技能，应包含 `java2cangjie-*` 和 `cangjie-*` 系列。也可以运行：

```bash
opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie
```

**固定版本**：URL 后加 `#<tag>`，例如：

```json
{
  "plugin": ["java2cangjie-superpowers@git+https://github.com/thjyneg/java2cangjie.git#v3.0.0"]
}
```

### 方式二：项目级本地安装

将仓库克隆到项目中，OpenCode 启动时会自动加载 `.opencode/plugins/` 目录下的插件：

```bash
# 在项目根目录下
git clone https://github.com/thjyneg/java2cangjie.git .java2cangjie
```

然后在项目根目录创建 `.opencode/plugins/` 目录，并添加符号链接：

**Linux/macOS：**
```bash
mkdir -p .opencode/plugins
ln -s ../../.java2cangjie/.opencode/plugins/java2cangjie.js .opencode/plugins/java2cangjie.js
```

**Windows（以管理员身份运行）：**
```powershell
New-Item -ItemType Directory -Force -Path .opencode\plugins
New-Item -ItemType SymbolicLink -Path ".opencode\plugins\java2cangjie.js" -Target ".java2cangjie\.opencode\plugins\java2cangjie.js"
```

> **注意**：插件通过相对路径 `../../skills` 定位技能目录，因此必须使用符号链接，不能直接复制文件。

### 方式三：全局本地安装

将仓库克隆到 OpenCode 全局插件目录：

```bash
# 克隆到全局配置目录
git clone https://github.com/thjyneg/java2cangjie.git ~/.config/opencode/java2cangjie
```

创建符号链接到全局插件目录：

**Linux/macOS：**
```bash
ln -s ../java2cangjie/.opencode/plugins/java2cangjie.js ~/.config/opencode/plugins/java2cangjie.js
```

**Windows（以管理员身份运行）：**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.config\opencode\plugins\java2cangjie.js" -Target "$env:USERPROFILE\.config\opencode\java2cangjie\.opencode\plugins\java2cangjie.js"
```

这样在任何项目中启动 OpenCode 都可以使用 java2cangjie 插件。

## Plugin Tools

插件注册以下工作流控制工具：

| 工具 | 说明 |
|------|------|
| `analyze_project` | 分析 Java 项目结构和依赖 DAG |
| `next_batch` | 获取下一批待翻译文件（按依赖顺序） |
| `mark_complete` | 标记文件翻译完成 |
| `mark_blocked` | 标记文件翻译阻塞 |
| `translation_status` | 查看翻译进度 |

## Skills

插件提供以下技能：

| 技能 | 说明 |
|------|------|
| `using-java2cangjie` | Bootstrap 技能（自动注入） |
| `java2cangjie-translate` | 翻译执行 |
| `java2cangjie-fix` | 编译错误修复 |
| `java2cangjie-report` | 翻译报告生成 |
| `cangjie-lang-features` | 仓颉语言特性 |
| `cangjie-std` | 标准库速查 |
| `cangjie-stdx` | 扩展标准库 |
| `cangjie-toolchains` | 工具链文档 |
| `cangjie-regulations` | 编码规范 |
| `cangjie-original-docs` | 完整原始文档 fallback |

## Usage

```
use skill tool to load java2cangjie-translate
use skill tool to list skills
```

开始翻译：

```
请将 /path/to/java-project 翻译为仓颉语言
```

## Updating

### GitHub 自动安装方式

重启 OpenCode 即可自动更新。固定版本需手动更改 tag。

### 本地安装方式

```bash
cd <clone_dir> && git pull
```

## Troubleshooting

### Plugin not loading

1. 检查日志：`opencode run --print-logs "hello" 2>&1 | grep -i java2cangjie`
2. 确认配置正确（GitHub URL 或本地符号链接）
3. 确保 OpenCode 版本 >= 1.0.0

### Skills not found

1. 使用 `skill` 工具列出已发现的技能
2. 检查插件是否成功加载（见上方日志检查）
3. 本地安装时确认符号链接指向正确（`../../skills` 相对路径）

### Tool mapping

当技能引用 Claude Code 工具时：
- `TodoWrite` → `todowrite`
- `Task` with subagents → `@mention` syntax
- `Skill` tool → OpenCode 的原生 `skill` 工具
- File operations → 原生文件操作工具

## Claude Code Installation

如使用 Claude Code，请参考项目根目录 [README.md](../README.md) 中的「方式一：Claude Code」章节。

## Getting Help

- 报告问题：https://github.com/thjyneg/java2cangjie/issues
