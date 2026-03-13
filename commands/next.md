# /afyapowers:next — Advance to Next Phase

You are advancing the active feature to the next workflow phase. Follow these steps exactly:

## Step 1: Identify Active Feature

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature."
3. Read `.afyapowers/<slug>/state.yaml`

## Step 2: Validate Current Phase Completion

Check that the current phase has produced its required artifacts:

| Current Phase | Validation |
|--------------|------------|
| design | `.afyapowers/<slug>/artifacts/design.md` exists |
| plan | `.afyapowers/<slug>/artifacts/plan.md` exists |
| implement | Zero unchecked `- [ ]` items in `.afyapowers/<slug>/artifacts/plan.md` |
| review | `.afyapowers/<slug>/artifacts/review.md` exists AND its Verdict section contains "Approved" |
| complete | `.afyapowers/<slug>/artifacts/completion.md` exists |

If validation fails:
- Tell the user what's still needed (e.g., "The design artifact is missing. Complete the design phase first.")
- For implement: list the remaining unchecked tasks
- For review: if verdict is "Changes Requested", report the findings and explain what needs fixing
- Do NOT advance.

## Step 3: Handle Terminal Phase

If the current phase is `complete` and validation passes:
1. Update `state.yaml`: set `phases.complete.status` to `completed`, set `phases.complete.completed_at`, set feature-level `status` to `completed`
2. Append to `history.yaml`: `phase_completed` event for `complete`, then `feature_completed` event
3. Tell the user: "Feature '<feature-name>' is complete!"
4. Stop here — do not advance further.

## Step 4: Advance Phase

Determine the next phase from the ordered list: design → plan → implement → review → complete.

1. Update `state.yaml`:
   - Set current phase's `status` to `completed` and `completed_at` to current timestamp
   - Set next phase's `status` to `in_progress` and `started_at` to current timestamp
   - Set `current_phase` to the next phase name
2. Append to `history.yaml`:
   - `phase_completed` event for the current phase (include `command: /afyapowers:next`)
   - `phase_started` event for the next phase

## Step 5: Invoke Next Phase Skill

Tell the user which phase is starting, then invoke the appropriate skill:

| Next Phase | Skill to Invoke | What It Does |
|-----------|----------------|--------------|
| plan | **writing-plans** skill | Break design into implementation tasks |
| implement | **implementing** skill | Execute tasks with TDD + subagents |
| review | **reviewing** skill | 2-step code review (spec compliance + quality) |
| complete | **completing** skill | Merge/PR/cleanup, produce completion summary |

When the skill completes and produces its artifact:
1. Save the artifact to `.afyapowers/<slug>/artifacts/`
2. Update `state.yaml` to add the artifact to the current phase's artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Phase '<current-phase>' complete. Run `/afyapowers:next` to proceed to **<next-phase>**."

For the `complete` phase, instead say: "Phase complete. Run `/afyapowers:next` to finalize the feature."
