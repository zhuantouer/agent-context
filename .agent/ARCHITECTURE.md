# Project Architecture

## Overview
`agent-context` is a lightweight Cursor plugin that gives coding agents persistent project memory through an auto-maintained `.agent/` directory.

## Tech Stack
- Language: Markdown rules/skills plus Node.js validation scripts
- Framework: Cursor plugin format
- Build tool: none detected
- Test framework: plugin template validation via Node.js script

## Directory Structure
- `plugins/agent-context/` - Cursor plugin package installed or published to Cursor.
- `plugins/agent-context/rules/` - Always-applied agent operating protocol.
- `plugins/agent-context/skills/` - Agent skills for bootstrapping, syncing context, and updating progress.
- `plugins/agent-context/hooks/` - Cursor hooks, including session start reminders.
- `.cursor-plugin/` - Local marketplace metadata.
- `scripts/` - Repository scripts such as plugin template validation.

## Entry Points
- `plugins/agent-context/.cursor-plugin/plugin.json` - Plugin manifest.
- `plugins/agent-context/rules/agent-context-core.mdc` - Core always-applied agent instructions.
- `scripts/validate-template.mjs` - Validation command for plugin structure.

## Key Modules
- Core rule: enforces context bootstrap, recovery, progress tracking, confirmation guardrails, and lessons learned.
- Skills: provide focused workflows for bootstrapping context, syncing context after changes, and updating progress.
- Hook: reminds new sessions to read `.agent/PROGRESS.md` first.

## Data Flow
The plugin injects rules, skills, and a session-start hook into Cursor. Agents then persist project knowledge, commands, progress, decisions, and lessons into the target project's `.agent/` files.
