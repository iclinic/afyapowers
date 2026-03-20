# Design: Figma Shallow Node Map & Rate Limit Optimization

## Problem Statement

The Figma workflow generates too many nodes by recursing `get_metadata` to depth 5 during the design phase. This produces inflated Node Maps, creates too many fine-grained tasks, and causes rate limiting issues with the Figma MCP server (15 requests/minute limit). Tasks currently map to deep nodes (layers 3-4) representing internal component parts (icons, labels, containers), when they should map to meaningful units at layer 2 (whole components or sections).

## Requirements

- Design phase must build a complete Node Map with a single `get_metadata` call at depth 2
- Each Figma task must map to exactly one node ID
- Reusable components must still be detected and built first (Layer 1 tasks)
- Concurrency must stay within the 15 req/min rate limit
- The implementer subagent's `get_metadata` fallback (for truncated `get_design_context`) must be preserved

## Constraints

- Figma MCP rate limit: 15 requests/minute (revised down from the previously documented 20 req/min)
- Each Figma task makes 3 mandatory MCP calls (`get_variable_defs`, `get_screenshot`, `get_design_context`). A 4th call (`get_metadata` fallback) may occur if `get_design_context` is truncated, but this is rare and not counted in baseline rate limit math
- The implementer subagent cannot be given multiple node IDs — one task = one node ID
- Node Map must still provide enough structure for the planning phase to infer task layers

## Approaches Considered

### Approach A: Shallow Node Map + Type-Based Layer Inference (Chosen)
Single `get_metadata` call at depth 2. Use Figma node types (COMPONENT/COMPONENT_SET vs INSTANCE vs FRAME) to infer task layers. 2 layers instead of 3. Single node ID per task.

**Trade-offs:** Simplest change, fewest MCP calls, relies on subagent to handle component internals during implementation (which it already does well).

### Approach B: Shallow Node Map + Manual Task Grouping
Same as A, but groups semantically related layer-2 nodes into single tasks during planning.

**Trade-offs:** Fewer tasks but fragile grouping logic. Figma variants already handled via COMPONENT_SET, making grouping redundant.

### Approach C: Screen-Level Tasks (Layer 1 Only)
Map tasks to layer-1 nodes (entire screens). Subagent implements everything in one shot.

**Trade-offs:** Fewest tasks but each becomes very large — subagent context may overflow. Loses reusable component ordering entirely.

## Chosen Approach

**Approach A: Shallow Node Map + Type-Based Layer Inference.** It dramatically reduces design-phase MCP calls, keeps tasks at meaningful granularity (one component = one task), and preserves reusable component ordering via node types without extra complexity.

## Architecture

### Design Phase Changes

The Figma discovery process in `skills/design/SKILL.md` changes from recursive multi-call traversal to a single-call process:

1. **Parse each URL** to extract fileKey and nodeId (unchanged)

2. **Single `get_metadata` call at depth 2** from the root node:
   - Layer 0: Page
   - Layer 1: Screen/Section (top-level frames — names and dimensions are included in metadata)
   - Layer 2: Component or element (the task unit)
   - No recursion — the single call returns the full tree to depth 2
   - Breakpoints are inferred from top-level frame names and dimensions (e.g., "Desktop" at 1440px, "Mobile" at 375px)

3. **Build the Node Map** from the response, collapsing repeated INSTANCE nodes with `×N` notation

No `get_screenshot` or `get_design_context` calls during the design phase — these are deferred to implementation, where the subagent already calls them per-task. This keeps the design phase at exactly **1 MCP call** regardless of file complexity.

### Node Map Format

The Node Map becomes shallower (max 2 levels instead of 5):

```
#### Page: Landing Page
- **Hero Section** (node `1:2`, FRAME, 1440x800)
  - Hero Title (node `1:3`, TEXT)
  - CTA Button (node `1:4`, COMPONENT)
  - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
```

### Reusable Component Detection

From the single `get_metadata` response at depth 2:

1. **COMPONENT/COMPONENT_SET nodes** at layer 2 are definitions — automatically reusable (become Layer 1 tasks)
2. **INSTANCE nodes** sharing the same `componentId` are usages — collapsed with `×N` in the Node Map. If their definition exists in the same file, it confirms reuse
3. **Everything else** at layer 2 (FRAME, TEXT, etc.) — part of the parent section's Layer 2 task

### Planning Phase Changes

Task layer inference simplifies from 3 layers to 2:

1. **Layer 1 — Reusable components:** COMPONENT/COMPONENT_SET nodes at layer 2. Each becomes a task with its single node ID. No dependencies. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task.

2. **Layer 2 — Sections:** Each top-level FRAME becomes a task with its single node ID. Depends on any Layer 1 tasks whose components appear as children within that frame.

No Layer 3 (page assembly) — removed entirely.

### Figma Task Structure

Simplified from a multi-row Nodes table to a single node ID:

```markdown
**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
```

### SDD Concurrency Changes

Figma concurrency cap reduced from 3 to 2 tasks per wave cycle:
- 2 tasks × 3 MCP calls = 6 calls per cycle
- Safely under the 15 req/min limit

### Implementer Subagent Changes

The implementer receives a single node ID per task. The 3 mandatory MCP calls are each made once:

1. `get_variable_defs(fileKey, nodeId)` — one call
2. `get_screenshot(fileKey, nodeId)` — one call
3. `get_design_context(fileKey, nodeId)` — one call

**Fallback preserved:** If `get_design_context` response is truncated, the subagent can still call `get_metadata` on child nodes to get more detail.

No changes to token mapping rules, asset rules, implementation rules, code quality, or reporting.

## Files to Modify

| File | Change |
|------|--------|
| `skills/design/SKILL.md` | Replace recursive `get_metadata` (lines 113-125) with single depth-2 call; remove `get_design_context` on top-level frames |
| `skills/writing-plans/SKILL.md` | 2-layer inference (remove Layer 3); single node ID per task; update Figma Task Structure |
| `skills/subagent-driven-development/SKILL.md` | Concurrency cap 3 → 2; update "Why" comment and worked example |
| `skills/implementing/implement-figma-design.md` | Update Step 1/2/3 to reference single node ID; remove "for each node ID" language |
| `templates/design.md` | Shallower Node Map format (max 2 levels); update Breakpoints section to note they are inferred from frame names/dimensions in metadata |
| `templates/plan.md` | Simplified Figma task structure (single Node ID instead of Nodes table) |

## Testing Strategy

- Validate with a real Figma file that the single `get_metadata` call at depth 2 returns sufficient structure (page → section → component)
- Verify that COMPONENT/COMPONENT_SET and INSTANCE types are correctly identified at layer 2
- Test that the concurrency cap of 2 keeps MCP calls under 15/min during SDD execution
- Confirm the implementer subagent can still use `get_metadata` as fallback when `get_design_context` is truncated

## Open Questions

None — all questions resolved during design conversation.
