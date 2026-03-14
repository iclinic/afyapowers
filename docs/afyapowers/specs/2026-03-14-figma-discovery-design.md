# Figma Discovery Design

## Overview

Add a standalone Figma discovery skill that identifies and maps Figma node references during the Design phase, so that implementation subagents can fetch visual details from Figma MCP tools when building UI components.

The approach: a dedicated skill handles the interactive discovery flow (ask, collect URLs, discover nodes, confirm). The confirmed references are persisted in the design spec. Downstream skills (writing-plans, implementer) consume these references through small instruction updates — no new skill modes needed.

## Problem Statement

When implementing front-end features, subagents need visual context from Figma designs to match layout, structure, and intent. Currently there is no mechanism to ask whether Figma layouts exist, discover relevant node IDs, or carry those references through the planning and implementation pipeline.

Without this, subagents either lack visual context entirely or require ad-hoc manual instructions per task.

## Requirements

- Ask the user whether Figma layouts are available during the Design phase
- Accept one or more Figma URLs (file, page, or frame level)
- Use Figma MCP tools to discover top-level frames/nodes under each URL
- Present discovered nodes for user confirmation and labeling
- Persist confirmed references in the design spec (`## Figma References` section)
- Enable the planner to assign Figma nodes to tasks via a `**Figma:**` section
- Enable implementation subagents to call Figma MCP tools for referenced nodes before writing code
- Be agnostic to which Figma MCP server is configured (multiple servers exist)

## Constraints

- The discovery skill does NOT extract tokens, spacing, colors, or visual details — it only builds the reference map
- Each implementation subagent does its own Figma MCP calls to fetch visual details at implementation time
- The skill must work with any Figma MCP server (tool-name agnostic)
- The Figma inquiry only happens for features that involve front-end/UI work

## Approaches Considered

### Approach A: Fully Interactive Discovery

Single skill handles everything in the Design session: ask, collect, discover, confirm, write to spec. Downstream concerns (task mapping, subagent consumption) handled by updating existing skill prompts.

**Trade-off:** Simple, minimal new files. But downstream guidance lives in 3 places.

### Approach B: Two-Phase Skill (Discovery + Mapping)

Skill has two modes — discovery (Design phase) and mapping (Plan phase). Mapping mode reads the Figma References section and guides the planner through assigning nodes to tasks.

**Trade-off:** More encapsulated, but the mapping step is simple enough that a few lines in the writing-plans skill suffice. Adds unnecessary complexity.

### Approach C: Discovery Skill + Prompt Updates

Standalone skill handles only discovery (the complex part). Simple downstream concerns — task mapping during planning, node consumption during implementation — are handled by small instruction additions to existing skills.

**Trade-off:** Figma logic lives in 3 places, but each piece is minimal and appropriately scoped. The skill stays focused and isolated.

## Chosen Approach

**Approach C: Discovery Skill + Prompt Updates.**

The discovery flow is the only genuinely complex part — it involves user interaction, MCP tool calls, and node selection. Planning and implementation steps are straightforward "read this section, act on it" instructions that fit naturally into existing prompts. This keeps the skill isolated (easier to evolve independently) while avoiding over-engineering downstream.

## Architecture

### Component 1: Figma Discovery Skill (`skills/figma-discovery/SKILL.md`)

A standalone skill invoked late in the Design phase, after the design is shaped but before writing the spec document.

**Flow:**

1. **Ask:** "Do you have Figma layouts for this feature?"
   - If **no** → skill exits, design continues normally
   - If **yes** → proceed to step 2

2. **Collect URLs:** Ask the user to paste one or more Figma URLs (file, page, or frame-level links)

3. **Discover nodes:** For each URL, use available Figma MCP tools to fetch the node/frame tree. The skill instructs the agent to inspect what Figma MCP tools are available in the environment and use them to list frames/components under the provided URLs. No specific tool names are hardcoded.

4. **Present for confirmation:** Display discovered nodes in a structured list with names and IDs. Ask the user to:
   - Confirm which nodes are relevant to this feature
   - Optionally add descriptions/labels to each node

5. **Write to spec:** Append a `## Figma References` section to the design.md artifact:

```markdown
## Figma References
- `https://figma.com/file/abc123?node-id=12:34` — Login form
- `https://figma.com/file/abc123?node-id=12:56` — Error states
- `https://figma.com/file/abc123?node-id=12:78` — Dashboard overview
```

### Component 2: Design Skill Integration

A small addition to `skills/design/SKILL.md`:

- After the design conversation has shaped the architecture and components, but before writing the spec document, the Design skill checks whether the feature involves front-end/UI work
- If it does → invoke the Figma discovery skill
- If it doesn't → skip entirely
- The Design skill does not ask about Figma itself — it delegates entirely to the Figma discovery skill

### Component 3: Writing-Plans Instruction Update

A small instruction block added to `skills/writing-plans/SKILL.md`:

> If the design spec contains a `## Figma References` section, assign relevant Figma nodes to tasks using a `**Figma:**` section. Each task that involves implementing a UI element with a corresponding Figma reference should include it. Tasks with no relevant Figma nodes omit the section entirely.

Resulting task format:

```markdown
### Task 3: Login Screen
**Files:**
- Create: `src/components/LoginScreen.tsx`
- Test: `src/components/__tests__/LoginScreen.test.tsx`
**Depends on:** Task 1, Task 2
**Figma:**
- `https://figma.com/file/abc123?node-id=12:34` — Login form
- `https://figma.com/file/abc123?node-id=12:56` — Error states
```

The `**Figma:**` section is treated like `**Files:**` and `**Depends on:**` — metadata the planner curates per task.

### Component 4: Implementer Prompt Update

A small instruction block added to `skills/implementing/implementer-prompt.md`:

> If your assigned task has a `**Figma:**` section, use the available Figma MCP tools to fetch visual details for those specific nodes before writing code. Inspect the available Figma MCP tools in your environment and use them to retrieve layout, component structure, and visual specs for the referenced node IDs. Use this information to guide your implementation — matching the design's structure, hierarchy, and visual intent.

Key behaviors:
- Agnostic to which Figma MCP server is configured — subagent discovers available tools at runtime
- Fetches details only for node IDs listed in its task, not the whole file
- If no `**Figma:**` section exists, proceeds normally without Figma calls
- If Figma MCP tools are unavailable or calls fail, the subagent proceeds without visual context but must include a `**Figma Status: unable to access Figma MCP**` note in its task completion output. The orchestrator should surface this when marking the task done, so it's visible that the task was implemented without Figma reference

## Data Flow

```
Design phase
  → Design skill detects UI work
  → Invokes Figma discovery skill
  → User provides Figma URLs
  → Skill calls Figma MCP to discover nodes
  → User confirms relevant nodes
  → Confirmed nodes written to design.md ## Figma References
                    ↓
Plan phase
  → Writing-plans skill reads design.md
  → Planner assigns Figma nodes to tasks via **Figma:** section
  → Each task in plan.md has its relevant node references
                    ↓
Implement phase
  → Subagent receives task with **Figma:** section
  → Subagent calls Figma MCP tools for listed node IDs
  → Subagent uses visual details to guide implementation
```

## Error Handling

| Scenario | Behavior |
|---|---|
| Figma MCP tools not available | Skill warns user that no Figma MCP tools were found in the environment. Exits gracefully — design continues without Figma references. |
| Figma URL is invalid or inaccessible | Skill reports the error for that specific URL and asks user to provide a corrected URL or skip it. Other URLs continue processing. |
| MCP call returns no nodes | Skill informs user that no frames/components were found under the URL. Asks if the URL is correct or if they want to skip it. |
| User confirms zero nodes | Skill exits — no `## Figma References` section is written. Design continues normally. |
| Subagent can't access Figma MCP during implementation | Subagent proceeds without visual context and includes `**Figma Status: unable to access Figma MCP**` in its task completion output. The orchestrator surfaces this when marking the task done, making it visible that the task was implemented without Figma reference. Implementation is not blocked. |

## Testing Strategy

This feature is entirely prompt/skill-based (no runtime code). Validation is manual:

- Verify the Figma discovery skill correctly asks, collects, discovers, and writes references
- Verify the writing-plans skill picks up Figma references and the planner assigns them to tasks
- Verify implementation subagents call Figma MCP tools when `**Figma:**` section is present
- Verify graceful degradation when Figma MCP tools are unavailable

## Changes to Existing Files

### Modified Files

1. **`skills/design/SKILL.md`** — Add step to invoke figma-discovery skill for UI features, late in design phase
2. **`skills/writing-plans/SKILL.md`** — Add instruction for planner to use `**Figma:**` section when Figma references exist in spec
3. **`skills/implementing/implementer-prompt.md`** — Add instruction for subagents to call Figma MCP tools when task has `**Figma:**` section

### New Files

1. **`skills/figma-discovery/SKILL.md`** — The standalone Figma discovery skill

### Unchanged Files

- `skills/implementing/SKILL.md` — Still just invokes SDD
- `skills/subagent-driven-development/SKILL.md` — No changes (tasks with `**Figma:**` are just tasks with extra metadata)
- `skills/implementing/spec-reviewer-prompt.md` — No changes
- `skills/implementing/code-quality-reviewer-prompt.md` — No changes
- `templates/plan.md` — No structural changes (the `**Figma:**` field is optional, not part of the template)

## Design Decisions

1. **Standalone skill over integrated steps** — The Figma discovery flow is complex enough to warrant isolation, and the user wants the flexibility to evolve it independently.
2. **Tool-name agnostic** — Multiple Figma MCP servers exist with different tool names. The skill instructs agents to discover available tools at runtime rather than hardcoding names.
3. **No token/style extraction during discovery** — Discovery builds only the reference map (URLs + node IDs). Each subagent fetches its own visual details at implementation time, keeping the discovery skill simple and the visual data fresh.
4. **Late Design phase invocation** — Asking about Figma after the design is shaped (not before) means the user has better context to identify which frames are relevant.
5. **Spec-embedded persistence** — Confirmed Figma references live in the design.md `## Figma References` section rather than a separate file. The spec is the single source of truth flowing into planning.
6. **Optional per-task** — The `**Figma:**` section is only added to tasks with relevant Figma nodes. Backend or infrastructure tasks simply omit it.

## Open Questions

None — all questions resolved during design discussion.
