---
name: reviewing
description: "Use when the current afyapowers phase is review — performs 2-step code review (spec compliance + quality)"
---

# Review Phase

Perform a comprehensive 2-step code review of the completed feature implementation.

## Phase Gate

If this skill was invoked by `/afyapowers:next` (you already know the active feature slug and confirmed the phase is `review` from the conversation context above):
- Skip steps 1-3 and proceed to Gather Context

Otherwise (direct invocation):
1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `review`
3. If not in review phase, tell the user the current phase and stop

## Process

### Step 0: Create the phase task list (ordering enforcement)

Before gathering context, create this phase's steps as tasks in the platform's task-tracking tool
(Claude Code: `TaskCreate` + `TaskUpdate` with `addBlockedBy`; other agents: the equivalent task/todo
tool — without dependency support, keep the numbering and enforce the chain by protocol), each blocked
by the previous:

- **T1** Gather context (Step 1)
- **T2** Dispatch both reviewers in parallel (Step 2); stays `in_progress` until both report
- **T3** Consolidate + fix via subagent + re-review (Step 3); only completes when every Critical/
  Important finding and spec gap is resolved or explicitly escalated to the user
- **T4** Produce review.md (Step 4) — **additionally blocked by T3**: the artifact is written once,
  after the loops close, never before
- **T5** Complete (Step 5)

Mark `in_progress` before starting, `completed` only with the exit condition met; never start a blocked
task.

### Step 1: Gather Context

1. Read from `.afyapowers/features/<feature>/artifacts/design.md` the sections the spec review needs: `## Requisitos`, `## Casos de Borda & Estados`, `## Árvore de Componentes de DS`, `## Decisões de Reúso de Componentes`, `## Contrato de Layout`, `## Questões em Aberto` — **not the whole document** (the Figma inventory, JIRA transcription, and architecture prose are not spec-compliance inputs; the DS/token fidelity was already verified per task by the figma-token-verifier during implement)
2. Read the plan's **task list and checkboxes** from `.afyapowers/features/<feature>/artifacts/plan.md` (headings + `**Type:**`/`**Depends on:**` lines suffice — not the task bodies)
3. Identify the base and head commit SHAs for the feature's changes (use `git log`)
4. Run `git diff --stat <base_sha>..<head_sha>` to get a compact summary of changed files
5. Read `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` if it exists — these are concerns flagged by implementers during the implementation phase. Note its two sections: **Impedimentos** (output diverges from the design/Figma in look or behavior) and **Ressalvas**. Each blocking concern must be verified as either fixed in the diff or explicitly accepted by the user; any that is neither forces a **Alterações Solicitadas** verdict (see Step 4). A blocking-concern line carrying an `[ACCEPTED BY USER: <reason>]` marker counts as explicitly accepted — the acceptance was recorded during implementation and needs no fresh confirmation this session.

**Do NOT capture the full `git diff` output.** The review agents will read code and diffs themselves using their tool access.

### Step 2: Dispatch Both Reviewers — in parallel

Dispatch @"spec-reviewer (agent)" and @"code-quality-reviewer (agent)" **in the same turn**. They read
different things for different questions and neither's input depends on the other's output — serializing
them was measured at ~25 minutes of pure waiting. A spec fix that later invalidates part of the quality
review is the rare case; re-dispatching the quality reviewer for the affected files (its max-2 loop)
costs less than always serializing.

To @"spec-reviewer (agent)":
- Provide the design sections gathered in Step 1 as "what was requested" — **including `## Árvore de Componentes de DS` and `## Decisões de Reúso de Componentes` when present.** Those hold the per-component verdicts the user confirmed, and verifying the code honored them is spec compliance, not a style question
- Provide a summary of implemented changes as "what was built"
- Provide the base and head commit SHAs and the `git diff --stat` summary (the agent will read code and diffs itself)
- Include a "Priority Areas" section with the contents of `implementation-concerns.md` (or "No concerns were flagged." if the file doesn't exist)

To @"code-quality-reviewer (agent)":
- Provide: what was implemented, plan reference, description
- Provide the base and head commit SHAs and the `git diff --stat` summary (the agent will read code and diffs itself)
- Include a "Priority Areas" section with the contents of `implementation-concerns.md` (or "No concerns were flagged." if the file doesn't exist)

### Step 3: Consolidate Findings and Fix — via subagent

Consolidate both reports. Categorize quality findings by severity (Critical, Important, Minor): Critical
and Important must be fixed before proceeding; Minor is noted, never blocks. Spec gaps always block.

**Apply the fixes through a fix subagent, not in this conversation.** Dispatch @"tdd-implementer (agent)"
with a synthetic task: the consolidated findings (each with file:line and the reviewer's rationale), the
allowed file list, and the requirement that each fix keeps/extends test coverage. Applying dozens of
Read/Edit/test turns in the orchestrator context re-sends the entire review-phase context on every one of
them; the fix subagent does it in a small fresh context and reports back. Verify its report against the
findings (spot-check the diffs), then:

- Re-dispatch each reviewer whose findings required fixes, **scoped to the affected findings/files** (max 2 iterations per reviewer)
- If still unresolved after 2 iterations, report remaining issues to the user and ask them to decide how to proceed

### Step 4: Produce Review Artifact

Read the template from `<plugin-root>/templates/review.md` (`<plugin-root>` = the `Plugin root:` path injected at session start; templates live at the plugin root, NOT inside the skill directory). Fill in:
- Spec compliance findings and resolutions
- Code quality findings and resolutions
- **`## Conformidade de Design System`** (only when the design has `## Árvore de Componentes de DS`): one row per tree node, recording the confirmed verdict, where it landed in the code (`arquivo:linha`), and whether the code honored it. Plus the composition/variant checks and which annotations and edge-case states were actually covered. A node whose verdict was `Importar` but which appears in the diff as a **new definition** is a duplicated design-system component — record it as Critical, because it is permanent, invisible in review of the file itself, and will drift from the real component from day one
- Blocking-concern findings: for each blocking concern from `implementation-concerns.md`, record whether it was fixed in the diff or explicitly accepted by the user, with the resolution. A concern line marked `[ACCEPTED BY USER: <reason>]` is "Accepted by user" — use the marker's reason as the resolution.
- Final verdict (in the `## Veredito` section): write exactly **Aprovado** — only if the spec compliance review passes, the code quality review passes, **and** every blocking concern is fixed or explicitly accepted (including those carrying an `[ACCEPTED BY USER: …]` marker). Any of the above failing, or any unresolved/unaccepted blocking concern → **Alterações Solicitadas**.

Save to `.afyapowers/features/<feature>/artifacts/review.md`

### Step 5: Complete

Update `state.yaml` to add `review.md` to the review phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Fase review concluída. Rode `/afyapowers:next` para avançar para **complete**."

**Important:** The verdict MUST be **Aprovado** for `/afyapowers:next` to accept the transition. If issues remain, keep the verdict as **Alterações Solicitadas** and work with the user to resolve them.
