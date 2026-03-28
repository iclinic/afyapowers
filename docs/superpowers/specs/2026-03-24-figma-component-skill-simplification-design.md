# Design: Simplify Component Skill to Pre-flight + Optional Dispatch

## Problem Statement

The `/afyapowers:component` skill has an 8-gate validation pipeline that the LLM consistently violates:

1. **Calls forbidden MCP tools** (`get_design_context`) during the gate phase
2. **Runs gates in parallel** despite explicit sequential requirement
3. **Explores the codebase** for conventions, tokens, and patterns — work that belongs to the implementer subagent

The root cause is prompt length and complexity. The 8-gate structure with detailed instructions per gate gives the LLM too many places to go off-script. The hard rules exist but are buried in a ~280-line document.

## Requirements

- The skill should ONLY do pre-flight checks: parse URL, check dependencies, suggest output location
- Forbidden MCP calls (`get_design_context`, `get_screenshot`, `get_variable_defs`) must never happen during pre-flight
- No codebase exploration for conventions, tokens, or patterns — only Glob for component directories and read `package.json` for framework detection
- Present results to user with a confirmation prompt before dispatching the subagent
- Keep the implementer subagent prompt unchanged — it works correctly

## Constraints

- Figma MCP server must be connected (`get_metadata`, `get_code_connect_map` are the only tools used)
- Figma MCP rate limit: 15 requests/minute
- Component must be a COMPONENT or COMPONENT_SET
- All child component dependencies must exist in codebase before implementation

## Chosen Approach: Aggressive Simplification

Flatten the 8-gate pipeline into 3 linear phases. Cut prompt length by ~60%. Put the forbidden-actions blocklist at the very top in an unmissable position.

### Why not reinforce existing structure?

The LLM ignores rules proportional to prompt length. Adding more guardrails to a 280-line prompt makes it longer, not more compliant. Shorter prompt = higher compliance.

## Architecture

### File Structure (unchanged)

```
skills/component/
├── SKILL.md                          # Orchestration skill (simplified)
└── component-implementer-prompt.md   # Subagent prompt (unchanged)
```

### New SKILL.md Structure

**Top of file: 3-line blocklist** (before anything else)
```
NEVER call get_design_context, get_screenshot, or get_variable_defs.
NEVER launch Explore agents or scan the codebase for conventions/tokens/patterns.
NEVER run phases in parallel — execute them sequentially, one at a time.
```

**Phase 1 — Parse & Validate (no codebase access)**

1. Extract `fileKey` and `nodeId` from URL (ask if missing)
2. Verify all 5 Figma MCP tools are available
3. Call `get_metadata(fileKey, nodeId)` — confirm COMPONENT or COMPONENT_SET. **Store the full response — it is reused in Phase 2 for dependency detection. Do NOT make additional MCP calls.**
4. Call `get_code_connect_map(fileKey, nodeId)` — check for existing implementation (hard stop if exists). **Store the full response — it is reused in Phase 2 for dependency cross-referencing. Do NOT call this again.**

**Phase 2 — Dependencies & Location (limited codebase access)**

1. From the **stored metadata response** (Phase 1, step 3), recursively scan descendant nodes for INSTANCE types with `componentId` references. No additional MCP calls needed.
2. Cross-reference each `componentId` against the **stored Code Connect map** (Phase 1, step 4). No additional MCP calls needed.
3. Hard stop if any dependencies are missing — list them
4. Glob for component directories: `src/components/**`, `src/ui/**`, `components/**`, `lib/components/**`, `packages/*/src/components/**`
5. Detect framework from `package.json` dependencies and config files (`next.config.*`, `nuxt.config.*`, `vite.config.*`)
6. Glob for `.storybook/` and `*.stories.*`

**Phase 3 — Present & Confirm**

Show summary:
```
## Pre-flight Results

- **Component:** <name> (<COMPONENT | COMPONENT_SET>)
- **Variants:** <count> — <list> (if COMPONENT_SET)
- **Dependencies:** All found | Missing: <list>
- **Suggested directory:** <path> (override? provide a different path)
- **Framework:** <detected> (override? specify a different framework)
- **Storybook:** detected — generate story file? (yes/no) | not detected
- **Code Connect:** No existing mapping

Ready to implement this component?
```

The user can:
- Confirm everything and proceed to dispatch
- Override the suggested directory by providing a different path
- Override the detected framework
- Accept or decline Storybook story generation (only asked if Storybook is detected)
- Decline to stop entirely

### Gates Removed vs Kept

| Current Gate | Status | Reason |
|---|---|---|
| Gate 1 — URL Parsing | **Kept** (Phase 1, step 1) | Essential |
| Gate 2 — MCP Availability | **Kept** (Phase 1, step 2) | Essential |
| Gate 3 — Node Type | **Kept** (Phase 1, step 3) | Essential |
| Gate 4 — Variant Structure | **Removed** | Low value — ungrouped variants are rare and this gate requires an extra MCP call on the parent node. If variants are ungrouped, the subagent can still handle single components. |
| Gate 5 — Code Connect Dedup | **Kept** (Phase 1, step 4) | Essential — prevents duplicate work |
| Gate 6 — Dependency Detection | **Kept** (Phase 2, steps 1-3) | Core requirement from user |
| Gate 7 — Output Location | **Kept** (Phase 2, steps 4-5) | Core requirement from user |
| Gate 8 — Storybook Detection | **Kept** (Phase 2, step 6) | User wants to keep it |

### Trigger Conditions (kept from current skill)

- **Explicit:** User invokes `/afyapowers:component`
- **Implicit:** User asks to implement/build/create/develop a Figma component — detected via keywords ("implement", "build", "create", "develop") combined with "component" and a Figma URL or reference. All three conditions must be present.

### YAML Frontmatter (kept from current skill)

```yaml
---
name: component
description: Develop Figma components with strict validation, Code Connect dedup, and autonomous implementation. Standalone — not part of the 5-phase workflow.
metadata:
  mcp-server: figma
---
```

### Dispatch

After user confirms, dispatch the implementer subagent **using the Agent tool** with the `component-implementer-prompt.md` template, filling in placeholders:
- `[FILE_KEY]`, `[NODE_ID]`, `[NODE_TYPE]`, `[VARIANT_LIST]`, `[OUTPUT_DIRECTORY]`, `[FRAMEWORK]`, `[GENERATE_STORYBOOK]`, `[COMPONENT_NAME]`

### After the Subagent Returns

- **If DONE:** Commit all created files and report success to the user.
- **If BLOCKED:** Relay the block reason using the standard stopped format.

### Error Handling (unchanged format)

```
**STOPPED** — [Phase]: [Clear reason]

**What to do:** [Actionable instruction]
```

## Key Files to Modify

- `skills/component/SKILL.md` — rewrite with simplified 3-phase structure
- `commands/component.md` — update documentation to match new structure

## Files NOT Modified

- `skills/component/component-implementer-prompt.md` — works correctly, no changes

## Verification

1. Invoke `/afyapowers:component` with a Figma URL
2. Verify: NO `get_design_context` calls appear in the output
3. Verify: NO Explore agents are launched
4. Verify: Gates run sequentially (Phase 1 completes before Phase 2)
5. Verify: Only `get_metadata` and `get_code_connect_map` MCP calls are made
6. Verify: Summary is presented and user is asked to confirm before dispatch
7. Verify: If user confirms, subagent is dispatched with correct context
