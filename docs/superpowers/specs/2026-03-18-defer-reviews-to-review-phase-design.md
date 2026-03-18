# Defer Per-Task Reviews to Review Phase

## Problem

The implementation phase currently dispatches spec-compliance and code-quality reviewer subagents after each task completes. The review phase then runs those same reviews again holistically. This duplication is expensive — per-task reviews add significant time to implementation without proportional quality gains, since the holistic review catches the same issues with better cross-task context.

The behavior is also inconsistent: sometimes reviews run per-task, sometimes they don't, depending on how the orchestrator interprets the instructions.

## Decision

Remove per-task spec-compliance and code-quality review subagent dispatches from the implementation phase. The review phase becomes the single quality gate for these concerns.

### What changes

1. **SDD orchestrator** (`skills/subagent-driven-development/SKILL.md`) — Stop dispatching spec-reviewer and code-quality-reviewer subagents per task. Collect `DONE_WITH_CONCERNS` notes into an artifact for the review phase.
2. **Standard implementer prompt** (`skills/implementing/implementer-prompt.md`) — Remove references to post-implementation review loops. Keep the self-review checklist. Encourage proactive use of `DONE_WITH_CONCERNS`.
3. **Figma implementer prompt** (`skills/implementing/implement-figma-design.md`) — Keep the visual validation loop (Steps 5-6: achieve parity, validate against screenshot). Remove references to spec-compliance and code-quality review subagents.
4. **Implementing skill** (`skills/implementing/SKILL.md`) — Remove references to review templates as part of the implementation flow.
5. **Review phase** (`skills/reviewing/SKILL.md`) — Read collected concerns from `implementation-concerns.md` and pass them as priority areas to both reviewers.

### What stays the same

- Implementer self-review checklist (lightweight, no subagent dispatch)
- Status return contract: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`
- Figma visual validation loop (unique to Figma tasks, stays inside the implementer subagent)
- Review phase fix loops (max 5 iterations per review type)
- Review artifact output and approval gate
- All review prompt templates (still used by the review phase)

## Design

### 1. SDD Orchestrator Changes

**File:** `skills/subagent-driven-development/SKILL.md`

**Remove:**
- All instructions to dispatch `spec-reviewer-prompt.md` and `code-quality-reviewer-prompt.md` subagents after each task
- The "Final code review" step in the process graph
- Red flags about skipping per-task reviews, review ordering, and moving to next task while reviews have open issues
- The worked example text referencing "passes reviews" / "fails spec review"

**Add:**
- After each task returns, accept its status directly
- If status is `DONE_WITH_CONCERNS`, store the task number and concerns in a collected list
- After all tasks complete, if any concerns were collected, write them to `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` with format:

```markdown
# Implementation Concerns

Collected during implementation phase. Priority areas for the review phase.

## Task N: [task name]
- [concern text from implementer report]

## Task M: [task name]
- [concern text from implementer report]
```

**Update status handling:**
- `DONE`: Mark task `completed`, update plan checkbox. No review dispatch.
- `DONE_WITH_CONCERNS`: Read concerns. If about correctness/scope, store in concerns list and mark `completed`. If the concern indicates the task is fundamentally broken (e.g., "I couldn't get tests to pass"), treat as `BLOCKED` instead.
- `NEEDS_CONTEXT` and `BLOCKED`: Unchanged.

**Update process graph:** Remove "Final code review" node. The path goes from "All tasks done?" directly to "Complete".

**Update Prompt Templates section:** Remove references to `spec-reviewer-prompt.md` and `code-quality-reviewer-prompt.md` as SDD subagent prompts. These templates still exist — they're used by the review phase — but SDD no longer dispatches them.

**Update Red Flags section:** Remove:
- "Skip reviews (spec compliance OR code quality)" — no longer applies per-task
- "Start code quality review before spec compliance passes" — no longer applies per-task
- "Move to next task while either review has open issues" — no longer applies
- "Accept 'close enough' on spec compliance" — moved to review phase concern
- "Skip review loops" — moved to review phase concern
- "Let implementer self-review replace actual review" — the self-review is now the only per-task check; the review phase is the actual review

Add:
- "Silently discard DONE_WITH_CONCERNS notes — always collect and persist them"

**Update worked example:** Remove review references:
```
--- Cycle 1 ---
Completed: []
Ready: [1, 2] → no file overlap → dispatch both
  → Agent(Task 1), Agent(Task 2) dispatched in parallel
  → Both return DONE
Completed: [1, 2]

--- Cycle 2 ---
Ready: [3, 4] → no file overlap → dispatch both
  → Task 3 returns DONE_WITH_CONCERNS (concern noted)
  → Task 4 returns DONE
Completed: [1, 2, 3, 4]
Concerns collected: [Task 3: "..."]

--- Cycle 3 ---
Ready: [5] → dispatch
  → Task 5 returns DONE
Completed: [1, 2, 3, 4, 5] → Write implementation-concerns.md → Done
```

### 2. Standard Implementer Prompt Changes

**File:** `skills/implementing/implementer-prompt.md`

No structural changes to the template. The prompt does not currently reference review subagents being dispatched after it — it focuses on the implementer's own workflow. The self-review section stays as-is.

**Add** to the "Report Format" section, after the existing status descriptions:

```
Be thorough with DONE_WITH_CONCERNS — this is your primary channel for flagging
issues to the review phase. If anything feels uncertain, incomplete, or fragile,
flag it. The review phase will prioritize your concerns.
```

### 3. Figma Implementer Prompt Changes

**File:** `skills/implementing/implement-figma-design.md`

No structural changes needed. The Figma prompt already self-contains its visual validation loop (Steps 5-6) and does not reference external review subagents. The self-review section stays as-is.

**Add** the same `DONE_WITH_CONCERNS` encouragement to the "Report Format" section as the standard implementer.

### 4. Implementing Skill Changes

**File:** `skills/implementing/SKILL.md`

**Add** after "After SDD Completes" step 3 (Update state.yaml):

```
4. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` exists,
   mention it to the user: "Implementation concerns were collected — they will be
   prioritized during the review phase."
```

No other changes needed — this file delegates to SDD and doesn't reference review templates directly.

### 5. Review Phase Changes

**File:** `skills/reviewing/SKILL.md`

**Update Step 1 (Gather Context)** — add a fourth item:

```
4. Read `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` if it exists —
   these are concerns flagged by implementers during the implementation phase
```

**Update Step 2 (Spec Compliance Review)** — when dispatching the spec-reviewer, add to the prompt:

```
## Priority Areas

The following concerns were flagged during implementation. Check these areas first:

[contents of implementation-concerns.md, or "No concerns were flagged." if file doesn't exist]
```

**Update Step 3 (Code Quality Review)** — same addition to the code-quality-reviewer dispatch:

```
## Priority Areas

The following concerns were flagged during implementation. Check these areas first:

[contents of implementation-concerns.md, or "No concerns were flagged." if file doesn't exist]
```

No changes to Steps 4-5.

## Files Changed

| File | Change Type | Summary |
|------|-------------|---------|
| `skills/subagent-driven-development/SKILL.md` | Major edit | Remove per-task review dispatches, add concerns collection, update graph/examples/red-flags |
| `skills/implementing/implementer-prompt.md` | Minor edit | Add DONE_WITH_CONCERNS encouragement |
| `skills/implementing/implement-figma-design.md` | Minor edit | Add DONE_WITH_CONCERNS encouragement |
| `skills/implementing/SKILL.md` | Minor edit | Mention concerns artifact after SDD completes |
| `skills/reviewing/SKILL.md` | Minor edit | Read and pass concerns to reviewers as priority areas |

## Files NOT Changed

| File | Reason |
|------|--------|
| `skills/implementing/spec-reviewer-prompt.md` | Still used by review phase — template unchanged |
| `skills/implementing/code-quality-reviewer-prompt.md` | Still used by review phase — template unchanged |
| `skills/reviewing/code-reviewer.md` | Still used by review phase — template unchanged |

## Net Effect

- Implementation phase gets faster: no review subagent dispatches per task
- Review phase is slightly smarter: receives concerns context from implementation
- Quality bar unchanged: reviews still happen, just consolidated in one place
- Consistent behavior: reviews always happen during review phase, never during implementation
