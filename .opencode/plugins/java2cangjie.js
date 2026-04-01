import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { tool } from '@opencode-ai/plugin';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };
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
  const javaFiles = [];
  const fileMap = new Map(); // className -> filePath

  const scanDir = (dir) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.name.endsWith('.java')) {
        const className = entry.name.replace('.java', '');
        javaFiles.push({ path: fullPath, className, deps: [] });
        fileMap.set(className, fullPath);
      }
    }
  };

  if (!fs.existsSync(javaRoot)) {
    return { error: `Java source directory not found: ${javaRoot}` };
  }
  scanDir(javaRoot);

  // Parse imports to build dependency graph
  for (const file of javaFiles) {
    const content = fs.readFileSync(file.path, 'utf8');
    const importLines = content.match(/^import\s+[\w.]+;/gm) || [];
    for (const imp of importLines) {
      const importedClass = imp.replace('import ', '').replace(';', '').split('.').pop();
      if (fileMap.has(importedClass) && importedClass !== file.className) {
        file.deps.push(importedClass);
      }
    }
  }

  // Topological sort (Kahn's algorithm)
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

  const getBootstrapContent = () => {
    const skillPath = path.join(skillsDir, 'using-java2cangjie', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;
    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);
    const toolMapping = `**Tool Mapping for OpenCode:**
- \`TodoWrite\` → \`todowrite\`
- \`Skill\` tool → OpenCode's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` → Your native tools
- Plugin tools: \`analyze_project\`, \`next_batch\`, \`mark_complete\`, \`mark_blocked\`, \`translation_status\``;

    return `<EXTREMELY_IMPORTANT>
You have the Java to Cangjie translation system.
**IMPORTANT: The using-java2cangjie skill content is included below. It is ALREADY LOADED.**
${content}
${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    'experimental.chat.system.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (bootstrap) {
        (output.system ||= []).push(bootstrap);
      }
    },

    tool: {
      analyze_project: tool({
        description: 'Analyze Java project structure, build dependency graph, return translation batch plan',
        args: {
          javaPath: tool.schema.string().describe('Path to Java source root directory'),
          maxBatchSize: tool.schema.number().default(3).describe('Max files per batch (default: 3)'),
          outputDir: tool.schema.string().optional().describe('Output directory for translated files (default: <javaPath>/../j2cjgenerated/)'),
        },
        async execute(args, context) {
          const { javaPath, maxBatchSize, outputDir } = args;
          const outDir = outputDir || path.join(path.dirname(javaPath), 'j2cjgenerated');
          const result = analyzeJavaDependencies(javaPath, maxBatchSize);
          if (result.error) return result;

          currentState = {
            projectPath: javaPath,
            outputDir: outDir,
            totalFiles: result.totalFiles,
            batches: {},
            dagSummary: result.dagSummary,
            createdAt: new Date().toISOString()
          };
          for (const batch of result.batches) {
            currentState.batches[batch.id] = {
              status: 'pending',
              files: batch.files,
              dependencies: batch.dependencies,
              retries: 0
            };
          }
          saveState(outDir);

          return {
            totalFiles: result.totalFiles,
            totalBatches: result.batches.length,
            batches: result.batches.map(b => ({
              id: b.id,
              fileCount: b.files.length,
              files: b.files.map(f => f.className),
              dependencies: b.dependencies
            })),
            dagSummary: result.dagSummary,
            outputDir: outDir
          };
        }
      }),

      next_batch: tool({
        description: 'Get next batch of Java files ready for translation (all dependencies completed)',
        args: {},
        async execute(args, context) {
          if (!currentState) return { error: 'No active project. Call analyze_project first.' };
          for (const [batchId, batch] of Object.entries(currentState.batches)) {
            if (batch.status !== 'pending') continue;
            const allDepsComplete = batch.dependencies.every(
              depId => currentState.batches[depId]?.status === 'completed'
            );
            if (allDepsComplete) {
              batch.status = 'in_progress';
              batch.startedAt = new Date().toISOString();
              saveState(currentState.outputDir);
              return {
                batchId,
                files: batch.files,
                ready: true
              };
            }
          }
          const completed = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
          const blocked = Object.values(currentState.batches).filter(b => b.status === 'blocked').length;
          const pending = Object.values(currentState.batches).filter(b => b.status === 'pending').length;
          return {
            ready: false,
            message: 'No batches available. All dependencies must be completed first.',
            progress: { completed, blocked, pending }
          };
        }
      }),

      mark_complete: tool({
        description: 'Mark a translation batch as complete (compilation passed)',
        args: {
          batchId: tool.schema.string().describe('Batch identifier'),
          outputFiles: tool.schema.array(tool.schema.string()).optional().describe('Generated Cangjie file paths'),
        },
        async execute(args, context) {
          const { batchId, outputFiles } = args;
          if (!currentState || !currentState.batches[batchId]) {
            return { error: `Batch ${batchId} not found` };
          }
          currentState.batches[batchId].status = 'completed';
          currentState.batches[batchId].outputFiles = outputFiles || [];
          currentState.batches[batchId].completedAt = new Date().toISOString();
          saveState(currentState.outputDir);

          const completed = Object.values(currentState.batches).filter(b => b.status === 'completed').length;
          return {
            batchId,
            status: 'completed',
            progress: `${completed}/${currentState.totalFiles} files done`,
            allComplete: completed === Object.keys(currentState.batches).length
          };
        }
      }),

      mark_blocked: tool({
        description: 'Mark a translation batch as blocked (failed after max retries)',
        args: {
          batchId: tool.schema.string().describe('Batch identifier'),
          reason: tool.schema.string().describe('Error description'),
        },
        async execute(args, context) {
          const { batchId, reason } = args;
          if (!currentState || !currentState.batches[batchId]) {
            return { error: `Batch ${batchId} not found` };
          }
          currentState.batches[batchId].status = 'blocked';
          currentState.batches[batchId].blockReason = reason;
          currentState.batches[batchId].blockedAt = new Date().toISOString();
          saveState(currentState.outputDir);

          const available = Object.entries(currentState.batches).filter(([id, b]) => {
            if (b.status !== 'pending') return false;
            return b.dependencies.every(depId => currentState.batches[depId]?.status === 'completed');
          });

          return {
            batchId,
            status: 'blocked',
            reason,
            canProceed: available.length > 0,
            availableBatches: available.map(([id]) => id)
          };
        }
      }),

      translation_status: tool({
        description: 'Get current translation progress',
        args: {},
        async execute(args, context) {
          if (!currentState) return { error: 'No active project. Call analyze_project first.' };
          const batches = Object.values(currentState.batches);
          return {
            projectPath: currentState.projectPath,
            outputDir: currentState.outputDir,
            totalFiles: currentState.totalFiles,
            totalBatches: batches.length,
            completed: batches.filter(b => b.status === 'completed').length,
            inProgress: batches.filter(b => b.status === 'in_progress').length,
            blocked: batches.filter(b => b.status === 'blocked').length,
            pending: batches.filter(b => b.status === 'pending').length,
            blockedBatches: batches.filter(b => b.status === 'blocked').map(b => ({
              id: Object.entries(currentState.batches).find(([_, v]) => v === b)?.[0],
              reason: b.blockReason
            }))
          };
        }
      })
    }
  };
};
