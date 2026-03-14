---
name: figma-discovery
description: "Discovers Figma node references for UI features during the Design phase. Asks for Figma URLs, uses MCP tools to list frames/nodes, and writes confirmed references to the design spec."
---

# Figma Discovery

Identify and map Figma design references for UI features, so implementation subagents can fetch visual details from Figma MCP tools when building components.

**This skill is invoked by the Design skill** — do not invoke it directly. It runs late in the Design phase, after the design is shaped but before writing the spec document.

## Flow

### Step 1: Ask

Ask the user:

> "Do you have Figma layouts for this feature?"

- If **no** → exit the skill. Design continues normally without Figma references.
- If **yes** → proceed to Step 2.

### Step 2: Collect URLs

Ask the user to paste one or more Figma URLs. These can be file-level, page-level, or frame-level links.

> "Please paste the Figma URL(s) for this feature (one per line). These can be file, page, or frame links."

### Step 3: Discover Nodes

For each URL provided:

1. Inspect the available MCP tools in your environment to find Figma-related tools (e.g., tools that can fetch file structure, list nodes, get frames). Do NOT hardcode specific tool names — different Figma MCP servers use different naming conventions.
2. Use the available Figma MCP tools to fetch the node/frame tree for the URL.
3. Collect the top-level frames and components with their node IDs and names.

**If no Figma MCP tools are available:** Warn the user:

> "No Figma MCP tools are available in the current environment. Skipping Figma discovery — design will continue without Figma references. You can configure a Figma MCP server and re-run this step later."

Exit the skill gracefully.

**If a URL is invalid or inaccessible:** Report the error for that specific URL and ask the user to provide a corrected URL or skip it. Continue processing other URLs.

**If no nodes are found under a URL:** Inform the user and ask if the URL is correct or if they want to skip it.

### Step 4: Present for Confirmation

Display all discovered nodes in a structured list:

> "I found the following frames/components in your Figma files. Please confirm which ones are relevant to this feature, and optionally add a description for each:"
>
> **From `<URL 1>`:**
> 1. `node-id=12:34` — "Frame Name"
> 2. `node-id=12:56` — "Another Frame"
>
> **From `<URL 2>`:**
> 3. `node-id=45:67` — "Component Name"
>
> "Which of these are relevant? You can list the numbers (e.g., '1, 3') and add descriptions (e.g., '1 — Login form, 3 — Dashboard header')."

Wait for the user to confirm. If the user confirms zero nodes, exit the skill — no Figma References section will be written.

### Step 5: Write to Spec

Append a `## Figma References` section to the design spec with the confirmed nodes. Format each entry as a full URL with the node ID embedded, followed by the label:

```markdown
## Figma References
- `https://figma.com/file/abc123?node-id=12:34` — Login form
- `https://figma.com/file/abc123?node-id=12:56` — Error states
- `https://figma.com/file/abc123?node-id=12:78` — Dashboard overview
```

The URL should be the original Figma file/page URL with `?node-id=X:Y` appended (or preserved if the original URL already targeted a specific node).

## Key Constraints

- **Do NOT extract tokens, spacing, colors, or visual details.** This skill only builds the reference map. Implementation subagents do their own MCP calls later to fetch visual specifics.
- **Be tool-name agnostic.** Different Figma MCP servers expose different tool names. Always discover available tools at runtime.
- **One question at a time.** Follow the flow step by step — don't combine steps.

## Error Handling

| Scenario | Behavior |
| --- | --- |
| No Figma MCP tools available | Warn user, exit gracefully. Design continues without references. |
| Invalid or inaccessible URL | Report error for that URL, ask for correction or skip. Continue with other URLs. |
| No nodes found under URL | Inform user, ask if URL is correct or skip. |
| User confirms zero nodes | Exit skill. No Figma References section written. |
