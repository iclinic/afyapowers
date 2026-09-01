---
name: implementing
description: "Fase implement do afyapowers-dev: orquestra a execução das tarefas do plano. NUNCA invoque por iniciativa própria — roda apenas por invocação explícita do usuário ou da skill next."
---

# Implementing Phase

Orchestrate plan execution by delegating to subagent-driven-development.

**Announce at start:** "Estou usando a skill implementing para executar o plano."

## Phase Gate

If this skill was invoked by `/afyapowers-dev:next` (you already know the active feature slug and confirmed the phase is `implement` from the conversation context above):
- Skip step 1 — use the slug from context
- Read the plan and design (steps 2-3) — these are working content needed for implementation

Otherwise (direct invocation):
1. Run `python3 "<plugin-root>/scripts/feature.py" gate implement` (plugin root is in your session context). If `match=false`, tell the user the current phase and stop. Use the returned `slug` as the active feature.
2. Read the plan from `.afyapowers/features/<feature>/artifacts/plan.md`
3. Read the design from `.afyapowers/features/<feature>/artifacts/design.md` for context

## Validate Plan

- Parse all tasks from the plan (checkbox items: `- [ ]` and `- [x]`)
- If all tasks are already complete, tell the user and suggest `/afyapowers-dev:next`
- If uncompleted tasks remain, proceed to execution

## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers-dev:subagent-driven-development` via the Skill tool to execute all plan tasks.

- Announce: "Usando o subagent-driven-development para executar as tarefas de implementação."
- Invoke the skill. Follow its instructions completely.
- The plan content and design are already in the conversation context — SDD will use them directly.
- After SDD completes, resume the parent flow below.

## After SDD Completes

1. Verify all plan checkboxes are marked complete (`- [x]`)
2. If any remain unchecked, report which tasks are incomplete and ask the user how to proceed
3. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` was created, record it: `python3 "<plugin-root>/scripts/feature.py" record-artifact implementation-concerns.md`
4. If `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` exists, read it and handle the two severities differently:
   - **Impedimentos** (output diverges from the design/Figma in look or behavior): do **NOT** smoothly advance. Present each blocking concern to the user and require an explicit decision per concern — **fix now** (loop back into implementation to resolve it) or **explicitly accept the divergence** (record the acceptance by appending `[ACCEPTED BY USER: <reason>]` to that concern's line in `implementation-concerns.md`). Only once every blocking concern is resolved or accepted may you suggest `/afyapowers-dev:next`.
     - **Verificação adiada é impedimento:** a concern whose text merely defers verification to a later step (adia verificação) — e.g. "will validate in review", "not verified now, check in review" — is itself an **Impedimento**, never a Ressalva, even if it was filed as non-blocking. Reclassify it under Impedimentos and apply the same fix-now-or-accept gate above before advancing; the phase does not advance on the strength of a promise to verify later.
   - **Ressalvas:** mention them — "Ressalvas foram coletadas — serão priorizadas durante a fase de review." These do not gate advancement.
5. Tell the user: "Fase implement concluída. Rode `/afyapowers-dev:next` para avançar para **review**." (Only after all blocking concerns are resolved or explicitly accepted.)

**This gate is also enforced in code.** `/afyapowers-dev:next` runs `feature.py advance`, which reads `implementation-concerns.md` and refuses the implement→review transition while any line under `## Impedimentos` lacks an `[ACCEPTED BY USER: <reason>]` marker. So skipping step 4 does not let the phase advance — it just produces a confusing error at `/afyapowers-dev:next` instead of the conversation the user should have had here. Do the step properly: present each blocking concern, get a decision per concern, and write the acceptance markers as they are given.
