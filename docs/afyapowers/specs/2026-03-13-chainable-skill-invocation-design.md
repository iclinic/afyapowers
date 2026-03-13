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

**Change type:** Rewrite to thin orchestrator

The implementing skill becomes a lightweight phase-level orchestrator:

1. Phase gate (unchanged): read active feature, confirm phase, load plan and design
2. Validate plan has uncompleted tasks
3. **REQUIRED SUB-SKILL:** Invoke `afyapowers:subagent-driven-development` via Skill tool
4. After SDD completes, verify all plan checkboxes are marked complete
5. Suggest `/afyapowers:next`

**What implementing retains:**
- Phase gate logic
- Plan loading and validation
- Phase completion (state.yaml update, suggesting next phase)

**What implementing delegates to SDD:**
- All per-task subagent dispatch (implementer, spec reviewer, code quality reviewer)
- Task iteration and completion tracking
- Model selection decisions
- Handling implementer status (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED)
- TDD enforcement (via embedded prompts)
- All review loop logic
- Red flags and constraints around subagent management

**Context passing:** SDD receives context from the conversation — the plan content and design are already loaded by implementing before SDD is invoked. No explicit parameter passing needed.

### 4. `skills/subagent-driven-development/SKILL.md`

**Change type:** Minor updates

- Ensure it owns the full per-task cycle (already does)
- Remove "When to Use" section comparing itself to executing-plans (no longer needed — SDD is always invoked by implementing)
- Update `## Integration` section to reflect it's invoked by implementing as a REQUIRED SUB-SKILL
- Keep all existing logic: process flow, model selection, handling implementer status, red flags
- Add explicit statement that it reads the plan content from the conversation context (already loaded by implementing)

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
