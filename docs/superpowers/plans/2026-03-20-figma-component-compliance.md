# Figma Component Compliance Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix component node ID preservation in design docs and per-component task generation in implementation plans.

**Architecture:** Three independent edits to skill instruction files and one template. Each change adds worked examples and validation checklists to enforce LLM compliance with existing rules that were being skipped.

**Tech Stack:** Markdown skill files (no code changes)

---

### Task 1: Update design template Node Map format

**Files:**
- Modify: `templates/design.md:53-61`
**Depends on:** none

- [ ] **Step 1: Replace the Node Map section**

  Replace lines 53-61 in `templates/design.md`. The current flat format (single `#### Page:` with all nodes nested under frames) becomes a two-subsection format with **Reusable Components** and **Screens** separated.

  Current content (lines 53-61):
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

  Replace with:
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

- [ ] **Step 2: Verify the template renders correctly**

  Read the full file and confirm the Figma Resources section flows logically: File → File Key → Breakpoints → Node Map (with Reusable Components and Screens subsections).

- [ ] **Step 3: Commit**

  ```bash
  git add templates/design.md
  git commit -m "refactor(template): separate Node Map into Reusable Components and Screens"
  ```

---

### Task 2: Add worked example + validation to design skill

**Files:**
- Modify: `skills/design/SKILL.md:117-134`
**Depends on:** Task 1

- [ ] **Step 1: Rename Layer to Depth in lines 117-127**

  In the `get_metadata` instructions, replace all "Layer 0/1/2" references with "Depth 0/1/2" and rewrite sub-instructions a/b/c to reference the separated format.

  Replace lines 117-127 (from `From the response, build the Node Map` through the `×N` count instruction) with:

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

- [ ] **Step 2: Insert worked example + validation after line 134**

  After the line `Use the template from \`templates/design.md\` for the section structure.`, insert the following block:

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

- [ ] **Step 3: Verify no "Layer" references remain in the get_metadata section**

  Search `skills/design/SKILL.md` for the word "layer" (case-insensitive) in the Figma discovery section (lines 107-140 area). Only "depth" should appear. "Layer" references may still exist elsewhere in the file if they refer to other contexts — that's fine, only the `get_metadata` instructions should use "depth".

- [ ] **Step 4: Commit**

  ```bash
  git add skills/design/SKILL.md
  git commit -m "refactor(design): depth terminology + worked example + validation checklist for Node Map"
  ```

---

### Task 3: Add worked example + validation to writing-plans skill

**Files:**
- Modify: `skills/writing-plans/SKILL.md:35-41`
**Depends on:** none

- [ ] **Step 1: Update Layer 1/Layer 2 descriptions in lines 35-37**

  Replace lines 35-37 (from `1. **Layer 1 — Reusable components:**` through `2. **Layer 2 — Sections:**`) with:

  ```
  1. **Layer 1 — Reusable components:** Each entry in the Node Map's **Reusable Components** subsection becomes a Layer 1 task with its single node ID. No dependencies. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task. If **Reusable Components** is empty or says "(none)", there are no Layer 1 tasks.

  2. **Layer 2 — Screens:** Each entry in the Node Map's **Screens** subsection becomes a Layer 2 task with its single node ID. Depends on any Layer 1 tasks whose components were originally children of that frame (either as COMPONENT/COMPONENT_SET nodes extracted to Reusable Components, or as INSTANCE nodes referencing a Reusable Component).
  ```

  Note: "Sections" is renamed to "Screens" for consistency with the Node Map format.

- [ ] **Step 2: Insert worked example + validation after line 41**

  After the line `Each Figma task uses the Figma Task Structure format (see below) with a single node ID and breakpoints from the design doc's \`## Figma Resources\` section.`, insert:

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

- [ ] **Step 3: Commit**

  ```bash
  git add skills/writing-plans/SKILL.md
  git commit -m "refactor(writing-plans): explicit Node Map references + worked example + validation checklist"
  ```
