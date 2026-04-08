/**
 * Java2Cangjie plugin for OpenCode.ai
 *
 * Injects translation bootstrap context via chat messages transform.
 * Auto-registers skills directory via config hook (no symlinks needed).
 * Provides 6 custom tools for dependency-driven translation workflow.
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

    // 1. Parse regular imports: import x.y.Z; or import x.y.*
    const regularImports = normalized.match(/^import\s+(?!static\b)([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of regularImports) {
      const imported = imp.replace(/^import\s+/, '').replace(/\s*;$/, '').trim();
      if (imported.endsWith('.*')) {
        // Wildcard import: resolve all classes in that package
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

    // 2. Parse static imports: import static x.y.Z.method; or import static x.y.Z.*
    const staticImports = normalized.match(/^import\s+static\s+([\w.]+(?:\.\*)?)\s*;/gm) || [];
    for (const imp of staticImports) {
      const imported = imp.replace(/^import\s+static\s+/, '').replace(/\s*;$/, '').trim();
      // static import: last segment is method/field, second-to-last is class
      // e.g. import static net.lingala.zip4j.util.Zip4jUtil.convertCharArrayToByteArray
      //   -> class = Zip4jUtil
      // e.g. import static net.lingala.zip4j.util.InternalZipConstants.*
      //   -> class = InternalZipConstants
      const parts = imported.split('.');
      if (imported.endsWith('.*')) {
        // static wildcard: second-to-last is the class
        const className = parts.length >= 2 ? parts[parts.length - 2] : null;
        if (className && fileMap.has(className) && className !== file.className) {
          depSet.add(className);
        }
      } else {
        // static method/field: second-to-last is the class
        const className = parts.length >= 2 ? parts[parts.length - 2] : null;
        if (className && fileMap.has(className) && className !== file.className) {
          depSet.add(className);
        }
      }
    }

    // 3. Detect same-package implicit dependencies
    // Java classes in the same package can reference each other without imports
    if (info.packageName && packageToClasses.has(info.packageName)) {
      const samePkgClasses = packageToClasses.get(info.packageName);
      for (const cls of samePkgClasses) {
        if (cls !== file.className) {
          // Check if this class name actually appears in the content
          // Use word boundary to avoid partial matches
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

  // Handle remaining nodes in dependency cycles: force-add them
  // sorted only contains cycle-free nodes; remaining have circular deps
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
  const remaining = [...sorted];
  while (remaining.length > 0) {
    const batch = remaining.splice(0, maxBatchSize);
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

  // Count lines for each file
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
// Plugin export
// ============================================================

export const Java2CangjiePlugin = async ({ client, directory }) => {
  const skillsDir = path.resolve(__dirname, '../../skills');

  // Helper to generate bootstrap content
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

**IMPORTANT: The using-java2cangjie skill content is included below. It is ALREADY LOADED - you are currently following it. Do NOT use the skill tool to load "using-java2cangjie" again - that would be redundant.**

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    // Inject skills path into live config so OpenCode discovers all java2cangjie skills
    // without requiring manual symlinks or config file edits.
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into the first user message of each session.
    // Using a user message instead of a system message avoids:
    //   1. Token bloat from system messages repeated every turn
    //   2. Multiple system messages breaking Qwen and other models
    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) return;
      const firstUser = output.messages.find(m => m.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;
      // Only inject once
      if (firstUser.parts.some(p => p.type === 'text' && p.text.includes('EXTREMELY_IMPORTANT'))) return;
      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: 'text', text: bootstrap });
    },

    // Preserve context across session compaction
    'experimental.session.compacting': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (typeof bootstrap === 'string' && bootstrap.length > 0) {
        output.context.push(bootstrap);
      }
    },

    tool: {
      analyze_project: tool({
        description: 'Analyze Java project structure, build dependency graph, return translation batch plan',
        args: {
          javaPath: tool.schema.union([tool.schema.string(), tool.schema.array(tool.schema.string())]).describe('Path(s) to Java source root directory(ies). Can be a single path or array of paths.'),
          maxBatchSize: tool.schema.number().optional().describe('Max files per batch (default: 3)'),
          outputDir: tool.schema.string().optional().describe('Output directory for translated files (default: <javaPath>/../j2cjgenerated/)'),
        },
        async execute(args, context) {
          try {
            const { javaPath } = args;
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
        description: 'Get next batch of Java files ready for translation. BLOCKS if a batch is currently in_progress — you must compile_batch() first to complete or block the current batch before getting the next one.',
        args: {},
        async execute(args, context) {
          try {
            if (!currentState) return result({ error: 'No active project. Call analyze_project first.' });

            // GUARD: Enforce one-batch-at-a-time — must compile before advancing
            const inProgress = Object.entries(currentState.batches).find(
              ([id, b]) => b.status === 'in_progress'
            );
            if (inProgress) {
              return result({
                ready: false,
                blocked: true,
                message: `BLOCKED: Batch ${inProgress[0]} is still in_progress. You MUST call compile_batch("${inProgress[0]}") to compile and complete it before requesting the next batch.`,
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
        description: 'Compile the output project with cjpm build for the given batch. On success, automatically marks the batch as completed. On failure, returns compile errors for fixing. After 3 failed attempts, automatically marks the batch as blocked. This is the REQUIRED way to advance batches — do NOT call mark_complete without compiling first.',
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
              return result({ error: `Batch ${batchId} status is '${batch.status}', not 'in_progress'. Call next_batch() first to start a batch.` });
            }

            // Find module directory (where cjpm.toml exists)
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
                error: `No cjpm.toml found under ${outputDir}. Ensure the output project has been initialized with a cjpm.toml file.`,
                message: `No cjpm.toml found. Create the Cangjie project structure first (cjpm.toml + src/ directory).`
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

            // Run cjpm build in the module directory
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
              // Auto-mark as completed
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
              // Timeout — don't count against retry limit, suggest manual compile
              batch.retries -= 1; // undo the increment
              saveState(currentState.outputDir);
              return result({
                batchId,
                compiled: false,
                status: 'in_progress',
                error: `cjpm build timed out (300s). This usually means too many errors or a slow build.`,
                message: `TIMEOUT: cjpm build timed out. Try running "cd ${moduleDir} && cjpm build 2>&1" manually, then use mark_complete("${batchId}") if it succeeds, or fix errors and retry compile_batch.`
              });
            }

            if (batch.retries >= MAX_RETRIES) {
              // Auto-block after max retries
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
                message: `BLOCKED: Compilation failed ${MAX_RETRIES} times. Batch marked as blocked. Use java2cangjie-fix skill to resolve manually.`
              });
            }

            // Still has retries left — keep in_progress
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
        description: 'Manual override: mark a batch as completed. Prefer using compile_batch() instead, which compiles and auto-marks on success. Use this ONLY when you have already verified compilation externally.',
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
    }
  };
};
