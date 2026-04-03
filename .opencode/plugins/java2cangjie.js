/**
 * Java2Cangjie plugin for OpenCode.ai
 *
 * Exact superpowers pattern — zero external dependencies:
 * - Config hook: auto-registers skills directory
 * - Message transform: injects bootstrap context into first user message
 *
 * No custom tools — all workflow operations use native tools (Bash, Read, Write, Edit).
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ============================================================
// Frontmatter parser (same as superpowers — no dependencies)
// ============================================================

const extractAndStripFrontmatter = (content) => {
  const normalized = content.replace(/\r\n/g, '\n');
  const match = normalized.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content: normalized };
  const frontmatterStr = match[1];
  const body = match[2];
  const frontmatter = {};
  for (const line of frontmatterStr.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      frontmatter[key] = value;
    }
  }
  return { frontmatter, content: body };
};

// ============================================================
// Plugin export — superpowers pattern exactly
// ============================================================

export const Java2CangjiePlugin = async ({ client, directory }) => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  const getBootstrapContent = () => {
    const skillPath = path.join(skillsDir, 'using-java2cangjie', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;
    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);

    const toolMapping = `**Tool Mapping for OpenCode:**
When skills reference tools you don't have, substitute OpenCode equivalents:
- \`TodoWrite\` → \`todowrite\`
- \`Skill\` tool → OpenCode's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → Your native tools

**Translation Workflow using native tools:**
1. **Analyze**: Run \`python scripts/analyze_deps.py <javaPath> [--max-batch-size N]\` via Bash to build dependency DAG and generate batch plan
2. **Next batch**: Read \`.java2cangjie_state.json\` from the output directory, find the first batch with status "pending" whose dependencies are all "completed"
3. **Translate**: Read Java files, write Cangjie files using Read/Write/Edit tools
4. **Compile**: Run \`cd <outputDir>/<module> && cjpm build 2>&1\` via Bash
5. **On success**: Edit \`.java2cangjie_state.json\` to mark batch as "completed"
6. **On failure**: Fix errors and retry compile (max 3 times). After 3 failures, mark batch as "blocked" with reason
7. **Repeat** from step 2 until all batches done, then generate report

**State file**: \`<outputDir>/.java2cangjie_state.json\` — edit with Write/Edit tool to track progress.

**NEVER:** skip compilation, advance to next batch while one is in_progress, or mark complete without compiling first.`;

    return `<EXTREMELY_IMPORTANT>
You have the Java to Cangjie translation system.

**IMPORTANT: The using-java2cangjie skill content is included below. It is ALREADY LOADED - do NOT use the skill tool to load it again.**

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    // Register skills directory so OpenCode auto-discovers all SKILL.md files
    // (same mechanism as superpowers — modifies live config singleton)
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into the first user message of each session.
    // Using user message avoids token bloat from repeated system messages.
    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages?.length) return;
      const firstUser = output.messages.find(m => m.info?.role === 'user');
      if (!firstUser || !firstUser.parts?.length) return;
      // Only inject once
      if (firstUser.parts.some(p => p.type === 'text' && p.text?.includes('EXTREMELY_IMPORTANT'))) return;
      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: 'text', text: bootstrap });
    }
  };
};
