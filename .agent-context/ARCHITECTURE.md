# Project Architecture

## Overview
`agent-context` is a lightweight goal-directed work-memory plugin. `PROGRESS.md` is the short goal/now/milestone map; `worklog/YYYY-MM-DD.md` holds detailed task evidence. Relevant links, not dates, connect sessions. One protocol and three skills serve Cursor, Codex and CodeBuddy; no separate handoff artifact.

## Tech Stack
- Language: Markdown rules/skills, JSON manifests, Python hook logic, Bash entry points, Node.js validation
- Framework: Cursor plugin format + Codex plugin format + CodeBuddy plugin format, from a single package
- Build tool: none
- Test framework: `scripts/validate-template.mjs` (structure, host-drift, always-on size review lines) + `scripts/test-hooks.py` (hook behaviour, stdlib `unittest`)

## Directory Structure
- `plugins/agent-context/` — the single plugin package, installed to any of the three hosts.
- `plugins/agent-context/rules/` — canonical operating protocol (also the source Codex injects at session start).
- `plugins/agent-context/skills/` — host-neutral skills, shared verbatim by every host.
- `plugins/agent-context/hooks/` — per-host hook configs plus the shared hook implementation.
- `.cursor-plugin/marketplace.json` — Cursor marketplace index.
- `.agents/plugins/marketplace.json` — Codex marketplace index.
- `.codebuddy-plugin/marketplace.json` — CodeBuddy marketplace index.
- `scripts/` — install and validation utilities.

## Entry Points
- `plugins/agent-context/.cursor-plugin/plugin.json` — Cursor manifest (declares `rules/`, `skills/`, `hooks/hooks.json`).
- `plugins/agent-context/.codex-plugin/plugin.json` — Codex manifest (declares `skills/`, `hooks/codex-hooks.json`; Codex has no rules slot).
- `plugins/agent-context/.codebuddy-plugin/plugin.json` — CodeBuddy manifest (declares `skills/`, `hooks/codebuddy-hooks.json`; `rules/` is auto-discovered, no schema field).
- `plugins/agent-context/rules/agent-context-core.mdc` — the protocol, single source of truth.
- `scripts/install-local.sh [cursor|codex|codebuddy|all]` — local install.
- `node scripts/validate-template.mjs` — validation.

## Module Map
_Verified against: worktree based on `11823a4`, 2026-09-17. This review covers `hooks/scripts/session-context.py`, `skills/update-progress/`, `scripts/test-hooks.py`, `scripts/validate-template.mjs`, `scripts/install-local.sh` and the behavior-acceptance README. Unchanged rule/host wiring retains earlier verification; decision-only replay does not verify installed-host behavior._

| Module | Responsibility | Boundary |
|--------|----------------|----------|
| `rules/agent-context-core.mdc` | The operating protocol: startup/recovery, file ownership, architecture checkpoint, execution, evidence, response style, hygiene | Only canonical copy. Cursor and CodeBuddy load it as an always-applied rule; the Codex hook reads and injects it. Nothing else may restate it. Size is a review signal, not a cap: the validator warns past 4200 chars and warns more strongly past 6000. |
| `skills/*/SKILL.md` | Three workflows: bootstrap, sync knowledge, maintain state map and dated evidence | `update-progress` owns PROGRESS/worklog templates, task-link navigation and lossless legacy migration. No daily rollover or handoff skill; shared content stays host-neutral. |
| `hooks/scripts/hook_payload.py` | Parse a host hook payload; resolve the project directory; name which hosts use Claude I/O and which inject the protocol | Knows each host's field precedence. No product logic. |
| `hooks/scripts/session-context.py` | Select current PROGRESS sections and their task links; prepend protocol for Codex only | `Current State` remains the marker; legacy progress/handoff inputs still load. Milestones, Deferred and legacy Work Log stay on demand. Never scan/read daily logs or choose dates. Over-budget fields are omitted, not sliced. Unclosed fences carry source-line diagnostics without guessing headings. No writes or migration. |
| `hooks/scripts/work-signal.py` | Advisory large-modified-code-file signal | No freshness or record-writing prompt. Cursor uses `followup_message`; Codex/CodeBuddy use `systemMessage`, not forced continuation. Fails open and respects turn/loop guards. |
| `hooks/scripts/*.sh` | Cursor entry points | Thin wrappers only, because Cursor's `hooks.json` requires a bare relative path. Codex and CodeBuddy call Python directly. Keep `handoff-signal.py` and `stop-handoff-reminder.sh` as forwarding entry points for cached pre-0.2 host commands; they carry no old bookkeeping behavior. |
| `hooks/hooks.json` / `hooks/codex-hooks.json` / `hooks/codebuddy-hooks.json` | Per-host hook wiring | Separate files: Cursor uses camelCase events and a flat command; Codex and CodeBuddy use PascalCase nested Claude-style hooks. |
| `scripts/validate-template.mjs` | Structure validation for every host, release-version consistency, and rule-size review lines | Compares each plugin's host manifests and optional marketplace entry versions, not marketplace metadata versions. Size growth remains advisory. |
| `scripts/install-local.sh` | Copy one plugin to the selected host and activate where supported | Shared stdlib copy excludes generated bytecode/cache files; source and unrelated plugins stay untouched. |
| `scripts/test-hooks.py` | Recovery, fence diagnostics, budgets, legacy/Stop guards, release-version and installer regressions | Stable fixtures, not mutable project records. Packaging tests use temporary repositories/HOME, require Node for the validator and Bash for the installer; no claim about LLM judgment. |

## Data Flow
Cursor and CodeBuddy load the canonical rule via `rules/`; Codex receives it from SessionStart. All three hosts use `session-context.py` to read current `PROGRESS.md` sections without history; the work record itself is the source, not a copied snapshot. Before consolidation, old progress and HANDOFF are separate read-only inputs. Skills update project files; hooks never do. Cursor wrappers emit camelCase I/O, while Codex/CodeBuddy call Python with Claude-style envelopes. Stop runs only the advisory code-size check.

Dependency direction is one-way: hook entry points → shared hook logic → `hook_payload`. Nothing in `hooks/` imports from `skills/` or `rules/` except `session-context.py` reading the protocol file as data.

## Terms
- Host: Cursor, Codex, or CodeBuddy — the agent runtime that loads the plugin.
- Host-neutral: shared content that names a skill without a host's invocation prefix.
