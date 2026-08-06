---
name: afyapowers-design
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and produces a full technical design."
model: claude-opus-5
---

# Design Phase

Help turn ideas into fully formed technical designs through natural collaborative dialogue.

Start by gathering the **requirements** — JIRA, Figma, and clarifying questions — *before* looking at any existing code. Only once the requirement is locked do you explore the codebase. Then present the full design — from requirements through architecture — and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

<REQUIREMENTS-BEFORE-CODE>
Do NOT read project files, docs, or git history before requirements are gathered (JIRA + Figma + clarifying questions). Exploring existing code first anchors the design on what already exists and biases it toward reusing whatever you happen to find — the exact failure mode where a design reuses a component that doesn't match the actual requirement. Gather the requirement first; explore the codebase only afterward, and evaluate any reuse candidate **against** the requirement, never as the starting point. You may rely on what the user's request, JIRA, and Figma tell you to frame questions — but no codebase reads until the dedicated exploration step.

**One exception — referenced contracts are requirement inputs, not exploration.** When the requirement points at an API contract (a generated API client, OpenAPI spec, DTO/type definitions, backend endpoint signatures), read that contract surface **before** the question rounds: endpoint shapes, field names, types, nullability. Questions asked without the contract in hand get re-litigated once it surfaces. Scope it strictly to the contract — no reuse scanning, no convention reading.
</REQUIREMENTS-BEFORE-CODE>

<QUESTION-ECONOMY>
Every question round costs a full user round-trip — the dominant wall-clock cost of this phase. Three rules:

1. **Evidence pre-answers questions — it never skips them.** Before any question round, exhaust the evidence in hand: Figma inventory, annotations, **real rendered texts and variant geometry**, the JIRA description, the referenced contract. When the evidence settles an item, **do not silently adopt the answer**: present it to the user as a question whose first option is the evidence-backed answer, marked as recommended and citing the evidence (e.g. "O H1 real do Figma (nó `3048:1876`) é 'Transmissões' — usar esse título?"). The user confirms in one click or overrides. What the evidence buys is a *pre-answered* question — cheap to confirm, batched with others — instead of an open one the user has to research; it never buys the right to decide without showing them.
2. **Batch related questions** — up to 4 per message via `AskUserQuestion`, grouped by theme (scope, data contract, states, layout), each with options and your recommendation first. Never one-question-at-a-time when a batch is ready; never pad a batch with questions whose answers the evidence already gives.
3. **Decision by exception for low-consequence items.** Items where any reasonable option works (visual fallbacks, tiebreaks, copy details) are presented as a block: "N decisões de baixa consequência — recomendo os defaults abaixo; aceite o bloco ou ajuste os que discordar", listing each item with its recommendation and one-line rationale. One round instead of N. **High-consequence items — scope, contract shape, who-wins conflicts, states architecture — never enter these blocks**: they get their own explicit question, batched up to 4.

Every decision is still the user's and every finding is still surfaced — these rules compress rounds, never the decision set.
</QUESTION-ECONOMY>

<REQUIREMENTS-GATE>
Requirements are inputs to be challenged, not facts to transcribe. JIRA tickets, Figma annotations, and acceptance criteria are incomplete by default — they describe the happy path and omit states, rules, and edge cases. You MUST interrogate them (Requirements Interrogation step) until contradictions are resolved, edge cases are mapped, business rules are confirmed by the user, and risky assumptions are surfaced. Do NOT write the design doc while any **BLOCKING** interrogation item is unresolved — the user must answer or explicitly defer each one first. Confirming what the inputs already say is not enough; you must actively probe for what they leave out.
</REQUIREMENTS-GATE>

## Phase Gate

1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `design`
3. If not in design phase, tell the user the current phase and stop

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Step 0 — Create the phase task list (ordering enforcement)

Before starting item 1, **create the checklist below as tasks in the platform's task-tracking tool**
(on Claude Code: `TaskCreate` + `TaskUpdate` with `addBlockedBy`; on other agents: the equivalent
task/todo tool), chained so each item is blocked by the previous one. Where the tool has no dependency
support, number the tasks (`T1`, `T2`, …) and enforce the chain by protocol. This is what keeps the
order stable across a long session: instructions fade after 200 turns, but the task list is tracked by
the harness, resurfaces during the session, and makes a violation mechanically visible ("T11 is still
blocked") instead of a memory failure.

- One task per checklist item (T1–T13), each blocked by the preceding item. Extra explicit edges:
  **T11 (write design doc) additionally blocked by T5, T6 and T7** — the three that close decisions.
- Conditional items that don't apply (no JIRA → T1; no Figma → T2, T6, T10) are marked `completed`
  immediately with a note ("não se aplica — sem Figma"), never deleted — the chain stays intact.
- Loops live INSIDE their task: T5 stays `in_progress` across interrogator follow-ups and only completes
  on `BLOCKING items: 0`; T12 spans the whole review loop.
- Protocol per task: mark `in_progress` before starting → do the work → mark `completed`. **Never start
  a task the list shows as blocked (or, without dependency support, whose predecessor is not completed);
  never mark one completed with its exit condition unmet.**

## Checklist

You MUST complete these items in order. **Requirements first (1-4), code exploration only after (5).**

1. **JIRA discovery (offer-based)** — offer the user the chance to provide a JIRA issue key; if provided, fetch and summarize the issue (see below)
2. **Figma discovery (trigger-based)** — check user request against trigger keywords (see below); if match, ask about Figma and run discovery **via the figma-reader subagent** (see below)
3. **Read referenced contracts (evidence, not exploration)** — if the requirement references an API contract (generated client, OpenAPI/DTO files, backend types), read the **contract surface only** now. It is a requirement input, like JIRA and Figma — not codebase exploration (see REQUIREMENTS-BEFORE-CODE)
4. **Ask clarifying questions** — confirm **and challenge** the inputs (see below); batches of up to 4 related questions per message
5. **Interrogate requirements (REQUIRED)** — dispatch @"requirements-interrogator (agent)" on the gathered inputs. **Pre-answer every `RESPONDÍVEL-POR-EVIDÊNCIA` finding from the evidence in hand** (Figma inventory, annotations, real texts, contract) and present each resolution to the user as a recommended answer to confirm — never adopt it silently. Drive the question loop (evidence confirmations + `DECISÃO-DO-USUÁRIO` questions, batched) and **follow up with the interrogator after each round of answers** until it returns `BLOCKING items: 0` (see REQUIREMENTS-GATE)
6. **Análise de Design System (só quando há Figma)** — invoke `afyapowers-analyzing-design-system` on the `### Componentes` entries. **HARD GATE:** every component instance whose original is not declared in the file you read requires a direct node link from the user. Check JIRA and the initial request first, then ask for **all** pending components in one open-question message (validating each answer on arrival, re-asking only failures); the phase stops until all are resolved. Then confirm **every** node's verdict with the user — in compact batches of up to 4 nodes per prompt, one explicit answer per node — and record the completed `### Componentes` entries + `## Árvore de Componentes de DS`. Skip entirely when there is no Figma (see below)
7. **Explore the codebase** — ONLY now, with the requirement locked. Read files, docs, recent commits. Identify reuse candidates and evaluate each against the requirement/Figma — never let existing code become the starting point (see REQUIREMENTS-BEFORE-CODE). Apply the **Component Reuse Gate**: ask the user before adopting **any** candidate, without exception. **For every component the design will adopt (`Importar`/`Derivar`/`Atualizar`, DS or not): read its implementation source (the `.tsx`/component file), not just its types or Storybook args** — every behavior the design claims about an adopted component must be verified in its code (see Verify Adopted Components)
8. **Propose 2-3 approaches** — with trade-offs and your recommendation
9. **Present design** — in 2-3 blocks of related sections, get user approval per block (see Presenting the design)
10. **Confirm the Layout Contract (when Figma is present)** — if Figma discovery ran, confirm `## Contrato de Layout` (derived by the figma-reader from `get_metadata`) is present and complete in the design doc; if there is no Figma reference, omit the section (see below)
11. **Write design doc** — save to `.afyapowers/features/<feature>/artifacts/design.md` — only once **all decisions are closed**: no BLOCKING interrogation item open, every DS-tree node confirmed, and **every reuse candidate carrying the user's recorded decision** (see DECISIONS-BEFORE-WRITE). Use **stable requirement IDs** (see Stable IDs)
12. **Design review loop** — dispatch @"design-reviewer (agent)"; fix issues and re-dispatch until approved (max 3 iterations, then surface to human — see After the Design)
13. **User reviews written spec** — ask user to review the spec file before proceeding

**Why the DS analysis comes after the interrogation (item 6, not item 4):** it reads the codebase to
decide what already exists. Requirements must be locked first, or the requirement gets anchored on
whatever the code happens to contain — the same reason as REQUIREMENTS-BEFORE-CODE. A missing DS
component is a code-inventory fact; it must never block requirements gathering.

**The terminal state is suggesting `/afyapowers:next`.** Do NOT invoke any implementation skill or advance phases. The `/afyapowers:next` command handles phase transitions.

## The Process

**Understanding the idea:**

- Do NOT read project files, docs, or git history yet (see REQUIREMENTS-BEFORE-CODE). Work from the user's request, JIRA, and Figma until the dedicated codebase-exploration step.
- Before asking detailed questions, assess scope from the request/JIRA: if it describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then design the first sub-project through the normal flow. Each sub-project gets its own design → plan → implementation cycle.
- For appropriately-scoped projects, ask questions per QUESTION-ECONOMY: batches of up to 4 related questions, multiple choice preferred, recommendation first
- Focus on understanding: purpose, constraints, success criteria

**JIRA discovery (offer-based):**

This is the FIRST step — before any codebase exploration. Offer the user:

> "Is there a JIRA issue associated with this feature? If so, share the issue key (e.g., PROJ-123)."

If the user provides a JIRA issue key:

1. **Resolve the Atlassian cloud ID:**
   - Call `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` (no parameters)
   - If exactly one site is returned, use its `id` as the `cloudId`
   - If multiple sites are returned, present them as a multiple-choice question and let the user pick

2. **Fetch the issue:**
   ```
   mcp__claude_ai_Atlassian__getJiraIssue(
     cloudId: "<resolved_cloud_id>",
     issueIdOrKey: "<user_provided_key>",
     responseContentFormat: "markdown"
   )
   ```

3. **Build the JIRA context summary** from the response:
   - **Summary:** issue summary field
   - **Issue Type:** story, bug, task, epic, etc.
   - **Description:** full description in markdown
   - **Acceptance Criteria:** extracted from description or custom fields if present
   - **Linked Issues:** dependencies, blockers, related issues
   - **Labels / Components:** for categorization context

   Present this summary to the user for confirmation before proceeding.

4. **Proceed to Figma discovery** (the JIRA summary and description text is now part of the context when evaluating Figma trigger keywords)

If no JIRA issue is provided, proceed directly to Figma discovery.

**If the Atlassian MCP server is unavailable:** Warn the user and **stop the JIRA discovery flow**. Do not attempt to proceed without it — the user asked for JIRA context, so a silent fallback would undermine the purpose. Suggest the user check their MCP server connection and retry.

**Figma discovery (trigger-based):**

After JIRA discovery (and still before any codebase exploration), check the user's request for these trigger keywords (case-insensitive, word-level matching):

> page, landing page, screen, view, layout, header, footer, navbar, sidebar, UI component, form, modal, dialog, card, hero, section, banner, responsive, breakpoint, mobile, desktop, dashboard, panel, widget

If any keyword matches, ask the user:

> "Does this feature have Figma designs? If so, please share the Figma URL(s)."

If a keyword matches but the request is clearly not UI work (e.g., "write unit tests for the landing page API endpoint"), use judgment — when in doubt, ask.

If no keywords match, skip Figma discovery and proceed to clarifying questions.

If the user provides Figma URL(s), dispatch @"figma-reader (agent)" with all the URLs and the feature
context. Announce: "Usando o figma-reader para inventariar o Figma." It parses each URL, inventories the
screens and components via a single `get_metadata` call per file, extracts **all** Dev Mode data
annotations and the **real rendered texts** via a read-only `use_figma` call, and derives the Layout
Contract. It returns the complete `## Recursos do Figma` section — `### Arquivos`, `### Breakpoints`,
`### Telas`, `### Componentes` and `### Anotações de Design` — plus `## Contrato de Layout`, ready to
drop into the design doc (template: `<plugin-root>/templates/design.md`).

**Why a subagent:** the raw MCP payloads behind this step (figma-use skill + metadata + annotations)
are ~100k+ characters. In a subagent they are read once and discarded; in the main conversation they
would be re-sent on every turn of the whole phase. Only the structured inventory the subagent returns
enters your context. Never call `use_figma`/`get_figma_skill` in the main design conversation.

Annotations carry semantic intent: business rules, responsive rules, interactive-state behavior,
animations, accessibility rules, content rules, development-specific instructions, spacing, and
more. Treat them as real requirements — business rules flow into the design's requirements, and
the rest into the relevant design sections. Carry them into the clarifying questions below so the
user can confirm them before the design is written.

No `get_screenshot` calls during the design phase — screenshots are deferred to implementation, where
the subagent already calls them per-task. `get_design_context` is called during the design phase in
exactly one place: the DS analysis (checklist item 5) calls it **at most once per distinct DS original,
and only when needed** — an original that already exists in code with the required variants covered is
resolved from the code inventory alone, with no `get_design_context` call (see the sub-skill's Step 5).
It is never called to implement anything.

**If no Figma designs:** Proceed normally. Do not include the Figma Resources section in the design doc.

**Design tokens are NOT extracted during design phase.** They are deferred to implementation time — the implementer subagent will fetch them via `get_variable_defs` when needed.

**Análise de Design System (only when Figma is present):**

This step runs ONLY when Figma discovery produced the Telas/Componentes inventory — skip it entirely for backend/API/CLI/lib features and for UI work with no Figma. It runs **after** the requirements interrogation closes (checklist item 5) and **before** the codebase exploration.

Invoke `afyapowers-analyzing-design-system`. Pass it:

- the `### Componentes` entries the figma-reader returned — which already separate the locally-declared ones from those marked `NÃO RESOLVIDO`;
- the full figma-reader inventory (`### Telas`/`### Componentes` carry every coordinate; the raw `get_metadata` stayed inside the subagent — the sub-skill fetches its own only if the inventory genuinely lacks something);
- **every Figma URL you already have** — from the JIRA issue and from the user's initial request. These are candidate origin files; the sub-skill still validates each one, but handing them over saves the user an exchange;
- caller mode `design`.

It resolves every instance **to its original component in the file that declares it**, checks the real codebase, recommends a verdict per node (`Implementar` | `Importar` | `Atualizar` | `Derivar`), and **confirms every one of them with the user — in compact batches of up to 4 nodes per prompt, each node with its own explicit answer**. It returns the confirmed tree (with the origin fileKey + original node id per node), the validated origin map, the warnings, the skip set, and the import path of every `Importar` node.

**Write the confirmed verdicts to `## Árvore de Componentes de DS`** and complete each component's `C#` entry under `### Componentes` (origin, coordinates, type, validation, declared variants) in `design.md` — the sub-skill persists each row as it is confirmed, so an interrupted session resumes instead of restarting. Omit both sections entirely when the layout uses no component instances.

<HARD-GATE-ORIGENS>
**The design phase STOPS while any component instance has no validated origin file.**

The figma-reader's full-subtree sweep already resolves most origins by itself: a **visible** instance whose original is declared **in the same file** (any page) comes back with coordinates filled — no link needed. What remains unresolved, and what this gate collects, is exactly two cases: the original lives in an **external library file** (`remote` — typically the design system), or the main component could not be resolved at all. **Hidden instances never reach this gate** — the sweep excludes them (they appear only in the `Ignorados (hidden)` line; do not ask for their links). **Icons never reach this gate either** — the reader inventories them in `### Ícones`, and their sourcing (icon lib / local svgs / Figma export / fallback chain) is a strategy decision made with the user in the DS analysis (its Step 7.5), recorded in `## Estratégia de Ícones`. Never ask for an icon's origin link. You cannot analyze or implement a component from its instance: an instance shows only the one variant that screen used, so building from it yields a permanently poorer duplicate of the real component.

So, for **every** unresolved instance, the user must supply the **direct link to the component node**. **Check the JIRA issue and the initial request first** — the design-system links are often already there.

**You do the asking, all pending components in one message.** Do not wait for the user to volunteer links. The moment pending components are detected, **interrupt the phase** and ask, openly, for every pending component's link in a single numbered list — an open question, not a multiple-choice prompt: the answers are URLs the user has to fetch from Figma. Say in the same message that they may skip any component or tell you they cannot find it, and what skipping costs. Validate each answer on arrival (matching links to components by validation, never by order), then re-ask **only** the ones that failed or are still missing.

Tell them how to get it: right-click the component in Figma → **"Copy link to selection"**. The sub-skill owns this loop — see its Step 2.

**Only a direct node link is accepted.** A URL without `node-id` is rejected **before any MCP call** — no `get_metadata`, no page listing, no search. A file-level link does not say *which* component it means, so resolving it would mean matching by name, and names collide (`Card` vs `Card / Legacy`, two `Card`s in different sections). Guessing which original a component maps to is the exact error this gate exists to stop. It also happens to be two clicks of work for the user versus a call per page for us.

Then **validate** each accepted link: the node must be reachable, it must be a `COMPONENT` or `COMPONENT_SET`, and its name must correspond to the component you asked about. A link pointing at a frame, or at another *instance* inside the design-system file, does not count. If it resolves to a different component than the one requested, say which — do not quietly refile it. Say what failed and ask again.

Do not proceed on a partial set, do not defer a component "for later", and never fall back to reading the instance. If the user genuinely cannot produce a link, the analysis stops and reports what is blocked — that is the correct outcome, not a component built from an instance.
</HARD-GATE-ORIGENS>

**Once every origin is validated, a missing component is not a blocker — it is a task:**

- `Implementar` / `Derivar` → the plan phase generates a `UI Component` task, pointing at the **original** in its own file. The component gets built **inside** this feature, with plan review, code review and commits, like any other work.
- `Atualizar` → also a task, but the additive change to a shared component was **approved by the user during this phase**, in the confirmation loop. That approval is what authorizes it; do not let an `Atualizar` reach the plan without it.
- `Importar` → no task. The import path travels into the plan so the consuming screen imports it.

Beyond the origin gate, stop and ask only where the analysis genuinely cannot resolve something: two originals sharing a name, or a tree large enough to need prioritization first.

**Code Connect not configured:** if `get_code_connect_map` indicates Code Connect isn't set up for the file (rather than returning an empty/negative mapping for a specific component), do NOT treat this as "everything is missing." Tell the user Code Connect isn't configured, and fall back to the codebase search alone for the existence check — flagging every affected node as **reduced confidence** so the confirmation loop presents it as uncertain. Do not report an existence verdict as settled when the authoritative source was unavailable.

**No DS components in the layout:** if the layout uses no DS library instances, omit the `## Árvore de Componentes de DS` section and continue normally.

**Component Reuse Gate (always — Figma or not):**

**NEVER adopt an existing codebase or design-system (DS) component into the design without the user's explicit approval.** There is no exception. Reuse is not a default and it is not a conclusion you are allowed to reach on your own — it is a decision that belongs to the user, every single time.

Judge each candidate on three axes and **report** what you found:

- **Name** — does the component's name correspond to what the requirement/Figma calls for? A name mismatch (e.g. `DropdownPicker` for a Figma "Specialty Chip") is a real difference, not a detail.
- **Layout / visuals** — are colors, shape, sizing and states identical to what the requirement/Figma shows?
- **Behavior / interaction model** — is runtime behavior identical: popover vs drawer, inline vs modal, anchored vs full-screen, search vs no-search? This is the axis most often missed — a DS component can look adjustable and behave fundamentally differently.

<NO-SILENT-REUSE>
A match on all three axes is your **recommendation**, never your authorization. Whether the three axes match is itself your judgement, and it is precisely the judgement the user needs to check — so it cannot be the thing that lets you skip asking them.

Present every candidate: name it, state the verdict per axis, name every difference you found, and say what you recommend. Then adopt it **only on explicit approval**. One question per candidate — batched up to 4 candidates per prompt (e.g. via `AskUserQuestion`), each with its own explicit answer.

Example: "Figma shows an inline chip + anchored popover; the DS `DropdownPicker` renders a bottom drawer with a search field — reuse it anyway, or build a custom chip to match Figma?"

And for the case that used to pass silently: "Figma shows a Submit Button; `PrimaryButton` (DS) matches on name, visuals and interaction model as far as I can tell. Reuse it?"
</NO-SILENT-REUSE>

Record every candidate in the `## Decisões de Reúso de Componentes` section of the design doc (template: `<plugin-root>/templates/design.md`), with **both** your recommendation and the user's decision, so any divergence between the two is visible in the artifact. *"If it's different, it's wrong"* unless the user has explicitly accepted the divergence.

<DECISIONS-BEFORE-WRITE>
**The reuse gate closes BEFORE design.md is written — never after.** All reuse-candidate questions are
asked during the codebase exploration (checklist item 7), and the doc is written (item 11) already
carrying every decision. Writing the doc with undecided candidates and patching it as the answers arrive
is a violation: the design-reviewer and the user review would run against a document changing underneath
them, and a decision recorded as an afterthought edit is exactly the kind that skips its cross-references
(requirements, DS tree, tasks). If a new reuse candidate is only discovered while writing, STOP the
write, ask, then resume with the decision in hand.
</DECISIONS-BEFORE-WRITE>

**Division of labour with the DS analysis:** for Figma DS components, `## Árvore de Componentes de DS` is the authority — that is where the verdict and its confirmation live, and each of those nodes was already individually confirmed. This gate covers everything else: any non-DS component from the codebase you are considering adopting. Do not record the same component in both sections; if the two ever disagree about a DS component, the tree wins.

**Clarifying questions — confirm AND challenge (JIRA and/or Figma-informed):**

When JIRA and/or Figma data was gathered, do NOT just play it back for confirmation. Confirmation establishes a baseline; your real job is to **challenge** the inputs. Inputs are incomplete by default — they describe the happy path and omit states, rules, and edge cases.

- **Confirm the baseline:** present the ticket's requirements/AC/scope and what the design shows (structure, breakpoints, hierarchy, annotations) and ask the user to confirm, correct, or extend. Surface annotations explicitly — they encode business rules, behavior, animations, accessibility, dev instructions the user must validate.
- **Then challenge every input.** For each requirement, acceptance criterion, and annotation, actively probe: Does it conflict with another source? What states does it not mention (empty, loading, error, zero/one/many, unauthorized)? What business rule is implied but unstated? What term is vague? What is it quietly assuming (API shape, data presence, layout host)? Confirming "yes that's what it says" is not enough — find what it leaves out.
- Ask about things no source covers: technical constraints, architecture preferences, performance, security/permissions.
- Batch per QUESTION-ECONOMY: up to 4 related questions per message, multiple choice preferred, your recommendation first.

Examples (challenge, not just confirm):
- **With JIRA:** "PROJ-123 says '[summary]'. The AC cover [X, Y] but say nothing about what happens when the list is empty or the request fails — what should those show?"
- **With Figma:** "The Figma annotation says 'disabled until valid', but no validation rules are given. What exactly makes the form valid?"
- **Contradiction:** "JIRA says results are paginated; the Figma annotation describes infinite scroll. Which is correct?"

When neither JIRA nor Figma is available, ask questions one at a time to understand purpose, constraints, and success criteria — and still probe for edge cases, states, and assumptions.

**Requirements Interrogation (REQUIRED):**

After the baseline confirm+challenge pass, run a dedicated adversarial analysis before writing anything. This is a hard gate (see REQUIREMENTS-GATE) — the design doc may not be written while any BLOCKING item is open.

1. **Dispatch @"requirements-interrogator (agent)".** Announce: "Usando o requirements-interrogator para estressar os requisitos." Paste the raw inputs only (NO codebase — exploration comes later): the user's request, the JIRA context, the Figma Telas + Componentes inventory + verbatim annotations + real rendered texts, the referenced contract surface, and the user answers gathered so far. It returns findings across five lenses (contradictions, gaps/business rules, edge cases, ambiguities, risky assumptions), each tagged BLOCKING or non-blocking **and classified `RESPONDÍVEL-POR-EVIDÊNCIA` or `DECISÃO-DO-USUÁRIO`**, plus a `BLOCKING items: N` count.
2. **Pre-answer the evidence-answerable findings — then put them in front of the user.** For every `RESPONDÍVEL-POR-EVIDÊNCIA` finding, resolve it from the evidence — the inventory and texts already in hand, a targeted `get_metadata`/`get_variable_defs` lookup, the contract. **Every resolution is presented to the user as a question whose recommended (first) option is the evidence-backed answer, citing the evidence** — batched up to 4 per message like any other question, mixable with `DECISÃO-DO-USUÁRIO` questions in the same batch. Never adopt an evidence resolution silently: the user must see and confirm (or override) each one before the design is written. What the lookup removes is the user's research burden, not their visibility.
3. **Drive the loop with the user.** Every finding is surfaced — none is silently dropped: deciding an item is not worth asking is itself a decision about the requirement, and it is not yours to make. Apply QUESTION-ECONOMY: evidence confirmations and high-consequence findings as explicit questions in batches of up to 4 (recommended option first); low-consequence `DECISÃO-DO-USUÁRIO` findings as decision-by-exception blocks (defaults + rationale, accept-or-adjust).
4. **Follow up after EVERY round of answers — the follow-up is not optional.** Whenever the interrogator's last response contained any finding, feed the round's outcomes back to it after the user answers: answers create second-order gaps (contradictions among themselves, consequences of the chosen options), and only the interrogator's next pass surfaces them — observed in practice at ~36 second-order BLOCKING items in one feature. The loop **only closes when the interrogator itself returns `BLOCKING items: 0`** — never because you judged the answers complete. A single dispatch is the correct total only when the FIRST response already returns `BLOCKING items: 0`. Keep the payload lean: prefer **continuing the same interrogator agent** with a follow-up message carrying only the new answers/resolutions — its first-dispatch context (inventory, annotations, JIRA) is intact, so nothing is re-sent. If the platform cannot continue an agent, dispatch fresh with **only the findings list + the answers**: second-order gaps live in the decision set, not in the unchanged inventory. Cap: max 3 follow-ups; if BLOCKING items remain after that, surface them all to the user to resolve or explicitly defer each one — do not keep looping.
5. **Resolve or defer.** Every BLOCKING item must end resolved (evidence confirmed by the user, or answered by the user) or explicitly deferred (user chose to). Only then proceed. Reflect confirmed business rules into Requirements, and record the outcomes in the design doc's `## Casos de Borda & Estados`, `## Premissas & Riscos`, and `## Questões em Aberto` sections (Status: resolved / deferred).

**Explore the codebase (only after the requirement is locked):**

Now — and only now — read the project: files, docs, recent commits, existing patterns and components. Doing this *after* requirements keeps the requirement, not the existing code, as the anchor (see REQUIREMENTS-BEFORE-CODE).

- Explore the current structure and conventions so the design fits the project.
- Identify reuse candidates (existing components, utilities, patterns) — but treat each as a *candidate measured against the requirement*, not as the thing the design must bend toward. A candidate that doesn't match the requirement/Figma is not a fit; prefer building to the requirement over retrofitting a near-match.
- Run the **Component Reuse Gate** above on every candidate you would reuse: ask the user before adopting **any** of them (batched up to 4 per prompt, one explicit answer each), no exceptions. Never settle on a reuse the user hasn't approved — and never conclude that a candidate is close enough that asking would be a formality.
- Where existing code has problems that affect the work (a file grown too large, tangled responsibilities), note targeted improvements — but don't propose unrelated refactoring.

**Verify Adopted Components (MANDATORY before writing the design doc):**

For **every** component the design adopts — `Importar`, `Derivar`, or `Atualizar`, DS tree or reuse gate alike — read its **implementation source** (the `.tsx`/component file), not just its `.types.ts` or Storybook args. Every behavioral claim the design makes about an adopted component must be verified against its code: does the prop actually control what the design assumes? Is the element conditional or unconditional? What does the component render when the prop is absent?

This is the single largest source of design-review blockers observed in practice: an interface says `onRetryLabel` and the design concludes the CTA is optional, but the `.tsx` renders the button unconditionally — a spec requirement no component can satisfy, discovered only in review iteration 2. Reading the interface is not reading the component. One targeted read per adopted component, before the doc is written, is far cheaper than a review iteration.

**Stable IDs (design doc conventions):**

Number requirements, premissas, and questões with **stable IDs that are never renumbered**: `R1, R2…`, `P1…`, `Q1…`. A requirement added later gets the next free ID regardless of where it sits logically; a removed one leaves a gap (mark `R7 — removido: <motivo>`). Renumbering breaks every cross-reference in the doc and burns an entire review iteration on reference repair — observed in practice. Cross-reference by ID, never by position.

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the full design
- Present in **2-3 blocks of related sections**, asking for approval once per block — not per section (a ~20-section design approved section-by-section costs ~20 user round-trips for the same decisions):
  1. **Requisitos & Contexto** — problem, requirements, constraints, JIRA context, edge cases & states
  2. **Figma & DS** (when present) — Figma resources, DS tree, reuse decisions, layout contract
  3. **Arquitetura & Entrega** — chosen approach, architecture, data flow, interfaces, error handling, testing strategy, dependencies, premissas, questões em aberto
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- If a block draws corrections, revise and re-present **that block** before moving on
- Cover all sections from the design template: problem statement, requirements, constraints, chosen approach, architecture, data flow, interfaces, error handling, testing strategy, dependencies, and the interrogation outputs — `## Casos de Borda & Estados`, `## Premissas & Riscos`, and `## Questões em Aberto` (with Status)
- If JIRA discovery was performed, include the `## Contexto do JIRA` section with issue key, summary, acceptance criteria, and linked issues
- If Figma discovery was performed, include the `## Recursos do Figma` section with file info, breakpoints, node map, and the `### Anotações de Design` list. Reflect the annotations in the relevant design sections too — business rules in Requirements, the rest wherever they fit (Constraints, Architecture, Error Handling, Testing Strategy) — not just the annotations list.
- If the design reuses any existing non-DS codebase component, include the `## Decisões de Reúso de Componentes` section recording each candidate, its name/layout/behavior parity per axis, **your recommendation**, and **the user's decision** (per the Component Reuse Gate above). Every row must carry a decision the user actually made.
- If Figma discovery ran and the layout uses DS components, include the `## Árvore de Componentes de DS` section with the confirmed tree returned by `afyapowers-analyzing-design-system` — every node's verdict, its dependencies, its confirmed code name, and the import path for `Importar` nodes. This is what the plan phase reads to derive `UI Component` tasks.
- If Figma discovery was performed, confirm `## Contrato de Layout` is present and complete (see below); if there is no Figma reference, omit the section
- Be ready to go back and clarify if something doesn't make sense

**Layout Contract (when Figma is present):**

`## Contrato de Layout` is populated by the figma-reader subagent during Figma discovery (measurements derived from `get_metadata` — container max-width, side margins, gaps, column count, min/max per piece, per breakpoint). It serves as the fidelity guide for the implementer: concrete acceptance measures to hit, per breakpoint.

The design phase's job here is only to GUARANTEE that `## Contrato de Layout` is present and complete in the design doc whenever Figma discovery ran — the design-reviewer must reject the design if it is missing or incomplete in that case. If there is no Figma reference (backend/API/CLI/lib features with no UI, or UI work with no Figma), omit the section entirely (same rule as `## Recursos do Figma`).

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## Required Sub-Skills

**REQUIRED:** Dispatch @"figma-reader (agent)" when the user provides Figma URL(s) — see Figma discovery above.

**REQUIRED:** Dispatch @"requirements-interrogator (agent)" during the Requirements Interrogation step (before exploring the codebase or writing the design) and loop until `BLOCKING items: 0`. See the Requirements Interrogation section above.

**REQUIRED when Figma discovery produced the Telas/Componentes inventory:** Invoke `afyapowers-analyzing-design-system` after the interrogation closes and before exploring the codebase.

- Announce: "Usando o analyzing-design-system para resolver os componentes de DS."
- Pass it the `### Componentes` entries, the inventory the figma-reader returned, every Figma URL you already have (JIRA + initial request), and caller mode `design`.
- It confirms every node with the user (in compact batches, one explicit answer per node) and persists each batch as it goes. Do not confirm nodes yourself in parallel with it, and do not accept a tree with unconfirmed rows.
- Record the returned tree in `## Árvore de Componentes de DS`, then resume the parent flow (codebase exploration).

**REQUIRED:** Dispatch @"design-reviewer (agent)" after writing the design artifact — see the Design Review Loop below.

## After the Design

**Documentation:**

- Write the validated design to `.afyapowers/features/<feature>/artifacts/design.md`
  - Use the template from `<plugin-root>/templates/design.md`. `<plugin-root>` is the `Plugin root:` path the session-start hook injects into the session context (e.g. `…/dist/claude`) — the `templates/` directory lives at the plugin root, **NOT inside this skill's directory**; never look for templates under `skills/`
  - Write it section by section via Write/Edit — never echo the full document back into the conversation
- Commit the design document to git

**Design Review Loop:**
After writing the design document:

1. Announce: "Usando o design-reviewer para validar o design." Dispatch @"design-reviewer (agent)" with the design document path
2. If Issues Found: verify each claim against the code/Figma, fix, re-dispatch, repeat until Approved
3. If loop exceeds **3 iterations**, surface the remaining issues to the human for guidance — the Verify Adopted Components step exists precisely so this loop converges fast

**User Review Gate:**
After the design review loop passes, ask the user to review the written design before proceeding:

> "Design written to `.afyapowers/features/<feature>/artifacts/design.md`. Please review it and let me know if you want to make any changes."

Wait for the user's response. If they request changes, make them and re-run the design review loop. Only proceed once the user approves.

**Completion:**

- Update `state.yaml` to add `design.md` to the design phase's artifacts list
- Append `artifact_created` event to `history.yaml`
- Tell the user: "Fase design concluída. Rode `/afyapowers:next` para avançar para **plan**."

## Key Principles

- **Question economy** - Evidence before questions; batches of up to 4 related questions; decision-by-exception blocks for low-consequence items (see QUESTION-ECONOMY)
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Assume nothing — confirm everything** - Every substantive decision in this phase belongs to the user: which component gets adopted, every DS verdict, every derive-vs-update cut, every proposed name, every interrogation finding. You analyze and recommend; they decide. There is no confidence level, match quality, or "obvious case" that converts a decision into an assumption
- **Never reuse a component without asking** - No exceptions, not even a perfect match on name + layout + behavior. Whether it matches is your judgement, and that judgement is exactly what the user needs to check — so it can never be the reason you skipped asking them
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense
