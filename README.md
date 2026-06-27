# agent-context

A lightweight [Cursor plugin](https://cursor.com/cn/docs/plugins) that gives your AI coding agent **persistent project context, task handoff, and project-specific working habits** — without the manual overhead.

## What it solves

| Pain point | How agent-context fixes it |
|------------|---------------------------|
| API keys / config forgotten mid-session | `.agent/CONFIG.md` persists key locations, auto-loaded each session |
| Agent re-reads the entire codebase every time | `.agent/ARCHITECTURE.md` gives instant project map |
| Commands re-discovered through trial & error | `.agent/COMMANDS.md` caches commands plus the validation profile |
| No idea what's done vs. what's left | `.agent/PROGRESS.md` tracks everything, auto-updated |
| New chats lose the execution thread | `.agent/HANDOFF.md` captures current task, next action, touched files, validation, and blockers |
| Agent misses local project habits | `.agent/CONVENTIONS.md` stores style, workflow, boundaries, and user preferences |
| Agent hallucinates or free-wheels | Built-in confirmation guardrails |
| Hard-won lessons disappear after the chat | `.agent/MEMORY.md` captures project decisions, user corrections, failures, and mistakes to avoid |

## How it works

The plugin installs **rules**, **skills**, and lightweight hooks that make your AI agent self-manage a `.agent/` directory in your project:

```
.agent/
├── HANDOFF.md        ← active task state, next action, validation, blockers
├── PROGRESS.md       ← project progress tracker (completed / in-progress / backlog)
├── ARCHITECTURE.md   ← project structure, tech stack, entry points
├── COMMANDS.md       ← commands + validation profile
├── CONFIG.md         ← API key locations, env setup (paths only, never values)
├── CONVENTIONS.md    ← project habits, user preferences, boundaries
└── MEMORY.md         ← decisions, lessons, user corrections, and failures
```

Recommended git model:

- Commit shared knowledge files: `ARCHITECTURE.md`, `COMMANDS.md`, `CONFIG.md` (paths only, never values), `CONVENTIONS.md`, `MEMORY.md`, and usually `PROGRESS.md`.
- Treat `HANDOFF.md` as local working state by default. It changes often and can create noisy diffs or team conflicts.
- For teams, consider ignoring only the handoff file:

```gitignore
.agent/HANDOFF.md
```

If you want handoffs shared across a branch or PR, commit them intentionally.

**You don't maintain these files.** The agent does. The core rule (`agent-context-core.mdc`, `alwaysApply: true`) instructs the agent to:

1. **Bootstrap** `.agent/` on first run (or when you run `/bootstrap-context`)
2. **Resume from handoff** at the start of every new session, reinforced by the `sessionStart` hook
3. **Load context on demand** instead of dumping every reference file into the chat
4. **Auto-update** context files as the project evolves
5. **Track progress** in `PROGRESS.md` and active task state in `HANDOFF.md`
6. **Follow project conventions** captured in `CONVENTIONS.md`
7. **Use validation profiles** from `COMMANDS.md` before claiming work is done
8. **Confirm before** risky actions (core logic changes, deletions, new deps)
9. **Capture experience and failure lessons** so future agents avoid repeating mistakes

## How to know it's working

You should notice practical changes in agent behavior:

- New chats resume from `.agent/HANDOFF.md` without you re-explaining the task.
- Agents re-read less of the codebase because `.agent/ARCHITECTURE.md` points them to the right files.
- Validation happens more consistently because `.agent/COMMANDS.md` records the project's checks.
- Handoffs name a concrete next action plus the check that proves it worked.
- Lessons from mistakes show up in `.agent/MEMORY.md` instead of disappearing with the chat.
- Diffs stay focused because the core rule tells agents to keep edits tied to the user's request.

## Installation

### Option A: Local plugin (recommended for development)

Per [Cursor plugin docs](https://cursor.com/docs/plugins#test-plugins-locally), copy the plugin into `~/.cursor/plugins/local/`:

```bash
git clone https://github.com/yourusername/agent-context.git ~/workspace/agent-context
cd ~/workspace/agent-context
./scripts/install-local.sh
```

> **Important:** Cursor **rejects symlinks** to paths outside `~/.cursor/plugins/local/` for security. Do not use `ln -sf` to your workspace — the plugin will silently fail to load (`0 plugins loaded` in Cursor Plugins log). Re-run `./scripts/install-local.sh` after editing the plugin, then **Developer: Reload Window**.

Verify under **Settings → Plugins → Installed** (not the per-project Skills tab).

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

## Skills

Skills follow the [Agent Skills](https://cursor.com/cn/docs/skills) format (`skills/<name>/SKILL.md`). The agent invokes them automatically when relevant, or you can trigger them manually with `/skill-name` in chat.

| Skill | Auto trigger | Manual |
|-------|--------------|--------|
| `bootstrap-context` | First run, or when `.agent/` is missing | `/bootstrap-context` |
| `sync-context` | After significant project changes | `/sync-context` |
| `update-progress` | After completing a task; status queries | `/update-progress` |
| `handoff` | Before new chats, compaction, pauses, blockers, or after substantive edits/validation | `/handoff` |

## Rules

| Rule | Scope | Description |
|------|-------|-------------|
| `agent-context-core.mdc` | `alwaysApply: true` | Minimal operating protocol — recovery order, canonical file ownership, safety checks, and memory hygiene |

See [Cursor Rules docs](https://cursor.com/cn/docs/rules) for how `alwaysApply` rules are injected into every session.

## Hooks

- `sessionStart` emits JSON with `additional_context` (per [Cursor hooks](https://cursor.com/docs/hooks)). If `.agent/HANDOFF.md` exists, it injects a short handoff summary so the new chat can resume immediately. It resolves the project path via `CURSOR_PROJECT_DIR`, not the plugin install directory.
- `stop` runs a conservative handoff reminder after completed agent turns. It only asks the agent to refresh `.agent/HANDOFF.md` when the git worktree has changes that appear newer than the handoff. It skips aborted/error turns, fails open, and uses `loop_limit: 1` to avoid reminder loops.

## Development

Validate plugin structure:

```bash
node scripts/validate-template.mjs
```

Bootstrap avoids Unix-only scan commands in generated guidance. Prefer Cursor file tools, `rg`, or `git ls-files` so the workflow works across macOS, Linux, and Windows-style environments.

## Philosophy

Inspired by [AgenticMetaEngineering](https://github.com/anthropic/AgenticMetaEngineering) and [Superpowers](https://github.com/obra/superpowers), but **radically simplified**:

- **No 8-stage workflow.** No gate audits. No mandatory worktrees.
- **No 20+ plugins.** One plugin, one rule file, four skills.
- **No per-requirement directory scaffolding.** Just `.agent/`.
- **The agent maintains the context, not you.** You just code.

The key insight from AME: **LLM context window is "working memory"; files are the "hard drive."** Move everything that needs to persist out of the conversation and into files. But unlike AME, we don't wrap that in a heavy process framework — just a lightweight rule that tells the agent to do it automatically.

## License

MIT
