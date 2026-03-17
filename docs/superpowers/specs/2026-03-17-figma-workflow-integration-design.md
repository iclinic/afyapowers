# Design: Figma Workflow Integration

## Problem Statement

The afyapowers workflow currently has no support for Figma-driven UI implementation. When features involve frontend/UI work with Figma designs, the workflow treats them identically to backend or logic-heavy features — using TDD cycles and code snippets in plans. This leads to:

- No structured way to capture Figma design data during the design phase
- No mapping between Figma nodes and implementation tasks during planning
- Implementer subagents have no Figma-specific workflow — they follow TDD instead of a design-first visual fidelity approach

The goal is to add conditional Figma support across the design, planning, and implementation phases while keeping the existing workflow intact for non-Figma tasks.

## Requirements

1. **Design phase** must detect when a feature involves UI/frontend work and ask the user for Figma URLs
2. **Design phase** must use Figma MCP tools to crawl the Figma file and build a structural node map with breakpoints
3. **Design artifact** must include an optional `## Figma Resources` section with file info, breakpoints, and hierarchical node map
4. **Planning phase** must produce Figma-specific task formats for tasks that map to Figma nodes — no TDD, no code snippets, design-workflow steps instead
5. **Planning phase** must allow mixed plans where Figma and non-Figma tasks coexist with standard dependency handling
6. **SDD orchestrator** must route to the correct implementer prompt based on whether a task has Figma resources
7. **Figma implementer prompt** must follow the official Figma implement-design workflow (fetch context → screenshot → assets → translate → visual parity → validate), adapted to task-level execution
8. **Figma implementer** must NOT use TDD — focus is on design implementation and visual validation against Figma
9. **Review pipeline** (spec compliance + code quality) remains unchanged — reviews Figma task output the same as any other
10. **Non-Figma tasks** must be completely unaffected by these changes

## Constraints

- Figma MCP server must be available (remote mode) for Figma discovery and implementation
- Design phase Figma discovery uses `get_metadata` (structural) for all nodes and `get_design_context` only for top-level frames (to discover breakpoints and layout patterns) — keeps the phase lightweight
- Design tokens are NOT extracted during design phase — deferred to implementation time via `get_variable_defs`
- Asset URLs come from the remote Figma MCP server — no localhost assumption

## Approaches Considered

### Approach 1: Conditional Steps in Existing Skills (Recommended)

Add conditional Figma behavior to the existing design, writing-plans, and SDD skills. Create a new Figma implementer prompt template. No new phases or workflow stages.

**Trade-offs:**
- (+) Minimal structural change — extends existing skills
- (+) Mixed plans (Figma + non-Figma tasks) work naturally
- (+) Existing review pipeline works unchanged
- (-) Skills get slightly longer with conditional sections

### Approach 2: Separate Figma-Specific Phase Pipeline

Create parallel Figma-specific versions of design, plan, and implement skills that activate when a feature is Figma-driven.

**Trade-offs:**
- (+) Clean separation, no conditionals
- (-) Duplication of shared logic (phase gates, review loops, SDD algorithm)
- (-) Can't handle mixed features (some tasks Figma, some not) without switching between pipelines
- (-) Maintenance burden of keeping two pipelines in sync

### Approach 3: Post-Planning Figma Enrichment

Keep design and planning unchanged. Add a post-planning step that scans the plan, identifies UI tasks, and enriches them with Figma data.

**Trade-offs:**
- (+) Zero changes to existing skills
- (-) Figma context doesn't inform design decisions (breakpoints, component decomposition)
- (-) Extra phase adds friction
- (-) Harder to get the node-to-task mapping right retroactively

## Chosen Approach

**Approach 1: Conditional Steps in Existing Skills.** It's the simplest path that keeps the workflow unified while supporting both Figma and non-Figma tasks in the same plan. The Figma context informs design and planning decisions naturally, and the prompt routing in SDD is a clean detection mechanism.

## Architecture

### Design Phase (modified)

After the initial clarifying questions, if the feature involves UI/frontend work:

1. Ask: "Does this feature have Figma designs? If so, please share the Figma URL(s)."
2. If user provides URL(s):
   - Parse file key and node ID(s) from each URL
   - Run `get_metadata` on each URL to get the full node tree (pages, frames, components with IDs, names, types, positions, sizes)
   - Run `get_design_context` on top-level frames only — to discover breakpoints and overall layout patterns
   - Build the `## Figma Resources` section in the design doc
3. If no Figma designs → proceed normally, no Figma section

The Figma discovery happens after clarifying questions but before proposing approaches — so the structural understanding of the Figma file informs the architecture discussion.

### Planning Phase (modified)

When decomposing the design into tasks, the planner checks if the component being implemented has corresponding nodes in the `## Figma Resources` section.

**For Figma tasks:**
- Add a `**Figma:**` block with file key, relevant breakpoints, and nodes table
- Steps follow the implement-design workflow: fetch context → screenshot → assets → translate → visual parity → validate → commit
- No code snippets — steps describe what to achieve
- No TDD cycle

**For non-Figma tasks:**
- Standard task structure unchanged — TDD, code snippets, red-green-refactor

Both task types coexist in the same plan with standard dependency handling.

### SDD Orchestrator (modified)

When dispatching a task, the orchestrator checks for a `**Figma:**` section in the task text:

- **Has `**Figma:**`** → use `skills/implementing/implement-figma-design.md` prompt template. Paste the Figma metadata (file key, nodes table, breakpoints) into the agent context.
- **No `**Figma:**`** → use `skills/implementing/implementer-prompt.md` (existing, unchanged)

The wave execution algorithm, concurrency limits, file overlap validation, dependency resolution, and review pipeline are all unchanged.

### Figma Implementer Prompt (new)

A new prompt template at `skills/implementing/implement-figma-design.md`, heavily based on the official Figma implement-design skill (`figma-implement-design-example.md`), adapted to run at task level.

**Workflow:**
1. **Get Node IDs** — from the task's `**Figma:**` section (already provided, no URL parsing needed)
2. **Fetch Design Context** — `get_design_context` for all task nodes. If response is too large/truncated, use `get_metadata` to identify children and fetch individually.
3. **Capture Visual Reference** — `get_screenshot` for the task's root node(s). Keep accessible throughout implementation.
4. **Download Required Assets** — images, icons, SVGs returned by the Figma MCP server. Use asset URLs exactly as returned. Do NOT import new icon packages. Do NOT create placeholders if a source URL is provided.
5. **Translate to Project Conventions** — Treat Figma MCP output as a representation of design intent, not final code. Replace utility classes with project's design system tokens. Reuse existing components. Follow project's routing, state management, and data-fetch patterns.
6. **Achieve 1:1 Visual Parity** — Pixel-perfect matching across all specified breakpoints. Use design tokens from Figma where available. When project tokens differ from Figma values, prefer project tokens but adjust to maintain visual fidelity.
7. **Validate Against Figma** — Compare against screenshot. Checklist: layout (spacing, alignment, sizing), typography (font, size, weight, line height), colors, interactive states (hover, active, disabled), responsive behavior across all breakpoints, assets render correctly, accessibility standards met.

**Self-review** focuses on: visual fidelity, design system integration, asset handling, responsive correctness — not TDD discipline.

**Same escalation model:** DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED.

## Data Flow

```
User provides Figma URL(s)
        │
        ▼
[Design Phase] ──get_metadata──► Node tree (IDs, names, types, positions)
        │       ──get_design_context──► Top-level frame analysis (breakpoints, layout)
        │
        ▼
design.md ## Figma Resources
  ├── File info (URL, file key)
  ├── Breakpoints (discovered from top-level frames)
  └── Node Map (hierarchical: page → section → component)
        │
        ▼
[Planning Phase] ── maps nodes to tasks
        │
        ▼
plan.md tasks with **Figma:** sections
  ├── File key
  ├── Relevant breakpoints
  └── Nodes table (ID, name, type, parent)
        │
        ▼
[SDD Orchestrator] ── detects **Figma:** → routes to Figma implementer prompt
        │
        ▼
[Figma Implementer Subagent]
  ├── get_design_context (per node)
  ├── get_screenshot (visual reference)
  ├── get_variable_defs (design tokens, at implementation time)
  ├── Implement with visual parity
  └── Validate against screenshot
        │
        ▼
[Review Pipeline] ── spec compliance → code quality (unchanged)
```

## API / Interface Changes

### Design Template (`templates/design.md`)

New optional section appended:

```markdown
## Figma Resources
<!-- Only included when feature has Figma designs -->

**File:** `<figma_url>`
**File Key:** `<file_key>`

### Breakpoints
<!-- Discovered from top-level frame analysis via get_design_context -->
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

### Node Map
<!-- Hierarchical structure from get_metadata -->

#### Page: <page_name>
- **<section_name>** (node `<node_id>`, <type>, <width>x<height>)
  - <component_name> (node `<node_id>`, <type>)
```

### Plan Template (`templates/plan.md`)

New Figma task format alongside existing format:

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/component`
**Depends on:** none | Task X

**Figma:**
- **File Key:** `<file_key>`
- **Breakpoints:** <breakpoint> (<width>px), ...
- **Nodes:**
  | Node ID | Name | Type | Parent |
  |---------|------|------|--------|
  | `<id>` | <name> | <type> | <parent> |

- [ ] Step 1: Fetch design context for all task nodes
- [ ] Step 2: Capture screenshot for visual reference
- [ ] Step 3: Download required assets
- [ ] Step 4: Translate to project conventions
- [ ] Step 5: Achieve 1:1 visual parity across all breakpoints
- [ ] Step 6: Validate against Figma screenshot
- [ ] Step 7: Commit
```

### SDD Prompt Routing

Detection logic added to `skills/subagent-driven-development/SKILL.md`:

```
When dispatching a task:
  IF task text contains **Figma:** section
    → use skills/implementing/implement-figma-design.md prompt
  ELSE
    → use skills/implementing/implementer-prompt.md prompt
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Figma MCP server unavailable during design | Warn user, suggest checking MCP server connection. Cannot proceed with Figma discovery without it. |
| `get_metadata` returns truncated data | Fetch page-level metadata first, then drill into individual sections |
| `get_design_context` too large for a node | Use `get_metadata` to identify children, fetch individually |
| Figma URL format unrecognized | Ask user to provide URL in standard format: `https://figma.com/design/:fileKey/:fileName?node-id=X-Y` |
| Asset URLs inaccessible at implementation time | Report as DONE_WITH_CONCERNS, note which assets couldn't be downloaded |
| No Figma MCP tools available to implementer subagent | Report as BLOCKED — Figma MCP server required for Figma tasks |
| Design/project token conflict | Prefer project tokens, adjust spacing/sizing minimally to maintain visual fidelity |

## Testing Strategy

- Manual validation: run a Figma-driven feature through the full workflow (design → plan → implement → review)
- Verify non-Figma features are completely unaffected
- Verify mixed plans (Figma + non-Figma tasks) execute correctly with proper prompt routing
- Verify Figma discovery produces accurate node maps by comparing with Figma file structure

## Dependencies

- Figma MCP server (remote mode) must be configured and accessible
- Figma MCP tools required: `get_metadata`, `get_design_context`, `get_screenshot`, `get_variable_defs`

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `skills/design/SKILL.md` | Modify | Add conditional Figma discovery step after clarifying questions |
| `templates/design.md` | Modify | Add optional `## Figma Resources` section |
| `skills/writing-plans/SKILL.md` | Modify | Add Figma task format alongside existing TDD format |
| `templates/plan.md` | Modify | Add Figma task example template |
| `skills/subagent-driven-development/SKILL.md` | Modify | Add prompt routing logic for Figma vs standard tasks |
| `skills/implementing/implement-figma-design.md` | Create | Figma implementer prompt — based on official skill, adapted to task-level |

## Open Questions

None — all decisions resolved during brainstorming.
