# Figma Workflow Improvements Design

## Overview

Two improvements to the Figma integration in the afyapowers workflow:

1. **Early Figma Discovery** — Move Figma discovery from late in the Design phase (after design approval) to the very beginning, so discovered layouts inform the entire design conversation.
2. **Visual Fidelity Review** — Add a third review stage in the SDD pipeline that validates implementation accuracy against Figma layouts using Figma MCP + Playwright MCP tools.

## Problem Statement

### Early Discovery

Currently, Figma discovery runs after the design conversation is complete (step 5 of the design checklist). By then, the design has already been shaped without visual context from Figma — the references are just appended to an already-formed spec. This means the design skill may ask questions that Figma layouts already answer, and proposed approaches don't account for actual layout constraints.

### Visual Fidelity

Implementation subagents fetch Figma visual details before coding, but there is no verification that the resulting implementation actually matches the Figma design. Discrepancies in spacing, colors, typography, layout structure, and component states go undetected until manual review.

## Requirements

### Early Discovery
- Figma discovery must run at the beginning of the Design phase, right after context exploration
- Discovered layouts must be available as context throughout the design conversation
- The design skill should naturally skip questions that Figma layouts already answer
- The figma-discovery skill itself does not change — only when it's invoked changes

### Visual Fidelity Review
- Every task with `**Figma:**` references must be visually validated after implementation
- Validation must compare layout, spacing, colors, typography, and component states
- The reviewer must use Figma MCP tools to fetch visual specs and Playwright MCP tools to inspect the running implementation
- If validation fails, the implementer is re-dispatched with a discrepancy report to fix issues
- After 3 failed fix attempts, the task escalates as `BLOCKED`
- If Figma MCP or Playwright MCP tools are unavailable, execution stops and asks the user to install them (with option to continue without validation)
- The orchestrator must detect how to start the dev server and start it automatically before the first wave

## Constraints

- The figma-discovery skill itself remains unchanged
- Visual fidelity review follows the same pattern as existing spec-compliance and code-quality reviews (subagent dispatch + implementer re-dispatch on failure)
- Only tasks with `**Figma:**` references go through visual fidelity review
- MCP tool discovery remains agnostic (no hardcoded tool names)

## Chosen Approach

### Early Discovery
Move the Figma discovery invocation from step 5 (post-design-approval) to step 2 (post-context-exploration) in the design skill's checklist. The discovered layouts become working context for the rest of the design conversation.

### Visual Fidelity Review
Add visual fidelity as a third review stage in the existing SDD two-stage review pipeline (spec compliance → code quality → visual fidelity). This follows the exact same pattern — subagent dispatched for review, implementer re-dispatched on failure. No new orchestration concepts needed.

## Architecture

### Component 1: Early Figma Discovery (Design Skill Update)

The design skill's checklist and digraph are updated to invoke figma-discovery early:

**New flow:**
1. Explore project context
2. **Detect UI/front-end work → invoke figma-discovery skill**
3. Discovered Figma layouts become part of the conversation context
4. Ask clarifying questions (informed by what Figma already shows — skip redundant ones)
5. Propose approaches (informed by actual layout constraints)
6. Present design sections
7. Write spec (Figma references already integrated throughout)
8. Spec review loop
9. User reviews spec

The figma-discovery skill itself is unchanged. The design skill's digraph updates the conditional Figma branch to occur early, with a "Non-UI feature?" bypass that skips straight to clarifying questions.

### Component 2: Pre-Execution Checks (SDD Update)

Before dispatching the first wave, the SDD orchestrator performs these checks if any task in the plan has `**Figma:**` references:

1. **Check Figma MCP tools:** Inspect available MCP tools for Figma-related tools. If unavailable → stop and ask the user: "Figma MCP tools are not available. Visual fidelity validation requires them. Please install a Figma MCP server and return to this conversation. Do you want to continue without visual validation?"

2. **Check Playwright MCP tools:** Same pattern. If unavailable → stop and ask the user to install Playwright MCP tools.

3. **Start dev server:** Inspect the codebase (package.json scripts, framework config) to determine how to start the dev server. Start it in the background and wait for it to be ready (port responding). If the dev server fails to start → stop and ask the user for help.

These checks run once at the start of implementation, not per-task or per-wave.

### Component 3: Visual Fidelity Reviewer (`skills/implementing/visual-fidelity-reviewer-prompt.md`)

A new subagent prompt, structured like `spec-reviewer-prompt.md`. The reviewer:

1. Receives the task's `**Figma:**` references and the list of files changed
2. Uses Figma MCP tools to fetch full visual details for each referenced node:
   - Layout structure and hierarchy
   - Spacing and sizing values
   - Colors (fill, stroke, background)
   - Typography (font family, size, weight, line height)
   - Design tokens if available
3. Uses Playwright MCP tools to inspect the running implementation:
   - Navigates to the relevant page/component
   - Takes screenshots
   - Inspects computed styles, dimensions, spacing
4. Compares implementation against Figma on:
   - Layout structure and hierarchy
   - Spacing and sizing
   - Colors and typography
   - Component states (hover, active, disabled, etc.)
   - Responsive behavior (if specified in Figma)
5. Returns verdict:
   - **✅ Visual fidelity passed** — implementation matches Figma
   - **❌ Visual fidelity failed** — detailed discrepancy report with specific elements, expected vs actual values, and what needs to change

### Component 4: Three-Stage Review Pipeline (SDD Update)

The SDD's per-task review pipeline extends from two stages to three:

```
Implementation complete
  → Stage 1: Spec compliance review
    → If fails: re-dispatch implementer with issues → re-review
  → Stage 2: Code quality review
    → If fails: re-dispatch implementer with issues → re-review
  → Stage 3: Visual fidelity review (only for tasks with **Figma:** references)
    → If fails: re-dispatch implementer with discrepancy report → re-review
    → Cap: 3 fix iterations, then escalate as BLOCKED
  → Task marked done
```

When the visual fidelity review fails, the implementer is re-dispatched with the discrepancy report appended to its context — same pattern as spec-compliance and code-quality failures. The implementer fixes the specific issues and the visual fidelity review runs again.

After 3 failed visual fidelity attempts, the task escalates as `BLOCKED` with accumulated discrepancy reports so the user can intervene.

### Component 5: Dev Server Cleanup (SDD Update)

After the final wave completes, if the orchestrator started a dev server, it kills the process.

### Component 6: Implementer Prompt Update

The implementer prompt is updated to handle visual-fidelity re-dispatch:

> If you are being re-dispatched due to a visual fidelity review failure, you will receive a discrepancy report listing specific elements with expected vs actual values. Fix each listed discrepancy. Do not make unrelated changes.

## Data Flow

```
Design phase
  → Design skill detects UI work
  → Invokes Figma discovery skill (EARLY — step 2)
  → Discovered layouts inform the rest of the design conversation
  → Confirmed nodes written to design.md ## Figma References
                    ↓
Plan phase
  → Planner assigns Figma nodes to tasks via **Figma:** section
                    ↓
Implement phase (pre-execution)
  → SDD checks: Figma MCP available? Playwright MCP available?
  → If unavailable: stop, ask user to install, option to continue without
  → SDD inspects codebase, starts dev server
                    ↓
Implement phase (per-task, within each wave)
  → Subagent implements task (fetches Figma details before coding)
  → Stage 1: Spec compliance review
  → Stage 2: Code quality review
  → Stage 3: Visual fidelity review (Figma MCP + Playwright MCP)
    → Pass: task marked done
    → Fail: implementer re-dispatched with discrepancy report (max 3 iterations)
    → 3 failures: escalate as BLOCKED
                    ↓
Implement phase (post-execution)
  → Dev server killed
```

## Error Handling

| Scenario | Behavior |
|---|---|
| Figma MCP tools not available at implementation start | Stop execution. Ask user to install Figma MCP server. Offer option to continue without visual validation. |
| Playwright MCP tools not available at implementation start | Stop execution. Ask user to install Playwright MCP tools. Offer option to continue without visual validation. |
| Dev server fails to start | Stop execution. Ask user for help starting the dev server. |
| Visual fidelity review fails (iteration 1-3) | Re-dispatch implementer with discrepancy report. Implementer fixes and re-submits for visual review. |
| Visual fidelity review fails (iteration 3+) | Task escalates as `BLOCKED` with accumulated discrepancy reports. User must intervene. |
| Figma MCP call fails during visual review | Review reports the failure. Orchestrator asks user if they want to retry or skip visual validation for this task. |
| Playwright navigation fails | Review reports the failure with details (URL attempted, error). Orchestrator asks user for guidance. |

## Testing Strategy

This feature is entirely prompt/skill-based (no runtime code). Validation is manual:

- Verify Figma discovery runs early in design phase and layouts inform subsequent questions
- Verify pre-execution checks detect MCP tool availability and stop appropriately
- Verify dev server is detected, started, and cleaned up
- Verify visual fidelity reviewer dispatches for tasks with `**Figma:**` references
- Verify implementer re-dispatch on visual fidelity failure with discrepancy report
- Verify 3-iteration cap and escalation to `BLOCKED`
- Verify tasks without `**Figma:**` references skip visual fidelity review entirely

## Changes to Existing Files

### Modified Files

1. **`skills/design/SKILL.md`** — Move Figma discovery invocation from step 5 (post-design-approval) to step 2 (post-context-exploration). Update digraph accordingly.
2. **`skills/subagent-driven-development/SKILL.md`** — Add pre-execution checks (Figma MCP, Playwright MCP, dev server startup). Add visual fidelity review as third review stage. Add 3-iteration cap with escalation. Add dev server cleanup.
3. **`skills/implementing/implementer-prompt.md`** — Add instructions for handling visual-fidelity re-dispatch with discrepancy reports.

### New Files

1. **`skills/implementing/visual-fidelity-reviewer-prompt.md`** — Subagent prompt for the visual fidelity reviewer.

### Unchanged Files

- `skills/figma-discovery/SKILL.md` — No changes needed
- `skills/writing-plans/SKILL.md` — Already handles Figma reference mapping
- `skills/implementing/SKILL.md` — Just an orchestrator, delegates to SDD
- `skills/implementing/spec-reviewer-prompt.md` — No changes
- `skills/implementing/code-quality-reviewer-prompt.md` — No changes

## Design Decisions

1. **Early discovery over late discovery** — Running Figma discovery at the beginning of the design phase means layouts inform the entire design conversation. The skill naturally avoids asking questions that Figma already answers, and approach proposals account for actual layout constraints.
2. **Third review stage over post-wave validation** — Adding visual fidelity as a review stage in the existing pipeline requires no new orchestration concepts. It follows the same subagent dispatch + implementer re-dispatch pattern already used for spec compliance and code quality.
3. **Hard stop on missing MCP tools** — If Figma or Playwright MCP tools are unavailable, execution stops and asks the user to install them rather than silently skipping. Visual fidelity is important enough that skipping should be a conscious user decision.
4. **Orchestrator-managed dev server** — The SDD inspects the codebase and starts the dev server automatically, avoiding manual user steps and framework-specific assumptions in the skill prompts.
5. **3-iteration cap** — Prevents infinite fix loops while giving the implementer enough chances to converge on the correct visual output.
6. **Sequential visual review within waves** — Since reviews already run sequentially per task, only one Playwright instance is active at a time, avoiding concurrency issues with the dev server.

## Open Questions

None — all questions resolved during design discussion.
