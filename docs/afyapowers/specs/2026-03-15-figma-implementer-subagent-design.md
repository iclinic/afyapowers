# Figma Implementer Subagent Design

## Problem

The current Figma-to-implementation pipeline produces ~50% visual fidelity. The problems are:

1. **Poor initial implementation** — the generic implementer doesn't extract or apply Figma design data effectively
2. **Broken fix loop** — the verification→fix cycle doesn't converge on correct output
3. **No working visual fidelity review** — the review stage is specced but not functioning correctly
4. **Context bloat** — Figma MCP tools return large token payloads that pollute the implementer's context alongside unrelated task data

## Approach

Create a dedicated Figma implementer subagent that SDD dispatches instead of the generic implementer for tasks with `**Figma:**` references. This subagent owns the full implement→preview→screenshot→compare→fix loop internally. The visual fidelity reviewer is enhanced with a two-pass comparison (visual + structured). The SDD orchestrator gains task routing logic to select the right implementer.

## Architecture

### New: Figma Implementer Subagent (`figma-implementer-prompt.md`)

A specialized subagent prompt that replaces the generic implementer for Figma tasks. Key differences from the generic implementer:

#### 1. Figma Context Extraction Upfront

Before writing any code, the agent calls all 4 Figma MCP tools and produces a compact **design spec summary**:

Do NOT hardcode Figma MCP tool names — discover available tools at runtime. Look for tools that match these capabilities:

1. **Screenshot tool** — visual capture of the target design (look at it first, build mental model)
2. **Design context tool** — framework-specific styling info (detect project stack from `package.json` and config files first)
3. **Metadata tool** — structural hierarchy (layer IDs, types, positions, sizes, nesting)
4. **Variables/tokens tool** — design system variables (colors, spacing, typography tokens)

From the raw MCP output, extract a compact summary in structured key-value format:

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

This summary becomes the agent's working reference — not the raw MCP output. Fetch the Figma screenshot once and reuse it across all self-correction iterations (do not re-fetch).

#### 2. Always Create Temporary Preview Route

No Storybook path. Every Figma task gets a `/dev/preview/ComponentName` route (adapted to the project's routing framework, e.g., `src/app/dev/preview/ComponentName/page.tsx` for Next.js).

For full-page tasks that already have a route, the agent still creates a preview route with mock data if the actual page requires auth or complex data that isn't available in dev.

Preview requirements:
- Render the component with representative props/data that exercise the visual states shown in Figma
- If Figma shows multiple states (hover, disabled, error), render all states vertically on the same preview page
- Keep the preview minimal — no extra layout, navigation, or decoration

#### 3. Internal Self-Correction Loop (Up to 5 Iterations)

After initial implementation, the agent runs a tight feedback loop. Do NOT hardcode Playwright MCP tool names — discover available tools at runtime.

1. **Wait for compilation** — After modifying code, wait for the dev server to finish recompilation (check for build errors). If the preview shows a build error, fix the code error first — this does not count as a self-correction iteration. If the dev server becomes unreachable, attempt to restart it once before reporting BLOCKED.
2. **Navigate** — Use a Playwright navigation tool to open the preview route
3. **Screenshot** — Use a Playwright screenshot tool to capture the implementation
4. **Visual compare** — Look at both images (Figma screenshot vs implementation screenshot), identify obvious issues (missing elements, wrong layout, clearly wrong colors)
5. **Structured compare** — Use a Playwright evaluate tool with `getComputedStyle` to extract actual CSS values from key elements. Use a Playwright snapshot tool first to identify the DOM structure, then target elements by role, text content, or CSS selectors. Compare against the design spec summary using these tolerances:
   - Colors: match after normalizing both sides to hex (note: `getComputedStyle` returns `rgb()` format — convert to hex before comparing)
   - Spacing/dimensions: within 4px tolerance
   - Typography: exact font-family, size within 2px, exact weight
   - Border radius: within 2px
6. **Fix** — If discrepancies found, fix the code and repeat from step 1
7. **Exit** — If no discrepancies or 5 iterations reached, report back to SDD

The agent tracks what it fixed each iteration to avoid thrashing (fixing the same thing back and forth).

**On re-dispatch** (when SDD sends back with a discrepancy report from the visual fidelity reviewer): run only 2 internal self-correction iterations instead of 5, since the fix instructions are targeted and specific.

#### 4. No TDD for Figma Tasks

The generic implementer enforces strict TDD (red-green-refactor). The figma implementer skips TDD and focuses on visual accuracy. The self-correction loop with Playwright serves as the verification mechanism instead.

If the task has functional/behavioral requirements beyond styling (e.g., form validation, click handlers, data fetching), write tests after implementation to verify them. The red-green-refactor cycle is not required for Figma tasks.

#### 5. Report Format

Same as generic implementer with additions:
- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **Figma Status:** accessed successfully | partial access | unable to access Figma MCP
- **Preview URL:** e.g., `http://localhost:3000/dev/preview/LoginForm`
- **Preview File:** e.g., `src/app/dev/preview/LoginForm/page.tsx`
- **Self-Correction Iterations:** N/5 (how many loops were needed)
- **Remaining Discrepancies:** (if any after 5 iterations)

### Modified: Visual Fidelity Reviewer

The existing `visual-fidelity-reviewer-prompt.md` is enhanced with a two-pass comparison approach.

#### Two-Pass Comparison

**Pass 1 — Visual Judgment:**
Look at both screenshots (Figma vs implementation). Identify obvious issues:
- Missing or extra elements
- Wrong layout direction or structure
- Clearly wrong colors
- Missing component states (hover, disabled, error)
- Wrong proportions or visual character

**Pass 2 — Structured Comparison:**
Use Playwright tools to extract computed styles from the implementation (do NOT hardcode tool names — discover at runtime). Use a Playwright snapshot tool first to identify DOM structure, then use an evaluate tool with `getComputedStyle` on targeted elements. Convert `rgb()` values from `getComputedStyle` to hex before comparing. Use Figma MCP tools to get expected values. Compare numerically:
- Colors: exact hex match (tolerate color space conversion differences)
- Spacing: within 4px tolerance
- Typography: exact font-family, size within 2px, exact weight
- Dimensions: within 4px tolerance
- Border radius: within 2px

#### Output Format

On **PASS**: `✅ Visual fidelity passed` (same as today). SDD cleans up preview files.

On **FAIL**: structured discrepancy report with precise values:
```
❌ Visual fidelity failed

Discrepancy 1: Background color on hero section
- Element: .hero-banner
- Aspect: color
- Expected (Figma): #1A2B3C
- Actual (Implementation): #2C3D4E
- Fix required: Update background color in hero-banner component

Discrepancy 2: Spacing between card grid items
- Element: .card-grid
- Aspect: spacing
- Expected (Figma): gap 24px
- Actual (Implementation): gap 16px
- Fix required: Update grid gap value
```

#### Tolerance Thresholds

**Report as discrepancy (FAIL):**
- Wrong layout structure (missing elements, wrong nesting, wrong flex/grid direction)
- Visibly wrong colors (not sub-shade rendering differences)
- Wrong typography (wrong font family, significantly wrong size/weight)
- Spacing off by more than ~4px or visually noticeable
- Missing component states when specified in Figma
- Wrong proportions or sizing that changes visual character

**Tolerate (PASS):**
- Sub-pixel rounding (1-2px)
- Font rendering differences between Figma and browser
- Color space conversion differences (sRGB vs display-P3)
- Anti-aliasing differences
- Shadow/blur rendering differences between Figma and CSS

### Modified: SDD Orchestrator

#### Task Routing

When dispatching a task, SDD checks for `**Figma:**` section:
- **Has Figma refs** → dispatch using `figma-implementer-prompt.md`
- **No Figma refs** → dispatch using `implementer-prompt.md` (unchanged)

#### Review Pipeline for Figma Tasks (2 stages)

1. **Stage 1: Spec compliance** — unchanged, verifies the implementation meets the task's functional requirements
2. **Stage 2: Visual fidelity review** — replaces code quality as the gating review for Figma tasks

Rationale: the figma-implementer already does 5 internal self-correction passes with structured CSS comparison. A separate code quality review on styling code adds little value and slows the pipeline. The visual fidelity reviewer catches what matters.

For non-Figma tasks, the review pipeline remains unchanged (spec compliance → code quality).

#### Re-dispatch on Visual Fidelity Failure

When the visual fidelity reviewer reports FAIL:
1. SDD re-dispatches the figma-implementer with the full discrepancy report
2. The re-dispatched agent fixes only what's listed in the discrepancy report
3. After fix, SDD runs visual fidelity review again (skip spec compliance — already passed)
4. Repeat until pass or iteration cap reached

#### Iteration Cap: 5 Total Visual Fidelity Review Cycles

SDD tracks visual fidelity review cycles per task. A cycle = one visual fidelity review dispatch. After 5 total cycles (the initial review counts as cycle 1, each re-review after a fix counts as another), escalate:

> "Task N has failed visual fidelity review 5 times. Remaining issues: [list]. Please review and provide guidance."

#### Preview Cleanup

Same as today: SDD deletes preview files after visual fidelity passes. Re-dispatched agents reuse the same preview route.

### Modified: Generic Implementer

Remove from `implementer-prompt.md`:
- The `## Figma References` section (tool sequence, graceful degradation, Figma status reporting)
- The `## Visual Fidelity Re-Dispatch` section
- The `## Component Preview` section (Storybook detection, preview route creation)

These responsibilities now live exclusively in `figma-implementer-prompt.md`. The generic implementer handles only non-Figma tasks.

## Data Flow

```
SDD receives task with **Figma:** references
  │
  ├─ Dispatch figma-implementer subagent
  │    │
  │    ├─ Fetch Figma context (screenshot, design context, metadata, tokens)
  │    ├─ Extract compact design spec summary
  │    ├─ Implement component
  │    ├─ Create temp preview route
  │    └─ Self-correction loop (up to 5x):
  │         ├─ Navigate to preview (Playwright)
  │         ├─ Take screenshot (Playwright)
  │         ├─ Visual compare (Figma screenshot vs implementation)
  │         ├─ Structured compare (getComputedStyle vs design spec)
  │         └─ Fix discrepancies
  │
  ├─ Spec compliance review (stage 1)
  │    └─ Pass/fail on functional requirements
  │
  ├─ Visual fidelity review (stage 2)
  │    ├─ Pass 1: Visual judgment (both screenshots)
  │    ├─ Pass 2: Structured comparison (computed CSS vs Figma values)
  │    └─ Output: PASS or FAIL with discrepancy report
  │
  ├─ If FAIL: re-dispatch figma-implementer with discrepancy report
  │    └─ Repeat visual fidelity review (up to 5 total cycles)
  │
  └─ If PASS: clean up preview files, mark task completed
```

## File Changes

### New:
- `skills/implementing/figma-implementer-prompt.md` — follows the same prompt template structure as `implementer-prompt.md` (Task tool general-purpose format)

### Modified:
- `skills/implementing/visual-fidelity-reviewer-prompt.md` — two-pass comparison, structured output
- `skills/subagent-driven-development/SKILL.md`:
  - Add task routing logic (Figma vs non-Figma implementer dispatch)
  - Add `figma-implementer-prompt.md` to the Prompt Templates section
  - Update the process digraph to show the routing branch
  - Update "Visual Fidelity Review (Third Stage)" section to reflect 2-stage pipeline for Figma tasks
  - Update Red Flags: the rule "Start visual fidelity review before code quality passes" does not apply to Figma tasks (code quality is skipped)
  - Update iteration cap from 3 to 5
  - Remove Storybook references from preview cleanup
- `skills/implementing/implementer-prompt.md` — remove Figma References, Visual Fidelity Re-Dispatch, and Component Preview sections
