# Figma Discovery Implementation Plan

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone Figma discovery skill and update existing skills to propagate Figma node references through the design → plan → implement pipeline.

**Architecture:** A new skill (`skills/figma-discovery/SKILL.md`) handles the interactive discovery flow. Three existing files receive small instruction additions: the design skill invokes the new skill, the writing-plans skill maps nodes to tasks, and the implementer prompt consumes them.

**Tech Stack:** Markdown skill files, Figma MCP tools (agnostic — no specific server hardcoded)

---

## Chunk 1: Core Implementation

### Task 1: Create the Figma Discovery Skill

**Files:**
- Create: `skills/figma-discovery/SKILL.md`
**Depends on:** none

- [ ] **Step 1: Create the skill directory and file**

Create `skills/figma-discovery/SKILL.md` with the following content:

```markdown
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
```

- [ ] **Step 2: Verify the file was created**

Check that `skills/figma-discovery/SKILL.md` exists and has the correct frontmatter (`name: figma-discovery`).

- [ ] **Step 3: Commit**

```bash
git add skills/figma-discovery/SKILL.md
git commit -m "feat: add Figma discovery skill"
```

### Task 2: Update the Design Skill to Invoke Figma Discovery

**Files:**
- Modify: `skills/design/SKILL.md`
**Depends on:** Task 1

- [ ] **Step 1: Add Figma discovery step to the checklist**

In `skills/design/SKILL.md`, find the `## Checklist` section. Add a new step between step 4 ("Present design") and step 5 ("Write design doc"):

```markdown
5. **Figma discovery** (UI features only) — if the feature involves front-end/UI work, invoke the `figma-discovery` skill to identify Figma references before writing the spec
```

Renumber the subsequent steps (current 5 → 6, 6 → 7, 7 → 8).

- [ ] **Step 2: Add Figma discovery step to the process flow**

In the `digraph design` section, add a new node and edge between "User approves design?" and "Write design doc":

```dot
"Figma discovery\n(UI features only)" [shape=box];

"User approves design?" -> "Figma discovery\n(UI features only)" [label="yes"];
"Figma discovery\n(UI features only)" -> "Write design doc";
```

Remove the existing direct edge from "User approves design?" to "Write design doc".

- [ ] **Step 3: Add instructions for invoking the Figma discovery skill**

After the "Presenting the design" section and before "Working in existing codebases", add a new section:

```markdown
**Figma discovery (UI features only):**

- After the user approves the design sections, check whether the feature involves front-end/UI work (based on the design conversation context — components, screens, layouts, visual elements)
- If it does → invoke the `figma-discovery` skill (located at `skills/figma-discovery/SKILL.md`). The skill will ask about Figma layouts, discover nodes, and write a `## Figma References` section to the design spec.
- If it doesn't (purely backend, infrastructure, data pipeline, etc.) → skip entirely and proceed to writing the spec
- Do NOT ask about Figma yourself — delegate entirely to the Figma discovery skill
```

- [ ] **Step 4: Verify the changes**

Read `skills/design/SKILL.md` and confirm:
- The checklist has the new step 5 with correct numbering
- The process flow digraph includes the Figma discovery node
- The instruction section is placed correctly

- [ ] **Step 5: Commit**

```bash
git add skills/design/SKILL.md
git commit -m "feat: invoke Figma discovery skill from design phase for UI features"
```

### Task 3: Update the Writing-Plans Skill for Figma Task Mapping

**Files:**
- Modify: `skills/writing-plans/SKILL.md`
**Depends on:** Task 1

- [ ] **Step 1: Add Figma mapping instruction**

In `skills/writing-plans/SKILL.md`, find the `## Dependency Declaration` section. After it (and before `## Plan Document Header`), add a new section:

```markdown
## Figma References

If the design spec contains a `## Figma References` section, assign relevant Figma nodes to tasks using a `**Figma:**` line after `**Depends on:**`.

- Each task that involves implementing a UI element with a corresponding Figma reference should include the relevant node URLs
- Tasks with no relevant Figma nodes omit the `**Figma:**` section entirely
- The `**Figma:**` section uses the same bulleted list format as `**Files:**`

**Example:**

```markdown
### Task 3: Login Screen
**Files:**
- Create: `src/components/LoginScreen.tsx`
- Test: `src/components/__tests__/LoginScreen.test.tsx`
**Depends on:** Task 1, Task 2
**Figma:**
- `https://figma.com/file/abc123?node-id=12:34` — Login form
- `https://figma.com/file/abc123?node-id=12:56` — Error states
```
```

- [ ] **Step 2: Update the Task Structure example**

In the `## Task Structure` section, add the optional `**Figma:**` line to the example template, after `**Depends on:**`:

```markdown
**Depends on:** none | Task X, Task Y
**Figma:** _(optional — only for tasks with Figma references)_
- `https://figma.com/file/...?node-id=X:Y` — Description
```

- [ ] **Step 3: Verify the changes**

Read `skills/writing-plans/SKILL.md` and confirm:
- The new Figma References section is placed correctly
- The Task Structure example includes the optional Figma line
- No existing content was accidentally altered

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat: add Figma reference mapping instructions to writing-plans skill"
```

### Task 4: Update the Implementer Prompt for Figma Consumption

**Files:**
- Modify: `skills/implementing/implementer-prompt.md`
**Depends on:** Task 1

- [ ] **Step 1: Add Figma instructions to the implementer prompt**

In `skills/implementing/implementer-prompt.md`, find the `## Your Job` section. Before it, add a new section:

```markdown
    ## Figma References

    If your task has a `**Figma:**` section, you MUST use Figma MCP tools to fetch
    visual details for those nodes BEFORE writing code:

    1. Inspect the available MCP tools in your environment to find Figma-related tools
       (do NOT hardcode tool names — different Figma MCP servers use different names)
    2. For each node URL in your `**Figma:**` section, call the appropriate Figma MCP
       tool to fetch layout, component structure, and visual specs for that node ID
    3. Use the fetched visual details to guide your implementation — match the design's
       structure, hierarchy, and visual intent

    **If no Figma MCP tools are available** or calls fail: proceed without visual
    context, but you MUST include `**Figma Status: unable to access Figma MCP**` in
    your task completion report. The orchestrator will surface this so it's visible
    that the task was implemented without Figma reference.

    If your task does NOT have a `**Figma:**` section, ignore this — proceed normally.
```

- [ ] **Step 2: Add Figma Status to the Report Format**

In the `## Report Format` section, add a line to the report items:

```markdown
    - **Figma Status:** (only if task had `**Figma:**` section) — accessed successfully | unable to access Figma MCP
```

- [ ] **Step 3: Verify the changes**

Read `skills/implementing/implementer-prompt.md` and confirm:
- The Figma References section is placed before `## Your Job`
- The Report Format includes the Figma Status line
- No existing content was accidentally altered

- [ ] **Step 4: Commit**

```bash
git add skills/implementing/implementer-prompt.md
git commit -m "feat: add Figma MCP consumption instructions to implementer prompt"
```
