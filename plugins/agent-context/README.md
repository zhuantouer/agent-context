# Agent Context

Project memory in seven plain markdown files. The agent maintains a `.agent-context/` directory holding the current task handoff, progress ledger, project map, commands, config locations, conventions, and lessons learned.

No index, no database, no MCP server: the hooks are Python standard library only, and the same source installs into Cursor, Codex, and CodeBuddy.

## Components

| Type | Items |
|------|-------|
| Rules | `agent-context-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `sync-context`, `update-progress`, `handoff` — auto-invoked or via `/skill-name` |
| Hooks | `sessionStart` — injects `.agent-context/HANDOFF.md` summary when available; `stop` — gently reminds stale handoff refreshes |

## How to know it's working

- New chats resume from `.agent-context/HANDOFF.md` without repeated setup.
- Agents use `.agent-context/ARCHITECTURE.md` and `.agent-context/COMMANDS.md` instead of rediscovering project structure and checks.
- Handoffs include a concrete next action and the validation that should prove it worked.
- Diffs stay focused on the user request instead of collecting unrelated cleanup.

## Local testing

```bash
./scripts/install-local.sh            # Cursor → ~/.cursor/plugins/local/
./scripts/install-local.sh codebuddy  # CodeBuddy → ~/.codebuddy/plugins/
./scripts/install-local.sh all
```

Do **not** symlink from outside `~/.cursor/plugins/local/`; Cursor rejects it. Then reload the host (**Developer: Reload Window** in Cursor, `/reload-plugins` in CodeBuddy).

## Git model

Commit shared `.agent-context/` knowledge files when useful, but treat `.agent-context/HANDOFF.md` as local working state by default unless a branch intentionally wants to share the handoff.

At a validated milestone the agent recommends a commit and names what it would cover; it does not commit unless you ask.

## Validation

From the repository root:

```bash
node scripts/validate-template.mjs
```
