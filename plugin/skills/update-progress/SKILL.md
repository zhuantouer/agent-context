---
name: update-progress
description: 维护简短的 PROGRESS.md 地图与按需的 work log，用于状态变化、决策证据或历史迁移。
---

# Update Progress

遵循 `Agentic 方法论` 的写入触发：当前状态与历史证据分开存——地图只记现在，过程与证据进 `worklog/`，两者不重复。

## Instructions

1. 先读相关内容并保留人工记录。状态未变则不写文件。
2. 每轮检查当前问题是否仍属于 `Objective`。新当前目标覆盖 `Objective`，不得追加日期史或并列旧口径；未结案旧线进 `Other Goals`；已回答、判负或放弃的进 `Closed Questions`。推断内容标 assumption。
3. 满足下方判据时先写 worklog；仅当目标、当前结论/缺口、next check、milestone 或相关链接变化时更新 `PROGRESS.md`。决定性验证、限制与阻塞留在当前状态，细节链接到日志。
4. 简短报告结论与缺口；仅在有用时给下一步。不建 handoff、不按天建空日志、不自动执行积压项。

## Write criteria

仅当本次工作至少产生以下一项时才写 worklog：

- 改变当前结论或后续决策的证据；
- 可复用的验证结果；
- 失败但排除了一个合理方案；
- 需要跨会话保留的重要决策及理由；
- 明确的阻塞、限制或未验证风险。

过程性工具调用、无新结论的重复检查、只读状态查询不记录。

## Progress template

标题保持英文，这样跨项目的链接与恢复都稳定；正文用项目语言。`Current State` 是当前格式的标志。省略用不到的章节，但不要省略不确定性。

```markdown
# Project Progress

## Objective
[只放当前目标线，不追加历史；缺省段可省略。]
**目标**：[一句话，沿用用户措辞。]
**当前验收标准**：[可判定指标；推断的标 assumption，未分辨不记为零。]
**当前子目标**：[只到下一决策点。]

## Other Goals
[可选：未结案目标 + 状态（并行推进 / 暂停 / 等待前置）+ 恢复条件 + 链接。]

## Closed Questions
[可选：状态（已回答 / 已判负 / 被取代）+ 结论 + 证据链接 + 不得沿用的旧口径。]

## Constraints
[可选：范围、非目标、投入上限和用户约束。]

## Current State
[日期/版本、当前任务、结论、验证缺口、阻塞及相关链接；无任务可写 "No active task"。]

## Next Check
[可选：缺口 → 动作与预期证据 → 决策或停止条件。]

## Milestones
- [可选：粗粒度结果、日期、证据链接；合并旧项。]

## Deferred
- [可选：机会与再次查看条件；不代表已批准。]
```

## Daily log template

只在有值得留存的工作时建日志，日期用用户本地工作日期，不是下次会话。连续的工作留在原文件里直到产生新结果。追加前先读当天已有内容，绝不覆盖其他任务。

```markdown
# Work Log — YYYY-MM-DD

## Pilot
[目的/任务；仅在需要时给前序条目链接。]
- Work and evidence: [结果、决定性命令/来源/产物、验证、局限。]
- Conclusion: [预期 vs 实际；对目标的影响，包含被证伪的假设。]
```

小标题要能说明内容且保持稳定，同一天内唯一；保留被链接的锚点。从 PROGRESS 引用：`worklog/YYYY-MM-DD.md#task`；日志之间：`YYYY-MM-DD.md#task`。链接前先确认文件/标题存在。不要把整张状态图或每次工具调用都抄进日志。

## Recovery and growth

1. 完整读 `PROGRESS.md`；信息不足时跟随当前任务链接。
2. 没有链接时按任务搜索日志并只读匹配章节；不按日期批量加载、不建空日志、不复制旧笔记。
3. 保持地图可完整重读：细节进日志，合并旧 milestone，移除过时链接但保留结论、决定性限制和相关证据。不建日志索引或第二层归档。
4. 可复用的命令、偏好和教训分别归 `COMMANDS.md`、`CONVENTIONS.md`、`MEMORY.md`，只链接不复制；不列 touched files。

## Legacy migration

`HANDOFF.md` 之类的旧快照是只读的迁移来源：可以读、可以把内容并进 `worklog/` 和 `PROGRESS.md`，但不得往里写新内容，也不得新建一个。仅当遇到尚不含 `Current State` 章节的旧格式 progress 或 `HANDOFF.md` 时，读 `references/legacy-migration.md`。
