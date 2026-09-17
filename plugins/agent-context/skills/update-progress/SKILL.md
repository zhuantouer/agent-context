---
name: update-progress
description: Maintains a short PROGRESS.md map and on-demand work logs for meaningful results, status or legacy migration.
---

# Update Progress

Follow the protocol's write triggers: one current-state map, separate historical evidence; no duplicate task state.

## Instructions

1. Answer unchanged status from context without writes. Read only needed files/sections. Read existing content before editing; preserve manual additions.
2. Log meaningful work, experiments, decisions and failures in `worklog/YYYY-MM-DD.md` first. Update `PROGRESS.md` only for changed goal, current conclusion/gap, next check, milestone or relevant evidence link; more evidence alone need not change the map.
3. Derive goals from user intent; mark assumptions and retain goals across task completion. Connect gap/hypothesis → useful check → expected evidence → decision. No mandatory per-action form or goal tree.
4. Compare actual/expected evidence; passing tests do not prove user outcomes. Retain decisive validation, limits and blockers in current conclusions; link log details.
5. Briefly report conclusion/gap; recommend a useful next step only if one exists. No handoff document, daily rollover or automatic backlog execution.

## Progress template

Keep English headings for hooks; use the project language for bodies. `Current State` marks the current format. Omit unused sections, not uncertainty.

```markdown
# Project Progress

## Objective
[User outcome/success evidence; mark assumed or unknown criteria.]

## Constraints
[Decision-relevant scope, non-goals, effort limits, user constraints; omit if none.]

## Current State
[As of date/revision: active tasks, conclusion, validation/gaps, blockers. Relevant links only, e.g. [pilot evidence](worklog/YYYY-MM-DD.md#pilot). "No active task" is valid.]

## Next Check
[Gap/hypothesis → action + expected evidence → decision/stop condition. Link prerequisites as needed; omit if no useful next step.]

## Milestones
- [Coarse outcome/date/evidence link. Consolidate older milestones; not every task/day/log.]

## Deferred
- [Opportunity/revisit condition; not approved work. Brief, link details; omit if empty.]
```

## Daily log template

Create logs only for meaningful work, dated by the user's local work date, not the next session. Keep continued work in its original file until a new result. Read existing daily content before appending; never overwrite other tasks.

```markdown
# Work Log — YYYY-MM-DD

## Pilot
[Purpose/task; prior-entry link only if needed.]
- Work and evidence: [result, decisive command/source/artifact, validation, limitations.]
- Conclusion: [expected vs actual; goal implication, including failed hypotheses.]
```

Use descriptive, stable headings, unique per same-day entry; preserve linked anchors. From PROGRESS: `worklog/YYYY-MM-DD.md#task`; between logs: `YYYY-MM-DD.md#task`. Verify file/heading targets before linking. Do not copy the full state map or every tool call into logs.

## Recovery and growth

- Resume from PROGRESS, not the calendar. Read logs only if the map is insufficient, following current-task links even across dates or past newer entries. Never auto-load yesterday/latest, create today's empty file or copy old notes into today.
- For unlinked history queries, list dates or search tasks in `worklog/`; read matching sections, not all logs. Recover and repair missing/broken links from relevant evidence; newer does not mean task-relevant.
- SessionStart carries only `Objective`, `Constraints`, `Current State`, `Next Check` and their link text. Milestones/logs are on demand. Over-budget sections are explicitly omitted; read their sources before dependent decisions. Never hide constraints to fit.
- Shorten PROGRESS by moving details to logs, removing obsolete task links and consolidating milestones. After material edits, verify the excerpt retains conclusions, decisive limits and relevant links; never hide constraints or raise caps to fit. No exhaustive log index. Read large logs by task section; no second archive hierarchy without need.
- Reusable commands/preferences/lessons belong in `COMMANDS.md`/`CONVENTIONS.md`/`MEMORY.md`, respectively; link rather than duplicate. Do not list touched files; Git does.

## Legacy migration

Only during substantive record updates or explicit migration requests:
1. Before the `Current State` format, reconcile progress and any `HANDOFF.md` by evidence, not mtime. Retain unknowns/conflicts; ask only if decision-relevant. Never re-merge current-format progress with stale handoff.
2. Move history to logs with original dates, outcomes and evidence. Missing/ambiguous dates or ranges: keep original labels in a clearly marked imported section under the migration date; never invent exact dates. Preserve existing daily entries; skip those already migrated.
3. Write and verify destination entries/links before removing source detail. Compare preserved entries/counts or exact text, then leave coarse milestones/current state in PROGRESS. Repeated migration must not duplicate work or erase user additions.
4. Delete legacy sources only after authorized cleanup and content preservation. Hooks never migrate, create logs or delete files. Keep cached legacy hook entries; no dual state writes for old plugins.
