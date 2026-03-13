# Features Directory Restructure — Design Spec

## Problem Statement

Feature directories currently live at `.afyapowers/<DATE>-<SLUG>/`, mixing feature state with plugin-level files (like `active`). This makes the `.afyapowers/` root cluttered as features accumulate and provides no clear separation between plugin configuration and feature data.

## Requirements

1. Move all feature directories under `.afyapowers/features/<DATE>-<SLUG>/`
2. Move the `active` file to `.afyapowers/features/active`
3. Dynamically create `.afyapowers/.gitignore` on first feature creation, containing `features/active`
4. Update all path references across commands, skills, hooks, and documentation
5. No changes to file formats (state.yaml, history.yaml, artifacts)
6. No changes to phase flow, command names, or skill names

## Constraints

- This is a path-only change — no format or behavior changes
- The `.gitignore` must live at `.afyapowers/.gitignore` (not inside `features/`) for future extensibility
- The `active` file is the only gitignored item for now

## New Directory Layout

```
.afyapowers/
├── .gitignore              # dynamically created; contains "features/active"
└── features/
    ├── active              # current feature slug (gitignored)
    ├── 2026-03-13-add-button/
    │   ├── state.yaml
    │   ├── history.yaml
    │   └── artifacts/
    │       ├── design.md
    │       ├── plan.md
    │       └── ...
    └── 2026-03-14-fix-auth/
        └── ...
```

## Changes Required

### 1. Commands (commands/*.md)

All 7 commands reference `.afyapowers/` paths for feature directories and the `active` file. Update:

- **new.md** — Feature directory creation path changes to `.afyapowers/features/<slug>/`. Active file path changes to `.afyapowers/features/active`. Add logic: if `.afyapowers/.gitignore` doesn't exist, create it with `features/active`.
- **next.md** — State/artifact read/write paths update to `.afyapowers/features/<slug>/`
- **status.md** — State read path updates
- **history.md** — History read path updates
- **features.md** — Scan path changes from `.afyapowers/` to `.afyapowers/features/`. Active file read path changes to `.afyapowers/features/active`.
- **switch.md** — Active file write path changes to `.afyapowers/features/active`. Feature scan glob changes from `.afyapowers/*/state.yaml` to `.afyapowers/features/*/state.yaml`.
- **abort.md** — State write path updates. Active file read/clear path changes to `.afyapowers/features/active`.

### 2. Skills (skills/*/SKILL.md)

Skills that reference feature paths need updates:

- **design/SKILL.md** — Artifact write path
- **writing-plans/SKILL.md** — Artifact read/write paths
- **implementing/SKILL.md** — Artifact read/write paths
- **reviewing/SKILL.md** — Artifact read/write paths
- **completing/SKILL.md** — Artifact read/write paths
- **auto-documentation/SKILL.md** — Artifact read paths
- **design/spec-document-reviewer-prompt.md** — Artifact path reference
- **subagent-driven-development/SKILL.md** — Artifact path reference

### 3. Hooks (hooks/session-start)

The bash script reads `.afyapowers/active` and scans `.afyapowers/` for feature directories. Update:

- Active file path: `.afyapowers/active` → `.afyapowers/features/active`
- Feature scan path: `.afyapowers/*/state.yaml` → `.afyapowers/features/*/state.yaml`

### 4. Documentation (README.md)

Update directory structure references in README.md. Historical docs/specs/plans are left as-is — they describe the system at the time they were written.

## Breaking Change

This is a breaking change for any existing features in `.afyapowers/<slug>/`. Existing features must be manually moved to `.afyapowers/features/<slug>/` after the update. There is no automatic migration.

## .gitignore Creation Logic

In `/afyapowers:new`, as part of feature directory setup:

1. Ensure `.afyapowers/features/` directory exists (mkdir -p)
2. If `.afyapowers/.gitignore` does not exist, create it with content: `features/active`
3. Create the feature directory at `.afyapowers/features/<DATE>-<SLUG>/`
4. Proceed with feature creation as normal

## What Stays the Same

- state.yaml format and content
- history.yaml format and content
- Artifact file formats (design.md, plan.md, review.md, completion.md)
- Phase flow: design → plan → implement → review → complete
- All command names (`/afyapowers:new`, `/afyapowers:next`, etc.)
- All skill names
- Template files (templates/*.md)
- Plugin configuration (plugin.json)

## Testing Strategy

- Create a new feature and verify it lands in `.afyapowers/features/<slug>/`
- Verify `.afyapowers/.gitignore` is created on first feature with correct content
- Verify `active` file is written to `.afyapowers/features/active`
- Run through a full phase cycle (design → complete) to confirm all paths work
- Verify `/afyapowers:features` lists features from the new location
- Verify `/afyapowers:switch` reads/writes the new active path
- Verify session-start hook picks up active feature from new path
- Verify `git status` does not show the `active` file
