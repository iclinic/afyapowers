---
name: afyapowers-dev-new
description: Start a New Feature
disable-model-invocation: true
---
# /afyapowers-dev:new — Start a New Feature

You are starting a new feature workflow. Follow these steps exactly:

## Step 0: Verify Python

afyapowers-dev requires Python 3.9+ at runtime (the feature state machine is Python). Check it is available:

```bash
command -v python3 >/dev/null && echo OK || echo MISSING
```

If the result is `MISSING`, tell the user: "O afyapowers-dev requer Python 3.9+, que não está no seu PATH. Instale o Python 3.9 ou mais recente e rode `/afyapowers-dev:new` novamente." Then **stop** — do not create any feature.

## Step 1: Get Feature Name

Ask the user: "Em qual feature você está trabalhando? Me dê um nome curto e uma breve descrição."

Wait for the user's response before proceeding.

## Step 2: Create the Feature

Run the feature script with the name the user provided. The script path is in your session context (injected by the session-start hook as "Feature script: ..."):

```bash
python3 "<feature-script-path>" new "<feature name>"
```

One call does everything deterministically: scaffolds the base `.afyapowers/` structure (dirs, `.gitignore`, empty `current-jira-ticket` — empty = the Jira ticket was never asked about; the design phase fills it in with the validated key or `none`), generates the dated slug (with collision suffixes), creates the feature directory with `artifacts/`, writes `state.yaml` and `history.yaml`, and sets `.afyapowers/features/active`. Existing files are never overwritten.

Confirm the output is `ok=true` and store the returned `slug` — it is the feature directory name used below. If the output is `ok=false` or the command errors, report the error and stop.

## Step 3: Confirm and Begin Design

Tell the user:
> Feature "<feature-name>" criada em `.afyapowers/features/<slug>/`.
> Fase atual: **design**
>
> Iniciando o design...

Then invoke `afyapowers-dev-design` via the Skill tool to begin the design phase. It will guide the conversation to clarify requirements, explore approaches, define architecture, and reach alignment.

When the design skill completes and produces the `design.md` artifact:
1. Save it to `.afyapowers/features/<slug>/artifacts/design.md`
2. Record it: `python3 "<feature-script-path>" record-artifact design.md` (updates `state.yaml` and `history.yaml`; confirm `ok=true`)
3. Tell the user: "Fase design concluída. Rode `/afyapowers-dev:next` para avançar para **plan**."
