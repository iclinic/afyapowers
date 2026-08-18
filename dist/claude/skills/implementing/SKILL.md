---
name: implementing
description: "Use when the current afyapowers phase is implement — orchestrates implementation via subagent-driven-development"
model: sonnet
effort: medium
---

# Implementing Phase

Orchestrate plan execution by delegating to subagent-driven-development.

**Announce at start:** "Estou usando a skill implementing para executar o plano."

## Phase Gate

If this skill was invoked by `/afyapowers:next` (you already know the active feature slug and confirmed the phase is `implement` from the conversation context above):
- Skip steps 1-3 — use the slug from context
- Read the plan and design (steps 4-5) — these are working content needed for implementation

Otherwise (direct invocation):
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
   - Each worktree updates the canonical feature plan at `.afyapowers/features/<feature>/artifacts/plan.md` in its own branch, but may only mark the tasks assigned to its group
   - After all worktrees finish, merge them back into the parent branch and verify the parent plan has all tasks marked `[x]`
   - If all tasks are `[x]`, the implement phase is complete: run `/afyapowers:next` on the parent feature to proceed to review
   - If some tasks remain unchecked after the merge, stay in the implement phase and continue from the remaining tasks
   - **STOP here** — do not invoke SDD in this run (the worktrees handled implementation)

## Invoke Sub-Skill

**REQUIRED:** Invoke `afyapowers:subagent-driven-development` via the Skill tool to execute all plan tasks.

- Announce: "Usando o subagent-driven-development para executar as tarefas de implementação."
- Invoke the skill. Follow its instructions completely.
- The plan content and design are already in the conversation context — SDD will use them directly.
- After SDD completes, resume the parent flow below.

## After SDD Completes

1. Verify all plan checkboxes are marked complete (`- [x]`)
2. If any remain unchecked, report which tasks are incomplete and ask the user how to proceed
3. Update `state.yaml` to reflect progress
4. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` exists, read it and handle the two severities differently:
   - **Impedimentos** (output diverges from the design/Figma in look or behavior): do **NOT** smoothly advance. Present each blocking concern to the user and require an explicit decision per concern — **fix now** (loop back into implementation to resolve it) or **explicitly accept the divergence** (record the acceptance by appending `[ACCEPTED BY USER: <reason>]` to that concern's line in `implementation-concerns.md`). Only once every blocking concern is resolved or accepted may you suggest `/afyapowers:next`.
     - **Verificação adiada é impedimento:** a concern whose text merely defers verification to a later step (adia verificação) — e.g. "will validate in review", "not verified now, check in review" — is itself an **Impedimento**, never a Ressalva, even if it was filed as non-blocking. Reclassify it under Impedimentos and apply the same fix-now-or-accept gate above before advancing; the phase does not advance on the strength of a promise to verify later.
   - **Ressalvas:** mention them — "Ressalvas foram coletadas — serão priorizadas durante a fase de review." These do not gate advancement.
5. Tell the user: "Fase implement concluída. Rode `/afyapowers:next` para avançar para **review**." (Only after all blocking concerns are resolved or explicitly accepted.)

**This gate is also enforced in code.** `/afyapowers:next` runs `preflight.py`, which reads `implementation-concerns.md` and refuses the implement→review transition while any line under `## Impedimentos` lacks an `[ACCEPTED BY USER: <reason>]` marker. So skipping step 4 does not let the phase advance — it just produces a confusing error at `/afyapowers:next` instead of the conversation the user should have had here. Do the step properly: present each blocking concern, get a decision per concern, and write the acceptance markers as they are given.
