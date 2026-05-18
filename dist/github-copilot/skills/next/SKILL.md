---
name: next
description: Advance to Next Phase
disable-model-invocation: true
---
# /afyapowers:next — Advance to Next Phase

You are advancing the active feature to the next workflow phase. Follow these steps exactly:

## Step 1: Preflight Validation

Run the preflight script to validate the current phase without reading artifact files into context. The plugin root path is available in your session context (injected by the session-start hook as "Plugin root: ..."):

```bash
bash "<plugin-root>/skills/next/scripts/preflight.sh"
```

Parse the JSON output:
- If `error` is `"no_active_feature"`: tell the user "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature." Stop.
- If `valid` is `false`: report the `error` message. For implement phase, also show `task_progress`. Stop.
- If `valid` is `true`: proceed to Step 2.

## Step 2: Handle Terminal Phase

If `current_phase` is `complete` and `next_phase` is `finalize`:
1. Read `.afyapowers/features/<slug>/state.yaml` (use the `slug` from preflight output)
2. Update it: set `phases.complete.status` to `completed`, `phases.complete.completed_at` to now, feature `status` to `completed`
3. Append to `history.yaml`: `phase_completed` event for `complete`, then `feature_completed` event
4. Tell the user: "Feature '<feature>' is complete!"
5. Stop here.

## Step 3: Advance Phase

1. Read `.afyapowers/features/<slug>/state.yaml` (use the `slug` from preflight output)
2. Update it:
   - Set current phase's `status` to `completed` and `completed_at` to current timestamp
   - Set next phase's `status` to `in_progress` and `started_at` to current timestamp
   - Set `current_phase` to `next_phase`
3. Append to `history.yaml`:
   - `phase_completed` event for the current phase (include `command: /afyapowers:next`)
   - `phase_started` event for the next phase

## Step 4: Invoke Next Phase Skill

Tell the user which phase is starting, then invoke the appropriate skill:

| Next Phase | Skill to Invoke |
|-----------|----------------|
| plan | **writing-plans** |
| implement | **implementing** |
| review | **reviewing** |
| complete | **completing** |

When the skill completes and produces its artifact:
1. Save the artifact to `.afyapowers/features/<slug>/artifacts/`
2. Update `state.yaml` to add the artifact to the current phase's artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Phase '<current-phase>' complete. Run `/afyapowers:next` to proceed to **<next-phase>**."

For the `complete` phase, instead say: "Phase complete. Run `/afyapowers:next` to finalize the feature."
