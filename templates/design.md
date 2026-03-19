# Design: {{feature_name}}

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
