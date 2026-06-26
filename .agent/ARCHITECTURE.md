# Project Architecture

## Overview
`agent-context` is a lightweight Cursor plugin that gives coding agents persistent project memory, task handoff, validation habits, and project-specific conventions through an auto-maintained `.agent/` directory.

## Tech Stack
- Language: Markdown rules/skills plus Node.js validation scripts
- Framework: Cursor plugin format
- Build tool: none detected
- Test framework: plugin template validation via Node.js script

## Directory Structure
- `plugins/agent-context/` - Cursor plugin package installed or published to Cursor.
- `plugins/agent-context/rules/` - Always-applied agent operating protocol.
- `plugins/agent-context/skills/` - Agent skills for bootstrapping context, syncing context, updating progress, and writing task handoffs.
- `plugins/agent-context/hooks/` - Cursor hooks for session-start context injection and stop-time handoff reminders.
- `.cursor-plugin/` - Local marketplace metadata.
- `scripts/` - Repository scripts such as plugin template validation.

## Entry Points
- `plugins/agent-context/.cursor-plugin/plugin.json` - Plugin manifest.
- `plugins/agent-context/rules/agent-context-core.mdc` - Core always-applied agent instructions.
- `scripts/validate-template.mjs` - Validation command for plugin structure.

## Key Modules
- Core rule: provides a minimal always-on protocol for recovery order, canonical `.agent/` file ownership, safety checks, and memory hygiene.
- Skills: provide focused workflows for bootstrapping context, syncing context after changes, updating progress, and preserving active task state.
- Hooks: inject `.agent/HANDOFF.md` summary on session start and gently remind handoff refreshes on stop when changed files look newer than the handoff.

## Data Flow
The plugin injects rules, skills, and a session-start hook into Cursor. Agents then persist project knowledge, active task state, commands, validation profile, conventions, progress, and long-term memory into the target project's `.agent/` files.
