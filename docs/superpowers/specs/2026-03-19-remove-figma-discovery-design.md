# Remove Figma Discovery: Deepen Design, Simplify Planning

## Problem

The `figma-discovery` skill is a heavy two-phase process (scan + parallel subagent analysis with recursive `get_metadata`) that consumes excessive tokens and produces unreliable results. The design document already includes a `## Figma Resources` section with node IDs and hierarchy — if we deepen that Node Map to component boundaries during design time, the discovery phase becomes unnecessary.

## Solution

Three changes:

1. **Delete `figma-discovery`** entirely — skill file and artifact template
2. **Deepen the design skill's Node Map** — recurse `get_metadata` until hitting COMPONENT/INSTANCE/COMPONENT_SET nodes or leaf nodes
3. **Simplify `writing-plans`** — remove discovery dispatch, read layers directly from the design doc's Node Map

## Design

### 1. Delete figma-discovery

**Files removed:**
- `skills/figma-discovery/SKILL.md`
- `templates/figma-component-mapping.md`

**References to clean up:**
- `skills/writing-plans/SKILL.md` — remove all figma-discovery dispatch logic (conditional `## Figma Resources` detection that triggers discovery, parallel subagent spawning per frame, merge step, and Step 4 layered generation from the mapping artifact)
- `skills/subagent-driven-development/SKILL.md` — remove any references to figma-discovery
- Any mention of `figma-component-mapping.md` as an artifact

### 2. Deepen the design skill's Node Map generation

**File modified:** `skills/design/SKILL.md`

**Current behavior:** Calls `get_metadata` on root nodes and builds a ~2-level Node Map.

**New behavior:** Recurse deeper:

1. Call `get_metadata` on each root node ID
2. For each child that is a container type (FRAME, GROUP, SECTION) but **not** a COMPONENT/INSTANCE/COMPONENT_SET, recurse with another `get_metadata` call
3. Stop when hitting:
   - **COMPONENT, INSTANCE, or COMPONENT_SET** — record as a leaf in the Node Map (component boundary)
   - **Leaf node types** (TEXT, RECTANGLE, VECTOR, LINE, ELLIPSE) — record and stop
   - **Max depth 5** from root — safety valve to prevent runaway recursion
4. The Node Map captures the full path: Page → Section → Subsection → Component

**Repetition detection:** If the same COMPONENT/INSTANCE appears multiple times as siblings (same name or same component ID), collapse to a single entry with a `×N` count to signal reusability.

**Example output:**

```markdown
#### Page: Homepage
- **Hero Section** (node `123`, FRAME, 1440x800)
  - Headline Group (node `124`, FRAME)
    - Title (node `125`, TEXT)
    - Subtitle (node `126`, TEXT)
  - CTA Button (node `127`, COMPONENT)
  - Hero Image (node `128`, INSTANCE)
- **Stats Section** (node `130`, FRAME, 1440x400)
  - Stats Card (node `131`, COMPONENT) ×3
```

### 3. Simplify `writing-plans` Figma handling

**File modified:** `skills/writing-plans/SKILL.md`

**What gets removed:**
- Conditional check that detects `## Figma Resources` and triggers figma-discovery dispatch
- Parallel subagent spawning (one per top-level frame)
- Merge step combining discovery outputs into `figma-component-mapping.md`
- Step 4's dependency on the mapping artifact

**What replaces it:**

When the design doc contains `## Figma Resources`, `writing-plans` reads the Node Map directly and infers layers:

1. **Layer 1 — Reusable components:** Nodes marked as COMPONENT/COMPONENT_SET, or entries with `×N` count. Individual tasks, no dependencies.
2. **Layer 2 — Sections:** Top-level FRAME nodes that contain the reusable components. Depend on the Layer 1 components they use.
3. **Layer 3 — Page assembly:** If multiple sections exist, a task that assembles them into the page layout. Depends on all Layer 2 tasks.

**Task format unchanged** — File Key, Breakpoints, Nodes table, single implementation step. The only difference is node data comes from the design doc's Node Map instead of a discovery artifact.

**No Figma MCP calls at planning time.** The design doc is the single source of truth.

### 4. Update the design doc template

**File modified:** `templates/design.md`

Update `## Figma Resources` section to reflect deeper Node Map expectations and `×N` convention:

```markdown
## Figma Resources

**File:** `<figma_url>`
**File Key:** `<file_key>`

### Breakpoints
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

### Node Map
<!-- Recursive get_metadata down to component boundaries (COMPONENT/INSTANCE/COMPONENT_SET) or leaf nodes. -->
<!-- Mark repeated components with ×N count to signal reusability. -->

#### Page: <page_name>
- **<section_name>** (node `<node_id>`, <type>, <width>x<height>)
  - <subsection_name> (node `<node_id>`, <type>)
    - <component_name> (node `<node_id>`, COMPONENT) ×N
  - <leaf_name> (node `<node_id>`, TEXT)
```

## Files Changed

| File | Change |
|------|--------|
| `skills/figma-discovery/SKILL.md` | Delete |
| `templates/figma-component-mapping.md` | Delete |
| `skills/design/SKILL.md` | Add recursive `get_metadata` to component boundaries in Node Map generation |
| `skills/writing-plans/SKILL.md` | Remove discovery dispatch, add direct Node Map layer inference |
| `templates/design.md` | Update Figma Resources section with deeper hierarchy example and `×N` convention |
| `skills/subagent-driven-development/SKILL.md` | Remove any figma-discovery references (if present) |

## Design Principles

1. **Single source of truth** — the design doc's Node Map is the only Figma structure artifact. No intermediate mappings.
2. **One phase produces, one phase consumes** — design builds the Node Map, planning reads it. No Figma calls at planning time.
3. **Component boundaries as natural stopping points** — recurse until hitting COMPONENT/INSTANCE/COMPONENT_SET, which is semantically meaningful rather than an arbitrary depth limit.
4. **Token efficiency** — eliminates the expensive two-phase discovery process (scan + parallel subagent analysis) that was the primary token consumer.
