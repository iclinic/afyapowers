# No Code Snippets in Plans — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update planning constraints to eliminate code snippets from all tasks, replacing them with descriptive instructions, and enforce design/logic task separation when Figma resources are present.

**Architecture:** Two file changes — rewrite the task structure and constraints in `writing-plans/SKILL.md`, and update `templates/plan.md` to match. All changes are to Markdown skill files.

**Tech Stack:** Markdown skill files (no code changes)

**Spec:** `docs/superpowers/specs/2026-03-19-no-code-snippets-in-plans-design.md`

---

## Chunk 1: All Tasks

### Task 1: Update writing-plans skill — no code snippets constraint and new task structure

**Files:**
- Modify: `skills/writing-plans/SKILL.md`

**Depends on:** none

> **Note:** Line references below are to the original file before any edits. The implementer should locate content by section headings and surrounding context, not by line numbers alone, since earlier insertions will shift subsequent line numbers.

- [ ] **Step 1: Update the Overview paragraph**

  In the Overview section (line 10), remove the reference to providing "code" in plans. The overview currently says to document "which files to touch for each task, code, testing, docs they might need to check, how to test it." Change "code" to "step-by-step instructions" so it reads: "which files to touch for each task, step-by-step instructions, testing, docs they might need to check, how to test it."

- [ ] **Step 2: Add the No Code Snippets top-level constraint**

  Insert a new section `## No Code Snippets` immediately before the `## Bite-Sized Task Granularity` section (before line 58). This section must state:

  - Tasks must never contain code blocks with implementation code, test code, or inline code examples
  - Steps describe what to build, what to test, edge cases, and expected behavior — in plain language
  - The only acceptable code blocks are shell commands for running tests or committing
  - When Figma Resources are present in the design doc, any task involving styling (CSS, Tailwind, component layout/disposition, visual properties) MUST be treated as a Figma task
  - Always split design and logic into separate tasks. Design (Figma) tasks come first; logic tasks depend on them. Goal: 100% visual fidelity before adding behavior
  - What counts as styling: CSS properties, Tailwind classes, component layout, spacing, typography, colors, responsive breakpoints, content disposition
  - What stays as standard tasks: API integration, state management, form validation, event handlers, data fetching, business logic

- [ ] **Step 3: Update the Bite-Sized Task Granularity section**

  Replace lines 60-67 (the standard and Figma task granularity descriptions). The new content should describe:

  - Standard tasks use TDD-inspired steps with descriptive instructions (no code snippets). Each step describes what to do, why, which edge cases to cover, and expected outcomes.
  - The step sequence is: write the failing test (describe behaviors and expected outcomes) → run test and confirm failure (specify command and expected error) → implement minimal code (describe approach, patterns, decisions) → run test and confirm pass (specify command) → commit
  - Figma tasks: unchanged — single workflow step, the subagent prompt owns the how

- [ ] **Step 4: Replace the Task Structure section**

  Replace lines 106-148 (the entire `## Task Structure` section including the fenced code block with Python examples). The new task structure template must use descriptive steps without any code snippets. The format:

  - Task heading with component name
  - Files block (Create/Modify/Test with exact paths)
  - Depends on line
  - Step 1: Write the failing test — describe what behaviors to test (valid inputs, invalid inputs, edge cases), expected outcomes for each scenario, which file to write the test in, and what module/function is being tested
  - Step 2: Run the test and confirm it fails — specify the exact command and expected failure reason
  - Step 3: Implement the minimal code to pass the test — describe what the implementation should do, key decisions (patterns to follow, utilities to reuse), edge cases to handle, and which file to modify
  - Step 4: Run the test and confirm it passes — specify the exact command
  - Step 5: Commit

  Use the same fenced markdown block format (````markdown`) but with descriptive text instead of code blocks inside steps.

- [ ] **Step 5: Update the Figma Task Structure section**

  In the `## Figma Task Structure` section (lines 150-183), add guidance about the design/logic split. After the "How to identify Figma tasks" paragraph, add a note:

  - When Figma resources exist, tasks that involve any styling (CSS, Tailwind, layout, disposition) must be Figma tasks, even if they also have logic
  - Always create separate tasks: a Figma task for the visual design, then a standard task for the behavior/logic that depends on the Figma task
  - Example: "Contact Form Layout (Figma)" → "Contact Form Logic" (depends on layout task)

- [ ] **Step 6: Update the Remember section**

  Replace lines 185-190 (the Remember bullet list) with:

  - Exact file paths always
  - Describe behavior and edge cases completely (not just "add validation") — but never include code snippets
  - Exact commands with expected output
  - DRY, YAGNI, TDD-inspired (standard tasks), frequent commits
  - Figma tasks: no TDD, no code snippets, single workflow step — the subagent prompt owns the how
  - When Figma resources exist: always split design (Figma task) and logic (standard task) into separate tasks. Design first, logic depends on it
  - Any task touching styling (CSS, Tailwind, layout, disposition) MUST be a Figma task when Figma resources are available

- [ ] **Step 7: Verify coherence**

  Read the full `skills/writing-plans/SKILL.md` file and confirm:
  - No code snippets remain in task structure examples
  - The No Code Snippets section is present before Bite-Sized Task Granularity
  - The design/logic split rule is documented in both the No Code Snippets section and the Figma Task Structure section
  - The Remember section reflects the new constraints
  - The file reads coherently end-to-end with no contradictions

- [ ] **Step 8: Commit**

  Stage `skills/writing-plans/SKILL.md` and commit with message: `refactor(writing-plans): remove code snippets, add descriptive task structure and design/logic split rule`

---

### Task 2: Update plan template

**Files:**
- Modify: `templates/plan.md:13-33`

**Depends on:** Task 1

- [ ] **Step 1: Replace the standard task template**

  Replace lines 13-33 (the two standard task examples). The new standard task template should show:

  - Task heading with component name
  - Files block with Create/Modify/Test using placeholder paths
  - Depends on line
  - Five TDD-inspired steps as concise one-liners that describe the pattern:
    - Step 1: Write the failing test — describe behaviors to test and expected outcomes
    - Step 2: Run the test and confirm it fails
    - Step 3: Implement — describe what to build and key decisions
    - Step 4: Run the test and confirm it passes
    - Step 5: Commit

  Keep the Figma task template (lines 34-49) unchanged.

- [ ] **Step 2: Verify coherence**

  Read the full `templates/plan.md` and confirm:
  - Standard task template has no code snippets
  - Standard task template shows descriptive TDD-inspired steps
  - Figma task template is unchanged
  - Plan header is unchanged

- [ ] **Step 3: Commit**

  Stage `templates/plan.md` and commit with message: `refactor(template): replace code-snippet task template with descriptive steps`
