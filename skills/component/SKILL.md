---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
---

# Component Skill

<FORBIDDEN>
NEVER call get_design_context, get_screenshot, or get_variable_defs. Only the subagent calls these.
NEVER launch Explore agents or scan the codebase for conventions, tokens, or patterns.
NEVER run phases in parallel. Execute Phase 1, then Phase 2, then Phase 3, in order.
NEVER implement the component yourself. You are the orchestrator. The subagent implements.
</FORBIDDEN>

Develop a single Figma component into production code. This skill is **standalone** — not part of the 5-phase workflow.

## Trigger Conditions

**Explicit:** User runs `/afyapowers:component`.

**Implicit:** User asks to implement/build/create/develop a Figma component. Requires all three: action keyword + "component" + Figma URL. If no URL, ask for it.

---

## Phase 1 — Parse & Validate

No codebase access in this phase. Only MCP calls allowed: `get_metadata` and `get_code_connect_map`.

**Step 1 — Parse URL.** Extract `fileKey` and `nodeId` from `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>`. Normalize `nodeId` from `-` to `:` format. If no URL provided, ask the user.

Hard stop if URL is malformed or missing `node-id`:
```
**STOPPED** — Parse & Validate: Malformed Figma URL or missing node ID.

**What to do:** Provide a valid Figma component URL with the `node-id` parameter. Right-click a component in Figma → "Copy link".
```

**Step 2 — Check MCP availability.** Verify these 5 tools are callable: `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`, `get_code_connect_map`.

Hard stop if any are missing:
```
**STOPPED** — Parse & Validate: Required Figma MCP tools are not available.

**What to do:** Ensure the Figma MCP server is connected and running.
```

**Step 3 — Validate node type.** Call `get_metadata(fileKey, nodeId)`. Confirm the node type is `COMPONENT` or `COMPONENT_SET`.

**Store the full metadata response. It is reused in Phase 2. Do NOT make additional MCP calls.**

Hard stop if node type is wrong:
```
**STOPPED** — Parse & Validate: The selected node is a <actual_type>, not a COMPONENT or COMPONENT_SET.

**What to do:** Select an actual component in Figma (purple diamond icon), not a frame or instance.
```

**Step 4 — Check Code Connect.** Call `get_code_connect_map(fileKey, nodeId)`. Look for an existing entry matching this component by its Figma component key (from the metadata response). Component key is the authoritative match — not name.

**Store the full Code Connect map response. It is reused in Phase 2. Do NOT call this again.**

Hard stop if component already exists:
```
**STOPPED** — Parse & Validate: This component already exists in the codebase at `<existing_file_path>`.

**What to do:** Modify the existing file directly rather than creating a duplicate.
```

---

## Phase 2 — Dependencies & Location

Limited codebase access: only Glob and reading `package.json` / config files. No Explore agents. No scanning for conventions or patterns.

**Step 1 — Check dependencies.** From the **stored metadata response** (Phase 1, Step 3), recursively scan all descendant nodes for `INSTANCE` types with `componentId` references. No additional MCP calls needed.

**Step 2 — Cross-reference dependencies.** For each `componentId` found, check the **stored Code Connect map** (Phase 1, Step 4) for a matching entry. No additional MCP calls needed.

Hard stop if any dependencies are missing:
```
**STOPPED** — Dependencies: Missing child component dependencies.

The following components are used inside this component but have not been implemented yet:
<list of missing component names and their componentIds>

**What to do:** Implement the missing child components first using `/afyapowers:component`, then retry. Build bottom-up — leaf components before parents.
```

**Step 3 — Detect output location.** Glob for existing component directories:
- `src/components/**`
- `src/ui/**`
- `components/**`
- `lib/components/**`
- `packages/*/src/components/**`

**Step 4 — Detect framework.** Check:
- `package.json` dependencies: `react`, `vue`, `angular`, `svelte`
- Config files: `next.config.*`, `nuxt.config.*`, `vite.config.*`
- File extensions in component directories: `.tsx`, `.vue`, `.svelte`

**Step 5 — Detect Storybook.** Glob for `.storybook/` and `*.stories.*`. If not found, skip silently.

---

## Phase 3 — Present & Confirm

Show the pre-flight results to the user:

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

---

## Dispatch

After the user confirms, dispatch the implementer subagent using the **Agent tool**. Build the prompt from `component-implementer-prompt.md`, filling in:

- `[FILE_KEY]` — from Phase 1, Step 1
- `[NODE_ID]` — from Phase 1, Step 1
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET from Phase 1, Step 3
- `[VARIANT_LIST]` — variant names from metadata (or "N/A — single component")
- `[OUTPUT_DIRECTORY]` — confirmed path from Phase 3
- `[FRAMEWORK]` — confirmed framework from Phase 3
- `[GENERATE_STORYBOOK]` — yes or no from Phase 3
- `[COMPONENT_NAME]` — component name from metadata

### After the Subagent Returns

- **If DONE:** Commit all created files and report success.
- **If BLOCKED:** Relay the block reason:
```
**STOPPED** — Component Implementation: <reason from subagent>

**What to do:** <actionable instruction based on the block reason>
```
