# Chainable Skill Invocation Implementation Plan

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a "REQUIRED SUB-SKILL" convention across phase skills so they formally chain to sub-skills instead of duplicating logic.

**Architecture:** Each phase skill that chains to a sub-skill gets a standardized `## Required Sub-Skills` section. `implementing` is rewritten as a thin orchestrator delegating to `subagent-driven-development`. TDD rules are embedded directly in the implementer prompt (subagents can't call the Skill tool).

**Tech Stack:** Markdown skill files (no runtime code changes)

---

## Chunk 1: Formalize Existing Sub-Skills (design + writing-plans)

### Task 1: Add Required Sub-Skills section to design skill

**Files:**
- Modify: `skills/design/SKILL.md:110-136` (After the Design section)

- [ ] **Step 1: Read the current file to confirm line positions**

Run: Read `skills/design/SKILL.md` and confirm `## After the Design` starts at line 110.

- [ ] **Step 2: Add Required Sub-Skills section before "After the Design"**

Insert a new section between `## The Process` block (ends at line 108) and `## After the Design` (line 110). The new section goes at line 110, pushing existing content down:

```markdown
## Required Sub-Skills

**REQUIRED:** Dispatch spec-document-reviewer subagent after writing the design artifact.

- Announce: "Using spec-document-reviewer to validate the design."
- Dispatch subagent using `skills/design/spec-document-reviewer-prompt.md`
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: resume the parent flow (user review gate)
```

Insert this immediately before the `## After the Design` heading (line 110), with a blank line before and after.

- [ ] **Step 3: Verify the file is valid**

Read `skills/design/SKILL.md` and confirm:
- The new `## Required Sub-Skills` section exists between the last content section and `## After the Design`
- The existing "Spec Review Loop" subsection under "After the Design" (lines 118-123) is intentionally retained — `Required Sub-Skills` is the formal declaration of the pattern, while "Spec Review Loop" contains the detailed procedure. Both are needed.
- The rest of the file is unchanged

Note: If line numbers have shifted from what's described above, find sections by heading name rather than line number.

- [ ] **Step 4: Commit**

```bash
git add skills/design/SKILL.md
git commit -m "feat(design): add Required Sub-Skills section formalizing spec-document-reviewer dispatch"
```

---

### Task 2: Add Required Sub-Skills section to writing-plans skill

**Files:**
- Modify: `skills/writing-plans/SKILL.md:115-134` (Plan Review Loop section area)

- [ ] **Step 1: Read the current file to confirm line positions**

Run: Read `skills/writing-plans/SKILL.md` and confirm `## Plan Review Loop` starts at line 116.

- [ ] **Step 2: Add Required Sub-Skills section before "Plan Review Loop"**

Insert a new section immediately before `## Plan Review Loop` (line 116):

```markdown
## Required Sub-Skills

**REQUIRED:** Dispatch plan-document-reviewer subagent after writing each plan chunk.

- Announce: "Using plan-document-reviewer to validate the plan."
- Dispatch subagent using `skills/writing-plans/plan-document-reviewer-prompt.md`
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: proceed to next chunk or completion
```

Insert with a blank line before and after.

- [ ] **Step 3: Verify the file is valid**

Read `skills/writing-plans/SKILL.md` and confirm:
- The new `## Required Sub-Skills` section exists between `## Remember` and `## Plan Review Loop`
- The existing "Plan Review Loop" section is intentionally retained — `Required Sub-Skills` is the formal declaration of the pattern, while "Plan Review Loop" contains the detailed procedure. Both are needed.
- The rest of the file is unchanged

Note: If line numbers have shifted from what's described above, find sections by heading name rather than line number.

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): add Required Sub-Skills section formalizing plan-document-reviewer dispatch"
```

---

## Chunk 2: Rewrite implementing as thin orchestrator

### Task 3: Rewrite implementing/SKILL.md

**Files:**
- Modify: `skills/implementing/SKILL.md` (full rewrite of body after frontmatter)

- [ ] **Step 1: Read the current file**

Read `skills/implementing/SKILL.md` to confirm current content matches expectations (frontmatter lines 1-4, full body lines 5-141).

- [ ] **Step 2: Replace entire file body (keep frontmatter)**

Replace lines 1-141 with the following complete file:

```markdown
---
name: implementing
description: "Use when the current afyapowers phase is implement — orchestrates implementation via subagent-driven-development"
---

# Implementing Phase

Orchestrate plan execution by delegating to subagent-driven-development.

**Announce at start:** "I'm using the implementing skill to execute the plan."

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `implement`
3. If not in implement phase, tell the user the current phase and stop
4. Read the plan from `.afyapowers/<feature>/artifacts/plan.md`
5. Read the design from `.afyapowers/<feature>/artifacts/design.md` for context

## Validate Plan

- Parse all tasks from the plan (checkbox items: `- [ ]` and `- [x]`)
- If all tasks are already complete, tell the user and suggest `/afyapowers:next`
- If uncompleted tasks remain, proceed to execution

## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:subagent-driven-development` via the Skill tool to execute all plan tasks.

- Announce: "Using subagent-driven-development to execute implementation tasks."
- Invoke the skill. Follow its instructions completely.
- The plan content and design are already in the conversation context — SDD will use them directly.
- After SDD completes, resume the parent flow below.

## After SDD Completes

1. Verify all plan checkboxes are marked complete (`- [x]`)
2. If any remain unchecked, report which tasks are incomplete and ask the user how to proceed
3. Update `state.yaml` to reflect progress
4. Tell the user: "Implement phase complete. Run `/afyapowers:next` to proceed to **review**."
```

- [ ] **Step 3: Verify the rewrite**

Read `skills/implementing/SKILL.md` and confirm:
- Frontmatter has updated description: `"Use when the current afyapowers phase is implement — orchestrates implementation via subagent-driven-development"`
- Contains sections: Phase Gate, Validate Plan, Required Sub-Skills, After SDD Completes
- Does NOT contain: process flow diagram, Model Selection, Handling Implementer Status, Prompt Templates, Red Flags
- Total file is ~40 lines (significantly shorter than the original ~141)

- [ ] **Step 4: Commit**

```bash
git add skills/implementing/SKILL.md
git commit -m "feat(implementing): rewrite as thin orchestrator delegating to SDD"
```

---

### Task 4: Update subagent-driven-development/SKILL.md

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:11-19,101-119,151-159`

- [ ] **Step 1: Read the current file**

Read `skills/subagent-driven-development/SKILL.md` and confirm:
- `## When to Use` section at lines 11-18
- `## Advantages` section at lines 101-119
- `## Integration` section at lines 151-159

- [ ] **Step 2: Remove the "When to Use" section**

Delete lines 11-19 (the `## When to Use` heading through to the blank line before `## The Process`):

```
## When to Use

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Two-stage review after each task: spec compliance first, then code quality
- Faster iteration (no human-in-loop between tasks)

```

- [ ] **Step 3: Remove the "Advantages" section**

Delete the `## Advantages` section (was lines 101-119, now shifted after previous deletion). Remove from `## Advantages` through the blank line before `## Red Flags`:

```
## Advantages

**vs. Manual execution:**
- Subagents follow TDD naturally
- Fresh context per task (no confusion)
- Parallel-safe (subagents don't interfere)
- Subagent can ask questions (before AND during work)

**vs. Executing Plans:**
- Same session (no handoff)
- Continuous progress (no waiting)
- Review checkpoints automatic

**Quality gates:**
- Self-review catches issues before handoff
- Two-stage review: spec compliance, then code quality
- Review loops ensure fixes actually work
- Spec compliance prevents over/under-building

```

- [ ] **Step 4: Rewrite the "Integration" section**

Replace the current `## Integration` section:

```markdown
## Integration

**Required workflow skills:**
- **using-git-worktrees** - Set up isolated workspace before starting
- **writing-plans** - Creates the plan this skill executes

**Subagents should use:**
- **test-driven-development** - Follow TDD for each task
```

With:

```markdown
## Integration

**Invoked by:**
- **implementing** (REQUIRED SUB-SKILL) — implementing loads the plan and design, then invokes SDD to execute all tasks

**Subagent prompts:**
- `skills/implementing/implementer-prompt.md` — TDD rules are embedded directly in this prompt
- `skills/implementing/spec-reviewer-prompt.md` — spec compliance review
- `skills/implementing/code-quality-reviewer-prompt.md` — code quality review

**Context:** When invoked by implementing, the plan and design are already in the conversation context. Use them directly. If the plan is not in context (e.g., invoked standalone), read it from `.afyapowers/<feature>/artifacts/plan.md`.
```

- [ ] **Step 5: Verify the changes**

Read `skills/subagent-driven-development/SKILL.md` and confirm:
- No `## When to Use` section
- No `## Advantages` section
- `## Integration` section has new content with "Invoked by", "Subagent prompts", and "Context" subsections
- All other sections (The Process, Model Selection, Handling Implementer Status, Prompt Templates, Red Flags) are unchanged

- [ ] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat(SDD): remove comparison sections, rewrite Integration for sub-skill pattern"
```

---

## Chunk 3: Embed TDD in implementer prompt + completing sub-skill

### Task 5: Add TDD section to implementer-prompt.md

**Files:**
- Modify: `skills/implementing/implementer-prompt.md` (after "Your Job", before "Code Organization")

- [ ] **Step 1: Read the current file**

Read `skills/implementing/implementer-prompt.md` and locate:
- The `## Your Job` section (starts at line 29)
- The "While you work" paragraph (lines 40-41) — this is the last content in the Your Job section
- The `## Code Organization` section (starts at line 44)

- [ ] **Step 2: Add TDD section after "While you work" paragraph and before "Code Organization"**

Insert the following block **after** the "While you work" paragraph (line 41: `It's always OK to pause and clarify. Don't guess or make assumptions.`) and **before** `## Code Organization` (line 44). The TDD section goes inside the template code fence, between these two sections:

```markdown
    ## Test-Driven Development

    You MUST follow the RED-GREEN-REFACTOR cycle for all implementation work.

    **The Iron Law: No production code without a failing test first.**

    ### The Cycle

    1. **RED — Write one failing test** showing what should happen
       - One behavior per test, clear name, real code (no mocks unless unavoidable)
    2. **Verify RED — Run the test, confirm it fails**
       - Must fail because the feature is missing (not typos or errors)
       - If the test passes immediately, you're testing existing behavior — fix the test
    3. **GREEN — Write minimal code to make the test pass**
       - Simplest code that passes. Don't add features beyond the test.
    4. **Verify GREEN — Run tests, confirm all pass**
       - If the test fails, fix code not test. If other tests fail, fix now.
    5. **REFACTOR — Clean up while staying green**
       - Remove duplication, improve names, extract helpers. Don't add behavior.
    6. **Repeat** for the next behavior.

    ### Red Flags — STOP and Start Over

    - Writing code before the test
    - Test passes immediately (you're not testing new behavior)
    - Skipping the "verify fail" step
    - Over-engineering beyond what the current test requires

    Wrote code before a test? Delete it. Implement fresh from tests.
```

Note: This content must be indented with 4 spaces to match the template's indentation level (it's inside a code fence representing the prompt template).

- [ ] **Step 3: Verify the addition**

Read `skills/implementing/implementer-prompt.md` and confirm:
- `## Test-Driven Development` section appears between `## Your Job` and `## Code Organization`
- The TDD section includes The Cycle (6 steps) and Red Flags
- Indentation matches the surrounding template content (4-space indent)

- [ ] **Step 4: Commit**

```bash
git add skills/implementing/implementer-prompt.md
git commit -m "feat(implementer-prompt): embed TDD rules directly in subagent prompt"
```

---

### Task 6: Add Required Sub-Skills to completing skill + update Step 3.5

**Files:**
- Modify: `skills/completing/SKILL.md:14-55` (Process section)

- [ ] **Step 1: Read the current file**

Read `skills/completing/SKILL.md` and confirm:
- `## Process` starts at line 16
- `### Step 3.5: Update Documentation` starts at line 45
- Step 3.5 currently reads: `Read and follow \`skills/auto-documentation/SKILL.md\`.`

- [ ] **Step 2: Add Required Sub-Skills section before "## Process"**

Insert a new section between `## Phase Gate` (ends at line 14) and `## Process` (line 16):

```markdown
## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:auto-documentation` via the Skill tool after executing the user's completion choice (Step 3).

- Announce: "Using auto-documentation to update project documentation."
- Invoke the skill. Follow its instructions completely.
- After it completes, resume the parent flow (Step 4: produce completion artifact).

This is the formal declaration. The actual invocation point is Step 3.5 below.
```

- [ ] **Step 3: Rewrite Step 3.5 to use the sub-skill pattern**

Replace the current Step 3.5 content:

```markdown
### Step 3.5: Update Documentation

Read and follow `skills/auto-documentation/SKILL.md`.

The following context is available from the current feature:
- Feature name from `.afyapowers/active`
- Artifacts: design.md, plan.md, review.md (in `.afyapowers/<feature>/artifacts/`)
- Git diff from the feature branch

After documentation is updated, proceed to Step 4.
```

With:

```markdown
### Step 3.5: Update Documentation

**REQUIRED SUB-SKILL:** Invoke `afyapowers:auto-documentation` via the Skill tool.

Announce: "Using auto-documentation to update project documentation."

The auto-documentation skill will use the following context from the current feature:
- Feature name from `.afyapowers/active`
- Artifacts: design.md, plan.md, review.md (in `.afyapowers/<feature>/artifacts/`)
- Git diff from the feature branch

After the skill completes, proceed to Step 4.
```

- [ ] **Step 4: Verify the changes**

Read `skills/completing/SKILL.md` and confirm:
- New `## Required Sub-Skills` section exists between `## Phase Gate` and `## Process`
- The Required Sub-Skills section includes a cross-reference note pointing to Step 3.5 as the invocation point
- Step 3.5 now uses `**REQUIRED SUB-SKILL:**` pattern instead of `Read and follow`
- All other steps are unchanged

- [ ] **Step 5: Commit**

```bash
git add skills/completing/SKILL.md
git commit -m "feat(completing): add Required Sub-Skills section, update Step 3.5 for auto-documentation"
```

---

## Verification

After all tasks are complete, verify the full chain map:

- [ ] **Read each modified file and confirm the Required Sub-Skills pattern is consistent across all four skills:**
  - `skills/design/SKILL.md` — dispatches spec-document-reviewer
  - `skills/writing-plans/SKILL.md` — dispatches plan-document-reviewer
  - `skills/implementing/SKILL.md` — invokes SDD via Skill tool
  - `skills/completing/SKILL.md` — invokes auto-documentation via Skill tool

- [ ] **Confirm implementing is now a thin orchestrator** (no process diagram, no model selection, no status handling, no red flags)

- [ ] **Confirm SDD retained its core logic** (process diagram, model selection, status handling, red flags all present) but lost When to Use, Advantages, and old Integration

- [ ] **Confirm implementer-prompt.md has TDD rules** embedded between Your Job and Code Organization

- [ ] **Confirm no files were created** (only modifications to existing files)
