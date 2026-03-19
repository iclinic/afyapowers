# Figma Workflow Rewrite: Simplified Pipeline with Absolute Authority

## Problem

The current Figma implementation workflow has three interconnected failures:

1. **Figma authority not enforced** — tokens are ignored in favor of project defaults, Figma assets are substituted with local icon libraries, and layouts are disrespected. The design should have 100% authority over the implementation.
2. **Subagent prompt too complex** — at ~300 lines with accumulated patches, agents skip steps or get confused. The workflow needs to be short, clear, and non-negotiable.
3. **Plan-level duplication** — plan tasks duplicate the implementation steps that the subagent prompt already defines, creating confusion about which instructions to follow.
4. **Discovery too shallow** — `figma-discovery` produces screen-level task breakdowns instead of component-level, because `get_metadata` is not recursed deep enough into the node hierarchy.

## Solution

Three targeted changes:

### 1. Rewrite `skills/implementing/implement-figma-design.md`

Replace the entire file with a clean, ~100-120 line subagent prompt built on three non-negotiable principles and a strict 3-step MCP workflow.

#### Core Principles

1. **Figma is absolute authority** — every visual property (color, spacing, typography, layout, assets) comes from Figma. Never substitute, approximate, or prefer codebase patterns over what Figma says. If a token doesn't exist in the project, hardcode the Figma value.
2. **3 MCP calls in strict order** — `get_variable_defs` -> `get_screenshot` -> `get_design_context`. No skipping, no reordering.
3. **Assets come from Figma** — always use Figma-provided assets. Check if the exact same asset already exists in the codebase before downloading. Never substitute with a local icon library or package.

#### 3-Step MCP Workflow

**Step 1: Build Token Reference Table**
- Call `get_variable_defs` for each node ID in the task's Figma block
- Build a lookup table: token name -> resolved value (colors, typography, spacing, borders, shadows, opacity)
- This table is the single source of truth for all design values

**Step 2: Capture Visual Reference**
- Call `get_screenshot` for the primary node(s)
- Source of truth for layout — how things are arranged, sized, and spaced visually
- Keep accessible throughout implementation for comparison

**Step 3: Fetch Design Context + Cross-Reference**
- Call `get_design_context` for each node ID
- Provides: component hierarchy, auto-layout, sizing modes, variants, interactive states, implementation suggestions
- Cross-reference every token name from the suggestions against the Step 1 table
- Token Mapping Rule:
  - Name match + value match -> use project token
  - Name match + value mismatch -> hardcode Figma value
  - No match -> hardcode Figma value
- If response is truncated: use `get_metadata` to get child node IDs, then call `get_design_context` on children individually (only case where `get_metadata` is used in the subagent)
- Fallback: if `get_variable_defs` returns no tokens for a node, use raw values from `get_design_context` and flag as DONE_WITH_CONCERNS

#### Asset Handling Rules

1. Always use Figma assets — icons, images, SVGs from the MCP server
2. Dedup check before downloading — search codebase for an existing exact match. If found, use the existing file. If not, download from Figma.
3. Never substitute — never import icon libraries (lucide, heroicons, etc.) as replacements. Never create placeholders.
4. SVG for icons — icons saved as `.svg`, not raster formats. Photos/illustrations can be raster.
5. Use URLs as-is — asset URLs from MCP server used directly without modification

#### Implementation Rules

1. **Figma overrides codebase patterns** — if Figma specifies a layout, color, spacing, or structure that differs from codebase conventions, follow Figma.
2. **Reuse existing components when they match** — if the project has a matching component, use it. But if Figma shows something different, implement what Figma shows (extend or create new).
3. **Token mapping is strict** — exact name + exact value = project token. Anything else = hardcode Figma value. No "close enough".
4. **No additions beyond Figma** — don't add JSDoc, extra types, extra features, or refactoring that Figma didn't ask for.
5. **File constraint** — only modify files listed in the task's Files section. Need another file? Report NEEDS_CONTEXT.

#### Reporting

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What was implemented
- Visual validation result (does it match the screenshot?)
- Files changed
- Any concerns (tokens without matches, inaccessible assets, layout ambiguities)

### 2. Trim Plan Template and Writing-Plans Skill

**`templates/plan.md`** — replace the 7 duplicated Figma steps with a single step:

```markdown
### Task N: [UI Component Name] (Figma)

**Files:**
- Create: `exact/path/to/component`

**Depends on:** none | Task X

**Figma:**
- **File Key:** `<file_key>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Nodes:**
  | Node ID | Name | Type | Parent |
  |---------|------|------|--------|
  | `<id>` | <name> | <type> | <parent> |

- [ ] Implement using the Figma implementer workflow and commit
```

**`skills/writing-plans/SKILL.md`** — replace the Figma steps list (lines 112-118) with: "For Figma tasks, a single step: 'Implement using the Figma implementer workflow and commit'. The subagent prompt owns the how."

The plan says **what** (which component, which nodes, which files). The subagent prompt owns **how** (MCP calls, token mapping, asset handling).

### 3. Fix Discovery Depth in `skills/figma-discovery/SKILL.md`

**Problem:** Phase 2 subagents run `get_metadata` once on their assigned region and only see first-level children. A screen with a "Hero Section" containing "Title", "Subtitle", "CTA Button" only shows the Hero frame, not its internals.

**Fix:** Add explicit recursion to Phase 2, step 1:

1. Run `get_metadata` on the assigned region to get first-level children
2. For each child that is a FRAME with children (not leaf nodes like TEXT or RECTANGLE), run `get_metadata` again to explore deeper
3. Continue until reaching leaf nodes or depth 3-4
4. Apply the heuristic engine to the full tree, not just the top level

This ensures discovery finds components at all levels: "Hero Section" contains "CTA Button" as reusable, "Stats Card" repeated 3x as reusable, etc.

**Strengthen layered task generation** (Step 4 in writing-plans):
- Layer 1: reusable components found at leaf/mid levels (buttons, cards, badges)
- Layer 2: sections that compose those components (hero, sidebar, content area)
- Layer 3: page assembly

## Files Changed

| File | Change |
|------|--------|
| `skills/implementing/implement-figma-design.md` | Full rewrite (~100-120 lines) |
| `templates/plan.md` | Replace 7 Figma steps with single step |
| `skills/writing-plans/SKILL.md` | Replace Figma steps list with single-step guidance |
| `skills/figma-discovery/SKILL.md` | Add recursive depth to Phase 2 metadata exploration |

## Design Principles

1. **Figma is law** — the design has absolute authority over the implementation. No exceptions.
2. **Single ownership** — the plan says what, the subagent prompt says how. No duplication.
3. **Simplicity** — fewer lines = fewer things to skip. The subagent prompt should be short enough that an agent reads and follows every word.
4. **Depth over breadth in discovery** — recurse into the node tree to find components, don't stop at the screen level.
