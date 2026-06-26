# Technical Decisions Log

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-26 | Keep project memory in `.agent/` files | Persistent files are the plugin's core value: project understanding, accumulated experience, and lessons learned survive chat context loss. |
| 2026-06-26 | Remove cross-review from the plugin | Cross-review diluted the product direction; the plugin should stay small and focus on durable agent context. |

## Lessons Learned
| Date | Lesson | Context |
|------|--------|---------|
| 2026-06-26 | Cross-review is not part of the core product direction | The plugin should stay focused on helping agents understand projects and preserve hard-won context. |
