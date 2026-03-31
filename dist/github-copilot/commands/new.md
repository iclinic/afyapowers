---
description: Start a New Feature
name: new
---
# /afyapowers:new — Start a New Feature

You are starting a new feature workflow. Follow these steps exactly:

## Step 1: Get Feature Name

Ask the user: "What feature are you working on? Give me a short name and a brief description."

Wait for the user's response before proceeding.

## Step 2: Create Feature Directory

Using the feature name provided:

1. Generate a slug: lowercase the name, replace spaces with hyphens, strip any characters that aren't letters, numbers, or hyphens, truncate to 50 characters
2. Get today's date in YYYY-MM-DD format
3. Construct the directory name: `<date>-<slug>`
4. Check if `.afyapowers/features/<directory-name>/` already exists. If so, append `-2` (then `-3`, etc.) until unique
5. Ensure `.afyapowers/features/` directory exists (create if not)
6. If `.afyapowers/.gitignore` does not exist, create it with content: `features/active`
7. Create the directory structure:
   - `.afyapowers/features/<directory-name>/`
   - `.afyapowers/features/<directory-name>/artifacts/`

## Step 3: Initialize State Files

Create `.afyapowers/features/<directory-name>/state.yaml`:

```yaml
feature: <feature-name-from-user>
status: active
created_at: <current-ISO-8601-timestamp>
current_phase: design
phases:
  design:
    status: in_progress
    started_at: <current-ISO-8601-timestamp>
    artifacts: []
  plan:
    status: pending
  implement:
    status: pending
  review:
    status: pending
  complete:
    status: pending
```

Create `.afyapowers/features/<directory-name>/history.yaml`:

```yaml
events:
  - timestamp: <current-ISO-8601-timestamp>
    event: feature_created
    phase: design
    command: /afyapowers:new
    details: "Feature '<feature-name>' created"
  - timestamp: <current-ISO-8601-timestamp>
    event: phase_started
    phase: design
```

## Step 4: Set Active Feature

Write the directory name (e.g., `2026-03-12-add-submit-button`) to `.afyapowers/features/active`.

## Step 5: Confirm and Begin Design

Tell the user:
> Feature "<feature-name>" created at `.afyapowers/features/<directory-name>/`.
> Current phase: **design**
>
> Starting design...

Then invoke the **design** skill to begin the design phase. The design skill will guide the conversation to clarify requirements, explore approaches, define architecture, and reach alignment.

When the design skill completes and produces the `design.md` artifact:
1. Save it to `.afyapowers/features/<directory-name>/artifacts/design.md`
2. Update `state.yaml` to add `design.md` to the design phase artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Design phase complete. Run `/afyapowers:next` to proceed to **plan**."
