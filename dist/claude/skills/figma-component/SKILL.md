---
name: afyapowers:figma-component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
model: claude-opus-4-6
effort: high
disable-model-invocation: true
---

# Component Skill

<FORBIDDEN>
Before EVERY Figma MCP tool call, you MUST check:
1. Which phase am I in?
2. Is this tool listed in the current phase's MCP_ALLOWLIST?
3. If NO → STOP. Do not call it. Only the implementer subagent may use it.

NEVER call get_screenshot or get_variable_defs — only the subagent calls these. NEVER call get_design_context to implement the component — that is the subagent's job. (Phase 3 has a single scoped exception: the DS resolution chain in Phase 3 below may call get_design_context per distinct DS original, plus get_libraries / search_design_system / get_context_for_code_connect / get_code_connect_map, for diff/verdict ONLY — see the Phase 3 MCP_ALLOWLIST. These resolve DS originals and emit verdicts; they never implement.)
NEVER launch Explore agents or scan the codebase for conventions, tokens, or patterns — EXCEPT the targeted codebase existence check performed inline in Phase 3 for its 3-way verdict (R4/R8).
NEVER run phases in parallel. Execute Phase 1, then Phase 2, then Phase 3, then Phase 4, then Dispatch, in order.
NEVER implement the component yourself. You are the orchestrator. The subagent implements. Building the DS tree in Phase 3 is analysis, not implementation.
NEVER skip task creation. You MUST create all tasks before starting any work.
NEVER mark a task as completed without actually doing the work.
NEVER start a task that is blocked by an incomplete task.
</FORBIDDEN>

Develop a single Figma component into production code. This skill is **standalone** — not part of the 5-phase workflow.

## Trigger Conditions

**Manual only.** This skill is never auto-invoked. It runs only when the user explicitly runs `/afyapowers:figma-component`. If no Figma URL was provided, ask for it.

---

## Step 0 — Create Tasks

**Before doing ANY work, create all 10 tasks using TaskCreate, then set up dependencies with TaskUpdate.**

Create the following tasks in order:

| # | Subject | Description |
|---|---------|-------------|
| T1 | Phase 1.1: Parse Figma URL | Extract fileKey and nodeId from the Figma URL. Normalize nodeId from `-` to `:` format. |
| T2 | Phase 1.2: Check MCP availability | Verify all 5 required Figma MCP tools are callable. |
| T3 | Phase 1.3: Validate node type via get_metadata | Call get_metadata and confirm the node is COMPONENT or COMPONENT_SET. Store the full response. |
| T4 | Phase 1.4: Check Code Connect via get_code_connect_map | Call get_code_connect_map and check for existing implementation. Store the full response. |
| T5 | Phase 2.1: Check child dependencies from stored metadata | Scan stored metadata for INSTANCE nodes with componentId references. |
| T6 | Phase 2.2: Cross-reference dependencies with Code Connect map | Check each componentId against the stored Code Connect map. Feed the DS analysis; do NOT hard-stop on missing deps. |
| T7 | Phase 2.3: Detect output location, framework, Storybook | Glob for component directories, check package.json, detect Storybook. |
| T8 | Phase 3: Build DS Component Tree | Reusing the stored metadata from T3, run the inline DS resolution chain to detect → resolve → diff → emit verdicts and assemble the `## Árvore de Componentes de DS`. |
| T9 | Phase 4: Present pre-flight + item-by-item confirmation | Show the pre-flight summary and DS tree, then confirm/override each ambiguous verdict and proposed derivative name in leaves→root order. Handle rejected dependencies. |
| T10 | Dispatch implementer subagent(s) per node | For each code-task node (leaves→root), build the extended subagent prompt and dispatch. Each subagent includes self-review against Figma data. Handle the results. |

After creating all 10 tasks, set up dependencies using TaskUpdate `addBlockedBy`:
- T2 blocked by T1
- T3 blocked by T2
- T4 blocked by T3
- T5 blocked by T4
- T6 blocked by T5
- T7 blocked by T6
- T8 blocked by T7
- T9 blocked by T8
- T10 blocked by T9

**Task execution protocol:** For every task:
1. Mark it `in_progress` with TaskUpdate before starting
2. Do the work described in the task
3. Mark it `completed` with TaskUpdate when done
4. Do NOT proceed to the next task until the current one is completed

---

## Phase 1 — Parse & Validate

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: get_metadata, get_code_connect_map.
ANY other Figma MCP call (get_design_context, get_screenshot, get_variable_defs) is FORBIDDEN.
If you are about to call a tool not in this list, STOP. You are violating the skill protocol.
</MCP_ALLOWLIST>

No codebase access in this phase. Only MCP calls allowed: `get_metadata` and `get_code_connect_map`.

### Task T1 — Parse URL

Mark T1 `in_progress`. Extract `fileKey` and `nodeId` from `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>`. Normalize `nodeId` from `-` to `:` format. If no URL provided, ask the user. Mark T1 `completed`.

Hard stop if URL is malformed or missing `node-id`:
```
**STOPPED** — Parse & Validate: Malformed Figma URL or missing node ID.

**What to do:** Provide a valid Figma component URL with the `node-id` parameter. Right-click a component in Figma → "Copy link".
```

### Task T2 — Check MCP availability

Mark T2 `in_progress`. Verify these 5 tools are callable: `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`, `get_code_connect_map`. Mark T2 `completed`.

Hard stop if any are missing:
```
**STOPPED** — Parse & Validate: Required Figma MCP tools are not available.

**What to do:** Ensure the Figma MCP server is connected and running.
```

### Task T3 — Validate node type

Mark T3 `in_progress`. Call `get_metadata(fileKey, nodeId)`. Confirm the node type is `COMPONENT` or `COMPONENT_SET`. Mark T3 `completed`.

**Store the full metadata response. It is reused in Phase 2. Do NOT make additional MCP calls.**

Hard stop if node type is wrong:
```
**STOPPED** — Parse & Validate: The selected node is a <actual_type>, not a COMPONENT or COMPONENT_SET.

**What to do:** Select an actual component in Figma (purple diamond icon), not a frame or instance.
```

### Task T4 — Check Code Connect

Mark T4 `in_progress`. Call `get_code_connect_map(fileKey, nodeId)`. Look for an existing entry matching this component by its Figma component key (from the metadata response). Component key is the authoritative match — not name. Mark T4 `completed`.

**Store the full Code Connect map response. It is reused in Phase 2. Do NOT call this again.**

Hard stop if component already exists:
```
**STOPPED** — Parse & Validate: This component already exists in the codebase at `<existing_file_path>`.

**What to do:** Modify the existing file directly rather than creating a duplicate.
```

---

### Phase Gate: Phase 1 → Phase 2

Before proceeding: verify tasks T1–T4 are all `completed`. If any task triggered a hard stop, do NOT continue.

---

## Phase 2 — Dependencies & Location

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE.
ALL Figma MCP calls are FORBIDDEN in this phase. Use stored data from Phase 1 only.
If you are about to call any Figma MCP tool, STOP. You are violating the skill protocol.
</MCP_ALLOWLIST>

Limited codebase access: only Glob and reading `package.json` / config files. No Explore agents. No scanning for conventions or patterns.

### Task T5 — Check dependencies

Mark T5 `in_progress`. From the **stored metadata response** (Phase 1, Task T3), recursively scan all descendant nodes for `INSTANCE` types with `componentId` references. No MCP calls needed. Mark T5 `completed`.

### Task T6 — Cross-reference dependencies

Mark T6 `in_progress`. For each `componentId` found, check the **stored Code Connect map** (Phase 1, Task T4) for a matching entry. No MCP calls needed. Mark T6 `completed`.

**Do NOT hard-stop on missing dependencies.** Unlike the previous single-node behavior, this skill is now DS-aware: missing children are no longer a dead end. Record which dependencies already exist (Code Connect hit → likely `Importar` candidates) and which are missing (no hit → likely `Implementar`/`Derivar` candidates). This split is an **input to Phase 3** — the DS resolution analysis below resolves every dependency into a tree node with its own verdict, and the Dispatch phase implements the missing ones **leaves→root** in the same run. No "build the children first, then retry" round-trip.

### Task T7 — Detect output location, framework, Storybook

Mark T7 `in_progress`.

**Detect output location.** Glob for existing component directories:
- `src/components/**`
- `src/ui/**`
- `components/**`
- `lib/components/**`
- `packages/*/src/components/**`

**Detect framework.** Check:
- `package.json` dependencies: `react`, `vue`, `angular`, `svelte`
- Config files: `next.config.*`, `nuxt.config.*`, `vite.config.*`
- File extensions in component directories: `.tsx`, `.vue`, `.svelte`

**Detect Storybook.** Glob for `.storybook/` and `*.stories.*`. If not found, skip silently.

Mark T7 `completed`.

---

### Phase Gate: Phase 2 → Phase 3

Before proceeding: verify tasks T5–T7 are all `completed`. If any task triggered a hard stop, do NOT continue.

---

## Phase 3 — Analyze Design System

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: the DS resolution chain ONLY — `get_libraries`, `search_design_system`, `get_design_context` (per distinct DS original, for diff/verdict), `get_context_for_code_connect` (conditional, needs the lib file URL), and `get_code_connect_map`. These run under the budget rules below (R13, ~12 req/min, backoff on 429).
FORBIDDEN in this phase: `get_screenshot`, `get_variable_defs`, and any call whose result you already hold (do NOT re-run `get_metadata` — reuse the T3 response). If you are about to call get_screenshot or get_variable_defs, STOP.
</MCP_ALLOWLIST>

Targeted codebase reads for the existence verdict (R4/R8 — props/types, Storybook argTypes, grep of usages) are permitted here **only as part of** the DS resolution chain below. No Explore agents; no convention/token scanning beyond that verdict check.

### Task T8 — Build the DS Component Tree

Mark T8 `in_progress`. Build the `## Árvore de Componentes de DS` **inline**, for the target `node-id` + `file-key` (from Phase 1, Task T1) and, if the user supplied one, the **DS library file URL**.

**Reuse the stored metadata from Phase 1, Task T3 (R13) — do NOT repeat `get_metadata`.** The instances and their `componentId` references were already scanned from that response in Phase 2, Task T5; reuse that same derived structure here instead of re-deriving it. The resolution chain below starts directly at `get_libraries`.

**Resolution chain, Dev-seat and economical (R13).** Resolve each INSTANCE to its DS original by running the sequence below **in order**, respecting the MCP budget (~12 req/min). Each step has a single purpose; never repeat a call whose result you already hold:

| # | Call | Scope / cardinality | Purpose |
|---|------|----------------------|---------|
| 1 | `get_libraries` | **1×**, cache the returned `libKey`s for this run | Discover the available DS libraries (R2) |
| 2 | `search_design_system` | scoped to the cached DS libraries (not global) | Resolve the original + `assetType` + `componentKey` + docs (R2) |
| 3 | `get_design_context` | **per distinct original, NOT per instance** | Name + main node-id + descriptions/annotations; feeds the diff (R3) |
| 4 | `get_context_for_code_connect` | on the lib's `COMPONENT_SET`, **conditional** — see below | Full variant catalog (R5) |
| 5 | `get_code_connect_map` + codebase search | per original | Existence verdict (R4/R8) |

Budget and cache rules:
- **Cache the `libKey`s** returned by the single `get_libraries` call and reuse them in `search_design_system` — never call `get_libraries` a second time within the same analysis.
- **`get_design_context` is per distinct original, not per instance.** If five instances reference the same `componentId`, make **one** call for that original, not five.
- **Never repeat a call whose result you already have.** Before any call, check whether the data is already in hand (stored metadata, lib cache, context already read).
- **Backoff + retry on 429 (rate limit):** wait **30–60s** and retry. A 429 does **not** hard-stop the phase — it is transient, just a delay. If it persists after retries, report it as a CONCERN, not a fatal error.

**Step 4 is conditional.** `get_context_for_code_connect` on the lib's `COMPONENT_SET` requires the lib file's `fileKey`, which the Figma MCP does not expose (`get_libraries` returns a `libraryKey` hash, not a `fileKey`; `search_design_system` returns `componentKey` + a virtual `filePath`, neither a `fileKey` nor `nodeId`). Therefore:
- This step is possible **only if the user supplied the DS library file URL** (`https://figma.com/design/<fileKey>/...?node-id=...`).
- **Without the lib URL, this is the standard path, not the exception** — go straight to the "catálogo não confirmado" fallback described below. Don't treat this as a failure; it is the common, expected case.
- **Asking for / confirming the DS library URL is therefore a critical, recurring step**, not optional, whenever a generic is being built from scratch.

**Diff instance↔original and the reuse-vs-derive cut.** Compare each INSTANCE against its resolved original (via that original's `get_design_context` plus the instance's composition from the stored metadata). The reuse-vs-derive cut and the content-only-vs-structural classification live in `references/ds-implementation.md` §1 — follow that file, do not duplicate the heuristic here. In summary: content-only diffs (text/image/icon swap, existing variant value, visibility of an existing slot) ⇒ **reuse** the generic with props/variant; structural diffs (added/removed child, layout change, composed subcomponent, new behavior, style outside any existing token/variant) ⇒ **derive** (a wrapper composing the base generic, per `references/ds-implementation.md` §2). Record the diverging fields in the **Paridade** column — it is the justification for the reuse/derive verdict.

**3-way existence verdict, verified against the codebase (R4/R8/R9/R14).** For each original, decide between three verdicts by inspecting the **real code** (not just Figma):
- **Implementar (complete)** — the generic does not exist in the codebase (not in Code Connect, not found by search). Full implementation task for the generic from scratch.
- **Importar** — the generic already exists **and** covers the required variant. The check inspects props/types/union types, Storybook `argTypes`, and codebase usages (TypeScript props as the primary signal, Storybook and usage grep as secondary/tertiary). No new code task — just import.
- **Atualizar (additive)** — the generic exists but is **missing** the required variant, **and** it can be added **non-breakingly** (new optional prop, new variant value, new optional slot). Requires **explicit user approval** (`references/ds-implementation.md` §3.2).

**Hard rule (R9/R14):** the additive-vs-breaking determination happens **here**, in Phase 3. The check inspects the code (props/types/Storybook); if the required variant can **only** be added in a breaking way (prop removal/change, type change, default change), the verdict **already comes out as `Derivar`** — never `Atualizar`. This keeps the confirmed tree stable so Dispatch never has to reclassify at runtime.

Use `get_code_connect_map` + codebase search for the existence check (R4/R8). Where the code-derived variant inventory is low-confidence (weak typing, `...rest` spreads, third-party wrappers), **flag reduced confidence** — the item-by-item confirmation in Phase 4 is the safety net.

**Just-in-time catalog / "catálogo não confirmado" (R5).** When building a generic from scratch (verdict `Implementar`), the full variant catalog is just-in-time:
- **Ask for / confirm the DS library URL** (resolution chain, step 4). With it, read the lib's `COMPONENT_SET` and assemble the full catalog; the **Fonte do catálogo** column becomes `Figma lib <url/libName>`.
- **If the URL is unavailable** (the common path — see above), implement only the **observed** variants/states (those used on the consuming screens, inferred via the consumer's `get_design_context`) and flag **"catálogo não confirmado"**; the **Fonte do catálogo** column becomes `só observado — catálogo não confirmado`. Treat this as the expected, recurring path, with the URL prompt as a standard step.

**Leaves→root order (R6).** Order the tree rows in leaves→root topological order: a component appears **after** all of its dependencies. For `Derivar`, the **first** item in the **Depende de** column is always the base generic the derivative composes — this guarantees the derivative's task only runs after the base generic's task/import.

**Instance grouping and proposed derivative names (§3.5).** Instances of the same original with content-only diffs ⇒ a single "reuse" pattern (one entry). Groups with equivalent sets of structural diffs ⇒ **one derivative per group**, not one per instance. Propose each derivative's code name preserving its semantics, checking for **name collisions** in the codebase before proposing it (`references/ds-implementation.md` §3.5): if it collides, propose an alternative (e.g., `ProfileCard` exists ⇒ `ProfileCardCompact`).

**Edge cases — none of these abort silently:**
- **Orphan original** (INSTANCE whose `componentId` resolves to nothing in any lib or the codebase): implement isolated + warning; verdict `Implementar`, catalog source as available. Record the warning that the original was not found.
- **Inaccessible lib / missing lib URL:** implement **observed** + "catálogo não confirmado" warning. This is **distinct** from an orphan — here the original *was* resolved (via `search_design_system`), but the **full variant catalog** could not be read. It is the **standard** path without the lib URL.
- **429 (rate limit):** backoff 30–60s + retry. Does **not** fail the phase. If it persists, CONCERN, not a fatal error.
- **Ambiguous `search_design_system` match** (more than one candidate): disambiguate using name + description + `componentKey`. If still ambiguous, **confirm with the user** — never guess.
- **Instance with no overrides** (exact copy of the original): use the generic directly; **do not create a derivative**.
- **Multiple instances of the same original:** one resolution (one `get_design_context`), grouped per the rule above.
- **Combinatorial set** (`size × type × state` axes): each axis becomes an **independent prop**, not a cartesian product of variants.
- **Component shared by multiple parents:** a **single entry** in the tree; parents reference it via the **Depende de** column. Never duplicate the row.
- **Divergent verdict across screens** (the same instance shows different diffs on different screens): the **more specific** one wins (derive beats reuse).
- **Tree with 30+ nodes:** ask the user to **prioritize** and **record what was left out** — never truncate silently.

Capture the assembled tree (columns: `Nó (nome Figma · main node-id · componentKey) | Tipo Figma | Veredito | Depende de | Paridade | Nome no código (proposto) | Fonte do catálogo | Task Type`) plus any warnings (catálogo não confirmado, originais órfãos, confiança reduzida de inventário, itens fora de escopo por priorização). Mark T8 `completed`.

For a **single self-contained component with no DS instances**, the tree is a single row (the target itself) — the flow degrades gracefully to the original single-node behavior.

---

### Phase Gate: Phase 3 → Phase 4

Before proceeding: verify task T8 is `completed` and the DS tree is assembled. If any task triggered a hard stop, do NOT continue.

---

## Phase 4 — Present & Confirm (item by item)

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE.
ALL Figma MCP calls are FORBIDDEN in this phase.
If you are about to call any Figma MCP tool, STOP. You are violating the skill protocol.
</MCP_ALLOWLIST>

### Task T9 — Present pre-flight results & confirm item by item

Mark T9 `in_progress`. First show the global pre-flight summary:

```
## Pre-flight Results

- **Target component:** <name> (<COMPONENT | COMPONENT_SET>)
- **Variants:** <count> — <list> (if COMPONENT_SET)
- **DS tree:** <N> nodes — <count Implementar> to implement, <count Derivar> to derive, <count Atualizar> to update, <count Importar> to reuse
- **Suggested directory:** <path> (you can override this)
- **Framework:** <detected> (you can override this)
- **Storybook:** detected — generate story files? (yes/no) | not detected
- **Code Connect:** <target: existing mapping | none>
- **Catalog:** <confirmed | "catálogo não confirmado" for: list of nodes> — provide the DS library URL to confirm the full variant catalog
```

Then print the `## Árvore de Componentes de DS` table so the user can see every node, its verdict, its dependencies, and its proposed code name.

**Confirm item by item, in leaves→root order** (a node is confirmed only after all its dependencies are confirmed). This mirrors the design-phase confirmation (R7, parity). For **each node** whose:

- **verdict is `Atualizar`** — an additive update to an existing generic **always** requires explicit user approval before it is applied (`references/ds-implementation.md` §3.2), regardless of confidence or ambiguity. The standalone path has no broad design-doc review to catch it, so this individual prompt IS the approval gate, OR
- **verdict is ambiguous** (e.g. reduced-inventory confidence on `Importar`/`Atualizar`, `search_design_system` ambiguity, `Atualizar`-vs-`Derivar` borderline, orphan original), OR
- **name is a proposed derivative** (`Derivar` nodes and any renamed generic),

present the node and ask the user to **confirm or override**:
- override the verdict (e.g. `Importar` → `Atualizar`, or `Atualizar` → `Derivar`),
- for `Atualizar`, explicitly approve (or decline) applying the additive change to the existing generic,
- override the proposed code name (e.g. accept `ProfileCardCompact` or supply another),
- accept or decline the "catálogo não confirmado" fallback (or provide the DS library URL now to confirm the catalog).

Nodes with an unambiguous `Implementar`/`Importar` verdict and no proposed derivative name need no individual prompt — present them as already-decided in the tree. (`Atualizar` always prompts, per the first bullet above.)

**Shared components are confirmed once.** A component depended on by several parents appears as a single tree row; confirm it a single time and reuse that decision for every parent — never re-ask per parent.

**Rejected-dependency handling.** If the user rejects a node (declines to implement/derive it) that another node **depends on**, you cannot silently implement the parent. **Block the parent** and ask how to proceed for each affected parent:
- **Skip the parent** too (default), or
- **Implement the parent without the dependency** (the parent renders without that child / with a placeholder).

Record the choice. Default to **skip the parent** if the user does not choose. Cascade: skipping a parent that is itself a dependency re-triggers the same question for its parents.

The user may also override the directory or framework, decline Storybook, or decline the whole run. Mark T9 `completed` after all item-by-item confirmations are resolved.

---

### Phase Gate: Phase 4 → Dispatch

Before proceeding: verify task T9 is `completed` and the user has confirmed the tree (item by item). If the user declined the whole run, STOP. Carry forward the confirmed verdicts, confirmed code names, and the set of nodes to dispatch vs. skip.

---

## Dispatch

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE for the orchestrator.
The implementer subagent will make its own MCP calls (get_variable_defs, get_screenshot, get_design_context) plus 2 review calls.
You as the orchestrator must NOT call any Figma MCP tools here.
</MCP_ALLOWLIST>

### Task T10 — Dispatch implementer subagent(s) per node

Mark T10 `in_progress`. Walk the confirmed DS tree in **leaves→root order** and dispatch @"figma-component-implementer (agent)" **once per code-task node**. A node with a code task is one whose `Task Type` is a code task (e.g. `UI Component`) — i.e. verdict `Implementar`, `Derivar`, or `Atualizar`. **Skip `Importar` nodes** (`Task Type = —`): no new code is dispatched; record the existing import path/symbol so parents reference it.

**Ordering & dependency rules:**
- Never dispatch a node before every node in its `Depende de` column has been dispatched (or is an already-satisfied `Importar`). For a `Derivar` node, its base — the **first** item in `Depende de` — must be implemented/imported first so the wrapper can compose it.
- **Shared components are dispatched once.** A node depended on by several parents is implemented a single time; every parent reuses that result. Never dispatch it per parent.
- **Skipped nodes.** Do NOT dispatch a node the user rejected in Phase 4, nor a parent chosen to be skipped because of a rejected dependency. For a parent confirmed as "implement without the dependency", dispatch it and state in the prompt that the missing child is intentionally omitted (placeholder / rendered without it).

Build each subagent prompt filling in **per node** (from that node's tree row / stored metadata), plus the global confirmed settings:

- `[FILE_KEY]` — the node's Figma file key (the target `fileKey` from Phase 1, Task T1 for nodes in the target file)
- `[NODE_ID]` — the node's main node-id (from its tree row / stored metadata)
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET for that node
- `[VARIANT_LIST]` — variant names for that node (or "N/A — single component")
- `[OUTPUT_DIRECTORY]` — confirmed path from Phase 4
- `[FRAMEWORK]` — confirmed framework from Phase 4
- `[GENERATE_STORYBOOK]` — yes or no from Phase 4
- `[COMPONENT_NAME]` — the confirmed code name for the node (proposed name from the tree, as confirmed/overridden in Phase 4)
- `[VERDICT]` — the confirmed verdict for the node: `implementar` | `importar` | `atualizar` | `derivar` (lowercase). Controls the subagent's behavior mode.
- `[BASE_COMPONENT]` — for `derivar`, the existing generic base the wrapper composes (the first item in `Depende de`); for `atualizar`, the set being extended. Empty otherwise.
- `[CATALOG_SOURCE]` — from the node's `Fonte do catálogo` column, mapped to the subagent's contract: `código` (project code inventory), `Figma lib URL` (lib file read via the provided URL), or `só observado` (catalog NOT confirmed). This calibrates the "catálogo não confirmado" warning.

Dispatch nodes sequentially in leaves→root order; wait for each subagent to return before dispatching the next node that depends on it (independent leaves may be dispatched in the same wave). Handle each result per the section below.

### After the Subagent(s) Return

Aggregate the results of all node dispatches, then commit. If a leaf subagent reports BLOCKED, do NOT dispatch parents that depend on it — surface the block and skip the dependent subtree.

Before committing, analyze the project's commit conventions:
1. Run `git log --oneline -10` to identify the commit message pattern
2. Check for hook config files: `.lefthook.yml`, `lefthook.yml`, `.husky/pre-commit`, `commitlint.config.*`, `.commitlintrc*`
3. If commit messages include a Jira/ticket ID, extract it from the branch name: run `git branch --show-current` and look for a pattern like `ABC-123` (uppercase letters, dash, digits)
4. Use the detected convention for the commit message (e.g., `feat(ABC-123): implement [COMPONENT_NAME]` for conventional commits with ticket ID)

If a commit fails (pre-commit hook, commitlint, etc.): read the error, fix the issue (rewrite message format, run formatter, fix lint), re-stage, and retry up to 3 times. Never use `--no-verify`.

Commit once, at the end, after all node subagents have returned (a single commit covering the whole tree — or one per node if that better matches the project convention). Aggregate the per-node outcomes:

- **If DONE (all nodes' self-review checks passed):** Commit all created files using the project's commit convention and report success per node (including which `Importar` nodes were reused and the import paths). Mark T10 `completed`.
- **If DONE (with unresolved self-review issues on any node):** Commit all created files using the project's commit convention, report success, and relay the unresolved issues per node to the user so they can review manually. Mark T10 `completed`.
- **If BLOCKED (any node):** Relay the block reason and name the node, note which dependent parents were skipped, and report the nodes that did complete. Mark T10 `completed` (the task was executed, even though a subagent was blocked):
```
**STOPPED** — Component Implementation: <reason from subagent>

**What to do:** <actionable instruction based on the block reason>
```
