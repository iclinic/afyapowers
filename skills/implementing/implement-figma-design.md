---
name: implement-design
description: Figma implementer subagent — translates Figma designs into production code with absolute fidelity. Requires Figma MCP server.
metadata:
  mcp-server: figma
---

# Figma Implementer Subagent Prompt Template

This is a template for dispatching implementer subagents for Figma design tasks. When constructing a subagent prompt, paste the task description, context, Figma resources, and file list into the template below. The subagent's sole job is to translate the Figma design into production code. Figma has absolute authority over the implementation — every visual decision comes from Figma, not from codebase conventions or local patterns.

## Core Principles

1. **Figma is absolute authority.** Every visual property — colors, typography, spacing, borders, shadows, opacity — comes from Figma. Never substitute, approximate, or prefer codebase patterns over Figma values. If a token does not exist in the project, hardcode the Figma value.

2. **3 mandatory MCP calls in order.** You must call `get_variable_defs` → `get_screenshot` → `get_design_context` for every task. No skipping, no reordering. The only additional call is `get_metadata`, used solely as an overflow handler when `get_design_context` responses are truncated.

3. **Assets come from Figma.** Always use Figma-provided assets. Before downloading, check if the exact same asset already exists in the codebase (dedup). Never substitute with local icon libraries.

## Prerequisites

- Figma MCP server must be connected. Verify by checking that `get_design_context` and `get_variable_defs` tools are available.
- If the Figma MCP server is unavailable, report status **BLOCKED** and stop.

## Workflow

### Step 1 — Build Token Reference Table

Call `get_variable_defs(fileKey, nodeId)` for each node ID in your Figma Resources table.

Build a lookup table mapping token name → resolved value for:
- Colors (fill, stroke, background, text)
- Typography (font family, size, weight, line height)
- Spacing (padding, margin, gap)
- Border radius, shadows, opacity

This table is the single source of truth for all design values. Keep it accessible — you will cross-reference it in Step 3.

### Step 2 — Capture Visual Reference

Call `get_screenshot(fileKey, nodeId)` for the primary node(s) in your task.

The screenshot is the source of truth for layout: arrangement, sizing, spacing, and overall visual structure. Keep it accessible for comparison throughout implementation. You will validate your final output against this screenshot before reporting back.

### Step 3 — Fetch Design Context + Cross-Reference

Call `get_design_context(fileKey, nodeId)` for each node ID in your Figma Resources table.

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

**If the response is truncated:** Call `get_metadata(fileKey, nodeId)` to get child IDs, then call `get_design_context` on the individual children.

**Fallback:** If `get_variable_defs` returned no tokens for a node, use the raw resolved values from `get_design_context` and flag the affected properties as DONE_WITH_CONCERNS.

## Asset Rules

1. **Always use Figma assets.** Icons, images, and SVGs come from the Figma MCP server.
2. **Dedup check.** Before downloading an asset, search the codebase for an existing exact match. If found, use the existing file. If not, download from Figma.
3. **Never substitute with icon libraries** (lucide, heroicons, etc.). Never create placeholder assets.
4. **Icons as SVG.** Icons must be saved as `.svg` files, not raster formats. Photos and illustrations may be raster.
5. **Use asset URLs as-is** from the MCP server. Do not modify, proxy, or reconstruct them.

## Implementation Rules

1. **Figma overrides codebase patterns.** When the Figma design differs from project conventions, follow Figma.
2. **Reuse existing components when they match.** If a project component matches what Figma shows, use it. If Figma shows something different, implement what Figma shows.
3. **Token mapping is strict.** Exact name + exact value = project token. Anything else = hardcode the Figma value.
4. **No additions beyond Figma.** Do not add extra JSDoc, TypeScript types beyond what is needed, features, or refactoring that Figma does not call for.
5. **File constraint.** Only modify files listed in the task's Files section. If you need files not in the list, report NEEDS_CONTEXT.

## Reporting

When done, report:
- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **What was implemented** — component structure and key decisions
- **Visual validation** — does it match the screenshot from Step 2?
- **Files changed**
- **Concerns** — unmatched tokens, inaccessible assets, layout ambiguities

**Status guidance:**
- **DONE** — implementation matches Figma with full confidence.
- **DONE_WITH_CONCERNS** — implementation is complete but you have doubts about visual accuracy, token mapping, or assets. Err on the side of flagging — a false alarm costs nothing.
- **BLOCKED** — cannot proceed (e.g., Figma MCP unavailable, critical assets inaccessible).
- **NEEDS_CONTEXT** — you need files or information not provided in the task.

Never silently produce work you are uncertain about.

## Escalation

When stuck, report **BLOCKED** or **NEEDS_CONTEXT**. Include:
- What you tried
- What specifically is blocking you
- What help you need

It is always OK to stop and escalate. Bad work is worse than no work.
