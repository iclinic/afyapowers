---
name: new
description: Start a New Feature
disable-model-invocation: true
---
# /afyapowers-dev:new — Start a New Feature

You are starting a new feature workflow. Follow these steps exactly:

## Step 0: Verify Python

afyapowers-dev requires Python 3.9+ at runtime (setup and history logging). Check it is available:

```bash
command -v python3 >/dev/null && echo OK || echo MISSING
```

If the result is `MISSING`, tell the user: "O afyapowers-dev requer Python 3.9+, que não está no seu PATH. Instale o Python 3.9 ou mais recente e rode `/afyapowers-dev:new` novamente." Then **stop** — do not create any feature.

## Step 1: Get Feature Name

Ask the user: "Em qual feature você está trabalhando? Me dê um nome curto e uma breve descrição."

Wait for the user's response before proceeding.

## Step 2: Create Feature Directory

Using the feature name provided:

1. Generate a slug: lowercase the name, replace spaces with hyphens, strip any characters that aren't letters, numbers, or hyphens, truncate to 50 characters
2. Get today's date in YYYY-MM-DD format
3. Construct the directory name: `<date>-<slug>`
4. Check if `.afyapowers/features/<directory-name>/` already exists. If so, append `-2` (then `-3`, etc.) until unique
5. Scaffold the base `.afyapowers/` structure by running the setup script. Its path is in your session context (injected by the session-start hook as "Setup script: ..."):
   ```bash
   python3 "<setup-script-path>"
   ```
   This idempotently creates `.afyapowers/features/`, `.afyapowers/history/`, `.afyapowers/.gitignore`, and an empty `.afyapowers/current-jira-ticket` (empty = the Jira ticket was never asked about; the design phase fills it in with the validated key or `none`). Existing files are never overwritten. Confirm the output is `ok=true`; if it is `ok=false` or the command errors, report the error and stop.
6. Create the feature directory structure:
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
    command: /afyapowers-dev:new
    details: "Feature '<feature-name>' created"
  - timestamp: <current-ISO-8601-timestamp>
    event: phase_started
    phase: design
```

## Step 4: Set Active Feature

Write the directory name (e.g., `2026-03-12-add-submit-button`) to `.afyapowers/features/active`.

## Step 5: Confirm and Begin Design

Tell the user:
> Feature "<feature-name>" criada em `.afyapowers/features/<directory-name>/`.
> Fase atual: **design**
>
> Iniciando o design...

Then invoke `afyapowers-dev:design` via the Skill tool to begin the design phase. It will guide the conversation to clarify requirements, explore approaches, define architecture, and reach alignment.

When the design skill completes and produces the `design.md` artifact:
1. Save it to `.afyapowers/features/<directory-name>/artifacts/design.md`
2. Update `state.yaml` to add `design.md` to the design phase artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Fase design concluída. Rode `/afyapowers-dev:next` para avançar para **plan**."
