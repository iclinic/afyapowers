# Figma Token Authority: `get_variable_defs` as Source of Truth

## Problem

The `get_design_context` MCP tool returns Tailwind-biased implementation suggestions for all visual properties (colors, typography, spacing, borders, shadows, etc.). When the project uses a different styling framework, these suggestions cause visual discrepancies in the implemented UI.

Without `get_variable_defs` as a reference, the implementer has no way to verify the values behind the token names used in `get_design_context` output and blindly trusts the framework-biased implementation suggestions.

## Solution

Split Step 1 of the `implement-figma-design.md` implementer subagent prompt into two explicit sub-steps. `get_variable_defs` is called **first** to build an authoritative token reference table, then `get_design_context` is called and its token names are cross-referenced against that table:

- `get_variable_defs` (first) — build the authoritative token name → value lookup table
- `get_design_context` (second) — use for structure, behavior, AND implementation suggestions, but cross-reference all token names against the lookup table from Step 1a

## Scope

**Only** `skills/implementing/implement-figma-design.md` is modified.

**Not changed:**
- `skills/figma-discovery/SKILL.md` — discovery remains lightweight and structural
- `skills/design/SKILL.md` — design phase does not extract tokens
- `templates/design.md` — no token information added
- `templates/figma-component-mapping.md` — no token information added

## Detailed Changes

### Step 1a: Fetch Authoritative Design Tokens

Call `get_variable_defs` for each node ID **first**. This builds the authoritative token reference table — a mapping of token names to their actual values:

- Colors (fill, stroke, background, text)
- Typography (font family, size, weight, line height)
- Spacing (padding, margin, gap)
- Border radius
- Shadows
- Opacity

This lookup table is used in Step 1b to validate token names from `get_design_context`.

### Step 1b: Fetch Design Context with Token Cross-Reference

Call `get_design_context` for each node ID. This provides:

- Component hierarchy and children ordering
- Auto-layout direction and mode
- Constraints and sizing modes (fixed/hug/fill)
- Variants and interactive states (hover, active, disabled, focus)
- Component props and slot/composition patterns
- Implementation suggestions with token names

**Cross-reference all token names** from `get_design_context` against the lookup table from Step 1a. For each token name in the implementation suggestions, apply the Token Mapping Rule below to determine the correct value to use.

**Fallback when `get_variable_defs` returns no tokens for a node:** Use the raw resolved values from `get_design_context` and report the affected properties as DONE_WITH_CONCERNS so they can be verified in the review phase.

### Token Mapping Rule

When translating Figma tokens to project code:

1. **Name match + value match:** If a Figma variable name matches a project design system token by name AND their resolved values are identical, use the project token.
2. **Name match + value mismatch:** If a Figma variable name matches a project token by name BUT the values differ, use the exact Figma value hardcoded. Figma is the source of truth.
3. **No name match:** If no project token matches the Figma variable name, use the exact Figma value hardcoded.

**Never** approximate or use a "closest" project token. It is either an exact match (name + value) or a hardcoded Figma value.

### Updated Step 4: Translate to Project Conventions

Replace the entire "Key principles" list and "Design System Integration" subsection. Remove Tailwind-specific language (e.g., "Replace Tailwind utility classes..."). The updated section:

**Key principles:**
- Use the `get_design_context` implementation suggestions as a starting point, but cross-reference all token names against the `get_variable_defs` lookup table (Step 1a)
- Map Figma variable names from Step 1a to project design system tokens by name; verify values match before using the project token
- If no matching token exists or values differ, use the exact Figma value hardcoded — never approximate with a "close enough" project token
- Reuse existing components (buttons, inputs, typography, icon wrappers) instead of duplicating functionality
- Respect existing routing, state management, and data-fetch patterns

**Design System Integration:**
- ALWAYS use components from the project's design system when possible
- Map Figma variable names to project design tokens using the Token Mapping Rule (Step 1a)
- When a matching component exists, extend it rather than creating a new one
- Document any new components added to the design system

### Updated Step 5: Achieve Visual Parity

Replace the **entire** "Guidelines" list in Step 5. The current guidance contains conflicting rules (e.g., "prefer design system tokens" and "adjust minimally") that contradict the token authority model. The full replacement:

**Guidelines:**
- Prioritize Figma fidelity to match designs exactly
- All visual property values must be validated against `get_variable_defs` (Step 1a) — this is mandatory, not optional
- When a Figma variable name matches a project token **and their values are identical**, use the project token
- When a Figma variable name matches a project token **but the values differ**, use the exact Figma value hardcoded (Figma is the source of truth)
- When no matching project token exists by name, use the exact Figma value hardcoded
- Do not use approximate tokens. Always cross-reference token names from `get_design_context` against `get_variable_defs`
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
4. **Separation of concerns:** `get_variable_defs` owns authoritative token values. `get_design_context` provides structure, behavior, and implementation suggestions whose token names are validated against `get_variable_defs`.
5. **Token extraction at task level:** Tokens are fetched per-node during implementation, not pre-extracted during discovery or design phases.
