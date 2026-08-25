# Agent Handoff

## Current Task
Make agent replies structured, plain, and concise across Cursor and Codex.

## Status
Done. The canonical protocol now includes a short `Response Style` section. It requires answer-first ordering, plain language, focused paragraphs, consistent finding structure, explicit uncertainty, and complete explanations when brevity risks correctness.

## Next Action
Reload Cursor (Developer → Reload Window), then ask a fresh session to explain a technical finding and check whether it follows conclusion, evidence, next-step order without unexplained terminology.

## Touched Files
- `plugins/agent-context/rules/agent-context-core.mdc` — added `Response Style`
- `.agent-context/MEMORY.md` — recorded the product decision
- `.agent-context/PROGRESS.md` — recorded completion and freshness
- `.agent-context/HANDOFF.md` — replaced stale task snapshot

## Validation
- `node scripts/validate-template.mjs` — passed
- `./scripts/install-local.sh cursor` — installed to `~/.cursor/plugins/local/agent-context`
- Still needed: Cursor window reload and a fresh-session behavior check

## Source Freshness
Verified against the working tree on 2026-08-25.

## Blockers
None.

## User Instructions
Prefer plain, structured replies. Do not remove uncertainty words when they carry real meaning, and do not copy unfamiliar terminology from another project without explaining it.

## Notes for Next Agent
The style rule is shared by both hosts through the canonical protocol. Codex was not reinstalled in this task.
