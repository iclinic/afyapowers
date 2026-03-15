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
