---
name: next
description: Advance to Next Phase
disable-model-invocation: true
---
# /afyapowers-dev:next — Advance to Next Phase

You are advancing the active feature to the next workflow phase. Follow these steps exactly:

## Step 0: Verify Python

afyapowers-dev requires Python 3.9+ at runtime (the feature state machine is Python). Check it is available:

```bash
command -v python3 >/dev/null && echo OK || echo MISSING
```

If the result is `MISSING`, tell the user: "O afyapowers-dev requer Python 3.9+, que não está no seu PATH. Instale o Python 3.9 ou mais recente e rode `/afyapowers-dev:next` novamente." Then **stop**.

## Step 1: Validate and Advance

Run the feature script to validate the current phase (without reading artifact files into context) and, when valid, execute the phase transition — `state.yaml` and `history.yaml` are updated deterministically by the script. The script path is in your session context (injected by the session-start hook as "Feature script: ..."):

```bash
python3 "<feature-script-path>" advance
```

Parse the key=value output (one `KEY=VALUE` per line). The emitted keys describe the PRE-transition state; when `advanced=true`, `next_phase` is the phase that just started:
- If the only line is `error=no_active_feature`: tell the user "Nenhuma feature ativa. Rode `/afyapowers-dev:new` para começar uma, ou `/afyapowers-dev:switch` para selecionar uma existente." Stop.
- If the only line is `error=no_state_file`: tell the user "O arquivo de estado da feature está faltando. A feature pode estar corrompida. Rode `/afyapowers-dev:features` para verificar." Stop.
- If `advanced=false`: report the `error` value. For implement phase, also show `task_progress`. Stop.
- If `advanced=true` and `next_phase=finalize`: the feature was marked completed. Tell the user: "A feature '<feature>' está completa!" and stop here.
- If `advanced=true` otherwise: proceed to Step 2.

## Step 2: Invoke Next Phase Skill

Tell the user which phase is starting, then invoke the appropriate skill:

| Next Phase | Skill to Invoke | What It Does |
|-----------|----------------|--------------|
| plan | `afyapowers-dev:writing-plans` | Break design into implementation tasks |
| implement | `afyapowers-dev:implementing` | Execute tasks with TDD + subagents |
| review | `afyapowers-dev:reviewing` | 2-step code review (spec + quality) |
| complete | `afyapowers-dev:completing` | Merge/PR/cleanup and completion summary |

When the skill completes and produces its artifact:
1. Save the artifact to `.afyapowers/features/<slug>/artifacts/`
2. Record it: `python3 "<feature-script-path>" record-artifact <artifact-filename>` (updates `state.yaml` and `history.yaml`; confirm `ok=true`)
3. Tell the user: "Fase '<phase-that-just-ran>' concluída. Rode `/afyapowers-dev:next` para avançar para **<phase-after-that>**."

Use the phase names from the table above — the phase that just ran is the one you invoked the skill for (from the `next_phase` in the advance output), and the phase after that is one step further in the workflow.

For the `complete` phase, instead say: "Fase concluída. Rode `/afyapowers-dev:next` para finalizar a feature."
