# Agent Context

Cursor plugin that auto-maintains a `.agent/` directory in your project for persistent context, task handoff, project conventions, validation habits, and lessons learned.

## Components

| Type | Items |
|------|-------|
| Rules | `agent-context-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `sync-context`, `update-progress`, `handoff` — auto-invoked or via `/skill-name` |
| Hooks | `sessionStart` — injects `.agent/HANDOFF.md` summary when available; `stop` — gently reminds stale handoff refreshes |

## How to know it's working

- New chats resume from `.agent/HANDOFF.md` without repeated setup.
- Agents use `.agent/ARCHITECTURE.md` and `.agent/COMMANDS.md` instead of rediscovering project structure and checks.
- Handoffs include a concrete next action and the validation that should prove it worked.
- Diffs stay focused on the user request instead of collecting unrelated cleanup.

## Local testing

```bash
./scripts/install-local.sh   # from repo root — copies to ~/.cursor/plugins/local/
```

Do **not** symlink from outside `~/.cursor/plugins/local/`; Cursor rejects it. Then **Developer: Reload Window**.

## Git model

Commit shared `.agent/` knowledge files when useful, but treat `.agent/HANDOFF.md` as local working state by default unless a branch intentionally wants to share the handoff.

## Validation

From the repository root:

```bash
node scripts/validate-template.mjs
```
