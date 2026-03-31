---
name: completing
description: "Use when the current afyapowers phase is complete — handles merge/PR/cleanup and produces completion summary"
---

# Complete Phase

Finalize the feature: verify everything works, merge or create PR, produce completion summary.

## Phase Gate

1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `complete`
3. If not in complete phase, tell the user the current phase and stop

## Required Sub-Skills

**REQUIRED:** Invoke `afyapowers:auto-documentation` via the Skill tool after executing the user's completion choice (Step 3).

- Announce: "Using auto-documentation to update project documentation."
- Invoke the skill. Follow its instructions completely.
- After it completes, resume the parent flow (Step 4: produce completion artifact).

This is the formal declaration. The actual invocation point is Step 3.5 below.

## Process

### Step 1: Final Verification

1. Run the project's test suite — all tests must pass
2. Verify no uncommitted changes remain
3. Read `.afyapowers/features/<feature>/artifacts/review.md` — confirm verdict is "Approved"

If anything fails, report to the user and work to resolve before proceeding.

### Step 2: Present Options

Ask the user which completion path they prefer:

1. **Merge locally** — Merge the feature branch into the main branch
2. **Create PR** — Push the branch and create a pull request
3. **Keep as-is** — Leave the branch for later, just produce the summary
4. **Discard** — Abandon the changes (confirm first!)

Wait for the user's choice.

### Step 3: Execute Choice

Execute the user's chosen option:
- **Merge:** `git checkout main && git merge <branch> && git push`
- **PR:** `git push -u origin <branch>` then `gh pr create` with summary from artifacts
- **Keep:** No git operations
- **Discard:** Confirm, then clean up

### Step 3.5: Update Documentation

**REQUIRED SUB-SKILL:** Invoke `afyapowers:auto-documentation` via the Skill tool.

Announce: "Using auto-documentation to update project documentation."

The auto-documentation skill will use the following context from the current feature:
- Feature name from `.afyapowers/features/active`
- Artifacts: design.md, plan.md, review.md (in `.afyapowers/features/<feature>/artifacts/`)
- Git diff from the feature branch

After the skill completes, proceed to Step 4.

### Step 4: Produce Completion Artifact

Read the template from `templates/completion.md`. Fill in:
- Summary of what was delivered (from design + review)
- Key files and components changed (from git diff)
- How to test (from design's testing strategy)
- PR/merge info (from Step 3)

Save to `.afyapowers/features/<feature>/artifacts/completion.md`

### Step 5: Complete

Update `state.yaml` to add `completion.md` to the complete phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Complete phase done. Run `/afyapowers:next` to finalize the feature."

When the user runs `/afyapowers:next`, the command will mark the feature as `completed`.
