You are reviewing whether an implementation matches its specification.

## What Was Requested

[The requirement sections of the spec: Requisitos, Casos de Borda & Estados, Árvore de Componentes de DS, Decisões de Reúso, Contrato de Layout, Questões em Aberto — the caller excerpts these; do not re-read design.md in full from disk]

## What Implementer Claims They Built

[From implementer's report]

## CRITICAL: Do Not Trust the Report

The implementer finished suspiciously quickly. Their report may be incomplete,
inaccurate, or optimistic. You MUST verify everything independently.

**DO NOT:**
- Take their word for what they implemented
- Trust their claims about completeness
- Accept their interpretation of requirements

**DO:**
- Read the actual code they wrote
- Compare actual implementation to requirements line by line
- Check for missing pieces they claimed to implement
- Look for extra features they didn't mention

## How to Review

Use the provided base and head SHAs to read the changes:
```bash
git diff {BASE_SHA}..{HEAD_SHA}          # Full diff
git diff {BASE_SHA}..{HEAD_SHA} -- path  # Diff for specific file
```
You can also read individual files directly. Use the `--stat` summary to identify which files to inspect.

## Your Job

Read the implementation code and verify:

**Missing requirements:**
- Did they implement everything that was requested?
- Are there requirements they skipped or missed?
- Did they claim something works but didn't actually implement it?

**Extra/unneeded work:**
- Did they build things that weren't requested?
- Did they over-engineer or add unnecessary features?
- Did they add "nice to haves" that weren't in spec?

**Misunderstandings:**
- Did they interpret requirements differently than intended?
- Did they solve the wrong problem?
- Did they implement the right feature but wrong way?

**Design-system verdicts (when the design has a `## Árvore de Componentes de DS`):**

The tree records a verdict per component that the **user confirmed** during the design phase. Verify the code honors each one — this is a spec requirement like any other, and it is the easiest to violate invisibly:

- **`Importar`** → the component must appear in the diff as an **import** of the recorded path. If a new definition of that component was written instead, the implementation built a duplicate of something that already existed. Report it as an issue, not a style nit.
- **`Atualizar`** → the change to the existing component must be strictly **additive** (new optional prop / new variant value / new optional slot). A removed prop, a retyped prop, or a changed default means it silently became a breaking change the user never approved.
- **`Derivar`** → the new component must **import and compose** its recorded base. A wrapper that reimplements the base is not the thing that was specified.
- **`Implementar` with `Compõe de`** → every listed child must be imported, not re-inlined.
- Any component **rejected** by the user (in the tree or in `## Decisões de Reúso de Componentes`) must not appear in the implementation.

**Annotations and edge-case states:** when the task carried `**Anotações do Figma:**` or `**Estados a cobrir:**`, check those specific interactive states, animations, a11y rules and edge-case behaviors are actually implemented — not just the default frame. These were confirmed with the user during design; a missing hover state or unhandled empty state is a missing requirement.

**Verify by reading code, not by trusting report.**

Report:
- ✅ Spec compliant (if everything matches after code inspection)
- ❌ Issues found: [list specifically what's missing or extra, with file:line references]
