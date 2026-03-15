# Figma Workflow V2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve Figma-to-implementation visual fidelity by adding screenshots to discovery, specific tool sequences to the implementer, component preview surfaces for testing, and practical fidelity thresholds.

**Architecture:** Four coordinated updates to existing skill/prompt files. No new files created. All changes are prompt text — no runtime code or tests.

**Tech Stack:** Markdown skill files

---

## Chunk 1: Skill and Prompt Updates

### Task 1: Add screenshots to Figma discovery

**Depends on:** none

**Files:**
- Modify: `skills/figma-discovery/SKILL.md`

- [ ] **Step 1: Update the skill description line**

Change line 10:

Old:
```
**This skill is invoked by the Design skill** — do not invoke it directly. It runs late in the Design phase, after the design is shaped but before writing the spec document.
```

New:
```
**This skill is invoked by the Design skill** — do not invoke it directly. It runs early in the Design phase (step 2, after context exploration), so discovered layouts inform the entire design conversation.
```

- [ ] **Step 2: Add Step 4.5 between Step 4 and Step 5**

After the Step 4 section (after line 62 — "Wait for the user to confirm. If the user confirms zero nodes, exit the skill — no Figma References section will be written."), add the following new section:

```markdown
### Step 4.5: Fetch Screenshots

For each confirmed node, fetch a screenshot to provide visual context for the design conversation:

1. Look for a screenshot-related Figma MCP tool (e.g., one that captures or renders a node as an image)
2. Call it for each confirmed node
3. Present the screenshots inline in the conversation

This gives the design skill actual visual context — the agent can now see what the layouts look like, not just their names.

**If no screenshot tool is available:** Warn the user:

> "Screenshot tool not available in the current Figma MCP server. Continuing without visual previews — discovery still produces references as normal."

Continue to Step 5.

**If a screenshot fails for a specific node:** Warn for that node and continue with the others. Not every node needs a screenshot for discovery to be useful.

**Note:** Screenshots are conversational context only — they inform the design discussion but are NOT written to the spec document. The implementer fetches its own screenshots later during implementation.
```

- [ ] **Step 3: Commit**

```bash
git add skills/figma-discovery/SKILL.md
git commit -m "feat: add screenshot fetching to Figma discovery (Step 4.5)"
```

---

### Task 2: Replace implementer Figma instructions with specific tool sequence and add component preview

**Depends on:** none

**Files:**
- Modify: `skills/implementing/implementer-prompt.md`

- [ ] **Step 1: Replace the Figma References section**

Replace the entire `## Figma References` section in the implementer prompt (lines 38-55 of the template, inside the code block) with:

```
    ## Figma References

    If your task has a `**Figma:**` section, you MUST fetch visual details from Figma
    BEFORE writing any code. Follow this sequence for each node URL:

    ### Figma Tool Sequence (in order)

    1. **Screenshot** — Find a screenshot/render tool in the available Figma MCP tools
       and fetch a visual capture of the node. Look at it. Understand what you're
       building before reading any data.

    2. **Design Context** — Find a design-context tool that returns styling and layout
       information. Before calling it, detect the project's frontend stack by inspecting
       `package.json` and framework config files (e.g., `next.config.*`, `vite.config.*`,
       `nuxt.config.*`, `angular.json`). Request output in the detected framework format.
       If the stack is ambiguous, use the tool's default output format.

    3. **Metadata** — Find a metadata tool that returns the node's structural hierarchy
       (layer IDs, types, positions, sizes). Use this to understand nesting, layout
       direction, and component structure.

    4. **Design Tokens** — Find a variables/tokens tool that returns design system
       variables (colors, spacing, typography). If available, use token names in your
       code when they map to the project's existing design system.

    **Order matters.** Screenshot first (mental model), then code context, then
    structure, then tokens. Cross-reference all sources when implementing.

    **Graceful degradation:** If any tool fails or is unavailable, proceed with
    whatever data you have. The screenshot is most critical. If even screenshots
    fail, report `**Figma Status: partial access**`.

    Do NOT hardcode Figma MCP tool names — discover available tools at runtime.

    **If no Figma MCP tools are available:** Proceed without visual context, but
    include `**Figma Status: unable to access Figma MCP**` in your report.

    If your task does NOT have a `**Figma:**` section, ignore this — proceed normally.
```

- [ ] **Step 2: Add Component Preview section after Visual Fidelity Re-Dispatch section**

After the `## Visual Fidelity Re-Dispatch` section (after line 70 — "Report status as usual. Include `**Figma Status: fixes applied**` in your report."), add:

```
    ## Component Preview

    If your task implements an isolated component (not a full page with its own route),
    you MUST create a preview surface so the visual fidelity reviewer can see it.

    **Detection:**
    1. Check if Storybook exists: look for `.storybook/` directory or `storybook`
       in `package.json` devDependencies
    2. If Storybook exists → create a story file following the project's existing
       story conventions (look at existing `*.stories.*` files for the pattern)
    3. If no Storybook → create a temporary preview route at a path like
       `/dev/preview/ComponentName` (adapt to the project's routing framework)

    **Preview requirements:**
    - Render the component with representative props/data that exercise the visual
      states shown in Figma
    - If Figma shows multiple states (hover, disabled, error), render all states
      vertically on the same preview page
    - Keep the preview minimal — no extra layout, navigation, or decoration

    **File constraint exemption:** Preview files are exempt from the "you may ONLY
    modify files in your task's **Files:** section" constraint. You may create preview
    files without them being listed in your task.

    **If Storybook is detected but story creation fails:** Fall back to the temporary
    route approach.

    **If preview creation fails entirely:** Report BLOCKED with details.

    **Page-level tasks:** If your task implements a full page that already has a route,
    skip preview creation — the reviewer will navigate to the actual route.
```

- [ ] **Step 3: Add Preview URL and Preview File to the report format**

In the Report Format section (around line 182), add two new fields after the Figma Status line:

Old:
```
    - **Figma Status:** (only if task had `**Figma:**` section) — accessed successfully | unable to access Figma MCP | fixes applied
```

New:
```
    - **Figma Status:** (only if task had `**Figma:**` section) — accessed successfully | unable to access Figma MCP | partial access | fixes applied
    - **Preview URL:** (only if preview was created) — URL where the component can be viewed (e.g., http://localhost:3000/dev/preview/LoginForm)
    - **Preview File:** (only if preview was created) — path to the preview file created (e.g., src/app/dev/preview/LoginForm/page.tsx)
```

- [ ] **Step 4: Commit**

```bash
git add skills/implementing/implementer-prompt.md
git commit -m "feat: add specific Figma tool sequence and component preview to implementer"
```

---

### Task 3: Update visual fidelity reviewer with practical threshold

**Depends on:** none

**Files:**
- Modify: `skills/implementing/visual-fidelity-reviewer-prompt.md`

- [ ] **Step 1: Replace the comparison instructions in Step 3**

Replace the Step 3 section (lines 63-78 inside the code block) with:

```
    ### Step 3: Compare

    For each Figma reference, compare the implementation against the design.

    **Report as a discrepancy (FAIL):**
    - Wrong layout structure (missing elements, wrong nesting, wrong flex/grid direction)
    - Visibly wrong colors (not sub-shade rendering differences)
    - Wrong typography (wrong font family, significantly wrong size/weight)
    - Significantly wrong spacing (off by more than ~4px, or visually noticeable gaps)
    - Missing component states (hover/disabled/error not implemented when specified in Figma)
    - Wrong proportions or sizing that changes the visual character

    **Tolerate (PASS):**
    - Sub-pixel rounding differences (1-2px)
    - Minor font rendering differences between Figma and browser
    - Slight color variations due to color space conversion (sRGB vs display-P3)
    - Anti-aliasing differences
    - Differences in shadow/blur rendering between Figma and CSS

    **Guiding principle:** "Would a human reviewer flag this in a PR review?" If not,
    it passes.
```

- [ ] **Step 2: Replace the Step 4 Report section**

Replace lines 80-94 (the Step 4 and CRITICAL note) with:

```
    ### Step 4: Report

    Report your findings:

    - **✅ Visual fidelity passed** — implementation matches Figma design
      (minor rendering differences within tolerance are acceptable)
    - **❌ Visual fidelity failed** — list each discrepancy:
      - Element: [which element]
      - Aspect: [layout/spacing/color/typography/states/responsive]
      - Expected (Figma): [value]
      - Actual (Implementation): [value]
      - Fix required: [what needs to change]

    **CRITICAL:** Do NOT pass a review with significant discrepancies. Focus on
    issues that a human reviewer would flag in a PR review — structural problems,
    visibly wrong colors, missing states, significantly wrong spacing. Tolerate
    minor rendering differences inherent to Figma-to-browser translation.
```

- [ ] **Step 3: Update the Dev Server section to clarify preview URL usage**

Replace lines 23-27 (the `## Dev Server` section inside the code block, including the route line) with:

```
    ## Dev Server

    [DEV SERVER BASE URL — e.g., http://localhost:3000]
    [PREVIEW URL OR PAGE ROUTE — from implementer's **Preview URL:** field,
     or the actual page route if implementing a full page]
```

- [ ] **Step 4: Update Step 1 to use specific Figma tool types**

Replace lines 37-49 (Step 1: Fetch Figma Visual Details) with:

```
    ### Step 1: Fetch Figma Visual Details

    Inspect the available MCP tools in your environment to find Figma-related
    tools (do NOT hardcode tool names — different servers use different names).

    For each node URL in the Figma references:
    1. **Screenshot** — Fetch a visual capture of the node to see the design
    2. **Design Context** — Fetch styling and layout info for comparison data
    3. **Metadata** — Fetch structural hierarchy (positions, sizes, nesting)
    4. **Design Tokens** — Fetch variables (colors, spacing, typography) if available

    Use all available data to build your comparison baseline. If some tools
    are unavailable, work with what you have — screenshot + design context
    is sufficient for most comparisons.
```

- [ ] **Step 5: Commit**

```bash
git add skills/implementing/visual-fidelity-reviewer-prompt.md
git commit -m "feat: update visual fidelity reviewer with practical threshold and tool sequence"
```

---

### Task 4: Update SDD with preview cleanup and preview URL passthrough

**Depends on:** 2, 3

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md`

- [ ] **Step 1: Update the Visual Fidelity Review section to pass preview URL**

In the "Visual Fidelity Review (Third Stage)" section (lines 244-270), update the "Provide to the reviewer" list.

Old:
```
**Provide to the reviewer:**
- The task's `**Figma:**` references
- The dev server URL and route to the component
- The list of files the implementer modified
- The implementer's report summary
```

New:
```
**Provide to the reviewer:**
- The task's `**Figma:**` references
- The dev server base URL
- The preview URL or page route: use the implementer's `**Preview URL:**` field if present, otherwise use the actual page route for the component
- The list of files the implementer modified
- The implementer's report summary
```

- [ ] **Step 2: Add preview cleanup after visual fidelity passes**

After the "If ✅ Visual fidelity passed: Mark task as completed." line (line 256), add:

```
After marking the task as completed, check if the implementer reported a `**Preview File:**` path. If so, immediately delete that file to clean up the temporary preview. Do this before proceeding to the next task or wave.

```

- [ ] **Step 3: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat: add preview URL passthrough and cleanup to SDD"
```
