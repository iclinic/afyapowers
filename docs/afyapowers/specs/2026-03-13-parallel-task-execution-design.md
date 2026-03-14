# Parallel Task Execution Design

## Overview

Add support for parallel task execution during the implement phase. Tasks that don't depend on each other and don't modify the same files can run concurrently, significantly reducing implementation time.

The approach: explicit dependency declarations in plans, resolved into execution waves by the subagent-driven-development (SDD) skill at runtime.

## Plan Format Changes

Every task in a plan must declare its dependencies via a `**Depends on:**` line. Tasks with no dependencies use `none`.

### Updated Task Structure

The `**Files:**` field uses the existing multi-line bulleted format from writing-plans. The `**Depends on:**` field is a comma-separated list of task numbers, or `none`.

```markdown
### Task 1: Create user model
**Files:**
- Create: `src/models/user.py`
- Test: `tests/models/test_user.py`
**Depends on:** none

- [ ] Step 1: Write failing test
- [ ] Step 2: ...

### Task 2: Create auth middleware
**Files:**
- Create: `src/middleware/auth.py`
- Test: `tests/middleware/test_auth.py`
**Depends on:** none

### Task 3: Create login endpoint
**Files:**
- Create: `src/routes/login.py`
- Test: `tests/routes/test_login.py`
**Depends on:** Task 1, Task 2
```

### Updated Plan Template

The `templates/plan.md` template changes from a flat checklist to a heading-based task structure to support per-task metadata:

```markdown
# Implementation Plan: {{feature_name}}

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence]

**Architecture:** [2-3 sentences]

**Tech Stack:** [Key technologies]

---

### Task 1: [Component Name]
**Files:**
- Create: `path/to/file`
- Modify: `path/to/existing`
- Test: `tests/path`
**Depends on:** none

- [ ] Step 1: ...
- [ ] Step 2: ...

### Task 2: [Component Name]
**Files:** ...
**Depends on:** Task 1

- [ ] Step 1: ...
```

### Plan-Time Validation

The `writing-plans` skill validates at authoring time:
- Every task has a `**Depends on:**` line
- Parallel-eligible tasks (no mutual dependency) don't share files in their `**Files:**` lists
- If file overlap is found between parallel-eligible tasks, a dependency is added to make them sequential
- Dependencies include not just file-level overlap but also logical dependencies (e.g., Task B imports a module created by Task A). The plan author is responsible for declaring all dependencies — file overlap validation is a safety net, not a substitute for thinking about task ordering

## Dependency Resolution & Wave Computation

The SDD skill resolves the dependency graph into execution waves before dispatching tasks.

### Algorithm

1. Parse all tasks and their `**Depends on:**` lines into a list:
   ```
   Task 1: deps=[]        Task 2: deps=[]
   Task 3: deps=[1,2]     Task 4: deps=[1,2]
   Task 5: deps=[3,4]
   ```
2. Check for cycles: if any task is never ready (its dependencies form a loop), report the cycle and stop
3. Build the ready set — tasks with no dependencies, or whose dependencies are all completed:
   ```
   Completed: []
   Ready: [Task 1, Task 2]  (no deps)
   Waiting: [Task 3, Task 4, Task 5]
   ```
4. Before dispatching, validate file lists don't overlap between ready tasks. If overlap found, keep one, move the other back to waiting
5. Cap the dispatch at **max 3 concurrent tasks**. If more are ready, queue the extras for the next cycle
6. Dispatch ready tasks as parallel Agent calls (one message, multiple Agent tool calls)
7. **Wait for all dispatched tasks to return** (this is how the Agent tool works — all calls in a message return together)
8. Process results: mark completed tasks, handle failures
9. Recompute ready set from scratch and repeat from step 3 until all tasks are done

### Worked Example

```
Plan: 5 tasks. Task 1,2 have no deps. Task 3,4 depend on 1,2. Task 5 depends on 3,4.

--- Cycle 1 ---
Completed: []
Ready: [1, 2] → no file overlap → dispatch both
  → Agent(Task 1), Agent(Task 2) dispatched in parallel
  → Both return DONE, pass reviews
Completed: [1, 2]

--- Cycle 2 ---
Ready: [3, 4] (deps [1,2] all completed) → no file overlap → dispatch both
  → Agent(Task 3), Agent(Task 4) dispatched in parallel
  → Task 3 fails spec review, gets fixed, passes on re-review
  → Task 4 passes
Completed: [1, 2, 3, 4]

--- Cycle 3 ---
Ready: [5] (deps [3,4] all completed) → dispatch
  → Agent(Task 5) dispatched
  → Passes
Completed: [1, 2, 3, 4, 5] → Done
```

### Important: Wave Semantics

Because the Agent tool requires all parallel calls in a message to return before the orchestrator can act, execution is inherently wave-based. The orchestrator dispatches a batch, waits for all to return, then computes the next batch. This is simpler than a streaming scheduler and matches the tool's actual behavior.

However, this means that if Task 3 completes quickly but Task 4 takes a long time, tasks depending only on Task 3 must wait for Task 4 to finish before the orchestrator can dispatch them. This is an acceptable trade-off for simplicity.

## Parallel Subagent Dispatch

Each parallel task gets its own complete pipeline: implement → spec review → quality review. This reuses the existing SDD prompts (`implementer-prompt.md`, `spec-reviewer-prompt.md`, `code-quality-reviewer-prompt.md`).

### Per-Task Agent Dispatch

The orchestrator (SDD) dispatches multiple Agent tool calls in a single message — one per ready task. Each agent gets:
- The full task description (steps, file list, code snippets from the plan)
- The design spec content (for context)
- A constraint: **only modify files listed in your task's `Files:` section**
- Expected output: status (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) + summary of changes

### Review Pipeline

Each task's full review pipeline (implement → spec review → quality review) runs within its own Agent call. The agent dispatches reviewers as subagents within its own context. Multiple task pipelines run concurrently across different Agent calls.

### Orchestrator Responsibilities

1. Track which tasks are in-flight, completed, or failed
2. When a wave returns, process each task's result:
   - **DONE** (passed both reviews): mark task complete in the plan (`- [x]`)
   - **DONE_WITH_CONCERNS**: read concerns, address if needed, mark complete
   - **NEEDS_CONTEXT**: surface the question to the user. Queue the task for re-dispatch after the user responds. Other completed tasks in the wave still count. **The orchestrator does not pause** — it immediately recomputes the ready set from all completed tasks and dispatches any tasks that are ready and not blocked by the NEEDS_CONTEXT task. Once the user responds, the blocked task re-enters the ready set in the next cycle
   - **BLOCKED**: assess the blocker (same as current SDD). Queue for re-dispatch or escalate. Same non-blocking behavior as NEEDS_CONTEXT — other ready tasks continue
3. Recompute ready set and dispatch next wave
4. When all tasks are done, proceed to final code review as today

### File Constraint Enforcement

- **Plan-time:** writing-plans validates no overlap between parallel-eligible tasks
- **Execution-time:** before dispatching a wave, orchestrator checks declared file lists. If overlap detected at runtime (e.g., plan was modified during implementation), fall back to sequential for those tasks

### Git Commit Strategy

Since parallel tasks modify non-overlapping files (enforced by file-list validation), parallel commits to the same branch are safe. Each subagent commits its own changes independently. Commit ordering is non-deterministic across parallel tasks but deterministic within a single task's steps. This is acceptable because the tasks are independent by definition.

## Changes to Existing Skills

### Modified Files

1. **`skills/writing-plans/SKILL.md`**
   - Every task must have a `**Depends on:**` line
   - Plan-time file overlap validation for parallel-eligible tasks
   - Guidance that dependencies include logical dependencies (imports, shared interfaces), not just file overlap
   - Updated task structure example to include the new field

2. **`skills/subagent-driven-development/SKILL.md`**
   - Dependency graph parsing and wave computation (with worked step-by-step example)
   - Max concurrency of 3 concurrent tasks
   - Parallel Agent dispatch (multiple Agent calls in one message)
   - Runtime file overlap validation as safety net
   - Wave-based execution: dispatch batch, wait for all, recompute, repeat
   - Handling of NEEDS_CONTEXT/BLOCKED: surface to user, queue for next cycle
   - Replace red flag "Don't dispatch multiple implementation subagents in parallel" with "Don't dispatch implementation subagents that modify the same files in parallel"

3. **`skills/dispatching-parallel-agents/SKILL.md`**
   - Merge best patterns (agent prompt structure, verification steps, decision flowchart) into SDD
   - Keep as standalone skill for ad-hoc parallel debugging outside the implementation workflow (different use case: investigating independent failures, not executing plan tasks)

4. **`templates/plan.md`**
   - Structural change from flat checklist to heading-based task format with `**Files:**` and `**Depends on:**` metadata per task

5. **`skills/implementing/implementer-prompt.md`**
   - Add file constraint reminder: only modify files listed in your task's `Files:` section

6. **`skills/writing-plans/plan-document-reviewer-prompt.md`** (if exists, or inline review instructions)
   - Update to validate new plan format: every task must have a `**Depends on:**` line, dependency references must point to valid task numbers

### Unchanged Files

- `skills/implementing/SKILL.md` — Still just invokes SDD
- `skills/implementing/spec-reviewer-prompt.md` — No changes
- `skills/implementing/code-quality-reviewer-prompt.md` — No changes

## Edge Cases & Failure Modes

### Circular Dependencies

If the dependency graph has a cycle, the orchestrator detects this during step 2 of the algorithm (before execution begins). If a cycle is found, it reports immediately: "Circular dependency detected — the following tasks form a cycle: [list]. Please fix the plan." Execution does not start until the cycle is resolved.

### All Tasks in a Wave Fail

If every task in a wave returns NEEDS_CONTEXT or BLOCKED, the orchestrator surfaces all blockers to the user at once rather than looping. Same max-retry behavior as current SDD.

### Plan Modified Mid-Implementation

Tasks can be added/removed during implementation (already supported). Each cycle, the orchestrator re-parses the plan file. New tasks with `**Depends on:** none` become immediately eligible. New tasks with dependencies wait normally.

### Single-Task Plans

If a plan has no parallelizable tasks (every task depends on the previous), the wave executor degrades gracefully to sequential execution — identical to current SDD behavior. No special case needed.

### Missing `Depends on:` Line

Treated as a plan validation error. The orchestrator warns and falls back to fully sequential execution for safety rather than assuming no dependencies.

### Failed Task Retry and Repo State

When a task fails and is retried, the repo already contains commits from other parallel tasks that succeeded. This is safe because parallel tasks modify non-overlapping files — the failed task's retry operates only on its own files, and other tasks' commits are irrelevant to it.

## Design Decisions

1. **Dependency graph over batch syntax** — More flexible scheduling. Tasks unblock as soon as their specific dependencies complete, not when an entire batch finishes.
2. **File-list validation over worktrees** — Simpler. No merge step. If tasks share files, run them sequentially.
3. **Wave-based execution** — Matches Agent tool semantics (dispatch N, wait for N). Simpler than streaming. Acceptable trade-off: some tasks may wait slightly longer than theoretically necessary.
4. **Max 3 concurrent tasks** — Practical limit for context window, rate limits, and system resources. Can be adjusted based on experience.
5. **Plan-time + execution-time validation** — Belt and suspenders. Catch issues early, enforce at runtime.
6. **Keep dispatching-parallel-agents for debugging** — Different use case (ad-hoc investigation vs plan execution). Merge implementation patterns into SDD but keep the debugging skill.
7. **Prompt instructions over code** — Dependency resolution lives in skill markdown with a worked step-by-step example. Plans have 5-15 tasks — this is well within LLM capability for simple graph operations when given a concrete algorithm to follow.
