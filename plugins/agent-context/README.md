# Agent Context

Cursor plugin that auto-maintains a `.agent/` directory in your project for persistent context, progress tracking, and cross-model review.

## Components

| Type | Items |
|------|-------|
| Rules | `agent-context-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `sync-context`, `update-progress`, `cross-model-review` — auto-invoked or via `/skill-name` |
| Hooks | `sessionStart` — injects `.agent/` recovery reminder via `additional_context` |

## Local testing

```bash
./scripts/install-local.sh   # from repo root — copies to ~/.cursor/plugins/local/
```

Do **not** symlink from outside `~/.cursor/plugins/local/`; Cursor rejects it. Then **Developer: Reload Window**.

## Validation

From the repository root:

```bash
node scripts/validate-template.mjs
```
