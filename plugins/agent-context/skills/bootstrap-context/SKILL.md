---
name: bootstrap-context
description: Initialize .agent/ context directory for a new project. Run automatically on first interaction when .agent/ is missing, or manually via /bootstrap-context.
---

# Bootstrap Project Context

## When to use

- Project root does not have a `.agent/` directory
- User explicitly asks to initialize or refresh project context
- User runs `/bootstrap-context`

## Instructions

### Step 1: Detect existing context

Check if `.agent/` exists in project root. If it does, read all files and ask the user whether they want to refresh or keep existing context.

### Step 2: Scan project structure

Read these files if they exist (do NOT read every file — only the key entry points):

- `README.md` — project description, setup instructions
- `package.json` / `pyproject.toml` / `requirements.txt` / `Cargo.toml` / `go.mod` — dependencies, scripts, metadata
- `Makefile` / `justfile` — task runners
- `.env.example` / config templates — environment variables needed
- `docker-compose.yml` / `Dockerfile` — containerization setup
- `.cursor/rules/*` — existing Cursor rules
- Any `CLAUDE.md` or `AGENTS.md` — existing AI agent instructions

Run these shell commands to understand structure:
- `find . -maxdepth 2 \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" \) -type f | head -40` — identify main source files (parentheses group `-o` predicates so `-maxdepth` applies to all)
- `ls -la` — root directory listing
- `git remote -v` — git remote info (if applicable)

### Step 3: Generate context files

Create `.agent/` directory and write these files:

#### `.agent/ARCHITECTURE.md`
```markdown
# Project Architecture

## Overview
[1-2 sentence project description from README/metadata]

## Tech Stack
- Language: [from package.json/pyproject.toml/etc.]
- Framework: [if detected]
- Build tool: [if detected]
- Test framework: [if detected]

## Directory Structure
[Key directories with descriptions, from your scan]

## Entry Points
[Main files: index.ts, main.py, app.py, etc.]

## Key Modules
[Important modules and their responsibilities]

## Data Flow
[If applicable — how data moves through the system]
```

#### `.agent/COMMANDS.md`
```markdown
# Project Commands

## Setup
| Purpose | Command |
|---------|---------|
| Install deps | [from package.json/pyproject.toml] |
| Activate env | [if venv/conda detected] |

## Development
| Purpose | Command |
|---------|---------|
| Start dev server | [if detected] |
| Run tests | [if detected] |
| Lint | [if detected] |
| Type check | [if detected] |

## Build & Deploy
| Purpose | Command |
|---------|---------|
| Build | [if detected] |
| Deploy | [if detected] |

## Data Processing
[If applicable — data pipeline commands]

## Custom Scripts
[Any scripts found in package.json scripts, Makefile targets, etc.]
```

#### `.agent/CONFIG.md`
```markdown
# Project Configuration

## Environment Variables
| Variable | Purpose | Location |
|----------|---------|----------|
| [name] | [what it's for] | .env |

## API Keys
[If any API keys are needed, document WHERE they are stored — never the actual values]

## External Services
[Any external services the project depends on]

## Local Setup
[Steps to get the project running locally]
```

#### `.agent/PROGRESS.md`
```markdown
# Project Progress

## Current Focus
[Auto-detected from recent git log, or "Initial setup"]

## Completed
- [x] (YYYY-MM-DD) Project context initialized

## In Progress
(none)

## Backlog
(none)

## Blockers
(none)
```

#### `.agent/DECISIONS.md`
```markdown
# Technical Decisions Log

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|

## Lessons Learned
| Date | Lesson | Context |
|------|--------|---------|
```

### Step 4: Present to user

Show the user:
1. A summary of what was detected and generated.
2. Ask them to review the files and add anything you missed.
3. Tell them: "From now on, I'll auto-maintain these files. You don't need to manage them manually."

### Important

- **Never hardcode API keys or secrets** in `.agent/CONFIG.md` — only document where they're stored.
- **Don't over-scan** — stick to the files listed above. Don't read every source file.
- **Keep it concise** — these are reference files, not comprehensive documentation.
- **If the project is minimal** (no README, no config files), still create the `.agent/` structure with placeholders and ask the user to fill in.
