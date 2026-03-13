# Chainable Skill Invocation — Design Spec

## Problem Statement

Skills in afyapowers operate in isolation within each phase. When `implementing` runs, it duplicates logic that already exists in `subagent-driven-development`. The `completing` skill manually describes auto-documentation steps instead of invoking the skill. There is no formal pattern for one skill to invoke another within a phase, leading to duplication and inconsistent behavior.

## Requirements

1. Define a "REQUIRED SUB-SKILL" convention that any phase skill can use to invoke another skill
2. `design` must invoke spec-document-reviewer as a formalized sub-skill
3. `writing-plans` must invoke plan-document-reviewer as a formalized sub-skill
4. `implementing` must become a thin orchestrator that delegates to `subagent-driven-development`
5. `subagent-driven-development` must embed TDD rules directly in implementer prompts
6. `completing` must invoke `auto-documentation` as a formalized sub-skill
7. Manual `/afyapowers:next` gates between the 5 major phases remain unchanged

## Constraints

- No changes to phase transition logic (commands, state.yaml, history.yaml)
- No changes to cross-cutting skills (systematic-debugging, verification-before-completion, etc.)
- No changes to the `reviewing` phase skill
- Subagents cannot call the Skill tool, so TDD must be embedded in prompts, not invoked
- Max chain depth is 2 (implementing → SDD → TDD-in-prompts)

## Chosen Approach: "REQUIRED SUB-SKILL" Declaration Pattern

Each phase skill that chains to a sub-skill uses a consistent structure:

```markdown
## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:<skill-name>` via the Skill tool at [specific trigger point].

- Announce: "Using [skill-name] to [purpose]."
- Invoke the skill. Follow its instructions completely.
- After it completes, resume the parent skill flow.
```

Rules:
- The parent skill pauses execution while the sub-skill runs
- The sub-skill returns control implicitly when its instructions are fully followed
- Sub-skills do NOT invoke the parent (no circular chains)
- A sub-skill can itself have REQUIRED SUB-SKILLs (max depth 2)

## Architecture: Chain Map

```
design ──REQUIRED──▶ spec-document-reviewer (subagent dispatch)
writing-plans ──REQUIRED──▶ plan-document-reviewer (subagent dispatch)
implementing ──REQUIRED──▶ subagent-driven-development (Skill tool invocation)
                            └─ implementer prompt embeds TDD rules
                            └─ owns: implementer → spec reviewer → code quality reviewer
completing ──REQUIRED──▶ auto-documentation (Skill tool invocation)
```

## Changes Per File

### 1. `skills/design/SKILL.md`

**Change type:** Add section

Add a `## Required Sub-Skills` section formalizing the existing spec-document-reviewer dispatch:

```markdown
## Required Sub-Skills

**REQUIRED:** Dispatch spec-document-reviewer subagent after writing the design artifact.

- Announce: "Using spec-document-reviewer to validate the design."
- Dispatch subagent using `skills/design/spec-document-reviewer-prompt.md`
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: resume the parent flow (user review gate)
```

The spec review loop logic already exists in the checklist and process sections. This section makes the pattern explicit and consistent with other skills.

### 2. `skills/writing-plans/SKILL.md`

**Change type:** Add section

Add a `## Required Sub-Skills` section formalizing the existing plan-document-reviewer dispatch:

```markdown
## Required Sub-Skills

**REQUIRED:** Dispatch plan-document-reviewer subagent after writing each plan chunk.

- Announce: "Using plan-document-reviewer to validate the plan."
- Dispatch subagent using `skills/writing-plans/plan-document-reviewer-prompt.md`
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: proceed to next chunk or completion
```

### 3. `skills/implementing/SKILL.md`

**Change type:** Full rewrite (replaces entire file body after frontmatter)

The implementing skill becomes a lightweight phase-level orchestrator. The entire current content (process flow diagram, Model Selection, Handling Implementer Status, Prompt Templates, Red Flags, and all per-task dispatch logic) is **removed** and replaced with the following structure:

#### New file structure:

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

**What is removed** (all of this now lives in SDD):
- The full process flow diagram (dot graph)
- Model Selection section
- Handling Implementer Status section (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED)
- Prompt Templates section (references to implementer-prompt.md, spec-reviewer-prompt.md, code-quality-reviewer-prompt.md)
- Red Flags section (subagent management rules)
- All per-task dispatch logic

**What implementing retains:**
- Phase gate logic
- Plan loading, parsing, and validation
- Phase completion (state.yaml update, suggesting next phase)

**Context passing:** SDD receives context from the conversation — the plan content and design are already loaded by implementing before SDD is invoked. SDD should use the plan content already in conversation context rather than re-reading the file. However, SDD's "Read plan, extract all tasks" step is kept as a fallback — if the plan is in context, SDD uses it directly; if invoked in another way in the future, SDD can still load the file itself.

### 4. `skills/subagent-driven-development/SKILL.md`

**Change type:** Targeted updates to 3 sections

**Remove "When to Use" section** (lines comparing SDD vs executing-plans). No longer needed — SDD is always invoked by implementing.

**Remove "Advantages" section** (lines comparing SDD vs manual execution and executing-plans). These comparisons are obsolete now that SDD is the standard execution path.

**Rewrite `## Integration` section** to:

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

Note: The old Integration section's line "Subagents should use test-driven-development" is removed. TDD is now embedded directly in the implementer prompt — subagents don't invoke skills.

**Keep unchanged:** Process flow diagram, Model Selection, Handling Implementer Status, Red Flags, all per-task dispatch logic.

**Regarding SDD's final code review step:** SDD's process ends with "Dispatch final code reviewer for entire implementation" before "Complete." This step is kept — it serves as a post-implementation sanity check within the implement phase. The separate `reviewing` phase that follows is a more thorough, design-level review. These are complementary, not duplicative: SDD's final review catches obvious issues before the phase ends, while the reviewing phase does a full spec compliance + quality audit.

### 5. `skills/implementing/implementer-prompt.md`

**Change type:** Add TDD section

Add a `## Test-Driven Development` section after "Your Job" and before "Code Organization". Content extracted from `skills/test-driven-development/SKILL.md`:

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

### 6. `skills/completing/SKILL.md`

**Change type:** Add section, update Step 3.5

Add a `## Required Sub-Skills` section:

```markdown
## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:auto-documentation` via the Skill tool after executing the user's completion choice (Step 3).

- Announce: "Using auto-documentation to update project documentation."
- Invoke the skill. Follow its instructions completely.
- After it completes, resume the parent flow (Step 4: produce completion artifact).
```

Update Step 3.5 to reference the sub-skill pattern instead of the current inline instructions:

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

### 7. No changes to:

- `skills/test-driven-development/SKILL.md` — stays as standalone reference. Its core rules are embedded in implementer-prompt.md.
- `skills/reviewing/SKILL.md` — independent phase, no sub-skills needed
- `skills/systematic-debugging/SKILL.md` — cross-cutting, unchanged
- `skills/verification-before-completion/SKILL.md` — cross-cutting, unchanged
- `skills/using-git-worktrees/SKILL.md` — cross-cutting, unchanged
- `skills/dispatching-parallel-agents/SKILL.md` — cross-cutting, unchanged
- All commands (`new.md`, `next.md`, `status.md`, etc.)
- State management (state.yaml, history.yaml)
- Hooks

## Testing Strategy

1. **Manual walkthrough:** Run a feature through the full workflow and verify:
   - `design` announces and dispatches spec-document-reviewer correctly
   - `writing-plans` announces and dispatches plan-document-reviewer correctly
   - `implementing` invokes SDD via Skill tool, does NOT dispatch subagents itself
   - SDD dispatches implementer with TDD section in prompt
   - SDD runs full review cycle (spec then quality)
   - `completing` invokes auto-documentation via Skill tool
2. **Verify no regression:** Existing `/afyapowers:next` phase gates still work correctly
3. **Verify chain depth:** implementing → SDD → TDD-in-prompts works end-to-end

## Dependencies

- No external dependencies
- No new files created (only modifications to existing skill files)
- No changes to plugin manifest or hooks
