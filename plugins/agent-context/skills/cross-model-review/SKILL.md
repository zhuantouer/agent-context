---
name: cross-model-review
description: Review recent work in the current chat using existing context, then apply accepted fixes. Use when the user runs /cross-model-review or wants a second opinion.
disable-model-invocation: true
---

# Cross-Model Review (in-chat, no subagent)

## When to use

- User runs `/cross-model-review`
- User wants a second opinion on recent work
- User mentions "cross-model review", "expert review", or "review my changes"

**Do not spawn a subagent.** Review in the **current conversation** and reuse context already loaded.

## Why no subagent

Subagents start with a blank context window. That forces the parent to dump large briefs into the Task prompt, and the reviewer often re-explores the repo — **double token cost** for worse coverage. This chat already has task history, files read, and diffs. Use that.

---

### Step 1: Cross-model intent (optional)

If the user wants a **different model** to review (not the current chat model):

- Tell them to **switch the input-box model**, then send `/cross-model-review` again.
- Do **not** spawn a subagent to simulate cross-model.

If the user is fine with the **current model** self-reviewing, proceed immediately.

Skip this step when the user already switched models or said "review with current model".

---

### Step 2: Gather context (minimal reads)

**Reuse first.** Only read what is **not** already in this conversation:

| Source | When to read |
|--------|----------------|
| This chat history | Task goal, decisions, files already discussed — **default** |
| `git diff` / `git diff --staged` | Changed lines not already in context |
| `.agent/ARCHITECTURE.md` | Architecture not already summarized in chat |
| `.agent/DECISIONS.md` | Prior decisions relevant to the change |
| `.agent/COMMANDS.md` | Only if reviewing build/test/deploy changes |

**Do NOT:**

- Paste entire files or long diffs into a subagent prompt (there is no subagent)
- Re-read files unchanged since this session already covered them
- Run broad exploration (`find`, repo-wide `grep`, directory trees) to "understand the project"
- Duplicate dependency lists, install steps, or `.agent/` content already in chat

If `.agent/` is missing and architecture is unclear, run `/bootstrap-context` first or read only the changed files plus `README.md`.

---

### Step 3: Review (you, in this chat)

Act as a **skeptical independent reviewer** using existing context plus any minimal reads from Step 2.

Check:

- Correctness, edge cases, security
- Error handling and failure modes
- Breaking changes vs `.agent/DECISIONS.md` / architecture
- Test gaps for non-trivial logic

Ignore style-only nits.

Output **only**:

```markdown
## Cross-Model Review Findings

### Summary
[1-3 sentences]

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | critical/high/medium/low | file:line | ... | ... |

### Questions
- [Ambiguities needing user input, if any]

### Verdict
[approve / approve-with-notes / request-changes]
```

---

### Step 4: Process findings

For each finding:

- **✅ Accept** — fix immediately in the codebase
- **❌ Reject** — explain with evidence from code already in context
- **⚠️ Discuss** — ask the user before changing

Then output:

```markdown
## Review Processing Summary

| # | Review Point | Verdict | Action Taken |
|---|-------------|---------|--------------|
| ... | ... | ... | ... |
```

Append to `.agent/DECISIONS.md`:

```markdown
### Review: [task] (YYYY-MM-DD)
- **Reviewer**: in-chat ([current chat model name])
- **Points accepted**: N
- **Points rejected**: N
- **Key outcomes**: [...]
```

---

## Fallback: External model (manual)

Only when the user explicitly wants ChatGPT / Claude web / another app **outside Cursor**:

1. Generate a lean **Review Request** (task, changed file list, 1-line per file — no full file dumps).
2. User pastes into external model and returns feedback.
3. Process feedback (Accept / Reject / Discuss), apply fixes, log in `.agent/DECISIONS.md`.

---

## Important

- **No subagent** — never spawn `independent-reviewer` or any Task reviewer.
- **Context reuse** — chat memory is the primary source; `.agent/` fills gaps.
- **Minimal I/O** — smallest read set that answers "is this change correct?"
- **Be decisive** — fix clear issues without asking on every minor point.
