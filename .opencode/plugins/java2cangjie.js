/**
 * Java2Cangjie plugin for OpenCode.ai
 *
 * Follows the superpowers plugin pattern for skills + bootstrap,
 * plus registers custom translation workflow tools via @opencode-ai/plugin.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import { tool } from '@opencode-ai/plugin';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ============================================================
// Helper
// ============================================================

const result = (data) => JSON.stringify(data, null, 2);

// ============================================================
// Frontmatter parser
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
// Dependency analysis engine
// ============================================================

const analyzeJavaDependencies = (javaRoot, maxBatchSize = 3) => {
  const javaRoots = Array.isArray(javaRoot) ? javaRoot : [javaRoot];
  const javaFiles = [];
  const fileMap = new Map();
  const packageToClasses = new Map();

  const scanDir = (dir, pkg = '') => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scanDir(fullPath, pkg ? `${pkg}.${entry.name}` : entry.name);
      } else if (entry.name.endsWith('.java')) {
        const className = entry.name.replace('.java', '');
        javaFiles.push({ path: fullPath, className, deps: [] });
        fileMap.set(className, { path: fullPath, packageName: '' });
      }
    }
  };

  for (const root of javaRoots) {
    if (!fs.existsSync(root)) continue;
    scanDir(root);
  }

  if (javaFiles.length === 0) {
    return { error: `No Java files found in: ${javaRoots.join(', ')}` };
  }

  for (const file of javaFiles) {
    const content = fs.readFileSync(file.path, 'utf8');
    const pkgMatch = content.match(/^package\s+([\w.]+)\s*;/m);
    if (pkgMatch) {
      const pkg = pkgMatch[1];
      fileMap.get(file.className).packageName = pkg;
      if (!packageToClasses.has(pkg)) packageToClasses.set(pkg, []);
      packageToClasses.get(pkg).push(file.className);
    }
  }

  for (const file of javaFiles) {
    const content = fs.readFileSync(file.path, 'utf8');
    const normalized = content.replace(/\r\n/g, '\n');
    const depSet = new Set();
    const info = fileMap.get(file.className);

    const regularImports = normalized.match(/^import\s+(?!static\b)([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of regularImports) {
      const imported = imp.replace(/^import\s+/, '').replace(/\s*;$/, '').trim();
      if (imported.endsWith('.*')) {
        const pkg = imported.slice(0, -2);
        for (const cls of (packageToClasses.get(pkg) || [])) {
          if (cls !== file.className) depSet.add(cls);
        }
      } else {
        const importedClass = imported.split('.').pop();
        if (fileMap.has(importedClass) && importedClass !== file.className) depSet.add(importedClass);
      }
    }

    const staticImports = normalized.match(/^import\s+static\s+([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of staticImports) {
      const imported = imp.replace(/^import\s+static\s+/, '').replace(/\s*;$/, '').trim();
      const parts = imported.split('.');
      const className = imported.endsWith('.*')
        ? (parts.length >= 2 ? parts[parts.length - 2] : null)
        : (parts.length >= 2 ? parts[parts.length - 2] : null);
      if (className && fileMap.has(className) && className !== file.className) depSet.add(className);
    }

    if (info.packageName && packageToClasses.has(info.packageName)) {
      for (const cls of packageToClasses.get(info.packageName)) {
        if (cls !== file.className) {
          const regex = new RegExp('\\b' + cls.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b');
          if (regex.test(content)) depSet.add(cls);
        }
      }
    }

    file.deps = [...depSet];
  }

  const inDegree = new Map();
  const adjList = new Map();
  for (const file of javaFiles) {
    inDegree.set(file.className, 0);
    adjList.set(file.className, []);
  }
  for (const file of javaFiles) {
    for (const dep of file.deps) {
      if (adjList.has(dep)) {
        adjList.get(dep).push(file.className);
        inDegree.set(file.className, inDegree.get(file.className) + 1);
      }
    }
  }

  const sorted = [];
  const queue = [];
  for (const [cls, deg] of inDegree) {
    if (deg === 0) queue.push(cls);
  }
  while (queue.length > 0) {
    const cls = queue.shift();
    sorted.push(cls);
    for (const neighbor of adjList.get(cls)) {
      inDegree.set(neighbor, inDegree.get(neighbor) - 1);
      if (inDegree.get(neighbor) === 0) queue.push(neighbor);
    }
  }

  if (sorted.length < javaFiles.length) {
    const sortedSet = new Set(sorted);
    const remaining = javaFiles
      .filter(f => !sortedSet.has(f.className))
      .sort((a, b) => (inDegree.get(a.className) || 0) - (inDegree.get(b.className) || 0));
    for (const file of remaining) sorted.push(file.className);
  }

  const batches = [];
  const remainingList = [...sorted];
  while (remainingList.length > 0) {
    const batch = remainingList.splice(0, maxBatchSize);
    const batchId = `batch-${batches.length + 1}`;
    const batchDeps = [];
    for (const cls of batch) {
      const file = javaFiles.find(f => f.className === cls);
      for (const dep of file.deps) {
        const depBatchIdx = batches.findIndex(b => b.files.includes(dep));
        if (depBatchIdx >= 0 && !batchDeps.includes(`batch-${depBatchIdx + 1}`)) batchDeps.push(`batch-${depBatchIdx + 1}`);
      }
    }
    batches.push({
      id: batchId,
      files: batch.map(cls => {
        const file = javaFiles.find(f => f.className === cls);
        const stats = fs.statSync(file.path);
        return { className: cls, path: file.path, size: stats.size, lines: 0 };
      }),
      dependencies: batchDeps,
      status: 'pending'
    });
  }

  for (const batch of batches) {
    for (const file of batch.files) {
      file.lines = fs.readFileSync(file.path, 'utf8').split('\n').length;
    }
  }

  return { totalFiles: javaFiles.length, batches, dagSummary: batches.map(b => b.files.map(f => f.className).join(', ')).join(' → ') };
};

// ============================================================
// State management
// ============================================================

const STATE_FILE = '.java2cangjie_state.json';
let currentState = null;

const saveState = (outputDir) => {
  if (!currentState) return;
  const statePath = path.join(outputDir, STATE_FILE);
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
  fs.writeFileSync(statePath, JSON.stringify(currentState, null, 2));
};

// ============================================================
// Plugin export
// ============================================================

export const Java2CangjiePlugin = async ({ client, directory }) => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  const getBootstrapContent = () => {
    const skillPath = path.join(skillsDir, 'using-java2cangjie', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;
    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);
    const toolMapping = `**Tool Mapping for OpenCode:**
- \`TodoWrite\` → \`todowrite\`
- \`Skill\` tool → OpenCode's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → Your native tools
- Plugin tools: \`analyze_project\`, \`next_batch\`, \`compile_batch\`, \`mark_complete\`, \`mark_blocked\`, \`translation_status\`

**MANDATORY Batch Workflow (enforced by tools):**
1. \`analyze_project()\` → build dependency DAG + batches
2. \`next_batch()\` → get next ready batch (BLOCKS if another is in_progress)
3. Translate Java → Cangjie files
4. \`compile_batch(batchId)\` → run \`cjpm build\`, auto-complete on success, return errors on failure
5. If compile fails → fix errors → \`compile_batch(batchId)\` again (max 3 retries, then auto-blocked)
6. Only after compile succeeds can you call \`next_batch()\` for the next batch
7. Repeat until all batches done → generate report

**NEVER:** skip compile_batch, call next_batch while a batch is in_progress, or use mark_complete without compiling.`;

    return `<EXTREMELY_IMPORTANT>
You have the Java to Cangjie translation system.

**IMPORTANT: The using-java2cangjie skill content is included below. It is ALREADY LOADED - do NOT use the skill tool to load it again.**

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    // Register skills directory — same pattern as superpowers
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into first user message — same pattern as superpowers
    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages?.length) return;
      const firstUser = output.messages.find(m => m.info?.role === 'user');
      if (!firstUser || !firstUser.parts?.length) return;
      if (firstUser.parts.some(p => p.type === 'text' && p.text?.includes('EXTREMELY_IMPORTANT'))) return;
      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: 'text', text: bootstrap });
    },

    // Custom tools — uses static import matching OpenCode official docs
    tool: {
      analyze_project: tool({
        description: 'Analyze Java project structure, build dependency graph, return translation batch plan',
        args: {
          javaPath: tool.schema.string().describe('Path(s) to Java source root. Comma-separated for multiple paths.'),
          maxBatchSize: tool.schema.number().optional().describe('Max files per batch (default: 3)'),
          outputDir: tool.schema.string().optional().describe('Output directory (default: <javaPath>/../j2cjgenerated/)'),
        },
        async execute(args, context) {
          try {
            const javaPath = args.javaPath.includes(',')
              ? args.javaPath.split(',').map(p => p.trim())
              : args.javaPath;
            const maxBatchSize = args.maxBatchSize || 3;
            const outDir = args.outputDir || path.join(path.dirname(typeof javaPath === 'string' ? javaPath : javaPath[0]), 'j2cjgenerated');
            const analysis = analyzeJavaDependencies(javaPath, maxBatchSize);
            if (analysis.error) return result({ error: analysis.error });

            currentState = {
              projectPath: javaPath,
              outputDir: outDir,
              totalFiles: analysis.totalFiles,
              batches: {},
              dagSummary: analysis.dagSummary || '',
              createdAt: new Date().toISOString()
            };
            for (const batch of analysis.batches) {
              currentState.batches[batch.id] = {
                status: 'pending',
                files: batch.files,
                dependencies: batch.dependencies,
                retries: 0
              };
            }
            saveState(outDir);

            return result({
              totalFiles: analysis.totalFiles || 0,
              totalBatches: analysis.batches.length || 0,
              batches: analysis.batches.map(b => ({
                id: b.id, fileCount: b.files.length,
                files: b.files.map(f => f.className),
                dependencies: b.dependencies || []
              })),
              dagSummary: analysis.dagSummary || '',
              outputDir: outDir
            });
          } catch (e) {
            return result({ error: `analyze_project failed: ${e.message}` });
          }
        }
      }),

      next_batch: tool({
        description: 'Get next batch of Java files ready for translation. BLOCKS if a batch is in_progress.',
        args: {},
        async execute(args, context) {
          try {
            if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });
            const inProgress = Object.entries(currentState.batches).find(([, b]) => b.status === 'in_progress');
            if (inProgress) {
              return result({
                ready: false, blocked: true,
                message: `BLOCKED: Batch ${inProgress[0]} is still in_progress. Call compile_batch("${inProgress[0]}") first.`,
                currentBatch: inProgress[0], retries: inProgress[1].retries || 0
              });
            }
            for (const [batchId, batch] of Object.entries(currentState.batches)) {
              if (batch.status !== 'pending') continue;
              if ((batch.dependencies || []).every(depId => currentState.batches[depId]?.status === 'completed')) {
                batch.status = 'in_progress';
                batch.startedAt = new Date().toISOString();
                saveState(currentState.outputDir);
                return result({ batchId, files: batch.files || [], ready: true });
              }
            }
            const batches = Object.values(currentState.batches);
            return result({
              ready: false,
              message: 'No batches available.',
              progress: {
                completed: batches.filter(b => b.status === 'completed').length,
                blocked: batches.filter(b => b.status === 'blocked').length,
                pending: batches.filter(b => b.status === 'pending').length
              }
            });
          } catch (e) {
            return result({ error: `next_batch failed: ${e.message}` });
          }
        }
      }),

      compile_batch: tool({
        description: 'Compile with cjpm build. Auto-completes on success, returns errors on failure. After 3 failures auto-blocks.',
        args: {
          batchId: tool.schema.string().describe('Batch identifier to compile'),
          outputFiles: tool.schema.string().optional().describe('Comma-separated list of generated Cangjie file paths'),
        },
        async execute(args, context) {
          try {
            const { batchId } = args;
            if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });
            const batch = currentState.batches[batchId];
            if (!batch) return result({ error: `Batch ${batchId} not found.` });
            if (batch.status !== 'in_progress') return result({ error: `Batch ${batchId} is '${batch.status}', not 'in_progress'.` });

            const outputDir = currentState.outputDir;
            let moduleDir = null;
            const findCjpmToml = (dir, depth) => {
              if (depth > 3) return null;
              try {
                const entries = fs.readdirSync(dir, { withFileTypes: true });
                for (const e of entries) if (e.name === 'cjpm.toml') return dir;
                for (const e of entries) if (e.isDirectory()) { const f = findCjpmToml(path.join(dir, e.name), depth + 1); if (f) return f; }
              } catch (_) {}
              return null;
            };
            moduleDir = findCjpmToml(outputDir, 0);
            if (!moduleDir) {
              batch.retries = (batch.retries || 0) + 1;
              saveState(currentState.outputDir);
              return result({ batchId, compiled: false, status: 'in_progress', retries: batch.retries, retriesLeft: 3 - batch.retries, error: `No cjpm.toml found under ${outputDir}.` });
            }

            // Ensure placeholder .cj files
            const ensurePlaceholders = (currentPath) => {
              try {
                const entries = fs.readdirSync(currentPath, { withFileTypes: true });
                if (!entries.some(e => e.isFile() && e.name.endsWith('.cj')) && entries.some(e => e.isDirectory() && e.name !== 'target' && e.name !== '.cached')) {
                  const p = path.join(currentPath, '_pkg.cj');
                  if (!fs.existsSync(p)) fs.writeFileSync(p, '// placeholder\n');
                }
                for (const e of entries) if (e.isDirectory() && e.name !== 'target' && e.name !== '.cached') ensurePlaceholders(path.join(currentPath, e.name));
              } catch (_) {}
            };
            ensurePlaceholders(path.join(moduleDir, 'src'));

            const MAX_RETRIES = 3;
            let compileOutput = '', compileSuccess = false, timedOut = false;
            try {
              compileOutput = execSync('cjpm build 2>&1', { cwd: moduleDir, encoding: 'utf8', timeout: 300000, maxBuffer: 10 * 1024 * 1024, shell: true, stdio: ['pipe', 'pipe', 'pipe'] });
              compileSuccess = true;
            } catch (e) {
              timedOut = e.killed || /ETIMEDOUT|timed?\s*out/i.test(e.message);
              compileOutput = e.stdout || e.stderr || e.message || String(e);
            }

            if (compileSuccess) {
              batch.status = 'completed';
              batch.outputFiles = args.outputFiles ? args.outputFiles.split(',').map(s => s.trim()) : [];
              batch.completedAt = new Date().toISOString();
              saveState(currentState.outputDir);
              const done = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
              const total = Object.keys(currentState.batches).length;
              return result({ batchId, compiled: true, status: 'completed', progress: `${done}/${total} batches done`, allComplete: done === total, output: compileOutput.trim() });
            }

            batch.retries = (batch.retries || 0) + 1;
            if (timedOut) { batch.retries--; saveState(currentState.outputDir); return result({ batchId, compiled: false, status: 'in_progress', error: 'cjpm build timed out (300s).' }); }
            if (batch.retries >= MAX_RETRIES) {
              batch.status = 'blocked'; batch.blockReason = `Failed after ${MAX_RETRIES} attempts.\n${compileOutput.trim().slice(0, 2000)}`;
              batch.blockedAt = new Date().toISOString(); saveState(currentState.outputDir);
              return result({ batchId, compiled: false, status: 'blocked', retries: batch.retries, error: compileOutput.trim(), message: `BLOCKED after ${MAX_RETRIES} failures.` });
            }
            saveState(currentState.outputDir);
            return result({ batchId, compiled: false, status: 'in_progress', retries: batch.retries, retriesLeft: MAX_RETRIES - batch.retries, error: compileOutput.trim(), message: `Attempt ${batch.retries}/${MAX_RETRIES}. Fix and retry compile_batch("${batchId}").` });
          } catch (e) {
            return result({ error: `compile_batch failed: ${e.message}` });
          }
        }
      }),

      mark_complete: tool({
        description: 'Manual override: mark batch completed. Prefer compile_batch() instead.',
        args: {
          batchId: tool.schema.string().describe('Batch identifier'),
          outputFiles: tool.schema.string().optional().describe('Comma-separated generated file paths'),
        },
        async execute(args, context) {
          try {
            const { batchId } = args;
            if (!currentState || !currentState.batches[batchId]) return result({ error: `Batch ${batchId} not found` });
            currentState.batches[batchId].status = 'completed';
            currentState.batches[batchId].outputFiles = args.outputFiles ? args.outputFiles.split(',').map(s => s.trim()) : [];
            currentState.batches[batchId].completedAt = new Date().toISOString();
            saveState(currentState.outputDir);
            const done = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
            return result({ batchId, status: 'completed', progress: `${done}/${currentState.totalFiles} files done`, allComplete: done === Object.keys(currentState.batches).length });
          } catch (e) {
            return result({ error: `mark_complete failed: ${e.message}` });
          }
        }
      }),

      mark_blocked: tool({
        description: 'Mark a batch as blocked (failed after max retries)',
        args: {
          batchId: tool.schema.string().describe('Batch identifier'),
          reason: tool.schema.string().describe('Error description'),
        },
        async execute(args, context) {
          try {
            const { batchId, reason } = args;
            if (!currentState || !currentState.batches[batchId]) return result({ error: `Batch ${batchId} not found` });
            currentState.batches[batchId].status = 'blocked';
            currentState.batches[batchId].blockReason = reason;
            currentState.batches[batchId].blockedAt = new Date().toISOString();
            saveState(currentState.outputDir);
            const available = Object.entries(currentState.batches).filter(([, b]) => b.status === 'pending' && (b.dependencies || []).every(d => currentState.batches[d]?.status === 'completed'));
            return result({ batchId, status: 'blocked', reason, canProceed: available.length > 0, availableBatches: available.map(([id]) => id) });
          } catch (e) {
            return result({ error: `mark_blocked failed: ${e.message}` });
          }
        }
      }),

      translation_status: tool({
        description: 'Get current translation progress',
        args: {},
        async execute(args, context) {
          try {
            if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });
            const batches = Object.values(currentState.batches);
            return result({
              projectPath: currentState.projectPath, outputDir: currentState.outputDir,
              totalFiles: currentState.totalFiles || 0, totalBatches: batches.length,
              completed: batches.filter(b => b.status === 'completed').length,
              inProgress: batches.filter(b => b.status === 'in_progress').length,
              blocked: batches.filter(b => b.status === 'blocked').length,
              pending: batches.filter(b => b.status === 'pending').length,
            });
          } catch (e) {
            return result({ error: `translation_status failed: ${e.message}` });
          }
        }
      })
    }
  };
};
