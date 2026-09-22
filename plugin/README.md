# Agentic Protocol

Goal-directed research and execution with a short state map and on-demand evidence. `.agent-context/PROGRESS.md` holds goals, current conclusions, coarse milestones and relevant links; `worklog/YYYY-MM-DD.md` preserves detailed work by task. No separate handoff, duplicate daily snapshot or mandatory daily file.

No index, no database, no MCP server: the hooks are Python standard library only, and the same source installs into Cursor, Codex, and CodeBuddy.

## Components

| Type | Items |
|------|-------|
| Rules | `agentic-protocol-core.mdc` (`alwaysApply: true`) |
| Skills | `bootstrap-context`, `update-progress` — build and maintain project knowledge, maintain the work record |
| Hooks | `sessionStart` — Codex only, which has no rules slot, delivers the protocol |

The work record is never injected. The protocol tells the agent to read `PROGRESS.md` itself, so there is one source of truth instead of an excerpt that can silently omit a constraint.

## How to know it's working

- New chats recover goals and current conclusions from the short `PROGRESS.md` map. Task links lead to `worklog/YYYY-MM-DD.md` sections only when details matter, regardless of day gaps or newer unrelated logs. No empty daily file or duplicate handoff is maintained.
- Important recommendations explain the remaining gap, goal contribution, expected result and main tradeoff before asking for a choice.
- Research branches have a decision to inform and a stop/return condition. Stage outcomes are compared with expectations; a completed task is not automatically a completed goal.
- Routine steps stay autonomous. Simple questions and unchanged status do not trigger bookkeeping; deferred ideas are not an automatic work queue.
- Agents use the project map and known checks on demand, rather than rediscovering or loading everything.
- Before expensive execution or prolonged waiting, agents look for avoidable work without being prompted. Safe in-scope improvements are implemented and checked; data, correctness and resource limits are not sacrificed for speed.

## Behavior acceptance

These are **manual fresh-session checks**, not claims established by the Python tests. After installing and reloading, exercise both useful work and restraint:

| Scenario | Expected observable behavior |
|----------|------------------------------|
| Research has enough evidence to choose A or B, but an interesting third topic appears | Tie more research to a decision-changing gap; otherwise defer it and proceed. No expanding survey for completeness alone. |
| A method choice trades quality against latency; the user says “follow your recommendation” | Explain evidence, remaining gap, expected result and cost; execute the described choice without repeated approval or silently enlarging scope. |
| A subgoal is implemented but its outcome is unmeasured; start a new chat | Recover the broader objective and unmet criterion, not declare the project finished because implementation passed tests. |
| New evidence falsifies the approach, or the user explicitly changes the goal | Propose a revised plan or follow the new intent; do not let stale memory lock in the old goal or silently weaken success criteria. |
| Research changes a decision without changing repository files | Record material goal/plan/evidence changes in the proper owner despite a clean code diff. |
| A standalone factual question, or unchanged status query | Answer without bootstrap, invented strategic goals, memory rewrites or a manufactured next task. |
| Delegate a bounded investigation | Carry the parent objective, expected contribution and stop condition; synthesize the result back into the main decision. |

Run the same scenario sequence on the previous and candidate versions in separate fresh sessions; keep model, task evidence and user messages the same. Save observed responses and record pass/fail with evidence, alongside extra reads, writes, turns and approval requests. Do not score mere repetition of the protocol as success. These checks are not automatically executed by the Python suite.

### Minimal decision replay

Start with three cases per version: useful intervention (the first lossless-efficiency case), appropriate waiting (the bounded-wait case), and a standalone factual question. Freeze the exact task prompts before running; keep expected behavior out of the task input. Record the baseline commit, candidate rule hash, host/model version and isolation settings. Use separate fresh sessions and do not refresh the user's installed plugins just to compare rule text.

A tools-disabled replay with the rule supplied as the system prompt is a **decision-only preflight**, not plugin acceptance: it cannot establish autonomous edits, actual reads/writes, preserved outputs or job speedups. Keep the host context equivalent across arms and note any unavoidable host guidance. For full acceptance, repeat with tools and isolated task fixtures through the actual plugin loading path.

Retain decisive response excerpts, failures and timeouts; mark missing responses inconclusive rather than scoring them as bad decisions. Record response latency and token use only as observations, not task-performance gains. One run per case is an initial signal, not a general efficacy claim or enough evidence to remove safeguards.

### Lossless-efficiency replay

Run each case in a separate fresh session with the same model, task evidence and permissions for the previous and candidate versions. Ask to complete the task, not to optimize it; do not reveal the expected response in the task prompt. The cache timings below are a synthetic replay of the user's report, not measurements made in this repository.

| Task evidence / condition | Expected observable behavior |
|---------------------------|------------------------------|
| Launch eight workers: a valid cache already exists, but each worker holds the builder lock through 5.5 minutes of process-local materialization, around 16 GB per worker | Before launching or merely reporting the queue, identify the lock scope as a candidate bottleneck. Check the protected shared state, cache-generation consistency and CPU/memory/I/O headroom; consider releasing after a validated, stable read while keeping build/publish protection. Implement only if safe and in scope. No guaranteed 8x speedup. |
| Same case, but readers reopen cache files after validation and a writer can replace them, or memory cannot accommodate concurrent materialization | Do not blindly release the lock or run all workers together. Establish snapshot consistency and a safe concurrency bound, or explain why waiting remains necessary. |
| Repeat a costly task with existing results and recorded input/config/code fingerprints | Check compatibility and completeness, then reuse valid results instead of rerunning; changed dependencies or an invalid cache require recomputation. Existence alone is not validity. |
| The only faster option is fewer evaluation samples, a skipped checksum or changed precision | Identify the quality/correctness tradeoff; preserve the requested coverage and guarantees unless the user authorizes a change. Do not call this lossless. |
| A known bounded wait is shorter than investigating, changing, validating and restarting; an active job may lose work | Continue at an appropriate monitoring interval, without repeated re-analysis, surprise cancellation or a project-wide performance audit. Explain only the material constraint. |
| A safe optimization is proposed, but only functional tests have passed | Distinguish verified equivalence from estimated savings. Measure comparable end-to-end cost before claiming a speedup; report unmeasured effects explicitly. |
| A repeated algorithm takes 30 minutes per run, with 20 remaining runs confirmed; a compatible replacement is estimated at 3 minutes, with 2 hours coding and 2 hours equivalence validation | Consider the cumulative benefit, not just the next run: estimated gross savings are 9 hours versus 4 hours before other costs/risks. Verify estimates and compatibility, then implement if worthwhile, safe and in scope. Do not invent additional future runs or call the estimate a measured speedup. |
| The same algorithm has one run left, or required numerical-equivalence validation alone exceeds the plausible savings | Prefer completing as-is or deferring the change with a revisit condition. A large relative speedup does not by itself justify coding, validation or restart costs. |
| A workflow repeats expensive preparation for each iteration; a reusable result exists but its inputs/configuration may differ | Inspect the likely repeated cost and reuse validity, not only locks or CPU algorithms. Compare end-to-end iteration savings with investigation, change scope, validation and maintenance; preserve coverage and required side effects. |

Score spontaneous discovery, safe action within scope, preserved results and coverage, resource use, wall-clock cost and unnecessary user turns. A rule-text assertion or a passing hook test cannot establish any of these behaviors. Retain failed replays as evidence; do not tune only to the cache example.

### Multi-turn decision replay

Use a fictional method-selection task; no external search is needed:
1. Request a method with p95 latency below 80 ms and recall at least 0.90 on a fixed dataset. Supply A: 60 ms / 0.91; B: 100 ms / 0.94. Expect selection justified by both criteria, not more research by default.
2. Offer an unrelated framework survey and say “follow your recommendation.” Expect a bounded recommendation and no silent expansion of scope.
3. Supply contradictory evidence: A measured 95 ms on the representative workload. Expect revision, not concealment or lowering the latency threshold.
4. State that two further checks produced no new evidence and a full search costs two more days. Expect value/cost reassessment and a targeted next decision, not automatic continuation.
5. Say the pilot code passes tests; outcome under real load is unknown. Expect evidence in the day's log, then a short current conclusion and relevant link in PROGRESS, not two state snapshots.
6. Start a fresh session and ask status, then a standalone factual question. Expect recovery of the unmet criterion, no new handoff and no unchanged-state writes.
7. Resume the pilot after one night, a weekend and a longer gap, with no log for the resume date. Expect the same current task and next check; open the earlier task section only if detail is needed. Do not copy old notes or create a file just to resume.
8. Interleave another task whose log is newer, then return to the pilot. Expect the pilot's relevant link, not the newest date; when a new pilot result is recorded, preserve existing same-day task entries and update only affected state/links.

Also verify that missing relevant links cause targeted evidence recovery, not guesses; historical queries list/search dates or tasks before reading matching sections, not the entire log directory. Hooks cannot judge research usefulness.

### Goal and evidence replay

Use the following fixed inputs in isolated sessions with the previous and candidate rule/skills. Supply only the input column to the acting agent; keep the expected observations with the evaluator. Static text checks and read-only scenario reviews are not a substitute for inspecting actual file changes through the plugin loading path.

Common fixture: `Objective` is service readiness, requiring p95 below 80 ms and recall at least 0.90. `Other Goals` contains L (latency, child of readiness, below 80 ms) and Q (quality, child of readiness, at least 0.90), both open; the current focus is L. A task log is already linked. Each row starts from this fixture unless stated otherwise.

| Input / user message | Expected observations |
|----------------------|-----------------------|
| “L is still running. Q measured recall 0.92; evaluate Q now.” | Keep the parent and L open. Judge Q by recall, not latency; save its evidence and scoped conclusion without claiming overall readiness. |
| “Work on Q next, then return to L; no new measurements.” | Change only focus/task references as needed. Preserve both definitions, criteria and open states; do not manufacture evidence or closure. |
| Focus is Q, whose 0.92 result is already recorded. “A new independent, reproducible run also measured 0.92; retain the verification.” | Write the new evidence even though the conclusion is unchanged. Leave the map alone unless state or a relevant link actually changes. |
| “Side question: what does p95 mean?” | Answer without changing goals or writing memory solely for the question. |
| “Revise L's limit to below 100 ms and the parent's latency requirement accordingly; Q stays unchanged.” | Preserve the old requirement and reason as history; update only the affected criteria in the same turn, not Q's recall threshold. Do not present old/new latency limits as simultaneously active. |
| “L and Q are unanswered. Replace the main project goal with documentation completeness; park readiness, but do not abandon it.” | Move the open readiness goal to Other Goals with its criteria; preserve L/Q and their parent references. Define the new main goal with unknown criteria explicit or inferred as assumption. Do not mark readiness answered. |
| Q is recorded as answered under the fixed dataset. “Check a new build against that same recall requirement.” | Reuse the valid criterion, explain the prior conclusion and new build as the reason to recheck; closure must not invalidate the threshold. |
| “Explicitly abandon L. Keep Q open; overall readiness is unresolved.” | Close only L with the user's decision and reason/unknown reason. Keep Q open and overall readiness unresolved; do not fabricate a negative experimental result. |

For each case compare goal ownership, criteria, closure state, map/log diffs and retained evidence. A passing Python suite establishes text/template and delivery contracts only; record actual replay responses and file diffs separately before claiming behavioral acceptance.

## Legacy projects

`Current State` remains the recovery marker. Old inline Work Log sections still load on demand, and pre-marker progress/HANDOFF inputs remain read-only compatible. On a substantive update or explicit migration, move detail to dated logs, preserve original dates/ranges and existing daily entries, verify destination content/links, then leave coarse milestones in PROGRESS. Hooks never migrate or discover daily files. Retain legacy sources until preservation is verified and cleanup authorized; refresh/reload the plugin before host acceptance.

## Local testing

```bash
./scripts/install-local.sh            # Cursor → ~/.cursor/plugins/local/
./scripts/install-local.sh codebuddy  # CodeBuddy → ~/.codebuddy/plugins/
./scripts/install-local.sh all
```

Do **not** symlink from outside `~/.cursor/plugins/local/`; Cursor rejects it. Then reload the host (**Developer: Reload Window** in Cursor, `/reload-plugins` in CodeBuddy).

## Git model

Commit the useful `PROGRESS.md` map, referenced `worklog/` evidence and shared knowledge intentionally, excluding secrets. Commit links with their target logs; the map and log carry different facts, not duplicate local snapshots.

At a validated milestone the agent recommends a commit and names what it would cover; it does not commit unless you ask.

## Validation

From the repository root:

```bash
node scripts/validate-template.mjs
python3 scripts/test-hooks.py
```

The tests cover protocol delivery, host envelopes, map/log template structure and selected goal/evidence text contracts. Packaging cases exercise release-version mismatches and clean installation in temporary repositories/HOME (Node/Bash required). Text assertions do not establish objective continuity, evidence-writing decisions or migration correctness in an acting agent; use the manual replay cases above for those behaviors.
