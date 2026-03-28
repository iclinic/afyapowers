# Design: Standalone Figma Component Development Skill

## Problem Statement

The current Figma workflow is tightly coupled to the 5-phase development pipeline (design → plan → implement → review → complete). When a developer needs to implement a single Figma component — whether building out a design system or adding a standalone component to a project — there is no dedicated, streamlined path. The developer must either run the full workflow (overkill) or manually invoke MCP tools without guardrails (error-prone).

## Requirements

- Standalone skill with dedicated command `afyapowers:component`, independent of the 5-phase workflow
- Support both explicit invocation (`/afyapowers:component`) and implicit detection (user asks to implement a Figma component)
- Validate that the Figma node is a COMPONENT or COMPONENT_SET before proceeding
- Detect ungrouped variants (siblings that should be in a COMPONENT_SET) and hard stop if found
- Check Code Connect for existing component mappings — hard stop if component already exists
- Detect missing child component dependencies — hard stop and list what needs to be implemented first
- Auto-detect output directory from project structure, confirm with user
- Detect Storybook/docs setup and offer to generate alongside the component
- Fully autonomous implementation after all gates pass — hard stop on any issue (no partial results)

## Constraints

- Figma MCP server must be connected (tools: `get_metadata`, `get_variable_defs`, `get_screenshot`, `get_design_context`, `get_code_connect_map`)
- Figma MCP rate limit: 15 requests/minute
- Component must be a COMPONENT or COMPONENT_SET — no other node types accepted
- Variants must be properly grouped in a COMPONENT_SET (Figma best practice)
- All child component dependencies must exist in the codebase before implementation

## Approaches Considered

### Approach A: Single Monolithic Skill

One `SKILL.md` file containing the entire workflow — validation, Figma fetching, Code Connect checks, and implementation — in a single document.

**Trade-offs:** Simple to maintain and read. But large file (~300+ lines), duplicates logic from existing `implement-figma-design.md`, and creates a maintenance burden when Figma implementation rules evolve.

### Approach B: Skill + Dedicated Subagent Prompt (Chosen)

A `SKILL.md` that owns orchestration (validation gates, user interaction, Code Connect check, dependency detection) and delegates Figma-to-code implementation to a dedicated subagent prompt adapted from `implement-figma-design.md`.

**Trade-offs:** Separates orchestration from implementation. Leverages battle-tested Figma implementation logic. Consistent with the project's existing architecture (skill + subagent prompt pattern). Requires two files to coordinate.

### Approach C: Skill as Pure Orchestrator + Multiple Subagents

Separate subagents for validation, Code Connect, dependency scanning, and implementation.

**Trade-offs:** Maximum modularity. But over-engineered — validation and checking steps are lightweight and sequential. Only implementation benefits from subagent isolation.

## Chosen Approach

**Approach B: Skill + Dedicated Subagent Prompt.** Matches the project's existing architecture, keeps validation gates in the orchestrating skill, and reuses proven Figma implementation logic via a dedicated subagent.

## Architecture

### File Structure

```
skills/component/
├── SKILL.md                          # Orchestration skill (gates + user interaction)
└── component-implementer-prompt.md   # Subagent prompt (Figma-to-code translation)
```

### SKILL.md Frontmatter

```yaml
---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
command: afyapowers:component
---
```

### Trigger Conditions

- **Explicit:** User invokes `/afyapowers:component`
- **Implicit:** User asks to implement/build/create/develop a Figma component — detected via keywords ("implement", "build", "create", "develop") combined with "component" and a Figma URL or reference

### Orchestration Pipeline

Eight sequential validation gates. Each must pass before proceeding. Any failure = hard stop.

```
Gate 1: Input & URL Parsing
    ↓
Gate 2: Figma MCP Availability
    ↓
Gate 3: Node Type Validation
    ↓
Gate 4: Variant Structure Validation
    ↓
Gate 5: Code Connect Dedup Check
    ↓
Gate 6: Dependency Detection
    ↓
Gate 7: Output Location Resolution
    ↓
Gate 8: Storybook/Docs Detection
    ↓
Dispatch: Component Implementer Subagent
```

### Gate Details

**Gate 1 — Input & URL Parsing:**
- If the user provided a Figma URL, parse `fileKey` and `nodeId` from it
- If no URL was provided, ask for it
- Hard stop if URL is malformed or missing node ID

**Gate 2 — Figma MCP Availability:**
- Verify `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`, and `get_code_connect_map` tools are available
- Hard stop with status BLOCKED if any are unavailable

**Gate 3 — Node Type Validation:**
- Call `get_metadata(fileKey, nodeId)` to fetch the node
- Verify the node type is COMPONENT or COMPONENT_SET
- Hard stop if it's any other type (FRAME, INSTANCE, GROUP, etc.) — tell the user to select an actual component in Figma

**Gate 4 — Variant Structure Validation:**
- If the node is a COMPONENT_SET — pass (variants are properly grouped)
- If the node is a COMPONENT — call `get_metadata(fileKey, parentNodeId)` on the component's parent node (parent ID is available in the Gate 3 metadata response) to enumerate siblings. Check if any sibling components share the same base name with different property suffixes (e.g., "Button/Default", "Button/Hover") that are NOT grouped in a COMPONENT_SET
- Hard stop if ungrouped variants detected — tell the user to group them into a Component Set in Figma first

**Gate 5 — Code Connect Dedup Check:**
- Call `get_code_connect_map()` and look for an existing entry matching this component by Figma component key (the unique identifier Figma assigns to each component, available in the Gate 3 metadata response). Component key is the authoritative match criterion — name matching is not used since components can be renamed
- Hard stop if the component already has a Code Connect mapping — notify the user with the existing file path from the mapping

**Gate 6 — Dependency Detection:**
- From the metadata, scan child nodes for INSTANCE types that reference other components
- For each referenced component, check via Code Connect whether it already exists in the codebase
- Hard stop if any dependency is missing — list the missing child components and tell the user to implement them first

**Gate 7 — Output Location Resolution:**
- Scan project for existing component directories (e.g., `src/components/`, `src/ui/`, design system paths)
- Propose the detected location to the user, ask them to confirm or override
- If no component directory is detected (e.g., brand new project), ask the user to specify the output directory explicitly — do not guess or create a default structure

**Gate 8 — Storybook/Docs Detection:**
- Check if the project has Storybook configured (look for `.storybook/`, `*.stories.*` files) or similar doc tooling
- If found, ask the user if they want a story/doc file generated alongside the component
- If not found, skip silently

### Component Implementer Subagent

The subagent receives a fully validated context from the orchestrator and focuses purely on Figma-to-code translation.

**Core principles (inherited from `implement-figma-design.md`):**
- Figma is absolute authority
- 3 mandatory MCP calls in order: `get_variable_defs` → `get_screenshot` → `get_design_context`
- Strict token mapping (exact name + exact value = use project token, otherwise hardcode Figma value)
- Assets from Figma with dedup check
- Accessibility additions are the one exception (semantic HTML, aria-labels)

**Differences from existing `implement-figma-design.md`:**
- No file constraint from a plan — the orchestrator provides the output directory
- Must handle all variants in a COMPONENT_SET in one pass
- Must generate Storybook file if requested (receives flag from orchestrator)
- Status reporting: DONE or BLOCKED only. Token mapping fallbacks (hardcoding Figma values when no project token matches) and accessibility additions are expected behavior — they produce DONE, not concerns. BLOCKED is reserved for issues that prevent completion (missing assets, MCP failures, ambiguous design structure)
- Component file naming derived from Figma component name, converted to project conventions (e.g., PascalCase for React)

**Reuse mechanism:** The subagent prompt is a **fork** of `implement-figma-design.md`, not a wrapper. The standalone component context (no plan, no file constraints, all-variants-in-one-pass) diverges enough from plan-driven task context that a shared base would add coupling without benefit. If core Figma implementation rules change (token mapping, MCP call order), both files must be updated.

**Context received from orchestrator:**
- `fileKey`, `nodeId`
- Node type (COMPONENT or COMPONENT_SET)
- Variant list (names and property combinations) if COMPONENT_SET
- Output directory path
- Whether to generate Storybook/docs
- Project framework context (React, Vue, etc.)

**Framework detection:** The orchestrator detects the project framework before dispatch by checking for framework markers: `package.json` dependencies (react, vue, angular, svelte), config files (`next.config.*`, `nuxt.config.*`, `vite.config.*`), or file extensions in the component directories (`.tsx`, `.vue`, `.svelte`). This is a lightweight check performed as part of Gate 7 (output location resolution) since both steps inspect the same project structure.

**Status reporting:** DONE or BLOCKED with reason. No partial results.

### Error Handling

Every hard stop follows a consistent format:

```
**STOPPED** — [Gate Name]: [Clear reason]

**What to do:** [Actionable instruction for the user]
```

| Gate | Reason | User Action |
|------|--------|-------------|
| Gate 1 | Malformed URL or missing node ID | Provide a valid Figma component link with node ID |
| Gate 2 | Figma MCP server unavailable | Connect the Figma MCP server |
| Gate 3 | Node is not COMPONENT or COMPONENT_SET | Select an actual component node in Figma |
| Gate 4 | Ungrouped variants detected | Group the variants into a Component Set in Figma |
| Gate 5 | Component already exists (Code Connect match) | Shows existing file path — no work needed |
| Gate 6 | Missing child component dependencies | Lists missing components — implement them first |
| Subagent | Any issue during implementation | Reports what went wrong — user investigates |

No retries, no workarounds, no partial results. The user fixes the root cause and re-invokes the skill.

## Testing Strategy

- Verify each gate independently with valid and invalid inputs
- Test COMPONENT vs COMPONENT_SET handling paths
- Test Code Connect dedup with matching and non-matching entries
- Test dependency detection with components that have and lack child dependencies
- Test output location detection across different project structures
- Test Storybook detection with and without Storybook configured
- End-to-end: valid COMPONENT_SET with all gates passing through to DONE status
