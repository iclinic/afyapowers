---
name: afyapowers:implementing
description: "Use when the current afyapowers phase is implement — orchestrates implementation via subagent-driven-development"
---

# Implementing Phase

Orchestrate plan execution by delegating to subagent-driven-development.

**Announce at start:** "I'm using the implementing skill to execute the plan."

## Phase Gate

1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `implement`
3. If not in implement phase, tell the user the current phase and stop
4. Read the plan from `.afyapowers/features/<feature>/artifacts/plan.md`
5. Read the design from `.afyapowers/features/<feature>/artifacts/design.md` for context

## Validate Plan

- Parse all tasks from the plan (checkbox items: `- [ ]` and `- [x]`)
- If all tasks are already complete, tell the user and suggest `/afyapowers:next`
- If uncompleted tasks remain, proceed to execution

## Parallel Split Analysis

Before dispatching tasks, check if the plan can be split into independent parallel groups.

### Detect disconnected components

1. Parse all tasks from the plan: extract task numbers, `**Depends on:**` lines, and `**Files:**` sections
2. Build the dependency graph
3. Find **disconnected components** — groups of tasks with NO dependencies between them:
   - Start with each task as its own group
   - If Task A depends on Task B, merge their groups
   - If Task A and Task B share files (from `**Files:**` sections), merge their groups
   - After processing all deps and overlaps, count remaining distinct groups

4. **If only 1 group** (all tasks are connected): proceed directly to the SDD invocation below.

5. **If 2+ disconnected groups exist**, analyze each group:
   - List tasks in the group
   - Describe the group by its primary domain (infer from file paths and task names)
   - List key files/directories the group touches

6. **Present the choice to the user:**

```
Your plan has <N> independent task groups with no dependencies between them:

  Group A (Tasks 1, 2, 5): <domain_description>
    Files: <key_directories>

  Group B (Tasks 3, 4): <domain_description>
    Files: <key_directories>

How would you like to execute?

  1) Sequential (default) — one agent implements all tasks using wave execution
  2) Parallel worktrees — creates <N> worktrees with territory-based file isolation,
     each implements its task group, then merges back for unified review
```

7. **If user chooses 1 (Sequential):** proceed to the SDD invocation below.

8. **If user chooses 2 (Parallel):**
   - Invoke `parallel-split` skill with: feature slug, plan content, design content, task groups, parsed tasks
   - The parallel-split skill creates worktrees, each running ONLY the implement phase for its task group
   - **After all worktrees complete and merge back:**
     - Re-read the parent plan.md — verify all checkboxes are `[x]` (worktree merges update the parent plan)
     - If some remain unchecked, report them to the user
     - **Resume the parent flow at "After SDD Completes" below** (the parent continues with review → complete)
   - **STOP here** — do not invoke SDD (the worktrees handled implementation)

## Invoke Sub-Skill

**REQUIRED:** Invoke `afyapowers:subagent-driven-development` via the Skill tool to execute all plan tasks.

- Announce: "Using subagent-driven-development to execute implementation tasks."
- Invoke the skill. Follow its instructions completely.
- The plan content and design are already in the conversation context — SDD will use them directly.
- After SDD completes, resume the parent flow below.

## After SDD Completes

1. Verify all plan checkboxes are marked complete (`- [x]`)
2. If any remain unchecked, report which tasks are incomplete and ask the user how to proceed
3. Update `state.yaml` to reflect progress
4. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` exists, mention it to the user: "Implementation concerns were collected — they will be prioritized during the review phase."
5. Tell the user: "Implement phase complete. Run `/afyapowers:next` to proceed to **review**."
