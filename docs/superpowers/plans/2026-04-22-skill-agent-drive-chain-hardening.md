# Agent/Skill 驱动链路加固 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 skill/agent 链路中 7 个可能导致步骤遗漏的问题，确保翻译工作流不依赖 AI 记忆。

**Architecture:** 在 skill 中补充 TodoWrite 约束、修正脚本路径、补齐缺失的工作流步骤。在 agent 中声明 TodoWrite 工具权限。

**Tech Stack:** Markdown (skills/agents), Bash (hooks)

---

### Task 1: 修复 bootstrap skill 中的脚本路径和无效引用

**Files:**
- Modify: `skills/using-java2cangjie/SKILL.md:33,71`

- [ ] **Step 1: 修复 analyze_deps.py 路径**

将第 33 行：
```
1. Runs `scripts/analyze_deps.py` for dependency analysis and batch planning
```
改为：
```
1. Runs `python <PLUGIN_ROOT>/scripts/analyze_deps.py` for dependency analysis and batch planning
```

- [ ] **Step 2: 删除不存在的 checkpoint 引用**

将第 71 行：
```
- Checkpoint template: `templates/checkpoint.md`
```
整行删除。

- [ ] **Step 3: 验证无残留的裸 `scripts/` 路径**

Search: `grep -n 'scripts/' skills/using-java2cangjie/SKILL.md`
Expected: 只有 `<PLUGIN_ROOT>/scripts/` 形式

---

### Task 2: 为 translate skill 添加 TodoWrite 约束

**Files:**
- Modify: `skills/java2cangjie-translate/SKILL.md` — 在 Translation Loop 开头添加 TodoWrite 要求

- [ ] **Step 1: 在 Translation Loop 章节开头插入 TodoWrite 要求**

在 `## Translation Loop` 下方、`For each batch` 之前插入：

```markdown
**You MUST use TodoWrite to track each batch.** Create the todo list for every batch before starting:

```
TodoWrite: [
  {"content": "Read Java source files for batch", "status": "pending", "activeForm": "Reading Java source files"},
  {"content": "Scan imports and create mock stubs (if needed)", "status": "pending", "activeForm": "Scanning imports and creating mock stubs"},
  {"content": "Query Cangjie documentation for mappings", "status": "pending", "activeForm": "Querying Cangjie documentation"},
  {"content": "Translate files in batch", "status": "pending", "activeForm": "Translating files"},
  {"content": "Compile: python <PLUGIN_ROOT>/scripts/cjpm-build <module>", "status": "pending", "activeForm": "Compiling translated code"},
  {"content": "Fix errors (if compilation failed)", "status": "pending", "activeForm": "Fixing compilation errors"},
  {"content": "Update state file and proceed to next batch", "status": "pending", "activeForm": "Updating state file"}
]
```

Mark each task `in_progress` before starting, `completed` immediately after finishing. Only ONE task in_progress at a time.
```

- [ ] **Step 2: 验证 TodoWrite 模板包含 "create mock stubs" 步骤**

Read the modified section and confirm "Scan imports and create mock stubs" is present.

---

### Task 3: 为 report skill 添加 TodoWrite 约束

**Files:**
- Modify: `skills/java2cangjie-report/SKILL.md` — 在 Overview 后插入 TodoWrite 要求

- [ ] **Step 1: 在 `## Overview` 和 `## Report Sections` 之间插入 TodoWrite 要求**

```markdown
## Report Generation Discipline

**Use TodoWrite to track report sections.** Create the list before starting:

```
TodoWrite: [
  {"content": "Generate Executive Summary", "status": "pending", "activeForm": "Generating Executive Summary"},
  {"content": "Collect Translation Statistics", "status": "pending", "activeForm": "Collecting Translation Statistics"},
  {"content": "Analyze Error Breakdown from state file", "status": "pending", "activeForm": "Analyzing Error Breakdown"},
  {"content": "Verify Compilation Status", "status": "pending", "activeForm": "Verifying Compilation Status"},
  {"content": "Summarize Batch Progress", "status": "pending", "activeForm": "Summarizing Batch Progress"},
  {"content": "Write Recommendations", "status": "pending", "activeForm": "Writing Recommendations"},
  {"content": "Save report to <output_dir>/TRANSLATION_REPORT.md", "status": "pending", "activeForm": "Saving report file"}
]
```

Mark each section `completed` as you finish it. Do NOT skip sections.
```

---

### Task 4: 补充 agent 的 mock stub 步骤和 TodoWrite 工具声明

**Files:**
- Modify: `agents/cangjie-translate-engineer.md`

- [ ] **Step 1: 在 frontmatter tools 中添加 TodoWrite**

将：
```yaml
tools:
  write: true
  edit: true
  bash: true
```
改为：
```yaml
tools:
  write: true
  edit: true
  bash: true
  todowrite: true
```

- [ ] **Step 2: 在 Translation Workflow 的 TodoWrite 模板中添加 mock 步骤**

将现有的 Translation Workflow TodoWrite 模板：
```
TodoWrite: [
  {"content": "Read Java source files and understand structure", ...},
  {"content": "Query Cangjie docs for API/language mappings needed", ...},
  {"content": "Translate <File1>.java → <File1>.cj", ...},
  ...
]
```
改为（在 "Query Cangjie docs" 之前插入 mock 步骤）：
```
TodoWrite: [
  {"content": "Read Java source files and understand structure", "status": "pending", "activeForm": "Reading Java source files"},
  {"content": "Scan imports: identify mock stubs needed vs Cangjie std mappings", "status": "pending", "activeForm": "Scanning imports for mock stubs"},
  {"content": "Create mock stubs in _mock/ directory (if needed)", "status": "pending", "activeForm": "Creating mock stubs"},
  {"content": "Query Cangjie docs for API/language mappings needed", "status": "pending", "activeForm": "Querying Cangjie documentation"},
  {"content": "Translate <File1>.java → <File1>.cj", "status": "pending", "activeForm": "Translating <File1>"},
  {"content": "Translate <File2>.java → <File2>.cj", "status": "pending", "activeForm": "Translating <File2>"},
  {"content": "Compile: python <PLUGIN_ROOT>/scripts/cjpm-build <module>", "status": "pending", "activeForm": "Compiling translated code"},
  {"content": "Fix compilation errors (if any)", "status": "pending", "activeForm": "Fixing compilation errors"},
  {"content": "Report results", "status": "pending", "activeForm": "Reporting results"}
]
```

- [ ] **Step 3: 验证 agent 文件完整性**

Read the full file and confirm:
- `todowrite: true` in frontmatter
- TodoWrite template has "Scan imports" and "Create mock stubs" steps
- All other content unchanged

---

### Task 5: 最终全链路验证

**Files:** All modified files

- [ ] **Step 1: 验证所有 skill/agent 中的脚本路径一致**

```bash
grep -rn 'scripts/' skills/ agents/ --include='*.md' | grep -v '<PLUGIN_ROOT>/scripts/'
```
Expected: 无结果（所有 scripts/ 引用都带 PLUGIN_ROOT 前缀）

- [ ] **Step 2: 验证 TodoWrite 约束覆盖所有工作流 skill**

```bash
grep -l 'TodoWrite' skills/java2cangjie-*/SKILL.md agents/cangjie-translate-engineer.md
```
Expected: 3 个文件（translate, fix, report skill）+ 1 个 agent

- [ ] **Step 3: 验证无引用已删除的 agent**

```bash
grep -rn 'cangjie-engineer\|error-fixer' skills/ agents/ CLAUDE.md --include='*.md'
```
Expected: 仅在 docs/ 设计文档的历史注释中出现

- [ ] **Step 4: 提交所有改动**

```bash
git add skills/ agents/ CLAUDE.md README.md hooks/session-start scripts/cjpm-build
git commit -m "fix: 加固 skill/agent 驱动链路 - TodoWrite 约束 + 路径修正 + mock 步骤补齐"
```
