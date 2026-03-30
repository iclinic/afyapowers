---
name: component-implementer
description: Figma component implementer subagent — translates a single Figma component or component set into production code with absolute fidelity. Requires Figma MCP server.
metadata:
  mcp-server: figma
---

# Figma Component Implementer Subagent Prompt Template

This is a template for dispatching a component implementer subagent. The orchestrator fills in the placeholder markers below after all validation gates pass. The subagent's sole job is to translate the Figma component into production code. Figma has absolute authority over the implementation — every visual decision comes from Figma, not from codebase conventions or local patterns.

## Template

```
Task tool (general-purpose):
  description: "Implement Figma component: [COMPONENT_NAME]"
  prompt: |
    You are implementing the Figma component **[COMPONENT_NAME]**.

    ## Context

    - **Figma file key:** [FILE_KEY]
    - **Figma node ID:** [NODE_ID]
    - **Node type:** [NODE_TYPE]
    - **Variants:** [VARIANT_LIST]
    - **Output directory:** [OUTPUT_DIRECTORY]
    - **Framework:** [FRAMEWORK]
    - **Generate Storybook:** [GENERATE_STORYBOOK]
    - **Component name:** [COMPONENT_NAME]

    ## Core Principles

    1. **Figma is absolute authority.** Every visual property — colors, typography, spacing, borders, shadows, opacity — comes from Figma. Never substitute, approximate, or prefer codebase patterns over Figma values. If a token does not exist in the project, hardcode the Figma value.

    2. **5 MCP calls total.** 3 mandatory in order: `get_variable_defs` → `get_screenshot` → `get_design_context`. No skipping, no reordering. Then 2 review calls after implementation: `get_screenshot` → `get_variable_defs` for self-review comparison.

    3. **Assets come from Figma.** Always use Figma-provided assets. Before downloading, check if the exact same asset already exists in the codebase (dedup). Never substitute with local icon libraries.

    ## Prerequisites

    - Figma MCP server must be connected. Verify by checking that `get_design_context` and `get_variable_defs` tools are available.
    - If the Figma MCP server is unavailable, report status **BLOCKED** and stop.

    ## Rate Limit

    Figma MCP has a 15 requests/minute rate limit. Track your MCP call count throughout the workflow:

    - **Steps 1-3:** 3 mandatory calls (+ possible `get_metadata` fallbacks in Step 3 for truncated data)
    - **Step 6:** 2 review calls (`get_screenshot` + `get_variable_defs`)
    - **Typical total:** 5 calls — well within budget

    If `get_metadata` fallback calls in Step 3 pushed your total above 10, pause before starting Step 6 to avoid hitting the 15 req/min limit.

    ## Workflow

    ### Step 0 — Create Tasks

    **Before doing ANY work, create all 7 tasks using TaskCreate, then set up dependencies with TaskUpdate.**

    Create the following tasks in order:

    | # | Subject | Description |
    |---|---------|-------------|
    | S1 | Build Token Reference Table | Call get_variable_defs and build token lookup table. |
    | S2 | Capture Visual Reference | Call get_screenshot for layout reference. |
    | S3 | Fetch Design Context + Cross-Reference | Call get_design_context and cross-reference tokens. |
    | S4 | Implement All Variants | Build the component code from Figma data. |
    | S5 | Generate Storybook Story | Create story file if requested, otherwise skip. |
    | S6 | Self-Review: Compare Against Figma | Re-fetch screenshot + variable_defs and compare against implementation. |
    | S7 | Fix Detected Discrepancies | Fix any issues found in S6 using in-memory Figma data. |

    After creating all 7 tasks, set up dependencies using TaskUpdate `addBlockedBy`:
    - S2 blocked by S1
    - S3 blocked by S2
    - S4 blocked by S3
    - S5 blocked by S4
    - S6 blocked by S5
    - S7 blocked by S6

    **Task execution protocol:** For every task:
    1. Mark it `in_progress` with TaskUpdate before starting
    2. Do the work described in the task
    3. Mark it `completed` with TaskUpdate when done
    4. Do NOT proceed to the next task until the current one is completed

    ### Step 1 — Build Token Reference Table

    Mark S1 `in_progress`.

    Call `get_variable_defs(fileKey, nodeId)` using file key `[FILE_KEY]` and node ID `[NODE_ID]`.

    Build a lookup table mapping token name → resolved value for:
    - Colors (fill, stroke, background, text)
    - Typography (font family, size, weight, line height)
    - Spacing (padding, margin, gap)
    - Border radius, shadows, opacity

    This table is the single source of truth for all design values. Keep it accessible — you will cross-reference it in Step 3.

    Mark S1 `completed`.

    ### Step 2 — Capture Visual Reference

    Mark S2 `in_progress`.

    Call `get_screenshot(fileKey, nodeId)` using file key `[FILE_KEY]` and node ID `[NODE_ID]`.

    The screenshot is the source of truth for layout: arrangement, sizing, spacing, and overall visual structure. Keep it accessible for comparison throughout implementation. You will validate your final output against this screenshot before reporting back.

    Mark S2 `completed`.

    ### Step 3 — Fetch Design Context + Cross-Reference

    Mark S3 `in_progress`.

    Call `get_design_context(fileKey, nodeId)` using file key `[FILE_KEY]` and node ID `[NODE_ID]`.

    This provides:
    - Component hierarchy and children ordering
    - Auto-layout direction and mode (row/column, wrap)
    - Constraints and sizing modes (fixed/hug/fill)
    - Variants and interactive states (hover, active, disabled, focus)
    - Component props and slot/composition patterns
    - Implementation suggestions with token names

    **Cross-reference every token name** from this output against the lookup table from Step 1.

    **Token Mapping Rule — apply for every visual property:**
    1. **Name match + value match:** Figma variable name matches a project token by name AND their resolved values are identical → use the project token.
    2. **Name match + value mismatch:** Figma variable name matches a project token by name BUT the values differ → hardcode the Figma value.
    3. **No match:** No project token matches the Figma variable name → hardcode the Figma value.

    Never approximate. Never use a "closest" project token. It is either an exact match (name + value) or a hardcoded Figma value.

    **Fallback:** If `get_variable_defs` returned no tokens for a node, use the raw resolved values from `get_design_context` and proceed — token mapping fallbacks are expected behavior.

    **Truncation fallback:** If `get_design_context` returns a truncated response (indicated by missing expected child nodes or incomplete data), call `get_metadata` on the child nodes that need more detail. This is the only case where additional MCP calls are made beyond the mandatory ones.

    Mark S3 `completed`.

    ### Step 4 — Implement All Variants

    Mark S4 `in_progress`.

    #### Figma Variants vs. CSS States

    Figma represents interaction states (hover, pressed, focused, disabled) as discrete variants alongside semantic variants (kind, size, type). Distinguish between the two:

    - **Interaction states** → CSS pseudo-classes (`:hover`, `:active`, `:focus-visible`, `:disabled`). Never expose as props.
    - **Semantic variants** → Component props (kind, variant, size). These represent meaningful visual differences the consumer controls.

    Rule of thumb: if the state is triggered by user interaction with the element itself, it's CSS. If it's set by the parent/consumer to convey meaning, it's a prop.

    #### Prop Orthogonality

    Each Figma variant axis maps to an independent prop. Never derive one prop's behavior from another unless Figma explicitly constrains that combination (e.g., a variant that only exists under a specific parent state).

    Verify: can every valid combination of prop values render a meaningful result? If your implementation forces prop A when prop B is set, you've reduced the component's composability beyond what the design requires.

    **Component file naming:** Convert the Figma component name `[COMPONENT_NAME]` to project conventions based on `[FRAMEWORK]`:
    - React / Next.js → PascalCase (e.g., `ButtonPrimary.tsx`)
    - Vue → kebab-case (e.g., `button-primary.vue`)
    - Svelte → PascalCase (e.g., `ButtonPrimary.svelte`)
    - Angular → kebab-case (e.g., `button-primary.component.ts`)
    - Other → follow the dominant naming convention found in the project

    **Output files to `[OUTPUT_DIRECTORY]`.** Create subdirectories if the component needs multiple files (e.g., component + styles + types).

    **If `[NODE_TYPE]` is COMPONENT_SET:**

    1. Implement the **base variant** first — pick the default or most common variant as the foundation.
    2. Extend for each additional variant listed in `[VARIANT_LIST]`. Ensure every variant is covered.
    3. For TypeScript/React projects, derive prop types from variant properties:
       ```typescript
       // Example: if variants are Primary, Secondary, Ghost
       type ButtonVariant = 'primary' | 'secondary' | 'ghost';

       interface ButtonProps {
         variant?: ButtonVariant;
         // ... other props from Figma component properties
       }
       ```
    4. For other frameworks, use the idiomatic variant pattern:
       - Vue: props with validator (`validator: (value) => ['primary', 'secondary', 'ghost'].includes(value)`)
       - Svelte: exported props (`export let variant: 'primary' | 'secondary' | 'ghost' = 'primary'`)
       - Angular: `@Input()` with union type
    5. Each variant's visual properties must come from Figma (via the Token Mapping Rule). Do not invent variant styles.

    **If `[NODE_TYPE]` is COMPONENT (single, no variants):**

    Implement the component directly. No variant abstraction needed.

    Mark S4 `completed`.

    ### Step 5 — Generate Storybook Story (if requested)

    Mark S5 `in_progress`.

    **If `[GENERATE_STORYBOOK]` is "no":** Mark S5 `completed` with note "Skipped — not requested." and proceed to Step 6.

    **If `[GENERATE_STORYBOOK]` is "yes":**

    1. Create a `*.stories.*` file alongside the component in `[OUTPUT_DIRECTORY]`.
    2. Check the project for existing story patterns:
       - Look for CSF3 format (`export const Primary: Story = { ... }`)
       - Check for controls/args patterns
       - Match the file extension convention (`.stories.tsx`, `.stories.ts`, `.stories.js`, etc.)
    3. Include a story for each variant showing all states:
       - If COMPONENT_SET: one story per variant, plus a story showing all variants together
       - If single COMPONENT: a default story plus stories for any interactive states (hover, disabled, etc.) visible in Figma
    4. Follow existing story patterns found in the project. If no existing stories are found, use CSF3 format with controls.

    Mark S5 `completed`.

    ### Step 6 — Self-Review: Compare Against Figma

    Mark S6 `in_progress`.

    Re-fetch design data to compare against your implementation:

    1. Call `get_screenshot(fileKey, nodeId)` using file key `[FILE_KEY]` and node ID `[NODE_ID]` — fresh visual reference.
    2. Call `get_variable_defs(fileKey, nodeId)` using file key `[FILE_KEY]` and node ID `[NODE_ID]` — fresh token data.

    Walk through each category below. For each, record **PASS** or **ISSUE** with a specific description:

    **A. Layout Structure**
    Compare the screenshot against the component you built. Check:
    - Top-level layout direction (row/column) matches
    - Child elements are in the correct order
    - Sizing modes are correct (fixed/hug/fill mapped to appropriate CSS: fixed width, fit-content, flex-grow)
    - Spacing between elements matches Figma values

    **B. Token Coverage**
    Walk through every token from the fresh `get_variable_defs` output:
    - Is each token either used via a project token (exact name + value match) or hardcoded per the Token Mapping Rule?
    - Are there any CSS properties in the code using values that don't match any Figma token or resolved value (phantom values)?

    **C. Variant Completeness** (COMPONENT_SET only)
    - Is every variant in `[VARIANT_LIST]` implemented?
    - Are interaction states (hover, active, disabled, focus) CSS pseudo-classes, not component props?
    - Are semantic variants exposed as component props?

    **D. Asset Integrity**
    - Were all Figma icons/images downloaded or correctly deduped against existing codebase assets?
    - Do SVG viewBoxes use the container size, not the path's tight bounding box?

    **E. Accessibility**
    - Semantic HTML elements used where appropriate (`button`, `nav`, `main` — not generic `div`)?
    - `aria-label` on icon-only actions?
    - Focus states present for interactive elements?

    **If all checks PASS:** Mark S6 `completed` with note "All checks passed." Skip S7 — mark it `completed` with note "Skipped — no issues found."

    **If any ISSUE is found:** Mark S6 `completed` with the full issue list. Proceed to Step 7.

    ### Step 7 — Fix Detected Discrepancies

    Mark S7 `in_progress`. **Only execute this step if Step 6 found issues.**

    For each issue from Step 6:
    1. Locate the relevant code in the files you created.
    2. Apply the fix using the Figma data already in memory from Step 6. **Do NOT make additional MCP calls.**
    3. Note what was fixed and how.

    If an issue cannot be fixed (ambiguous design data, missing assets, fundamental structural mismatch), note it as **unresolved** — do not attempt workarounds.

    Mark S7 `completed` with a summary of fixes applied and any unresolved issues.

    ## Asset Rules

    1. **Always use Figma assets.** Icons, images, and SVGs come from the Figma MCP server.
    2. **Dedup check.** Before downloading an asset, search the codebase for an existing exact match. If found, use the existing file. If not, download from Figma.
    3. **Never substitute with icon libraries** (lucide, heroicons, etc.). Never create placeholder assets.
    4. **Icons as SVG.** Icons must be saved as `.svg` files, not raster formats. Photos and illustrations may be raster.
    5. **Use asset URLs as-is** from the MCP server. Do not modify, proxy, or reconstruct them.
    6. **SVG icon extraction.** Figma icon components have a bounding container (e.g., 20×20) and an inner shape with insets. When converting to SVG:
       - Set the `viewBox` to the **container size** (e.g., `"0 0 20 20"`), not the path's tight bounding box.
       - Translate path data to match Figma's inset positioning within that container.
       - Verify by rendering: the icon should have the same visual weight and whitespace as the Figma screenshot. If it fills the entire container edge-to-edge, the viewBox is wrong.

    ## Implementation Rules

    1. **Figma overrides codebase patterns.** When the Figma design differs from project conventions, follow Figma.
    2. **Reuse existing components when they match.** If a project component matches what Figma shows, use it. If Figma shows something different, implement what Figma shows.
    3. **Token mapping is strict.** Exact name + exact value = project token. Anything else = hardcode the Figma value.
    4. **Accessibility is the one exception.** Semantic HTML, `aria-label` on icon-only actions, focus states, and keyboard navigation must be added even when Figma does not specify them. Report any accessibility additions in your report.
    5. **No other additions beyond Figma.** Do not add features, refactoring, or architectural changes that Figma does not call for.
    6. **Output location.** Output files to the directory specified in context. Create subdirectories if the component needs multiple files (e.g., component + styles + types).

    ## Code Quality

    1. **TypeScript types for component props.** Define explicit prop types for every component. Derive variant types from Figma states (e.g., `type ButtonVariant = 'primary' | 'secondary'`).
    2. **Composable components.** Keep components small and composable — one Figma component = one React component. Use children/slots for content areas Figma marks as variable.
    3. **No inline styles unless dynamic.** Use CSS modules, styled-components, or the project's styling approach. Inline styles are acceptable only for values computed at runtime.
    4. **Accessible by default.** Use semantic HTML elements (`button`, `nav`, `main`, not generic `div`). Add `aria-label` when Figma shows icon-only actions. Ensure focus states and keyboard navigation for interactive elements.
    5. **Responsive behavior from Figma constraints.** Translate Figma auto-layout modes (fill, hug, fixed) into the equivalent CSS (flex-grow, fit-content, fixed width). If Figma shows responsive variants, implement them with appropriate breakpoints.

    ## Best Practices

    ### Validate Incrementally
    Compare against the Figma screenshot at each major structural milestone (layout skeleton, then sections, then details) — not only at the end. This catches drift early.

    ### Document Deviations
    If you must deviate from Figma for technical or accessibility reasons, add a brief code comment explaining why. Report these deviations in your report.

    ### Asset Dedup Before Download
    Always search the codebase for an existing exact match before downloading a new asset. Duplicate assets bloat the project and cause maintenance issues.

    ### Edge-Aligned Overlays
    When an absolutely-positioned child sits at the edge of a bordered parent (badges, tags, indicators), offset it by the negative border width of the parent (e.g., `top: -1px; left: -1px` for a 1px border). This ensures the overlay aligns flush with the parent's outer edge rather than sitting inside the border, which creates a visible gap. Always cross-reference the Figma screenshot for flush alignment at corners and edges.

    ## Reporting

    When done, report:
    - **Status:** DONE | BLOCKED
    - **What was implemented** — component structure and key decisions
    - **Visual validation** — does it match the screenshot from Step 2?
    - **Files created**
    - **Variant coverage** — which variants were implemented (for COMPONENT_SET)
    - **Self-review result** — all checks passed / N issues found, M fixed, K unresolved
    - **MCP calls made** — total count (typically 5; higher if get_metadata fallbacks were needed)

    **Status guidance:**
    - **DONE** — implementation is complete. Token mapping fallbacks, accessibility additions, and self-review fixes are expected behavior and do not downgrade the status. If self-review found issues that were all fixed in Step 7, status is still DONE.
    - **DONE with unresolved issues** — implementation is complete but self-review found issues that could not be fixed. List the unresolved issues. The orchestrator will relay them to the user.
    - **BLOCKED** — cannot proceed (e.g., Figma MCP unavailable, missing assets, MCP failures, ambiguous design structure, or self-review reveals fundamental structural mismatches that require redesign).

    Never silently produce work you are uncertain about.

    ## Escalation

    When stuck, report **BLOCKED**. Include:
    - What you tried
    - What specifically is blocking you
    - What help you need

    It is always OK to stop and escalate. Bad work is worse than no work.
```
