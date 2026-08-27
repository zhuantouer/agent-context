# Agent Handoff

## Current Task
Stop the protocol from producing spot-only fixes: make the defect class, not the reported location, the default fix scope.

## Status
Done. `Safety` now opens with a same-defect sweep requirement (sibling call sites, parallel modules, other UI surfaces, each supported host) that must run before a fix is called done, repairs same-root-cause instances that are equally safe to verify, and lists the rest with locations instead of silently leaving them. The surgical-edit clause still applies, but now traces changed lines to the request, that sweep, or resulting cleanup, and "unrelated" means a different root cause.

## Next Action
Reload Cursor (Developer → Reload Window), then in a fresh session point at one instance of a bug that exists in several places and check whether the reply lists the other occurrences without being asked.

## Touched Files
- `plugins/agent-context/rules/agent-context-core.mdc` — replaced the single surgical-edit line with the sweep clause plus a re-scoped surgical clause
- `.agent-context/MEMORY.md` — recorded the fix-scope decision
- `.agent-context/PROGRESS.md` — recorded completion and freshness
- `.agent-context/HANDOFF.md` — this snapshot

## Validation
- `node scripts/validate-template.mjs` — passed
- `./scripts/install-local.sh cursor` — installed to `~/.cursor/plugins/local/agent-context`
- Rule body size: 3849 → 4242 chars (+393, ~98 tokens by the chars/4 estimate; not tokenizer-measured)
- Still needed: Cursor window reload and the fresh-session behavior check above

## Source Freshness
Verified against the working tree on 2026-08-27.

## Blockers
None.

## User Instructions
When fixing a bug, do not stop at the place the user pointed to; the same problem often lives in other modules or UI surfaces and should be found without being asked.

## Notes for Next Agent
Codex was not reinstalled in this task. The 2026-08-05 open question in `MEMORY.md` applies here too: this is prose guidance, so its effect is assumed, not measured — if fresh sessions still report only the spot they were given, the sweep needs a hook-side signal rather than more wording.
