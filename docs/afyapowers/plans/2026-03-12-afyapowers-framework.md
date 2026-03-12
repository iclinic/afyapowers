# afyapowers Framework Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code / Cursor plugin that enforces a deterministic, phase-gated development workflow with persistent state, session continuity, and full auditability.

**Architecture:** Plugin with 7 slash commands (markdown prompts), 12 skills (6 phase + 6 cross-cutting), 5 artifact templates, a session-start hook, and per-feature YAML state files. All skills are forked from superpowers and adapted for phase-aware behavior.

**Tech Stack:** Markdown (commands, skills), YAML (state files), Shell script (session-start hook), JSON (plugin metadata)

**Spec:** `docs/afyapowers/specs/2026-03-12-afyapowers-framework-design.md`

---

## Chunk 1: Plugin Scaffolding, Hook, and Templates

### Task 1: Plugin Metadata

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Create plugin.json**

```json
{
  "name": "afyapowers",
  "description": "Deterministic, phase-gated development workflow with persistent state and auditability",
  "version": "0.1.0",
  "author": "afyapowers",
  "license": "MIT"
}
```

- [ ] **Step 2: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: add plugin metadata"
```

---

### Task 2: Session-Start Hook Configuration

**Files:**
- Create: `hooks/hooks.json`

- [ ] **Step 1: Create hooks.json**

```json
{
  "hooks": [
    {
      "type": "UserPromptSubmit",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/session-start",
      "triggers": ["startup", "resume", "clear", "compact"],
      "asynchronous": false
    }
  ]
}
```

- [ ] **Step 2: Commit**

```bash
git add hooks/hooks.json
git commit -m "chore: add hook configuration"
```

---

### Task 3: Session-Start Hook Script

**Files:**
- Create: `hooks/session-start`

The hook script reads `.afyapowers/active` and injects feature context at session start. It must:
1. Read `.afyapowers/active` to find the active feature slug
2. Fall back to scanning `.afyapowers/*/state.yaml` for `in_progress` features
3. Read the active feature's `state.yaml`
4. Output JSON with `additionalContext` containing feature name, current phase, phase statuses, artifacts

- [ ] **Step 1: Create the session-start shell script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Find .afyapowers directory relative to working directory
AFYA_DIR=".afyapowers"

# If no .afyapowers directory, nothing to inject
if [ ! -d "$AFYA_DIR" ]; then
  echo '{}'
  exit 0
fi

ACTIVE_FEATURE=""
ACTIVE_FILE="$AFYA_DIR/active"

# Try reading the active file first
if [ -f "$ACTIVE_FILE" ]; then
  ACTIVE_FEATURE=$(cat "$ACTIVE_FILE" | tr -d '[:space:]')
  # Validate it points to an existing feature
  if [ ! -d "$AFYA_DIR/$ACTIVE_FEATURE" ]; then
    ACTIVE_FEATURE=""
  fi
fi

# Fallback: scan for features with in_progress phases
if [ -z "$ACTIVE_FEATURE" ]; then
  IN_PROGRESS_FEATURES=()
  for state_file in "$AFYA_DIR"/*/state.yaml; do
    [ -f "$state_file" ] || continue
    if grep -q "status: in_progress" "$state_file" 2>/dev/null; then
      feature_dir=$(dirname "$state_file")
      feature_slug=$(basename "$feature_dir")
      # Skip aborted features
      if grep -q "^status: aborted" "$state_file" 2>/dev/null; then
        continue
      fi
      IN_PROGRESS_FEATURES+=("$feature_slug")
    fi
  done

  if [ ${#IN_PROGRESS_FEATURES[@]} -eq 1 ]; then
    ACTIVE_FEATURE="${IN_PROGRESS_FEATURES[0]}"
  elif [ ${#IN_PROGRESS_FEATURES[@]} -gt 1 ]; then
    # Multiple in-progress features, list them
    FEATURE_LIST=$(printf ', "%s"' "${IN_PROGRESS_FEATURES[@]}")
    FEATURE_LIST="[${FEATURE_LIST:2}]"
    CONTEXT="Multiple features are in-progress: ${FEATURE_LIST}. Run /afyapowers:switch to select one, or /afyapowers:features to see all."
    echo "{\"additionalContext\": \"$CONTEXT\"}"
    exit 0
  fi
fi

# No active feature found
if [ -z "$ACTIVE_FEATURE" ]; then
  echo '{}'
  exit 0
fi

# Read state.yaml for the active feature
STATE_FILE="$AFYA_DIR/$ACTIVE_FEATURE/state.yaml"
if [ ! -f "$STATE_FILE" ]; then
  echo '{}'
  exit 0
fi

# Extract key fields from state.yaml
FEATURE_NAME=$(grep "^feature:" "$STATE_FILE" | sed 's/^feature: *//')
CURRENT_PHASE=$(grep "^current_phase:" "$STATE_FILE" | sed 's/^current_phase: *//')
FEATURE_STATUS=$(grep "^status:" "$STATE_FILE" | head -1 | sed 's/^status: *//')
CREATED_AT=$(grep "^created_at:" "$STATE_FILE" | sed 's/^created_at: *//')

# Collect artifacts
ARTIFACTS=""
ARTIFACT_DIR="$AFYA_DIR/$ACTIVE_FEATURE/artifacts"
if [ -d "$ARTIFACT_DIR" ]; then
  ARTIFACTS=$(ls "$ARTIFACT_DIR" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
fi

# Count plan tasks if in implement phase
TASK_INFO=""
PLAN_FILE="$ARTIFACT_DIR/plan.md"
if [ "$CURRENT_PHASE" = "implement" ] && [ -f "$PLAN_FILE" ]; then
  TOTAL=$(grep -c '^\- \[' "$PLAN_FILE" 2>/dev/null || echo "0")
  DONE=$(grep -c '^\- \[x\]' "$PLAN_FILE" 2>/dev/null || echo "0")
  TASK_INFO=" ($DONE of $TOTAL tasks completed)"
fi

# Build context message
CONTEXT="You have an active feature: \\\"$FEATURE_NAME\\\" (started ${CREATED_AT%T*})\\nCurrent phase: ${CURRENT_PHASE}${TASK_INFO}\\nArtifacts: ${ARTIFACTS:-none}\\n\\nRun /afyapowers:status for details, or continue working on the current phase.\\n\\nIMPORTANT: You are operating within the afyapowers deterministic workflow. Do NOT advance phases autonomously. When the current phase is complete, suggest the user run /afyapowers:next."

echo "{\"additionalContext\": \"$CONTEXT\"}"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x hooks/session-start
```

- [ ] **Step 3: Verify script runs without errors when no .afyapowers directory exists**

Run: `cd /tmp && bash /Users/rafaelpapastamatiou/dev/afyapowers/hooks/session-start`
Expected: `{}`

- [ ] **Step 4: Commit**

```bash
git add hooks/session-start
git commit -m "feat: add session-start hook for active feature injection"
```

---

### Task 4: Artifact Templates

**Files:**
- Create: `templates/brainstorm.md`
- Create: `templates/tech-spec.md`
- Create: `templates/plan.md`
- Create: `templates/review.md`
- Create: `templates/completion.md`

- [ ] **Step 1: Create templates/brainstorm.md**

```markdown
# Brainstorm: {{feature_name}}

## Problem Statement
<!-- What problem are we solving and why -->

## Requirements
<!-- Key requirements discovered during brainstorming -->

## Constraints
<!-- Technical, business, or time constraints -->

## Approaches Considered
<!-- 2-3 approaches with trade-offs -->

### Approach 1: ...
### Approach 2: ...

## Chosen Approach
<!-- Which approach and why -->

## Open Questions
<!-- Anything unresolved -->
```

- [ ] **Step 2: Create templates/tech-spec.md**

```markdown
# Tech Spec: {{feature_name}}

## Overview
<!-- 1-2 sentence summary -->

## Architecture
<!-- Components, how they interact -->

## Data Flow
<!-- How data moves through the system -->

## API / Interface Changes
<!-- New or modified interfaces -->

## Error Handling
<!-- Failure modes and how they're handled -->

## Testing Strategy
<!-- What to test and how -->

## Dependencies
<!-- External dependencies or prerequisites -->
```

- [ ] **Step 3: Create templates/plan.md**

```markdown
# Implementation Plan: {{feature_name}}

## Tasks
<!-- Ordered, bite-sized tasks (2-5 min each) -->

- [ ] Task 1: ...
- [ ] Task 2: ...
- [ ] Task 3: ...

## Dependencies Between Tasks
<!-- Which tasks block others -->

## Testing Approach
<!-- RED-GREEN-REFACTOR per task -->
```

- [ ] **Step 4: Create templates/review.md**

```markdown
# Code Review: {{feature_name}}

## Spec Compliance Review
<!-- Does implementation match tech-spec? -->

### Findings

| Severity | Finding | Resolution |
|----------|---------|------------|

## Code Quality Review
<!-- Code standards, patterns, edge cases -->

### Findings

| Severity | Finding | Resolution |
|----------|---------|------------|

## Verdict
<!-- Approved / Changes Requested -->
```

- [ ] **Step 5: Create templates/completion.md**

```markdown
# Completion: {{feature_name}}

## Summary
<!-- What was delivered -->

## Changes Made
<!-- Key files and components changed -->

## How to Test
<!-- Steps to verify the feature works -->

## PR / Merge Info
<!-- Link to PR, branch name, merge details -->
```

- [ ] **Step 6: Commit**

```bash
git add templates/
git commit -m "feat: add artifact templates for all workflow phases"
```

---

## Chunk 2: Commands

All commands live in `commands/afyapowers/`. Each is a markdown prompt that the agent follows when the user invokes the corresponding slash command. Commands read/write YAML state files and invoke skills.

### Task 5: /afyapowers:new Command

**Files:**
- Create: `commands/afyapowers/new.md`

- [ ] **Step 1: Create the new command**

The command must:
1. Ask the user for a feature name/description
2. Generate a slug (lowercase, hyphens, strip special chars, max 50 chars)
3. Create `.afyapowers/<date>-<slug>/` directory structure
4. Handle naming collisions (append -2, -3, etc.)
5. Initialize `state.yaml` and `history.yaml`
6. Write the feature slug to `.afyapowers/active`
7. Invoke the brainstorming skill

```markdown
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
4. Check if `.afyapowers/<directory-name>/` already exists. If so, append `-2` (then `-3`, etc.) until unique
5. Create the directory structure:
   - `.afyapowers/<directory-name>/`
   - `.afyapowers/<directory-name>/artifacts/`

## Step 3: Initialize State Files

Create `.afyapowers/<directory-name>/state.yaml`:

```yaml
feature: <feature-name-from-user>
status: active
created_at: <current-ISO-8601-timestamp>
current_phase: brainstorm
phases:
  brainstorm:
    status: in_progress
    started_at: <current-ISO-8601-timestamp>
    artifacts: []
  design:
    status: pending
  plan:
    status: pending
  implement:
    status: pending
  review:
    status: pending
  complete:
    status: pending
```

Create `.afyapowers/<directory-name>/history.yaml`:

```yaml
events:
  - timestamp: <current-ISO-8601-timestamp>
    event: feature_created
    phase: brainstorm
    command: /afyapowers:new
    details: "Feature '<feature-name>' created"
  - timestamp: <current-ISO-8601-timestamp>
    event: phase_started
    phase: brainstorm
```

## Step 4: Set Active Feature

Write the directory name (e.g., `2026-03-12-add-submit-button`) to `.afyapowers/active`.

## Step 5: Confirm and Begin Brainstorming

Tell the user:
> Feature "<feature-name>" created at `.afyapowers/<directory-name>/`.
> Current phase: **brainstorm**
>
> Starting brainstorming...

Then invoke the **brainstorming** skill to begin the brainstorm phase. The brainstorming skill will guide the conversation to clarify requirements, explore approaches, and reach alignment.

When the brainstorming skill completes and produces the `brainstorm.md` artifact:
1. Save it to `.afyapowers/<directory-name>/artifacts/brainstorm.md`
2. Update `state.yaml` to add `brainstorm.md` to the brainstorm phase artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Brainstorm phase complete. Run `/afyapowers:next` to proceed to **design**."
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/new.md
git commit -m "feat: add /afyapowers:new command"
```

---

### Task 6: /afyapowers:next Command

**Files:**
- Create: `commands/afyapowers/next.md`

- [ ] **Step 1: Create the next command**

```markdown
# /afyapowers:next — Advance to Next Phase

You are advancing the active feature to the next workflow phase. Follow these steps exactly:

## Step 1: Identify Active Feature

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature."
3. Read `.afyapowers/<slug>/state.yaml`

## Step 2: Validate Current Phase Completion

Check that the current phase has produced its required artifacts:

| Current Phase | Validation |
|--------------|------------|
| brainstorm | `.afyapowers/<slug>/artifacts/brainstorm.md` exists |
| design | `.afyapowers/<slug>/artifacts/tech-spec.md` exists |
| plan | `.afyapowers/<slug>/artifacts/plan.md` exists |
| implement | Zero unchecked `- [ ]` items in `.afyapowers/<slug>/artifacts/plan.md` |
| review | `.afyapowers/<slug>/artifacts/review.md` exists AND its Verdict section contains "Approved" |
| complete | `.afyapowers/<slug>/artifacts/completion.md` exists |

If validation fails:
- Tell the user what's still needed (e.g., "The brainstorm artifact is missing. Complete the brainstorm phase first.")
- For implement: list the remaining unchecked tasks
- For review: if verdict is "Changes Requested", report the findings and explain what needs fixing
- Do NOT advance.

## Step 3: Handle Terminal Phase

If the current phase is `complete` and validation passes:
1. Update `state.yaml`: set `phases.complete.status` to `completed`, set `phases.complete.completed_at`, set feature-level `status` to `completed`
2. Append to `history.yaml`: `phase_completed` event for `complete`, then `feature_completed` event
3. Tell the user: "Feature '<feature-name>' is complete!"
4. Stop here — do not advance further.

## Step 4: Advance Phase

Determine the next phase from the ordered list: brainstorm → design → plan → implement → review → complete.

1. Update `state.yaml`:
   - Set current phase's `status` to `completed` and `completed_at` to current timestamp
   - Set next phase's `status` to `in_progress` and `started_at` to current timestamp
   - Set `current_phase` to the next phase name
2. Append to `history.yaml`:
   - `phase_completed` event for the current phase (include `command: /afyapowers:next`)
   - `phase_started` event for the next phase

## Step 5: Invoke Next Phase Skill

Tell the user which phase is starting, then invoke the appropriate skill:

| Next Phase | Skill to Invoke | What It Does |
|-----------|----------------|--------------|
| design | **design** skill | Produce tech spec from brainstorm output |
| plan | **writing-plans** skill | Break design into implementation tasks |
| implement | **implementing** skill | Execute tasks with TDD + subagents |
| review | **reviewing** skill | 2-step code review (spec compliance + quality) |
| complete | **completing** skill | Merge/PR/cleanup, produce completion summary |

When the skill completes and produces its artifact:
1. Save the artifact to `.afyapowers/<slug>/artifacts/`
2. Update `state.yaml` to add the artifact to the current phase's artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Phase '<current-phase>' complete. Run `/afyapowers:next` to proceed to **<next-phase>**."

For the `complete` phase, instead say: "Phase complete. Run `/afyapowers:next` to finalize the feature."
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/next.md
git commit -m "feat: add /afyapowers:next command"
```

---

### Task 7: /afyapowers:status Command

**Files:**
- Create: `commands/afyapowers/status.md`

- [ ] **Step 1: Create the status command**

```markdown
# /afyapowers:status — Show Feature Status

Display the current state of the active feature.

## Steps

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature."
3. Read `.afyapowers/<slug>/state.yaml`
4. Display the status in this format:

```
Feature: <feature-name>
Status: <active|completed|aborted>
Created: <date>
Current Phase: <phase-name>

Phases:
  ✅ brainstorm    — completed (artifacts: brainstorm.md)
  🔄 design        — in_progress (artifacts: tech-spec.md)
  ⏳ plan          — pending
  ⏳ implement     — pending
  ⏳ review        — pending
  ⏳ complete      — pending
```

Use ✅ for completed, 🔄 for in_progress, ⏳ for pending, ❌ for aborted.

If in the implement phase, also show task progress:
```
  🔄 implement     — in_progress (3 of 7 tasks completed)
```
Parse `artifacts/plan.md` to count checked vs unchecked items.
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/status.md
git commit -m "feat: add /afyapowers:status command"
```

---

### Task 8: /afyapowers:features Command

**Files:**
- Create: `commands/afyapowers/features.md`

- [ ] **Step 1: Create the features command**

```markdown
# /afyapowers:features — List All Features

List all features and their current states.

## Steps

1. Scan all directories under `.afyapowers/` (skip the `active` file)
2. For each directory, read `state.yaml`
3. Display a table:

```
| Feature | Phase | Status | Created |
|---------|-------|--------|---------|
| add-submit-button | implement | active | 2026-03-12 |
| fix-auth-flow | complete | completed | 2026-03-10 |
| refactor-api | brainstorm | aborted | 2026-03-11 |
```

4. Indicate which feature is currently active (from `.afyapowers/active`) with a marker like `→` or `(active)`.

If no `.afyapowers/` directory exists or it's empty, tell the user: "No features found. Run `/afyapowers:new` to start one."
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/features.md
git commit -m "feat: add /afyapowers:features command"
```

---

### Task 9: /afyapowers:switch Command

**Files:**
- Create: `commands/afyapowers/switch.md`

- [ ] **Step 1: Create the switch command**

```markdown
# /afyapowers:switch — Switch Active Feature

Switch the active feature context. This command accepts an optional argument: the feature name or slug.

## Steps

### If no argument provided:

1. List all non-aborted features from `.afyapowers/*/state.yaml`
2. Show them as a numbered list with current phase and status
3. Ask the user to pick one
4. Wait for their response

### Once a feature is selected (by argument or user choice):

1. Find the matching feature directory under `.afyapowers/` (match by slug or feature name)
2. Verify the feature is not aborted. If it is, tell the user: "Feature '<name>' is aborted and cannot be switched to. Run `/afyapowers:new` to start a new feature."
3. Write the feature's directory name to `.afyapowers/active`
4. Read the feature's `state.yaml`
5. Display its status (same format as `/afyapowers:status`)

This command does NOT modify either feature's `state.yaml`. Switching is purely a pointer change.
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/switch.md
git commit -m "feat: add /afyapowers:switch command"
```

---

### Task 10: /afyapowers:history Command

**Files:**
- Create: `commands/afyapowers/history.md`

- [ ] **Step 1: Create the history command**

```markdown
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
  [2026-03-12 10:30:00] phase_started — brainstorm
  [2026-03-12 10:42:00] artifact_created — brainstorm.md (brainstorm phase)
  [2026-03-12 10:45:00] phase_completed — brainstorm (via /afyapowers:next)
  [2026-03-12 10:45:00] phase_started — design
  [2026-03-12 10:50:00] artifact_created — tech-spec.md (design phase)
```

Format each event on one line with timestamp, event type, and relevant details.
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/history.md
git commit -m "feat: add /afyapowers:history command"
```

---

### Task 11: /afyapowers:abort Command

**Files:**
- Create: `commands/afyapowers/abort.md`

- [ ] **Step 1: Create the abort command**

```markdown
# /afyapowers:abort — Abort Current Feature

Abandon the active feature. This is irreversible — aborted features cannot be resumed.

## Steps

1. Read `.afyapowers/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature to abort."
3. Read `.afyapowers/<slug>/state.yaml`
4. Confirm with the user: "Are you sure you want to abort feature '<feature-name>'? This cannot be undone."
5. Wait for confirmation.

### On confirmation:

1. Update `state.yaml`:
   - Set feature-level `status` to `aborted`
   - Set the current in_progress phase's `status` to `aborted`
2. Append to `history.yaml`:
   - `feature_aborted` event with current timestamp and the phase it was aborted in
3. Clear `.afyapowers/active` (delete the file or empty it)
4. Tell the user: "Feature '<feature-name>' has been aborted. Run `/afyapowers:new` to start a new feature."
```

- [ ] **Step 2: Commit**

```bash
git add commands/afyapowers/abort.md
git commit -m "feat: add /afyapowers:abort command"
```

---

## Chunk 3: Phase Skills — Brainstorming, Design, Writing Plans

Phase skills are forked from superpowers and adapted to be phase-aware. Each skill reads the current feature state, does its work, produces an artifact from the template, and suggests `/afyapowers:next` when done.

### Task 12: Brainstorming Skill

**Files:**
- Create: `skills/brainstorming/SKILL.md`
- Create: `skills/brainstorming/spec-document-reviewer-prompt.md`

- [ ] **Step 1: Create skills/brainstorming/SKILL.md**

Fork from superpowers `skills/brainstorming/SKILL.md` with these adaptations:
- Remove the visual companion section (simplify for v1)
- Remove the TodoWrite/task creation references (commands handle workflow)
- Change spec output path from `docs/superpowers/specs/` to `.afyapowers/<feature>/artifacts/brainstorm.md`
- Add phase-awareness: read `state.yaml` at start, confirm current phase is `brainstorm`
- Remove the "Transition to implementation" step (the `/afyapowers:next` command handles transitions)
- Replace "Invoke writing-plans skill" terminal state with "Suggest `/afyapowers:next`"
- Keep: one question at a time, multiple choice preferred, 2-3 approaches, incremental validation
- Keep: spec review loop with subagent dispatch (max 5 iterations)
- Keep: user review gate before proceeding

The skill should end with: "Brainstorm phase complete. Run `/afyapowers:next` to proceed to **design**."

- [ ] **Step 2: Create skills/brainstorming/spec-document-reviewer-prompt.md**

Fork from superpowers `skills/brainstorming/spec-document-reviewer-prompt.md`. No changes needed — the reviewer checks completeness, coverage, consistency, clarity, YAGNI, scope, and architecture.

- [ ] **Step 3: Commit**

```bash
git add skills/brainstorming/
git commit -m "feat: add brainstorming skill (forked from superpowers)"
```

---

### Task 13: Design Skill

**Files:**
- Create: `skills/design/SKILL.md`

- [ ] **Step 1: Create skills/design/SKILL.md**

This is a new skill (superpowers doesn't have a separate "design" phase — it's part of brainstorming). The design skill:

1. Reads the brainstorm artifact (`.afyapowers/<feature>/artifacts/brainstorm.md`) to understand requirements
2. Reads the tech-spec template from `templates/tech-spec.md`
3. Guides the user through producing a tech spec:
   - Architecture decisions
   - Component design
   - Data flow
   - API/interface changes
   - Error handling strategy
   - Testing strategy
   - Dependencies
4. Validates the tech spec covers all sections
5. Dispatches a spec-document-reviewer subagent (reuse brainstorming's reviewer prompt)
6. Saves the completed spec to `.afyapowers/<feature>/artifacts/tech-spec.md`

```markdown
---
name: design
description: "Use when the current afyapowers phase is design — produces a tech spec from brainstorm output"
---

# Design Phase

Produce a detailed technical specification from the brainstorm artifact.

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `design`
3. If not in design phase, tell the user the current phase and stop

## Process

### Step 1: Review Brainstorm Output

Read `.afyapowers/<feature>/artifacts/brainstorm.md` to understand:
- Problem statement and requirements
- Constraints
- Chosen approach

### Step 2: Produce Tech Spec

Read the template from `templates/tech-spec.md`. Work through each section with the user:

1. **Overview** — Summarize the feature in 1-2 sentences
2. **Architecture** — Define components and how they interact. Ask the user clarifying questions if the brainstorm doesn't fully specify architecture.
3. **Data Flow** — How data moves through the system
4. **API / Interface Changes** — New or modified interfaces
5. **Error Handling** — Failure modes and recovery strategies
6. **Testing Strategy** — What to test and how (unit, integration, e2e)
7. **Dependencies** — External dependencies or prerequisites

Present each section for validation. Scale detail to complexity — a few sentences if straightforward, more detail if nuanced.

### Step 3: Spec Review

After the user approves the tech spec:

1. Save it to `.afyapowers/<feature>/artifacts/tech-spec.md`
2. Dispatch a spec-document-reviewer subagent using `skills/brainstorming/spec-document-reviewer-prompt.md`
3. If issues found: fix and re-dispatch (max 5 iterations)
4. If approved: proceed to user review

### Step 4: User Review

Ask the user to review the written tech spec:
> "Tech spec saved to `.afyapowers/<feature>/artifacts/tech-spec.md`. Please review and let me know if you'd like any changes."

Wait for approval.

### Step 5: Complete

Update `state.yaml` to add `tech-spec.md` to the design phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Design phase complete. Run `/afyapowers:next` to proceed to **plan**."

## Key Principles

- Build on the brainstorm output — don't re-ask questions already answered
- Focus on technical decisions, not requirements (those are in the brainstorm)
- Be specific about interfaces and data flow
- YAGNI — only design what's needed for the chosen approach
```

- [ ] **Step 2: Commit**

```bash
git add skills/design/
git commit -m "feat: add design skill for tech spec production"
```

---

### Task 14: Writing Plans Skill

**Files:**
- Create: `skills/writing-plans/SKILL.md`
- Create: `skills/writing-plans/plan-document-reviewer-prompt.md`

- [ ] **Step 1: Create skills/writing-plans/SKILL.md**

Fork from superpowers `skills/writing-plans/SKILL.md` with these adaptations:
- Change plan output path from `docs/superpowers/plans/` to `.afyapowers/<feature>/artifacts/plan.md`
- Add phase-awareness: read `state.yaml` at start, confirm current phase is `plan`
- Read the tech spec from `.afyapowers/<feature>/artifacts/tech-spec.md` as input
- Replace the header template's `superpowers:subagent-driven-development` reference with `afyapowers implementing skill`
- Replace execution handoff with "Suggest `/afyapowers:next`"
- Keep: file structure mapping, bite-sized task granularity (2-5 min), task structure template, plan review loop
- Keep: DRY, YAGNI, TDD, frequent commits
- Keep: complete code in plan, exact file paths, exact commands with expected output

The skill should end with: "Plan phase complete. Run `/afyapowers:next` to proceed to **implement**."

- [ ] **Step 2: Create skills/writing-plans/plan-document-reviewer-prompt.md**

Fork from superpowers `skills/writing-plans/plan-document-reviewer-prompt.md`. No changes needed — the reviewer checks completeness, spec alignment, task decomposition, file structure, syntax, chunk size.

- [ ] **Step 3: Commit**

```bash
git add skills/writing-plans/
git commit -m "feat: add writing-plans skill (forked from superpowers)"
```

---

## Chunk 4: Phase Skills — Implementing, Reviewing, Completing

### Task 15: Implementing Skill

**Files:**
- Create: `skills/implementing/SKILL.md`
- Create: `skills/implementing/implementer-prompt.md`
- Create: `skills/implementing/spec-reviewer-prompt.md`
- Create: `skills/implementing/code-quality-reviewer-prompt.md`

- [ ] **Step 1: Create skills/implementing/SKILL.md**

Fork from superpowers `skills/subagent-driven-development/SKILL.md` with these adaptations:
- Add phase-awareness: read `state.yaml` at start, confirm current phase is `implement`
- Read the plan from `.afyapowers/<feature>/artifacts/plan.md`
- Read the tech spec from `.afyapowers/<feature>/artifacts/tech-spec.md` for context
- Replace all `superpowers:` skill references with afyapowers equivalents
- Update subagent prompt template paths to `skills/implementing/`
- Keep: fresh subagent per task, two-stage review (spec → quality), status handling, model selection guidance
- Keep: never dispatch multiple implementers in parallel, max 5 review iterations
- When all tasks complete, mark plan checkboxes as done (`- [x]`)
- End with: "Implement phase complete. Run `/afyapowers:next` to proceed to **review**."

- [ ] **Step 2: Create skills/implementing/implementer-prompt.md**

Fork from superpowers `skills/subagent-driven-development/implementer-prompt.md`. Adaptations:
- Replace `superpowers:test-driven-development` references with `afyapowers test-driven-development`
- Replace `superpowers:systematic-debugging` references with `afyapowers systematic-debugging`
- Keep: task description injection, context/scene-setting, questions encouraged, code organization guidance, self-review checklist, report format

- [ ] **Step 3: Create skills/implementing/spec-reviewer-prompt.md**

Fork from superpowers `skills/subagent-driven-development/spec-reviewer-prompt.md`. No significant changes needed — the reviewer verifies what was requested vs what was built by reading code, not trusting reports.

- [ ] **Step 4: Create skills/implementing/code-quality-reviewer-prompt.md**

Create based on superpowers `skills/requesting-code-review/code-reviewer.md`. This is the code quality review template with placeholders for: what was implemented, plan/requirements, base SHA, head SHA, description. Includes review checklist (Code Quality, Architecture, Testing, Requirements, Production Readiness) and output format (Strengths, Issues by severity, Recommendations, Assessment).

- [ ] **Step 5: Commit**

```bash
git add skills/implementing/
git commit -m "feat: add implementing skill with subagent prompts (forked from superpowers)"
```

---

### Task 16: Reviewing Skill

**Files:**
- Create: `skills/reviewing/SKILL.md`
- Create: `skills/reviewing/code-reviewer.md`

- [ ] **Step 1: Create skills/reviewing/SKILL.md**

This skill orchestrates the 2-step review at the feature level (after all implementation tasks are done):

```markdown
---
name: reviewing
description: "Use when the current afyapowers phase is review — performs 2-step code review (spec compliance + quality)"
---

# Review Phase

Perform a comprehensive 2-step code review of the completed feature implementation.

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `review`
3. If not in review phase, tell the user the current phase and stop

## Process

### Step 1: Gather Context

1. Read `.afyapowers/<feature>/artifacts/tech-spec.md` — the requirements
2. Read `.afyapowers/<feature>/artifacts/plan.md` — the implementation plan
3. Get the git diff for the feature's changes (use `git log` and `git diff` to identify the relevant commits)

### Step 2: Spec Compliance Review

Dispatch a spec-reviewer subagent using `skills/implementing/spec-reviewer-prompt.md`:
- Provide the tech spec content as "what was requested"
- Provide a summary of implemented changes as "what was built"
- Provide the relevant code diff

If the reviewer finds spec gaps:
1. Report the findings to the user
2. The user fixes issues (code changes happen during review phase)
3. Re-dispatch the spec reviewer
4. Repeat until spec-compliant (max 5 iterations)

### Step 3: Code Quality Review

Dispatch a code-quality-reviewer subagent using `skills/reviewing/code-reviewer.md`:
- Provide: what was implemented, plan reference, base/head SHAs, description

If the reviewer finds issues:
1. Categorize by severity (Critical, Important, Minor)
2. Critical and Important: must be fixed before proceeding
3. Minor: note for later, do not block
4. Fix issues and re-dispatch (max 5 iterations)

### Step 4: Produce Review Artifact

Read the template from `templates/review.md`. Fill in:
- Spec compliance findings and resolutions
- Code quality findings and resolutions
- Final verdict: "Approved" (only if both reviews pass)

Save to `.afyapowers/<feature>/artifacts/review.md`

### Step 5: Complete

Update `state.yaml` to add `review.md` to the review phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Review phase complete. Run `/afyapowers:next` to proceed to **complete**."

**Important:** The verdict MUST be "Approved" for `/afyapowers:next` to accept the transition. If issues remain, keep the verdict as "Changes Requested" and work with the user to resolve them.
```

- [ ] **Step 2: Create skills/reviewing/code-reviewer.md**

Fork from superpowers `skills/requesting-code-review/code-reviewer.md`. Keep the full review template with placeholders and checklist. No significant changes needed.

- [ ] **Step 3: Commit**

```bash
git add skills/reviewing/
git commit -m "feat: add reviewing skill with code reviewer template"
```

---

### Task 17: Completing Skill

**Files:**
- Create: `skills/completing/SKILL.md`

- [ ] **Step 1: Create skills/completing/SKILL.md**

```markdown
---
name: completing
description: "Use when the current afyapowers phase is complete — handles merge/PR/cleanup and produces completion summary"
---

# Complete Phase

Finalize the feature: verify everything works, merge or create PR, produce completion summary.

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `complete`
3. If not in complete phase, tell the user the current phase and stop

## Process

### Step 1: Final Verification

1. Run the project's test suite — all tests must pass
2. Verify no uncommitted changes remain
3. Read `.afyapowers/<feature>/artifacts/review.md` — confirm verdict is "Approved"

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

### Step 4: Produce Completion Artifact

Read the template from `templates/completion.md`. Fill in:
- Summary of what was delivered (from tech spec + review)
- Key files and components changed (from git diff)
- How to test (from tech spec's testing strategy)
- PR/merge info (from Step 3)

Save to `.afyapowers/<feature>/artifacts/completion.md`

### Step 5: Complete

Update `state.yaml` to add `completion.md` to the complete phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Complete phase done. Run `/afyapowers:next` to finalize the feature."

When the user runs `/afyapowers:next`, the command will mark the feature as `completed`.
```

- [ ] **Step 2: Commit**

```bash
git add skills/completing/
git commit -m "feat: add completing skill for feature finalization"
```

---

## Chunk 5: Cross-Cutting Skills

These skills are used within phases (mainly implement) and are forked directly from superpowers with minimal changes — mostly replacing `superpowers:` references with afyapowers equivalents.

### Task 18: Test-Driven Development Skill

**Files:**
- Create: `skills/test-driven-development/SKILL.md`
- Create: `skills/test-driven-development/testing-anti-patterns.md`

- [ ] **Step 1: Create skills/test-driven-development/SKILL.md**

Fork from superpowers `skills/test-driven-development/SKILL.md`. Changes:
- Replace any `superpowers:` references in Integration section
- Keep everything else as-is: Iron Law, RED-GREEN-REFACTOR cycle, good tests criteria, rationalizations, red flags, verification checklist

- [ ] **Step 2: Create skills/test-driven-development/testing-anti-patterns.md**

Fork from superpowers `skills/test-driven-development/testing-anti-patterns.md`. No changes needed.

- [ ] **Step 3: Commit**

```bash
git add skills/test-driven-development/
git commit -m "feat: add TDD skill (forked from superpowers)"
```

---

### Task 19: Systematic Debugging Skill

**Files:**
- Create: `skills/systematic-debugging/SKILL.md`
- Create: `skills/systematic-debugging/root-cause-tracing.md`

- [ ] **Step 1: Create skills/systematic-debugging/SKILL.md**

Fork from superpowers `skills/systematic-debugging/SKILL.md`. Changes:
- Replace `superpowers:test-driven-development` → afyapowers TDD skill reference
- Replace `superpowers:verification-before-completion` → afyapowers verification skill reference
- Keep everything else: 4 phases, root cause investigation, pattern analysis, hypothesis testing, implementation, red flags

- [ ] **Step 2: Create skills/systematic-debugging/root-cause-tracing.md**

Fork from superpowers. No changes needed.

- [ ] **Step 3: Commit**

```bash
git add skills/systematic-debugging/
git commit -m "feat: add systematic-debugging skill (forked from superpowers)"
```

---

### Task 20: Verification Before Completion Skill

**Files:**
- Create: `skills/verification-before-completion/SKILL.md`

- [ ] **Step 1: Create skills/verification-before-completion/SKILL.md**

Fork from superpowers `skills/verification-before-completion/SKILL.md`. No changes needed — this skill is self-contained with no external skill references.

- [ ] **Step 2: Commit**

```bash
git add skills/verification-before-completion/
git commit -m "feat: add verification-before-completion skill (forked from superpowers)"
```

---

### Task 21: Using Git Worktrees Skill

**Files:**
- Create: `skills/using-git-worktrees/SKILL.md`

- [ ] **Step 1: Create skills/using-git-worktrees/SKILL.md**

Fork from superpowers `skills/using-git-worktrees/SKILL.md`. Changes:
- Replace `superpowers:` references in Integration section with afyapowers equivalents
- Keep: directory selection, safety verification, creation steps, auto-detect setup, common mistakes

- [ ] **Step 2: Commit**

```bash
git add skills/using-git-worktrees/
git commit -m "feat: add using-git-worktrees skill (forked from superpowers)"
```

---

### Task 22: Dispatching Parallel Agents Skill

**Files:**
- Create: `skills/dispatching-parallel-agents/SKILL.md`

- [ ] **Step 1: Create skills/dispatching-parallel-agents/SKILL.md**

Fork from superpowers `skills/dispatching-parallel-agents/SKILL.md`. No significant changes needed — this skill is largely self-contained.

- [ ] **Step 2: Commit**

```bash
git add skills/dispatching-parallel-agents/
git commit -m "feat: add dispatching-parallel-agents skill (forked from superpowers)"
```

---

### Task 23: Subagent-Driven Development Skill

**Files:**
- Create: `skills/subagent-driven-development/SKILL.md`

- [ ] **Step 1: Create skills/subagent-driven-development/SKILL.md**

Fork from superpowers `skills/subagent-driven-development/SKILL.md`. Changes:
- Replace all `superpowers:` skill references with afyapowers equivalents
- Update prompt template paths to point to `skills/implementing/` (where the prompt templates live)
- Keep: process flow, model selection, status handling, red flags, advantages

Note: This skill is the orchestration pattern used BY the implementing skill. The implementing skill is phase-aware and delegates to this skill's patterns for task execution.

- [ ] **Step 2: Commit**

```bash
git add skills/subagent-driven-development/
git commit -m "feat: add subagent-driven-development skill (forked from superpowers)"
```

---

### Task 24: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Write a README covering:
- What afyapowers is (deterministic phase-gated workflow plugin)
- Installation (Claude Code plugin install)
- Quick start (`/afyapowers:new` → work through phases → `/afyapowers:next`)
- Commands reference (table of all 7 commands)
- Workflow phases (the 6 phases with descriptions)
- Project structure (what `.afyapowers/` contains)

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with installation and usage guide"
```
