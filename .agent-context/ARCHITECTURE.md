# Project Architecture

## Overview
`agent-context` is a lightweight plugin that gives coding agents persistent project memory, task handoff, validation habits, and project conventions through an auto-maintained `.agent-context/` directory in the target project. One plugin package serves two hosts: Cursor and Codex.

## Tech Stack
- Language: Markdown rules/skills, JSON manifests, Python hook logic, Bash entry points, Node.js validation
- Framework: Cursor plugin format + Codex plugin format, from a single package
- Build tool: none
- Test framework: `scripts/validate-template.mjs` (structure + host-drift assertions)

## Directory Structure
- `plugins/agent-context/` — the single plugin package, installed to either host.
- `plugins/agent-context/rules/` — canonical operating protocol (also the source Codex injects at session start).
- `plugins/agent-context/skills/` — host-neutral skills, shared verbatim by both hosts.
- `plugins/agent-context/hooks/` — both hosts' hook configs plus the shared hook implementation.
- `.cursor-plugin/marketplace.json` — Cursor marketplace index.
- `.agents/plugins/marketplace.json` — Codex marketplace index.
- `scripts/` — install and validation utilities.

## Entry Points
- `plugins/agent-context/.cursor-plugin/plugin.json` — Cursor manifest (declares `rules/`, `skills/`, `hooks/hooks.json`).
- `plugins/agent-context/.codex-plugin/plugin.json` — Codex manifest (declares `skills/`, `hooks/codex-hooks.json`; Codex has no rules slot).
- `plugins/agent-context/rules/agent-context-core.mdc` — the protocol, single source of truth.
- `scripts/install-local.sh [cursor|codex|all]` — local install.
- `node scripts/validate-template.mjs` — validation.

## Module Map
_last verified: 2026-08-03_

| Module | Responsibility | Boundary |
|--------|----------------|----------|
| `rules/agent-context-core.mdc` | The operating protocol: recovery order, file ownership, update triggers, safety, hygiene | Only canonical copy. Cursor loads it as an always-applied rule; the Codex hook reads and injects it. Nothing else may restate it. |
| `skills/*/SKILL.md` | Focused workflows: bootstrap, sync, progress, handoff | Must stay host-neutral — no `/name` or `$name` invocation prefixes. Enforced by the validator. |
| `hooks/scripts/hook_payload.py` | Parse a host hook payload; resolve the project directory | Knows each host's field precedence. No product logic. |
| `hooks/scripts/session-context.py` | Build session-start context: protocol (Codex only) + handoff excerpt | One implementation, host chosen by argv. Cursor omits the protocol because its rule already supplies it. |
| `hooks/scripts/handoff-signal.py` | Two independent stop signals — stale handoff (high frequency) and oversized touched files (low frequency) | One implementation; hosts differ only in turn gate and output shape. Each signal is computed by its own function so either can be tuned alone. Advisory only: Cursor uses `followup_message`, Codex uses `systemMessage`, never a forced continuation. Fails open. |
| `hooks/scripts/*.sh` | Cursor entry points | Thin wrappers only, because Cursor's `hooks.json` requires a bare relative path. Codex calls Python directly. |
| `hooks/hooks.json` / `hooks/codex-hooks.json` | Per-host hook wiring | Separate files: the two hosts use different event names and output schemas. |
| `scripts/validate-template.mjs` | Structure validation for both hosts + drift assertions | The signal that keeps the single-copy invariants true. |

## Data Flow
The host loads the plugin. Cursor injects the protocol via its always-applied rule and calls the `.sh` hooks; Codex has no rules slot, so its `SessionStart` hook injects the protocol read from `rules/` plus the handoff. Both hosts' hooks funnel into the same Python implementation, which reads the target project's `.agent-context/` state. Skills and the protocol then instruct the agent to write project knowledge back into `.agent-context/`.

Dependency direction is one-way: hook entry points → shared hook logic → `hook_payload`. Nothing in `hooks/` imports from `skills/` or `rules/` except `session-context.py` reading the protocol file as data.

## Terms
- Host: Cursor or Codex, the agent runtime that loads the plugin.
- Host-neutral: shared content that names a skill without a host's invocation prefix.
