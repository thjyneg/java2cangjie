---
name: java2cangjie-report
description: "Use when generating translation reports, summarizing Java to Cangjie translation results, documenting translation outcomes, or when translation is complete and a summary is needed. Trigger on 'generate translation report', 'translation summary', 'show translation results', or when all batches are done"
---

# Java to Cangjie Translation - Report

## Overview

Generate a comprehensive translation report after all translation and fixing is complete.

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

## Report Sections

Generate the following sections in order:

### 1. Executive Summary

```markdown
# Java to Cangjie Translation Report

## Summary
- **Project**: <project_name>
- **Date**: <date>
- **Status**: Complete / Partially Complete
- **Total Java files**: <count>
- **Total Cangjie files**: <count>
- **Compilation**: Pass / Fail
```

### 2. Translation Statistics

Collect via commands:
```bash
# Count source files
find <java_source> -name "*.java" | wc -l
# Count output files
find <output_dir> -name "*.cj" | wc -l
# Count lines
find <output_dir> -name "*.cj" -exec wc -l {} +
```

Report:
- Total files translated
- Lines of code (input vs output)
- Translation rate (files successfully translated / total)

### 3. Error Breakdown

Read from state file:
```bash
cat <output_dir>/.java2cangjie_state.json
```

Report:
- Total errors encountered
- Errors fixed successfully
- Errors remaining (if any)
- Error categories with counts

### 4. Compilation Status

```bash
python <PLUGIN_ROOT>/scripts/cjpm-build <output_dir>/<module>
echo "Exit code: $?"
```

Report:
- Final compilation result
- Modules compiled successfully
- Modules with errors (if any)

### 5. Batch Progress

From state file, report:
- Completed batches
- Blocked batches (with reasons)
- Pending batches (if any)

### 6. Recommendations

Based on results, suggest:
- Manual review areas (if quality concerns)
- Additional testing needs
- Known limitations or adapter code needed
- Next steps for integration

## Output

Save report as `<output_dir>/TRANSLATION_REPORT.md`.

## Template

```markdown
# Java to Cangjie Translation Report

## Executive Summary
- **Project**: <name>
- **Date**: <date>
- **Translation Status**: <status>
- **Compilation Status**: <pass/fail>

## Statistics
| Metric | Value |
|--------|-------|
| Java files | <count> |
| Cangjie files | <count> |
| Total batches | <count> |
| Completed batches | <count> |
| Blocked batches | <count> |
| Total errors fixed | <count> |

## Error Analysis
| Category | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| Missing import | <n> | <n> | <n> |
| Type mismatch | <n> | <n> | <n> |
| API difference | <n> | <n> | <n> |
| Syntax error | <n> | <n> | <n> |

## Compilation
- **Status**: <pass/fail>
- **Modules**: <count> total, <count> successful

## Recommendations
1. <recommendation>
2. <recommendation>
```
