---
name: bootstrap-context
description: Create concise .agent/ project memory for a repository. Use when .agent/ is missing, when the user asks to initialize or refresh context, or via /bootstrap-context.
---

# Bootstrap Project Context

## Use When

- Project root has no `.agent/`
- The user asks to initialize or refresh project context
- The user runs `/bootstrap-context`

## Instructions

1. If `.agent/` exists, read it and ask whether to refresh or keep it.
2. Scan only key project files; do not read the whole codebase.
3. Create or refresh the `.agent/` files below with concise facts.
4. Report detected stack, generated files, and gaps the user should review.
5. Tell the user: "From now on, I'll auto-maintain these files. You don't need to manage them manually."

## Scan Inputs

Read if present:

- `README.md`
- `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`
- `Makefile`, `justfile`
- `.env.example`, config templates
- `docker-compose.yml`, `Dockerfile`
- `.cursor/rules/*`
- `CLAUDE.md`, `AGENTS.md`

Prefer file-search tools, `rg`, or portable git commands such as `git ls-files`. Avoid broad scans and Unix-only `find ... | head ...` examples.

## Files

#### `.agent/HANDOFF.md`
```markdown
# Agent Handoff

## Current Task
Initial project context setup.

## Status
`.agent/` context files were generated for the project.

## Next Action
Review generated context files with the user and start the requested task.

## Touched Files
- `.agent/` — persistent project context

## Validation
- Last run: (none)
- Still needed: Run the project's recommended validation command once identified.

## Source Freshness
Initial context generated from key project files.

## Blockers
(none)

## User Instructions
(none)

## Notes for Next Agent
Read this file first, then `.agent/PROGRESS.md`. Load other `.agent/` files only when needed.
```

#### `.agent/ARCHITECTURE.md`
```markdown
# Project Architecture

## Overview
[1-2 sentence project description]

## Tech Stack
- Language: [from package.json/pyproject.toml/etc.]
- Framework: [if detected]
- Build tool: [if detected]
- Test framework: [if detected]

## Directory Structure
[Key directories and responsibilities]

## Entry Points
[Main files or commands]

## Key Modules
[Important modules and responsibilities]

## Data Flow
[If applicable]
```

#### `.agent/COMMANDS.md`
```markdown
# Project Commands

## Setup
- Install deps: [command or "(none detected)"]
- Activate env: [command or "(none detected)"]

## Development
- Start dev server: [command or "(none detected)"]
- Test: [command or "(none detected)"]
- Lint: [command or "(none detected)"]
- Type check: [command or "(none detected)"]

## Validation Profile
- Small docs/context edit: [recommended check and caveat]
- Code change: [recommended check and caveat]

## Build & Deploy
- Build: [command or "(none detected)"]
- Deploy: [command or "(none detected)"]

## Custom Scripts
[package.json scripts, Makefile targets, data jobs, etc.]

## Command Notes
- [Slow/flaky commands, environment gotchas, or "(none yet)"]
```

#### `.agent/CONFIG.md`
```markdown
# Project Configuration

## Environment Variables
- `[name]` — [purpose], [location]

## API Keys
[Where keys live; never values]

## External Services
[Services and purpose, or "(none detected)"]

## Local Setup
[Concise local setup notes]
```

#### `.agent/CONVENTIONS.md`
```markdown
# Project Conventions

## Coding Style
[Formatter, linter, naming, structure, abstraction preferences, or "(none recorded yet)"]

## User Preferences
[Durable communication or workflow preferences, or "(none recorded yet)"]

## Project Boundaries
[Files, modules, or behaviors that need extra care, or "(none recorded yet)"]

## Review and Validation Habits
[Preferred checks before claiming completion]

## Domain Vocabulary
[Stable project terms and meanings, or "(none recorded yet)"]
```

#### `.agent/PROGRESS.md`
```markdown
# Project Progress

## Current Focus
[Current project focus, or "Initial setup"]

## Completed
- [x] (YYYY-MM-DD) Project context initialized

## Older Milestones
(none)

## In Progress
(none)

## Backlog
(none)

## Blockers
(none)

## Context Freshness
- Last sync: YYYY-MM-DD
- Source revision: [git commit/branch if available, or "(unknown)"]
```

#### `.agent/MEMORY.md`
```markdown
# Project Memory

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

## Lessons Learned
| Date | Type | Lesson | Corrective Guidance |
|------|------|--------|---------------------|
| | | | |
```

## Rules

- Never store secret values.
- Use real dates from the system.
- If the project is minimal, still create the structure with concise "(none detected)" entries.
- Keep files useful for future agents, not comprehensive docs.
