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

### Token Mapping Rule

When translating Figma tokens to project code:

1. **Name match + value match:** If a Figma variable name matches a project design system token by name AND their resolved values are identical, use the project token.
2. **Name match + value mismatch:** If a Figma variable name matches a project token by name BUT the values differ, use the exact Figma value hardcoded. Figma is the source of truth.
3. **No name match:** If no project token matches the Figma variable name, use the exact Figma value hardcoded.

**Never** approximate or use a "closest" project token. It is either an exact match (name + value) or a hardcoded Figma value.

### Updated Step 4: Translate to Project Conventions

Remove Tailwind-specific language. The key principle becomes:

> Map Figma variable names from Step 1b to project design system tokens by name. Verify that matched tokens have identical values. If no matching token exists or values differ, use the exact Figma value hardcoded. Never approximate with a "close enough" project token.

### Updated Step 5: Achieve Visual Parity

Replace the optional `get_variable_defs` guidance with mandatory usage:

> All visual property values must come from `get_variable_defs` (Step 1b). When a Figma variable name matches a project token and their values match, use the project token. When a Figma variable name matches a project token but the values differ, use the exact Figma value hardcoded (Figma is the source of truth). When no matching project token exists by name, use the exact Figma value hardcoded. Do not use approximate tokens. Do not use values from `get_design_context`.

### Updated Common Issues

Replace the "Design token values differ from project" entry:

> If a Figma variable has no matching project token by name, or the matched token has a different value, use the exact Figma value hardcoded. Do not substitute approximate project tokens.

## Design Principles

1. **Framework-agnostic:** The skill makes no assumptions about the project's styling framework. No Tailwind-specific language.
2. **Figma is the visual source of truth:** When in doubt, the Figma value wins over project token values.
3. **Exact or hardcoded, never approximate:** Token matching is strict name + value. Any mismatch falls through to hardcoded Figma values.
4. **Separation of concerns:** `get_design_context` owns structure/behavior. `get_variable_defs` owns visual tokens. No overlap.
5. **Token extraction at task level:** Tokens are fetched per-node during implementation, not pre-extracted during discovery or design phases.
