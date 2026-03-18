---
name: writing-plans
description: Use when the current afyapowers phase is plan — creates implementation plans from tech specs
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

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

## Figma Component Discovery (Conditional)

Before defining tasks, check if the design doc (`.afyapowers/features/<feature>/artifacts/design.md`) contains a `## Figma Resources` section.

**If Figma Resources are present:**

1. **Dispatch the figma-discovery skill** as a subagent with:
   - File Key(s) from the `## Figma Resources` section
   - Root Node ID(s) from the Node Map in `## Figma Resources`
   - Breakpoints (if listed in `## Figma Resources`)

   ```
   Agent tool (general-purpose):
     description: "Figma component discovery"
     prompt: |
       You are running the figma-discovery skill.
       Read and follow: skills/figma-discovery/SKILL.md

       Input:
       - File Key: <file_key>
       - Root Node IDs: <node_ids>
       - Breakpoints: <breakpoints_if_known>
       - Feature: <feature_name>

       Write output to: .afyapowers/features/<feature>/artifacts/figma-component-mapping.md
   ```

2. **Read the resulting component mapping** from `.afyapowers/features/<feature>/artifacts/figma-component-mapping.md`

3. **Use the mapping to generate layered tasks:**
   - **Layer 1 — Reusable components:** One task per component marked as `reusable-component` or `design-system-component`. These have no page-level dependencies and can be built first.
   - **Layer 2 — Page sections:** One task per `page-section`, with dependencies on any reusable components it uses as children.
   - **Layer 3 — Page assembly:** A final task composing all sections into the full page, depending on all section tasks.

   Each Figma task uses the Figma Task Structure format (see below) with node IDs and breakpoints from the component mapping.

**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**For standard (non-Figma) tasks, each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

**For Figma tasks, steps follow the implement-design workflow instead of TDD:**
- "Fetch design context for all task nodes" - step
- "Capture screenshot for visual reference" - step
- "Download required assets" - step
- "Translate to project conventions" - step
- "Achieve 1:1 visual parity across all breakpoints" - step
- "Validate against Figma screenshot" - step
- "Commit" - step

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

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Figma Task Structure

Use this format for tasks that implement UI components with Figma designs. The design doc's `## Figma Resources` section provides the source data for the Figma block.

**How to identify Figma tasks:** If the component being implemented has corresponding nodes in the design doc's `## Figma Resources` Node Map, it is a Figma task. Backend tasks, API routes, data models, business logic, and other non-UI tasks use the standard task structure above.

**No TDD, no code snippets.** Figma tasks describe what to achieve — the implementer subagent uses the Figma MCP tools and the implement-figma-design workflow to determine how.

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

- [ ] Step 1: Fetch design context for all task nodes
- [ ] Step 2: Capture screenshot for visual reference
- [ ] Step 3: Download required assets (images, icons, SVGs)
- [ ] Step 4: Translate to project conventions
- [ ] Step 5: Achieve 1:1 visual parity across all breakpoints
- [ ] Step 6: Validate against Figma screenshot
- [ ] Step 7: Commit
```

**Building the Figma block:**
- **File Key:** Copy from the design doc's `## Figma Resources` section
- **Breakpoints:** Include only the breakpoints relevant to this task's component (not all breakpoints in the design)
- **Nodes:** Select the nodes from the design doc's Node Map that correspond to this task's component and its children. Include the node ID, name, type, and parent for each.

**Mixed plans:** Figma and non-Figma tasks coexist in the same plan with standard dependency handling. A feature might have Tasks 1-2 as data models (standard TDD), Tasks 3-5 as UI components (Figma), and Task 6 as integration (standard TDD).

## Remember
- Exact file paths always
- Complete code in plan (not "add validation") — except for Figma tasks which use design-workflow steps instead of code
- Exact commands with expected output
- DRY, YAGNI, TDD (standard tasks), frequent commits
- Figma tasks: no TDD, no code snippets — steps describe what to achieve, not how to code it

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
