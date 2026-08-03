# Project Memory

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-27 | Borrow Karpathy-inspired ideas selectively rather than copying the full guideline set. | agent-context should stay focused on durable project memory and lightweight operating protocol. |
| 2026-07-01 | Improve modular-design behavior via an objective signal loop + anti-over-split guard, not more prose or a new heavy skill. | Prose conventions are easily ignored under context pressure and self-assessment is lenient; a measurable stop-hook signal plus a pre-edit checkpoint is lighter and harder to skip. |

## Lessons Learned
| Date | Type | Lesson | Corrective Guidance |
|------|------|--------|---------------------|
| 2026-06-27 | Product guidance | User value is easier to perceive when README names observable success signals. | Prefer "How to know it's working" style signals over only describing internal files. |
| 2026-06-27 | Handoff design | Rigid Goal/Verify fields may become low-signal boilerplate. | Make next actions concrete and verifiable, preferably referencing `.agent/COMMANDS.md`, without adding extra template fields. |
# Project Memory

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-26 | Keep project memory in `.agent/` files | Persistent files are the plugin's core value: project understanding, accumulated experience, and lessons learned survive chat context loss. |
| 2026-06-26 | Remove cross-review from the plugin | Cross-review diluted the product direction; the plugin should stay small and focus on durable agent context. |
| 2026-06-26 | Expand the plugin from project memory to agent work habits | The user clarified that token savings are secondary; the plugin should make AI-assisted coding smoother, more efficient, more reliable, and easier to resume. |
| 2026-06-26 | Use `.agent/MEMORY.md` for long-term project memory | The file stores broader long-term memory, not only technical decisions. |
| 2026-06-26 | Keep always-applied rules minimal | The core rule is injected every session, so detailed templates belong in skills and only routing/recovery/safety guidance should stay always-on. |
| 2026-06-26 | Use single-owner memory routing | Each durable fact should have exactly one canonical `.agent/` file to avoid split writes and missed reads. |
| 2026-06-26 | Add a conservative `stop` handoff reminder | A lightweight stop hook can catch stale handoffs without forcing every completion through a heavy workflow. |
| 2026-06-26 | Trim confirmation guardrails to judgment risks | Cursor/tool approvals already cover many mechanical permissions, so the plugin should focus confirmation on ambiguous intent, architecture choices, core behavior, critical config, and destructive operations. |

## Lessons Learned
| Date | Type | Lesson | Corrective Guidance |
|------|------|--------|---------------------|
| 2026-06-26 | lesson | Cross-review is not part of the core product direction | Keep the plugin focused on helping agents understand projects and preserve hard-won context. |
| 2026-06-26 | lesson | New-chat continuity needs an active handoff, not only project progress | Use `PROGRESS.md` for project state and `HANDOFF.md` for next action, touched files, validation, blockers, and user instructions. |
| 2026-06-26 | lesson | File names shape agent behavior | Use broad names like `MEMORY.md` when a file stores decisions, lessons, failures, and corrections. |
| 2026-06-26 | failure | Plugin changes are not active until the local plugin is reinstalled and Cursor reloads | After editing plugin files, run `./scripts/install-local.sh`, reload Cursor, and verify the installed copy if behavior matters. |
| 2026-06-26 | lesson | Long-lived `.agent/` files need compaction | Summarize old progress and repeated lessons instead of allowing context files to grow forever. |
| 2026-06-26 | lesson | End-of-session handoff reminders should be conditional | Trigger reminders only when changed files look newer than `HANDOFF.md`, fail open, and cap follow-up loops. |
| 2026-06-26 | failure | Adding a new hook script also requires updating the local install script | Ensure `scripts/install-local.sh` marks all installed hook scripts executable, not only the original session-start script. |
| 2026-06-26 | failure | Stop hooks must respect turn status | Only emit `followup_message` for `status: "completed"`; return `{}` for aborted/error turns so user cancellations are not overridden. |
