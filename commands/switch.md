# /afyapowers:switch — Switch Active Feature

Switch the active feature context. This command accepts an optional argument: the feature name or slug.

## Steps

### If no argument provided:

1. List all non-aborted features from `.afyapowers/*/state.yaml`
2. Show them as a numbered list with current phase and status
3. Ask the user to pick one
4. Wait for their response

### Once a feature is selected (by argument or user choice):

1. Find the matching feature directory under `.afyapowers/` (match by slug or feature name)
2. Verify the feature is not aborted. If it is, tell the user: "Feature '<name>' is aborted and cannot be switched to. Run `/afyapowers:new` to start a new feature."
3. Write the feature's directory name to `.afyapowers/active`
4. Read the feature's `state.yaml`
5. Display its status (same format as `/afyapowers:status`)

This command does NOT modify either feature's `state.yaml`. Switching is purely a pointer change.
