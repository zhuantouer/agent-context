# Project Architecture

## Overview
`agent-context` is a lightweight plugin that gives coding agents persistent project memory, task handoff, validation habits, and project conventions through an auto-maintained `.agent-context/` directory in the target project. One plugin package serves three hosts: Cursor, Codex, and CodeBuddy.

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
_verified against: working tree at 2026-09-03 (CodeBuddy host adapter) — covers `plugins/agent-context/**`, `.codebuddy-plugin/**`, `.codebuddy/settings.json`, and `scripts/**`_

| Module | Responsibility | Boundary |
|--------|----------------|----------|
| `rules/agent-context-core.mdc` | The operating protocol: startup/recovery, file ownership, architecture checkpoint, execution, evidence, response style, hygiene | Only canonical copy. Cursor and CodeBuddy load it as an always-applied rule; the Codex hook reads and injects it. Nothing else may restate it. Size is a review signal, not a cap: the validator warns past 4200 chars and warns more strongly past 6000. |
| `skills/*/SKILL.md` | Focused workflows: bootstrap, sync, progress, handoff | Must stay host-neutral — no `/name` or `$name` invocation prefixes. Enforced by the validator. |
| `hooks/scripts/hook_payload.py` | Parse a host hook payload; resolve the project directory; name which hosts use Claude I/O and which inject the protocol | Knows each host's field precedence. No product logic. |
| `hooks/scripts/session-context.py` | Build session-start context: protocol (Codex only) + a fixed-size resume capsule built from selected `HANDOFF.md` fields | One implementation, host chosen by argv. Cursor and CodeBuddy omit the protocol because the plugin rule already supplies it. Emits state only — never instructions, which the protocol owns. |
| `hooks/scripts/handoff-signal.py` | Two independent stop signals — stale handoff (high frequency) and oversized touched files (low frequency) | One implementation; hosts differ only in turn gate and output shape. Each signal is computed by its own function so either can be tuned alone. Advisory only: Cursor uses `followup_message`, Codex and CodeBuddy use `systemMessage`, never a forced continuation. Fails open. |
| `hooks/scripts/*.sh` | Cursor entry points | Thin wrappers only, because Cursor's `hooks.json` requires a bare relative path. Codex and CodeBuddy call Python directly. |
| `hooks/hooks.json` / `hooks/codex-hooks.json` / `hooks/codebuddy-hooks.json` | Per-host hook wiring | Separate files: Cursor uses camelCase events and a flat command; Codex and CodeBuddy use PascalCase nested Claude-style hooks. |
| `scripts/validate-template.mjs` | Structure validation for every host, drift assertions, and the always-applied rule's size review lines | The signal that keeps the single-copy invariants true. Owns the normal/strong size warnings; growth is allowed and visible, not blocked. |
| `scripts/test-hooks.py` | Hook behaviour: capsule field selection, per-field clipping, size backstop, stop-signal firing conditions, and the template/capsule contract | Imports the hook modules by path and drives `handoff-signal.py` as a subprocess over a throwaway git repo. Owns behaviour assertions; the validator owns structure. |

## Data Flow
The host loads the plugin. Cursor and CodeBuddy inject the protocol via the always-applied rule in `rules/` and call the session-start hook for the handoff capsule only; Codex has no rules slot, so its `SessionStart` hook injects the protocol read from `rules/` plus the handoff. Cursor's hook I/O is camelCase JSON through `.sh` wrappers; Codex and CodeBuddy use Claude-style nested hooks and call Python directly. All three hosts' hooks funnel into the same Python implementation, which reads the target project's `.agent-context/` state. Skills and the protocol then instruct the agent to write project knowledge back into `.agent-context/`.

Dependency direction is one-way: hook entry points → shared hook logic → `hook_payload`. Nothing in `hooks/` imports from `skills/` or `rules/` except `session-context.py` reading the protocol file as data.

## Terms
- Host: Cursor, Codex, or CodeBuddy — the agent runtime that loads the plugin.
- Host-neutral: shared content that names a skill without a host's invocation prefix.
