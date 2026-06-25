---
name: cross-model-review
description: Format implementation for cross-model review, then process review feedback from another model. Use when the user wants to get a second opinion from a different LLM.
disable-model-invocation: true
---

# Cross-Model Review

## When to use

- User wants another model to review your work
- User mentions "review", "expert review", "second opinion"
- User switches to a different model and comes back with feedback
- User runs `/cross-model-review`

## Phase 1: Generate Review Package

When the user asks for a review of your work:

### Step 1: Summarize the task and changes

Collect:
- **Task description**: what the user originally asked for
- **Changes made**: files modified, files created, key logic changes
- **Context**: relevant `.agent/` files (architecture, decisions, commands)
- **Review focus areas**: anything you're uncertain about or want a second opinion on

### Step 2: Generate the review package

Output this formatted block for the user to paste into another model:

```markdown
## Review Request

### Task
[Original user request, paraphrased]

### Context
- Architecture: [key points from .agent/ARCHITECTURE.md]
- Relevant decisions: [from .agent/DECISIONS.md if applicable]

### Changes
[For each file changed:]
**[filename]**
- [change description]
- [key code snippet if non-trivial]

### Review Focus
- [Area 1 you want reviewed]
- [Area 2]
- [Any concerns you have]

### Questions for Reviewer
1. [Specific question]
2. [Specific question]
```

### Step 3: Instruct the user

Say: **"I've generated a review package above. Switch to your review model (e.g., GPT) and paste it. When you have the feedback, come back and paste it here — I'll process it."**

---

## Phase 2: Process Review Feedback

When the user returns with feedback from another model:

### Step 1: Parse the feedback

Identify each distinct point or recommendation in the review.

### Step 2: Evaluate each point

For each point, determine:

- **✅ Accept**: The point is valid and should be acted on.
  - Immediately apply the fix.
  - Note what was changed.

- **❌ Reject**: The point is not applicable or incorrect.
  - Explain why clearly and respectfully.
  - Reference code or context that supports your position.

- **⚠️ Discuss**: The point is partially valid or needs user input.
  - Explain the nuance.
  - Ask the user for their preference.

### Step 3: Output summary table

```markdown
## Review Processing Summary

| # | Review Point | Verdict | Action Taken |
|---|-------------|---------|--------------|
| 1 | [point] | ✅ Accept | Fixed in [file] |
| 2 | [point] | ❌ Reject | [reason] |
| 3 | [point] | ⚠️ Discuss | [question for user] |

### Changes Applied
[List of changes made as a result of accepted points]

### Items Needing Your Input
[Any ⚠️ items that need user decision]
```

### Step 4: Log the review

Append to `.agent/DECISIONS.md`:

```markdown
### Review: [task name] (YYYY-MM-DD)
- **Reviewer**: [model name if known]
- **Points accepted**: [count]
- **Points rejected**: [count]
- **Key outcomes**: [brief summary of what changed]
```

This builds institutional memory — future sessions can see what was reviewed and what decisions were made.

### Important

- **Be objective** — don't reject feedback just because it came from another model.
- **Be decisive** — if a point is clearly valid, accept and fix it immediately. Don't ask the user about every minor point.
- **Be respectful** — acknowledge good points, explain rejections with evidence.
- **Don't re-implement from scratch** — only apply the specific changes from accepted review points.
