# Design: Remove Code Snippets from Plans

## Summary

Update planning constraints to eliminate code snippets from all tasks. Plans become instruction-based: tasks include files involved, descriptions, and (when applicable) Figma references — but never code blocks with implementation or test code.

## Motivation

Code snippets in plans are causing problems. They become outdated, conflict with actual codebase patterns, and over-constrain the implementer. Plans should describe *what* and *why*, not dictate exact code.

## Changes

### 1. New Standard Task Structure

Standard (non-Figma) tasks follow TDD-inspired steps with descriptive instructions instead of code snippets:

- **Step 1: Write the failing test** — describe the behaviors to test, valid/invalid inputs, edge cases, expected outcomes. Specify the test file.
- **Step 2: Run the test and confirm it fails** — specify the command and expected failure reason.
- **Step 3: Implement the minimal code to pass the test** — describe what the implementation should do, key decisions, patterns to follow, edge cases. Reference the file to modify.
- **Step 4: Run the test and confirm it passes** — specify the command.
- **Step 5: Commit**

No code blocks anywhere. Only shell commands for running tests or committing are acceptable.

### 2. Styling = Figma Task Rule

When Figma Resources are present in the design doc:

1. **Always split design and logic into separate tasks.** The Figma task handles all visual aspects. A follow-up standard task handles behavior/logic.
2. **Design tasks come first.** The logic task depends on the Figma task. Goal: achieve 100% visual fidelity before adding behavior.
3. **What counts as styling:** CSS properties, Tailwind classes, component layout, spacing, typography, colors, responsive breakpoints, content disposition. If the task touches any of these and Figma resources exist, it's a Figma task.
4. **What stays as standard tasks:** API integration, state management, form validation, event handlers, data fetching, business logic — anything that doesn't affect visual output.

Example split:
- Task 3: Contact Form Layout (Figma) — implements the visual design
- Task 4: Contact Form Logic — depends on Task 3, adds validation, submission, error state behavior

### 3. Updated Constraints & Remember Section

**Bite-Sized Task Granularity:**
- Standard tasks: TDD-inspired steps with descriptive instructions (no code snippets). Each step describes what to do, why, edge cases, and expected outcomes.
- Figma tasks: single workflow step (unchanged).

**Remember section:**
- Exact file paths always
- Describe behavior and edge cases completely (not just "add validation") — but never include code snippets
- Exact commands with expected output (the command itself, not code blocks of implementation)
- DRY, YAGNI, TDD-inspired (standard tasks), frequent commits
- Figma tasks: no TDD, no code snippets, single workflow step — the subagent prompt owns the how
- When Figma resources exist: always split design (Figma task) and logic (standard task) into separate tasks. Design first, logic depends on it.
- Any task touching styling (CSS, Tailwind, layout, disposition) MUST reference Figma when Figma resources are available

**No Code Snippets constraint (top-level rule):**
Tasks must never contain code blocks with implementation code, test code, or inline code examples. Steps describe what to build, what to test, edge cases, and expected behavior — in plain language. The only acceptable code blocks are shell commands for running tests or committing.

### 4. Template Update (`templates/plan.md`)

Standard task template updated to use descriptive steps instead of code snippets. Figma task template unchanged.

## Files Affected

- Modify: `skills/writing-plans/SKILL.md`
- Modify: `templates/plan.md`
