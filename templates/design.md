# Design: {{feature_name}}

## JIRA Context
<!-- Only included when feature has a backing JIRA issue. Remove this section if not applicable. -->

**Issue:** [PROJ-123](https://your-site.atlassian.net/browse/PROJ-123)
**Type:** Story | Bug | Task | Epic
**Summary:** <!-- One-line summary from JIRA -->

### Requirements from JIRA
<!-- Key requirements extracted from the JIRA description and acceptance criteria -->
- ...

### Acceptance Criteria
<!-- Acceptance criteria from the JIRA issue, verbatim or lightly reformatted -->
- [ ] ...

### Linked Issues
<!-- Related JIRA issues: blockers, dependencies, related work -->
- Blocked by: PROJ-100 — ...
- Related to: PROJ-150 — ...

## Problem Statement
<!-- What problem are we solving and why -->

## Requirements
<!-- Key requirements discovered during design -->

## Constraints
<!-- Technical, business, or time constraints -->

## Approaches Considered
<!-- 2-3 approaches with trade-offs -->

### Approach 1: ...
### Approach 2: ...

## Chosen Approach
<!-- Which approach and why -->

## Architecture
<!-- Components, how they interact -->

## Data Flow
<!-- How data moves through the system -->

## API / Interface Changes
<!-- New or modified interfaces -->

## Error Handling
<!-- Failure modes and how they're handled -->

## Testing Strategy
<!-- What to test and how -->

## Dependencies
<!-- External dependencies or prerequisites -->

## Open Questions
<!-- Anything unresolved -->

## Figma Resources
<!-- Only included when feature has Figma designs. Remove this section if not applicable. -->
<!-- If the feature spans multiple Figma files, repeat the File/File Key/Node Map structure for each file. -->

**File:** `<figma_url>`
**File Key:** `<file_key>`

### Breakpoints
<!-- Inferred from top-level frame names and dimensions in the get_metadata response -->
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

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
