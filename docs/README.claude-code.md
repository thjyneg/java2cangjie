# Claude Code 安装指南

## 前置要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 已安装
- 仓颉工具链已安装（`cjpm`、`cjc`），用于编译验证
- Python 3.8+（可选，用于依赖分析脚本）

## 安装方式

### 方式一：项目级安装（推荐）

在项目根目录的 `.claude/settings.json` 中配置插件路径：

```json
{
  "permissions": {
    "allow": ["Bash(python *cjpm-build*)", "Bash(python *analyze_deps.py*)"]
  }
}
```

然后将本项目目录路径告诉 Claude Code：

```bash
claude --plugin-dir /path/to/java2cangjie
```

### 方式二：全局安装

将仓库克隆到 Claude Code 插件目录：

```bash
# macOS / Linux
git clone https://github.com/thjyneg/java2cangjie.git ~/.claude/plugins/java2cangjie

# Windows (Git Bash)
git clone https://github.com/thjyneg/java2cangjie.git "%USERPROFILE%\.claude\plugins\java2cangjie"
```

### 方式三：注册 hooks（手动）

如果方式一和方式二都不适用，可在全局 `settings.json` 中手动注册 SessionStart hook：

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|clear|compact",
      "hooks": [{
        "type": "command",
        "command": "\"/path/to/java2cangjie/hooks/run-hook.cmd\" session-start",
        "async": false
      }]
    }]
  }
}
```

## 验证安装

启动新的 Claude Code 会话后，系统提示应包含 "Java to Cangjie translation system"。

验证技能可用性：

```
请列出所有 java2cangjie 相关技能
```

应看到：
- `using-java2cangjie` — 引导技能
- `java2cangjie-translate` — 翻译映射规则
- `java2cangjie-fix` — 错误修复
- `java2cangjie-report` — 报告生成
- `cangjie-*` — 仓颉文档系列（6个）

## 快速开始

```bash
cd /path/to/java-project

# 在 Claude Code 中：
请将这个 Java 项目翻译为仓颉语言
```

AI 会自动：
1. 分析 Java 项目结构和依赖关系
2. 按依赖顺序分批翻译（叶子文件优先）
3. 每批翻译后编译验证
4. 编译失败时查文档修复（最多 3 次）
5. 生成翻译报告

## 翻译输出

翻译结果保存在 `<java_project>/j2cjgenerated/`，保持原始包结构。
