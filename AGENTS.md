# Agent Context Protocol

This repository develops the `agent-context` plugin and uses it on itself.

The operating protocol has exactly one canonical copy:

**[`plugins/agent-context/rules/agent-context-core.mdc`](plugins/agent-context/rules/agent-context-core.mdc)** (read it past the YAML frontmatter)

Read it before substantive work, and treat `.agent-context/` as this project's durable memory.
Cursor injects the protocol automatically through its always-applied rule; Codex injects it
through the plugin's `SessionStart` hook. Read the file directly when neither applies.

Do not copy the protocol text into this file. A second copy drifts from the first.
