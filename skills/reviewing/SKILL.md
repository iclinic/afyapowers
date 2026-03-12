---
name: reviewing
description: "Use when the current afyapowers phase is review — performs 2-step code review (spec compliance + quality)"
---

# Review Phase

Perform a comprehensive 2-step code review of the completed feature implementation.

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `review`
3. If not in review phase, tell the user the current phase and stop

## Process

### Step 1: Gather Context

1. Read `.afyapowers/<feature>/artifacts/tech-spec.md` — the requirements
2. Read `.afyapowers/<feature>/artifacts/plan.md` — the implementation plan
3. Get the git diff for the feature's changes (use `git log` and `git diff` to identify the relevant commits)

### Step 2: Spec Compliance Review

Dispatch a spec-reviewer subagent using `skills/implementing/spec-reviewer-prompt.md`:
- Provide the tech spec content as "what was requested"
- Provide a summary of implemented changes as "what was built"
- Provide the relevant code diff

If the reviewer finds spec gaps:
1. Report the findings to the user
2. The user fixes issues (code changes happen during review phase)
3. Re-dispatch the spec reviewer
4. Repeat until spec-compliant (max 5 iterations)

### Step 3: Code Quality Review

Dispatch a code-quality-reviewer subagent using `skills/reviewing/code-reviewer.md`:
- Provide: what was implemented, plan reference, base/head SHAs, description

If the reviewer finds issues:
1. Categorize by severity (Critical, Important, Minor)
2. Critical and Important: must be fixed before proceeding
3. Minor: note for later, do not block
4. Fix issues and re-dispatch (max 5 iterations)

### Step 4: Produce Review Artifact

Read the template from `templates/review.md`. Fill in:
- Spec compliance findings and resolutions
- Code quality findings and resolutions
- Final verdict: "Approved" (only if both reviews pass)

Save to `.afyapowers/<feature>/artifacts/review.md`

### Step 5: Complete

Update `state.yaml` to add `review.md` to the review phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Review phase complete. Run `/afyapowers:next` to proceed to **complete**."

**Important:** The verdict MUST be "Approved" for `/afyapowers:next` to accept the transition. If issues remain, keep the verdict as "Changes Requested" and work with the user to resolve them.
