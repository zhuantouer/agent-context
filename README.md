# agent-context

A lightweight [Cursor plugin](https://cursor.com/cn/docs/plugins) that gives your AI coding agent **persistent project context** — without the manual overhead.

## What it solves

| Pain point | How agent-context fixes it |
|------------|---------------------------|
| API keys / config forgotten mid-session | `.agent/CONFIG.md` persists key locations, auto-loaded each session |
| Agent re-reads the entire codebase every time | `.agent/ARCHITECTURE.md` gives instant project map |
| Commands re-discovered through trial & error | `.agent/COMMANDS.md` caches all known commands |
| No idea what's done vs. what's left | `.agent/PROGRESS.md` tracks everything, auto-updated |
| Agent hallucinates or free-wheels | Built-in confirmation guardrails |
| Cross-model review is a manual copy-paste mess | `/cross-model-review` command automates the workflow |

## How it works

The plugin installs **rules**, **skills**, **commands**, and a **sessionStart hook** that make your AI agent self-manage a `.agent/` directory in your project:

```
.agent/
├── ARCHITECTURE.md   ← project structure, tech stack, entry points
├── COMMANDS.md       ← build, test, lint, deploy, data processing commands
├── CONFIG.md         ← API key locations, env setup (paths only, never values)
├── PROGRESS.md       ← task progress tracker (completed / in-progress / backlog)
└── DECISIONS.md      ← technical decisions log + lessons learned
```

**You don't maintain these files.** The agent does. The core rule (`agent-context-core.mdc`, `alwaysApply: true`) instructs the agent to:

1. **Bootstrap** `.agent/` on first run (or when you run `/bootstrap-context`)
2. **Recover context** at the start of every new session by reading `.agent/` files (reinforced by the `sessionStart` hook)
3. **Auto-update** context files as the project evolves
4. **Track progress** in `PROGRESS.md` after each task
5. **Confirm before** risky actions (core logic changes, deletions, new deps)
6. **Facilitate cross-model review** with a structured review package format

## Installation

### Option A: Local plugin (recommended for development)

Per [Cursor plugin docs](https://cursor.com/docs/plugins#test-plugins-locally), link or copy the plugin into `~/.cursor/plugins/local/`:

```bash
git clone https://github.com/yourusername/agent-context.git ~/workspace/agent-context
ln -sf ~/workspace/agent-context/plugins/agent-context ~/.cursor/plugins/local/agent-context
```

Then run **Developer: Reload Window** in Cursor. Verify under **Settings → Plugins → Installed**.

### Option B: Local marketplace

Add this repository as a local marketplace (`.cursor-plugin/marketplace.json` at repo root), then install `agent-context` from the marketplace UI or:

```
/add-plugin agent-context
```

### Option C: Cursor Marketplace

After publishing via [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish):

```
/add-plugin agent-context
```

## Commands

| Command | What it does |
|---------|-------------|
| `/bootstrap-context` | Scan project and generate `.agent/` context files |
| `/sync-context` | Detect project changes and update `.agent/` files |
| `/status` | Show current project progress summary |
| `/update-progress` | Refresh `.agent/PROGRESS.md` after completing work |
| `/cross-model-review` | Generate review package or process review feedback |

## Skills

Skills follow the [Agent Skills](https://cursor.com/cn/docs/skills) format (`skills/<name>/SKILL.md`). The agent invokes them automatically when relevant; `/cross-model-review` is explicit-only (`disable-model-invocation: true`) because the core rule already covers review triggers.

| Skill | Trigger |
|-------|---------|
| `bootstrap-context` | First run, or when `.agent/` is missing |
| `sync-context` | After significant project changes |
| `update-progress` | After completing a task |
| `cross-model-review` | Via `/cross-model-review` (explicit) |

## Rules

| Rule | Scope | Description |
|------|-------|-------------|
| `agent-context-core.mdc` | `alwaysApply: true` | Core operating protocol — context management, progress tracking, confirmation guardrails, anti-repetition, cross-model review workflow |

See [Cursor Rules docs](https://cursor.com/cn/docs/rules) for how `alwaysApply` rules are injected into every session.

## Hooks

The `sessionStart` hook emits JSON with `additional_context` (per [Cursor hooks](https://cursor.com/docs/hooks)) to remind the agent to read `.agent/PROGRESS.md`. It resolves the project path via `CURSOR_PROJECT_DIR`, not the plugin install directory.

## Development

Validate plugin structure:

```bash
node scripts/validate-template.mjs
```

## Philosophy

Inspired by [AgenticMetaEngineering](https://github.com/anthropic/AgenticMetaEngineering) and [Superpowers](https://github.com/obra/superpowers), but **radically simplified**:

- **No 8-stage workflow.** No gate audits. No mandatory worktrees.
- **No 20+ plugins.** One plugin, one rule file, four skills.
- **No per-requirement directory scaffolding.** Just `.agent/`.
- **The agent maintains the context, not you.** You just code.

The key insight from AME: **LLM context window is "working memory"; files are the "hard drive."** Move everything that needs to persist out of the conversation and into files. But unlike AME, we don't wrap that in a heavy process framework — just a lightweight rule that tells the agent to do it automatically.

## License

MIT
