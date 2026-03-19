# Figma Token Authority: `get_variable_defs` as Source of Truth

## Problem

The `get_design_context` MCP tool returns Tailwind-biased implementation suggestions for all visual properties (colors, typography, spacing, borders, shadows, etc.). When the project uses a different styling framework, these suggestions cause visual discrepancies in the implemented UI.

The tool conflates two distinct concerns:
1. **Component structure and behavior** — hierarchy, auto-layout, constraints, variants, interactive states (useful and framework-agnostic)
2. **Visual token values** — colors, fonts, spacing (unreliable, Tailwind-biased)

## Solution

Split Step 1 of the `implement-figma-design.md` implementer subagent prompt into two explicit sub-steps with clearly defined, non-overlapping roles:

- `get_design_context` — structure and behavior only
- `get_variable_defs` — authoritative source for all visual tokens

## Scope

**Only** `skills/implementing/implement-figma-design.md` is modified.

**Not changed:**
- `skills/figma-discovery/SKILL.md` — discovery remains lightweight and structural
- `skills/design/SKILL.md` — design phase does not extract tokens
- `templates/design.md` — no token information added
- `templates/figma-component-mapping.md` — no token information added

## Detailed Changes

### Step 1a: Fetch Component Structure & Behavior

Call `get_design_context` for each node ID. Extract **only**:

- Component hierarchy and children ordering
- Auto-layout direction and mode
- Constraints and sizing modes (fixed/hug/fill)
- Variants and interactive states (hover, active, disabled, focus)
- Component props and slot/composition patterns

**Explicitly ignore** all visual property values from this output — colors, font specifications, spacing values, border radii, shadows, opacity, etc. These are Tailwind-biased suggestions and must not be used for implementation.

### Step 1b: Fetch Authoritative Design Tokens

Call `get_variable_defs` for each node ID. This is the **single source of truth** for all visual properties:

- Colors (fill, stroke, background, text)
- Typography (font family, size, weight, line height)
- Spacing (padding, margin, gap)
- Border radius
- Shadows
- Opacity

**Fallback when `get_variable_defs` returns no tokens for a node:** Use the raw resolved values from `get_design_context` (the actual computed values, not the Tailwind class suggestions) and report the affected properties as DONE_WITH_CONCERNS so they can be verified in the review phase.

### Token Mapping Rule

When translating Figma tokens to project code:

1. **Name match + value match:** If a Figma variable name matches a project design system token by name AND their resolved values are identical, use the project token.
2. **Name match + value mismatch:** If a Figma variable name matches a project token by name BUT the values differ, use the exact Figma value hardcoded. Figma is the source of truth.
3. **No name match:** If no project token matches the Figma variable name, use the exact Figma value hardcoded.

**Never** approximate or use a "closest" project token. It is either an exact match (name + value) or a hardcoded Figma value.

### Updated Step 4: Translate to Project Conventions

Replace the entire "Key principles" list and "Design System Integration" subsection. Remove Tailwind-specific language (e.g., "Replace Tailwind utility classes..."). The updated section:

**Key principles:**
- Treat the `get_design_context` output as a representation of component structure and behavior, **not** as visual styling guidance
- Map Figma variable names from Step 1b to project design system tokens by name; verify values match before using the project token
- If no matching token exists or values differ, use the exact Figma value hardcoded — never approximate with a "close enough" project token
- Reuse existing components (buttons, inputs, typography, icon wrappers) instead of duplicating functionality
- Respect existing routing, state management, and data-fetch patterns

**Design System Integration:**
- ALWAYS use components from the project's design system when possible
- Map Figma variable names to project design tokens using the Token Mapping Rule (Step 1b)
- When a matching component exists, extend it rather than creating a new one
- Document any new components added to the design system

### Updated Step 5: Achieve Visual Parity

Replace the **entire** "Guidelines" list in Step 5. The current guidance contains conflicting rules (e.g., "prefer design system tokens" and "adjust minimally") that contradict the token authority model. The full replacement:

**Guidelines:**
- Prioritize Figma fidelity to match designs exactly
- All visual property values must come from `get_variable_defs` (Step 1b) — this is mandatory, not optional
- When a Figma variable name matches a project token **and their values are identical**, use the project token
- When a Figma variable name matches a project token **but the values differ**, use the exact Figma value hardcoded (Figma is the source of truth)
- When no matching project token exists by name, use the exact Figma value hardcoded
- Do not use approximate tokens. Do not use visual property values from `get_design_context`
- Follow WCAG requirements for accessibility
- Keep components composable and reusable
- Add TypeScript types for component props
- Avoid inline styles unless truly necessary for dynamic values

### Updated Common Issues

Replace the "Design token values differ from project" entry:

> **Issue: Figma token has no matching project token or values differ**
> **Cause:** Project design system tokens have different values than Figma specs, or no equivalent token exists.
> **Solution:** Use the exact Figma value hardcoded. Do not substitute approximate project tokens. Only use a project token when both name and value match exactly.

### Updated Self-Review Section

Replace the "Design System Integration" bullet (currently: "Are design tokens mapped correctly (project tokens over hardcoded values)?"):

> Are design tokens mapped correctly? (Figma variable names matched to project tokens by name; values verified to be identical; hardcoded Figma values used when no exact match exists)

### Clarification: Two Sources of Truth

The screenshot from Step 2 remains the source of truth for **visual validation** (does the layout look right?). `get_variable_defs` is the source of truth for **token values** (what exact color/font/spacing value to use). These are complementary, not competing: tokens tell you what values to code, the screenshot tells you if the result looks correct.

## Design Principles

1. **Framework-agnostic:** The skill makes no assumptions about the project's styling framework. No Tailwind-specific language.
2. **Figma is the visual source of truth:** When in doubt, the Figma value wins over project token values.
3. **Exact or hardcoded, never approximate:** Token matching is strict name + value. Any mismatch falls through to hardcoded Figma values.
4. **Separation of concerns:** `get_design_context` owns structure/behavior. `get_variable_defs` owns visual tokens. No overlap.
5. **Token extraction at task level:** Tokens are fetched per-node during implementation, not pre-extracted during discovery or design phases.
