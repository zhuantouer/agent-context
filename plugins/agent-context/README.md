# Agent Context

Cursor plugin that auto-maintains a `.agent/` directory in your project for persistent context, task handoff, project conventions, validation habits, and lessons learned.

## Components

| Type | Items |
|------|-------|
| Rules | `agent-context-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `sync-context`, `update-progress`, `handoff` — auto-invoked or via `/skill-name` |
| Hooks | `sessionStart` — injects `.agent/HANDOFF.md` summary when available; `stop` — gently reminds stale handoff refreshes |

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
