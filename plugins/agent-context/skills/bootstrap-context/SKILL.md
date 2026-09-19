---
name: bootstrap-context
description: 初始化和维护 `.agent-context/` 里的知识类文件（结构、命令、配置、约定、决策）；状态类用 `update-progress`。
---

# Bootstrap Project Context

`.agent-context/` 的作用与归属见 `Agentic 方法论` 的 Project Memory。本 skill 负责**知识类**文件；状态类（`PROGRESS.md` + `worklog/`）归 `update-progress`。

## When to use

- 首次：`.agent-context/` 缺失时，实质性工作前
- 后续：结构、依赖、命令、配置、约定、决策或教训发生实质变化后
- 用户显式要求

## Instructions

1. 已有内容只增不覆盖；用户已要求的刷新无需再确认，出现实质冲突才问。
2. 只读与任务相关的 `README`、包/配置 manifest、env 示例、规则与宿主指令（如 `CLAUDE.md`、`AGENTS.md`），不扫全仓。
3. 文件由你自己写，不向用户索要信息；只记录下次会话仍有用的事实。
4. 建完或更新完简短报告：动了哪些文件、抓到什么事实、还有哪些未知。

## Update existing files

对已有文件做增量修改，不重写全文：

- 改前先读它；保留手工添加的内容；没变的部分不动；重复或过时的合并掉。
- 结构变了就更新架构描述、`verified against`（commit 加已核对的 worktree 改动，或 `(no git)`）与覆盖路径；只对你实际检查过的路径声称已重新验证。

## Finding changes

代码没变不等于没有变化 —— 目标、决策、证据的改变往往不落在 diff 里。

- 有 git：用 `git diff --name-only HEAD` 或 `git status --porcelain`；先确认可选的历史引用是否有效。
- 无 git：比较相关文件与已知 context，并标注不确定性；只在缺失的选择会影响工作时才问。

## What to fill in

各文件装什么见 `Agentic 方法论` 的 Project Memory，这里只给填充要点：

- `ARCHITECTURE.md`：overview、技术栈、结构、entry point、数据流、模块职责与边界。记 `verified against`（commit 加已核对的 worktree 改动，或 `(no git)`）与覆盖路径，不要只写日期。
- `COMMANDS.md`：setup/dev/test/lint/type/build/deploy 命令、validation profile、脚本、命令注意事项。
- `CONFIG.md`：环境变量名、密钥位置、依赖服务、本地搭建；不写 secret 值。
- `CONVENTIONS.md`：代码风格、偏好、边界、review 习惯、术语；模块化习惯：一个文件一个职责、按职责而非长度拆分、依赖单向、不过度碎片化。
- `PROGRESS.md`：用 `update-progress` 建地图。目标与验收标准从对话中提取（推断的标 assumption），产出形态未定时先记当前子目标。
- `MEMORY.md`：决策、经验教训与纠正性指引、跨任务的 open question。

## Rules

- 用真实日期。
- 所有文件可选，不留空占位。有目标、当前结论或有意义的工作时才建 `PROGRESS.md`；更旧的 context 用 `update-progress` 合并。
- 服务未来的 agent，不是写全面文档。
