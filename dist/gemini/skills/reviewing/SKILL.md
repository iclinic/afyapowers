
# Review Phase

Perform a comprehensive 2-step code review of the completed feature implementation.

## Phase Gate

If this skill was invoked by `/afyapowers-dev:next` (you already know the active feature slug and confirmed the phase is `review` from the conversation context above):
- Skip steps 1-3 and proceed to Gather Context

Otherwise (direct invocation):
1. Run `python3 "<plugin-root>/scripts/feature.py" gate review` (plugin root is in your session context). If `match=false`, tell the user the current phase and stop. Use the returned `slug` as the active feature.

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
- Provide the design spec content as "what was requested" — **including `## Árvore de Componentes de DS` and `## Decisões de Reúso de Componentes` when present.** Those hold the per-component verdicts the user confirmed, and verifying the code honored them is spec compliance, not a style question
- Provide a summary of implemented changes as "what was built"
- Provide the base and head commit SHAs and the `git diff --stat` summary (the agent will read code and diffs itself)
- Include a "Priority Areas" section with the contents of `implementation-concerns.md` (or "No concerns were flagged." if the file doesn't exist)

If the reviewer finds spec gaps:
1. Report the findings to the user
2. The user fixes issues (code changes happen during review phase)
3. Follow up on the **same** reviewer instance with only the delta (`<RESUME-REVIEW>`)
4. Repeat until spec-compliant (**max 3 iterations counting the first dispatch**)
5. If still non-compliant after 3 iterations, report unresolved findings to the user and ask them to decide how to proceed

<RESUME-REVIEW>
Iterations 2+ never re-send the spec, the diff summary or the concerns file — the reviewer already has all of it.

- **Claude Code:** send a follow-up to the same reviewer instance with `SendMessage` (its name/id came back with the dispatch; `ListAgents` finds it again, and if `SendMessage` is not loaded yet, load it before falling back to a re-dispatch): the list of issues that were fixed, plus the **new head SHA** and the `git diff --stat` of the corrections, and "Re-verifique apenas esses itens e os que você deixou em aberto; não re-audite o que já aprovou."
- **Other IDEs, or if the instance is no longer reachable:** re-dispatch with the corrections diff plus a one-paragraph recap of the previous findings — never the full spec again.
</RESUME-REVIEW>

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
4. Fix the issues, then follow up on the **same** reviewer instance with only the delta (`<RESUME-REVIEW>` above — same protocol, with the quality findings in place of the spec ones). **Max 3 iterations counting the first dispatch**
5. If still unresolved after 3 iterations, report remaining issues to the user and ask them to decide how to proceed

### Step 4: Produce Review Artifact

Read the template from `templates/review.md`. Fill in:
- Spec compliance findings and resolutions
- Code quality findings and resolutions
- **`## Conformidade de Design System`** (only when the design has `## Árvore de Componentes de DS`): one row per tree node, recording the confirmed verdict, where it landed in the code (`arquivo:linha`), and whether the code honored it. Plus the composition/variant checks and which annotations and edge-case states were actually covered. A node whose verdict was `Importar` but which appears in the diff as a **new definition** is a duplicated design-system component — record it as Critical, because it is permanent, invisible in review of the file itself, and will drift from the real component from day one
- Blocking-concern findings: for each blocking concern from `implementation-concerns.md`, record whether it was fixed in the diff or explicitly accepted by the user, with the resolution. A concern line marked `[ACCEPTED BY USER: <reason>]` is "Accepted by user" — use the marker's reason as the resolution.
- Final verdict (in the `## Veredito` section): write exactly **Aprovado** — only if the spec compliance review passes, the code quality review passes, **and** every blocking concern is fixed or explicitly accepted (including those carrying an `[ACCEPTED BY USER: …]` marker). Any of the above failing, or any unresolved/unaccepted blocking concern → **Alterações Solicitadas**.

Save to `.afyapowers/features/<feature>/artifacts/review.md`

### Step 5: Complete

Record it: `python3 "<plugin-root>/scripts/feature.py" record-artifact review.md` (updates `state.yaml` and `history.yaml`; confirm `ok=true`).

Tell the user: "Fase review concluída. Rode `/afyapowers-dev:next` para avançar para **complete**."

**Important:** The verdict MUST be **Aprovado** for `/afyapowers-dev:next` to accept the transition. If issues remain, keep the verdict as **Alterações Solicitadas** and work with the user to resolve them.
