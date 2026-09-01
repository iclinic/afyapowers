# /afyapowers-dev:abort — Abort Current Feature

Abandon the active feature. This is irreversible — aborted features cannot be resumed.

## Steps

1. Read `.afyapowers/features/active` to get the active feature slug
2. If no active feature, tell the user: "Nenhuma feature ativa para abortar."
3. Read `.afyapowers/features/<slug>/state.yaml`
4. Confirm with the user: "Tem certeza que deseja abortar a feature '<feature-name>'? Esta ação não pode ser desfeita."
5. Wait for confirmation.

### On confirmation:

1. Run `python3 "<plugin-root>/scripts/feature.py" abort "<short reason, if the user gave one>"` (plugin root is in your session context). It marks the feature and its current phase `aborted` in `state.yaml`, appends the `feature_aborted` event to `history.yaml`, and removes `.afyapowers/features/active`. Confirm `ok=true`.
2. Tell the user: "A feature '<feature-name>' foi abortada. Rode `/afyapowers-dev:new` para começar uma nova feature."
