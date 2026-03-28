# Remove Figma Discovery Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the token-heavy figma-discovery skill and move deep Node Map generation into the design phase, so planning reads Figma structure directly from the design doc.

**Architecture:** Three surgical changes — delete discovery files, deepen the design skill's `get_metadata` recursion to component boundaries, and simplify writing-plans to infer task layers from the design doc's Node Map. No intermediate artifacts.

**Tech Stack:** Markdown skill files (no code changes)

**Spec:** `docs/superpowers/specs/2026-03-19-remove-figma-discovery-design.md`

---

## Chunk 1: All Tasks

### Task 1: Delete figma-discovery skill and artifact template

**Files:**
- Delete: `skills/figma-discovery/SKILL.md`
- Delete: `templates/figma-component-mapping.md`
**Depends on:** none

- [ ] **Step 1: Delete `skills/figma-discovery/SKILL.md`**

Remove the entire file.

- [ ] **Step 2: Delete `templates/figma-component-mapping.md`**

Remove the entire file.

- [ ] **Step 3: Commit**

```bash
git add -u skills/figma-discovery/SKILL.md templates/figma-component-mapping.md
git commit -m "chore: delete figma-discovery skill and component mapping template"
```

---

### Task 2: Deepen the design skill's Node Map generation

**Files:**
- Modify: `skills/design/SKILL.md:107-131`
**Depends on:** none

- [ ] **Step 1: Replace the Figma discovery section (lines 107-131) with recursive Node Map generation**

Replace the current step 2 ("Fetch structural metadata") at lines 113-117 with recursive `get_metadata` logic. The new content for lines 113-117 should be:

```markdown
2. **Fetch structural metadata recursively** using `get_metadata` to build a deep Node Map
   ```
   get_metadata(fileKey=":fileKey", nodeId="X-Y")
   ```
   Recurse to discover the full component tree:
   a. Call `get_metadata` on each provided root node to get first-level children
   b. For each child that is a container type (FRAME, GROUP, SECTION) but **not** a COMPONENT/INSTANCE/COMPONENT_SET, call `get_metadata` again on that child
   c. Stop recursion when hitting:
      - **COMPONENT, INSTANCE, or COMPONENT_SET** — record as a component boundary in the Node Map
      - **Leaf node types** (TEXT, RECTANGLE, VECTOR, LINE, ELLIPSE) — record and stop
      - **Max depth 5** from root — safety valve to prevent runaway recursion on deeply nested files
   d. **Repetition detection:** If the same COMPONENT/INSTANCE appears multiple times as siblings (same name or same component ID), collapse to a single Node Map entry with a `×N` count to signal reusability to the planning phase
   e. The Node Map should capture the full path: Page → Section → Subsection → Component
```

- [ ] **Step 2: Verify the edit is correct**

Read `skills/design/SKILL.md` and confirm:
- Lines 113-117 now contain the recursive `get_metadata` instructions
- The rest of the file (steps 3 and 4 — `get_design_context` and "Build the Figma Resources section") is unchanged
- The file reads coherently end-to-end

- [ ] **Step 3: Commit**

```bash
git add skills/design/SKILL.md
git commit -m "feat(design): add recursive get_metadata to build deep Node Map"
```

---

### Task 3: Simplify writing-plans Figma handling

**Files:**
- Modify: `skills/writing-plans/SKILL.md:29-91`
**Depends on:** Task 1

- [ ] **Step 1: Replace the "Figma Component Discovery (Conditional)" section**

Replace lines 29-91 (the entire `## Figma Component Discovery (Conditional)` section, from `## Figma Component Discovery (Conditional)` through `**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.`) with the following:

```markdown
## Figma Task Layer Inference

Before defining Figma tasks, check if the design doc contains a `## Figma Resources` section with a `### Node Map`.

**If Figma Resources are present**, read the Node Map and infer task layers directly — no Figma MCP calls at planning time:

1. **Layer 1 — Reusable components:** Nodes of type COMPONENT or COMPONENT_SET, or entries with a `×N` count (indicating repetition). Each becomes an individual task with no dependencies. Never group multiple reusable components into a single task.

2. **Layer 2 — Sections:** Top-level FRAME nodes in the Node Map that contain Layer 1 components as children. Each becomes a task that depends on the Layer 1 components it uses.

3. **Layer 3 — Page assembly:** If multiple sections exist, create a final task composing all sections into the full page layout. Depends on all Layer 2 tasks.

**Granularity rule:** If a node is typed COMPONENT/COMPONENT_SET or has a `×N` count, it MUST be its own Layer 1 task. Do not merge it into a parent section's task.

Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the design doc's `## Figma Resources` section.

**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.
```

- [ ] **Step 2: Update the "Why this is required" note removal check**

Confirm the old "Why this is required" note (line 33) referencing "surface-level Figma analysis" and "Deep discovery" is gone. The new section should not reference figma-discovery or component mapping artifacts.

- [ ] **Step 3: Verify coherence**

Read `skills/writing-plans/SKILL.md` and confirm:
- The `## Figma Task Layer Inference` section replaces the old `## Figma Component Discovery (Conditional)` section
- No references to `figma-discovery`, `figma-component-mapping.md`, subagent dispatch, merge step, or `.afyapowers/features/<feature>/artifacts/figma/` remain
- The `## Figma Task Structure` section (lines ~196+) still references the design doc's Node Map (not a discovery artifact)
- The file reads coherently end-to-end

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "refactor(writing-plans): replace figma-discovery dispatch with direct Node Map layer inference"
```

---

### Task 4: Update the design doc template

**Files:**
- Modify: `templates/design.md:42-59`
**Depends on:** none

- [ ] **Step 1: Replace the Figma Resources section**

Replace lines 42-59 (the `## Figma Resources` section) with:

```markdown
## Figma Resources
<!-- Only included when feature has Figma designs. Remove this section if not applicable. -->
<!-- If the feature spans multiple Figma files, repeat the File/File Key/Node Map structure for each file. -->

**File:** `<figma_url>`
**File Key:** `<file_key>`

### Breakpoints
<!-- Discovered from top-level frame analysis via get_design_context -->
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

- [ ] **Step 2: Verify the edit**

Read `templates/design.md` and confirm the Node Map section now includes:
- Comments about recursive `get_metadata` to component boundaries
- Comments about `×N` convention for reusability
- Deeper hierarchy example (3 levels: section → subsection → component)

- [ ] **Step 3: Commit**

```bash
git add templates/design.md
git commit -m "docs(template): update Figma Resources with deeper Node Map format"
```
