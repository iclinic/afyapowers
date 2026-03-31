---
name: figma-component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
---

# Component Skill

<FORBIDDEN>
Before EVERY Figma MCP tool call, you MUST check:
1. Which phase am I in?
2. Is this tool listed in the current phase's MCP_ALLOWLIST?
3. If NO → STOP. Do not call it. Only the implementer subagent may use it.

NEVER call get_design_context, get_screenshot, or get_variable_defs. Only the subagent calls these.
NEVER launch Explore agents or scan the codebase for conventions, tokens, or patterns.
NEVER run phases in parallel. Execute Phase 1, then Phase 2, then Phase 3, then Dispatch, in order.
NEVER implement the component yourself. You are the orchestrator. The subagent implements.
NEVER skip task creation. You MUST create all tasks before starting any work.
NEVER mark a task as completed without actually doing the work.
NEVER start a task that is blocked by an incomplete task.
</FORBIDDEN>

Develop a single Figma component into production code. This skill is **standalone** — not part of the 5-phase workflow.

## Trigger Conditions

**Explicit:** User runs `/afyapowers:figma-component`.

**Implicit:** User asks to implement/build/create/develop a Figma component. Requires all three: action keyword + "component" + Figma URL. If no URL, ask for it.

---

## Step 0 — Create Tasks

**Before doing ANY work, create all 9 tasks using TaskCreate, then set up dependencies with TaskUpdate.**

Create the following tasks in order:

| # | Subject | Description |
|---|---------|-------------|
| T1 | Phase 1.1: Parse Figma URL | Extract fileKey and nodeId from the Figma URL. Normalize nodeId from `-` to `:` format. |
| T2 | Phase 1.2: Check MCP availability | Verify all 5 required Figma MCP tools are callable. |
| T3 | Phase 1.3: Validate node type via get_metadata | Call get_metadata and confirm the node is COMPONENT or COMPONENT_SET. Store the full response. |
| T4 | Phase 1.4: Check Code Connect via get_code_connect_map | Call get_code_connect_map and check for existing implementation. Store the full response. |
| T5 | Phase 2.1: Check child dependencies from stored metadata | Scan stored metadata for INSTANCE nodes with componentId references. |
| T6 | Phase 2.2: Cross-reference dependencies with Code Connect map | Check each componentId against the stored Code Connect map. |
| T7 | Phase 2.3: Detect output location, framework, Storybook | Glob for component directories, check package.json, detect Storybook. |
| T8 | Phase 3: Present pre-flight results & confirm | Show pre-flight summary and wait for user confirmation. |
| T9 | Dispatch implementer subagent | Build the subagent prompt and dispatch. Subagent includes self-review against Figma data. Handle the result. |

After creating all 9 tasks, set up dependencies using TaskUpdate `addBlockedBy`:
- T2 blocked by T1
- T3 blocked by T2
- T4 blocked by T3
- T5 blocked by T4
- T6 blocked by T5
- T7 blocked by T6
- T8 blocked by T7
- T9 blocked by T8

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

Hard stop if any dependencies are missing:
```
**STOPPED** — Dependencies: Missing child component dependencies.

The following components are used inside this component but have not been implemented yet:
<list of missing component names and their componentIds>

**What to do:** Implement the missing child components first using `/afyapowers:figma-component`, then retry. Build bottom-up — leaf components before parents.
```

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

## Phase 3 — Present & Confirm

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE.
ALL Figma MCP calls are FORBIDDEN in this phase.
If you are about to call any Figma MCP tool, STOP. You are violating the skill protocol.
</MCP_ALLOWLIST>

### Task T8 — Present pre-flight results

Mark T8 `in_progress`. Show the pre-flight results to the user:

```
## Pre-flight Results

- **Component:** <name> (<COMPONENT | COMPONENT_SET>)
- **Variants:** <count> — <list> (if COMPONENT_SET)
- **Dependencies:** All found | Missing: <list>
- **Suggested directory:** <path> (you can override this)
- **Framework:** <detected> (you can override this)
- **Storybook:** detected — generate story file? (yes/no) | not detected
- **Code Connect:** No existing mapping

Ready to implement this component?
```

Wait for the user to respond. The user can:
- Confirm and proceed to dispatch
- Override the suggested directory or framework
- Accept or decline Storybook story generation
- Decline to stop entirely

Mark T8 `completed` after user confirms.

---

### Phase Gate: Phase 3 → Dispatch

Before proceeding: verify task T8 is `completed` and the user has confirmed. If the user declined, STOP.

---

## Dispatch

<MCP_ALLOWLIST>
Permitted MCP tools in this phase: NONE for the orchestrator.
The implementer subagent will make its own MCP calls (get_variable_defs, get_screenshot, get_design_context) plus 2 review calls.
You as the orchestrator must NOT call any Figma MCP tools here.
</MCP_ALLOWLIST>

### Task T9 — Dispatch implementer subagent

Mark T9 `in_progress`. After the user confirms, dispatch the implementer subagent using the **Agent tool**. Build the prompt from `component-implementer-prompt.md`, filling in:

- `[FILE_KEY]` — from Phase 1, Task T1
- `[NODE_ID]` — from Phase 1, Task T1
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET from Phase 1, Task T3
- `[VARIANT_LIST]` — variant names from metadata (or "N/A — single component")
- `[OUTPUT_DIRECTORY]` — confirmed path from Phase 3
- `[FRAMEWORK]` — confirmed framework from Phase 3
- `[GENERATE_STORYBOOK]` — yes or no from Phase 3
- `[COMPONENT_NAME]` — component name from metadata

### After the Subagent Returns

- **If DONE (all self-review checks passed):** Commit all created files and report success. Mark T9 `completed`.
- **If DONE (with unresolved self-review issues):** Commit all created files, report success, and relay the unresolved issues to the user so they can review manually. Mark T9 `completed`.
- **If BLOCKED:** Relay the block reason. Mark T9 `completed` (the task was executed, even though the subagent was blocked):
```
**STOPPED** — Component Implementation: <reason from subagent>

**What to do:** <actionable instruction based on the block reason>
```
