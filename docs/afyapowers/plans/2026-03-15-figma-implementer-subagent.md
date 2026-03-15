# Figma Implementer Subagent Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a dedicated Figma implementer subagent with internal self-correction loop, enhance the visual fidelity reviewer with two-pass comparison, and update SDD to route Figma tasks to the new implementer.

**Architecture:** New figma-implementer prompt template replaces the generic implementer for Figma tasks. SDD gains task routing logic. Visual fidelity reviewer gets two-pass comparison (visual + structured). Generic implementer has Figma sections removed.

**Tech Stack:** Markdown prompt templates, Figma MCP tools, Playwright MCP tools

---

## Chunk 1: Core Changes

### Task 1: Create Figma Implementer Prompt Template

**Depends on:** none

**Files:**
- Create: `skills/implementing/figma-implementer-prompt.md`

- [ ] **Step 1: Create the figma-implementer prompt template**

Create `skills/implementing/figma-implementer-prompt.md` with the following content. This follows the same Task tool general-purpose format as `implementer-prompt.md`:

````markdown
# Figma Implementer Subagent Prompt Template

Use this template when dispatching a Figma implementer subagent. Use this INSTEAD of
`implementer-prompt.md` when the task has a `**Figma:**` section.

```
Task tool (general-purpose):
  description: "Implement Figma Task N: [task name]"
  prompt: |
    You are implementing a Figma-referenced task: Task N: [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## File Constraint

    You may ONLY modify the files listed in your task's **Files:** section:
    [LIST OF FILES FROM TASK]

    Do NOT create, modify, or delete any other files. If you believe you need to
    touch a file not in this list, report back with status NEEDS_CONTEXT and explain
    what file you need and why.

    **Exception:** Preview files (temporary routes for visual verification) are exempt
    from this constraint. You may create preview files without them being listed.

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria
    - The approach or implementation strategy
    - Dependencies or assumptions
    - Anything unclear in the task description

    **Ask them now.** Raise any concerns before starting work.

    ## Phase 1: Extract Figma Design Context

    Before writing ANY code, you MUST fetch and process all Figma design data.

    ### Figma Tool Discovery

    Inspect available MCP tools to find Figma-related tools. Do NOT hardcode tool
    names — different Figma MCP servers use different names. Look for tools that
    match these capabilities:

    1. **Screenshot tool** — captures a visual render of a Figma node
    2. **Design context tool** — returns framework-specific styling and layout info
    3. **Metadata tool** — returns structural hierarchy (layer IDs, types, positions, sizes)
    4. **Variables/tokens tool** — returns design system variables (colors, spacing, typography)

    ### Fetch Sequence

    For each node URL in the task's `**Figma:**` section, call the tools in this order:

    1. **Screenshot first** — Look at it. Understand what you're building before
       reading any data. This screenshot will be reused across all self-correction
       iterations — do NOT re-fetch it.

    2. **Design context** — Before calling, detect the project's frontend stack by
       inspecting `package.json` and framework config files (e.g., `next.config.*`,
       `vite.config.*`, `nuxt.config.*`, `angular.json`). Request output in the
       detected framework format. If ambiguous, use the tool's default format.

    3. **Metadata** — Fetch structural hierarchy to understand nesting, layout
       direction, and component structure.

    4. **Design tokens** — Fetch design system variables. If available, use token
       names in your code when they map to the project's existing design system.

    **Graceful degradation:** If any tool fails or is unavailable, proceed with
    whatever data you have. The screenshot is most critical. If even screenshots
    fail, report `**Figma Status: partial access**`.

    **If no Figma MCP tools are available:** Report `**Figma Status: unable to access
    Figma MCP**` and proceed without visual context.

    ### Extract Design Spec Summary

    From the raw MCP output, extract a compact summary in this structured format.
    This summary becomes your working reference for all implementation and comparison
    work — not the raw MCP output.

    ```
    ## Design Spec Summary

    ### Colors
    - background: #FFFFFF
    - primary-text: #1A1A1A
    - accent: #3B82F6

    ### Spacing
    - section-padding: 48px
    - card-gap: 24px
    - content-margin: 16px

    ### Typography
    - heading: Inter, 32px, weight 700, line-height 1.2
    - body: Inter, 16px, weight 400, line-height 1.5

    ### Layout
    - container: flex, column
    - card-grid: grid, 3 columns, gap 24px

    ### Border Radius
    - card: 12px
    - button: 8px

    ### Shadows
    - card: 0 2px 8px rgba(0,0,0,0.1)

    ### Component Hierarchy
    - Page > Header > Nav + Logo
    - Page > Hero > Heading + Subtitle + CTA
    - Page > CardGrid > Card[3] > Image + Title + Description
    ```

    Adapt the sections to match what the Figma design actually contains. Not every
    section will be relevant for every design.

    ## Phase 2: Implement

    Now implement the component/page based on:
    - Your design spec summary (primary reference for values)
    - The Figma screenshot (primary reference for visual layout)
    - The task description (functional requirements)

    Follow the file structure defined in the task's **Files:** section.
    Follow existing patterns in the codebase.

    ## Phase 3: Create Preview Route

    After implementation, create a temporary preview route so you can visually
    verify your work.

    Create a route at `/dev/preview/ComponentName` adapted to the project's routing
    framework (e.g., `src/app/dev/preview/ComponentName/page.tsx` for Next.js).

    **Preview requirements:**
    - Render the component with representative props/data that exercise the visual
      states shown in Figma
    - If Figma shows multiple states (hover, disabled, error), render all states
      vertically on the same preview page
    - Keep the preview minimal — no extra layout, navigation, or decoration
    - For full-page tasks that already have a route, still create the preview if the
      actual page requires auth or complex data not available in dev

    ## Phase 4: Self-Correction Loop (Up to 5 Iterations)

    Run a tight visual verification loop. Do NOT hardcode Playwright MCP tool
    names — discover available tools at runtime.

    ### Each Iteration:

    1. **Wait for compilation** — After modifying code, wait for the dev server to
       finish recompilation. If the preview shows a build error, fix the code error
       first — this does NOT count as an iteration. If the dev server becomes
       unreachable, attempt to restart it once before reporting BLOCKED.

    2. **Navigate** — Use a Playwright navigation tool to open the preview route.

    3. **Take screenshot** — Use a Playwright screenshot tool to capture the
       implementation as rendered in the browser.

    4. **Visual compare** — Look at both images (your Figma screenshot from Phase 1
       vs the implementation screenshot). Identify obvious issues:
       - Missing or extra elements
       - Wrong layout direction or structure
       - Clearly wrong colors
       - Missing component states
       - Wrong proportions

    5. **Structured compare** — Use a Playwright snapshot tool to identify the DOM
       structure, then use an evaluate tool with `getComputedStyle` to extract actual
       CSS values from key elements. Target elements by role, text content, or CSS
       selectors.

       Compare against your design spec summary using these tolerances:
       - Colors: match after normalizing both sides to hex (note: `getComputedStyle`
         returns `rgb()` format — convert to hex before comparing)
       - Spacing/dimensions: within 4px tolerance
       - Typography: exact font-family, size within 2px, exact weight
       - Border radius: within 2px

    6. **Fix** — If discrepancies found, fix the code and go back to step 1.

    7. **Exit** — If no discrepancies found, or 5 iterations reached, proceed to
       reporting.

    **Track what you fix each iteration** to avoid thrashing (fixing the same thing
    back and forth). If you find yourself reverting a previous fix, stop and think
    about why — there may be an interaction between styles.

    ## Visual Fidelity Re-Dispatch

    If you are being re-dispatched due to a visual fidelity review failure, you
    will receive a discrepancy report listing specific elements with expected vs
    actual values.

    **Your job on re-dispatch:**
    1. Read each discrepancy carefully — element, aspect, expected value, actual value
    2. Fix each listed discrepancy precisely (match the exact Figma values)
    3. Do NOT make unrelated changes — only fix what's in the discrepancy report
    4. Use Figma MCP tools to re-verify the expected values if needed
    5. Run only 2 self-correction iterations (not 5) — the fix instructions are
       targeted and specific

    Report status as usual. Include `**Figma Status: fixes applied**` in your report.

    ## Testing

    This task does NOT use strict TDD (red-green-refactor). The self-correction loop
    with Playwright serves as the visual verification mechanism.

    If the task has functional/behavioral requirements beyond styling (e.g., form
    validation, click handlers, data fetching), write tests AFTER implementation to
    verify them. The red-green-refactor cycle is not required.

    ## Code Organization

    You reason best about code you can hold in context at once, and your edits are more
    reliable when files are focused. Keep this in mind:
    - Follow the file structure defined in the plan
    - Each file should have one clear responsibility with a well-defined interface
    - If a file you're creating is growing beyond the plan's intent, stop and report
      it as DONE_WITH_CONCERNS — don't split files on your own without plan guidance
    - If an existing file you're modifying is already large or tangled, work carefully
      and note it as a concern in your report
    - In existing codebases, follow established patterns. Improve code you're touching
      the way a good developer would, but don't restructure things outside your task.

    ## When You're in Over Your Head

    It is always OK to stop and say "this is too hard for me." Bad work is worse than
    no work. You will not be penalized for escalating.

    **STOP and escalate when:**
    - The task requires architectural decisions with multiple valid approaches
    - You need to understand code beyond what was provided and can't find clarity
    - You feel uncertain about whether your approach is correct
    - The task involves restructuring existing code in ways the plan didn't anticipate
    - You've been reading file after file trying to understand the system without progress

    **How to escalate:** Report back with status BLOCKED or NEEDS_CONTEXT. Describe
    specifically what you're stuck on, what you've tried, and what kind of help you need.
    The controller can provide more context, re-dispatch with a more capable model,
    or break the task into smaller pieces.

    ## Before Reporting Back: Self-Review

    Review your work with fresh eyes. Ask yourself:

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?
    - Does the implementation visually match the Figma design?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate?
    - Is the code clean and maintainable?

    **Visual Fidelity:**
    - Did the self-correction loop resolve all discrepancies?
    - Are there remaining issues I should flag?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, report:
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented (or what you attempted, if blocked)
    - What you tested and test results
    - Files changed
    - Self-review findings (if any)
    - Any issues or concerns
    - **Figma Status:** accessed successfully | partial access | unable to access Figma MCP | fixes applied
    - **Preview URL:** URL where the component can be viewed (e.g., http://localhost:3000/dev/preview/LoginForm)
    - **Preview File:** path to the preview file created (e.g., src/app/dev/preview/LoginForm/page.tsx)
    - **Self-Correction Iterations:** N/5 (how many loops were needed)
    - **Remaining Discrepancies:** (list any issues that remain after all iterations, if any)

    Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
    Use BLOCKED if you cannot complete the task. Use NEEDS_CONTEXT if you need
    information that wasn't provided. Never silently produce work you're unsure about.
```
````

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/figma-implementer-prompt.md
git commit -m "feat: add Figma implementer subagent prompt template"
```

---

### Task 2: Update Visual Fidelity Reviewer

**Depends on:** none

**Files:**
- Modify: `skills/implementing/visual-fidelity-reviewer-prompt.md`

- [ ] **Step 1: Rewrite the visual fidelity reviewer prompt**

Replace the entire content of `skills/implementing/visual-fidelity-reviewer-prompt.md` with the two-pass comparison approach:

````markdown
# Visual Fidelity Reviewer Prompt Template

Use this template when dispatching a visual fidelity reviewer subagent.

**Purpose:** Verify implementation visually matches Figma design using a two-pass comparison (visual judgment + structured CSS extraction)

**Only dispatch after spec compliance review passes, and only for tasks with `**Figma:**` references.**

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

    Compare the running implementation against the Figma design using a two-pass
    approach. You must use both Figma MCP tools and Playwright MCP tools.

    Do NOT hardcode any MCP tool names — discover available tools at runtime.

    ### Pass 1: Visual Judgment

    **Fetch Figma visual details:**

    Inspect available MCP tools for Figma-related tools. For each node URL in the
    Figma references:
    1. **Screenshot** — Fetch a visual capture of the node to see the design
    2. **Design Context** — Fetch styling and layout info for comparison data
    3. **Metadata** — Fetch structural hierarchy (positions, sizes, nesting)
    4. **Design Tokens** — Fetch variables (colors, spacing, typography) if available

    Use all available data to build your comparison baseline. If some tools are
    unavailable, work with what you have — screenshot + design context is sufficient.

    **Inspect the running implementation:**

    Using Playwright MCP tools:
    1. Navigate to the dev server URL and route provided above
    2. Take a screenshot of the implemented component(s)

    **Compare visually:**

    Look at both screenshots side by side. Identify obvious issues:
    - Missing or extra elements
    - Wrong layout direction or structure
    - Clearly wrong colors
    - Missing component states (hover, disabled, error)
    - Wrong proportions or visual character

    ### Pass 2: Structured Comparison

    Use a Playwright snapshot tool first to identify the DOM structure, then use
    an evaluate tool with `getComputedStyle` on targeted elements. Target elements
    by role, text content, or CSS selectors.

    **Important:** `getComputedStyle` returns colors in `rgb()` format. Convert to
    hex before comparing against Figma values.

    Compare numerically against Figma design data:
    - Colors: exact hex match (tolerate color space conversion differences)
    - Spacing: within 4px tolerance
    - Typography: exact font-family, size within 2px, exact weight
    - Dimensions: within 4px tolerance
    - Border radius: within 2px

    Also check:
    - Component states if defined in Figma (hover, active, disabled, etc.)
    - Responsive behavior if specified in Figma

    ### Tolerance Thresholds

    **Report as discrepancy (FAIL):**
    - Wrong layout structure (missing elements, wrong nesting, wrong flex/grid direction)
    - Visibly wrong colors (not sub-shade rendering differences)
    - Wrong typography (wrong font family, significantly wrong size/weight)
    - Spacing off by more than ~4px or visually noticeable
    - Missing component states when specified in Figma
    - Wrong proportions or sizing that changes visual character

    **Tolerate (PASS):**
    - Sub-pixel rounding differences (1-2px)
    - Minor font rendering differences between Figma and browser
    - Slight color variations due to color space conversion (sRGB vs display-P3)
    - Anti-aliasing differences
    - Differences in shadow/blur rendering between Figma and CSS

    **Guiding principle:** "Would a human reviewer flag this in a PR review?" If not,
    it passes.

    ### Report

    Report your findings:

    - **✅ Visual fidelity passed** — implementation matches Figma design
      (minor rendering differences within tolerance are acceptable)

    - **❌ Visual fidelity failed** — list each discrepancy with precise values:

      Discrepancy N: [short description]
      - Element: [CSS selector or description of the element]
      - Aspect: [layout/spacing/color/typography/states/responsive]
      - Expected (Figma): [exact value from Figma]
      - Actual (Implementation): [exact value from getComputedStyle or visual inspection]
      - Fix required: [specific instruction on what to change]

    **CRITICAL:** Do NOT pass a review with significant discrepancies. Focus on
    issues that a human reviewer would flag in a PR review — structural problems,
    visibly wrong colors, missing states, significantly wrong spacing. Tolerate
    minor rendering differences inherent to Figma-to-browser translation.
```

**Reviewer returns:** Pass/Fail with detailed discrepancy report if failed.
````

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/visual-fidelity-reviewer-prompt.md
git commit -m "feat: enhance visual fidelity reviewer with two-pass comparison"
```

---

### Task 3: Update SDD Orchestrator

**Depends on:** none

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md`

- [ ] **Step 1: Update the header description**

Change line 8 from:
```
Execute plan by dispatching subagents per task with three-stage review (spec compliance → code quality → visual fidelity). Tasks with no mutual dependencies run in parallel waves for faster execution.
```
To:
```
Execute plan by dispatching subagents per task with review stages. Non-Figma tasks: spec compliance → code quality. Figma tasks: spec compliance → visual fidelity (code quality skipped — the figma-implementer's internal self-correction loop handles visual accuracy). Tasks with no mutual dependencies run in parallel waves for faster execution.
```

- [ ] **Step 2: Update the core principle line**

Change line 10 from:
```
**Core principle:** Fresh subagent per task + three-stage review (spec compliance → code quality → visual fidelity) = high quality, fast iteration
```
To:
```
**Core principle:** Fresh subagent per task + appropriate review stages = high quality, fast iteration
```

- [ ] **Step 3: Update the process description after the digraph**

Change line 54 from:
```
Each dispatched Agent runs the full task pipeline: implement → spec review → quality review → visual fidelity review (if task has Figma refs). Multiple pipelines run concurrently.
```
To:
```
Each dispatched Agent runs the task pipeline. Non-Figma tasks: implement → spec review → code quality review. Figma tasks: implement (via figma-implementer with internal self-correction) → spec review → visual fidelity review. Multiple pipelines run concurrently.
```

- [ ] **Step 4: Update the process digraph to show task routing**

In the digraph (lines 14-51), add a routing decision node. Replace the dispatch node and its connections. Change:
```
    "Cap at max 3, dispatch parallel Agent calls" [shape=box];
```
To:
```
    "Cap at max 3" [shape=box];
    "Task has Figma refs?" [shape=diamond];
    "Dispatch figma-implementer" [shape=box];
    "Dispatch generic implementer" [shape=box];
```

And update the edges. Replace:
```
    "Validate file overlap in ready set" -> "Cap at max 3, dispatch parallel Agent calls";
    "Cap at max 3, dispatch parallel Agent calls" -> "Wait for all agents to return";
```
With:
```
    "Validate file overlap in ready set" -> "Cap at max 3";
    "Cap at max 3" -> "Task has Figma refs?";
    "Task has Figma refs?" -> "Dispatch figma-implementer" [label="yes"];
    "Task has Figma refs?" -> "Dispatch generic implementer" [label="no"];
    "Dispatch figma-implementer" -> "Wait for all agents to return";
    "Dispatch generic implementer" -> "Wait for all agents to return";
```

- [ ] **Step 5: Add task routing section after "Handling Implementer Status" (after line 242)**

Insert a new section:

```markdown
## Task Routing

When dispatching a task, check for a `**Figma:**` section in the task description:

- **Has `**Figma:**` references** → dispatch using `skills/implementing/figma-implementer-prompt.md`
- **No `**Figma:**` references** → dispatch using `skills/implementing/implementer-prompt.md`

This routing applies to both initial dispatch and re-dispatch after visual fidelity failure.
```

- [ ] **Step 6: Update the Visual Fidelity Review section**

Replace the "Visual Fidelity Review (Third Stage)" section header and first line. Change:
```
## Visual Fidelity Review (Third Stage)

After code quality review passes, if the task has a `**Figma:**` section AND visual validation was not skipped during pre-execution checks, dispatch a visual fidelity reviewer.
```
To:
```
## Visual Fidelity Review (Figma Tasks Only)

After spec compliance review passes for a Figma task (tasks with a `**Figma:**` section), if visual validation was not skipped during pre-execution checks, dispatch a visual fidelity reviewer. Code quality review is skipped for Figma tasks — the figma-implementer's internal self-correction loop handles visual accuracy directly.
```

- [ ] **Step 7: Update the re-dispatch instruction**

Change the re-dispatch text from:
```
After the implementer fixes, run the visual fidelity review again (skip spec compliance and code quality — those already passed).
```
To:
```
After the figma-implementer fixes, run the visual fidelity review again (skip spec compliance — it already passed).
```

- [ ] **Step 8: Update the iteration cap**

Change:
```
**Iteration cap:** If visual fidelity fails 3 times for the same task, stop retrying. Mark the task as `BLOCKED` with the accumulated discrepancy reports and surface to the user:

> "Task N has failed visual fidelity review 3 times. The following discrepancies could not be resolved automatically: [list]. Please review and provide guidance."
```
To:
```
**Iteration cap:** 5 total visual fidelity review cycles per task. A cycle = one visual fidelity review dispatch. The initial review counts as cycle 1, each re-review after a fix counts as another. After 5 cycles, stop retrying. Mark the task as `BLOCKED` with the accumulated discrepancy reports and surface to the user:

> "Task N has failed visual fidelity review 5 times. The following discrepancies could not be resolved automatically: [list]. Please review and provide guidance."
```

- [ ] **Step 9: Update the Prompt Templates section**

Change:
```
## Prompt Templates

- `skills/implementing/implementer-prompt.md` - Dispatch implementer subagent
- `skills/implementing/spec-reviewer-prompt.md` - Dispatch spec compliance reviewer subagent
- `skills/implementing/code-quality-reviewer-prompt.md` - Dispatch code quality reviewer subagent
- `skills/implementing/visual-fidelity-reviewer-prompt.md` - Dispatch visual fidelity reviewer subagent
```
To:
```
## Prompt Templates

- `skills/implementing/implementer-prompt.md` - Dispatch implementer subagent (non-Figma tasks)
- `skills/implementing/figma-implementer-prompt.md` - Dispatch Figma implementer subagent (tasks with `**Figma:**` refs)
- `skills/implementing/spec-reviewer-prompt.md` - Dispatch spec compliance reviewer subagent
- `skills/implementing/code-quality-reviewer-prompt.md` - Dispatch code quality reviewer subagent (non-Figma tasks only)
- `skills/implementing/visual-fidelity-reviewer-prompt.md` - Dispatch visual fidelity reviewer subagent (Figma tasks only)
```

- [ ] **Step 10: Update Red Flags section**

Change:
```
- Skip any review stage (spec compliance, code quality, or visual fidelity)
```
To:
```
- Skip any applicable review stage (non-Figma: spec compliance + code quality; Figma: spec compliance + visual fidelity)
```

Change:
```
- **Start code quality review before spec compliance passes** (wrong order)
- **Start visual fidelity review before code quality passes** (wrong order)
```
To:
```
- **Start code quality review before spec compliance passes** (wrong order, non-Figma tasks)
- **Start visual fidelity review before spec compliance passes** (wrong order, Figma tasks)
```

- [ ] **Step 11: Update the Integration section's subagent prompts**

Change:
```
**Subagent prompts:**
- `skills/implementing/implementer-prompt.md` — TDD rules are embedded directly in this prompt
- `skills/implementing/spec-reviewer-prompt.md` — spec compliance review
- `skills/implementing/code-quality-reviewer-prompt.md` — code quality review
- `skills/implementing/visual-fidelity-reviewer-prompt.md` — visual fidelity review (third stage, Figma tasks only)
```
To:
```
**Subagent prompts:**
- `skills/implementing/implementer-prompt.md` — TDD implementer for non-Figma tasks
- `skills/implementing/figma-implementer-prompt.md` — Figma implementer with internal self-correction loop (Figma tasks)
- `skills/implementing/spec-reviewer-prompt.md` — spec compliance review
- `skills/implementing/code-quality-reviewer-prompt.md` — code quality review (non-Figma tasks only)
- `skills/implementing/visual-fidelity-reviewer-prompt.md` — visual fidelity review (Figma tasks only)
```

- [ ] **Step 12: Update preview cleanup to remove Storybook references**

In the visual fidelity passed section, change:
```
**If ✅ Visual fidelity passed:** Mark task as completed. Then check if the implementer reported a `**Preview File:**` path. If so, immediately delete that file to clean up the temporary preview before proceeding to the next task or wave.
```
To:
```
**If ✅ Visual fidelity passed:** Mark task as completed. Then check if the implementer reported a `**Preview File:**` path. If so, immediately delete that file (the temporary preview route) before proceeding to the next task or wave.
```

- [ ] **Step 13: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat: add Figma task routing and 2-stage review pipeline to SDD"
```

---

### Task 4: Clean Up Generic Implementer

**Depends on:** 1

**Files:**
- Modify: `skills/implementing/implementer-prompt.md`

- [ ] **Step 1: Remove Figma-specific sections**

Remove these three sections entirely from the prompt template (find each by its `##` header and remove everything up to the next `##` header):

1. The `## Figma References` section (includes the `### Figma Tool Sequence` subsection — remove everything from `## Figma References` up to but not including `## Visual Fidelity Re-Dispatch`)
2. The `## Visual Fidelity Re-Dispatch` section (remove everything from `## Visual Fidelity Re-Dispatch` up to but not including `## Component Preview`)
3. The `## Component Preview` section (remove everything from `## Component Preview` up to but not including `## Your Job`)

- [ ] **Step 2: Remove Figma-specific report fields**

In the Report Format section, remove:
```
    - **Figma Status:** (only if task had `**Figma:**` section) — accessed successfully | unable to access Figma MCP | partial access | fixes applied
    - **Preview URL:** (only if preview was created) — URL where the component can be viewed (e.g., http://localhost:3000/dev/preview/LoginForm)
    - **Preview File:** (only if preview was created) — path to the preview file created (e.g., src/app/dev/preview/LoginForm/page.tsx)
```

- [ ] **Step 3: Commit**

```bash
git add skills/implementing/implementer-prompt.md
git commit -m "refactor: remove Figma-specific sections from generic implementer"
```
