#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const errors = [];
const warnings = [];

// Size limits on the always-applied rule are a review trigger, not a spending cap.
// The original 3600-char ceiling was justified on cost, and that premise does not
// hold: measured 2026-09-01, the body is 3566 chars (~890 tokens) — 0.45% of a 200k
// context window. What actually degrades as the file grows is instruction weight,
// and this project has recorded that failure twice (2026-07-01: prose conventions
// get ignored under context pressure; 2026-08-13: a clause that "read as coverage
// but caught nothing"). A char count is a crude proxy for that, so it warns.
//
// Soft line: the size the 2026-08-27 audit judged bloated (4242), rounded down.
// Crossing it means re-run the clause audit. The second line is a stronger review
// signal for likely misplaced detail, not a correctness failure: size is too crude
// a proxy to block a capability the protocol genuinely needs.
//
// The audit asks about cost as well as value, because nothing else here does: both
// stop-hook signals push toward more work and these lines measure resident context,
// not the work the protocol imposes. A clause with no off-switch for trivial tasks
// is the growth to cut first (2026-09-01).
const ALWAYS_ON_SOFT_CHARS = 4200;
const ALWAYS_ON_STRONG_REVIEW_CHARS = 6000;

function addError(message) {
  errors.push(message);
}

function addWarning(message) {
  warnings.push(message);
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

// Mirrors read_protocol() in hooks/scripts/session-context.py: every host that
// consumes the rule uses the body without frontmatter, so that is what the
// budget has to measure.
function ruleBody(content) {
  if (!content.startsWith("---")) return content.trim();
  const frontmatterEnd = content.indexOf("---", 3);
  if (frontmatterEnd === -1) return content.trim();
  return content.slice(frontmatterEnd + 3).trim();
}

async function readJSON(filePath) {
  try {
    const content = await fs.readFile(filePath, "utf8");
    return JSON.parse(content);
  } catch (e) {
    return null;
  }
}

async function validateMarketplace() {
  const marketplacePath = path.join(repoRoot, ".cursor-plugin", "marketplace.json");
  if (!(await pathExists(marketplacePath))) {
    addError(".cursor-plugin/marketplace.json not found");
    return;
  }

  const marketplace = await readJSON(marketplacePath);
  if (!marketplace) {
    addError(".cursor-plugin/marketplace.json is invalid JSON");
    return;
  }

  if (!marketplace.name) {
    addError("marketplace.json: missing 'name'");
  }

  if (!marketplace.plugins || !Array.isArray(marketplace.plugins)) {
    addError("marketplace.json: missing or invalid 'plugins' array");
    return;
  }

  for (const plugin of marketplace.plugins) {
    if (!plugin.name) {
      addError("marketplace.json: plugin entry missing 'name'");
      continue;
    }
    if (!plugin.source) {
      addError(`marketplace.json: plugin '${plugin.name}' missing 'source'`);
      continue;
    }

    const pluginDir = path.resolve(repoRoot, plugin.source);
    if (!(await pathExists(pluginDir))) {
      addError(`marketplace.json: plugin '${plugin.name}' source path does not exist: ${plugin.source}`);
      continue;
    }

    await validatePlugin(pluginDir, plugin.name);
  }
}

async function validateCodexMarketplace() {
  const marketplacePath = path.join(repoRoot, ".agents", "plugins", "marketplace.json");
  if (!(await pathExists(marketplacePath))) {
    addError(".agents/plugins/marketplace.json not found (Codex marketplace)");
    return;
  }

  const marketplace = await readJSON(marketplacePath);
  if (!marketplace) {
    addError(".agents/plugins/marketplace.json is invalid JSON");
    return;
  }

  if (!marketplace.name) {
    addError("codex marketplace.json: missing 'name'");
  }

  if (!marketplace.plugins || !Array.isArray(marketplace.plugins)) {
    addError("codex marketplace.json: missing or invalid 'plugins' array");
    return;
  }

  for (const plugin of marketplace.plugins) {
    if (!plugin.name) {
      addError("codex marketplace.json: plugin entry missing 'name'");
      continue;
    }

    const sourcePath = typeof plugin.source === "string" ? plugin.source : plugin.source?.path;
    if (typeof sourcePath !== "string") {
      addError(`codex marketplace.json: plugin '${plugin.name}' missing 'source.path'`);
      continue;
    }
    if (!sourcePath.startsWith("./")) {
      addError(`codex marketplace.json: plugin '${plugin.name}' source.path must start with './'`);
    }

    // Codex resolves source.path relative to the marketplace root, which for a
    // repo marketplace is the repository root.
    const pluginDir = path.resolve(repoRoot, sourcePath);
    if (!(await pathExists(pluginDir))) {
      addError(`codex marketplace.json: plugin '${plugin.name}' source path does not exist: ${sourcePath}`);
      continue;
    }

    for (const field of ["installation", "authentication"]) {
      if (!plugin.policy?.[field]) {
        addError(`codex marketplace.json: plugin '${plugin.name}' missing 'policy.${field}'`);
      }
    }
    if (!plugin.category) {
      addError(`codex marketplace.json: plugin '${plugin.name}' missing 'category'`);
    }

    await validateCodexPlugin(pluginDir, plugin.name);
  }
}

async function validateCodebuddyMarketplace() {
  const marketplacePath = path.join(repoRoot, ".codebuddy-plugin", "marketplace.json");
  if (!(await pathExists(marketplacePath))) {
    addError(".codebuddy-plugin/marketplace.json not found (CodeBuddy marketplace)");
    return;
  }

  const marketplace = await readJSON(marketplacePath);
  if (!marketplace) {
    addError(".codebuddy-plugin/marketplace.json is invalid JSON");
    return;
  }

  if (!marketplace.name) {
    addError("codebuddy marketplace.json: missing 'name'");
  }

  if (!marketplace.plugins || !Array.isArray(marketplace.plugins)) {
    addError("codebuddy marketplace.json: missing or invalid 'plugins' array");
    return;
  }

  for (const plugin of marketplace.plugins) {
    if (!plugin.name) {
      addError("codebuddy marketplace.json: plugin entry missing 'name'");
      continue;
    }
    if (!plugin.description) {
      addError(`codebuddy marketplace.json: plugin '${plugin.name}' missing 'description'`);
    }

    const sourcePath = typeof plugin.source === "string" ? plugin.source : plugin.source?.path;
    if (typeof sourcePath !== "string") {
      addError(`codebuddy marketplace.json: plugin '${plugin.name}' missing 'source'`);
      continue;
    }
    if (!sourcePath.startsWith("./")) {
      addError(`codebuddy marketplace.json: plugin '${plugin.name}' source must start with './'`);
    }

    const pluginDir = path.resolve(repoRoot, sourcePath);
    if (!(await pathExists(pluginDir))) {
      addError(`codebuddy marketplace.json: plugin '${plugin.name}' source path does not exist: ${sourcePath}`);
      continue;
    }

    await validateCodebuddyPlugin(pluginDir, plugin.name);
  }
}

async function validateCodebuddyPlugin(pluginDir, pluginName) {
  const manifestPath = path.join(pluginDir, ".codebuddy-plugin", "plugin.json");
  if (!(await pathExists(manifestPath))) {
    addError(`CodeBuddy plugin '${pluginName}': missing .codebuddy-plugin/plugin.json`);
    return;
  }

  const manifest = await readJSON(manifestPath);
  if (!manifest) {
    addError(`CodeBuddy plugin '${pluginName}': plugin.json is invalid JSON`);
    return;
  }

  for (const field of ["name", "version", "description"]) {
    if (!manifest[field]) {
      addError(`CodeBuddy plugin '${pluginName}': plugin.json missing required field '${field}'`);
    }
  }

  const pathFields = ["skills", "hooks", "commands", "agents", "mcpServers"];
  for (const field of pathFields) {
    const value = manifest[field];
    const paths = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
    for (const rel of paths) {
      if (typeof rel !== "string") continue;
      if (!rel.startsWith("./")) {
        addError(`CodeBuddy plugin '${pluginName}': '${field}' entry '${rel}' must start with './'`);
      }
      if (!(await pathExists(path.join(pluginDir, rel)))) {
        addError(`CodeBuddy plugin '${pluginName}': '${field}' path not found: ${rel}`);
      }
    }
  }

  const hooksRel = typeof manifest.hooks === "string" ? manifest.hooks : "./hooks/hooks.json";
  if (hooksRel.replace(/^\.\//, "") === "hooks/hooks.json") {
    addError(
      `CodeBuddy plugin '${pluginName}': hooks must not point at hooks/hooks.json (that file is Cursor's camelCase config)`,
    );
  }
  await validateClaudeStyleHooks(pluginDir, pluginName, hooksRel, {
    envVar: "CODEBUDDY_PLUGIN_ROOT",
    hostArg: "codebuddy",
    label: "CodeBuddy",
  });
}

async function validateCodexPlugin(pluginDir, pluginName) {
  const manifestPath = path.join(pluginDir, ".codex-plugin", "plugin.json");
  if (!(await pathExists(manifestPath))) {
    addError(`Codex plugin '${pluginName}': missing .codex-plugin/plugin.json`);
    return;
  }

  const manifest = await readJSON(manifestPath);
  if (!manifest) {
    addError(`Codex plugin '${pluginName}': plugin.json is invalid JSON`);
    return;
  }

  for (const field of ["name", "version", "description"]) {
    if (!manifest[field]) {
      addError(`Codex plugin '${pluginName}': plugin.json missing required field '${field}'`);
    }
  }

  // Manifest paths must be './'-prefixed, resolve inside the plugin root, and exist.
  const pathFields = ["skills", "hooks", "mcpServers", "apps"];
  for (const field of pathFields) {
    const value = manifest[field];
    if (typeof value !== "string") continue;
    if (!value.startsWith("./")) {
      addError(`Codex plugin '${pluginName}': '${field}' must start with './'`);
    }
    if (!(await pathExists(path.join(pluginDir, value)))) {
      addError(`Codex plugin '${pluginName}': '${field}' path not found: ${value}`);
    }
  }

  const logo = manifest.interface?.logo;
  if (typeof logo === "string" && !(await pathExists(path.join(pluginDir, logo)))) {
    addError(`Codex plugin '${pluginName}': interface.logo not found: ${logo}`);
  }

  const hooksRel = typeof manifest.hooks === "string" ? manifest.hooks : "./hooks/hooks.json";
  await validateCodexHooks(pluginDir, pluginName, hooksRel);
}

async function validateClaudeStyleHooks(pluginDir, pluginName, hooksRel, options) {
  const { envVar, hostArg, label } = options;
  const hooksPath = path.join(pluginDir, hooksRel);
  if (!(await pathExists(hooksPath))) return;

  const hooksJson = await readJSON(hooksPath);
  if (!hooksJson) {
    addError(`${label} plugin '${pluginName}': ${hooksRel} is invalid JSON`);
    return;
  }

  const events = hooksJson.hooks;
  if (!events || typeof events !== "object") {
    addError(`${label} plugin '${pluginName}': ${hooksRel} missing 'hooks' object`);
    return;
  }

  const envPattern = new RegExp(`\\$\\{${envVar}[^}]*\\}([^"'\\s]+)`);

  for (const [eventName, matchers] of Object.entries(events)) {
    // Claude-family events are PascalCase; a camelCase key means Cursor config leaked in.
    if (/^[a-z]/.test(eventName)) {
      addError(
        `${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' looks like a Cursor event name (${label} uses PascalCase, e.g. SessionStart)`,
      );
    }
    if (!Array.isArray(matchers)) {
      addError(`${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' must be an array`);
      continue;
    }

    for (const matcher of matchers) {
      // Claude-family hosts nest the commands one level deeper than Cursor does.
      if (!Array.isArray(matcher?.hooks)) {
        addError(
          `${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' entry missing nested 'hooks' array`,
        );
        continue;
      }
      for (const hook of matcher.hooks) {
        if (hook.type !== "command") {
          addError(`${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' hook missing "type": "command"`);
          continue;
        }
        if (typeof hook.command !== "string") {
          addError(`${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' hook missing 'command'`);
          continue;
        }
        const hostToken = new RegExp(`(?:^|\\s)${hostArg}(?:\\s|"|$)`);
        if (!hostToken.test(hook.command)) {
          addError(
            `${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' command must pass '${hostArg}' as the host argument`,
          );
        }
        const scriptMatch = hook.command.match(envPattern);
        if (!scriptMatch) {
          addWarning(
            `${label} plugin '${pluginName}': ${hooksRel} event '${eventName}' command does not reference \${${envVar}}; it may not resolve when installed`,
          );
          continue;
        }
        const scriptPath = path.join(pluginDir, scriptMatch[1]);
        if (!(await pathExists(scriptPath))) {
          addError(`${label} hook '${eventName}': script not found: ${scriptMatch[1]}`);
        }
      }
    }
  }
}

async function validateCodexHooks(pluginDir, pluginName, hooksRel) {
  await validateClaudeStyleHooks(pluginDir, pluginName, hooksRel, {
    envVar: "PLUGIN_ROOT",
    hostArg: "codex",
    label: "Codex",
  });
}

async function validateHostNeutrality(pluginDir, pluginName) {
  const skillsDir = path.join(pluginDir, "skills");
  if (!(await pathExists(skillsDir))) return;

  const skillNames = (await fs.readdir(skillsDir, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);
  if (skillNames.length === 0) return;

  // Rules and skills are shared verbatim by every host, so they must not hardcode
  // one host's invocation prefix ('/name' in Cursor, '$name' in Codex).
  const sharedFiles = skillNames.map((name) => path.join(skillsDir, name, "SKILL.md"));
  const rulesDir = path.join(pluginDir, "rules");
  if (await pathExists(rulesDir)) {
    for (const file of await fs.readdir(rulesDir)) {
      if (/\.(md|mdc|markdown)$/.test(file)) sharedFiles.push(path.join(rulesDir, file));
    }
  }

  for (const file of sharedFiles) {
    if (!(await pathExists(file))) continue;
    const content = await fs.readFile(file, "utf8");
    for (const name of skillNames) {
      const pattern = new RegExp(`(^|[^\\w./-])[$/]${name}\\b`, "m");
      if (pattern.test(content)) {
        addError(
          `Host-specific invocation of skill '${name}' in ${path.relative(repoRoot, file)}: shared content must name the skill without a '/' or '$' prefix`,
        );
      }
    }
  }
}

async function validatePlugin(pluginDir, pluginName) {
  // Check plugin.json
  const pluginJsonPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
  if (!(await pathExists(pluginJsonPath))) {
    addError(`Plugin '${pluginName}': missing .cursor-plugin/plugin.json`);
    return;
  }

  const pluginJson = await readJSON(pluginJsonPath);
  if (!pluginJson) {
    addError(`Plugin '${pluginName}': plugin.json is invalid JSON`);
    return;
  }

  const requiredFields = ["name", "displayName", "version", "description"];
  for (const field of requiredFields) {
    if (!pluginJson[field]) {
      addError(`Plugin '${pluginName}': plugin.json missing required field '${field}'`);
    }
  }

  // Check name is kebab-case
  if (pluginJson.name && !/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/.test(pluginJson.name)) {
    addError(`Plugin '${pluginName}': name must be lowercase kebab-case`);
  }

  // Check rules
  const rulesDir = path.join(pluginDir, "rules");
  if (await pathExists(rulesDir)) {
    const files = await fs.readdir(rulesDir);
    for (const file of files) {
      if (file.endsWith(".mdc")) {
        const content = await fs.readFile(path.join(rulesDir, file), "utf8");
        if (!content.includes("description:")) {
          addError(`Rule '${file}': missing frontmatter 'description'`);
        }
        if (/^alwaysApply:\s*true\s*$/m.test(content)) {
          const bodyChars = ruleBody(content).length;
          if (bodyChars > ALWAYS_ON_STRONG_REVIEW_CHARS) {
            addWarning(
              `Rule '${file}': always-applied body is ${bodyChars} chars, past the ${ALWAYS_ON_STRONG_REVIEW_CHARS} strong-review line. Not a failure. Explain why the added capability must stay always-on rather than move into a skill, then audit scope and duplication.`,
            );
          } else if (bodyChars > ALWAYS_ON_SOFT_CHARS) {
            addWarning(
              `Rule '${file}': always-applied body is ${bodyChars} chars, past the ${ALWAYS_ON_SOFT_CHARS} review line. Not a failure. Re-run the clause audit: does each clause prevent a material observed or predictable failure, does anything duplicate a skill or the Ownership table, and does each clause name a condition that turns it off on trivial work?`,
            );
          }
        }
      }
    }
  }

  // Check skills
  const skillsDir = path.join(pluginDir, "skills");
  if (await pathExists(skillsDir)) {
    const entries = await fs.readdir(skillsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        const skillMd = path.join(skillsDir, entry.name, "SKILL.md");
        if (!(await pathExists(skillMd))) {
          addError(`Skill '${entry.name}': missing SKILL.md`);
        } else {
          const content = await fs.readFile(skillMd, "utf8");
          if (!content.includes("name:") || !content.includes("description:")) {
            addError(`Skill '${entry.name}': SKILL.md missing frontmatter 'name' or 'description'`);
          }
          const nameMatch = content.match(/^name:\s*([^\n]+)/m);
          if (nameMatch && nameMatch[1].trim() !== entry.name) {
            addError(
              `Skill '${entry.name}': frontmatter name '${nameMatch[1].trim()}' must match folder name`,
            );
          }
        }
      }
    }
  }

  // Check commands
  const commandsDir = path.join(pluginDir, "commands");
  if (await pathExists(commandsDir)) {
    const files = await fs.readdir(commandsDir);
    for (const file of files) {
      if (file.endsWith(".md")) {
        const content = await fs.readFile(path.join(commandsDir, file), "utf8");
        if (!content.includes("name:") || !content.includes("description:")) {
          addError(`Command '${file}': missing frontmatter 'name' or 'description'`);
        }
      }
    }
  }

  // Check agents (subagents)
  const agentsDir = path.join(pluginDir, "agents");
  if (await pathExists(agentsDir)) {
    const files = await fs.readdir(agentsDir);
    for (const file of files) {
      if (file.endsWith(".md")) {
        const content = await fs.readFile(path.join(agentsDir, file), "utf8");
        if (!content.includes("name:") || !content.includes("description:")) {
          addError(`Agent '${file}': missing frontmatter 'name' or 'description'`);
        }
        const baseName = file.replace(/\.md$/, "");
        const nameMatch = content.match(/^name:\s*([^\n]+)/m);
        if (nameMatch && nameMatch[1].trim() !== baseName) {
          addError(`Agent '${file}': frontmatter name '${nameMatch[1].trim()}' must match filename`);
        }
      }
    }
  }

  // Check hooks
  const hooksJsonPath = path.join(pluginDir, "hooks", "hooks.json");
  if (await pathExists(hooksJsonPath)) {
    const hooksJson = await readJSON(hooksJsonPath);
    if (!hooksJson) {
      addError(`Plugin '${pluginName}': hooks/hooks.json is invalid JSON`);
    } else {
      if (hooksJson.version !== 1) {
        addWarning(`Plugin '${pluginName}': hooks/hooks.json should include "version": 1`);
      }
      // Cursor events are camelCase; a PascalCase key means Codex config leaked in.
      for (const eventName of Object.keys(hooksJson.hooks ?? {})) {
        if (/^[A-Z]/.test(eventName)) {
          addError(
            `Plugin '${pluginName}': hooks/hooks.json event '${eventName}' looks like a Codex event name (Cursor uses camelCase, e.g. sessionStart)`,
          );
        }
      }
    }
  }

  // Check hook scripts exist
  if (hooksJsonPath && await pathExists(hooksJsonPath)) {
    const hooksJson = await readJSON(hooksJsonPath);
    if (hooksJson && hooksJson.hooks) {
      for (const [hookType, hookList] of Object.entries(hooksJson.hooks)) {
        for (const hook of hookList) {
          if (hook.command) {
            const scriptPath = path.join(pluginDir, "hooks", hook.command);
            if (!(await pathExists(scriptPath))) {
              addError(`Hook '${hookType}': script not found: ${hook.command}`);
            } else {
              try {
                await fs.access(scriptPath, fs.constants.X_OK);
              } catch {
                addWarning(`Hook '${hookType}': script is not executable: ${hook.command}`);
              }
            }
          }
        }
      }
    }
  }

  await validateHostNeutrality(pluginDir, pluginName);
}

async function main() {
  console.log("Validating agent-context plugin structure...\n");

  await validateMarketplace();
  await validateCodexMarketplace();
  await validateCodebuddyMarketplace();

  // Check for logo
  const logoPath = path.join(repoRoot, "plugins", "agent-context", "assets", "logo.svg");
  if (!(await pathExists(logoPath))) {
    addWarning("assets/logo.svg not found (referenced in plugin.json)");
  }

  if (warnings.length > 0) {
    console.log("\nWarnings:");
    for (const warning of warnings) {
      console.log(`  ⚠️  ${warning}`);
    }
  }

  if (errors.length > 0) {
    console.log("\nErrors:");
    for (const error of errors) {
      console.log(`  ❌ ${error}`);
    }
    console.log(`\n❌ Validation failed with ${errors.length} error(s).`);
    process.exit(1);
  }

  console.log("\n✅ Validation passed. Plugin structure is valid.");
}

await main();
