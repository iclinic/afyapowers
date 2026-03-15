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

    ## What Implementer Claims They Built

    [FROM IMPLEMENTER'S REPORT]

    ## Your Job

    Compare the running implementation against the Figma design. You must use
    both Figma MCP tools and Playwright MCP tools to perform this review.

    ### Step 1: Fetch Figma Visual Details

    Inspect the available MCP tools in your environment to find Figma-related
    tools (do NOT hardcode tool names — different servers use different names).

    For each node URL in the Figma references, fetch:
    - Layout structure and hierarchy
    - Spacing and sizing values (padding, margin, gap, width, height)
    - Colors (fill, stroke, background — exact hex/rgba values)
    - Typography (font family, size, weight, line height, letter spacing)
    - Design tokens if available
    - Component states (hover, active, disabled, focus) if defined
    - Responsive behavior / constraints if specified

    ### Step 2: Inspect the Running Implementation

    Inspect the available MCP tools in your environment to find Playwright-related
    tools (do NOT hardcode tool names).

    Using Playwright MCP tools:
    1. Navigate to the relevant page/component in the running dev server
    2. Take screenshots of the implemented component(s)
    3. Inspect computed styles, dimensions, and spacing of key elements
    4. Check component states if defined in Figma (hover, active, disabled, etc.)
    5. Check responsive behavior if specified in Figma

    ### Step 3: Compare

    For each Figma reference, compare the implementation against the design on:

    | Aspect | What to Check |
    |--------|---------------|
    | Layout | Element hierarchy, positioning, flex/grid structure |
    | Spacing | Padding, margin, gap values (exact match) |
    | Sizing | Width, height, min/max constraints |
    | Colors | Background, text, border, shadow colors (exact hex match) |
    | Typography | Font family, size, weight, line height, letter spacing |
    | States | Hover, active, disabled, focus appearances |
    | Responsive | Breakpoint behavior if specified in Figma |

    **Be precise.** Compare actual values, not approximations. A 2px spacing
    difference or a slightly different shade of blue counts as a discrepancy.

    ### Step 4: Report

    Report your findings:

    - **✅ Visual fidelity passed** — implementation matches Figma design
    - **❌ Visual fidelity failed** — list each discrepancy:
      - Element: [which element]
      - Aspect: [layout/spacing/color/typography/states/responsive]
      - Expected (Figma): [exact value]
      - Actual (Implementation): [exact value]
      - Fix required: [what needs to change]

    **CRITICAL:** Do NOT pass a review with known discrepancies. If there is
    any mismatch between the Figma design and the implementation, report it
    as failed. The implementer will be re-dispatched to fix the issues.
```

**Reviewer returns:** Pass/Fail with detailed discrepancy report if failed.
