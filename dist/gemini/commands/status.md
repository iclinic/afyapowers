# /afyapowers:status — Show Feature Status

Display the current state of the active feature.

## Steps

1. Read `.afyapowers/features/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature."
3. Read `.afyapowers/features/<slug>/state.yaml`
4. Display the status in this format:

```
Feature: <feature-name>
Status: <active|completed|aborted>
Created: <date>
Current Phase: <phase-name>

Phases:
  ✅ design       — completed (artifacts: design.md)
  🔄 plan         — in_progress
  ⏳ implement    — pending
  ⏳ review       — pending
  ⏳ complete     — pending
```

Use ✅ for completed, 🔄 for in_progress, ⏳ for pending, ❌ for aborted.

If in the implement phase, also show task progress:
```
  🔄 implement     — in_progress (3 of 7 tasks completed)
```
Parse `artifacts/plan.md` to count checked vs unchecked items.
