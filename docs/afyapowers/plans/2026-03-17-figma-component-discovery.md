# Figma Component Discovery Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a dedicated `figma-discovery` skill that performs deep, two-phase analysis of Figma files — identifying logical UI components, mapping them with breakpoints and node IDs — so the planning phase can generate granular, component-level tasks.

**Architecture:** A new skill at `skills/figma-discovery/SKILL.md` implements a two-phase Scan → Analyze workflow. Phase 1 uses `get_metadata`, `get_screenshot`, and `get_code_connect_map` for lightweight file-type detection and structure discovery. Phase 2 dispatches subagents per region that use `get_metadata`, `get_design_context`, `get_screenshot`, and `get_code_connect_suggestions` with a multi-heuristic engine to identify components. The `writing-plans` skill is modified to invoke this skill conditionally when a design doc contains Figma Resources.

**Tech Stack:** Figma MCP server (remote), MCP tools (`get_metadata`, `get_design_context`, `get_screenshot`, `get_code_connect_map`, `get_code_connect_suggestions`)

---

## Chunk 1: Figma Discovery Skill and Template

### Task 1: Create the figma-component-mapping template

**Files:**
- Create: `templates/figma-component-mapping.md`

**Depends on:** none

- [ ] **Step 1: Create `templates/figma-component-mapping.md`**

Create the template file that defines the output format for the figma-discovery skill. This template is used by the skill to structure its output artifact.

```markdown
# Figma Component Mapping: {{feature_name}}

## Scan Report

**File Key:** `<file_key>`
**File Type:** page | design-system
**Breakpoint Strategy:** multi-frame | single-responsive

### Breakpoints Detected
<!-- Only for page mode with multi-frame strategy -->
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

### Code Connect Mappings
<!-- Only if Code Connect is configured for this file -->
- <node_id> → <code_component_name> (<code_connect_src>)
<!-- If none: "No Code Connect mappings found." -->

## Component Mapping

### Strategy: multi-frame | single-responsive

### Components

#### N. <Component Name>
- **Type:** page-section | reusable-component | design-system-component
- **Description:** <what this component is and does visually>
- **Reusable:** yes (<N> instances) | no
- **Nodes by breakpoint:**
  | Breakpoint | Node ID | Size |
  |------------|---------|------|
  | <breakpoint> | `<node_id>` | <width>x<height> |
- **Children:**
  - <child_name> (<type>, node `<node_id>`)

<!-- For single responsive frame components, replace "Nodes by breakpoint" with: -->
<!-- - **Responsive strategy:** single-frame (auto-layout) -->
<!-- - **Node ID:** `<node_id>` -->
<!-- - **Size:** <width>x<height> (min-width: <min>px) -->
<!-- - **Note:** Responsive properties to be fetched at implementation time -->

<!-- For design-system-component, replace "Nodes by breakpoint" with: -->
<!-- - **Node ID:** `<node_id>` (ComponentSet) -->
<!-- - **Variants:** -->
<!--   | Variant | Node ID | -->
<!--   |---------|---------|  -->
<!--   | <variant_name> | `<node_id>` | -->
```

- [ ] **Step 2: Verify the template**

Read `templates/figma-component-mapping.md` and confirm it covers all three output modes: page mode (multi-frame), page mode (single responsive), and design system mode.

- [ ] **Step 3: Commit**

```bash
git add templates/figma-component-mapping.md
git commit -m "feat: add figma component mapping template"
```

---

### Task 2: Create the figma-discovery skill

**Files:**
- Create: `skills/figma-discovery/SKILL.md`

**Depends on:** Task 1

- [ ] **Step 1: Create `skills/figma-discovery/SKILL.md`**

This is the core skill file. It defines the two-phase Scan → Analyze workflow, the heuristic engine, and the output format.

```markdown
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

1. **Deep structural traversal** using `get_metadata` on its assigned region to explore the full subtree

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
```

- [ ] **Step 2: Verify the skill file**

Read `skills/figma-discovery/SKILL.md` and confirm:
- Frontmatter has name, description, and mcp-server metadata
- Both phases are fully documented with tools, steps, and expected behavior
- The heuristic engine lists all 5 signal types (markers, naming, depth, size/position, repetition)
- Breakpoint matching describes both passes (name, structural similarity)
- Both file type behaviors are documented (page mode, design system mode)
- Error handling covers all scenarios from the spec
- Output references the template

- [ ] **Step 3: Commit**

```bash
git add skills/figma-discovery/SKILL.md
git commit -m "feat: create figma-discovery skill with two-phase scan/analyze workflow"
```

---

## Chunk 2: Writing-Plans Integration

### Task 3: Add figma-discovery invocation to writing-plans skill

**Files:**
- Modify: `skills/writing-plans/SKILL.md`

**Depends on:** Task 2

> **Note:** The writing-plans skill already has Figma task structure support (added by the figma-workflow-integration plan). This task adds the conditional invocation of the figma-discovery skill to produce the component mapping before task generation.

- [ ] **Step 1: Add Figma Discovery invocation section**

In `skills/writing-plans/SKILL.md`, find the section between `## Scope Check` and `## File Structure`. After `## Scope Check` and its existing content (preserve it), insert a new section:

```markdown
## Figma Component Discovery (Conditional)

Before defining tasks, check if the design doc (`.afyapowers/features/<feature>/artifacts/design.md`) contains a `## Figma Resources` section.

**If Figma Resources are present:**

1. **Dispatch the figma-discovery skill** as a subagent with:
   - File Key(s) from the `## Figma Resources` section
   - Root Node ID(s) from the Node Map in `## Figma Resources`
   - Breakpoints (if listed in `## Figma Resources`)

   ```
   Agent tool (general-purpose):
     description: "Figma component discovery"
     prompt: |
       You are running the figma-discovery skill.
       Read and follow: skills/figma-discovery/SKILL.md

       Input:
       - File Key: <file_key>
       - Root Node IDs: <node_ids>
       - Breakpoints: <breakpoints_if_known>
       - Feature: <feature_name>

       Write output to: .afyapowers/features/<feature>/artifacts/figma-component-mapping.md
   ```

2. **Read the resulting component mapping** from `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md`

3. **Use the mapping to generate layered tasks:**
   - **Layer 1 — Reusable components:** One task per component marked as `reusable-component` or `design-system-component`. These have no page-level dependencies and can be built first.
   - **Layer 2 — Page sections:** One task per `page-section`, with dependencies on any reusable components it uses as children.
   - **Layer 3 — Page assembly:** A final task composing all sections into the full page, depending on all section tasks.

   Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the component mapping.

**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.
```

- [ ] **Step 2: Verify the modification**

Read `skills/writing-plans/SKILL.md` and confirm:
- The new section appears between Scope Check and File Structure
- The subagent dispatch template references `skills/figma-discovery/SKILL.md`
- The layered task generation strategy is documented (Layer 1 → 2 → 3)
- The conditional check is clear (presence of `## Figma Resources`)

- [ ] **Step 3: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat: add conditional figma-discovery invocation to writing-plans skill"
```
