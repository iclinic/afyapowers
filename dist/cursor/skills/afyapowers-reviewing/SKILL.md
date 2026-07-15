---
name: afyapowers-reviewing
description: "Use when the current afyapowers phase is review — performs 2-step code review (spec compliance + quality)"
model: claude-4-6-sonnet
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

### Step 1: Gather Context

1. Read `.afyapowers/features/<feature>/artifacts/design.md` — the requirements
2. Read `.afyapowers/features/<feature>/artifacts/plan.md` — the implementation plan
3. Identify the base and head commit SHAs for the feature's changes (use `git log`)
4. Run `git diff --stat <base_sha>..<head_sha>` to get a compact summary of changed files
5. Read `.afyapowers/features/<feature>/artifacts/implementation-concerns.md` if it exists — these are concerns flagged by implementers during the implementation phase. Note its two sections: **Impedimentos** (output diverges from the design/Figma in look or behavior) and **Ressalvas**. Each blocking concern must be verified as either fixed in the diff or explicitly accepted by the user; any that is neither forces a **Alterações Solicitadas** verdict (see Step 4). A blocking-concern line carrying an `[ACCEPTED BY USER: <reason>]` marker counts as explicitly accepted — the acceptance was recorded during implementation and needs no fresh confirmation this session.

**Do NOT capture the full `git diff` output.** The review agents will read code and diffs themselves using their tool access.

### Step 2: Spec Compliance Review

Dispatch @"spec-reviewer (agent)":
- Provide the design spec content as "what was requested"
- Provide a summary of implemented changes as "what was built"
- Provide the base and head commit SHAs and the `git diff --stat` summary (the agent will read code and diffs itself)
- Include a "Priority Areas" section with the contents of `implementation-concerns.md` (or "No concerns were flagged." if the file doesn't exist)

If the reviewer finds spec gaps:
1. Report the findings to the user
2. The user fixes issues (code changes happen during review phase)
3. Re-dispatch the spec reviewer
4. Repeat until spec-compliant (max 3 iterations)
5. If still non-compliant after 3 iterations, report unresolved findings to the user and ask them to decide how to proceed

**Gate:** Only proceed to Step 3 once the spec-reviewer reports compliance. Do not start the code quality review on code that will change due to spec issues.

### Step 3: Code Quality Review

Dispatch @"code-quality-reviewer (agent)":
- Provide: what was implemented, plan reference, description
- Provide the base and head commit SHAs and the `git diff --stat` summary (the agent will read code and diffs itself)
- Include a "Priority Areas" section with the contents of `implementation-concerns.md` (or "No concerns were flagged." if the file doesn't exist)

If the reviewer finds issues:
1. Categorize by severity (Critical, Important, Minor)
2. Critical and Important: must be fixed before proceeding
3. Minor: note for later, do not block
4. Fix issues and re-dispatch (max 3 iterations)
5. If still unresolved after 3 iterations, report remaining issues to the user and ask them to decide how to proceed

### Step 4: Visual Fidelity Review

Only run this step if `artifacts/design.md` marks `verificacao_visual: aplicável` for at least one task. If every task in `artifacts/design.md` is `verificacao_visual: não-aplicável`, skip this step entirely — do not dispatch the agent, and omit the "Revisão de Fidelidade Visual" section from the review artifact in Step 5.

Dispatch @"visual-fidelity-reviewer (agent)":
- Provide the Contrato de Verificação and Contrato de Layout from `artifacts/design.md`
- Provide the list of tasks marked `verificacao_visual: aplicável`
- Provide the contents of `implementation-concerns.md` so the agent can identify per-task code-only overrides (marker `[ACCEPTED BY USER: <reason>]`). For any task carrying that marker, the agent **skips** the visual verification for that task — this is not a silent PASS; the agent records the skip and the accepted reason instead
- The agent invokes the `visual-verification` skill itself, per applicable task/breakpoint/state — do not invoke that skill directly from this skill, and do not re-verify visually yourself

The agent returns, per task: PASS/FAIL/Pulado por override, with the measured values cited, plus any skeleton↔component boundary violations found.

If the agent reports FAIL for any task without an accepted override, or reports a boundary violation:
1. Report the findings to the user
2. The user fixes issues
3. Re-dispatch the visual-fidelity-reviewer (max 3 iterations)
4. If still failing after 3 iterations, report unresolved findings to the user and ask them to decide how to proceed

**Gate:** The overall review verdict cannot be **Aprovado** unless the visual-fidelity-reviewer reports **Aprovado**, or this step was skipped because no task required visual verification.

### Step 5: Produce Review Artifact

Read the template from `templates/review.md`. Fill in:
- Spec compliance findings and resolutions
- Code quality findings and resolutions
- Blocking-concern findings: for each blocking concern from `implementation-concerns.md`, record whether it was fixed in the diff or explicitly accepted by the user, with the resolution. A concern line marked `[ACCEPTED BY USER: <reason>]` is "Accepted by user" — use the marker's reason as the resolution.
- The `## Revisão de Fidelidade Visual` section, only when Step 4 ran: fill the findings table with any issues/boundary violations reported by the visual-fidelity-reviewer, the evidence table with one row per task/breakpoint/state verified (path under `artifacts/visual-checks/`), listing tasks skipped by an accepted override as PULADAS rather than failed, and the "Veredito da Fidelidade Visual" line with the agent's Aprovado/Alterações Solicitadas verdict. If Step 4 was skipped (no task required visual verification), omit this section entirely.
- Final verdict (in the `## Veredito` section): write exactly **Aprovado** — only if the spec compliance review passes, the code quality review passes, the visual fidelity review is Aprovado (or was skipped because no task required it), **and** every blocking concern is fixed or explicitly accepted (including those carrying an `[ACCEPTED BY USER: …]` marker). Any of the above failing, or any unresolved/unaccepted blocking concern → **Alterações Solicitadas**.

Save to `.afyapowers/features/<feature>/artifacts/review.md`

### Step 6: Complete

Update `state.yaml` to add `review.md` to the review phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Fase review concluída. Rode `/afyapowers:next` para avançar para **complete**."

**Important:** The verdict MUST be **Aprovado** for `/afyapowers:next` to accept the transition. If issues remain, keep the verdict as **Alterações Solicitadas** and work with the user to resolve them.
