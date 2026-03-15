# Figma Workflow V2 Design

## Overview

Four improvements to the Figma integration to fix poor visual fidelity in implementations:

1. **Enhanced Figma Discovery** — Fetch screenshots during discovery so the design conversation has actual visual context.
2. **Smarter Implementer Figma Consumption** — Replace vague "fetch visual specs" with a specific multi-tool sequence using the official Figma MCP server's capabilities.
3. **Component Preview for Visual Fidelity Testing** — Create preview surfaces (Storybook stories or temporary routes) so isolated components can be visually tested.
4. **Relaxed Visual Fidelity Threshold** — Replace pixel-perfect matching with practical fidelity standards that focus on issues a human would flag.

## Problem Statement

### Poor Implementation Fidelity
Implementations using Figma references are often completely different from the Figma layouts. Two root causes:

1. **No visual context during design.** The discovery skill only collects node IDs and names — the agent never sees the actual layouts. The design conversation is "informed by Figma" in name only.
2. **Vague implementer instructions.** The implementer prompt says "fetch layout, component structure, and visual specs" without specifying which tools to use or how to use them. The agent doesn't consistently fetch enough detail.

### Visual Fidelity Review Broken for Components
The visual fidelity reviewer assumes a navigable page/route exists. When implementing isolated components (buttons, cards, form fields), there's no page to navigate to — the component isn't rendered anywhere. The visual fidelity review stage effectively can't run for component-level tasks.

### Overly Strict Fidelity Threshold
The reviewer is told "a 2px spacing difference counts as a discrepancy." This produces noise from rendering differences between Figma and browsers, burning through the 3-iteration cap without meaningful progress.

## Requirements

- Discovery must fetch screenshots for confirmed Figma nodes so the design conversation has visual context
- Implementer must use a specific sequence of Figma MCP tools (`get_screenshot`, `get_design_context`, `get_metadata`, `get_variable_defs`) before writing code
- Implementer must detect the project's frontend stack and pass it to `get_design_context` for framework-specific output
- Component-level tasks must have a preview surface for visual fidelity testing
- Preview detection: use Storybook if available, otherwise create a temporary route
- Temporary preview files must be cleaned up after visual fidelity passes
- Visual fidelity threshold must focus on issues a human reviewer would flag, tolerating minor rendering differences

## Constraints

- Stack detection must be dynamic — no hardcoded framework assumptions (projects vary)
- Figma MCP tool names should still be discovered at runtime (tool-name agnostic), but the instructions should reference the *types* of tools to look for (screenshot, design context, metadata, variables)
- Preview cleanup is the SDD orchestrator's responsibility, not the implementer's
- Page-level tasks that already have routes skip preview creation

## Architecture

### Component 1: Enhanced Figma Discovery

The figma-discovery skill gains a new step between confirmation (Step 4) and output (Step 5):

**Step 4.5: Fetch Screenshots**
- For each confirmed node, call `get_screenshot` via Figma MCP
- Present screenshots inline in the conversation as visual context
- The design skill can now reference actual layouts ("looking at the login form, I see it uses a two-column split")

Screenshots are conversational context only — they are not written to the spec document. The implementer fetches its own screenshots later.

The existing instruction "skip questions that Figma layouts already answer" becomes meaningful because the agent can now see the layouts.

**No change to:** Node discovery flow (Steps 1-4), output format (Step 5 still writes `## Figma References`).

### Component 2: Smarter Implementer Figma Consumption

Replace the vague "fetch visual specs" instruction in the implementer prompt with a specific consumption sequence.

**Before writing any code, for each node URL in `**Figma:**` section:**

1. **`get_screenshot`** — See the target visual. Understand what you're building before reading data.
2. **`get_design_context`** — Detect the project's frontend stack (inspect `package.json`, framework configs) and request output in that format. Fall back to default (React + Tailwind) if stack is ambiguous.
3. **`get_metadata`** — Get structural hierarchy (layer IDs, types, positions, sizes) to understand nesting and layout structure.
4. **`get_variable_defs`** — Fetch design tokens (colors, spacing, typography variables) if available. Use token names in code when they map to the project's existing design system.

**Order matters:** Screenshot first (mental model), then code context, then structure, then tokens. The implementer cross-references all four sources when making implementation decisions.

**Stack detection:** The implementer inspects the project (package.json, framework config files) to determine the stack and passes that context to `get_design_context`. No hardcoded framework.

### Component 3: Component Preview for Visual Fidelity Testing

The implementer creates a preview surface for each component-level task before visual fidelity review runs.

**Detection logic (implementer responsibility):**
1. Check if Storybook exists: look for `.storybook/` directory or `storybook` in `package.json` devDependencies
2. If Storybook → create a story file following the project's existing story conventions
3. If no Storybook → create a temporary preview route (e.g., `/dev/preview/ComponentName`)

**Preview requirements:**
- Render the component with representative props/data that exercise the visual states shown in Figma
- If Figma shows multiple states (hover, disabled, error), render all states vertically on the same preview
- Keep the preview minimal — no extra layout, navigation, or decoration around the component

**Reporting:** The implementer includes the preview URL in its completion report (e.g., `http://localhost:3000/dev/preview/LoginForm` or Storybook URL). The visual fidelity reviewer uses this URL.

**Cleanup:** After visual fidelity passes, the SDD orchestrator deletes the temporary preview file. If using Storybook and the project already has stories as a convention, the story can optionally be kept — the orchestrator asks the user.

**Page-level tasks:** If the task implements a full page that already has a route, no preview is needed — the reviewer navigates to the actual route.

### Component 4: Relaxed Visual Fidelity Threshold

Replace the pixel-perfect standard in the visual fidelity reviewer prompt.

**Report as a discrepancy (fail):**
- Wrong layout structure (missing elements, wrong nesting, wrong flex/grid direction)
- Visibly wrong colors (not sub-shade rendering differences)
- Wrong typography (wrong font family, significantly wrong size/weight)
- Significantly wrong spacing (off by more than ~4px, or visually noticeable gaps)
- Missing component states (hover/disabled/error not implemented when specified in Figma)
- Wrong proportions or sizing that changes the visual character

**Tolerate (pass):**
- Sub-pixel rounding differences (1-2px)
- Minor font rendering differences between Figma and browser
- Slight color variations due to color space conversion (sRGB vs display-P3)
- Anti-aliasing differences
- Differences in shadow/blur rendering between Figma and CSS

**Guiding principle:** "Would a human reviewer flag this in a PR review?" If not, it passes.

## Data Flow

```
Design phase
  → Design skill detects UI work
  → Invokes Figma discovery skill (step 2)
  → User provides URLs, nodes discovered, user confirms
  → NEW: get_screenshot for each confirmed node
  → Screenshots become visual context for design conversation
  → Design shaped with actual visual awareness
  → Confirmed nodes written to spec ## Figma References
                    ↓
Plan phase
  → Planner assigns Figma nodes to tasks via **Figma:** section
                    ↓
Implement phase (pre-execution)
  → SDD checks: Figma MCP available? Playwright MCP available?
  → SDD starts dev server
                    ↓
Implement phase (per-task)
  → Implementer receives task with **Figma:** section
  → NEW: Specific tool sequence:
    1. get_screenshot (see the target)
    2. get_design_context (framework-specific code context)
    3. get_metadata (structural hierarchy)
    4. get_variable_defs (design tokens)
  → Implements matching Figma design
  → NEW: Creates preview surface if component-level task:
    - Storybook story (if Storybook exists)
    - Temporary route (if no Storybook)
  → Reports preview URL in completion report
  → Stage 1: Spec compliance review
  → Stage 2: Code quality review
  → Stage 3: Visual fidelity review (navigates to preview URL or page route)
    → NEW: Practical threshold, not pixel-perfect
    → Pass: task done
    → Fail: re-dispatch with discrepancy report (max 3 iterations)
  → NEW: SDD cleans up temporary preview files after visual fidelity passes
                    ↓
Implement phase (post-execution)
  → Dev server killed
```

## Changes to Existing Files

### Modified Files

1. **`skills/figma-discovery/SKILL.md`** — Add Step 4.5: fetch `get_screenshot` for each confirmed node and present inline as visual context.
2. **`skills/implementing/implementer-prompt.md`** — Replace vague Figma instructions with specific 4-tool consumption sequence. Add stack detection instructions. Add component preview creation instructions (Storybook detection + temp route fallback). Add preview URL to report format.
3. **`skills/implementing/visual-fidelity-reviewer-prompt.md`** — Replace pixel-perfect threshold with practical fidelity standard. Update to use preview URL from implementer report.
4. **`skills/subagent-driven-development/SKILL.md`** — Add preview cleanup step after visual fidelity passes. Pass preview URL from implementer report to visual fidelity reviewer.

### Unchanged Files

- `skills/design/SKILL.md` — No changes needed (already invokes figma-discovery early)
- `skills/writing-plans/SKILL.md` — No changes needed (already handles Figma reference mapping)

## Error Handling

| Scenario | Behavior |
|---|---|
| `get_screenshot` fails during discovery | Warn user, continue without screenshot for that node. Discovery still produces references. |
| `get_design_context` fails during implementation | Implementer proceeds with screenshot + metadata. Reports `Figma Status: partial access` |
| Storybook detected but story creation fails | Fall back to temporary route approach |
| Temporary route creation fails | Implementer reports BLOCKED with details. Orchestrator surfaces to user. |
| Preview URL unreachable by visual fidelity reviewer | Reviewer reports failure. Orchestrator asks user for guidance. |

## Design Decisions

1. **Screenshots during discovery, not just implementation** — The design conversation needs visual context to be actually informed by Figma. Token cost is worth it for better designs.
2. **Specific tool sequence over vague instructions** — Telling the implementer exactly which tools to call and in what order eliminates the inconsistency in Figma data fetching.
3. **Storybook-first, temp route fallback** — Leverage existing infrastructure when available; minimal temporary scaffolding when not.
4. **Practical fidelity over pixel-perfect** — Figma rendering and browser rendering will always differ slightly. Focus reviewer attention on issues that matter.
5. **Preview cleanup by orchestrator** — The implementer shouldn't manage cleanup lifecycle; the SDD orchestrator has the right vantage point to know when visual fidelity passed and cleanup is safe.
6. **Stack detection at implementation time** — Projects vary, so the implementer detects the stack dynamically rather than hardcoding a framework.
