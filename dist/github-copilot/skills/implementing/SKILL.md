---
name: implementing
description: "Use when the current afyapowers phase is implement — orchestrates implementation via subagent-driven-development"
---

# Implementing Phase

Orchestrate plan execution by delegating to subagent-driven-development.

**Announce at start:** "I'm using the implementing skill to execute the plan."

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

## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:subagent-driven-development` via the Skill tool to execute all plan tasks.

- Announce: "Using subagent-driven-development to execute implementation tasks."
- Invoke the skill. Follow its instructions completely.
- The plan content and design are already in the conversation context — SDD will use them directly.
- After SDD completes, resume the parent flow below.

## After SDD Completes

1. Verify all plan checkboxes are marked complete (`- [x]`)
2. If any remain unchecked, report which tasks are incomplete and ask the user how to proceed
3. Update `state.yaml` to reflect progress
4. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` exists, read it and handle the two severities differently:
   - **Blocking Concerns** (output diverges from the design/Figma in look or behavior): do **NOT** smoothly advance. Present each blocking concern to the user and require an explicit decision per concern — **fix now** (loop back into implementation to resolve it) or **explicitly accept the divergence** (record the acceptance). Only once every blocking concern is resolved or accepted may you suggest `/afyapowers:next`.
   - **Non-Blocking Concerns:** mention them — "Non-blocking concerns were collected — they will be prioritized during the review phase." These do not gate advancement.
5. Tell the user: "Implement phase complete. Run `/afyapowers:next` to proceed to **review**." (Only after all blocking concerns are resolved or explicitly accepted.)
