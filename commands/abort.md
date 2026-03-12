# /afyapowers:abort — Abort Current Feature

Abandon the active feature. This is irreversible — aborted features cannot be resumed.

## Steps

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature to abort."
3. Read `.afyapowers/<slug>/state.yaml`
4. Confirm with the user: "Are you sure you want to abort feature '<feature-name>'? This cannot be undone."
5. Wait for confirmation.

### On confirmation:

1. Update `state.yaml`:
   - Set feature-level `status` to `aborted`
   - Set the current in_progress phase's `status` to `aborted`
2. Append to `history.yaml`:
   - `feature_aborted` event with current timestamp and the phase it was aborted in
3. Clear `.afyapowers/active` (delete the file or empty it)
4. Tell the user: "Feature '<feature-name>' has been aborted. Run `/afyapowers:new` to start a new feature."
