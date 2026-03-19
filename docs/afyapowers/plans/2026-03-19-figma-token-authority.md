# Figma Token Authority Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `get_variable_defs` the authoritative source for visual tokens in the Figma implementer subagent prompt, replacing Tailwind-biased suggestions from `get_design_context`.

**Architecture:** Single-file edit to `skills/implementing/implement-figma-design.md`. Split Step 1 into two sub-steps (structure vs tokens), update Steps 4 and 5, update Common Issues, update Self-Review.

**Tech Stack:** Markdown (prompt template)

**Spec:** `docs/afyapowers/specs/2026-03-19-figma-token-authority-design.md`

---

## Chunk 1: All Changes

All changes target `skills/implementing/implement-figma-design.md` (inside the ``` code block that forms the subagent prompt template).

### Task 1: Split Step 1 into Step 1a and Step 1b

**Files:**
- Modify: `skills/implementing/implement-figma-design.md:59-77`

- [ ] **Step 1: Replace Step 1 header and body**

Replace lines 59-77 (the entire "### Step 1: Fetch Design Context" section) with:

```markdown
    ### Step 1a: Fetch Component Structure & Behavior

    Run get_design_context for each node ID in your Figma Resources table.

        get_design_context(fileKey="<file_key>", nodeId="<node_id>")

    Extract **only** structural and behavioral data from this output:
    - Component hierarchy and children ordering
    - Auto-layout direction and mode (row/column, wrap, etc.)
    - Constraints and sizing modes (fixed/hug/fill)
    - Variants and interactive states (hover, active, disabled, focus)
    - Component props and slot/composition patterns

    **Explicitly ignore** all visual property values from this output — colors,
    font specifications, spacing values, border radii, shadows, opacity, etc.
    These are framework-biased suggestions and must not be used for implementation.
    Visual tokens come exclusively from Step 1b.

    **If the response is too large or truncated:**
    1. Run get_metadata(fileKey="<file_key>", nodeId="<node_id>") to get the
       high-level node map
    2. Identify the specific child nodes needed from the metadata
    3. Fetch individual child nodes with
       get_design_context(fileKey="<file_key>", nodeId="<child_node_id>")

    ### Step 1b: Fetch Authoritative Design Tokens

    Run get_variable_defs for each node ID in your Figma Resources table.

        get_variable_defs(fileKey="<file_key>", nodeId="<node_id>")

    This is the **single source of truth** for all visual properties:
    - Colors (fill, stroke, background, text)
    - Typography (font family, size, weight, line height)
    - Spacing (padding, margin, gap)
    - Border radius, shadows, opacity

    **Token Mapping Rule — apply this when translating tokens to project code:**
    1. **Name match + value match:** Figma variable name matches a project token
       by name AND their resolved values are identical → use the project token
    2. **Name match + value mismatch:** Figma variable name matches a project token
       by name BUT the values differ → use the exact Figma value hardcoded
       (Figma is the source of truth)
    3. **No name match:** No project token matches → use the exact Figma value
       hardcoded

    **Never** approximate or use a "closest" project token. It is either an exact
    match (name + value) or a hardcoded Figma value.

    **Fallback:** If get_variable_defs returns no tokens for a node, use the raw
    resolved values from get_design_context (the actual computed values, not the
    framework-specific class suggestions) and report the affected properties as
    DONE_WITH_CONCERNS so they can be verified in the review phase.
```

- [ ] **Step 2: Verify the edit**

Read lines 59-110 of the file to confirm the new Step 1a and Step 1b are correctly placed and the truncation fallback is preserved.

- [ ] **Step 3: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "feat(figma): split Step 1 into structure (1a) and tokens (1b)"
```

### Task 2: Update Step 2 visual reference clarification

**Files:**
- Modify: `skills/implementing/implement-figma-design.md:85` (line number will have shifted after Task 1)

- [ ] **Step 1: Update Step 2 source-of-truth language**

Find the line:
```
    This screenshot serves as the **source of truth** for visual validation. Keep it
```

Replace with:
```
    This screenshot serves as the **source of truth for visual validation** (does the
    layout look right?). Note: `get_variable_defs` from Step 1b is the source of truth
    for **token values** (what exact color/font/spacing value to use). These are
    complementary — tokens tell you what values to code, the screenshot tells you if
    the result looks correct. Keep the screenshot
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "feat(figma): clarify two sources of truth in Step 2"
```

### Task 3: Replace Step 4 — Translate to Project Conventions

**Files:**
- Modify: `skills/implementing/implement-figma-design.md:104-122` (line numbers shifted after Tasks 1-2)

- [ ] **Step 1: Replace Step 4 body**

Find and replace lines 104-122 (the entire Step 4 section body after the header). Replace from "Translate the Figma output..." through the end of "Design System Integration" subsection with:

```markdown
    Translate the Figma output into the project's framework, styles, and conventions.

    **Key principles:**
    - Treat the get_design_context output (Step 1a) as a representation of component
      structure and behavior, **not** as visual styling guidance
    - Map Figma variable names from Step 1b to project design system tokens by name;
      verify values match before using the project token (see Token Mapping Rule in
      Step 1b)
    - If no matching token exists or values differ, use the exact Figma value
      hardcoded — never approximate with a "close enough" project token
    - Reuse existing components (buttons, inputs, typography, icon wrappers) instead
      of duplicating functionality
    - Respect existing routing, state management, and data-fetch patterns

    **Design System Integration:**
    - ALWAYS use components from the project's design system when possible
    - Map Figma variable names to project design tokens using the Token Mapping Rule
      (Step 1b)
    - When a matching component exists, extend it rather than creating a new one
    - Document any new components added to the design system
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "feat(figma): update Step 4 with token mapping rule references"
```

### Task 4: Replace Step 5 Guidelines

**Files:**
- Modify: `skills/implementing/implement-figma-design.md:129-138` (line numbers shifted)

- [ ] **Step 1: Replace Step 5 Guidelines list**

Find and replace the entire "Guidelines:" list (from "- Prioritize Figma fidelity..." through "- Avoid inline styles...") with:

```markdown
    **Guidelines:**
    - Prioritize Figma fidelity to match designs exactly
    - All visual property values must come from get_variable_defs (Step 1b) — this
      is mandatory, not optional
    - When a Figma variable name matches a project token **and their values are
      identical**, use the project token
    - When a Figma variable name matches a project token **but the values differ**,
      use the exact Figma value hardcoded (Figma is the source of truth)
    - When no matching project token exists by name, use the exact Figma value
      hardcoded
    - Do not use approximate tokens. Do not use visual property values from
      get_design_context
    - Follow WCAG requirements for accessibility
    - Keep components composable and reusable
    - Add TypeScript types for component props
    - Avoid inline styles unless truly necessary for dynamic values
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "feat(figma): update Step 5 guidelines with token authority rules"
```

### Task 5: Update Self-Review and Common Issues

**Files:**
- Modify: `skills/implementing/implement-figma-design.md` (Self-Review section ~line 199, Common Issues section ~line 256)

- [ ] **Step 1: Update Self-Review token bullet**

Find:
```
    - Are design tokens mapped correctly (project tokens over hardcoded values)?
```

Replace with:
```
    - Are design tokens mapped correctly? (Figma variable names matched to project
      tokens by name; values verified to be identical; hardcoded Figma values used
      when no exact match exists)
```

- [ ] **Step 2: Update Common Issues — design token entry**

Find and replace the entire "### Issue: Design token values differ from project" block (lines 256-259) with:

```markdown
    ### Issue: Figma token has no matching project token or values differ
    **Cause:** Project design system tokens have different values than Figma specs,
    or no equivalent token exists.
    **Solution:** Use the exact Figma value hardcoded. Do not substitute approximate
    project tokens. Only use a project token when both name and value match exactly.
```

- [ ] **Step 3: Commit**

```bash
git add skills/implementing/implement-figma-design.md
git commit -m "feat(figma): update self-review and common issues for token authority"
```
