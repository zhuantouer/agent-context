# Agent Handoff

## Current Task
Add a milestone commit reminder to the operating protocol so progress stays traceable.

## Status
Committed and installed. `Execution` carries one clause: at a coherent, validated, working-state milestone, recommend a commit and name what it would cover; commit only when the user asks; raise it once per milestone. Both READMEs document it. Rule body 4235 → 4486. Behavior in a live session is unverified — no session has yet produced the reminder at a milestone.

## Next Action
Reload Cursor (Developer → Reload Window), then at the next validated milestone check that the reply recommends a commit and names its scope without being asked. If it does not, the clause is prose with no enforcing mechanism and belongs in the clause audit `node scripts/validate-template.mjs` prompts for.

## Validation
- Last run: `node scripts/validate-template.mjs` — passed, with the expected size warning (body 4486, past the advisory 4200 review line). `python3 scripts/test-hooks.py` — 32 passed. `./scripts/install-local.sh` — Cursor copy refreshed.
- Not covered: no test asserts the new clause; it is prose with no invariant, like the rest of `Execution`.

## Blockers
(none)

## User Instructions
Replies must carry recommendations, not just conclusions. Judge the design as a whole rather than patching rules line by line. When a reviewer disagrees, say which points are accepted, which are rejected with reasons, and which need the user's decision. The goal is the capability, not the budget — do not let a size limit block protocol work.

## Notes for Next Agent
The reminder deliberately lives in the rule, not the stop hook: `git status --porcelain` cannot judge "milestone", and a nudge on every dirty turn is the every-turn-notification class rejected 2026-08-27. Do not move it into a hook without new evidence. Also: `~/.cursor/plugins/local/agent-context/` is not evidence of what the repo ships — a two-part terminology clause recorded as shipped on 2026-09-02 existed only there, and the user had deleted it on purpose; both records are corrected.
