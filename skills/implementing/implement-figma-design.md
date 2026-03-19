# Figma Design Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for a task that has a **Figma:** section. This replaces the standard `implementer-prompt.md` for Figma tasks.

**Key difference from standard implementer:** No TDD. The workflow follows the Figma implement-design pattern — fetch design context, capture visual reference, download assets, translate to project conventions, achieve visual parity, validate against Figma.

```
Task tool (general-purpose):
  description: "Implement Figma Task N: [task name]"
  prompt: |
    You are implementing a Figma design task: Task N — [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## Figma Resources

    **File Key:** [FILE_KEY from task's Figma section]
    **Breakpoints:** [BREAKPOINTS from task's Figma section]
    **Nodes:**
    [NODES TABLE from task's Figma section]

    ## File Constraint

    You may ONLY modify the files listed in your task's **Files:** section:
    [LIST OF FILES FROM TASK]

    Do NOT create, modify, or delete any other files. If you believe you need to
    touch a file not in this list, report back with status NEEDS_CONTEXT and explain
    what file you need and why.

    ## Before You Begin

    If you have questions about:
    - The design requirements or component behavior
    - The project's design system or conventions
    - Dependencies or assumptions
    - Anything unclear in the task description

    **Ask them now.** Raise any concerns before starting work.

    ## Prerequisites

    - Figma MCP server must be connected and accessible
      - Before proceeding, verify the Figma MCP server is connected by checking if
        Figma MCP tools (e.g., get_design_context, get_variable_defs) are available.
      - If the tools are not available, report back with status BLOCKED and explain
        that the Figma MCP server is required but not accessible.

    ## Your Job: Required Workflow

    **Follow these steps in order. Do not skip steps.**

    ### Step 1a: Fetch Authoritative Design Tokens

    Run get_variable_defs for each node ID in your Figma Resources table **first**.

        get_variable_defs(fileKey="<file_key>", nodeId="<node_id>")

    This builds the authoritative token reference table — a mapping of token names
    to their actual values for:
    - Colors (fill, stroke, background, text)
    - Typography (font family, size, weight, line height)
    - Spacing (padding, margin, gap)
    - Border radius, shadows, opacity

    Keep this lookup table accessible — you will use it in Step 1b to validate
    token names from get_design_context.

    **Token Mapping Rule — apply this when translating tokens to project code:**
    1. **Name match + value match:** Figma variable name matches a project token
       by name AND their resolved values are identical → use the project token
    2. **Name match + value mismatch:** Figma variable name matches a project token
       by name BUT the values differ → use the exact Figma value hardcoded
       (Figma is the source of truth)
    3. **No name match:** No project token matches → use the exact Figma value
       hardcoded

    **Never** approximate or use a "closest" project token. It is either an exact
    match (name + value) or a hardcoded Figma value.

    ### Step 1b: Fetch Design Context with Token Cross-Reference

    Run get_design_context for each node ID in your Figma Resources table.

        get_design_context(fileKey="<file_key>", nodeId="<node_id>")

    This provides:
    - Component hierarchy and children ordering
    - Auto-layout direction and mode (row/column, wrap, etc.)
    - Constraints and sizing modes (fixed/hug/fill)
    - Variants and interactive states (hover, active, disabled, focus)
    - Component props and slot/composition patterns
    - Implementation suggestions with token names

    **Cross-reference all token names** from this output against the lookup table
    from Step 1a. For each token name in the implementation suggestions, apply the
    Token Mapping Rule to determine the correct value to use.

    **If the response is too large or truncated:**
    1. Run get_metadata(fileKey="<file_key>", nodeId="<node_id>") to get the
       high-level node map
    2. Identify the specific child nodes needed from the metadata
    3. Fetch individual child nodes with
       get_design_context(fileKey="<file_key>", nodeId="<child_node_id>")

    **Fallback:** If get_variable_defs returns no tokens for a node, use the raw
    resolved values from get_design_context and report the affected properties as
    DONE_WITH_CONCERNS so they can be verified in the review phase.

    ### Step 2: Capture Visual Reference

    Run get_screenshot for the primary node(s) in your task.

        get_screenshot(fileKey="<file_key>", nodeId="<node_id>")

    This screenshot serves as the **source of truth for visual validation** (does the
    layout look right?). Note: `get_variable_defs` from Step 1a is the source of truth
    for **token values** (what exact color/font/spacing value to use). These are
    complementary — tokens tell you what values to code, the screenshot tells you if
    the result looks correct. Keep the screenshot accessible throughout implementation.
    You will compare your output against this screenshot before reporting back.

    ### Step 3: Download Required Assets

    Download any assets (images, icons, SVGs) returned by the Figma MCP server.

    **IMPORTANT:** Follow these asset rules:
    - Use asset URLs exactly as returned by the Figma MCP server — do NOT modify them
    - DO NOT import or add new icon packages — all assets should come from the Figma
      payload
    - DO NOT use or create placeholders if a source URL is provided by the MCP server
    - If an asset URL is inaccessible, note it as a concern but continue with the rest
    - **Icons must be saved as SVG**, not as raster image formats (PNG, JPG, WebP, etc.).
      When downloading icons from Figma, request them in SVG format and save them as
      `.svg` files. Other assets like background images, photos, and illustrations may
      remain as raster images.

    ### Step 4: Translate to Project Conventions

    Translate the Figma output into the project's framework, styles, and conventions.

    **Key principles:**
    - Use the get_design_context implementation suggestions (Step 1b) as a starting
      point, but cross-reference all token names against the get_variable_defs lookup
      table (Step 1a)
    - Map Figma variable names from Step 1a to project design system tokens by name;
      verify values match before using the project token (see Token Mapping Rule in
      Step 1a)
    - If no matching token exists or values differ, use the exact Figma value
      hardcoded — never approximate with a "close enough" project token
    - Reuse existing components (buttons, inputs, typography, icon wrappers) instead
      of duplicating functionality
    - Respect existing routing, state management, and data-fetch patterns

    **Design System Integration:**
    - ALWAYS use components from the project's design system when possible
    - Map Figma variable names to project design tokens using the Token Mapping Rule
      (Step 1a)
    - When a matching component exists, extend it rather than creating a new one
    - Document any new components added to the design system

    ### Step 5: Achieve 1:1 Visual Parity

    Strive for pixel-perfect visual parity with the Figma design across **all
    breakpoints specified in your task**.

    **Guidelines:**
    - Prioritize Figma fidelity to match designs exactly
    - Avoid hardcoded values — use design tokens from Figma where available
      (fetch with get_variable_defs if needed)
    - When conflicts arise between design system tokens and Figma specs, prefer design
      system tokens but adjust spacing or sizes minimally to match visuals
    - Follow WCAG requirements for accessibility
    - Keep components composable and reusable
    - Add TypeScript types for component props
    - Avoid inline styles unless truly necessary for dynamic values

    ### Step 6: Validate Against Figma

    Before marking complete, validate the final UI against the Figma screenshot from
    Step 2.

    **Validation checklist:**
    - [ ] Layout matches (spacing, alignment, sizing)
    - [ ] Typography matches (font, size, weight, line height)
    - [ ] Colors match exactly
    - [ ] Interactive states work as designed (hover, active, disabled)
    - [ ] Responsive behavior across all specified breakpoints
    - [ ] Assets render correctly
    - [ ] Accessibility standards met

    If you find discrepancies, fix them now. Compare side-by-side with the screenshot.
    Check spacing, colors, and typography values in the design context data.

    ### Step 7: Commit

    Commit your work with a descriptive message.

    ## Code Organization

    You reason best about code you can hold in context at once, and your edits are more
    reliable when files are focused. Keep this in mind:
    - Follow the file structure defined in the plan
    - Each file should have one clear responsibility with a well-defined interface
    - Place UI components in the project's designated design system directory
    - Follow the project's component naming conventions
    - If a file you're creating is growing beyond the plan's intent, stop and report
      it as DONE_WITH_CONCERNS — don't split files on your own without plan guidance
    - In existing codebases, follow established patterns

    ## When You're in Over Your Head

    It is always OK to stop and say "this is too hard for me." Bad work is worse than
    no work. You will not be penalized for escalating.

    **STOP and escalate when:**
    - The design is too complex to implement accurately in one pass
    - You need to understand code beyond what was provided and can't find clarity
    - You feel uncertain about whether your implementation matches the design
    - The task involves restructuring existing code in ways the plan didn't anticipate
    - Asset URLs are inaccessible and the design can't be implemented without them

    **How to escalate:** Report back with status BLOCKED or NEEDS_CONTEXT. Describe
    specifically what you're stuck on, what you've tried, and what kind of help you need.

    ## Before Reporting Back: Self-Review

    Review your work with fresh eyes. Ask yourself:

    **Visual Fidelity:**
    - Does the implementation match the Figma screenshot pixel-for-pixel?
    - Are all breakpoints covered and responsive behavior correct?
    - Did I capture all interactive states (hover, active, disabled, focus)?

    **Design System Integration:**
    - Did I reuse existing components where possible?
    - Are design tokens mapped correctly (project tokens over hardcoded values)?
    - Does the component follow the project's naming and organization conventions?

    **Asset Handling:**
    - Are all assets from the Figma payload used correctly?
    - Did I avoid importing external icon packages?
    - Do all assets render correctly?

    **Quality:**
    - Is the code clean and maintainable?
    - Did I avoid overbuilding (YAGNI)?
    - Did I follow existing patterns in the codebase?

    **Deviations:**
    - If I deviated from the Figma design, did I document why in code comments?
    - Are deviations limited to accessibility or technical constraints?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, report:
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented (component structure, key decisions)
    - Visual validation results (did it match the screenshot?)
    - Breakpoints covered
    - Files changed
    - Self-review findings (if any)
    - Any deviations from the Figma design and why

    Use DONE_WITH_CONCERNS if you completed the work but have doubts about visual
    accuracy or asset handling. Use BLOCKED if you cannot complete the task (e.g.,
    Figma MCP unavailable). Use NEEDS_CONTEXT if you need information that wasn't
    provided. Never silently produce work you're unsure about.

    Be thorough with DONE_WITH_CONCERNS — this is your primary channel for flagging
    issues to the review phase. If anything feels uncertain, incomplete, or fragile,
    flag it. The review phase will prioritize your concerns. Err on the side of
    flagging — a false alarm costs nothing, a missed concern costs a review cycle.

    ## Common Issues and Solutions

    ### Issue: Figma output is truncated
    **Cause:** The design is too complex or has too many nested layers.
    **Solution:** Use get_metadata to get the node structure, then fetch specific
    nodes individually with get_design_context.

    ### Issue: Design doesn't match after implementation
    **Cause:** Visual discrepancies between implemented code and Figma design.
    **Solution:** Compare side-by-side with screenshot from Step 2. Check spacing,
    colors, and typography values in the design context data.

    ### Issue: Assets not loading
    **Cause:** Asset URLs are inaccessible or have been modified.
    **Solution:** Use asset URLs exactly as returned by the Figma MCP server. Do not
    modify, proxy, or replace them. If still inaccessible, report as DONE_WITH_CONCERNS.

    ### Issue: Design token values differ from project
    **Cause:** Project design system tokens have different values than Figma specs.
    **Solution:** Prefer project tokens for consistency but adjust spacing/sizing
    minimally to maintain visual fidelity. Document the deviation.
```
