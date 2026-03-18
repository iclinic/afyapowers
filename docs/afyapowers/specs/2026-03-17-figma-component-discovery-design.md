# Design: Figma Component Discovery Skill

## Problem Statement

The current Figma discovery in the design phase produces a raw hierarchical Node Map — a dump of the Figma tree with node IDs, names, types, and sizes. There is no intelligent analysis of which nodes represent implementable components, no breakpoint matching across frames, and no support for design system files. The planning phase works with this flat data, producing less granular tasks that don't map cleanly to individual components.

The goal is a dedicated skill that performs deep, dynamic analysis of Figma files — identifying logical UI components, mapping them with their breakpoints, descriptions, and node IDs — so the planning phase can generate granular, component-level tasks.

## Requirements

1. A dedicated `figma-discovery` skill that performs deep analysis of Figma files
2. Two modes of operation based on file type detection:
   - **Page mode** — identifies page sections, logical components, matches across breakpoints
   - **Design system mode** — catalogs components with their variants, states, and tokens
3. Two-phase execution: lightweight **Scan** → targeted **Analyze**
4. Component identification using multiple heuristics: naming patterns, structural depth, Figma node types (FRAME, GROUP, COMPONENT, INSTANCE), size/position analysis, repetition detection, and Figma Component/Instance markers when present
5. Breakpoint matching across frames: name-first, structural-similarity fallback
6. Support for both multi-frame breakpoints (separate frames per breakpoint) and single responsive frames (auto-layout with constraints)
7. Output: rich component mapping with name, description, node IDs per breakpoint, children, reusability flag
8. Called conditionally by `writing-plans` when the design doc has a `## Figma Resources` section
9. Phase 2 uses subagents per region/group to avoid context overload and enable parallel execution

## Constraints

- Figma MCP server must be available — if unavailable, hard stop and ask user whether to fix or continue without Figma analysis
- Design phase stays lightweight (unchanged) — the deep analysis happens only during planning
- Must work with Figma files where designers have NOT used Figma's component features (infer components from structure)
- Must work with Figma files where designers HAVE used Figma's component features (use them as strong signals)
- Consistency within a file is assumed (all multi-frame or all single-responsive, not mixed)

## Approaches Considered

### Approach 1: Single-Pass Deep Crawl

One skill invocation does everything: detects file type, traverses the full hierarchy, identifies components, matches across breakpoints, and outputs the complete mapping.

**Trade-offs:**
- (+) Simplest mental model — one call, one output
- (+) All context available at once for better inference
- (-) Could hit context limits on large Figma files
- (-) All-or-nothing — if it fails midway, must restart
- (-) Harder to debug which heuristic made a bad call

### Approach 2: Two-Phase: Scan → Analyze (Chosen)

Phase 1 (Scan): Shallow crawl to detect file type, identify top-level frames, discover breakpoint strategy. Outputs a scan report.

Phase 2 (Analyze): Uses the scan report to do targeted deep dives with subagents per region. Each subagent uses `get_metadata` + `get_design_context` on its assigned region, applies heuristics, and returns its component mapping. Parent merges results.

**Trade-offs:**
- (+) Scan phase is fast and cheap — validates assumptions before deep dive
- (+) Targeted API calls — only fetches what's needed
- (+) Subagent parallelism avoids context overload
- (+) Handles large files well (chunked processing)
- (-) Two phases instead of one

### Approach 3: Three-Phase: Scan → Identify → Map

Scan → Identify component candidates → Map each candidate in detail.

**Trade-offs:**
- (+) Most granular control
- (-) Over-engineered for most cases — Phases 2 and 3 are naturally one step

## Chosen Approach

**Approach 2: Two-Phase Scan → Analyze.** It provides a fast checkpoint before the expensive analysis, handles both page and design system files naturally, uses subagents to avoid context overload, and avoids over-engineering.

## Architecture

### Skill Location

`skills/figma-discovery/SKILL.md`

### Phase 1: Scan

A single agent performs a lightweight scan using `get_metadata` on the root node(s) from the design doc's Figma Resources section. It produces a scan report with:

- **File type detection** — page vs design system. Signals:
  - Design system files: many top-level Component/ComponentSet nodes, no page-like layout
  - Page files: large frames with nested content sections
- **Breakpoint strategy** — multi-frame (separate frames per breakpoint, detected by naming patterns like "Desktop"/"Mobile" or by similar structures at different widths) vs. single responsive (one frame with auto-layout)
- **Top-level structure** — list of top-level frames with names, sizes, types
- **Candidate regions** — areas worth deep-diving into (avoids wasting API calls on decorative/trivial nodes)

### Phase 2: Analyze

A parent agent reads the scan report and dispatches **one subagent per candidate region/group**. Each subagent:

1. Receives the scan report context + its assigned region's node IDs
2. Uses `get_metadata` for structural traversal deeper into the tree
3. Uses `get_design_context` for detailed analysis of specific nodes (layout properties, spacing, typography, constraints)
4. Applies the heuristic engine to identify components:
   - **Figma component markers** — any COMPONENT or INSTANCE node is automatically a component candidate
   - **Naming patterns** — nodes named "Hero", "Header", "Card", "Footer", "Nav", "Sidebar", etc.
   - **Structural depth** — a FRAME with 3+ meaningful children (not just wrappers) is likely a component
   - **Size/position analysis** — full-width frames at top level = page sections; smaller repeated elements = reusable components
   - **Repetition detection** — if the same structure appears multiple times (same children types/count), it's a reusable component
5. Returns its local component mapping for that region

The parent agent then merges results:
- Deduplicates repeated components across regions
- For **page mode with multi-frame breakpoints**: matches components across breakpoint frames (name-first, structural-similarity fallback for unmatched nodes)
- Builds the final structured component mapping

### File Type Behavior

**Page mode:**
- Identifies page sections and logical components within each breakpoint frame
- Matches components across breakpoints
- Detects reusable components (repeated structures)

**Design system mode:**
- Catalogs each Component/ComponentSet with its variants (from Figma's variant properties)
- Captures component states (hover, disabled, active, etc.)
- No breakpoint matching needed (components are standalone)

### Single Responsive Frame Handling

When the scan detects a single responsive frame (auto-layout, constraints, min/max sizing), the analysis captures responsive behavior metadata instead of breakpoint node IDs — auto-layout direction, constraints, min/max widths — so the implementer knows how to build responsiveness.

## Data Flow

```
Writing-Plans detects ## Figma Resources in design doc
        │
        ▼
[Figma Discovery Skill — Phase 1: Scan]
  ├── get_metadata on root nodes
  ├── Detect file type (page vs design system)
  ├── Detect breakpoint strategy (multi-frame vs single responsive)
  └── Output: scan report with candidate regions
        │
        ▼
[Figma Discovery Skill — Phase 2: Analyze]
  ├── Parent dispatches subagent per region
  │     ├── get_metadata (structural traversal)
  │     ├── get_design_context (detailed analysis)
  │     ├── Apply heuristics → identify components
  │     └── Return local component mapping
  ├── Parent merges results
  │     ├── Deduplicate
  │     ├── Match across breakpoints (page mode)
  │     └── Build final mapping
  └── Output: figma-component-mapping.md
        │
        ▼
[Writing-Plans consumes mapping]
  ├── Layer 1: Tasks for reusable components (no deps)
  ├── Layer 2: Tasks for page sections (depend on reusable components they use)
  └── Layer 3: Page assembly task (depends on all sections)
```

## Output Format

### Page Mode

```markdown
## Component Mapping

### Breakpoints Detected
- Desktop: 1440px (Frame "Homepage - Desktop", node `42-1`)
- Tablet: 768px (Frame "Homepage - Tablet", node `83-1`)
- Mobile: 375px (Frame "Homepage - Mobile", node `120-1`)

### Strategy: multi-frame

### Components

#### 1. Hero Section
- **Type:** page-section
- **Description:** Full-width hero with headline, subtitle, and CTA button over background image
- **Reusable:** no
- **Nodes by breakpoint:**
  | Breakpoint | Node ID | Size |
  |------------|---------|------|
  | Desktop | `42-15` | 1440x600 |
  | Tablet | `83-12` | 768x450 |
  | Mobile | `120-8` | 375x400 |
- **Children:**
  - Heading (TEXT, node `42-16`)
  - Subtitle (TEXT, node `42-17`)
  - CTA Button (INSTANCE, node `42-18`)

#### 2. Feature Card
- **Type:** reusable-component
- **Description:** Card with icon, title, and description. Appears 3x in feature grid.
- **Reusable:** yes (3 instances)
- **Nodes by breakpoint:**
  | Breakpoint | Node ID | Size |
  |------------|---------|------|
  | Desktop | `42-30` | 400x300 |
  | Tablet | `83-25` | 350x280 |
  | Mobile | `120-20` | 375x250 |
- **Children:**
  - Icon (INSTANCE, node `42-31`)
  - Title (TEXT, node `42-32`)
  - Description (TEXT, node `42-33`)
```

### Single Responsive Frame

```markdown
#### 1. Hero Section
- **Type:** page-section
- **Description:** Full-width hero with auto-layout responsiveness
- **Reusable:** no
- **Responsive strategy:** single-frame (auto-layout)
- **Node ID:** `42-15`
- **Size:** 1440x600 (min-width: 375px)
- **Layout:** auto-layout, direction: vertical, wraps at breakpoint
- **Children:**
  - Heading (TEXT, node `42-16`)
  - Subtitle (TEXT, node `42-17`)
  - CTA Button (INSTANCE, node `42-18`)
```

### Design System Mode

```markdown
## Component Mapping

### File Type: design-system

### Components

#### 1. Button
- **Type:** design-system-component
- **Description:** Primary action button with multiple variants and states
- **Node ID:** `10-5` (ComponentSet)
- **Variants:**
  | Variant | Node ID | Properties |
  |---------|---------|------------|
  | Primary / Default | `10-6` | fill: blue-500, text: white |
  | Primary / Hover | `10-7` | fill: blue-600 |
  | Primary / Disabled | `10-8` | fill: gray-300, text: gray-500 |
  | Secondary / Default | `10-9` | fill: transparent, border: blue-500 |
- **Children:**
  - Label (TEXT, node `10-10`)
  - Icon (optional, INSTANCE, node `10-11`)
```

## Integration with Writing-Plans

The `writing-plans` skill is modified to:

1. **Detect Figma Resources** — check if the design doc has a `## Figma Resources` section
2. **Invoke figma-discovery** — dispatch as a subagent with file key(s) and root node ID(s) from the design doc
3. **Consume the component mapping** — use it to generate layered tasks:
   - **Layer 1 — Reusable components first:** One task per `reusable-component` or `design-system-component`. No page-level dependencies.
   - **Layer 2 — Page sections:** One task per `page-section`, depending on reusable components it contains as children.
   - **Layer 3 — Page assembly:** A final task composing all sections into the full page, depending on all section tasks.

Each Figma task gets the `**Figma:**` block with its specific node IDs per breakpoint from the component mapping.

Non-Figma tasks in the same plan remain unchanged — standard TDD format.

## Invocation Interface

**Caller:** `writing-plans` skill (dispatches as subagent)

**Input:**
- File Key(s): from design doc's `## Figma Resources`
- Root Node ID(s): from design doc's Node Map
- Breakpoints (if already known from design phase): from design doc

**Output:** Written to `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md`

The component mapping artifact is separate from the design doc (which stays lightweight) and gives implementer subagents a clean reference.

## Error Handling

| Scenario | Handling |
|----------|----------|
| Figma MCP server unavailable | Hard stop. Warn user and ask whether to fix the connection or continue without Figma analysis. |
| `get_metadata` returns truncated data for a large file | Scan phase fetches page-level first, then drills into sections individually |
| `get_design_context` too large for a node | Subagent uses `get_metadata` to identify children, fetches them individually |
| File type detection is ambiguous | Default to page mode, flag the ambiguity in the output for user review |
| Breakpoint matching fails (no name match, no structural match) | List the component as "unmatched" with a note — let the planner/user decide |
| Subagent fails or times out on a region | Parent continues with other regions, marks the failed region as incomplete in the output |
| No components identified (flat/simple file) | Output a minimal mapping with just the top-level frames, note that no component boundaries were detected |
| Design doc has no `## Figma Resources` section | Writing-plans skips figma-discovery entirely, proceeds with standard task generation |

## Testing Strategy

- Manual validation: run a Figma page file through the skill and verify the component mapping against manual inspection of the Figma file
- Manual validation: run a Figma design system file through the skill and verify variant/state cataloging
- Test with multi-frame breakpoint files and single responsive frame files
- Test with files where designers used Figma components and files where they didn't
- Verify writing-plans correctly generates layered tasks from the component mapping
- Verify non-Figma plans are completely unaffected

## Dependencies

- Figma MCP server must be configured and accessible
- Figma MCP tools required: `get_metadata`, `get_design_context`, `get_screenshot`
- Existing design doc must have `## Figma Resources` section (populated by design phase)

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `skills/figma-discovery/SKILL.md` | Create | New dedicated skill for deep Figma analysis |
| `skills/writing-plans/SKILL.md` | Modify | Add conditional invocation of figma-discovery when Figma Resources exist |
| `templates/figma-component-mapping.md` | Create | Template for the component mapping artifact |

## Open Questions

None — all decisions resolved during brainstorming.
