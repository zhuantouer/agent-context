---
name: update-progress
description: Maintain a short PROGRESS.md state map and on-demand worklog/YYYY-MM-DD.md evidence; use for meaningful results, status and legacy migration.
---

# Update Progress

Use the protocol's write triggers. Keep one current-state map and separate historical evidence, not two copies of task state.

## Instructions

1. Answer unchanged status from available context without writing. Read only files/sections needed for the update, and read existing content before editing. Preserve manual additions.
2. Save meaningful work, experiments, decisions and failed approaches in `worklog/YYYY-MM-DD.md` first. Then update `PROGRESS.md` only if the goal, current conclusion/gap, next check, milestone or relevant evidence link changed. More evidence alone need not rewrite the map.
3. Derive goals from user intent, label assumptions, and retain the goal across task completion. Connect the current gap/hypothesis → useful check → expected evidence → resulting decision; no mandatory per-action form or goal tree.
4. Compare actual with expected evidence; tests passing is not proof of the user outcome. Keep decisive validation, limitations and blockers in the current conclusion, with details linked from the log.
5. Briefly report the conclusion and remaining gap, with a next useful step if one exists. No handoff document, daily rollover or automatic backlog execution.

## Progress template

Keep these English headings for hook selection; write bodies in the project's language. Retain `Current State` as the current-format marker. Omit unused sections, not uncertainty.

```markdown
# Project Progress

## Objective
[User outcome and success evidence; label assumed or unknown criteria.]

## Constraints
[Decision-relevant scope, non-goals, effort limits and user constraints; omit if none.]

## Current State
[As of date/revision: active task(s), present conclusion, validation/gap and blockers. Include only relevant links, e.g. [pilot evidence](worklog/YYYY-MM-DD.md#pilot). "No active task" is valid.]

## Next Check
[Gap/hypothesis → action and expected evidence → decision/stop condition. Link prerequisite details if needed; omit when no useful next step remains.]

## Milestones
- [Coarse outcome and date, with an evidence link. Consolidate older milestones; not every task, day or log file.]

## Deferred
- [Worthwhile opportunity and revisit condition; not approved work. Keep brief, link detail. Omit if empty.]
```

## Daily log template

Create a dated file only when there is meaningful work to preserve. Use the user's local date of the work, not the date of the next session; continued work stays in its original file until there is a new result to record. Read an existing day's file before appending; never overwrite other tasks.

```markdown
# Work Log — YYYY-MM-DD

## Pilot
[Purpose/task; relevant prior entry link only if needed.]
- Work and evidence: [result, decisive command/source/artifact, validation and limitations.]
- Conclusion: [expected vs actual; implication for the goal, including a failed hypothesis.]
```

Use descriptive, stable task headings. Give separate same-day entries unique headings; retain linked anchors when editing. From PROGRESS link `worklog/YYYY-MM-DD.md#task`; between daily files link `YYYY-MM-DD.md#task`. Verify local file/heading targets before referencing them. Do not copy the entire current-state map or every tool call into a daily log.

## Recovery and growth

- Resume from PROGRESS regardless of calendar boundaries. If the map suffices, continue without opening a log. Otherwise follow the current task's relevant link, which may be older than the latest entry or span several dates. Never automatically load yesterday, select the newest file, create today's empty file, or copy old notes into today.
- For historical questions without a link, list dates or search the task in `worklog/`, then read matching sections; do not read every log. If a needed link is missing/broken, recover from relevant evidence and repair it rather than assuming a newer file belongs to the task.
- SessionStart carries only `Objective`, `Constraints`, `Current State` and `Next Check`, including links as text. Milestones/logs stay on demand. Over-budget sections are explicitly omitted; read the named source before a dependent decision, never hide a constraint to fit.
- Keep PROGRESS short by moving detail out, removing obsolete current-task links and consolidating old milestones. After material map edits, check that the current conclusion, decisive limits and relevant links survive the resume excerpt; move supporting detail to logs rather than hiding constraints or raising caps. No exhaustive log index. Large daily logs can be read by task section; do not impose a second archive hierarchy without need.
- Keep reusable commands, preferences and lessons in `COMMANDS.md`, `CONVENTIONS.md` and `MEMORY.md`. Link rather than duplicating owners. Do not list touched files; Git already carries that list.

## Legacy migration

Only during substantive record updates or an explicit migration request:
1. For pre-`Current State` records, reconcile old progress and `HANDOFF.md` if present using evidence, not mtime. Preserve unknowns/conflicts; ask only when they affect a decision. Already-current progress is not re-merged with stale handoff.
2. Move embedded work history into dated logs using recorded dates, preserving outcomes and evidence. For missing/ambiguous dates or date ranges, retain the original labels in a clearly marked imported section under the migration date; do not invent an exact occurrence date. Preserve existing daily content and skip already-migrated entries.
3. Write and verify the destination entries and links before removing source detail. Compare preserved entries/counts or exact text, then leave only coarse milestones and current state in PROGRESS. Repeat migration must not duplicate work or erase user additions.
4. Retain legacy source files unless cleanup is authorized and useful content is preserved. Hooks never migrate, create logs or delete files. Keep cached legacy hook entry points; no dual state writes for old plugins.
