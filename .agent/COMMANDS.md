# Project Commands

## Setup
| Purpose | Command |
|---------|---------|
| Install deps | No package manager setup detected |

## Development
| Purpose | Command |
|---------|---------|
| Validate plugin structure | `node scripts/validate-template.mjs` |

## Validation Profile
| Change Type | Recommended Check | Notes |
|-------------|-------------------|-------|
| Plugin rules, skills, hooks, metadata, or docs | `node scripts/validate-template.mjs` | Fast structural validation from repo root |
| Hook script changes | `node scripts/validate-template.mjs` plus `bash -n plugins/agent-context/hooks/scripts/session-start.sh` and `bash -n plugins/agent-context/hooks/scripts/stop-handoff-reminder.sh` | Validates hook references, executable bits, and shell syntax |
| Documentation-only change | Manual review plus `node scripts/validate-template.mjs` if plugin metadata/skills/hooks changed | Keep README and plugin README aligned |

## Build & Deploy
| Purpose | Command |
|---------|---------|
| Build | No build step detected |
| Local plugin install | `./scripts/install-local.sh` |

## Data Processing
(none)

## Custom Scripts
- `scripts/validate-template.mjs` validates the Cursor plugin template.
- `scripts/install-local.sh` installs the local plugin into Cursor's local plugins directory.

## Command Notes
- Run commands from the repository root unless a command states otherwise.
