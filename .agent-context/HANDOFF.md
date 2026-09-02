# Agent Handoff

## Current Task
Fix the user-reported terminology defect ("金标" for "ground truth"), then get this session's uncommitted rule work reviewed and committed.

## Status
Fixed. The cause was a literal instruction, `translate borrowed terminology into the current project's terms`, added 2026-08-25 and still shipped by `HEAD` (`4429f3f`); the uncommitted 08-27 compression had removed the push but left no counterweight, because the correctness-preservation list omits terminology while protecting paths, commands, units, and error text. `Response Style` now says to write each term the way its field does and to gloss rather than replace an unfamiliar one. A preservation-list entry was considered and rejected: it can require a term to survive but not name the form, and field usage decides (召回率 for recall, "ground truth" untranslated). Body 4309 chars. The user chose to review the diff before committing, so the fix currently lives only in the worktree and the installed copy.

## Earlier This Session
Cost axis audited and the asymmetry closed. Nothing in the plugin measured imposed work — both stop signals push toward more of it, the size lines measure resident context — so the validator's clause-audit prompt now also asks whether each clause names a condition that turns it off on trivial work. 12 of 16 clauses already carried an off-switch; the two that did not were introduced hours earlier and are re-scoped: the bug loop applies to a behavior bug, and `Evidence` bounds reading to the sampled list or section rather than "every source you cite to its end". Body 4239 chars.

## Earlier This Session
Done, unverified in a live session. Six stale restatements of the write triggers were repaired in `handoff/SKILL.md` (description + body), `update-progress/SKILL.md` (3 lines), `COMMANDS.md`, and `README.md`; two carried the `touched files` field retired on 2026-08-27, so that defect class had survived its own sweep. `handoff/SKILL.md` now defers to the `Ownership` table instead of keeping a competing list, and `test_retired_handoff_field_stays_retired` guards the retired field. The user approved all four wording changes: the bug loop is unconditional with an explicit unsafe/impossible escape, `Evidence` asks to read cited sources to the end and search the full claimed scope, and `Ownership` requires a fact that outlives the turn and is not already carried, with every file stated as optional.

## Next Action
Review `git diff` and commit; `HEAD` still ships the terminology-translation instruction, so any `git checkout` of the rule reverts the fix. Then reload Cursor and run two contrasting tasks in one fresh session: a real behavior bug, which must show a reproduction before the edit and the same check rerun after, and a trivial text fix, which must show none of that overhead.

## Blockers
None blocking work, but the fix is unprotected until committed: 14 modified files plus untracked `scripts/test-hooks.py` carry the 08-27 audit and the 09-01/09-02 rounds.

## Validation
- `python3 scripts/test-hooks.py` — 21 passed (was 20; +1 invariant)
- New invariant negative-tested both ways: reintroducing the retired field as a handoff component fails with an exact line number; the clause forbidding it still passes
- `node scripts/validate-template.mjs` passes; rule body 4239 chars, past the 4200 review line by recorded decision; the prompt's new cost question was answered rather than ignored — no clause is left with unbounded cost
- Full-scope grep confirms no stale copies of the retired phrasings
- `diff -r` confirms the installed plugin is byte-identical to source
- Not run: any real Cursor session, so capsule injection and both halves of the balance remain unverified in practice. Codex still not installed

## User Instructions
Replies must carry recommendations, not just conclusions. Judge the design as a whole rather than patching rules line by line. When a reviewer disagrees, say which points are accepted, which are rejected with reasons, and which need the user's decision. The goal is the capability, not the budget — do not let a size limit block protocol work.

## Notes for Next Agent
Diagnose an output-behavior complaint against `HEAD`, the worktree, and the installed copy, not just the file you can read. The terminology defect was caused by an instruction the worktree no longer contained, and reading the current rule alone would have exonerated it. This repo keeps large uncommitted rule edits for days, so the three copies routinely disagree.

Deleting a clause that pushed a behavior does not oppose that behavior. The 08-27 compression removed "translate borrowed terminology" and left terminology as the only correctness-relevant token type missing from the preservation list, so the behavior had nothing working against it.

The protocol has two halves and only one of them was ever instrumented. Every mechanism here either adds work (the two stop signals) or measures resident context (the two size lines); none measured the work the protocol imposes, while the admission gate was simultaneously broadened to let clauses in more easily. When adding a clause, state its cost on the cheapest task that triggers it, and give it a condition an outside reader could use to switch it off.

Replacing a vague hedge with no condition is not the same as replacing it with a checkable one. That mistake was made and corrected inside one session: "when feasible and proportionate" became unconditional, which is why a doc typo would have demanded a reproduction.

The recurring defect class in this repo is protocol wording restated outside the protocol: skill descriptions, `README.md`, and `COMMANDS.md` each keep their own copy, and they are not swept when the protocol changes. It has now recurred three times. When you change a clause, grep the old wording across the whole repo before calling the edit done, and prefer pointing at the `Ownership` table over restating it.

The four clauses changed this round all shared one flaw: they asked the agent to grade its own judgment ("likely to help", "all relevant evidence", "when feasible"). That is graded leniently under context pressure — the same reason the compaction rule failed. Prefer a condition an outside reader could check.

The optional-quality-layer split was asked again and deferred again on 2026-09-01, this time deliberately: the per-clause off-switches added the same day may already remove the overhead the split was meant to remove, so the contrast test in `Next Action` is what unblocks the decision. Do not reopen it without those two runs.

Still waiting on the user: whether `MEMORY.md` (~37KB) should move old decisions into a rationale appendix.
