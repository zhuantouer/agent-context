---
name: bootstrap-context
description: 初始化和维护 `.agent-context/` 里的知识类文件（结构、命令、配置、约定、决策）；状态类用 `update-progress`。
---

# Bootstrap Project Context

`.agent-context/` 的作用与归属见 `Agentic 方法论` 的 Project Memory。本 skill 负责**知识类**文件；状态类（`PROGRESS.md` + `worklog/`）归 `update-progress`。

## When to use

- 首次：`.agent-context/` 缺失且属于实质性工作（判定见 `Agentic 方法论` Startup）
- 后续：结构、依赖、命令、配置、约定、决策或教训发生实质变化后
- 用户显式要求

## Instructions

1. 只读与任务相关的 `README`、manifest、env 示例、规则与宿主指令，不扫全仓；有 git 时用 diff/status 定位变化，无 git 时比较相关文件并标注不确定性。
2. 改前先读，局部更新并保留仍有效的人工内容；只对实际检查过的路径声称已验证。结构变化时同步 `ARCHITECTURE.md` 的 `verified against`（commit 加已核对的 worktree，或 `(no git)`）和覆盖路径。
3. 自行从源码与实测提取事实，不向用户索要可自行查明的信息。只记录下次会话仍有用的内容；所有文件可选，不留空占位。
4. 若当前目标与 `PROGRESS.md` 不一致，不改状态文件；加载 `update-progress` 处理。
5. 完成后简短报告变更文件、关键事实与未知项。

## File contents

- `ARCHITECTURE.md`：overview、技术栈、结构、entry point、数据流、模块边界。
- `COMMANDS.md`：setup/dev/test/lint/type/build/deploy 命令、validation profile 和注意事项。
- `CONFIG.md`：环境变量名、secret 位置、依赖服务和本地搭建；不写 secret 值。
- `CONVENTIONS.md`：代码风格、工作流、偏好、边界、review 习惯和术语。
- `MEMORY.md`：决策与理由、经验教训、纠正性指引和跨任务 open question。

用真实日期；服务未来的 agent，不写全面文档。
