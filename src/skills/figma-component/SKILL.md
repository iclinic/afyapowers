---
claude:
  name: figma-component
  description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
  model: claude-opus-5
  effort: high
  disable-model-invocation: true
cursor:
  name: afyapowers-dev-figma-component
  description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
  metadata:
    mcp-server: figma
  allowed-tools:
    - Read
    - Bash
    - mcp__figma__get_metadata
    - mcp__figma__get_code_connect_map
  model: claude-opus-5
  disable-model-invocation: true
github-copilot:
  name: figma-component
  description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
  disable-model-invocation: true
---

# Component Skill

<FORBIDDEN>
Before EVERY Figma MCP tool call, you MUST check:
1. Which phase am I in?
2. Is this tool listed in the current phase's MCP_ALLOWLIST?
3. If NO → STOP. Do not call it. Only the implementer subagent may use it.

NEVER call get_screenshot or get_variable_defs — only the subagent calls these. NEVER call get_design_context yourself — Phase 3 delegates the whole resolution chain to the analyzing-design-system sub-skill, which owns those calls and its own budget. You make Figma MCP calls in Phase 1 only (get_metadata + get_code_connect_map).
NEVER launch Explore agents or scan the codebase for conventions, tokens, or patterns. The targeted existence check (props/types, Storybook argTypes, grep of usages) belongs to the analyzing-design-system sub-skill, not to you.
NEVER run phases in parallel. Execute Phase 1, then Phase 2, then Phase 3, then Phase 4, then Dispatch, in order.
NEVER implement the component yourself. You are the orchestrator. The subagent implements. Building the DS tree in Phase 3 is analysis, not implementation.
NEVER decide a verdict, a reuse, a grouping, or a component name on the user's behalf. The sub-skill confirms every node with them (in compact batches, one explicit answer per node). If a tree row reaches you without a decision, go back — do not fill it in.
NEVER skip task creation. You MUST create all tasks before starting any work.
NEVER mark a task as completed without actually doing the work.
NEVER start a task that is blocked by an incomplete task.
</FORBIDDEN>

Develop a single Figma component into production code. This skill is **standalone** — not part of the 5-phase workflow.

## Trigger Conditions

**Manual only.** This skill is never auto-invoked. It runs only when the user explicitly runs `/afyapowers-dev:figma-component`. If no Figma URL was provided, ask for it.

---

## Step 0 — Create Tasks

**Before doing ANY work, create all 10 tasks using TaskCreate, then set up dependencies with TaskUpdate.**

Create the following tasks in order:

| # | Subject | Description |
|---|---------|-------------|
| T1 | Phase 1.1: Parse Figma URL | Extract fileKey and nodeId from the Figma URL. Normalize nodeId from `-` to `:` format. |
| T2 | Phase 1.2: Check MCP availability | Verify all 5 required Figma MCP tools are callable. |
| T3 | Phase 1.3: Validate node type via get_metadata | Call get_metadata and confirm the node is COMPONENT or COMPONENT_SET. Store the full response. |
| T4 | Phase 1.4: Check Code Connect via get_code_connect_map | Call get_code_connect_map and record any existing implementation. Store the full response. An existing mapping is an input to the Phase 3 verdict, NOT a hard stop. |
| T5 | Phase 2.1: Check child dependencies from stored metadata | Scan stored metadata for INSTANCE nodes with componentId references. Split them: resolved (the COMPONENT/COMPONENT_SET is in the T3 subtree) vs. NÃO RESOLVIDA (it is not — original declared elsewhere, needs an origin URL from the user in Phase 3). |
| T6 | Phase 2.2: Cross-reference dependencies with Code Connect map | Check each componentId against the stored Code Connect map. A hit = child already exists → `Importar` (recursion stops there). Feed the analysis; do NOT hard-stop on missing deps. |
| T7 | Phase 2.3: Detect output location, framework, Storybook | Glob for component directories, check package.json, detect Storybook. |
| T8 | Phase 3: Build Component Tree | Invoke `{{skill:analyzing-design-system}}` with the stored T3 metadata and T4 Code Connect map. It resolves every dependency, recurses leaves→root (bounded at depth 2), diffs, recommends a verdict per node, and confirms EVERY node with the user in compact batches. Returns the confirmed `## Árvore de Componentes de DS`. |
| T9 | Phase 4: Present pre-flight summary | Show the global pre-flight summary (directory, framework, Storybook, resolved origins) and the confirmed DS tree. Confirm the run-level settings. Per-node verdicts were already confirmed in T8. |
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

**Store the full Code Connect map response. It is reused in Phase 2 and Phase 3.**

**An existing component is NOT a hard stop.** If the target already has a Code Connect mapping, record the mapped path and carry it into Phase 3 as an **input to the verdict**, not as a reason to refuse:

- it already covers the variant this node needs → the analysis will land on `Importar`, and there is nothing to build;
- it is missing the variant, addable non-breakingly → `Atualizar`;
- it is missing the variant and can only be extended by a breaking change, or the node diverges structurally → `Derivar`.

Phase 3 decides which, against the real code, and the user confirms it. Refusing here used to make one case unreachable: the design phase sends a component here precisely *because* it exists but does not cover a needed variant — a hard stop on "already exists" rejected exactly the input it was asked to handle, and there was no way forward inside the framework.

Only hard stop if the mapped path does not resolve at all (a stale Code Connect entry pointing at a file that no longer exists):
```
**STOPPED** — Parse & Validate: Code Connect maps this component to `<path>`, but that file does not exist.

**What to do:** The Code Connect mapping is stale. Update or remove it, then re-run.
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

Mark T5 `in_progress`. From the **stored metadata response** (Phase 1, Task T3), recursively scan all descendant nodes for `INSTANCE` types with `componentId` references. No MCP calls needed.

**Classify each distinct `componentId`:** does its main component node already appear **inside the T3 subtree** (same page/subtree captured) or **not** (its definition lives on another page, in a DS library, or is unknown)? Those outside the subtree are **not** resolved here — record them as "to resolve in Phase 3." This split is what Phase 3 walks. Mark T5 `completed`.

### Task T6 — Cross-reference dependencies

Mark T6 `in_progress`. For each `componentId` found, check the **stored Code Connect map** (Phase 1, Task T4) for a matching entry. No MCP calls needed. Mark T6 `completed`.

**Do NOT hard-stop on missing dependencies.** Unlike the previous single-node behavior, this skill is now DS-aware and composition-aware: missing children are no longer a dead end. Record which dependencies already exist (Code Connect hit → likely `Importar` candidates, and **recursion stops** at them — they are done) and which are missing (no hit → likely `Implementar`/`Derivar` candidates that Phase 3 must resolve and, if same-file, **recurse into**). This split is an **input to Phase 3** — the resolution analysis below resolves every dependency into a tree node with its own verdict, and the Dispatch phase implements the missing ones **leaves→root** in the same run. No "build the children first, then retry" round-trip.

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
The orchestrator makes NO Figma MCP calls in this phase. `{{skill:analyzing-design-system}}` owns the
resolution chain and its own budget (~12 req/min, backoff 30-60s on 429). Do not call `get_screenshot`
or `get_variable_defs` here or anywhere — those belong to the implementer subagent.
</MCP_ALLOWLIST>

### Task T8 — Build the DS Component Tree

Mark T8 `in_progress`. Invoke `{{skill:analyzing-design-system}}` — it is the single design-system
brain, shared with the design phase. Do NOT reimplement its resolution chain, verdict rules, or
confirmation loop here; if this file ever describes those rules again, that copy is stale.

Pass it:

- `fileKey` and the target `nodeId` from Phase 1, Task T1;
- the **stored `get_metadata` response** from Task T3 and the **stored Code Connect map** from Task T4,
  so it does not re-fetch what you already hold;
- the target's `INSTANCE` `componentId`s already derived in Phase 2, Task T5, split into
  resolves-inside-the-T3-subtree vs. resolves-outside-it;
- **every Figma URL you already have** — from the user's request or a previous run. These are candidate
  origin files for the unresolved instances; the sub-skill validates each one;
- caller mode `standalone`.

**Expect the sub-skill to stop and ask you for origin links.** Any `INSTANCE` whose
`COMPONENT`/`COMPONENT_SET` is not declared in the file you read has its original somewhere else, and
the sub-skill will not proceed without a **direct node link** to it — a URL carrying `node-id`, which
the user gets by right-clicking the component → "Copy link to selection". A file-level URL is rejected
before any MCP call, because it does not say which component it means.

The sub-skill asks for **all pending components' links in one message** (an open question, numbered
list) and validates each answer on arrival, re-asking only failures. Relay those questions verbatim,
including the note that the user may skip a component or say they cannot find it. Do not try to
satisfy them by reading the instance, by guessing a file, or by scanning a file for a matching name.

It resolves each dependency, recurses leaves->root (existence gates recursion, bounded at depth 2),
diffs each instance against its original, recommends a verdict per node, and **confirms every node with
the user in compact batches — one explicit answer per node**. It returns the confirmed tree, the
warnings, the skip set, and the import path of every `Importar` node.

**Persistence.** In `standalone` mode the sub-skill writes the tree to
`.afyapowers/features/<feature>/artifacts/ds-tree.md` when a feature is active. If there is no active
feature, the tree lives only in this conversation — tell the user that, so they know a second run will
re-resolve everything from scratch.

Mark T8 `completed` once the confirmed tree is in hand.

For a **single self-contained component with no sub-component instances**, the tree is a single row
(the target itself) and the flow degrades gracefully to the original single-node behavior.

---

### Phase Gate: Phase 3 → Phase 4

Before proceeding: verify task T8 is `completed` and the DS tree is assembled. If any task triggered a hard stop, do NOT continue.

---

## Phase 4 — Present pre-flight & confirm run settings

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE.
ALL Figma MCP calls are FORBIDDEN in this phase.
If you are about to call any Figma MCP tool, STOP. You are violating the skill protocol.
</MCP_ALLOWLIST>

### Task T9 — Present pre-flight results & confirm run settings

Mark T9 `in_progress`.

**The per-node verdicts were already confirmed in Phase 3.** `{{skill:analyzing-design-system}}` asked
the user about **every** node -- one explicit answer per node, leaves->root, in compact batches -- and
returned a tree where each row carries a decision the user actually made. Do NOT re-ask those questions here, and do NOT accept a
tree with unconfirmed rows: if any row is missing a decision, go back to T8 rather than filling it in
yourself.

Show the global pre-flight summary:

```
## Pre-flight Results

- **Target component:** <name> (<COMPONENT | COMPONENT_SET>)
- **Variants:** <count> -- <list> (if COMPONENT_SET)
- **Component tree:** <N> nodes -- <count Implementar> to implement, <count Derivar> to derive, <count Atualizar> to update, <count Importar> to reuse
- **Composition:** <count composites> composed of sub-components; <count resolved from another page of this file>; recursion depth <D>
- **Suggested directory:** <path> (you can override this)
- **Framework:** <detected> (you can override this)
- **Storybook:** detected -- generate story files? (yes/no) | not detected
- **Code Connect:** <target: existing mapping | none>
- **Origens:** <per node: declared in this file | resolved via the URL the user supplied (file + node-id)>
- **Skipped:** <nodes the user declined, and parents skipped or degraded as a result>
```

Then print the confirmed `## Árvore de Componentes de DS` table so the user sees the whole plan in one
place before anything is built -- every node, its confirmed verdict, its dependencies, and its confirmed
code name.

**Confirm the run-level settings that are not per-node** -- these are the only questions left at this
point, and each is still a separate question:

- the output directory,
- the framework,
- whether to generate Storybook stories,
- whether to proceed with the run at all.

The user may also decline the whole run here. Mark T9 `completed` once the run settings are confirmed.

---

### Phase Gate: Phase 4 → Dispatch

Before proceeding: verify task T9 is `completed`, that every tree row carries a user decision (confirmed node by node in Phase 3), and that the run-level settings are confirmed. If the user declined the whole run, STOP. Carry forward the confirmed verdicts, confirmed code names, and the set of nodes to dispatch vs. skip.

---

## Dispatch

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE for the orchestrator.
The implementer subagent will make its own 3 MCP calls (get_variable_defs, get_screenshot, get_design_context); its self-review reuses that data with no extra calls.
You as the orchestrator must NOT call any Figma MCP tools here.
</MCP_ALLOWLIST>

### Task T10 — Dispatch implementer subagent(s) per node

Mark T10 `in_progress`. Walk the confirmed DS tree in **leaves→root order** and dispatch @"figma-component-implementer (agent)" **once per code-task node**. A node with a code task is one whose `Task Type` is a code task (e.g. `UI Component`) — i.e. verdict `Implementar`, `Derivar`, or `Atualizar`. **Skip `Importar` nodes** (`Task Type = —`): no new code is dispatched; record the existing import path/symbol so parents reference it.

**Ordering & dependency rules:**
- Never dispatch a node before every node in its `Depende de` column has been dispatched (or is an already-satisfied `Importar`). For a `Derivar` node, its base — the **first** item in `Depende de` — must be implemented/imported first so the wrapper can compose it. For a **composite** `Implementar` node, ALL children in `Depende de` must be implemented/imported first; pass them as `[COMPOSE_FROM]` so the subagent imports and composes them.
- **Shared components are dispatched once.** A node depended on by several parents is implemented a single time; every parent reuses that result. Never dispatch it per parent.
- **Skipped nodes.** Do NOT dispatch a node the user rejected in Phase 4, nor a parent chosen to be skipped because of a rejected dependency. For a parent confirmed as "implement without the dependency", dispatch it and state in the prompt that the missing child is intentionally omitted (placeholder / rendered without it).

Build each subagent prompt filling in **per node** (from that node's tree row / stored metadata), plus the global confirmed settings:

- `[FILE_KEY]` — the node's Figma file key. Same-file/other-page nodes keep the **same `fileKey`** as the target (from Phase 1, Task T1) — a different page is not a different file.
- `[NODE_ID]` — the node's main node-id. For same-file/other-page nodes this is the **main component node-id resolved via `get_metadata`** in Phase 3 (route 2), not the instance node-id.
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET for that node
- `[VARIANT_LIST]` — variant names for that node (or "N/A — single component")
- `[OUTPUT_DIRECTORY]` — confirmed path from Phase 4
- `[FRAMEWORK]` — confirmed framework from Phase 4
- `[GENERATE_STORYBOOK]` — yes or no from Phase 4
- `[COMPONENT_NAME]` — the confirmed code name for the node (proposed name from the tree, as confirmed/overridden in Phase 4)
- `[VERDICT]` — the confirmed verdict for the node: `implementar` | `importar` | `atualizar` | `derivar` (lowercase). Controls the subagent's behavior mode.
- `[BASE_COMPONENT]` — for `derivar`, the existing generic base the wrapper composes (the first item in `Depende de`); for `atualizar`, the set being extended. Empty otherwise.
- `[COMPOSE_FROM]` — for a **composite** node (`implementar` with sub-components in its `Depende de`), the list of child components it must import and compose, each as `{ confirmed code name, resolved import path }`. By the time this node is dispatched, every child has already been implemented or imported (leaves→root order), so each entry has a real resolved path. The subagent imports and composes these — it MUST NOT reimplement them. Empty for nodes that compose nothing. (Distinct from `[BASE_COMPONENT]`: that is a single base being *derived from*; `[COMPOSE_FROM]` is N peer children being *composed*.)

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
