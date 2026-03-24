# Figma Component Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone skill (`afyapowers:component`) that validates, deduplicates, and implements individual Figma components with strict gate-based orchestration.

**Architecture:** Two files — `skills/component/SKILL.md` (orchestration with 8 sequential validation gates) and `skills/component/component-implementer-prompt.md` (subagent prompt forked from `implement-figma-design.md`, adapted for standalone component context). The skill is independent of the 5-phase workflow.

**Tech Stack:** Markdown skill files (no code changes)

---

## Chunk 1: Skill Files

### Task 1: Create the orchestration skill (SKILL.md)

**Files:**
- Create: `skills/component/SKILL.md`
- Reference: `skills/implementing/implement-figma-design.md` (for core principles consistency)
- Reference: `skills/design/SKILL.md` (for Figma URL parsing pattern)

**Depends on:** none

- [x] **Step 1: Write the SKILL.md file**

Create `skills/component/SKILL.md` with the following content. The file has three sections: frontmatter, trigger conditions, and the 8-gate orchestration pipeline.

**Frontmatter:**

```yaml
---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
command: afyapowers:component
---
```

**Trigger section:** Document both explicit (`/afyapowers:component`) and implicit trigger conditions. Implicit triggers fire when the user asks to implement/build/create/develop a Figma component — detected via keywords ("implement", "build", "create", "develop") combined with "component" and a Figma URL or reference.

**Gate pipeline:** Write all 8 gates as sequential, numbered sections. Each gate must include:
- What it does (one sentence)
- The MCP call or check it performs (exact tool name and parameters)
- Pass condition
- Hard stop condition with the exact error message format:

```
**STOPPED** — [Gate Name]: [Clear reason]

**What to do:** [Actionable instruction for the user]
```

The 8 gates in order:

**Gate 1 — Input & URL Parsing:**
- Parse `fileKey` and `nodeId` from user-provided Figma URL
- If no URL provided, ask for it
- Hard stop if URL is malformed or missing node ID
- URL format: `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>` (nodeId may use `-` instead of `:` in the URL, normalize to `:` format)

**Gate 2 — Figma MCP Availability:**
- Verify these MCP tools are available: `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`, `get_code_connect_map`
- Hard stop with BLOCKED if any are unavailable

**Gate 3 — Node Type Validation:**
- Call `get_metadata(fileKey, nodeId)`
- Pass if node type is COMPONENT or COMPONENT_SET
- Hard stop if any other type — tell user to select an actual component node in Figma
- Store the full metadata response — it is reused by Gates 4 and 6

**Gate 4 — Variant Structure Validation:**
- If COMPONENT_SET — pass immediately (variants are properly grouped)
- If COMPONENT — call `get_metadata(fileKey, parentNodeId)` using the parent ID from Gate 3 metadata. Enumerate siblings. Check if any sibling components share the same base name with different property suffixes (e.g., "Button/Default", "Button/Hover") that are NOT grouped in a COMPONENT_SET
- Hard stop if ungrouped variants detected — tell user to group them into a Component Set in Figma first

**Gate 5 — Code Connect Dedup Check:**
- Call `get_code_connect_map()`. Look for an existing entry matching this component by Figma component key (unique ID from Gate 3 metadata). Component key is the authoritative match — name matching is not used since components can be renamed
- Hard stop if match found — notify user with the existing file path from the mapping

**Gate 6 — Dependency Detection:**
- From the Gate 3 metadata, scan child nodes for INSTANCE types that reference other components (via `componentId`)
- For each referenced component, check via the Code Connect map (already fetched in Gate 5) whether it exists in the codebase
- Hard stop if any dependency is missing — list the missing child components and tell user to implement them first

**Gate 7 — Output Location Resolution + Framework Detection:**
- Scan project for existing component directories using Glob patterns: `src/components/**`, `src/ui/**`, `components/**`, `lib/components/**`, `packages/*/src/components/**`
- Detect project framework by checking: `package.json` dependencies (react, vue, angular, svelte), config files (`next.config.*`, `nuxt.config.*`, `vite.config.*`), or file extensions in component directories (`.tsx`, `.vue`, `.svelte`)
- Propose detected location and framework to user, ask to confirm or override
- If no component directory detected, ask user to specify the output directory explicitly — do not guess or create a default structure

**Gate 8 — Storybook/Docs Detection:**
- Check for Storybook: Glob for `.storybook/` directory and `*.stories.*` files
- If found, ask user if they want a story file generated alongside the component
- If not found, skip silently

**Dispatch section:** After all gates pass, describe the upfront summary shown to user before dispatching:
- Component name
- Type (COMPONENT or COMPONENT_SET)
- Variant count and names (if COMPONENT_SET)
- Output directory
- Framework
- Storybook: yes/no

Then dispatch the component implementer subagent (see `component-implementer-prompt.md`) with the full validated context. The dispatch uses the Agent tool with `subagent_type: general-purpose`.

After the subagent returns:
- If DONE — commit all files, report success to user
- If BLOCKED — relay the block reason to user with the standard STOPPED format

- [x] **Step 2: Review the file for internal consistency**

Read back the full `skills/component/SKILL.md` and verify:
- All 8 gates are present and in order
- Each gate has pass/fail conditions and hard stop messages
- No TODOs or placeholders remain
- Gate cross-references are correct (Gate 4 references Gate 3 metadata, Gate 6 references Gate 5 Code Connect map)
- The dispatch section references the correct subagent prompt file name

- [x] **Step 3: Commit**

```bash
git add skills/component/SKILL.md
git commit -m "feat(component): add orchestration skill with 8-gate validation pipeline"
```

---

### Task 2: Create the component implementer subagent prompt

**Files:**
- Create: `skills/component/component-implementer-prompt.md`
- Reference: `skills/implementing/implement-figma-design.md` (fork source)
- Reference: `skills/implementing/implementer-prompt.md` (for report format pattern)

**Depends on:** none

- [x] **Step 1: Write the component-implementer-prompt.md file**

Fork from `skills/implementing/implement-figma-design.md` and adapt for standalone component context. The file is a subagent prompt template with these sections:

**Template structure:** Use the same Agent tool dispatch template format as `skills/implementing/implementer-prompt.md` — a markdown code block with `Task tool (general-purpose):` header containing `description:` and `prompt: |` fields.

**Context injection:** The prompt template must include placeholder markers for the orchestrator to fill in:
- `[FILE_KEY]` — Figma file key
- `[NODE_ID]` — Figma node ID
- `[NODE_TYPE]` — COMPONENT or COMPONENT_SET
- `[VARIANT_LIST]` — variant names and property combinations (or "N/A — single component" for COMPONENT)
- `[OUTPUT_DIRECTORY]` — confirmed output path
- `[FRAMEWORK]` — detected framework (React, Vue, etc.)
- `[GENERATE_STORYBOOK]` — yes/no
- `[COMPONENT_NAME]` — Figma component name

**Core Principles section:** Copy verbatim from `implement-figma-design.md`:
1. Figma is absolute authority
2. 3 mandatory MCP calls in order: `get_variable_defs` → `get_screenshot` → `get_design_context`
3. Assets come from Figma (with dedup check)

**Prerequisites section:** Same as `implement-figma-design.md` — verify Figma MCP server is connected, report BLOCKED if not.

**Workflow section:** Same 3-step workflow as `implement-figma-design.md` (Build Token Reference Table → Capture Visual Reference → Fetch Design Context + Cross-Reference) with these adaptations:
- Remove all references to "task's Figma block" — replace with the injected `[FILE_KEY]` and `[NODE_ID]`
- After Step 3, add a **Step 4 — Implement All Variants** section:
  - If COMPONENT_SET: implement the base variant first, then extend for each additional variant. Use the variant list from the context to ensure all are covered. For TypeScript/React projects, derive prop types from variant properties (e.g., `type ButtonVariant = 'primary' | 'secondary' | 'ghost'`). For other frameworks, use the idiomatic variant pattern (e.g., Vue props with validator, Svelte exported props)
  - If single COMPONENT: implement directly
  - Component file naming: convert Figma component name to project conventions (PascalCase for React, kebab-case for Vue, etc. based on `[FRAMEWORK]`)
  - Output files to `[OUTPUT_DIRECTORY]`

**Storybook section:** Add a **Step 5 — Generate Storybook Story (if requested)** section:
- Only execute if `[GENERATE_STORYBOOK]` is "yes"
- Create a `*.stories.*` file alongside the component
- Include a story for each variant showing all states
- Follow existing story patterns in the project (check for CSF3 format, controls, etc.)

**Asset Rules section:** Copy verbatim from `implement-figma-design.md`.

**Implementation Rules section:** Adapted from `implement-figma-design.md`:
- Remove the file constraint rule (currently: "**File constraint.** Only modify files listed in the task's Files section. If you need files not in the list, report NEEDS_CONTEXT.") — replace with: "**Output location.** Output files to the directory specified in context. Create subdirectories if the component needs multiple files (e.g., component + styles + types)."
- Keep all other rules verbatim

**Code Quality section:** Copy verbatim from `implement-figma-design.md`.

**Best Practices section:** Copy verbatim from `implement-figma-design.md`.

**Reporting section:** Simplified from `implement-figma-design.md`:
- Status: DONE or BLOCKED only (no DONE_WITH_CONCERNS, no NEEDS_CONTEXT)
- Token mapping fallbacks and accessibility additions are expected behavior → DONE
- Missing assets, MCP failures, ambiguous design structure → BLOCKED
- Include: what was implemented, visual validation result, files created, variant coverage

**Escalation section:** Same as `implement-figma-design.md` — report BLOCKED with what was tried, what's blocking, what help is needed.

- [x] **Step 2: Cross-check against implement-figma-design.md**

Read both `skills/component/component-implementer-prompt.md` and `skills/implementing/implement-figma-design.md` side by side. Verify:
- Core principles are identical (Figma authority, 3 MCP calls, asset rules)
- Token Mapping Rule is identical (exact name + exact value = project token, otherwise hardcode)
- No accidental omissions from the fork
- The adaptations (no file constraint, all-variants-in-one-pass, Storybook, simplified status) are correctly applied

- [x] **Step 3: Commit**

```bash
git add skills/component/component-implementer-prompt.md
git commit -m "feat(component): add component implementer subagent prompt forked from implement-figma-design"
```

