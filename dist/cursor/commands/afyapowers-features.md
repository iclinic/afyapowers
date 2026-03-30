---
description: List All Features
name: afyapowers:features
---
# /afyapowers:features — List All Features

List all features and their current states.

## Steps

1. Scan all directories under `.afyapowers/features/` (skip the `active` file)
2. For each directory, read `state.yaml`
3. Display a table:

```
| Feature | Phase | Status | Created |
|---------|-------|--------|---------|
| add-submit-button | implement | active | 2026-03-12 |
| fix-auth-flow | complete | completed | 2026-03-10 |
| refactor-api | design | aborted | 2026-03-11 |
```

4. Indicate which feature is currently active (from `.afyapowers/features/active`) with a marker like `→` or `(active)`.

If no `.afyapowers/features/` directory exists or it's empty, tell the user: "No features found. Run `/afyapowers:new` to start one."
