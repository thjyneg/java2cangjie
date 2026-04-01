# Java to Cangjie Superpowers Plugin - Design Document

> **Version**: 3.0.0
> **Date**: 2026-03-31
> **Status**: Approved
> **Platforms**: Claude Code + OpenCode

---

## 1. Design Summary

Build a Superpowers-based plugin that translates Java projects to Cangjie language using pure AI translation with incremental dependency-driven strategy. The plugin uses a hybrid control architecture: programmatic tools enforce workflow reliability (dependency order, batch progression, compile verification), while Markdown skills guide AI translation quality.

### Core Principles

1. **Pure AI Translation** - No j2cj tool. AI reads Java, writes Cangjie, using documentation as reference.
2. **Incremental Dependency-Driven** - Parse dependency DAG, translate bottom-up in batches of 1-3 files, compile after each batch.
3. **Hybrid Control** - Plugin tools enforce deterministic workflow; skills guide creative work.
4. **Minimal Skills** - 4 skills only, each with a single clear purpose.

### Output Directory Convention

All translated Cangjie code is written to `<java_project_dir>/j2cjgenerated/`. This mirrors the original j2cj tool's output convention. The output directory contains:
- Translated `.cj` files preserving the original Java package structure
- `.java2cangjie_state.json` (plugin tool state, machine-readable)
- `TRANSLATION_REPORT.md` (final report, human-readable)

### Platform Support

| Platform | Registration | Hook Mechanism |
|----------|-------------|----------------|
| OpenCode | `.opencode/plugins/java2cangjie.js` (config + tools + system transform) | Built into plugin |
| Claude Code | `package.json` + `hooks/` | `hooks/hooks.json` + `hooks/session-start` |

---

## 2. Directory Structure

```
java2cangjie-superpowers/
├── package.json                         # npm package + plugin entry
├── .opencode/
│   ├── package.json                     # Plugin dependencies (@opencode-ai/plugin)
│   └── plugins/
│       └── java2cangjie.js              # OpenCode plugin (tools + config + bootstrap)
├── hooks/
│   ├── hooks.json                       # Claude Code hooks config
│   ├── run-hook.cmd                     # Cross-platform hook runner
│   └── session-start                    # Bootstrap injection script
├── skills/
│   ├── using-java2cangjie/
│   │   └── SKILL.md                     # Bootstrap skill
│   ├── java2cangjie-translate/
│   │   └── SKILL.md                     # Translation guidance
│   ├── java2cangjie-fix/
│   │   ├── SKILL.md                     # Error fixing workflow
│   │   └── error-patterns.md            # Common error patterns reference
│   ├── java2cangjie-report/
│   │   └── SKILL.md                     # Report generation
│   ├── cangjie-lang-features/           # Core language features
│   ├── cangjie-std/                     # Standard library quick reference
│   ├── cangjie-stdx/                    # Extended standard library
│   ├── cangjie-toolchains/              # Toolchain documentation
│   ├── cangjie-regulations/             # Coding conventions
│   └── cangjie-original-docs/           # Full original documentation fallback
├── agents/
│   ├── cangjie-engineer.md              # General Cangjie development expert
│   ├── translation-reviewer.md          # Quality reviewer (read-only)
│   └── error-fixer.md                   # Error fix executor (read-write)
├── templates/
│   └── checkpoint.md                    # Checkpoint template (for Claude Code manual checkpoints)
└── CLAUDE.md                            # Project-level instructions
```

### Removed from v1.0

| Item | Reason |
|------|--------|
| `tools/j2cj/j2cj.jar` | Pure AI translation, no j2cj tool |
| `scripts/j2cj_translate.py` | No tool invocation needed |
| `skills/java2cangjie-analyze/` | Replaced by 6 cangjie-* documentation skills |
| `skills/java2cangjie-test/` | Compile verification in translate skill + plugin tools |
| `.cursor-plugin/` | Cursor not supported |
| `hooks/hooks-cursor.json` | Cursor not supported |

### Added in v3.0

| Item | Purpose |
|------|---------|
| `skills/cangjie-lang-features/` | Core language features documentation |
| `skills/cangjie-std/` | Standard library quick reference |
| `skills/cangjie-stdx/` | Extended standard library |
| `skills/cangjie-toolchains/` | Toolchain documentation |
| `skills/cangjie-regulations/` | Coding conventions |
| `skills/cangjie-original-docs/` | Full original documentation fallback |
| `agents/cangjie-engineer.md` | General Cangjie development expert agent |
| `.opencode/package.json` | Plugin dependencies (@opencode-ai/plugin) |

---

## 3. Plugin Tools (Deterministic Control)

The OpenCode plugin registers custom tools using the official `tool` helper from `@opencode-ai/plugin`. These tools are the "hard control" layer.

### 3.1 Tool: `analyze_project`

**Purpose**: Scan Java project, build dependency DAG, return topological order.

```javascript
analyze_project: tool({
  description: 'Analyze Java project structure, build dependency graph, return translation plan',
  args: {
    javaPath: tool.schema.string().describe('Path to Java source root'),
    maxBatchSize: tool.schema.number().default(3).describe('Max files per batch (default: 3)')
  },
  async execute(args, context) {
    // 1. Scan Java files recursively
    // 2. Parse import statements
    // 3. Build internal dependency graph
    // 4. Topological sort
    // 5. Group into batches (leaf nodes first)
    // 6. Return: { totalFiles, batches: [{ id, files, dependencies }], dagSummary }
  }
})
```

**Output Example**:
```json
{
  "totalFiles": 15,
  "batches": [
    { "id": "batch-1", "files": ["Utils.java", "Constants.java"], "dependencies": [] },
    { "id": "batch-2", "files": ["Model.java"], "dependencies": ["batch-1"] },
    { "id": "batch-3", "files": ["Service.java", "Controller.java"], "dependencies": ["batch-2"] }
  ],
  "dagSummary": "Utils, Constants → Model → Service, Controller"
}
```

### 3.2 Tool: `next_batch`

**Purpose**: Return the next batch of files ready for translation.

```javascript
next_batch: tool({
  description: 'Get next batch of Java files ready for translation (all dependencies satisfied)',
  args: {},
  async execute(args, context) {
    // 1. Check which batches have completed dependencies
    // 2. Return first unstarted batch with all deps met
    // Returns: { batchId, files: [{path, size}], ready: true/false }
  }
})
```

### 3.3 Tool: `mark_complete`

**Purpose**: Mark a translation batch as successfully compiled, unlock dependents.

```javascript
mark_complete: tool({
  description: 'Mark a translation batch as complete (compilation passed)',
  args: {
    batchId: tool.schema.string().describe('Batch identifier'),
    outputFiles: tool.schema.array(tool.schema.string()).optional().describe('Generated Cangjie file paths')
  },
  async execute(args, context) {
    // 1. Update batch status to 'completed'
    // 2. Save checkpoint
    // 3. Return newly unblocked batches
  }
})
```

### 3.4 Tool: `mark_blocked`

**Purpose**: Mark a batch as blocked after failed attempts.

```javascript
mark_blocked: tool({
  description: 'Mark a translation batch as blocked (failed after max retries)',
  args: {
    batchId: tool.schema.string().describe('Batch identifier'),
    reason: tool.schema.string().describe('Error description')
  },
  async execute(args, context) {
    // 1. Update batch status to 'blocked'
    // 2. Save checkpoint
    // 3. Check if any other batches can proceed
  }
})
```

### 3.5 Tool: `translation_status`

**Purpose**: Get current translation progress and state.

```javascript
translation_status: tool({
  description: 'Get current translation progress, completed/blocked/pending counts',
  args: {},
  async execute(args, context) {
    // Returns: { total, completed, blocked, pending, currentBatch }
  }
})
```

### 3.6 State Management

All tool state is persisted to `<output_dir>/.java2cangjie_state.json`:

```json
{
  "projectPath": "/path/to/java/project",
  "totalFiles": 15,
  "batches": {
    "batch-1": { "status": "completed", "files": [...], "outputFiles": [...] },
    "batch-2": { "status": "in_progress", "files": ["Model.java"], "retries": 1 },
    "batch-3": { "status": "pending", "files": [...], "dependencies": ["batch-2"] }
  },
  "dependencyGraph": { ... }
}
```

---

## 4. Skills (AI Guidance)

### 4.1 `using-java2cangjie` (Bootstrap)

**Frontmatter**:
```yaml
---
name: using-java2cangjie
description: Use when translating Java projects or source files to Cangjie language, fixing translation errors, or configuring Java to Cangjie translation environment
---
```

**Content** (<150 lines):
- `<SUBAGENT-STOP>` tag
- Available skills list with trigger conditions (4 translation + 6 cangjie documentation)
- Available plugin tools list
- Key resource references (cangjie-* skills for documentation lookup)
- Quick start guide
- Workflow overview (new project vs. resume)

### 4.2 `java2cangjie-translate`

**Frontmatter**:
```yaml
---
name: java2cangjie-translate
description: Use when translating Java source code to Cangjie language, or when starting a new translation project
---
```

**Content** (<300 lines):

```
# Java to Cangjie Translation

## Overview
Pure AI translation with incremental dependency-driven strategy.
Output goes to <java_project>/j2cjgenerated/.

## OpenCode Environment (has plugin tools)
Use plugin tools for workflow control:
1. analyze_project() → dependency DAG + batch plan
2. next_batch() → next files to translate
3. mark_complete() / mark_blocked() → track progress

## Claude Code Environment (no plugin tools)
Manual workflow:
1. Scan Java files: find <java_dir> -name "*.java"
2. Build dependency graph: grep "^import" for internal deps
3. Topological sort manually, start with leaf nodes
4. Track progress in checkpoint file (templates/checkpoint.md)

## Translation Loop
For each batch (1-3 files):
  1. Read Java source files in current batch
  2. Lookup Cangjie documentation via skills:
     - cangjie-std → standard library types and APIs
     - cangjie-lang-features → language syntax and concepts
     - cangjie-stdx → extended library (JSON, encoding, etc.)
     - cangjie-original-docs → full documentation fallback
  3. Translate each file to Cangjie
  4. Write to <java_project>/j2cjgenerated/<package_path>/
  5. Compile: cd j2cjgenerated/<module> && cjpm build
  6. If passes: mark complete, proceed to next batch
  7. If fails (max 3 retries): mark blocked, proceed to next batch

## Translation Guidelines
- Java ArrayList<E> → std.collection.ArrayList<E>
- Java HashMap<K,V> → std.collection.HashMap<K,V>
- null → Option<T>.None or ?? operator
- instanceof → match pattern matching
- try/catch → try/except
- synchronized → std.sync.Mutex

## File Size Control
- Single file >200 lines: translate alone
- Small files: batch up to 3
- Always compile after each batch

## Context Window Management
- Read docs BEFORE translating, not during
- Focus on one file at a time within batch
- Use checkpoint/state to resume if context fills
```

### 4.3 `java2cangjie-fix`

**Frontmatter**:
```yaml
---
name: java2cangjie-fix
description: Use when fixing compilation errors in translated Cangjie code, or looking up Cangjie API documentation for error resolution
---
```

**Content** (<400 lines):

```
# Java to Cangjie Translation - Fix Errors

## Overview
Systematic error fixing following dependency-aware, one-at-a-time methodology.

## Error Analysis Process

### Step 1: Capture Errors
```bash
cd <output_dir> && cjpm build 2>&1
```

### Step 2: Categorize Errors
Group by pattern (see error-patterns.md):
- Type mismatch
- Missing import
- API difference
- Syntax error
- Generic type issue

### Step 3: Documentation Lookup (MANDATORY)
Priority order (using Cangjie skills):
1. cangjie-std → standard library types and APIs
2. cangjie-lang-features → language syntax, generics, concurrency, error handling
3. cangjie-stdx → extended library (JSON, encoding, configuration)
4. cangjie-original-docs → full original documentation fallback
5. error-patterns.md (in this skill's directory) → known error patterns

### Step 4: Fix One Error at a Time
1. Fix single error
2. Compile: cjpm build
3. Verify fix
4. If fail: git checkout -- <file>, try different approach
5. Max 3 retries per error, then report BLOCKED

## Rules
- NEVER batch multiple fixes without compiling between
- ALWAYS check documentation before guessing
- Fix dependencies before dependents
```

**`error-patterns.md`** (supplementary):
- Common Java-to-Cangjie error patterns
- Each pattern: symptom → cause → fix → doc reference
- Grows over time with real-world experience

### 4.4 `java2cangjie-report`

**Frontmatter**:
```yaml
---
name: java2cangjie-report
description: Use when generating translation reports or summarizing Java to Cangjie translation results
---
```

**Content** (<200 lines):
- Summary statistics (files, errors, fixes)
- Error breakdown by category
- Compilation status
- Quality metrics
- Recommendations
- Output as Markdown to `<output_dir>/TRANSLATION_REPORT.md`

---

## 5. Agents

### 5.1 `cangjie-engineer`

**Location**: `agents/cangjie-engineer.md`

General Cangjie development expert for writing, debugging, and building Cangjie code. Uses cangjie-* skills for documentation lookup (no web search, no memory mechanism).

**Capabilities**: Full (write: true, edit: true, bash: true)
**Use for**: Complex Cangjie code generation, debugging, and idiomatic code writing.

### 5.2 `translation-reviewer`

**Location**: `agents/translation-reviewer.md`

```yaml
---
name: translation-reviewer
description: |
  Use this agent when translated Cangjie code needs quality review
  against the original Java source.
model: inherit
---
```

**Capabilities**: Read-only (write: false, edit: false, bash: true)
**Output**: Issues categorized as Critical / Important / Suggestion

**Review checklist**:
- Correct Cangjie API usage
- Proper null handling (Option vs null)
- Import correctness
- Missing translations
- Type mapping accuracy

### 5.3 `error-fixer`

**Location**: `agents/error-fixer.md`

```yaml
---
name: error-fixer
description: |
  Use this agent when compilation errors in translated Cangjie code
  need to be fixed by looking up documentation.
model: inherit
---
```

**Capabilities**: Full (write: true, edit: true, bash: true)
**Process**: Read error → lookup docs → minimal fix → compile → verify
**Failure**: 3 attempts → report BLOCKED

---

## 6. OpenCode Plugin Implementation

### 6.0 package.json

**Root `package.json`** (plugin entry point):
```json
{
  "name": "java2cangjie-superpowers",
  "version": "3.0.0",
  "type": "module",
  "main": ".opencode/plugins/java2cangjie.js",
  "description": "Java to Cangjie translation plugin for OpenCode/Claude Code with incremental dependency-driven AI translation",
  "keywords": ["translation", "cangjie", "java", "superpowers"]
}
```

**`.opencode/package.json`** (plugin dependencies, auto-installed by OpenCode via `bun install`):
```json
{
  "dependencies": {
    "@opencode-ai/plugin": "latest"
  }
}
```

### 6.1 Plugin Structure

```javascript
// .opencode/plugins/java2cangjie.js
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { tool } from '@opencode-ai/plugin';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// State management
let projectState = null;
const STATE_FILE = '.java2cangjie_state.json';

// Frontmatter extraction
const extractAndStripFrontmatter = (content) => { ... };

// Dependency analysis (scan Java imports)
const analyzeDependencies = (javaPath, maxBatchSize) => { ... };

// State persistence
const loadState = (outputDir) => { ... };
const saveState = (outputDir, state) => { ... };

export const Java2CangjiePlugin = async ({ client, directory }) => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  const getBootstrapContent = () => {
    const skillPath = path.join(skillsDir, 'using-java2cangjie', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;
    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);
    return `<EXTREMELY_IMPORTANT>
You have the Java to Cangjie translation system.
${content}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    // Register skills directory
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into system prompt
    'experimental.chat.system.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (bootstrap) {
        (output.system ||= []).push(bootstrap);
      }
    },

    // Register workflow control tools using official tool helper
    // Uses @opencode-ai/plugin tool() for Zod schema validation
    // These are OpenCode-only. Claude Code falls back to skill-based manual workflow.
    tool: {
      analyze_project: tool({
        description: 'Analyze Java project structure, build dependency graph, return translation plan',
        args: {
          javaPath: tool.schema.string().describe('Path to Java source root'),
          maxBatchSize: tool.schema.number().default(3).describe('Max files per batch')
        },
        async execute(args, context) { ... }
      }),
      next_batch: tool({ ... }),
      mark_complete: tool({ ... }),
      mark_blocked: tool({ ... }),
      translation_status: tool({ ... })
    }
  };
};
```

### 6.2 Custom Tools Registration

OpenCode plugin tools use the official `tool` helper from `@opencode-ai/plugin`:

```javascript
import { tool } from '@opencode-ai/plugin';

// In plugin return object:
tool: {
  my_tool: tool({
    description: 'Tool description',
    args: {
      param1: tool.schema.string().describe('Parameter description'),
      param2: tool.schema.number().optional().describe('Optional parameter'),
    },
    async execute(args, context) {
      const { directory, worktree } = context;
      return { result: args.param1 };
    }
  })
}
```

Key differences from raw format:
- `tool` (singular) key in return object, not `tools` (plural)
- Each tool wrapped with `tool()` helper
- `args` with Zod schemas (`tool.schema.string()`, `tool.schema.number()`)
- `execute` receives `(args, context)` not destructured params

### 6.3 Agent Tools Format

OpenCode agents specify tool permissions in frontmatter:

```yaml
---
name: translation-reviewer
description: ...
model: inherit
tools:
  write: false
  edit: false
  bash: true
---
```

`tools` field controls which tools the agent can access. `model: inherit` means the agent uses the same model as the parent conversation.

### 6.4 Claude Code Hooks

**hooks/hooks.json**:
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|clear|compact",
      "hooks": [{
        "type": "command",
        "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
        "async": false
      }]
    }]
  }
}
```

**hooks/session-start**: Reads `using-java2cangjie/SKILL.md`, injects into system prompt (same pattern as superpowers).

**Note**: Claude Code does not support custom tools. For Claude Code, the workflow is guided purely by skills. The plugin tools are OpenCode-only.

---

## 7. Workflow

### 7.1 New Project Translation

```
User: "Translate this Java project to Cangjie"
  ↓
[System prompt contains using-java2cangjie bootstrap]
  ↓
AI recognizes translation task
  ↓
AI loads java2cangjie-translate skill
  ↓
AI calls analyze_project(javaPath) → gets DAG + batch plan
  ↓
[Translation Loop]
  AI calls next_batch() → batch-1 (leaf files)
  AI reads Java files + looks up Cangjie docs
  AI writes Cangjie files
  AI runs cjpm build
  ↓
  If pass: mark_complete("batch-1") → next_batch() → batch-2
  If fail: load java2cangjie-fix → fix → retry → mark_complete or mark_blocked
  ↓
  [Repeat until all batches processed]
  ↓
AI loads java2cangjie-report → generates TRANSLATION_REPORT.md
```

### 7.2 Resume Interrupted Translation

```
1. AI calls translation_status() → sees partial progress
2. AI calls next_batch() → gets next unstarted batch
3. Continue from translation loop
```

### 7.3 Claude Code Fallback (No Custom Tools)

On Claude Code (no plugin tools), the skill instructions include the same logic but as guidelines:
- Skill instructs AI to manually build dependency graph using grep
- Skill instructs AI to track progress using checkpoint files
- Less guaranteed but functionally equivalent

---

## 8. Implementation Roadmap

### Phase 0: POC Verification (0.5 day)

- [ ] Create `package.json`
- [ ] Create `.opencode/plugins/java2cangjie.js` (minimal: config + bootstrap, no tools yet)
- [ ] Create `skills/using-java2cangjie/SKILL.md` (bootstrap)
- [ ] Create `hooks/` (hooks.json, run-hook.cmd, session-start)
- **Verify**: OpenCode lists skills, system prompt contains bootstrap

### Phase 1: Core Skills + Plugin Tools (2 days)

- [ ] Add plugin tools (analyze_project, next_batch, mark_complete, mark_blocked, translation_status)
- [ ] Write `skills/java2cangjie-translate/SKILL.md`
- [ ] Write `skills/java2cangjie-fix/SKILL.md` + `error-patterns.md`
- [ ] Write `skills/java2cangjie-report/SKILL.md`
- **Verify**: Small Java project (5-10 files) end-to-end translation

### Phase 2: Agents + Integration (1 day)

- [ ] Write `agents/translation-reviewer.md`
- [ ] Write `agents/error-fixer.md`
- [ ] Test with superpowers workflow integration
- **Verify**: Full workflow with agent delegation

### Phase 3: Cleanup + Documentation (0.5 day)

- [x] Delete old skills (analyze, test)
- [x] Delete `tools/j2cj/`, `scripts/`
- [x] Add 6 cangjie-* documentation skills (replacing java2cangjie-analyze/docs/)
- [x] Add cangjie-engineer agent
- [x] Update CLAUDE.md
- [x] Write README.md
- [x] Fix plugin tool format to use official `tool` helper from `@opencode-ai/plugin`
- [x] Fix local plugin installation (auto-load from `.opencode/plugins/`)
- **Verify**: Clean install in fresh environment

**Total: 4 days**

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Plugin tools not supported on Claude Code | Skills include manual fallback instructions |
| AI ignores batch size limits | Plugin tools enforce batch boundaries |
| Dependency analysis misses imports | Combine import scanning + package structure heuristics |
| Large files exceed context window | Single-file batches for >200 line files |
| Translation quality varies | translation-reviewer agent provides QA |
| Checkpoint corruption | State persisted as JSON, auto-recoverable |
