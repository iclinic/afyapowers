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

## Component Reuse Decisions
<!-- Filled whenever the design reuses an existing codebase/DS component. One row per reuse. A
     component may be reused silently ONLY if it is an exact match on all three axes (Name + Layout +
     Behavior). Anything else requires the user's explicit approval before adopting it.
     Decision = "Exact match (auto)" or "Approved by user" or "Build custom (rejected)".
     Remove this section if no component is reused. -->

| Target (Figma node / requirement) | Candidate component | Name | Layout | Behavior | Decision |
|-----------------------------------|---------------------|------|--------|----------|----------|
<!-- e.g. | Specialty Chip (2:5471) | DropdownPicker (DS) | ✗ | ✗ | ✗ drawer vs popover | Build custom (rejected) | -->
<!-- e.g. | Submit Button (3:120)   | PrimaryButton (DS)  | ✓ | ✓ | ✓                   | Exact match (auto)     | -->

## Data Flow
<!-- How data moves through the system -->

## API / Interface Changes
<!-- New or modified interfaces -->

## Error Handling
<!-- Failure modes and how they're handled -->

## Edge Cases & States
<!-- Output of the Requirements Interrogation. One row per state/condition the feature must handle —
     empty, loading, error, zero/one/many, very-large, unauthorized, offline, boundary values, long
     text, etc. Confirmed with the user. Required for any stateful/UI feature. -->

| State / condition | Expected behavior |
|-------------------|-------------------|
<!-- e.g. | Empty list | Show "No quizzes yet" placeholder, hide filter | -->
<!-- e.g. | Request fails | Show retry banner; keep last good data if any | -->

## Assumptions & Risks
<!-- Output of the Requirements Interrogation. Every assumption the design depends on, with how it
     was confirmed. An unconfirmed BLOCKING assumption must be resolved before the design is written. -->

| Assumption | Confirmation | Risk if wrong |
|------------|--------------|---------------|
<!-- e.g. | GET /quiz/{id} returns {context, question, options[]} | Confirmed against homolog endpoint | Adapter + mocks wrong | -->

## Testing Strategy
<!-- What to test and how -->

## Dependencies
<!-- External dependencies or prerequisites -->

## Open Questions
<!-- Output of the Requirements Interrogation. Every item raised must end resolved or explicitly
     deferred — no BLOCKING row may be "open" when the design is written (REQUIREMENTS-GATE). -->

| Question | Severity | Status | Resolution |
|----------|----------|--------|------------|
<!-- e.g. | What makes the form valid? | blocking | resolved | All fields non-empty + email format | -->
<!-- e.g. | i18n for error copy? | non-blocking | deferred | Out of scope this iteration | -->

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

### Design Annotations
<!-- All Dev Mode annotations extracted via use_figma. One entry per annotated node, verbatim. Omit this subsection if none. -->
<!-- Annotations are requirements (business rules, behavior, animations, accessibility, dev instructions). Reflect them in the sections above too — business rules in Requirements. -->
<!-- Drop [<category>] if no Figma category; drop the "— pins:" clause if no pinned properties. -->
- node `<node_id>` (<node_name>) [<category>]: "<annotation label / note text>" — pins: <property types>
