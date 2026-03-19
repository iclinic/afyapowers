---
name: figma-discovery
description: "Deep analysis of Figma files to identify implementable components with node ID mappings and breakpoints. Called conditionally by writing-plans when a design doc has Figma Resources. NOT a user-facing skill."
metadata:
  mcp-server: figma
---

# Figma Component Discovery

## Overview

Performs deep, dynamic analysis of Figma files to identify logical UI components and produce a structured component mapping. The output maps each component with its node IDs, breakpoints, description, children, and reusability — enabling the planning phase to generate granular, component-level tasks.

## Prerequisites

- Figma MCP server must be connected and accessible
  - Before proceeding, verify the Figma MCP server is connected by checking if Figma MCP tools (e.g., `get_metadata`, `get_design_context`) are available.
  - **If the tools are not available: HARD STOP.** Warn the user and ask whether to fix the MCP server connection or continue without Figma analysis. Do not proceed silently.

## Input

Provided by the caller (typically `writing-plans`):

- **File Key(s):** from the design doc's `## Figma Resources` section
- **Root Node ID(s):** from the design doc's Node Map
- **Breakpoints (if already known):** from the design doc

## Execution: Two-Phase Workflow

### Phase 1: Scan

A lightweight scan to understand the file structure before committing to expensive deep dives.

**Tools used:**
- `get_metadata` — structural hierarchy (node IDs, names, types, positions, sizes)
- `get_screenshot` — visual understanding of page organization, section boundaries, and layout patterns
- `get_code_connect_map` — check if Code Connect mappings already exist (provides direct node-to-component mapping if configured)

**Run `get_metadata` on each root node ID.** Then run `get_screenshot` on each root node for visual context. Then run `get_code_connect_map` to check for existing mappings.

**Produce a scan report with:**

1. **File type detection** — page vs design system:
   - **Design system signals:** many top-level Component/ComponentSet nodes, no page-like layout, components organized by category (Buttons, Inputs, Cards, etc.)
   - **Page signals:** large frames with nested content sections, layout-oriented hierarchy, content-filled frames

2. **Breakpoint strategy** (page mode only):
   - **Multi-frame:** separate top-level frames per breakpoint, detected by:
     - Naming patterns: "Desktop", "Mobile", "Tablet", width suffixes like "1440", "375"
     - Similar internal structures at different widths
   - **Single responsive:** one frame using auto-layout with constraints/min-max sizing

3. **Top-level structure** — list of top-level frames with names, sizes, types

4. **Candidate regions** — areas worth deep-diving into:
   - Skip decorative/trivial nodes (simple rectangles, single-color backgrounds, basic dividers)
   - Focus on frames with meaningful children (3+ children, or named with component-like names)

5. **Existing Code Connect mappings** — if available, these provide pre-existing node-to-component mappings that supplement or shortcut the heuristic engine

### Phase 2: Analyze

Dispatch **one subagent per candidate region/group** for parallel execution. This avoids context overload on large files and enables faster processing.

**Each subagent receives:**
- The scan report (file type, breakpoint strategy, Code Connect mappings)
- Its assigned region's node IDs

**Each subagent performs:**

1. **Recursive structural traversal** using `get_metadata`:
   a. Run `get_metadata` on the assigned region's root node to get first-level children
   b. For each child that is a FRAME or GROUP with its own children (not leaf nodes like TEXT, RECTANGLE, VECTOR, LINE, ELLIPSE), run `get_metadata` again on that child to explore the next level
   c. Continue recursing until reaching leaf nodes or depth 4 (max from region root)
   d. Build a complete node tree from the merged results before proceeding to steps 2-5

   **Why recurse:** A single `get_metadata` call returns only immediate children. Without recursion, a "Hero Section" frame appears as a single node — its internal components (buttons, cards, badges) remain invisible, and discovery produces screen-level tasks instead of component-level tasks.

2. **Targeted detail fetching** using `get_design_context` on nodes that appear to be component boundaries (not for token extraction — for understanding structure, children, and layout relationships)

3. **Visual reference** using `get_screenshot` on the region to help identify component boundaries and visual grouping

4. **Figma component detection** using `get_code_connect_suggestions` to supplement heuristic analysis with Figma's own component detection capabilities

5. **Heuristic engine** — apply ALL of the following signals to identify components:

   a. **Figma component markers** — any COMPONENT or INSTANCE node is automatically a component candidate. This is the strongest signal when available.

   b. **Naming patterns** — nodes named with recognizable UI component names:
      - Page sections: "Hero", "Header", "Footer", "Nav", "Navbar", "Sidebar", "Banner", "CTA"
      - Reusable components: "Card", "Button", "Input", "Modal", "Dialog", "Badge", "Avatar", "Tooltip"
      - Layout: "Grid", "List", "Container", "Section", "Row", "Column"

   c. **Structural depth** — a FRAME with 3+ meaningful children (not just wrappers or single-child groups) is likely a component. Single-child FRAMEs are likely wrappers and should be traversed through.

   d. **Size/position analysis:**
      - Full-width frames at the top level of a page = page sections
      - Smaller elements at consistent sizes = reusable components
      - Elements aligned in grids or lists = instances of a reusable component

   e. **Repetition detection** — if the same structure appears multiple times (same child count, same child types, similar sizes), it's a reusable component. Mark it as such and count instances.

6. **Return** the local component mapping for the region

**Parent agent merges results:**

- Deduplicates repeated components found across regions
- For **page mode with multi-frame breakpoints**: matches components across breakpoint frames:
  - **First pass — name matching:** exact or fuzzy name match (e.g., "Hero Section" in Desktop matches "Hero Section" in Mobile)
  - **Second pass — structural similarity:** for unmatched nodes, compare child count, child types, and tree depth to find the best match
  - Components that remain unmatched after both passes are listed as "unmatched" with a note
- Builds the final structured component mapping

### File Type Behavior

**Page mode:**
- Identifies page sections and logical components within each breakpoint frame
- Matches components across breakpoints
- Detects reusable components (repeated structures)
- Output includes breakpoint-specific node IDs per component

**Design system mode:**
- Catalogs each Component/ComponentSet with its variants (from Figma's variant properties)
- Captures variant names and node IDs (no design tokens — those are deferred to implementation)
- Captures component states (hover, disabled, active, etc.) as variants
- No breakpoint matching needed (components are standalone)

## Output

Write the component mapping to `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md` using the template from `templates/figma-component-mapping.md`.

The output includes:
- Scan report summary (file type, breakpoint strategy, Code Connect mappings)
- Component list with: name, type, description, reusability flag, node IDs per breakpoint (or single node ID for responsive/design-system), children
- Unmatched components (if any) flagged for user review

## Error Handling

| Scenario | Handling |
| --- | --- |
| Figma MCP server unavailable | Hard stop. Warn user and ask whether to fix the connection or continue without Figma analysis. |
| `get_metadata` returns truncated data | Fetch page-level metadata first, then drill into individual sections |
| `get_design_context` too large for a node | Use `get_metadata` to identify children, fetch them individually |
| File type detection is ambiguous | Default to page mode, flag the ambiguity in the output for user review |
| Breakpoint matching fails | List the component as "unmatched" with a note — let the planner/user decide |
| Subagent fails or times out on a region | Parent continues with other regions, marks the failed region as incomplete |
| No components identified | Output minimal mapping with top-level frames, note that no component boundaries were detected |
