---
claude:
  name: afyapowers:analyzing-design-system
  description: "Resolves every Figma component instance to its ORIGINAL component in the file where it is declared, emits a verdict per node (Implementar/Importar/Atualizar/Derivar), and confirms every decision with the user in compact batches. Requires an origin file URL for every instance whose component is not declared in the file being read. Invoked by the design phase and by /afyapowers:figma-component."
  model: claude-opus-5
  effort: high
cursor:
  name: afyapowers-analyzing-design-system
  description: "Resolves every Figma component instance to its ORIGINAL component in the file where it is declared, emits a verdict per node (Implementar/Importar/Atualizar/Derivar), and confirms every decision with the user in compact batches. Requires an origin file URL for every instance whose component is not declared in the file being read. Invoked by the design phase and by /afyapowers:figma-component."
  model: claude-opus-5
gemini:
  name: analyzing-design-system
  description: "Resolves every Figma component instance to its ORIGINAL component in the file where it is declared, emits a verdict per node (Implementar/Importar/Atualizar/Derivar), and confirms every decision with the user in compact batches. Requires an origin file URL for every instance whose component is not declared in the file being read. Invoked by the design phase and by /afyapowers:figma-component."
github-copilot:
  name: analyzing-design-system
  description: "Resolves every Figma component instance to its ORIGINAL component in the file where it is declared, emits a verdict per node (Implementar/Importar/Atualizar/Derivar), and confirms every decision with the user in compact batches. Requires an origin file URL for every instance whose component is not declared in the file being read. Invoked by the design phase and by /afyapowers:figma-component."
---

# Analyzing Design System

Resolve every Figma component the layout uses to **its original component, in the file where it is declared**, then emit a verdict per node — verified against the real codebase — and confirm **every** verdict with the user before returning.

This is the single design-system brain. Two callers invoke it:

- **The design phase** (`{{skill:design}}`) — entry points are the `### Componentes` entries (`C1`, `C2`…) produced by `{{skill:reading-figma-designs}}`. Output goes back into those entries and into `design.md`.
- **`/afyapowers:figma-component`** (standalone) — the entry point is one target `COMPONENT`/`COMPONENT_SET`. Output goes into the active feature's `artifacts/` when there is one.

Neither caller reimplements these rules. If you are reading a copy of this logic somewhere else, that copy is stale.

<ALWAYS-THE-ORIGINAL>
**Never analyze or implement a component from its instance.** An instance shows one configuration — the variant that screen happened to use. The original holds every variant axis and the real structure; building from an instance produces a permanently poorer duplicate. For every `INSTANCE`, resolve the original in the file that declares it and read it there. If you cannot reach the original, **stop and ask** — never fall back to the instance.
</ALWAYS-THE-ORIGINAL>

<NO-SILENT-DECISIONS>
You do NOT decide anything here. You **analyze**, you **recommend**, and the user **decides**.

Every verdict, reuse, derive-vs-update cut, grouping, proposed name, and tiebreak is confirmed by the user. Decisions are **presented in compact batches** to spare round-trips, but **each node still gets its own explicit answer** — batching the presentation is fine; batching the *approval* ("confirm all?") is not. There is no "obvious case" that skips its question and no auto-approved default: a component that already exists in code still gets asked, because adopting it IS a decision.
</NO-SILENT-DECISIONS>

## Input contract

The caller provides:

- **`fileKey`** — the Figma file key of the layout being analyzed.
- **Entry points** — a single target `nodeId` (standalone) or the `### Componentes` entries (design phase), each already carrying either its original's coordinates or a `Pendência` line.
- **Stored responses already in hand** — any `get_metadata` and `get_code_connect_map` responses the caller already fetched. **Reuse them. Never re-fetch data the caller already holds.**
- **Origin file URLs already known** — from the JIRA issue, the user's request, or a previous run. Candidate origins; still validated (Step 3).
- **Caller mode** — `design` or `standalone` (only affects where output is persisted).

If entry points are missing or empty, report that back rather than guessing.

## MCP budget

Permitted calls: `get_metadata` (on the layout file, and on each **validated component node** the user linked), `get_code_connect_map`, and `get_design_context` — the last one **only** under the conditions in Step 5; it is the most expensive call here and the common path skips it.

Because every origin arrives as a direct node link, you never scan a file: one `get_metadata` per original, addressed exactly. A link with no `node-id` is rejected at the parse gate and costs no call (Step 3).

Forbidden: `get_screenshot` and `get_variable_defs` (they belong to the implementers); re-fetching anything you or the caller already hold. `get_libraries` and `search_design_system` are not used here — they resolve to `libraryKey`/`componentKey`/virtual paths, none of which is a `fileKey` + `nodeId`, so they cannot reach the original; the origin URL is the only path, which is why Step 2 is a hard gate.

Budget ~12 requests/minute. On a 429, wait a jittered **30–60s** and retry — a 429 is transient and does not abort the analysis; if it persists, report it as a concern.

Targeted codebase reads (props/types, Storybook `argTypes`, grep of usages) are permitted — they verify the existence verdict. Do not scan for conventions or tokens beyond that.

**Everything resolved here is persisted and never re-fetched downstream.** Verdicts, coordinates, variant catalogs, and import paths land in `design.md` (Step 8); the plan copies them into tasks and the implementers receive them as `[VERDICT]`/`[BASE_COMPONENT]`/`[COMPOSE_FROM]`. No later phase repeats this analysis or its MCP calls.

## Step 1 — Find every instance whose original you cannot see

Work from the `### Componentes` entries and the layout file's `get_metadata` response. Split by whether the entry already has its original's coordinates:

- **Resolved** — a `COMPONENT`/`COMPONENT_SET` with that node id appears in this file's metadata. Record its node id.
- **Unresolved** — no such node appears; the original is declared elsewhere (another page, or another file).

Keep a **visited-set** of resolved `componentId`s (dedup + cycle guard — never resolve or recurse the same `componentId` twice).

**Beware the depth limit.** The design-phase inventory is built at depth 2 and marks undescended subtrees `(subárvore não explorada)`. An original could be inside one of those — treat it as **unresolved**, not absent: say which case you believe it is and let the URL settle it.

Produce the **unresolved list**: one entry per distinct `componentId`, with the instance-reported name, instance count, and the screens involved. That list is the input to the gate.

## Step 2 — HARD GATE: ask for the pending components' links (one batched ask)

<HARD-GATE>
You may NOT proceed while any component lacks its original's coordinates. Not with a partial set, not with "I'll resolve that one later", and never by reading the instance instead.

**You ask. The user does not have to volunteer anything.** The moment you detect pending components, you request their links.
</HARD-GATE>

**First, spend the links you already have.** Run every origin URL from the input contract through Step 3 and see which pending components it resolves. Only what survives still needs asking.

### The ask — one message listing ALL pending components

Ask **openly, in a single message** (not a choice widget — the answer is a set of URLs only the user can produce). List every pending component in one block, in pt-BR, so the user resolves them in one Figma session and one reply:

> Preciso do link direto do **original** de cada componente abaixo (a instância mostra só a variante que a tela usou):
>
> 1. **Card** — 3 instâncias na tela "Listagem"
> 2. **Pagination** — 1 instância na tela "Listagem"
>
> No Figma: botão direito no componente (diamante roxo, no arquivo onde ele está declarado) → **"Copy link to selection"**. O link vem com `node-id`, assim: `https://figma.com/design/<fileKey>/<nome>?node-id=45-12`
>
> Pode colar todos de uma vez (numerados ou um por linha). Se não souber onde algum está declarado, ou preferir pular algum componente, me diga — pular bloqueia também o que depende dele.

**On reply:** match each link to its component by **validating** it (Step 3) — never by arrival order. Then **re-ask only what failed or is still missing**, naming each miss and its fix in one follow-up message. Repeat until every pending component is resolved, skipped, or declared unreachable.

**Exits (explicit user decisions, stated in the ask):** *skip this component* — record it in the skip set; dependents get blocked or degraded too; *cannot find where it is declared* — the component is reported unreachable and stays out of the tree.

<DIRECT-NODE-LINK-ONLY>
**Only a direct link to the component node is accepted.** A URL without `node-id` is rejected **before any MCP call** — parse, see no `node-id`, re-ask that component. A file-level link does not say *which* component (names collide; matching by name is guessing — exactly the error this gate stops), and resolving one costs a call per page for something the user produces in two clicks. When re-asking, state the miss and the fix:

> Esse link é do arquivo, não do componente — não me diz qual componente é o `Card`. Preciso do link direto: botão direito no componente → "Copy link to selection" (vem com `node-id=...`).
</DIRECT-NODE-LINK-ONLY>

**Do not soften the gate.** No "implement the observed variants for now", no file-level fallback, no proceeding with a subset. Skipping and unreachable are the only unresolved exits, both explicit user decisions.

## Step 3 — Validate every URL before trusting it

A link the user typed is a claim, not a fact. For **each** URL, in order — the parse gate first, so a bad link costs zero MCP calls:

1. **Parse.** Extract `fileKey` (segment after `/design/`) and `node-id` (`X-Y` → `X:Y`). No `node-id` → reject now (no MCP call), re-ask. Present but not matching `^\d+:\d+$` → report BLOCKED rather than passing an unvalidated value into a tool call.
2. **Reachable?** Call `get_metadata(fileKey, nodeId)`. On failure (permission, wrong key, deleted, not found) tell the user exactly what failed and ask for another link.
3. **The original, and the right one?** Both required:
   - **Type** — must be `COMPONENT` or `COMPONENT_SET`. A `FRAME`, `GROUP`, or `INSTANCE` (the most common mistake: an instance *inside* the DS file) → say what you found, re-ask.
   - **Identity** — the node's name must correspond to the component you asked about. If `Card`'s link resolves to `Pagination`, confirm before reassigning — it usually means a wrong selection was copied.
4. **Record two values and a type, then discard the link.** Store origin `fileKey`, node id, and type (`COMPONENT` vs `COMPONENT_SET`); clear the `Pendência` line. A filled coordinate IS the proof of validation — no separate flag, and the URL adds nothing once parsed.
5. **Keep unresolved anything a link did not settle**, with the `Pendência` reason updated — silently dropping an entry re-opens the gate.

`COMPONENT_SET` vs `COMPONENT` changes what "all variants" means for the node — record which it is.

Only when every entry has a validated origin (or an explicit skip/unreachable) do you continue.

## Step 4 — Resolve the tree, recursing leaves→root (bounded)

For each original — resolved in-file (Step 1) or via URL (Step 3):

**Existence gates recursion.** Run the existence check (`get_code_connect_map` + codebase search by name):

- **Exists in code** → recommended verdict `Importar`; **stop — do not recurse into it.** Its internals are already implemented; parents just import it.
- **Does not exist** → it must be built, so **recurse**: read the original's own subtree with `get_metadata` **in its own file**, find its `INSTANCE`s, and put each through Step 1 again (unresolved ones go back through the gate).

**Recursion is bounded at depth 2 from each entry point.** Children at depth 1 and 2 are resolved normally. Anything deeper is **not traversed**: record the node in the tree as `não resolvido — resolver na task do pai`, list it under the parent's **Depende de** with that marker, and add a warning. The parent's implementer task inherits the resolution (it reads the parent's design context and handles the deep child there). This caps the analysis cost on deeply nested trees — a depth-3+ chain of unbuilt components is rare enough that resolving it per-parent at implementation time beats paying O(N) MCP calls up front for every tree.

Each resolved node becomes a tree row with its own verdict; its sub-components go in **Depende de**. A node rendering ≥1 sub-component as a structural child is a **composite**: recommended verdict `Implementar`, children in **Depende de** (built or imported first, then composed — never reimplemented).

**The catalog is always confirmed.** Reading the original in its own file shows every variant axis it declares. If you cannot see the full catalog, you do not have the original — that is a gate failure, not a degraded mode.

## Step 5 — Classify the diff (the reuse-vs-derive cut)

Compare each `INSTANCE` against its resolved original and classify every divergence:

**Content-only** (points to reusing the generic): text (label, placeholder, title); image/icon swap in an existing slot; an existing variant value (`color="error"` when the original declares `color`); slot visibility (`showCloseButton={false}` when the slot exists).

**Structural** (points to deriving): child added/removed (badge over avatar, second CTA); layout changed (column→row, reorder, different gap); composed subcomponent (tooltip wrapping a button); new behavior (drag-and-drop, inline validation, animation); a style no declared variant expresses.

An instance whose divergences are **all** content-only is a **configuration**, not a derivation. Any structural divergence points to a derivative.

**When to fetch `get_design_context` for the diff — the expensive call is conditional:**

- **Skip it (common path):** the original **exists in code** (Code Connect or confident codebase match) AND the code's variant inventory (props/types, Storybook `argTypes`) covers the variants/states the layout uses AND the instance's metadata composition shows no structural divergence. The code inventory + metadata are sufficient evidence for an `Importar` recommendation — fetching the full design context would re-derive what the code already proves.
- **Fetch it (one call, per distinct original):** the original does NOT exist in code (you need its real structure to build it — this feeds the implementer's task context too); OR the required variant looks missing/uncertain in the code inventory (`Atualizar`/`Derivar` boundary needs the original's declared axes); OR the metadata suggests a structural divergence you cannot classify without the original's structure. Never fetch it twice for the same original.

**This classification is your reasoning, not your decision.** Record the diverging fields in the **Paridade** column — the justification shown to the user in Step 8. A style divergence is "structural" only when you can name why no declared variant reaches it; if you cannot, present it as uncertain.

## Step 6 — Recommend a verdict per node, verified against real code

For each original, inspect the **real code** — not just Figma — and recommend one of:

- **`Implementar`** — does not exist in the codebase (not in Code Connect, not found by search). Built from scratch, **from the original**, with every declared variant. A **composite**'s children are listed in **Depende de** and composed, not rebuilt.
- **`Importar`** — exists **and** covers the required variant. No new component code. Check TypeScript props/types/unions (primary), Storybook `argTypes` (secondary), usages (tertiary).
- **`Atualizar`** — exists but is missing a variant the original declares and the layout uses, **and** it can be added **non-breakingly** (new optional prop, variant value, or optional slot).
- **`Derivar`** — a new component that **wraps and composes** the existing base.

**The additive-vs-breaking determination happens here, not at implementation time.** If the variant can only be added by removing a prop, changing a type, or changing a default, recommend **`Derivar`** — never `Atualizar`. Deciding this now keeps the confirmed tree stable so no implementer reclassifies mid-build.

Where the code-derived inventory is low-confidence (weak typing, `...rest` spreads, third-party wrappers), **say so in the recommendation** — reduced confidence is information the user needs.

## Step 7 — Assemble the proposed tree

Order rows **leaves→root**: a node appears after everything it depends on; a `Derivar` node's first **Depende de** entry is always its base.

Columns:

```
Nó (nome Figma) | Arquivo do original (fileKey) | Node-id do original | Tipo Figma | Veredito | Depende de | Paridade | Nome no código (proposto) | Task Type
```

- **Arquivo/Node-id do original** are what the plan hands the implementer, so it reads the original.
- **Task Type** — `UI Component` for `Implementar`/`Atualizar`/`Derivar`; `—` for `Importar` (no task).
- A single self-contained component is a one-row tree.

Alongside the tree, collect **warnings**: orphan candidates, reduced confidence, depth-bounded nodes, anything left out by prioritization.

**Proposals that need the user's decision (carried into Step 8, never self-applied):**

- **Instance grouping** — content-only diffs of one original look like one reuse; equivalent structural diffs look like one derivative per group. Propose; the user confirms.
- **Proposed derivative names** — preserve semantics and **check the codebase for collisions first** (`ProfileCard` exists ⇒ propose `ProfileCardCompact`). Never shadow an existing symbol.
- **Divergent verdict across screens** — present both readings and ask (the more specific, derive, is usually right).
- **Instance with no overrides** — direct use is the obvious reading; still confirm it.

**Prioritize before confirming, when the tree is large (30+ nodes):** present it and ask which nodes to take on before the confirmation loop; record what was left out. Never truncate silently.

**Edge cases — none abort silently:** *truly unreachable original* → report it, keep it out of the tree, name what is blocked (never build from the instance); *cyclic dependency* → the visited-set stops recursion; point at the existing row; *shared component* → a single row, referenced by every parent; *same name, different `componentId`s* → two rows, disambiguated code names; *combinatorial set* (`size × type × state`) → note that each axis becomes an independent prop, never a cartesian union.

## Step 8 — Confirm every decision with the user, in compact batches

This step is the point of the skill. First present the **full proposed tree table** (with Paridade and recommendations) so the user sees the whole picture. Then walk it in **leaves→root** order and confirm in **batches of up to 4 nodes per prompt** — a node is only confirmed after everything it depends on is confirmed, so batch boundaries respect dependency order.

**Use `AskUserQuestion` (or the equivalent choice affordance) with one question per node, up to 4 per call.** Per node, the question carries: what the instance is and which variants the layout uses; **which original you resolved it to** and how; the full declared variant set; the **Paridade** (the justification); your **recommended verdict** (first option, marked as recommended) with the other verdicts as the remaining options; for `Implementar`/`Derivar`, the proposed code name and any collision; and any reduced confidence, stated plainly. This keeps the override one click while cutting a 20-node tree from 20 round-trips to 5.

**Every node gets its own answer.** `Importar` prompts. `Implementar` prompts. Batching groups the questions; it never converts a decision into an assumption, and there is no "confirm all" shortcut.

**Shared components are confirmed once** — a single row, one question; reuse the decision for every parent. Re-asking per parent is noise.

**Rejected dependencies cascade.** If the user declines a node another node depends on, block the parent and ask, per affected parent: **skip the parent too** (default), or **build it without that dependency** (without the child, or with a placeholder). Record the choice; a skipped parent that is itself a dependency re-triggers the question upward.

**Persist as you go — write each batch's confirmations immediately** (a session can end mid-loop):

- **`design` mode** — in `.afyapowers/features/<feature>/artifacts/design.md`: the decision into the `## Árvore de Componentes de DS` row for that `C#`, and the resolution into its `C#` entry under `### Componentes` (`Arquivo do original`, `Node ID do original`, `Tipo`, `Variantes que o original declara`; remove the `Pendência` line). Add new origin files to `### Arquivos` as `F2`, `F3`, …
- **`standalone` mode** — into `.afyapowers/features/<feature>/artifacts/ds-tree.md` when a feature is active; otherwise keep it in conversation and say so.

On re-entry, read what is persisted and **resume from the first unconfirmed node**. Never restart a confirmation the user already partly answered, and never re-ask for an origin URL already recorded and validated.

## Output contract

Return to the caller:

1. **The confirmed tree** — every row keyed by `C#`, carrying the user's decision (and your recommendation where they overrode it). Coordinates live in the `C#` entries, not duplicated here.
2. **The completed `C#` entries** — `Arquivo do original` (+ `F#`), `Node ID do original`, `Tipo`, full declared variant set.
3. **The warnings list** — unreachable originals, reduced confidence, depth-bounded nodes, deprioritized nodes.
4. **The skip set** — nodes the user declined, and parents blocked/degraded as a result.
5. **Import paths** for every `Importar` node.

The caller decides what to do with this. The design phase turns it into plan tasks; the standalone skill dispatches implementers from it. **This skill never implements anything.**

<ASK-SHAPE>
**Choice prompt when the answer is a choice; open question when the answer is a value.** Verdict confirmations (Step 8) are choices among four known values with a recommendation — use the choice widget, batched up to 4 nodes per call. Origin links (Step 2) are values only the user can produce — ask openly, all pending components in one message. The test: could you enumerate the valid answers in advance? If yes, offer them; if the user has to go fetch or type the answer, just ask.
</ASK-SHAPE>
