---
name: sync-context
description: Update .agent/ context files after significant project changes. Use when new files/modules are added, dependencies change, or architecture shifts.
---

# Sync Project Context

## When to use

- After adding new modules, directories, or major files to the project
- After changing dependencies (package.json, requirements.txt, etc.)
- After refactoring that changes the project structure
- After discovering new commands or configuration needs
- User explicitly asks to sync/update context
- User runs `/sync-context`

## Instructions

### Step 1: Detect changes since last sync

Use the first approach that works for this repository:

1. **Git repo with history** — run one of:
   - `git diff --name-only HEAD` — changes since last commit (includes unstaged)
   - `git diff --name-only HEAD~5` — recent changes (only if `git rev-parse --verify HEAD~5` succeeds)
   - `git log --oneline -5 -- .agent/` — recent context file commits
2. **New or shallow git repo** — use `git status --porcelain` and `git diff --name-only` instead of `HEAD~5`
3. **Not a git repo** — compare `.agent/` file timestamps, re-read `package.json` / `pyproject.toml` / `Makefile` for dependency or script changes, and ask the user what changed if unclear

Do not fail the sync workflow when `HEAD~5` does not exist.

### Step 2: Update relevant .agent/ files

Only update the files that need updating — don't rewrite everything:

#### ARCHITECTURE.md
- Add new modules/directories discovered
- Update tech stack if new dependencies added
- Update entry points if changed
- Update data flow if architecture shifted

#### COMMANDS.md
- Add any new commands discovered or created
- Update existing commands if they changed
- Add new npm scripts / Makefile targets

#### CONFIG.md
- Add new environment variables
- Update API key locations if changed
- Add new external services

#### PROGRESS.md
- Ensure current focus reflects what's actually being worked on
- Move completed items, add new tasks discovered

#### DECISIONS.md
- Log any significant technical decisions made since last sync
- Add lessons learned from recent work

### Step 3: Report

Tell the user which `.agent/` files were updated and a 1-line summary of what changed in each.

### Important

- **Don't delete information** unless it's confirmed obsolete — prefer marking as deprecated with a note.
- **Don't overwrite user's manual additions** — merge, don't replace.
- **Keep updates surgical** — only touch what changed.
