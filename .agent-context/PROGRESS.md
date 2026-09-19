# Project Progress

## Objective
Keep agent-assisted research and execution goal-directed across sessions. Success: understandable decisions, evidence-based conclusions and preserved work history without duplicate bookkeeping or routine full-history reads.

## Constraints
One current-state map; daily logs own detail. No separate handoff, automatic daily files or calendar-based resume. Preserve capability and decisive context. Do not auto-commit or refresh installed plugins; leave unrelated plugin caches untouched. Preferences: CONVENTIONS.md.

## Current State
2026-09-19: hooks reduced to Codex SessionStart (delivers the protocol); the Stop hook with its 600-line check and the `sync-context` skill are gone — knowledge files now belong to `bootstrap-context`, state files to `update-progress`. No host injects work-record content; the agent reads `PROGRESS.md` itself. Chinese rule canonical at ~3.3k chars (English 5977), no size warnings; the English fallback `.en.mdc.bak` was deleted 2026-09-19 on request (never committed, so not recoverable); rewritten as an executable method in 7 workflow-ordered sections. 30 tests pass (43 before StopSignal removal). [Plan A](worklog/2026-09-18.md#sessionstart-content-injection-removed-plan-a), [Method](worklog/2026-09-18.md#rule-rewritten-as-an-executable-working-method), [Slimming](worklog/2026-09-19.md#plugin-slimmed-to-one-hook-and-two-skills).

## Next Check
Commit the plan-A removal, Chinese rule switch and method rewrite, budget gate and discovery fix when authorized. After an authorized reload, probe a fresh chat without file reads for `# Agentic 方法论`: the budget check passing is necessary, not sufficient. Never raise the limit. Replay the Chinese rule — with the English fallback gone, any regression has to be fixed forward in the Chinese text.

## Milestones
- 2026-09-17 — Proactive-efficiency guidance added; recovery/packaging fixes validated. Decision-only replay remains preliminary. [Guidance](worklog/2026-09-17.md#proactive-lossless-efficiency), [review fixes](worklog/2026-09-17.md#review-follow-up).
- 2026-09-16 — State map plus dated evidence; no separate handoff or timestamp-driven bookkeeping. [Details](worklog/2026-09-16.md#daily-log-split).
- 2026-09-03 — Shared plugin supports Cursor, Codex and CodeBuddy; live host acceptance remains separate. [Evidence](worklog/2026-09-03.md#migrated-records).
- 2026-08-27 → 09-10 — Bounded recovery, proportional safeguards and milestone traceability; later design supersedes old snapshot mechanics. [Recovery](worklog/2026-08-27.md#migrated-records), [traceability](worklog/2026-09-10.md#migrated-records).
- 2026-06-26 → 08-03 — Plugin foundation, multi-host packaging and namespaced project memory. [Original date-range records](worklog/2026-09-16.md#imported-date-ranges).

## Deferred
Revisit host extensions, optional quality layers and historical-memory compaction only for a concrete need or measured failure. [Preserved opportunities and conditions](worklog/2026-09-16.md#deferred-opportunities).
- Renaming the plugin `agent-context`: rejected on 2026-08-03 because all eight candidates were taken by competitors, so it bought no discovery. The new argument is different — the rule's centre of gravity moved from memory to working method, so the name no longer matches. Revisit after the behavior replay confirms the positioning; check candidate availability on all three marketplaces first, since that is what killed the last attempt. `.agent-context/` keeps its name either way.
- Constraint check: the old `Current State` 800 / `Next Check` 400 caps died with plan A — `session-context.py` no longer reads `PROGRESS.md` at all (it injects the protocol for Codex only). Keep the map short because the rule asks for it, not because anything truncates it.
