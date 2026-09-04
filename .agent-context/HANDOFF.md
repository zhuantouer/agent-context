# Agent Handoff

## Current Task
Adapt `agent-context` for CodeBuddy as a third host of the same plugin package.

## Status
Done in the worktree and installed: `codebuddy plugin install agent-context@agent-context-marketplace` succeeded, `codebuddy plugin validate` passed after `skills` was changed to `["./skills/"]`. Live CodeBuddy session still unverified — no session has confirmed that plugin `rules/*.mdc` injects, or that Stop payload shape matches the skip logic.

## Next Action
In CodeBuddy, run `/reload-plugins` (or restart the IDE). Ask a fresh session which file owns validation commands — it must answer `COMMANDS.md` without reading a file if the rule loaded. If it cannot, the flat `.mdc` may not be discovered and the Codex-style SessionStart injection becomes the fallback to discuss.

## Validation
- Last run: `node scripts/validate-template.mjs` — passed (rule-size warning at 4235 chars, expected). `python3 scripts/test-hooks.py` — 32 passed. `codebuddy plugin validate ./plugins/agent-context` — passed. `./scripts/install-local.sh codebuddy` — marketplace added, plugin installed.
- Still needed: a live CodeBuddy session (rule injection + stop signal).
- Source checked: CodeBuddy docs (Rules page, plugin reference, marketplace, directory structure, IDE 4.5.0/4.7.2 release notes) on 2026-09-03; CLI validator vs published schema.

## Blockers
(none)

## User Instructions
Replies must carry recommendations, not just conclusions. Judge the design as a whole rather than patching rules line by line. When a reviewer disagrees, say which points are accepted, which are rejected with reasons, and which need the user's decision. The goal is the capability, not the budget — do not let a size limit block protocol work.

## Notes for Next Agent
CodeBuddy is hybrid: protocol via `rules/` like Cursor, hook JSON like Codex. Do not copy Codex's SessionStart protocol injection — that would double-load on IDE. `plugin.json` has no `rules` field; discovery is the `rules/` directory. `skills` must be an array (`["./skills/"]`); `hooks` stays a string to `./hooks/codebuddy-hooks.json`. Stop is `systemMessage`, never `decision: block`. Unverified: whether a flat `.mdc` loads, and whether IDE Stop sends `status` or `last_assistant_message`.
