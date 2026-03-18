# Figma Component Mapping: {{feature_name}}

## Scan Report

**File Key:** `<file_key>`
**File Type:** page | design-system
**Breakpoint Strategy:** multi-frame | single-responsive

### Breakpoints Detected
<!-- Only for page mode with multi-frame strategy -->
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

### Code Connect Mappings
<!-- Only if Code Connect is configured for this file -->
- <node_id> → <code_component_name> (<code_connect_src>)
<!-- If none: "No Code Connect mappings found." -->

## Component Mapping

### Strategy: multi-frame | single-responsive

### Components

#### N. <Component Name>
- **Type:** page-section | reusable-component | design-system-component
- **Description:** <what this component is and does visually>
- **Reusable:** yes (<N> instances) | no
- **Nodes by breakpoint:**
  | Breakpoint | Node ID | Size |
  |------------|---------|------|
  | <breakpoint> | `<node_id>` | <width>x<height> |
- **Children:**
  - <child_name> (<type>, node `<node_id>`)

<!-- For single responsive frame components, replace "Nodes by breakpoint" with: -->
<!-- - **Responsive strategy:** single-frame (auto-layout) -->
<!-- - **Node ID:** `<node_id>` -->
<!-- - **Size:** <width>x<height> (min-width: <min>px) -->
<!-- - **Note:** Responsive properties to be fetched at implementation time -->

<!-- For design-system-component, replace "Nodes by breakpoint" with: -->
<!-- - **Node ID:** `<node_id>` (ComponentSet) -->
<!-- - **Variants:** -->
<!--   | Variant | Node ID | -->
<!--   |---------|---------|  -->
<!--   | <variant_name> | `<node_id>` | -->
