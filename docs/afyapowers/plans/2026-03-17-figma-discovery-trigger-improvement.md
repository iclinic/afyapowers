# Figma Discovery Trigger Improvement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the design skill reliably detect UI/frontend requests and ask about Figma designs before clarifying questions, using confirmation-style questions when Figma data is available.

**Architecture:** Single-file change to `skills/design/SKILL.md`. Reorder checklist, add trigger keyword list, replace dot diagram, add confirmation-style question guidance.

**Tech Stack:** Markdown (skill definition)

**Spec:** `docs/afyapowers/specs/2026-03-17-figma-discovery-trigger-improvement-design.md`

---

## Chunk 1: Update SKILL.md

### Task 1: Reorder checklist and add trigger keyword list

**Files:**
- Modify: `skills/design/SKILL.md:28-37`

- [ ] **Step 1: Update the checklist section (lines 28-37)**

Replace the current checklist:

```markdown
## Checklist

You MUST complete these items in order:

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Figma discovery (conditional)** — if the feature involves UI/frontend work, run the Figma discovery process (see below)
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections scaled to their complexity, get user approval after each section
6. **Write design doc** — save to `.afyapowers/features/<feature>/artifacts/design.md`
7. **Spec review loop** — dispatch spec-document-reviewer subagent; fix issues and re-dispatch until approved (max 5 iterations, then surface to human)
8. **User reviews written spec** — ask user to review the spec file before proceeding
```

With:

```markdown
## Checklist

You MUST complete these items in order:

1. **Explore project context** — check files, docs, recent commits
2. **Figma discovery (trigger-based)** — check user request against trigger keywords (see below); if match, ask about Figma and run discovery before clarifying questions
3. **Ask clarifying questions** — if Figma data is available, use confirmation-style questions (see below); otherwise, standard one-at-a-time clarifying questions
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections scaled to their complexity, get user approval after each section
6. **Write design doc** — save to `.afyapowers/features/<feature>/artifacts/design.md`
7. **Spec review loop** — dispatch spec-document-reviewer subagent; fix issues and re-dispatch until approved (max 5 iterations, then surface to human)
8. **User reviews written spec** — ask user to review the spec file before proceeding
```

- [ ] **Step 2: Verify the edit is correct**

Read `skills/design/SKILL.md` lines 28-37 and confirm the new checklist is in place.

### Task 2: Replace the process flow dot diagram

**Files:**
- Modify: `skills/design/SKILL.md:39-72`

- [ ] **Step 1: Replace the dot diagram (lines 39-72)**

Replace the current `## Process Flow` section and its dot diagram with:

```markdown
## Process Flow

```dot
digraph design {
    "Explore project context" [shape=box];
    "Trigger keywords match?" [shape=diamond];
    "Ask Figma question" [shape=box];
    "Figma discovery" [shape=box];
    "Confirmation-style questions" [shape=box];
    "Standard clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write design doc" [shape=box];
    "Spec review loop" [shape=box];
    "Spec review passed?" [shape=diamond];
    "User reviews spec?" [shape=diamond];
    "Suggest /afyapowers:next" [shape=doublecircle];

    "Explore project context" -> "Trigger keywords match?";
    "Trigger keywords match?" -> "Ask Figma question" [label="yes"];
    "Trigger keywords match?" -> "Standard clarifying questions" [label="no"];
    "Ask Figma question" -> "Figma discovery" [label="user provides URLs"];
    "Ask Figma question" -> "Standard clarifying questions" [label="no Figma designs"];
    "Figma discovery" -> "Confirmation-style questions";
    "Confirmation-style questions" -> "Propose 2-3 approaches";
    "Standard clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write design doc" [label="yes"];
    "Write design doc" -> "Spec review loop";
    "Spec review loop" -> "Spec review passed?";
    "Spec review passed?" -> "Spec review loop" [label="issues found,\nfix and re-dispatch"];
    "Spec review passed?" -> "User reviews spec?" [label="approved"];
    "User reviews spec?" -> "Write design doc" [label="changes requested"];
    "User reviews spec?" -> "Suggest /afyapowers:next" [label="approved"];
}
```​
```

- [ ] **Step 2: Verify the edit is correct**

Read `skills/design/SKILL.md` lines 39-75 and confirm the new diagram is in place.

### Task 3: Reorder and update "The Process" subsections

**Files:**
- Modify: `skills/design/SKILL.md:78-123`

- [ ] **Step 1: Move Figma discovery section before clarifying questions guidance**

In "The Process" section, the current order of subsections is:
1. "Understanding the idea" (lines 78-87)
2. "Figma discovery (conditional)" (lines 88-123)
3. "Exploring approaches" (lines 125-129)

The Figma discovery section already comes right after "Understanding the idea", which is correct for the new flow. No reordering of subsections needed — just update the content.

- [ ] **Step 2: Update the Figma discovery subsection header and trigger logic**

Replace the current Figma discovery header and condition (lines 88-92):

```markdown
**Figma discovery (conditional):**

If the feature involves UI/frontend work, ask the user:

> "Does this feature have Figma designs? If so, please share the Figma URL(s)."
```

With:

```markdown
**Figma discovery (trigger-based):**

After exploring project context, check the user's request for these trigger keywords (case-insensitive, word-level matching):

> page, landing page, screen, view, layout, header, footer, navbar, sidebar, UI component, form, modal, dialog, card, hero, section, banner, responsive, breakpoint, mobile, desktop, dashboard, panel, widget

If any keyword matches, ask the user:

> "Does this feature have Figma designs? If so, please share the Figma URL(s)."

If a keyword matches but the request is clearly not UI work (e.g., "write unit tests for the landing page API endpoint"), use judgment — when in doubt, ask.

If no keywords match, skip Figma discovery and proceed to clarifying questions.
```

- [ ] **Step 3: Verify the edit is correct**

Read `skills/design/SKILL.md` lines 88-100 and confirm the new trigger logic is in place.

### Task 4: Add confirmation-style questions guidance

**Files:**
- Modify: `skills/design/SKILL.md` (after the Figma discovery section, before "Exploring approaches")

- [ ] **Step 1: Add confirmation-style questions subsection**

Insert the following new subsection between the Figma discovery section and "Exploring approaches":

```markdown
**Clarifying questions (Figma-informed):**

When Figma data was gathered in the previous step, replace open-ended clarifying questions with confirmation-style:

- Present what Figma shows (structure, breakpoints, component hierarchy) and ask the user to confirm or correct
- Then only ask about things not visible in the design: business logic, data sources, interactions, dynamic behavior

Example:
- **Open-ended (without Figma):** "How should the page be structured?"
- **Confirmation-style (with Figma):** "The Figma design shows a hero section, a 3-column feature grid, and a CTA footer across 3 breakpoints (mobile/tablet/desktop). Does this match what you want, or do you need changes?"

When no Figma data is available, use the standard approach: ask questions one at a time to understand purpose, constraints, and success criteria.
```

- [ ] **Step 2: Verify the edit is correct**

Read the updated section and confirm the new subsection appears between Figma discovery and "Exploring approaches".

### Task 5: Commit

- [ ] **Step 1: Commit the changes**

```bash
git add skills/design/SKILL.md
git commit -m "feat: add trigger keywords and reorder Figma discovery in design skill"
```
