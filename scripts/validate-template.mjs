#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const errors = [];
const warnings = [];

// This soft line is a review trigger about instruction weight, not a spending cap
// and not the host limit below. The original 3600-char ceiling was justified on
// cost, and that premise does not hold: measured 2026-09-01, the body is 3566 chars
// (~890 tokens) — 0.45% of a 200k context window. What actually degrades as the
// file grows is instruction weight, and this project has recorded that failure
// twice (2026-07-01: prose conventions get ignored under context pressure;
// 2026-08-13: a clause that "read as coverage but caught nothing"). A char count is
// a crude proxy for that, so it warns rather than failing.
//
// Its value is the size the 2026-08-27 audit judged bloated (4242), rounded down.
// Crossing it means re-run the clause audit; size alone is too crude a proxy to
// block a capability the protocol genuinely needs. The audit asks about cost as
// well as value, because nothing else here does: both stop-hook signals push
// toward more work and this line measures resident context, not the work the
// protocol imposes. A clause with no off-switch for trivial tasks is the growth to
// cut first (2026-09-01). A previous second review line shared the 6000 value for
// unrelated reasons; it was removed so one number does not carry two meanings.
const ALWAYS_ON_SOFT_CHARS = 4200;

// Hard host limit, not a review proxy. CodeBuddy support reported on 2026-09-18
// that its rule-injection budget is 6000 characters and that an over-budget rule
// is dropped SILENTLY: the IDE still logs "Successfully loaded plugin rule",
// lists it as always-applied and enabled, yet the text never reaches the model.
// That failure cost a full debugging session, so it must fail the build.
//
// Measured over the WHOLE file, not just the body: the reported figure was not
// broken down into frontmatter vs body, and the file is the only figure that
// cannot understate the cost. If the real budget turns out to exclude
// frontmatter, this is conservative by ~90 chars; the reverse mistake is silent.
// Aggregate budgets across several rules and host wrapper overhead are unknown.
const HOST_INJECTION_LIMIT_CHARS = 6000;
// Editing margin: crossing this is not a defect, it means the next clause needs
// compression first. Without it the limit becomes a cliff reachable by one line.
const HOST_INJECTION_HEADROOM_CHARS = 5700;

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

const pluginVersions = new Map();

async function validateReleaseVersion(pluginDir, plugin, host) {
  const manifestPath = path.join(pluginDir, `.${host}-plugin`, "plugin.json");
  const manifest = await readJSON(manifestPath);
  if (!manifest) return;
  const source = path.relative(repoRoot, manifestPath);
  const version = manifest.version;
  if (typeof version !== "string" || !version.trim()) {
    addError(`${source}: plugin version must be a non-empty string`);
    return;
  }
  const expected = pluginVersions.get(plugin.name);
  if (expected && version !== expected.version) {
    addError(`Plugin '${plugin.name}' version mismatch: ${source} has ${version}; ${expected.source} has ${expected.version}`);
  } else if (!expected) {
    pluginVersions.set(plugin.name, { version, source });
  }
  if (plugin.version !== undefined && plugin.version !== version) {
    addError(`Plugin '${plugin.name}' version mismatch: ${host} marketplace entry has ${JSON.stringify(plugin.version)}; ${source} has ${version}`);
  }
}

// One marketplace.json per host, all with the same skeleton: name, plugins array,
// a source path per entry. Only four things differ, so they are data here rather
// than three copies of the same loop. Adding a host means one row, not a rewrite.
//
//   requireRelative — Codex and CodeBuddy resolve the path against the marketplace
//     root, so it must start with './'. Cursor accepts any resolvable path.
//   required — extra fields beyond name/source (Codex: policy + category, because
//     the desktop UI hides a plugin that is not installable; CodeBuddy: the
//     marketplace card needs a description).
//
// Source shape is shared: Codex nests it under source.path, the other two use a
// bare string. `source` is optional in the error text only because one host hides
// it one level deeper.
const MARKETPLACES = [
  {
    host: "cursor",
    file: ".cursor-plugin/marketplace.json",
    requireRelative: false,
    required: [],
    validate: validatePlugin,
  },
  {
    host: "codex",
    file: ".agents/plugins/marketplace.json",
    requireRelative: true,
    required: ["policy.installation", "policy.authentication", "category"],
    validate: validateCodexPlugin,
  },
  {
    host: "codebuddy",
    file: ".codebuddy-plugin/marketplace.json",
    requireRelative: true,
    required: ["description"],
    validate: validateCodebuddyPlugin,
  },
];

function getPath(object, dotted) {
  return dotted.split(".").reduce((node, key) => node?.[key], object);
}

async function validateMarketplace({ host, file, requireRelative, required, validate }) {
  const marketplacePath = path.join(repoRoot, file);
  const source = path.relative(repoRoot, marketplacePath);
  if (!(await pathExists(marketplacePath))) {
    addError(`${source} not found`);
    return;
  }

  const marketplace = await readJSON(marketplacePath);
  if (!marketplace) {
    addError(`${source} is invalid JSON`);
    return;
  }
  if (!marketplace.name) {
    addError(`${source}: missing 'name'`);
  }
  if (!Array.isArray(marketplace.plugins)) {
    addError(`${source}: missing or invalid 'plugins' array`);
    return;
  }

  for (const plugin of marketplace.plugins) {
    if (!plugin.name) {
      addError(`${source}: plugin entry missing 'name'`);
      continue;
    }

    const sourcePath = typeof plugin.source === "string" ? plugin.source : plugin.source?.path;
    if (typeof sourcePath !== "string") {
      addError(`${source}: plugin '${plugin.name}' missing 'source' (a path string, or an object with 'path')`);
      continue;
    }
    if (requireRelative && !sourcePath.startsWith("./")) {
      addError(`${source}: plugin '${plugin.name}' source must start with './'`);
    }

    const pluginDir = path.resolve(repoRoot, sourcePath);
    if (!(await pathExists(pluginDir))) {
      addError(`${source}: plugin '${plugin.name}' source path does not exist: ${sourcePath}`);
      continue;
    }

    for (const field of required) {
      if (!getPath(plugin, field)) {
        addError(`${source}: plugin '${plugin.name}' missing '${field}'`);
      }
    }

    await validate(pluginDir, plugin.name);
    await validateReleaseVersion(pluginDir, plugin, host);
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

  // A declared directory is not scanned recursively: 2026-09-18 host logs reported
  // "Plugin agentic-protocol: 0 skill(s)" for "skills": ["./skills/"], where each skill
  // lives in its own subdirectory with SKILL.md. Declare each SKILL.md file instead;
  // a directory entry silently yields no skills in the host UI.
  if (manifest.skills !== undefined) {
    const declared = Array.isArray(manifest.skills) ? manifest.skills : [manifest.skills];
    for (const entry of declared) {
      if (typeof entry !== "string" || !entry.endsWith("SKILL.md")) {
        addError(`CodeBuddy plugin '${pluginName}': 'skills' entries must name a SKILL.md file (a bare directory is not discovered); omit the field to use skills/ convention`);
      }
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
          const fileChars = content.length;
          if (fileChars > HOST_INJECTION_LIMIT_CHARS) {
            addError(
              `Rule '${file}': always-applied file is ${fileChars} chars, over the ${HOST_INJECTION_LIMIT_CHARS} host injection limit. CodeBuddy drops an over-budget rule silently while still reporting it as loaded and enabled, so the protocol would never reach the model. Compress wording or move on-demand detail into a skill; do not raise this limit to fit.`,
            );
          } else if (fileChars > HOST_INJECTION_HEADROOM_CHARS) {
            addWarning(
              `Rule '${file}': always-applied file is ${fileChars} chars, ${HOST_INJECTION_LIMIT_CHARS - fileChars} below the ${HOST_INJECTION_LIMIT_CHARS} host injection limit. Not a failure. Compress before adding clauses, because crossing the limit silently drops the whole rule.`,
            );
          }
          const bodyChars = ruleBody(content).length;
          if (bodyChars > ALWAYS_ON_SOFT_CHARS) {
            addWarning(
              `Rule '${file}': always-applied body is ${bodyChars} chars, past the ${ALWAYS_ON_SOFT_CHARS} review line. Not a failure. Re-run the clause audit: does each clause prevent a material observed or predictable failure, does anything duplicate a skill or the Project Memory table, and does each clause name a condition that turns it off on trivial work?`,
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

  await validateHostNeutrality(pluginDir, pluginName);
}

async function main() {
  console.log("Validating agentic-protocol plugin structure...\n");

  for (const marketplace of MARKETPLACES) {
    await validateMarketplace(marketplace);
  }

  // Check for logo
  const logoPath = path.join(repoRoot, "plugins", "agentic-protocol", "assets", "logo.svg");
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
