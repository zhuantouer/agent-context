---
name: update-progress
description: Update .agent/PROGRESS.md with current task status after completing work or when the user asks for status.
---

Run the update-progress skill to refresh `.agent/PROGRESS.md`:
- Move completed items to Completed with today's date
- Update Current Focus and In Progress
- Add newly discovered tasks to Backlog
- Record or clear Blockers

Then summarize current focus, recent completions, blockers, and next backlog items for the user.

If `.agent/PROGRESS.md` does not exist, run `/bootstrap-context` first.
