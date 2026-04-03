/**
 * Java2Cangjie plugin for OpenCode.ai
 *
 * Follows the superpowers plugin pattern:
 * - Config hook: auto-registers skills directory (no symlinks needed)
 * - Message transform: injects bootstrap context into first user message
 * - Custom tools: registered via dynamic import of @opencode-ai/plugin
 *
 * Zero static external dependencies — core functionality (skills, bootstrap)
 * uses only Node.js built-ins, so it never crashes on missing packages.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ============================================================
// Helper: ensure tool execute returns string (required by OpenCode)
// ============================================================

const result = (data) => JSON.stringify(data, null, 2);

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

  // First pass: detect package for each class
  for (const file of javaFiles) {
    const content = fs.readFileSync(file.path, 'utf8');
    const pkgMatch = content.match(/^package\s+([\w.]+)\s*;/m);
    if (pkgMatch) {
      const pkg = pkgMatch[1];
      fileMap.get(file.className).packageName = pkg;
      if (!packageToClasses.has(pkg)) {
        packageToClasses.set(pkg, []);
      }
      packageToClasses.get(pkg).push(file.className);
    }
  }

  // Second pass: build dependency graph
  for (const file of javaFiles) {
    const content = fs.readFileSync(file.path, 'utf8');
    const normalized = content.replace(/\r\n/g, '\n');
    const depSet = new Set();
    const info = fileMap.get(file.className);

    // 1. Parse regular imports
    const regularImports = normalized.match(/^import\s+(?!static\b)([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of regularImports) {
      const imported = imp.replace(/^import\s+/, '').replace(/\s*;$/, '').trim();
      if (imported.endsWith('.*')) {
        const pkg = imported.slice(0, -2);
        const classes = packageToClasses.get(pkg) || [];
        for (const cls of classes) {
          if (cls !== file.className) depSet.add(cls);
        }
      } else {
        const importedClass = imported.split('.').pop();
        if (fileMap.has(importedClass) && importedClass !== file.className) {
          depSet.add(importedClass);
        }
      }
    }

    // 2. Parse static imports
    const staticImports = normalized.match(/^import\s+static\s+([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of staticImports) {
      const imported = imp.replace(/^import\s+static\s+/, '').replace(/\s*;$/, '').trim();
      const parts = imported.split('.');
      if (imported.endsWith('.*')) {
        const className = parts.length >= 2 ? parts[parts.length - 2] : null;
        if (className && fileMap.has(className) && className !== file.className) {
          depSet.add(className);
        }
      } else {
        const className = parts.length >= 2 ? parts[parts.length - 2] : null;
        if (className && fileMap.has(className) && className !== file.className) {
          depSet.add(className);
        }
      }
    }

    // 3. Detect same-package implicit dependencies
    if (info.packageName && packageToClasses.has(info.packageName)) {
      const samePkgClasses = packageToClasses.get(info.packageName);
      for (const cls of samePkgClasses) {
        if (cls !== file.className) {
          const regex = new RegExp('\\b' + cls.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b');
          if (regex.test(content)) {
            depSet.add(cls);
          }
        }
      }
    }

    file.deps = [...depSet];
  }

  // Topological sort (Kahn's algorithm) with cycle handling
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
    for (const file of remaining) {
      sorted.push(file.className);
    }
  }

  // Group into batches
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
        if (depBatchIdx >= 0 && !batchDeps.includes(`batch-${depBatchIdx + 1}`)) {
          batchDeps.push(`batch-${depBatchIdx + 1}`);
        }
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
      const content = fs.readFileSync(file.path, 'utf8');
      file.lines = content.split('\n').length;
    }
  }

  const dagSummary = batches.map(b => b.files.map(f => f.className).join(', ')).join(' → ');

  return {
    totalFiles: javaFiles.length,
    batches,
    dagSummary
  };
};

// ============================================================
// State management
// ============================================================

const STATE_FILE = '.java2cangjie_state.json';
let currentState = null;

const loadState = (outputDir) => {
  const statePath = path.join(outputDir, STATE_FILE);
  if (fs.existsSync(statePath)) {
    currentState = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  }
  return currentState;
};

const saveState = (outputDir) => {
  if (!currentState) return;
  const statePath = path.join(outputDir, STATE_FILE);
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
  fs.writeFileSync(statePath, JSON.stringify(currentState, null, 2));
};

// ============================================================
// Tool definitions (factory — called only if @opencode-ai/plugin available)
// ============================================================

const createTools = (tool) => ({
  analyze_project: tool({
    description: 'Analyze Java project structure, build dependency graph, return translation batch plan',
    args: {
      javaPath: tool.schema.string().describe('Path(s) to Java source root directory(ies). Use comma-separated for multiple paths.'),
      maxBatchSize: tool.schema.number().describe('Max files per batch (default: 3)'),
      outputDir: tool.schema.string().optional().describe('Output directory for translated files (default: <javaPath>/../j2cjgenerated/)'),
    },
    async execute(args, context) {
      try {
        // Support comma-separated multiple paths
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
            id: b.id,
            fileCount: b.files.length,
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
    description: 'Get next batch of Java files ready for translation. BLOCKS if a batch is currently in_progress — you must compile_batch() first.',
    args: {},
    async execute(args, context) {
      try {
        if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });

        const inProgress = Object.entries(currentState.batches).find(
          ([id, b]) => b.status === 'in_progress'
        );
        if (inProgress) {
          return result({
            ready: false,
            blocked: true,
            message: `BLOCKED: Batch ${inProgress[0]} is still in_progress. You MUST call compile_batch("${inProgress[0]}") first.`,
            currentBatch: inProgress[0],
            retries: inProgress[1].retries || 0
          });
        }

        for (const [batchId, batch] of Object.entries(currentState.batches)) {
          if (batch.status !== 'pending') continue;
          const allDepsComplete = (batch.dependencies || []).every(
            depId => currentState.batches[depId]?.status === 'completed'
          );
          if (allDepsComplete) {
            batch.status = 'in_progress';
            batch.startedAt = new Date().toISOString();
            saveState(currentState.outputDir);
            return result({
              batchId,
              files: batch.files || [],
              ready: true
            });
          }
        }
        const completed = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
        const blocked = Object.values(currentState.batches).filter(b => b.status === 'blocked').length;
        const pending = Object.values(currentState.batches).filter(b => b.status === 'pending').length;
        return result({
          ready: false,
          message: 'No batches available. All dependencies must be completed first.',
          progress: { completed, blocked, pending }
        });
      } catch (e) {
        return result({ error: `next_batch failed: ${e.message}` });
      }
    }
  }),

  compile_batch: tool({
    description: 'Compile the output project with cjpm build. On success, auto-marks batch as completed. On failure, returns errors. After 3 failures, auto-blocks the batch.',
    args: {
      batchId: tool.schema.string().describe('Batch identifier to compile'),
      outputFiles: tool.schema.array(tool.schema.string()).optional().describe('Generated Cangjie file paths from this batch'),
    },
    async execute(args, context) {
      try {
        const { batchId } = args;
        const outputFiles = args.outputFiles || [];
        if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });
        const batch = currentState.batches[batchId];
        if (!batch) return result({ error: `Batch ${batchId} not found.` });
        if (batch.status !== 'in_progress') {
          return result({ error: `Batch ${batchId} status is '${batch.status}', not 'in_progress'. Call next_batch() first.` });
        }

        const outputDir = currentState.outputDir;
        let moduleDir = null;

        const findCjpmToml = (dir, depth) => {
          if (depth > 3) return null;
          try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
              if (entry.name === 'cjpm.toml') return dir;
            }
            for (const entry of entries) {
              if (entry.isDirectory()) {
                const found = findCjpmToml(path.join(dir, entry.name), depth + 1);
                if (found) return found;
              }
            }
          } catch (_) {}
          return null;
        };

        moduleDir = findCjpmToml(outputDir, 0);

        if (!moduleDir) {
          batch.retries = (batch.retries || 0) + 1;
          saveState(currentState.outputDir);
          return result({
            batchId,
            compiled: false,
            status: 'in_progress',
            retries: batch.retries,
            retriesLeft: 3 - batch.retries,
            error: `No cjpm.toml found under ${outputDir}.`,
            message: `No cjpm.toml found. Create the Cangjie project structure first.`
          });
        }

        // Ensure placeholder .cj files for cjpm directory scanning
        const ensurePlaceholders = (baseDir, currentPath) => {
          try {
            const entries = fs.readdirSync(currentPath, { withFileTypes: true });
            const hasCjFile = entries.some(e => e.isFile() && e.name.endsWith('.cj'));
            const subdirs = entries.filter(e => e.isDirectory() && e.name !== 'target' && e.name !== '.cached');
            if (!hasCjFile && subdirs.length > 0) {
              const placeholderPath = path.join(currentPath, '_pkg.cj');
              if (!fs.existsSync(placeholderPath)) {
                fs.writeFileSync(placeholderPath, '// placeholder for cjpm directory scanning\n');
              }
            }
            for (const sub of subdirs) {
              ensurePlaceholders(baseDir, path.join(currentPath, sub.name));
            }
          } catch (_) {}
        };
        ensurePlaceholders(moduleDir, path.join(moduleDir, 'src'));

        // Run cjpm build
        const MAX_RETRIES = 3;
        let compileOutput = '';
        let compileSuccess = false;
        let timedOut = false;

        try {
          compileOutput = execSync('cjpm build 2>&1', {
            cwd: moduleDir,
            encoding: 'utf8',
            timeout: 300000,
            maxBuffer: 10 * 1024 * 1024,
            shell: true,
            stdio: ['pipe', 'pipe', 'pipe']
          });
          compileSuccess = true;
        } catch (e) {
          timedOut = e.killed || (e.message && (e.message.includes('ETIMEDOUT') || e.message.includes('timed out')));
          compileOutput = e.stdout || e.stderr || e.message || String(e);
          compileSuccess = false;
        }

        if (compileSuccess) {
          batch.status = 'completed';
          batch.outputFiles = outputFiles;
          batch.completedAt = new Date().toISOString();
          batch.compileOutput = compileOutput.trim();
          saveState(currentState.outputDir);

          const completed = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
          const total = Object.keys(currentState.batches).length;
          return result({
            batchId,
            compiled: true,
            status: 'completed',
            progress: `${completed}/${total} batches done (${currentState.totalFiles} files)`,
            allComplete: completed === total,
            output: compileOutput.trim()
          });
        }

        // Compilation failed
        batch.retries = (batch.retries || 0) + 1;

        if (timedOut) {
          batch.retries -= 1;
          saveState(currentState.outputDir);
          return result({
            batchId,
            compiled: false,
            status: 'in_progress',
            error: `cjpm build timed out (300s).`,
            message: `TIMEOUT: Try running "cd ${moduleDir} && cjpm build 2>&1" manually, then use mark_complete("${batchId}") if it succeeds.`
          });
        }

        if (batch.retries >= MAX_RETRIES) {
          batch.status = 'blocked';
          batch.blockReason = `Compilation failed after ${MAX_RETRIES} attempts. Last error:\n${compileOutput.trim().slice(0, 2000)}`;
          batch.blockedAt = new Date().toISOString();
          saveState(currentState.outputDir);

          return result({
            batchId,
            compiled: false,
            status: 'blocked',
            retries: batch.retries,
            error: compileOutput.trim(),
            message: `BLOCKED: Compilation failed ${MAX_RETRIES} times. Use java2cangjie-fix skill to resolve manually.`
          });
        }

        saveState(currentState.outputDir);
        return result({
          batchId,
          compiled: false,
          status: 'in_progress',
          retries: batch.retries,
          retriesLeft: MAX_RETRIES - batch.retries,
          error: compileOutput.trim(),
          message: `Compilation failed (attempt ${batch.retries}/${MAX_RETRIES}). Fix the errors above, then call compile_batch("${batchId}") again.`
        });
      } catch (e) {
        return result({ error: `compile_batch failed: ${e.message}` });
      }
    }
  }),

  mark_complete: tool({
    description: 'Manual override: mark a batch as completed. Prefer compile_batch() instead.',
    args: {
      batchId: tool.schema.string().describe('Batch identifier'),
      outputFiles: tool.schema.array(tool.schema.string()).optional().describe('Generated Cangjie file paths'),
    },
    async execute(args, context) {
      try {
        const { batchId } = args;
        const outputFiles = args.outputFiles || [];
        if (!currentState || !currentState.batches[batchId]) {
          return result({ error: `Batch ${batchId} not found` });
        }
        currentState.batches[batchId].status = 'completed';
        currentState.batches[batchId].outputFiles = outputFiles;
        currentState.batches[batchId].completedAt = new Date().toISOString();
        saveState(currentState.outputDir);

        const completed = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
        return result({
          batchId,
          status: 'completed',
          progress: `${completed}/${currentState.totalFiles} files done`,
          allComplete: completed === Object.keys(currentState.batches).length
        });
      } catch (e) {
        return result({ error: `mark_complete failed: ${e.message}` });
      }
    }
  }),

  mark_blocked: tool({
    description: 'Mark a translation batch as blocked (failed after max retries)',
    args: {
      batchId: tool.schema.string().describe('Batch identifier'),
      reason: tool.schema.string().describe('Error description'),
    },
    async execute(args, context) {
      try {
        const { batchId, reason } = args;
        if (!currentState || !currentState.batches[batchId]) {
          return result({ error: `Batch ${batchId} not found` });
        }
        currentState.batches[batchId].status = 'blocked';
        currentState.batches[batchId].blockReason = reason;
        currentState.batches[batchId].blockedAt = new Date().toISOString();
        saveState(currentState.outputDir);

        const available = Object.entries(currentState.batches).filter(([id, b]) => {
          if (b.status !== 'pending') return false;
          return (b.dependencies || []).every(depId => currentState.batches[depId]?.status === 'completed');
        });

        return result({
          batchId,
          status: 'blocked',
          reason,
          canProceed: available.length > 0,
          availableBatches: available.map(([id]) => id)
        });
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
          projectPath: currentState.projectPath,
          outputDir: currentState.outputDir,
          totalFiles: currentState.totalFiles || 0,
          totalBatches: batches.length,
          completed: batches.filter(b => b.status === 'completed').length,
          inProgress: batches.filter(b => b.status === 'in_progress').length,
          blocked: batches.filter(b => b.status === 'blocked').length,
          pending: batches.filter(b => b.status === 'pending').length,
          blockedBatches: batches.filter(b => b.status === 'blocked').map(b => ({
            id: Object.entries(currentState.batches).find(([_, v]) => v === b)?.[0],
            reason: b.blockReason || ''
          }))
        });
      } catch (e) {
        return result({ error: `translation_status failed: ${e.message}` });
      }
    }
  })
});

// ============================================================
// Plugin export — follows superpowers pattern exactly
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

  // Build hooks — config + message transform always work (zero external deps)
  const hooks = {
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

  // Dynamic import of @opencode-ai/plugin for tool registration.
  // If unavailable, skills and bootstrap still work — only tools are skipped.
  try {
    const { tool } = await import('@opencode-ai/plugin');
    hooks.tool = createTools(tool);
  } catch (e) {
    // @opencode-ai/plugin not available — tools will be skipped
    // Skills and bootstrap injection still work fine.
    if (typeof process !== 'undefined' && process.stderr) {
      process.stderr.write('[java2cangjie] Warning: @opencode-ai/plugin not available, custom tools not registered. Skills and bootstrap still active.\n');
    }
  }

  return hooks;
};
