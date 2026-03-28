# Design: Figma Component Node ID & Task Generation Compliance

## Problem Statement

Two issues in the Figma workflow cause components to be lost or merged:

1. **Design phase:** When `get_metadata` returns COMPONENT/COMPONENT_SET nodes, their node IDs are not reliably included in the design document's Node Map. The instructions exist but the LLM executing the skill doesn't follow them consistently.

2. **Planning phase:** Even when components are properly annotated in the Node Map, the writing-plans skill generates only screen-level tasks (Layer 2) instead of creating per-component tasks (Layer 1) followed by screen tasks that depend on them.

Both issues are independent — fixing the Node Map doesn't fix task generation, and vice versa.

## Requirements

- COMPONENT/COMPONENT_SET node IDs must always appear in the Node Map with their type annotation
- The Node Map must separate reusable components from screens into distinct subsections
- Writing-plans must generate Layer 1 (per-component) tasks before Layer 2 (per-screen) tasks
- Layer 2 tasks must depend on Layer 1 tasks whose components appear as children
- Components are optional — designs may have no COMPONENT/COMPONENT_SET nodes (all components external or pre-existing)
- When no reusable components exist, only Layer 2 tasks are generated

## Constraints

- Changes are limited to skill instruction files and templates — no code changes
- Must not break existing behavior for designs without Figma resources
- Must work within the existing single `get_metadata` call at depth 2

## Approaches Considered

### Approach A: Strengthen Existing Prose Instructions
Add `<CRITICAL>` tags and stronger emphasis around component handling rules.

**Trade-offs:** Minimal change but LLMs can still skip prose instructions under cognitive load — this is the current failure mode.

### Approach B: Add Concrete Examples Inline
Add worked examples showing correct Node Map and task output formats.

**Trade-offs:** Examples are more reliable than rules for LLM compliance, but no self-correction mechanism.

### Approach C: Structural Enforcement with Validation Checklists (Chosen)
Combine worked examples with explicit validation steps the LLM must execute after generating output.

**Trade-offs:** Most reliable — catches errors even if initial generation is wrong. Adds some processing time but prevents cascading failures.

## Chosen Approach

**Approach C: Structural Enforcement with Validation Checklists.** The current instructions already say the right thing — the problem is compliance. Adding examples + validation checklists gives the LLM both a pattern to follow and a self-check mechanism.

## Layer Numbering Alignment

The design skill and writing-plans skill currently use conflicting layer numbering:

- **Design skill:** Layer 0 = Page, Layer 1 = Screen/Section, Layer 2 = Component/element
- **Writing-plans skill:** Layer 1 = Reusable components, Layer 2 = Sections/screens

With the new separated Node Map format (Reusable Components / Screens subsections), the layer numbers in writing-plans become the authoritative reference for task generation:

- **Layer 1 tasks** → generated from **Reusable Components** subsection
- **Layer 2 tasks** → generated from **Screens** subsection

The design skill's Layer 0/1/2 numbering describes the `get_metadata` depth levels, not task layers. To avoid confusion, the design skill instructions will be updated to refer to "depth levels" (depth 0, depth 1, depth 2) instead of "layers", reserving "Layer 1" and "Layer 2" exclusively for task generation in writing-plans.

## Architecture

### Change 1: Node Map Separation (Design Phase + Template)

The Node Map format changes from a flat nested list to two subsections:

**Before:**
```
#### Page: Landing Page
- **Hero Section** (node `1:2`, FRAME, 1440x800)
  - CTA Button (node `1:4`, COMPONENT)
  - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
  - Hero Title (node `1:3`, TEXT)
```

**After:**
```
#### Page: Landing Page

**Reusable Components:**
- CTA Button (node `1:4`, COMPONENT)
- Pricing Tier (node `2:10`, COMPONENT_SET)

**Screens:**
- **Hero Section** (node `1:2`, FRAME, 1440x800)
  - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
  - Hero Title (node `1:3`, TEXT)
- **Pricing Section** (node `2:1`, FRAME, 1440x600)
  - Pricing Tier (node `2:12`, INSTANCE, componentId: `2:10`) ×1
  - Section Title (node `2:11`, TEXT)
```

When no COMPONENT/COMPONENT_SET nodes exist:
```
**Reusable Components:**
(none — all components are external or pre-existing)

**Screens:**
- **Hero Section** (node `1:2`, FRAME, 1440x800)
  - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
  ...
```

This separation makes Layer 1 vs Layer 2 task inference trivial for the planning phase.

**Template file update (`templates/design.md`):** Lines 53-61 change from:
```
### Node Map
<!-- Single get_metadata call at depth 2. Max 2 levels: top-level frames at level 1, components/elements at level 2. -->
<!-- Mark COMPONENT/COMPONENT_SET nodes as reusable. Collapse repeated INSTANCE nodes with ×N count. -->

#### Page: <page_name>
- **<section_name>** (node `<node_id>`, <type>, <width>x<height>)
  - <component_name> (node `<node_id>`, COMPONENT)
  - <element_name> (node `<node_id>`, INSTANCE, componentId: `<component_id>`) ×N
  - <leaf_name> (node `<node_id>`, TEXT)
```

To:
```
### Node Map
<!-- Single get_metadata call at depth 2. Separated into Reusable Components and Screens subsections. -->
<!-- COMPONENT/COMPONENT_SET nodes go in Reusable Components. Everything else stays under Screens. -->

#### Page: <page_name>

**Reusable Components:**
<!-- List all COMPONENT/COMPONENT_SET nodes with node IDs. If none, write: (none — all components are external or pre-existing) -->
- <component_name> (node `<node_id>`, COMPONENT)
- <component_set_name> (node `<node_id>`, COMPONENT_SET)

**Screens:**
<!-- List each top-level FRAME with children (excluding COMPONENT/COMPONENT_SET already listed above). Collapse repeated INSTANCE nodes with ×N count. -->
- **<screen_name>** (node `<node_id>`, FRAME, <width>x<height>)
  - <element_name> (node `<node_id>`, INSTANCE, componentId: `<component_id>`) ×N
  - <leaf_name> (node `<node_id>`, TEXT)
```

### Change 2: Worked Example + Validation in Design Skill

**Insertion point:** After line 134 in `skills/design/SKILL.md` (after `Use the template from \`templates/design.md\` for the section structure.`).

**Prose update:** In the `get_metadata` instructions (lines 117-127), rename "Layer 0/1/2" to "Depth 0/1/2" to avoid collision with writing-plans' Layer 1/Layer 2 task terminology. Also update step 2's sub-instructions to reference the separated format.

Lines 117-127 change from:
```
   From the response, build the Node Map using only the first 2 levels of the returned tree:
   - **Layer 0:** Page
   - **Layer 1:** Screen/Section (top-level frames — names and dimensions are included in metadata)
   - **Layer 2:** Component or element (the task unit)

   Ignore any nodes deeper than layer 2. Breakpoints are inferred from top-level frame names and dimensions (e.g., "Desktop" at 1440px, "Mobile" at 375px).

   From the response:
   a. Record each layer-2 node with its id, name, type, and parent
   b. Mark **COMPONENT/COMPONENT_SET** nodes as reusable
   c. Collapse repeated **INSTANCE** nodes sharing the same `componentId` with a `×N` count to signal reusability to the planning phase
```

To:
```
   From the response, build the Node Map using only the first 2 depth levels of the returned tree:
   - **Depth 0:** Page
   - **Depth 1:** Screen/Section (top-level frames — names and dimensions are included in metadata)
   - **Depth 2:** Component or element (the task unit)

   Ignore any nodes deeper than depth 2. Breakpoints are inferred from top-level frame names and dimensions (e.g., "Desktop" at 1440px, "Mobile" at 375px).

   From the response, build the Node Map with two subsections:
   a. **Reusable Components:** Extract all depth-2 nodes typed COMPONENT or COMPONENT_SET. List each with its node ID and type. If none exist, write `(none — all components are external or pre-existing)`.
   b. **Screens:** List each depth-1 FRAME with its node ID, type, and dimensions. Under each frame, list its depth-2 children (excluding COMPONENT/COMPONENT_SET nodes already listed above). Collapse repeated INSTANCE nodes sharing the same `componentId` with a `×N` count.
```

**Exact text to insert after line 134:**

````
   #### Example

   `get_metadata` returns:
   ```
   Page "Landing Page"
     Frame "Hero Section" (id: 1:2, type: FRAME, 1440x800)
       ├── "Hero Title" (id: 1:3, type: TEXT)
       ├── "CTA Button" (id: 1:4, type: COMPONENT)
       ├── "Card" (id: 1:5, type: INSTANCE, componentId: 2:10)
       ├── "Card" (id: 1:6, type: INSTANCE, componentId: 2:10)
       └── "Card" (id: 1:7, type: INSTANCE, componentId: 2:10)
     Frame "Pricing Section" (id: 2:1, type: FRAME, 1440x600)
       ├── "Pricing Tier" (id: 2:10, type: COMPONENT_SET)
       ├── "Section Title" (id: 2:11, type: TEXT)
       └── "Pricing Tier" (id: 2:12, type: INSTANCE, componentId: 2:10)
   ```

   Correct Node Map output:
   ```
   #### Page: Landing Page

   **Reusable Components:**
   - CTA Button (node `1:4`, COMPONENT)
   - Pricing Tier (node `2:10`, COMPONENT_SET)

   **Screens:**
   - **Hero Section** (node `1:2`, FRAME, 1440x800)
     - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
     - Hero Title (node `1:3`, TEXT)
   - **Pricing Section** (node `2:1`, FRAME, 1440x600)
     - Pricing Tier (node `2:12`, INSTANCE, componentId: `2:10`) ×1
     - Section Title (node `2:11`, TEXT)
   ```

   **Node Map validation (run before finalizing the Figma Resources section):**
   1. Every COMPONENT/COMPONENT_SET node from the metadata has an entry with `node \`<id>\`` and its type in **Reusable Components**
   2. No COMPONENT/COMPONENT_SET node was omitted or merged into a screen's children
   3. INSTANCE nodes with the same componentId are collapsed with ×N count under their parent screen in **Screens**
   4. Every depth-1 FRAME has its node ID and dimensions in **Screens**
   5. If no COMPONENT/COMPONENT_SET nodes exist, **Reusable Components** says `(none — all components are external or pre-existing)`
````

### Change 3: Worked Example + Validation in Writing-Plans Skill

**Insertion point:** After line 41 in `skills/writing-plans/SKILL.md` (after the granularity rule: `If a node is typed COMPONENT/COMPONENT_SET, it MUST be its own Layer 1 task. Do not merge it into a parent section's task.`).

**Prose update:** Update lines 35-37 to reference the separated Node Map subsections explicitly:

Lines 35-37 change from:
```
1. **Layer 1 — Reusable components:** COMPONENT/COMPONENT_SET nodes at layer 2. Each becomes a task with its single node ID. No dependencies. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task.

2. **Layer 2 — Sections:** Each top-level FRAME becomes a task with its single node ID. Depends on any Layer 1 tasks whose components appear as children within that frame.
```

To:
```
1. **Layer 1 — Reusable components:** Each entry in the Node Map's **Reusable Components** subsection becomes a Layer 1 task with its single node ID. No dependencies. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task. If **Reusable Components** is empty or says "(none)", there are no Layer 1 tasks.

2. **Layer 2 — Screens:** Each entry in the Node Map's **Screens** subsection becomes a Layer 2 task with its single node ID. Depends on any Layer 1 tasks whose components were originally children of that frame (either as COMPONENT/COMPONENT_SET nodes extracted to Reusable Components, or as INSTANCE nodes referencing a Reusable Component).
```

**Exact text to insert after line 41:**

````
   #### Example

   Given this Node Map from the design doc:
   ```
   **Reusable Components:**
   - CTA Button (node `1:4`, COMPONENT)
   - Pricing Tier (node `2:10`, COMPONENT_SET)

   **Screens:**
   - **Hero Section** (node `1:2`, FRAME, 1440x800)
     - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
     - Hero Title (node `1:3`, TEXT)
   - **Pricing Section** (node `2:1`, FRAME, 1440x600)
     - Pricing Tier (node `2:12`, INSTANCE, componentId: `2:10`) ×1
     - Section Title (node `2:11`, TEXT)
   ```

   Correct task output:
   ```
   Task 1: CTA Button (Figma)         — Layer 1, node `1:4`, depends on: none
   Task 2: Pricing Tier (Figma)       — Layer 1, node `2:10`, depends on: none
   Task 3: Hero Section (Figma)       — Layer 2, node `1:2`, depends on: Task 1, Task 2
   Task 4: Pricing Section (Figma)    — Layer 2, node `2:1`, depends on: Task 2
   ```

   Wrong output — DO NOT do this:
   ```
   Task 1: Hero Section (Figma)       — merges CTA Button into screen task
   Task 2: Pricing Section (Figma)    — merges Pricing Tier into screen task
   ```
   ↑ Components must be their own Layer 1 tasks. Never merge them into screen tasks.

   When **Reusable Components** is empty:
   ```
   Task 1: Hero Section (Figma)       — Layer 2, node `1:2`, depends on: none
   Task 2: Pricing Section (Figma)    — Layer 2, node `2:1`, depends on: none
   ```

   **Figma task validation (run before finalizing the plan):**
   1. Every entry in **Reusable Components** has a corresponding Layer 1 task with its node ID (trivially passes if Reusable Components is empty)
   2. Every entry in **Screens** has a corresponding Layer 2 task with its node ID
   3. No Layer 2 task includes implementation work for a component that has its own Layer 1 task
   4. Layer 2 tasks depend on Layer 1 tasks whose components were originally children of that frame (extracted COMPONENT/COMPONENT_SET or INSTANCE references)
````

## Files to Modify

| File | Change |
|------|--------|
| `skills/design/SKILL.md` | (1) Rename Layer 0/1/2 to Depth 0/1/2 in lines 117-127. (2) Rewrite sub-instructions a/b/c to reference the separated Reusable Components / Screens format. (3) Insert worked example + validation checklist after line 134. |
| `skills/writing-plans/SKILL.md` | (1) Update Layer 1/Layer 2 descriptions in lines 35-37 to reference Reusable Components / Screens subsections (also renames "Sections" to "Screens" for consistency with the Node Map format). (2) Insert worked example (correct + anti-pattern + empty case) + validation checklist after line 41. |
| `templates/design.md` | Update `### Node Map` section to use two-subsection format (Reusable Components + Screens), including the empty-components placeholder. |

## Testing Strategy

- Run the design phase on a Figma file containing both COMPONENT and COMPONENT_SET nodes and verify the Node Map output uses the separated format with all node IDs present
- Run writing-plans on a design doc with the separated Node Map and verify Layer 1 + Layer 2 tasks are generated correctly
- Test with a design that has no COMPONENT/COMPONENT_SET nodes to confirm graceful handling (empty Reusable Components, only Layer 2 tasks)

## Open Questions

None — all questions resolved during design conversation.
