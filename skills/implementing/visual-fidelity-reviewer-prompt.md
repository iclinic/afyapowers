# Visual Fidelity Reviewer Prompt Template

Use this template when dispatching a visual fidelity reviewer subagent.

**Purpose:** Verify implementation visually matches Figma design (layout, spacing, colors, typography, states)

**Only dispatch after code quality review passes, and only for tasks with `**Figma:**` references.**

```
Task tool (general-purpose):
  description: "Review visual fidelity for Task N"
  prompt: |
    You are reviewing whether a UI implementation visually matches its Figma design.

    ## Task Figma References

    [FIGMA REFERENCES FROM TASK'S **Figma:** SECTION]

    ## Files Changed

    [LIST OF FILES THE IMPLEMENTER MODIFIED]

    ## Dev Server

    [DEV SERVER BASE URL — e.g., http://localhost:3000]
    [PREVIEW URL OR PAGE ROUTE — from implementer's **Preview URL:** field,
     or the actual page route if implementing a full page]

    ## What Implementer Claims They Built

    [FROM IMPLEMENTER'S REPORT]

    ## Your Job

    Compare the running implementation against the Figma design. You must use
    both Figma MCP tools and Playwright MCP tools to perform this review.

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

    ### Step 2: Inspect the Running Implementation

    Inspect the available MCP tools in your environment to find Playwright-related
    tools (do NOT hardcode tool names).

    Using Playwright MCP tools:
    1. Navigate to the dev server URL and route provided above
    2. Take screenshots of the implemented component(s)
    3. Inspect computed styles, dimensions, and spacing of key elements
    4. Check component states if defined in Figma (hover, active, disabled, etc.)
    5. Check responsive behavior if specified in Figma

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

**Reviewer returns:** Pass/Fail with detailed discrepancy report if failed.
