# Review：方向变更回写目标补丁 — 已修复并验证

**Review 对象**：`plugin/rules/agentic-protocol-core.mdc`、`plugin/skills/update-progress/SKILL.md`、`plugin/skills/bootstrap-context/SKILL.md`、`scripts/test-hooks.py`。

**验证**：`python3 scripts/test-hooks.py` **32/32 OK**；`node scripts/validate-template.mjs` **通过且无警告**（规则正文 4190 字符，低于 4200 的 review line，硬上限 6000）。

---

## 一、发现（review 阶段）

A–F 六条全部落实且分层正确（core 持规范、skill 持操作、bootstrap 让渡状态写权），但有 1 个硬伤 + 2 个语义缺陷 + 1 个体积问题：

1. **测试红**：新增 `## 已回答的问题` 违反模板"标题保持英文"约定，`test_template_partitions_resume_and_history` 失败 1/32。
2. **"被取代" ≠ "已回答"**：被放弃的目标常未被回答，塞进"已回答"制造虚假记录。
3. **强制回写无门槛**：与"简单问答不写项目记忆"冲突，旁支提问会把主线目标挤出 Objective。
4. **事故特异叙事 + 字数**：正文 3418 → 4272（+25%），其中 ~250 字符是一次事故的叙事（baseline/scaling 例子、"一次真实失效"括号）。

## 二、已应用的修复

### 1. 目标模型从"单槽"改为"三分区"（含多目标线并存）

用户补充的真实场景：**多条目标线并行推进，切换 ≠ 结案**。因此不再是单槽覆盖：

| 分区 | 内容 |
|---|---|
| `## Objective` | **当前激活**的那一条线（唯一判定口径），切换时覆盖式改写 |
| `## Other Goals` | 其余线：`并行推进` / `暂停` / `等待前置` + 恢复条件（≤3 条），被点名才提升回 Objective |
| `## Closed Questions` | 已结案：`已回答` / `已判负` / `被取代` + 结论 + 证据链接 + "不得再用该口径解读" |

标题全部为英文，符合模板约定。

### 2. 强制回写加实质性门槛

触发条件收紧为"新问题**成为当前工作目标**（它驱动后续动作或用户确认继续）"；旁支提问（不驱动后续工作的）不改写 Objective，记进 worklog 或 `Deferred`。这同时给规则一个"在琐事上关闭"的条件，正是 validator 审计口径要求的。

### 3. 测试同步

`scripts/test-hooks.py` 新增 `OPEN_GOAL_SECTIONS` / `CLOSED_GOAL_SECTIONS` 常量，模板标题分区断言纳入两个新章节——任何新增章节都必须被显式登记，不会静默漏过。

### 4. 精简（4190 字符，validator 警告消除）

按 validator 自己的审计口径（"是否重复 skill 或 Project Memory 表格"）删掉：

- baseline/scaling 事故例子整段、"一次真实失效"括号叙事；
- 与 L23 重复的 assumption 提示、与 Goal Alignment 重复的目标线路由说明；
- 合并"方向变更"与"多条线"两段；压缩评审（F）条款冗余表述。

净效果：相比 G 版 **4272 → 4190**，且新增了多目标线能力；事故叙事已清零。

### 5. 措辞修正

`update-progress` 指令 2 的双"先"改为明确顺序（方向检测 → Objective → worklog → Current State）；"视为该 milestone 未完成"改为可执行的"补做回锚再继续"；`bootstrap-context` 的"交回/提示用户"改为"加载 `update-progress` 改写并告知用户"。

## 三、待你定夺（未动）

- **是否再压体积**：4190 已低于 review line，但比 HEAD（3418）多 772 字符。若还要更短，最可能牺牲的是三段式说明或多目标线的状态枚举——会削弱这次要修的行为，不建议。
- **本仓库自己的 `PROGRESS.md`**：`## Objective` 仍是旧自由文本格式，补丁落地后应按新三段模板迁移。
- **hosts 尚未生效**：安装的副本在 `~/.codebuddy/plugins/agentic-protocol`，仍是补丁前版本，需 `./scripts/install-local.sh all` 重装才能在会话里生效。
