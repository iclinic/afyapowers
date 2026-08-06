---
claude:
  name: afyapowers:completing
  description: "Use when the current afyapowers phase is complete — handles merge/PR/cleanup and produces completion summary"
  model: sonnet
  effort: medium
cursor:
  name: afyapowers-completing
  description: "Use when the current afyapowers phase is complete — handles merge/PR/cleanup and produces completion summary"
  model: composer-2
github-copilot:
  name: completing
  description: "Use when the current afyapowers phase is complete — handles merge/PR/cleanup and produces completion summary"
---

# Complete Phase

Finalize the feature: verify everything works, merge or create PR, produce completion summary.

## Phase Gate

If this skill was invoked by `/afyapowers:next` (you already know the active feature slug and confirmed the phase is `complete` from the conversation context above):
- Skip steps 1-3 and proceed to Final Verification

Otherwise (direct invocation):
1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `complete`
3. If not in complete phase, tell the user the current phase and stop

## Required Sub-Skills

**REQUIRED:** Invoke `{{skill:autodoc}}` via the Skill tool after executing the user's completion choice (Step 3).

- Announce: "Usando o autodoc para atualizar a documentação do projeto."
- Invoke the skill. Follow its instructions completely.
- After it completes, resume the parent flow (Step 4: produce completion artifact).

This is the formal declaration. The actual invocation point is Step 3.5 below.

## Process

### Step 0: Create the phase task list (ordering enforcement)

Before anything else, create this phase's steps as tasks in the platform's task-tracking tool
(Claude Code: `TaskCreate` + `TaskUpdate` with `addBlockedBy`; other agents: the equivalent task/todo
tool — without dependency support, keep the numbering and enforce the chain by protocol), each blocked
by the previous:

- **T1** Final verification (Step 1) — tests green, tree clean, verdict **Aprovado**
- **T2** Present options + user choice (Step 2)
- **T3** Execute choice (Step 3) — **blocked by T1 and T2**: merge/PR/discard are destructive; they
  never run before verification passes and the user has chosen
- **T4** Autodoc (Step 3.5)
- **T5** Completion artifact (Step 4)
- **T6** Complete (Step 5)

Mark `in_progress` before starting, `completed` only with the exit condition met; never start a blocked
task.

### Step 1: Final Verification

1. Run the project's test suite — all tests must pass
2. Verify no uncommitted changes remain
3. Read `.afyapowers/features/<feature>/artifacts/review.md` — confirm verdict is **Aprovado**

If anything fails, report to the user and work to resolve before proceeding.

### Step 2: Present Options

Ask the user which completion path they prefer:

1. **Merge locally** — Merge the feature branch into the main branch
2. **Create PR** — Push the branch and create a pull request
3. **Keep as-is** — Leave the branch for later, just produce the summary
4. **Discard** — Abandon the changes (confirm first!)

Wait for the user's choice.

### Step 3: Execute Choice

Execute the user's chosen option:
- **Merge:** `git checkout main && git merge <branch> && git push`
- **PR:** `git push -u origin <branch>` then `gh pr create` with summary from artifacts
- **Keep:** No git operations
- **Discard:** Confirm, then clean up

### Step 3.5: Update Documentation

**REQUIRED SUB-SKILL:** Invoke `{{skill:autodoc}}` via the Skill tool.

Announce: "Usando o autodoc para atualizar a documentação do projeto."

The autodoc skill will use the following context from the current feature:
- Feature name from `.afyapowers/features/active`
- Artifacts: design.md, plan.md, review.md (in `.afyapowers/features/<feature>/artifacts/`)
- Git diff from the feature branch

After the skill completes, proceed to Step 4.

### Step 4: Produce Completion Artifact

Read the template from `<plugin-root>/templates/completion.md` (`<plugin-root>` = the `Plugin root:` path injected at session start; templates live at the plugin root, NOT inside the skill directory). Fill in:
- Summary of what was delivered (from design + review)
- Key files and components changed (from git diff)
- How to test (from design's testing strategy)
- PR/merge info (from Step 3)

Save to `.afyapowers/features/<feature>/artifacts/completion.md`

### Step 5: Complete

Update `state.yaml` to add `completion.md` to the complete phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Fase complete concluída. Rode `/afyapowers:next` para finalizar a feature."

When the user runs `/afyapowers:next`, the command will mark the feature as `completed`.
