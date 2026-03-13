# /afyapowers:history — Show Feature History

Display the full event timeline for the active feature.

## Steps

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:switch` to select one."
3. Read `.afyapowers/<slug>/history.yaml`
4. Display the events in chronological order:

```
Feature: <feature-name>
History:

  [2026-03-12 10:30:00] feature_created — Feature 'add-submit-button' created (via /afyapowers:new)
  [2026-03-12 10:30:00] phase_started — design
  [2026-03-12 10:42:00] artifact_created — design.md (design phase)
  [2026-03-12 10:45:00] phase_completed — design (via /afyapowers:next)
  [2026-03-12 10:45:00] phase_started — plan
  [2026-03-12 10:50:00] artifact_created — plan.md (plan phase)
```

Format each event on one line with timestamp, event type, and relevant details.
