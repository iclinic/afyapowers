# Figma Workflow Rewrite Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the Figma implementation pipeline — rewrite subagent prompt, remove plan duplication, fix discovery depth.

**Architecture:** Three independent file changes: (1) full rewrite of the subagent prompt with 3-step MCP workflow and Figma absolute authority, (2) trim plan template and writing-plans skill to remove duplicated how-to steps, (3) add recursive metadata exploration to figma-discovery.

**Tech Stack:** Markdown skill files (no code changes)

---

### Task 1: Rewrite the Figma implementer subagent prompt

**Files:**
- Modify: `skills/implementing/implement-figma-design.md` (full rewrite)

**Depends on:** none

- [ ] **Step 1: Replace the entire file content**

Replace all 302 lines of `skills/implementing/implement-figma-design.md` with the new subagent prompt. The new file must contain exactly these sections in this order:

**Header (frontmatter):**
```yaml
---
name: implement-design
description: Figma implementer subagent — translates Figma designs into production code with absolute fidelity. Requires Figma MCP server.
metadata:
  mcp-server: figma
---
```

**Section: Figma Implementer Subagent Prompt Template**

Opening paragraph explaining this is a template for dispatching implementer subagents for Figma tasks, and that Figma has absolute authority over the implementation.

**Section: Core Principles (3 items)**
1. Figma is absolute authority — every visual property comes from Figma. Never substitute, approximate, or prefer codebase patterns. If a token doesn't exist in the project, hardcode the Figma value.
2. 3 mandatory MCP calls in order — `get_variable_defs` → `get_screenshot` → `get_design_context`. No skipping, no reordering. `get_metadata` only as overflow handler for truncated responses.
3. Assets come from Figma — always use Figma-provided assets. Check if exact same asset exists in codebase first (dedup). Never substitute with local icon libraries.

**Section: Prerequisites**
- Figma MCP server must be connected (check for `get_design_context`, `get_variable_defs` tools)
- If unavailable, report BLOCKED

**Section: Workflow (3 steps)**

Step 1 — Build Token Reference Table:
- Call `get_variable_defs(fileKey, nodeId)` for each node ID
- Build lookup table: token name → resolved value (colors, typography, spacing, borders, shadows, opacity)
- This is the single source of truth for all design values

Step 2 — Capture Visual Reference:
- Call `get_screenshot(fileKey, nodeId)` for primary nodes
- Source of truth for layout (arrangement, sizing, spacing)
- Keep accessible for comparison throughout implementation

Step 3 — Fetch Design Context + Cross-Reference:
- Call `get_design_context(fileKey, nodeId)` for each node ID
- Provides: hierarchy, auto-layout, sizing modes, variants, interactive states, implementation suggestions
- Cross-reference every token name against Step 1 table
- Token Mapping Rule:
  - Name match + value match → use project token
  - Name match + value mismatch → hardcode Figma value
  - No match → hardcode Figma value
- If truncated: use `get_metadata` to get child IDs, then `get_design_context` on children
- Fallback: if `get_variable_defs` returned no tokens, use raw `get_design_context` values and flag DONE_WITH_CONCERNS

**Section: Asset Rules (5 items)**
1. Always use Figma assets (icons, images, SVGs from MCP server)
2. Dedup check — search codebase for existing exact match before downloading. If found, use existing. If not, download from Figma.
3. Never substitute with icon libraries (lucide, heroicons, etc.). Never create placeholders.
4. Icons as SVG (`.svg`), not raster. Photos/illustrations can be raster.
5. Use asset URLs as-is from MCP server

**Section: Implementation Rules (5 items)**
1. Figma overrides codebase patterns — follow Figma when it differs from conventions
2. Reuse existing components when they match — but if Figma shows something different, implement what Figma shows
3. Token mapping is strict — exact name + exact value = project token. Anything else = hardcode.
4. No additions beyond Figma — no extra JSDoc, types, features, or refactoring
5. File constraint — only modify files in task's Files section. Otherwise report NEEDS_CONTEXT.

**Section: Reporting**
- Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What was implemented
- Visual validation (does it match the screenshot?)
- Files changed
- Concerns (unmatched tokens, inaccessible assets, layout ambiguities)

Use DONE_WITH_CONCERNS if any doubt about visual accuracy or assets. Use BLOCKED if Figma MCP unavailable. Use NEEDS_CONTEXT if need files not in task. Never silently produce uncertain work.

**Section: Escalation**
When stuck: report BLOCKED or NEEDS_CONTEXT with what you tried and what help you need.

**Target: ~150 lines total.** No examples section, no best practices section, no common issues section. The rules are the rules.

- [ ] **Step 2: Verify the rewrite**

Read the file back and confirm:
- Frontmatter is valid YAML
- All 3 MCP steps are present in correct order
- Token Mapping Rule is complete (3 cases)
- All 5 asset rules present
- All 5 implementation rules present
- Reporting section with all 4 statuses
- File is ~120-160 lines
- No references to Tailwind, no "prefer project tokens" language, no conflicting guidance

- [ ] **Step 3: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "rewrite(figma): simplified subagent prompt with absolute Figma authority"
```

### Task 2: Trim plan template — remove duplicated Figma steps

**Files:**
- Modify: `templates/plan.md:34-55`

**Depends on:** none

- [ ] **Step 1: Replace the Figma task template in plan.md**

In `templates/plan.md`, replace lines 34-55 (the entire `### Task N: [UI Component Name] (Figma)` block) with:

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

Key change: 7 implementation steps collapsed to 1 step. The subagent prompt owns the how.

- [ ] **Step 2: Commit**

```bash
git add templates/plan.md
git commit -m "refactor(plan): replace 7 Figma steps with single implementer workflow step"
```

### Task 3: Trim writing-plans skill — remove duplicated Figma guidance

**Files:**
- Modify: `skills/writing-plans/SKILL.md:111-118,226-232,244,247`

**Depends on:** none

- [ ] **Step 1: Replace the Figma steps block in Bite-Sized Task Granularity**

In `skills/writing-plans/SKILL.md`, replace lines 111-118:

```
**For Figma tasks, steps follow the implement-design workflow instead of TDD:**
- "Fetch design context for all task nodes" - step
- "Capture screenshot for visual reference" - step
- "Download required assets" - step
- "Translate to project conventions" - step
- "Achieve 1:1 visual parity across all breakpoints" - step
- "Validate against Figma screenshot" - step
- "Commit" - step
```

With:

```
**For Figma tasks:** a single step — "Implement using the Figma implementer workflow and commit". The subagent prompt owns the how. No implementation steps in the plan.
```

- [ ] **Step 2: Replace the 7-step checklist in Figma Task Structure**

In the same file, replace lines 226-232:

```
- [ ] Step 1: Fetch design context for all task nodes
- [ ] Step 2: Capture screenshot for visual reference
- [ ] Step 3: Download required assets (images, icons, SVGs)
- [ ] Step 4: Translate to project conventions
- [ ] Step 5: Achieve 1:1 visual parity across all breakpoints
- [ ] Step 6: Validate against Figma screenshot
- [ ] Step 7: Commit
```

With:

```
- [ ] Implement using the Figma implementer workflow and commit
```

- [ ] **Step 3: Update the Remember section**

In the same file, replace line 244 (keep line 243 `## Remember` heading intact):

```
- Complete code in plan (not "add validation") — except for Figma tasks which use design-workflow steps instead of code
```

With:

```
- Complete code in plan (not "add validation") — except for Figma tasks which have a single workflow step
```

And replace line 247:

```
- Figma tasks: no TDD, no code snippets — steps describe what to achieve, not how to code it
```

With:

```
- Figma tasks: no TDD, no code snippets, single workflow step — the subagent prompt owns the how
```

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "refactor(writing-plans): remove duplicated Figma implementation steps"
```

### Task 4: Strengthen layered task generation in writing-plans

**Files:**
- Modify: `skills/writing-plans/SKILL.md:79-87`

**Depends on:** Task 3

- [ ] **Step 1: Update Step 4 layered task generation**

In `skills/writing-plans/SKILL.md`, replace lines 79-87 (the Step 4 section content):

```
### Step 4: Generate layered tasks from the merged mapping

**Read the resulting component mapping** from `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md` and use it to generate layered tasks:

- **Layer 1 — Reusable components:** One task per component marked as `reusable-component` or `design-system-component`. These have no page-level dependencies and can be built first.
- **Layer 2 — Page sections:** One task per `page-section`, with dependencies on any reusable components it uses as children.
- **Layer 3 — Page assembly:** A final task composing all sections into the full page, depending on all section tasks.

Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the component mapping.
```

With:

```
### Step 4: Generate layered tasks from the merged mapping

**Read the resulting component mapping** from `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md` and use it to generate layered tasks:

- **Layer 1 — Reusable components:** One task per component marked as `reusable-component` or `design-system-component`. These are individual tasks — never group multiple reusable components into a single screen-level task. These have no page-level dependencies and can be built first.
- **Layer 2 — Page sections:** One task per `page-section`, with dependencies on any Layer 1 reusable components it uses as children.
- **Layer 3 — Page assembly:** A final task composing all sections into the full page, depending on all Layer 2 section tasks.

**Granularity rule:** If discovery identified a component (e.g., "Stats Card", "CTA Button") as reusable or as a distinct design-system-component, it MUST be its own task in Layer 1. Do not merge it into a parent section's task. The deeper the discovery goes, the more granular the tasks should be.

Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the component mapping.
```

- [ ] **Step 2: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "refactor(writing-plans): strengthen layered task generation granularity"
```

### Task 5: Fix discovery depth — add recursive metadata exploration

**Files:**
- Modify: `skills/figma-discovery/SKILL.md:69-71`

**Depends on:** none

- [ ] **Step 1: Replace Phase 2 step 1 with recursive instructions**

In `skills/figma-discovery/SKILL.md`, replace lines 71 (Phase 2, step 1):

```
1. **Deep structural traversal** using `get_metadata` on its assigned region to explore the full subtree
```

With:

```
1. **Recursive structural traversal** using `get_metadata`:
   a. Run `get_metadata` on the assigned region's root node to get first-level children
   b. For each child that is a FRAME or GROUP with its own children (not leaf nodes like TEXT, RECTANGLE, VECTOR, LINE, ELLIPSE), run `get_metadata` again on that child to explore the next level
   c. Continue recursing until reaching leaf nodes or depth 4 (max from region root)
   d. Build a complete node tree from the merged results before proceeding to steps 2-5

   **Why recurse:** A single `get_metadata` call returns only immediate children. Without recursion, a "Hero Section" frame appears as a single node — its internal components (buttons, cards, badges) remain invisible, and discovery produces screen-level tasks instead of component-level tasks.
```

- [ ] **Step 2: Commit**

```bash
git add skills/figma-discovery/SKILL.md
git commit -m "fix(figma-discovery): add recursive get_metadata for component-level depth"
```
