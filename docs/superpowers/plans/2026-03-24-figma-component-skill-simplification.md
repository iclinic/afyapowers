# Component Skill Simplification Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the `/afyapowers:component` skill from an 8-gate pipeline (~280 lines) to a 3-phase pre-flight check (~120 lines) that the LLM actually follows.

**Architecture:** Replace the verbose gate-per-section structure with a flat 3-phase flow: Parse & Validate → Dependencies & Location → Present & Confirm. Forbidden actions go at the very top. Subagent prompt is unchanged.

**Tech Stack:** Markdown (skill prompt files)

**Spec:** `docs/superpowers/specs/2026-03-24-figma-component-skill-simplification-design.md`

---

## Chunk 1: File Structure

### Files:
- Rewrite: `skills/component/SKILL.md`
- Rewrite: `commands/component.md`
- Unchanged: `skills/component/component-implementer-prompt.md`

---

### Task 1: Rewrite `skills/component/SKILL.md`

**Depends on:** none

**Files:**
- Rewrite: `skills/component/SKILL.md`

- [ ] **Step 1: Replace SKILL.md with the simplified 3-phase version**

Write the new SKILL.md with this exact content:

```markdown
---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
---

# Component Skill

<FORBIDDEN>
NEVER call get_design_context, get_screenshot, or get_variable_defs. Only the subagent calls these.
NEVER launch Explore agents or scan the codebase for conventions, tokens, or patterns.
NEVER run phases in parallel. Execute Phase 1, then Phase 2, then Phase 3, in order.
NEVER implement the component yourself. You are the orchestrator. The subagent implements.
</FORBIDDEN>

Develop a single Figma component into production code. This skill is **standalone** — not part of the 5-phase workflow.

## Trigger Conditions

**Explicit:** User runs `/afyapowers:component`.

**Implicit:** User asks to implement/build/create/develop a Figma component. Requires all three: action keyword + "component" + Figma URL. If no URL, ask for it.

---

## Phase 1 — Parse & Validate

No codebase access in this phase. Only MCP calls allowed: `get_metadata` and `get_code_connect_map`.

**Step 1 — Parse URL.** Extract `fileKey` and `nodeId` from `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>`. Normalize `nodeId` from `-` to `:` format. If no URL provided, ask the user.

Hard stop if URL is malformed or missing `node-id`:
```
**STOPPED** — Parse & Validate: Malformed Figma URL or missing node ID.

**What to do:** Provide a valid Figma component URL with the `node-id` parameter. Right-click a component in Figma → "Copy link".
```

**Step 2 — Check MCP availability.** Verify these 5 tools are callable: `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`, `get_code_connect_map`.

Hard stop if any are missing:
```
**STOPPED** — Parse & Validate: Required Figma MCP tools are not available.

**What to do:** Ensure the Figma MCP server is connected and running.
```

**Step 3 — Validate node type.** Call `get_metadata(fileKey, nodeId)`. Confirm the node type is `COMPONENT` or `COMPONENT_SET`.

**Store the full metadata response. It is reused in Phase 2. Do NOT make additional MCP calls.**

Hard stop if node type is wrong:
```
**STOPPED** — Parse & Validate: The selected node is a <actual_type>, not a COMPONENT or COMPONENT_SET.

**What to do:** Select an actual component in Figma (purple diamond icon), not a frame or instance.
```

**Step 4 — Check Code Connect.** Call `get_code_connect_map(fileKey, nodeId)`. Look for an existing entry matching this component by its Figma component key (from the metadata response). Component key is the authoritative match — not name.

**Store the full Code Connect map response. It is reused in Phase 2. Do NOT call this again.**

Hard stop if component already exists:
```
**STOPPED** — Parse & Validate: This component already exists in the codebase at `<existing_file_path>`.

**What to do:** Modify the existing file directly rather than creating a duplicate.
```

---

## Phase 2 — Dependencies & Location

Limited codebase access: only Glob and reading `package.json` / config files. No Explore agents. No scanning for conventions or patterns.

**Step 1 — Check dependencies.** From the **stored metadata response** (Phase 1, Step 3), recursively scan all descendant nodes for `INSTANCE` types with `componentId` references. No additional MCP calls needed.

**Step 2 — Cross-reference dependencies.** For each `componentId` found, check the **stored Code Connect map** (Phase 1, Step 4) for a matching entry. No additional MCP calls needed.

Hard stop if any dependencies are missing:
```
**STOPPED** — Dependencies: Missing child component dependencies.

The following components are used inside this component but have not been implemented yet:
<list of missing component names and their componentIds>

**What to do:** Implement the missing child components first using `/afyapowers:component`, then retry. Build bottom-up — leaf components before parents.
```

**Step 3 — Detect output location.** Glob for existing component directories:
- `src/components/**`
- `src/ui/**`
- `components/**`
- `lib/components/**`
- `packages/*/src/components/**`

**Step 4 — Detect framework.** Check:
- `package.json` dependencies: `react`, `vue`, `angular`, `svelte`
- Config files: `next.config.*`, `nuxt.config.*`, `vite.config.*`
- File extensions in component directories: `.tsx`, `.vue`, `.svelte`

**Step 5 — Detect Storybook.** Glob for `.storybook/` and `*.stories.*`. If not found, skip silently.

---

## Phase 3 — Present & Confirm

Show the pre-flight results to the user:

```
## Pre-flight Results

- **Component:** <name> (<COMPONENT | COMPONENT_SET>)
- **Variants:** <count> — <list> (if COMPONENT_SET)
- **Dependencies:** All found | Missing: <list>
- **Suggested directory:** <path> (you can override this)
- **Framework:** <detected> (you can override this)
- **Storybook:** detected — generate story file? (yes/no) | not detected
- **Code Connect:** No existing mapping

Ready to implement this component?
```

Wait for the user to respond. The user can:
- Confirm and proceed to dispatch
- Override the suggested directory or framework
- Accept or decline Storybook story generation
- Decline to stop entirely

---

## Dispatch

After the user confirms, dispatch the implementer subagent using the **Agent tool**. Build the prompt from `component-implementer-prompt.md`, filling in:

- `[FILE_KEY]` — from Phase 1, Step 1
- `[NODE_ID]` — from Phase 1, Step 1
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET from Phase 1, Step 3
- `[VARIANT_LIST]` — variant names from metadata (or "N/A — single component")
- `[OUTPUT_DIRECTORY]` — confirmed path from Phase 3
- `[FRAMEWORK]` — confirmed framework from Phase 3
- `[GENERATE_STORYBOOK]` — yes or no from Phase 3
- `[COMPONENT_NAME]` — component name from metadata

### After the Subagent Returns

- **If DONE:** Commit all created files and report success.
- **If BLOCKED:** Relay the block reason:
```
**STOPPED** — Component Implementation: <reason from subagent>

**What to do:** <actionable instruction based on the block reason>
```

- [ ] **Step 2: Verify the new SKILL.md**

Read the file and confirm:
1. No references to `get_design_context`, `get_screenshot`, or `get_variable_defs` outside the FORBIDDEN block and MCP availability check
2. No mention of "Gate" or "8 gates"
3. The FORBIDDEN block is at the very top, immediately after frontmatter
4. Phases are clearly sequential with `---` separators
5. Line count is under 160

- [ ] **Step 3: Commit**

```bash
git add skills/component/SKILL.md
git commit -m "refactor(component): simplify skill from 8-gate pipeline to 3-phase pre-flight"
```

---

### Task 2: Update `commands/component.md`

**Depends on:** none

**Files:**
- Rewrite: `commands/component.md`

- [ ] **Step 1: Replace commands/component.md with updated documentation**

Write the new content:

```markdown
# /afyapowers:component — Develop a Figma Component

You are developing a standalone Figma component. This is **not** part of the 5-phase workflow — it is an independent command for implementing individual components from Figma.

Invoke the **component** skill to handle the entire process. The skill will:

1. Ask for the Figma component URL (if not already provided)
2. Run a 3-phase pre-flight check (parse & validate, dependencies & location, present & confirm)
3. After user confirmation, dispatch an implementer subagent to translate the Figma design into production code
4. Hard stop on any issue — no partial results, no workarounds

Pass along any Figma URL or component reference the user has already provided.
```

- [ ] **Step 2: Commit**

```bash
git add commands/component.md
git commit -m "docs(component): update command docs to match simplified 3-phase skill"
```

---

### Task 3: Verify end-to-end

**Depends on:** Task 1, Task 2

**Files:** none (verification only)

- [ ] **Step 1: Invoke `/afyapowers:component` with a Figma URL and verify:**

1. NO `get_design_context` calls during pre-flight
2. NO Explore agents launched
3. Phases run sequentially (Phase 1 completes before Phase 2)
4. Only `get_metadata` and `get_code_connect_map` MCP calls are made
5. Summary is presented and user is asked to confirm before dispatch
6. If user confirms, subagent is dispatched with correct context
