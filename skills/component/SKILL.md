---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
command: afyapowers:component
---

# Component Skill

Develop a single Figma component into production code through an 8-gate validation pipeline. This skill is **standalone** — it does not participate in the 5-phase workflow (design → plan → implement → review → complete). Use it when you need to implement an individual component from a Figma file.

## Trigger Conditions

### Explicit Trigger

The user runs `/afyapowers:component`.

### Implicit Trigger

The user asks to implement, build, create, or develop a Figma component. Detected via:

- **Keywords** (case-insensitive): "implement", "build", "create", "develop"
- **Combined with**: "component"
- **Combined with**: a Figma URL (`figma.com/design/...`) or a Figma component reference

All three conditions must be present for an implicit trigger. If keywords and "component" are present but no Figma URL or reference, ask the user for the Figma URL before proceeding.

---

## Gate Pipeline

All 8 gates run sequentially. Every gate must pass before the next one begins. If any gate issues a hard stop, the pipeline halts immediately.

---

### Gate 1 — Input & URL Parsing

**What it does:** Parse `fileKey` and `nodeId` from the user-provided Figma URL.

**How:**
- Extract from URL format: `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>`
- The `nodeId` in the URL may use `-` instead of `:` (e.g., `1-2` instead of `1:2`). Normalize to `:` format for all subsequent MCP calls.
- If no URL was provided, ask the user for it.

**Pass condition:** A valid `fileKey` and `nodeId` have been extracted.

**Hard stop:** The URL is malformed or missing the `node-id` parameter.

```
**STOPPED** — Input & URL Parsing: Malformed Figma URL or missing node ID.

**What to do:** Provide a valid Figma component URL in the format:
https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>

Make sure the URL includes the `node-id` query parameter. You can get this by right-clicking a component in Figma and selecting "Copy link".
```

---

### Gate 2 — Figma MCP Availability

**What it does:** Verify that the required Figma MCP tools are available in the current environment.

**How:** Check that all of the following MCP tools are callable:
- `get_metadata`
- `get_design_context`
- `get_variable_defs`
- `get_screenshot`
- `get_code_connect_map`

**Pass condition:** All 5 tools are available.

**Hard stop:** One or more tools are unavailable.

```
**STOPPED** — Figma MCP Availability: BLOCKED — required Figma MCP tools are not available.

**What to do:** Ensure the Figma MCP server is connected and running. The following tools must be available: get_metadata, get_design_context, get_variable_defs, get_screenshot, get_code_connect_map. Check your MCP server configuration and restart if necessary.
```

---

### Gate 3 — Node Type Validation

**What it does:** Confirm that the selected Figma node is an actual component (not a frame, instance, or other node type).

**MCP call:**
```
get_metadata(fileKey, nodeId)
```

**Pass condition:** The node's `type` is `COMPONENT` or `COMPONENT_SET`.

**Hard stop:** The node type is anything other than `COMPONENT` or `COMPONENT_SET`.

```
**STOPPED** — Node Type Validation: The selected node is a <actual_type>, not a COMPONENT or COMPONENT_SET.

**What to do:** Select an actual component node in Figma (purple diamond icon), not a frame or instance. Right-click the component in the layers panel and select "Copy link" to get the correct URL.
```

> **Important:** Store the full metadata response from this call — it is reused by Gates 4 and 6.

---

### Gate 4 — Variant Structure Validation

**What it does:** Detect ungrouped variants that should be organized into a Component Set before implementation.

**How:**
- If the node from Gate 3 is a `COMPONENT_SET` — pass immediately. Variants are properly grouped.
- If the node is a `COMPONENT` — use the parent ID from the Gate 3 metadata response. Call:
  ```
  get_metadata(fileKey, parentNodeId)
  ```
  Enumerate the parent's children (siblings of the selected component). Check if any sibling components share the same base name with different property suffixes (e.g., `Button/Default`, `Button/Hover`) that are NOT already grouped in a `COMPONENT_SET`.

**Pass condition:** No ungrouped variants detected, or the node is already a `COMPONENT_SET`.

**Hard stop:** Ungrouped variants detected — sibling components share a base name with different suffixes but are not grouped in a Component Set.

```
**STOPPED** — Variant Structure Validation: Found ungrouped variants sharing the base name "<base_name>": <list of variant names>.

**What to do:** In Figma, select all variant components (e.g., <list of variant names>) and use "Combine as Variants" to group them into a Component Set. Then share the updated component URL.
```

---

### Gate 5 — Code Connect Dedup Check

**What it does:** Check whether this component has already been implemented by looking it up in the Code Connect mapping.

**MCP call:**
```
get_code_connect_map()
```

Look for an existing entry matching this component by its **Figma component key** (the unique ID from the Gate 3 metadata response). The component key is the authoritative match — name matching is not used since components can be renamed.

**Pass condition:** No existing Code Connect entry matches this component's key.

**Hard stop:** A Code Connect entry already exists for this component.

```
**STOPPED** — Code Connect Dedup Check: This component already exists in the codebase.

**What to do:** An implementation already exists at `<existing_file_path>`. If you need to update it, modify the existing file directly rather than creating a duplicate.
```

---

### Gate 6 — Dependency Detection

**What it does:** Identify child components that this component depends on and verify they exist in the codebase.

**How:**
- From the Gate 3 metadata response, scan all child nodes for `INSTANCE` types that reference other components (via `componentId`).
- For each referenced `componentId`, check the Code Connect map (already fetched in Gate 5) for a matching entry.
- Collect any dependencies that have no Code Connect entry.

**Pass condition:** All child component dependencies exist in the codebase (have Code Connect entries), or the component has no child component dependencies.

**Hard stop:** One or more child component dependencies are missing from the codebase.

```
**STOPPED** — Dependency Detection: Missing child component dependencies.

The following components are used inside this component but have not been implemented yet:
<list of missing component names and their componentIds>

**What to do:** Implement the missing child components first using `/afyapowers:component`, then retry this component. Components must be built bottom-up — leaf components before their parents.
```

---

### Gate 7 — Output Location Resolution + Framework Detection

**What it does:** Determine where the component file should be created and what framework to target.

**How:**

1. **Scan for existing component directories** using Glob patterns:
   - `src/components/**`
   - `src/ui/**`
   - `components/**`
   - `lib/components/**`
   - `packages/*/src/components/**`

2. **Detect project framework** by checking:
   - `package.json` dependencies: `react`, `vue`, `angular`, `svelte`
   - Config files: `next.config.*`, `nuxt.config.*`, `vite.config.*`
   - File extensions in component directories: `.tsx`, `.vue`, `.svelte`

3. **Propose** the detected output location and framework to the user. Ask for confirmation or override.

**Pass condition:** User confirms the output directory and framework.

**Hard stop:** No component directory detected and user does not specify one.

```
**STOPPED** — Output Location Resolution: No component directory detected in the project.

**What to do:** Specify the output directory where the component should be created (e.g., `src/components/`). No default directory will be assumed.
```

---

### Gate 8 — Storybook/Docs Detection

**What it does:** Check whether the project uses Storybook and offer to generate a story file.

**How:**
- Glob for `.storybook/` directory.
- Glob for `*.stories.*` files.

**If Storybook is detected:** Ask the user if they want a story file generated alongside the component.

**If Storybook is not detected:** Skip silently — do not mention Storybook.

**Pass condition:** Always passes. This gate is informational only.

---

## Dispatch

After all 8 gates pass, present an upfront summary to the user before dispatching:

```
## Component Implementation Summary

- **Component name:** <name from Figma metadata>
- **Type:** COMPONENT | COMPONENT_SET
- **Variants:** <count> — <list of variant names> (if COMPONENT_SET)
- **Output directory:** <confirmed path>
- **Framework:** <detected framework>
- **Storybook:** yes | no
```

Then dispatch the component implementer subagent (see `component-implementer-prompt.md`) with the full validated context using the Agent tool with `subagent_type: general-purpose`. Pass along:

- `fileKey` and `nodeId`
- Full metadata from Gate 3
- Code Connect map from Gate 5
- Confirmed output directory and framework
- Storybook preference from Gate 8

### After the Subagent Returns

- **If DONE:** Commit all created files and report success to the user.
- **If BLOCKED:** Relay the block reason to the user using the standard stopped format:

```
**STOPPED** — Component Implementation: <reason from subagent>

**What to do:** <actionable instruction based on the block reason>
```
