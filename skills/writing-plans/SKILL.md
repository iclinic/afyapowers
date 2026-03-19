---
name: writing-plans
description: Use when the current afyapowers phase is plan — creates implementation plans from tech specs
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, step-by-step instructions, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

## Phase Gate

1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `plan`
3. If not in plan phase, tell the user the current phase and stop
4. Read the design from `.afyapowers/features/<feature>/artifacts/design.md` as input

**Save plans to:** `.afyapowers/features/<feature>/artifacts/plan.md`

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during design. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Figma Task Layer Inference

Before defining Figma tasks, check if the design doc contains a `## Figma Resources` section with a `### Node Map`.

**If Figma Resources are present**, read the Node Map and infer task layers directly — no Figma MCP calls at planning time:

1. **Layer 1 — Reusable components:** Nodes of type COMPONENT or COMPONENT_SET, or entries with a `×N` count (indicating repetition). Each becomes an individual task with no dependencies. Never group multiple reusable components into a single task.

2. **Layer 2 — Sections:** Top-level FRAME nodes in the Node Map that contain Layer 1 components as children. Each becomes a task that depends on the Layer 1 components it uses.

3. **Layer 3 — Page assembly:** If multiple sections exist, create a final task composing all sections into the full page layout. Depends on all Layer 2 tasks.

**Granularity rule:** If a node is typed COMPONENT/COMPONENT_SET or has a `×N` count, it MUST be its own Layer 1 task. Do not merge it into a parent section's task.

Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the design doc's `## Figma Resources` section.

**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## No Code Snippets

Tasks must never contain code blocks with implementation code, test code, or inline code examples. Steps describe what to build, what to test, edge cases, and expected behavior — in plain language. The only acceptable code blocks are shell commands for running tests or committing.

**Styling = Figma task:** When Figma Resources are present in the design doc, any task involving styling (CSS, Tailwind, component layout/disposition, visual properties) MUST be treated as a Figma task. Always split design and logic into separate tasks. Design (Figma) tasks come first; logic tasks depend on them. Goal: 100% visual fidelity before adding behavior.

- **What counts as styling:** CSS properties, Tailwind classes, component layout, spacing, typography, colors, responsive breakpoints, content disposition
- **What stays as standard tasks:** API integration, state management, form validation, event handlers, data fetching, business logic

## Bite-Sized Task Granularity

**For standard (non-Figma) tasks,** each step is TDD-inspired with descriptive instructions (no code snippets). Each step describes what to do, why, which edge cases to cover, and expected outcomes:

- Write the failing test (describe behaviors and expected outcomes) → run test and confirm failure (specify command and expected error) → implement minimal code (describe approach, patterns, decisions) → run test and confirm pass (specify command) → commit

**For Figma tasks:** a single step — "Implement using the Figma implementer workflow and commit". The subagent prompt owns the how. No implementation steps in the plan.

## Dependency Declaration

Every task MUST have a `**Depends on:**` line immediately after the `**Files:**` block.

- Use `none` if the task has no dependencies
- Use `Task N` or `Task N, Task M` (comma-separated) to declare dependencies on other tasks
- Dependencies are by task number, matching the `### Task N:` heading

**What counts as a dependency:**
- Task B modifies a file that Task A creates → Task B depends on Task A
- Task B imports a module that Task A creates → Task B depends on Task A
- Task B builds on an interface that Task A defines → Task B depends on Task A
- Task B and Task A are completely independent → no dependency needed

**Plan-time file overlap validation:**
After declaring dependencies, check that tasks which could run in parallel (no mutual dependency) don't share files in their `**Files:**` lists. If two parallel-eligible tasks touch the same file, add a dependency between them to force sequential execution.

File overlap validation is a safety net, not a substitute for thinking about task ordering. Always declare logical dependencies (imports, shared interfaces) explicitly.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`
**Depends on:** none | Task X, Task Y

- [ ] **Step 1: Write the failing test**

  Describe what behaviors to test: valid inputs, invalid inputs, edge cases.
  Explain expected outcomes for each scenario. Specify which file to write
  the test in and what module/function is being tested.

- [ ] **Step 2: Run test to verify it fails**

  Specify the exact command to run and the expected failure reason.

- [ ] **Step 3: Implement the minimal code to pass the test**

  Describe what the implementation should do, key decisions (which pattern
  to follow, which existing utility to reuse), and edge cases to handle.
  Specify which file to modify.

- [ ] **Step 4: Run test to verify it passes**

  Specify the exact command to run.

- [ ] **Step 5: Commit**
````

## Figma Task Structure

Use this format for tasks that implement UI components with Figma designs. The design doc's `## Figma Resources` section provides the source data for the Figma block.

**How to identify Figma tasks:** If the component being implemented has corresponding nodes in the design doc's `## Figma Resources` Node Map, it is a Figma task. Backend tasks, API routes, data models, business logic, and other non-UI tasks use the standard task structure above.

**Design/logic split:** When Figma resources exist, tasks that involve any styling (CSS, Tailwind, layout, disposition) must be Figma tasks, even if they also have logic. Always create separate tasks: a Figma task for the visual design, then a standard task for the behavior/logic that depends on the Figma task. Example: "Contact Form Layout (Figma)" → "Contact Form Logic" (depends on layout task).

**No TDD, no code snippets.** Figma tasks describe what to achieve — the implementer subagent uses the Figma MCP tools and the Figma implementer workflow to determine how.

```markdown
### Task N: [UI Component Name] (Figma)

**Files:**
- Create: `exact/path/to/component`
- Create: `exact/path/to/styles` (if applicable)
**Depends on:** none | Task X, Task Y

**Figma:**
- **File Key:** `<file_key>`
- **Breakpoints:** <breakpoint_name> (<width>px), <breakpoint_name> (<width>px)
- **Nodes:**
  | Node ID | Name | Type | Parent |
  |---------|------|------|--------|
  | `<id>` | <name> | <type> | <parent> |
  | `<id>` | <name> | <type> | <parent> |

- [ ] Implement using the Figma implementer workflow and commit
```

**Building the Figma block:**
- **File Key:** Copy from the design doc's `## Figma Resources` section
- **Breakpoints:** Include only the breakpoints relevant to this task's component (not all breakpoints in the design)
- **Nodes:** Select the nodes from the design doc's Node Map that correspond to this task's component and its children. Include the node ID, name, type, and parent for each.

**Mixed plans:** Figma and non-Figma tasks coexist in the same plan with standard dependency handling. A feature might have Tasks 1-2 as data models (standard TDD), Tasks 3-5 as UI components (Figma), and Task 6 as integration (standard TDD).

## Remember
- Exact file paths always
- Describe behavior and edge cases completely (not just "add validation") — but never include code snippets
- Exact commands with expected output
- DRY, YAGNI, TDD-inspired (standard tasks), frequent commits
- Figma tasks: no TDD, no code snippets, single workflow step — the subagent prompt owns the how
- When Figma resources exist: always split design (Figma task) and logic (standard task) into separate tasks. Design first, logic depends on it
- Any task touching styling (CSS, Tailwind, layout, disposition) MUST be a Figma task when Figma resources are available

## Required Sub-Skills

**REQUIRED:** Dispatch plan-document-reviewer subagent after writing each plan chunk.

- Announce: "Using plan-document-reviewer to validate the plan."
- Dispatch subagent using `skills/writing-plans/plan-document-reviewer-prompt.md`
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: proceed to next chunk or completion

## Plan Review Loop

After completing each chunk of the plan:

1. Dispatch plan-document-reviewer subagent (see `skills/writing-plans/plan-document-reviewer-prompt.md`) for the current chunk
   - Provide: chunk content, path to spec document
2. If Issues Found:
   - Fix the issues in the chunk
   - Re-dispatch reviewer for that chunk
   - Repeat until Approved
3. If Approved: proceed to next chunk (or completion if last chunk)

**Chunk boundaries:** Use `## Chunk N: <name>` headings to delimit chunks. Each chunk should be ≤1000 lines and logically self-contained.

**Review loop guidance:**
- Same agent that wrote the plan fixes it (preserves context)
- If loop exceeds 5 iterations, surface to human for guidance
- Reviewers are advisory - explain disagreements if you believe feedback is incorrect

## Completion

After saving the plan:

1. Update `state.yaml` to add `plan.md` to the plan phase's artifacts list
2. Append `artifact_created` event to `history.yaml`
3. Tell the user: "Plan phase complete. Run `/afyapowers:next` to proceed to **implement**."
