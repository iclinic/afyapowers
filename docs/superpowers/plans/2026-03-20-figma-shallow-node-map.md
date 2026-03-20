# Figma Shallow Node Map & Rate Limit Optimization — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Reduce Figma MCP calls during design phase to 1, simplify task mapping to 1 node ID per task, and lower SDD concurrency cap to stay within 15 req/min.

**Architecture:** All changes are to markdown skill files and templates — no application code. Six files are updated to reflect the shallow Node Map approach (depth 2), 2-layer task inference, single node ID per task, and revised concurrency limits.

**Tech Stack:** Markdown (skill definitions, templates)

---

### Task 1: Update design template — shallow Node Map format

**Files:**
- Modify: `templates/design.md:50,53-62`
**Depends on:** none

- [x] **Step 1: Replace the Node Map section**

  Replace the current deep Node Map template (lines 53-62) with the shallow format. Lines 42-49 and 51-52 are preserved as-is. The new Node Map has max 2 levels: top-level frames at level 1, components/elements at level 2. Include `componentId` for INSTANCE nodes and `×N` notation for repeated instances.

  New example structure:
  ```
  #### Page: <page_name>
  - **<section_name>** (node `<node_id>`, <type>, <width>x<height>)
    - <component_name> (node `<node_id>`, COMPONENT)
    - <element_name> (node `<node_id>`, INSTANCE, componentId: `<component_id>`) ×N
    - <leaf_name> (node `<node_id>`, TEXT)
  ```

- [x] **Step 2: Update the Breakpoints section comment**

  Change the comment on line 50 from referencing `get_design_context` to noting that breakpoints are inferred from top-level frame names and dimensions in the `get_metadata` response.

- [x] **Step 3: Commit**

  ```bash
  git add templates/design.md
  git commit -m "refactor(template): shallow Node Map format with depth-2 structure"
  ```

---

### Task 2: Update plan template — single Node ID Figma task structure

**Files:**
- Modify: `templates/plan.md:28-44`
**Depends on:** none

- [x] **Step 1: Replace the Figma task template**

  Replace the current Figma task template (lines 28-44) which has a multi-row Nodes table with the simplified single Node ID structure:

  ```markdown
  ### Task N: [UI Component Name] (Figma)

  **Files:**
  - Create: `exact/path/to/component`

  **Depends on:** none | Task X

  **Figma:**
  - **File Key:** `<file_key>`
  - **Node ID:** `<id>`
  - **Breakpoints:** <breakpoint_name> (<width>px), ...

  - [x] Implement using the Figma implementer workflow and commit
  ```

- [x] **Step 2: Commit**

  ```bash
  git add templates/plan.md
  git commit -m "refactor(template): single Node ID in Figma task structure"
  ```

---

### Task 3: Update design skill — single get_metadata call at depth 2

**Files:**
- Modify: `skills/design/SKILL.md:107-138`
**Depends on:** none

- [x] **Step 1: Replace the entire Figma discovery process (lines 107-138) in a single pass**

  Replace everything from "If the user provides Figma URL(s):" (line 107) through "Use the template from `templates/design.md` for the section structure." (line 138). Lines 139-144 (MCP unavailable warning, no-Figma fallback, design tokens note) are preserved as-is. The new process has 3 steps:

  1. **Parse each URL** — extract fileKey and nodeId (keep existing URL format docs from lines 109-111)

  2. **Single `get_metadata` call at depth 2** from the root node. Describe the 3 layers returned:
     - Layer 0: Page
     - Layer 1: Screen/Section (top-level frames — names and dimensions included in metadata)
     - Layer 2: Component or element (the task unit)
     - No recursion — single call returns the full tree to depth 2
     - Breakpoints are inferred from top-level frame names and dimensions (e.g., "Desktop" at 1440px, "Mobile" at 375px)

  3. **Build the `## Figma Resources` section** for the design doc:
     - File info (URL, file key)
     - Breakpoints (inferred from top-level frame names and dimensions in the metadata response)
     - Node Map: record each layer-2 node with its id, name, type, and parent. Mark COMPONENT/COMPONENT_SET nodes as reusable. Collapse repeated INSTANCE nodes sharing the same `componentId` with `×N` notation.
     - Use the template from `templates/design.md` for the section structure

  This single replacement removes the old recursive `get_metadata` logic, the `get_design_context` on top-level frames step, and the old "Build the Figma Resources section" step — all in one pass. No `get_screenshot` or `get_design_context` calls during the design phase — these are deferred to implementation. This keeps the design phase at exactly 1 MCP call regardless of file complexity.

- [x] **Step 2: Commit**

  ```bash
  git add skills/design/SKILL.md
  git commit -m "refactor(design): single get_metadata call at depth 2 for Figma discovery"
  ```

---

### Task 4: Update writing-plans skill — 2-layer inference and single Node ID

**Files:**
- Modify: `skills/writing-plans/SKILL.md:29-181`
**Depends on:** none

- [x] **Step 1: Replace the Figma Task Layer Inference section**

  Replace lines 29-45 with the new 2-layer inference. The old Layer 1 rule on line 35 ("or entries with a `×N` count") must be removed and replaced with the new INSTANCE rule below:

  1. **Layer 1 — Reusable components:** COMPONENT/COMPONENT_SET nodes at layer 2. Each becomes a task with its single node ID. No dependencies. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task.

  2. **Layer 2 — Sections:** Each top-level FRAME becomes a task with its single node ID. Depends on any Layer 1 tasks whose components appear as children within that frame.

  Remove Layer 3 (page assembly) entirely.

  Update the granularity rule: "If a node is typed COMPONENT/COMPONENT_SET, it MUST be its own Layer 1 task. Do not merge it into a parent section's task."

  Update the Figma task reference to say "node ID" (singular) instead of "node IDs".

- [x] **Step 2: Replace the Figma Task Structure section**

  Replace lines 146-181. The new Figma Task Structure uses a single Node ID instead of a Nodes table:

  ```markdown
  ### Task N: [UI Component Name] (Figma)

  **Files:**
  - Create: `exact/path/to/component`
  - Create: `exact/path/to/styles` (if applicable)
  **Depends on:** none | Task X, Task Y

  **Figma:**
  - **File Key:** `<file_key>`
  - **Node ID:** `<id>`
  - **Breakpoints:** <breakpoint_name> (<width>px), ...

  - [x] Implement using the Figma implementer workflow and commit
  ```

  Update "Building the Figma block" instructions:
  - **File Key:** Copy from the design doc's `## Figma Resources` section
  - **Node ID:** The single node ID for this task's component from the Node Map
  - **Breakpoints:** Include only the breakpoints relevant to this task's component

  Remove the **Nodes:** instruction about selecting nodes and their children — no longer applicable.

- [x] **Step 3: Commit**

  ```bash
  git add skills/writing-plans/SKILL.md
  git commit -m "refactor(writing-plans): 2-layer inference and single Node ID per Figma task"
  ```

---

### Task 5: Update SDD skill — concurrency cap 3 → 2

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:90-167`
**Depends on:** none

- [x] **Step 1: Update the concurrency cap**

  On line 98, change "dispatch up to **3** per cycle" to "dispatch up to **2** per cycle". Update "pick the first 3" to "pick the first 2".

- [x] **Step 2: Update the "Why" comment**

  Replace line 100:
  - Old: `> **Why 3?** The Figma MCP rate-limits at 20 requests/minute. Each Figma task makes 3-4 MCP calls, so 3 concurrent tasks ≈ 9-12 calls — safely under the limit.`
  - New: `> **Why 2?** The Figma MCP rate-limits at 15 requests/minute. Each Figma task makes 3 mandatory MCP calls, so 2 concurrent tasks = 6 calls — safely under the limit.`

- [x] **Step 3: Update line 102**

  Change "up to 3 Figma" to "up to 2 Figma".

- [x] **Step 4: Update the prompt routing note**

  On line 105, change "nodes table" to "node ID" in the Figma metadata reference: "Include the Figma metadata (file key, node ID, breakpoints) in the agent context."

- [x] **Step 5: Update the Mixed Figma / Non-Figma worked example**

  Replace lines 161-167 to reflect the cap of 2:
  ```
  Ready: [1(std), 2(std), 3(figma), 4(figma), 5(std), 6(figma)]
  → Classify: non-Figma = [1, 2, 5], Figma = [3, 4, 6]
  → Apply caps: all non-Figma + first 2 Figma
  → Dispatch: [1, 2, 5] + [3, 4] = 5 parallel agents
  → Task 6 (Figma) waits for next cycle
  ```

- [x] **Step 6: Commit**

  ```bash
  git add skills/subagent-driven-development/SKILL.md
  git commit -m "refactor(sdd): figma concurrency cap 3 to 2 for 15 req/min limit"
  ```

---

### Task 6: Update implementer subagent — single node ID workflow

**Files:**
- Modify: `skills/implementing/implement-figma-design.md:27-50`
**Depends on:** none

- [x] **Step 1: Update Step 1 (Build Token Reference Table)**

  On line 29, change "Call `get_variable_defs(fileKey, nodeId)` for each node ID in your Figma Resources table" to "Call `get_variable_defs(fileKey, nodeId)` using the single node ID from your task's Figma block."

- [x] **Step 2: Update Step 2 (Capture Visual Reference)**

  On line 41, change "Call `get_screenshot(fileKey, nodeId)` for the primary node(s) in your task" to "Call `get_screenshot(fileKey, nodeId)` using the single node ID from your task's Figma block."

- [x] **Step 3: Update Step 3 (Fetch Design Context)**

  On line 47, change "Call `get_design_context(fileKey, nodeId)` for each node ID in your Figma Resources table" to "Call `get_design_context(fileKey, nodeId)` using the single node ID from your task's Figma block."

- [x] **Step 4: Commit**

  ```bash
  git add skills/implementing/implement-figma-design.md
  git commit -m "refactor(implementer): single node ID per task in MCP workflow"
  ```
