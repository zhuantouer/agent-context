---
name: update-progress
description: Update .agent/PROGRESS.md with current task status. Use after completing a task, starting a new task, or when the user asks for a status check.
---

# Update Progress

## When to use

- After completing a task or milestone
- When starting a new task
- When the user asks "what's the status?" or "where are we?"
- User runs `/update-progress`

## Instructions

### Step 1: Read current state

Read `.agent/PROGRESS.md` to see current state.

### Step 2: Determine updates needed

Ask yourself:
- Did I just complete something? → Move from In Progress to Completed.
- Am I starting something new? → Add to In Progress, set as Current Focus.
- Did I discover a new task? → Add to Backlog.
- Am I blocked on something? → Add/update Blockers.
- Did I resolve a blocker? → Remove from Blockers.

### Step 3: Update PROGRESS.md

Rewrite `.agent/PROGRESS.md` with updated content following the standard format:

```markdown
# Project Progress

## Current Focus
[The one thing you're working on right now]

## Completed
- [x] (YYYY-MM-DD) Task — brief description

## In Progress
- [ ] Task — current status

## Backlog
- [ ] Task — description

## Blockers
- (none, or description)
```

### Step 4: Report to user

Tell the user:
- What was just completed (if applicable)
- What's currently in progress
- What's blocked (if anything)
- What's next in the backlog

### Important

- **Use real dates** — get the current date from the system.
- **Keep descriptions concise** — one line per item.
- **Be honest about blockers** — don't hide problems.
- **Current Focus should be singular** — one thing at a time.
- **Don't delete completed items** — they're a record of progress.
