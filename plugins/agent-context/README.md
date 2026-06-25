# Agent Context

Cursor plugin that auto-maintains a `.agent/` directory in your project for persistent context, progress tracking, and cross-model review.

## Components

| Type | Items |
|------|-------|
| Rules | `agent-context-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `sync-context`, `update-progress`, `cross-model-review` |
| Commands | `/bootstrap-context`, `/sync-context`, `/status`, `/update-progress`, `/cross-model-review` |
| Hooks | `sessionStart` — injects `.agent/` recovery reminder via `additional_context` |

## Local testing

```bash
ln -sf "$(pwd)" ~/.cursor/plugins/local/agent-context
# or copy: cp -r plugins/agent-context ~/.cursor/plugins/local/agent-context
```

Then **Developer: Reload Window** in Cursor.

## Validation

From the repository root:

```bash
node scripts/validate-template.mjs
```
