# afyapowers Framework Design

## Overview

afyapowers is a Claude Code / Cursor plugin that enforces a deterministic, phase-gated development workflow with persistent state and full auditability. It is a fork/replacement of superpowers, adapting all skill content and customizing it for a company-specific deterministic workflow.

The core principle: **the user controls all workflow transitions through commands, the agent never auto-advances phases.**

### Problems Solved

1. **Loss of context across sessions** — Per-feature state files let a new session pick up exactly where the previous one stopped.
2. **Agent autonomy is too high** — Explicit phase gates via commands prevent the agent from jumping ahead or skipping steps.
3. **Lack of auditability** — Append-only history files record every transition, decision, and artifact creation.

## Architecture

The plugin consists of four components:

1. **Commands** (`.claude/commands/afyapowers/`) — 7 slash commands that control workflow transitions. Each command is a markdown prompt that reads current state, validates the phase, performs its action, and updates state.
2. **Skills** (forked from superpowers, adapted) — 12 skills total: 6 phase skills (one per workflow phase) + 6 cross-cutting skills (TDD, debugging, subagents, parallel agents, verification, worktrees). Phase skills are phase-aware: they read current state, produce artifacts from templates, and suggest the next command when done.
3. **State directory** (`.afyapowers/<date>-<feature-name>/`) — Per-feature directory containing `state.yaml`, `history.yaml`, and `artifacts/`.
4. **Templates** — Shipped with the plugin. Each phase has a corresponding artifact template that gets populated and saved into the feature's artifacts directory.

## Plugin Directory Structure

```text
afyapowers/                          # Plugin repo
├── .claude-plugin/
│   └── plugin.json                  # Plugin metadata
├── hooks/
│   ├── hooks.json                   # Session-start hook config
│   └── session-start                # Injects active feature context
├── commands/
│   └── afyapowers/
│       ├── new.md                   # /afyapowers:new
│       ├── next.md                  # /afyapowers:next
│       ├── status.md                # /afyapowers:status
│       ├── features.md              # /afyapowers:features
│       ├── switch.md                # /afyapowers:switch
│       ├── history.md               # /afyapowers:history
│       └── abort.md                 # /afyapowers:abort
├── skills/
│   ├── brainstorming/
│   │   └── SKILL.md
│   ├── design/
│   │   └── SKILL.md
│   ├── writing-plans/
│   │   └── SKILL.md
│   ├── implementing/
│   │   ├── SKILL.md
│   │   ├── implementer-prompt.md
│   │   ├── spec-reviewer-prompt.md
│   │   └── code-quality-reviewer-prompt.md
│   ├── reviewing/
│   │   ├── SKILL.md
│   │   └── code-reviewer.md
│   ├── completing/
│   │   └── SKILL.md
│   ├── test-driven-development/
│   │   ├── SKILL.md
│   │   └── testing-anti-patterns.md
│   ├── systematic-debugging/
│   │   ├── SKILL.md
│   │   └── root-cause-tracing.md
│   ├── subagent-driven-development/
│   │   └── SKILL.md
│   ├── dispatching-parallel-agents/
│   │   └── SKILL.md
│   ├── verification-before-completion/
│   │   └── SKILL.md
│   └── using-git-worktrees/
│       └── SKILL.md
├── templates/
│   ├── brainstorm.md
│   ├── tech-spec.md
│   ├── plan.md
│   ├── review.md
│   └── completion.md
└── README.md
```

## User Project Runtime Structure

Created at runtime in the user's project:

```text
.afyapowers/
├── active                               # Contains slug of active feature
├── 2026-03-12-add-submit-button/
│   ├── state.yaml
│   ├── history.yaml
│   └── artifacts/
│       ├── brainstorm.md
│       ├── tech-spec.md
│       └── plan.md
└── 2026-03-10-fix-auth-flow/
    ├── state.yaml
    ├── history.yaml
    └── artifacts/
        ├── brainstorm.md
        ├── tech-spec.md
        ├── plan.md
        ├── review.md
        └── completion.md
```

The `.afyapowers/` directory should be committed to the repo for auditability and team visibility.

### Active Feature Tracking

The file `.afyapowers/active` contains the directory name (slug) of the currently active feature, e.g.:

```text
2026-03-12-add-submit-button
```

This file is written by `/afyapowers:new` and `/afyapowers:switch`. The session-start hook reads it to inject the active feature context. If the file is missing or references a non-existent feature, the hook falls back to scanning for features with `in_progress` phases.

### Feature Naming

Feature directory names follow the format `<YYYY-MM-DD>-<slug>` where:
- Date is the creation date
- Slug is derived from the feature name: lowercased, spaces replaced with hyphens, special characters stripped, max 50 characters
- On collision (same date + slug), append `-2`, `-3`, etc.

## Workflow Phases

6 sequential phases, each with a dedicated skill and artifact:

| Phase | Skill | Artifact | Description |
|-------|-------|----------|-------------|
| brainstorm | `brainstorming` | `brainstorm.md` | Clarify requirements, explore approaches, reach alignment |
| design | `design` | `tech-spec.md` | Architecture, components, data flow, error handling, testing strategy |
| plan | `writing-plans` | `plan.md` | Break design into ordered, bite-sized tasks with checkboxes |
| implement | `implementing` | Code + tests in repo (no artifact file — the code is the artifact) | Execute tasks using TDD + subagents |
| review | `reviewing` | `review.md` | 2-step review: spec compliance then code quality |
| complete | `completing` | `completion.md` | Merge/PR/cleanup, summarize what was delivered |

### Cross-Cutting Skills

Used within phases (mainly implement), not tied to a single phase:

| Skill | When Used |
|-------|-----------|
| `test-driven-development` | Mandatory during implement — all subagents follow RED-GREEN-REFACTOR |
| `systematic-debugging` | When bugs or test failures are encountered |
| `subagent-driven-development` | Orchestrates implementer subagents during implement phase |
| `dispatching-parallel-agents` | When multiple independent tasks can run in parallel |
| `verification-before-completion` | Before any claim of "done" — evidence before assertions |
| `using-git-worktrees` | Optional isolation during implement phase |

### Phase-Aware Skill Behavior

Each phase skill follows this pattern:

1. Read `.afyapowers/<feature>/state.yaml` to confirm it's the right phase
2. Do the work (brainstorm, design, plan, etc.)
3. Produce the artifact from the template into `.afyapowers/<feature>/artifacts/`
4. Append `artifact_created` event to `history.yaml`
5. Suggest: "Phase complete. Run `/afyapowers:next` to proceed to [next phase]."

## State Files

### state.yaml

Source of truth for current feature state. Always read before any action.

```yaml
feature: add-submit-button
status: active                # active | completed | aborted
created_at: 2026-03-12T10:30:00Z
current_phase: design
phases:
  brainstorm:
    status: completed
    started_at: 2026-03-12T10:30:00Z
    completed_at: 2026-03-12T10:45:00Z
    artifacts:
      - brainstorm.md
  design:
    status: in_progress
    started_at: 2026-03-12T10:45:00Z
    artifacts:
      - tech-spec.md
  plan:
    status: pending
  implement:
    status: pending
  review:
    status: pending
  complete:
    status: pending
```

**Rules:**
- Feature statuses: `active` → `completed` or `aborted`
- Phase statuses: `pending` → `in_progress` → `completed` (or `aborted`)
- Only one phase can be `in_progress` at a time per feature
- A phase cannot start until the previous phase is `completed`
- Multiple features can be `active` simultaneously — the `active` file determines which one the agent works on

### history.yaml

Append-only audit trail. Events are never modified or deleted.

```yaml
events:
  - timestamp: 2026-03-12T10:30:00Z
    event: feature_created
    phase: brainstorm
    command: /afyapowers:new
    details: "Feature 'add-submit-button' created"

  - timestamp: 2026-03-12T10:30:00Z
    event: phase_started
    phase: brainstorm

  - timestamp: 2026-03-12T10:42:00Z
    event: artifact_created
    phase: brainstorm
    artifact: brainstorm.md

  - timestamp: 2026-03-12T10:45:00Z
    event: phase_completed
    phase: brainstorm
    command: /afyapowers:next

  - timestamp: 2026-03-12T10:45:00Z
    event: phase_started
    phase: design

  - timestamp: 2026-03-12T10:50:00Z
    event: artifact_created
    phase: design
    artifact: tech-spec.md
```

## Commands

### /afyapowers:new

- Asks user for a feature name/description
- Creates `.afyapowers/<date>-<slug>/` directory
- Initializes `state.yaml` with all phases as `pending`, sets brainstorm to `in_progress`
- Initializes `history.yaml` with `feature_created` and `phase_started` events
- Invokes the brainstorming skill within the brainstorm phase context

### /afyapowers:next

- Reads `state.yaml`, identifies current phase
- Validates that the current phase has produced its required artifacts
- If current phase is `complete`: marks feature `status: completed`, appends `feature_completed` event to `history.yaml`, and reports "Feature complete." Does **not** advance further.
- Otherwise: marks current phase as `completed`, next phase as `in_progress`
- Appends `phase_completed` + `phase_started` events to `history.yaml`
- Invokes the skill for the new phase

**Artifact validation:**

| Phase Completing | Required Artifact | Validation Method |
|-----------------|-------------------|-------------------|
| brainstorm | `brainstorm.md` | File exists in `artifacts/` |
| design | `tech-spec.md` | File exists in `artifacts/` |
| plan | `plan.md` | File exists in `artifacts/` |
| implement | All plan tasks done | Zero unchecked `- [ ]` items in `artifacts/plan.md` |
| review | `review.md` with "Approved" | File exists and Verdict section contains "Approved" |
| complete | `completion.md` | File exists in `artifacts/` |

**Implement phase validation:** The agent parses `artifacts/plan.md` and checks for unchecked `- [ ]` items. If any remain, it lists the incomplete tasks and does not advance. Tasks may be added or removed during the implement phase — validation always checks the current state of the file.

**Review phase rejection flow:** If the review verdict is "Changes Requested", `/afyapowers:next` will not advance. The agent reports the review findings. The user fixes issues during the review phase (code changes, re-review) until the verdict is "Approved", then runs `/afyapowers:next` again.

If the artifact is missing or validation fails, the agent tells the user what's still needed and does **not** advance.

### /afyapowers:status

- Reads `state.yaml` for the active feature
- Displays: feature name, current phase, status of all phases, artifacts produced

### /afyapowers:features

- Scans all directories under `.afyapowers/`
- Reads each `state.yaml`
- Displays a table: feature name, current phase, created date, status

### /afyapowers:switch

- Lists available features (excluding aborted) if no argument provided
- Writes the selected feature slug to `.afyapowers/active`
- Displays its current status
- Does **not** modify either feature's `state.yaml` — switching is purely a pointer change

### /afyapowers:history

- Reads `history.yaml` for the active feature
- Displays the full event timeline in a readable format

### /afyapowers:abort

- Marks current phase as `aborted` in `state.yaml`
- Sets feature-level `status: aborted`
- Appends `feature_aborted` event to `history.yaml`
- If the aborted feature was the active feature, clears `.afyapowers/active`

**Aborted features are read-only:** They appear in `/afyapowers:features` and `/afyapowers:history` but cannot be switched to or resumed. To retry, create a new feature with `/afyapowers:new`.

## Session Continuity

### Session-Start Hook

The hook is configured in `hooks/hooks.json` (same format as superpowers):

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

The `hooks/session-start` shell script:

1. Reads `.afyapowers/active` to find the active feature
2. If no active file, scans `.afyapowers/*/state.yaml` for features with `in_progress` phases
3. Reads the active feature's `state.yaml`
4. Outputs JSON with `additionalContext` containing: feature name, current phase, phase statuses, artifacts produced
5. If multiple features are in-progress and no active file exists, lists them and asks which one to resume

### What the Agent Sees

```text
You have an active feature: "add-submit-button" (started 2026-03-12)
Current phase: implement (3 of 7 tasks completed)
Artifacts: brainstorm.md, tech-spec.md, plan.md

Run /afyapowers:status for details, or continue working on the current phase.
```

### How the Agent Picks Up

- Reads `state.yaml` to know the current phase
- Reads artifacts to understand decisions already made (e.g., reads `tech-spec.md` to understand the design before continuing implementation)
- Reads `plan.md` to see which tasks are checked off vs remaining
- Reads `history.yaml` if it needs to understand what happened previously

No special "resume" command needed — the hook + state files give the agent everything it needs.

## Artifact Templates

Shipped with the plugin. Each phase has a corresponding template. Skills are responsible for reading the template, replacing `{{feature_name}}` with the feature name from `state.yaml`, filling in the sections, and saving the result to `artifacts/`. The only supported template variable is `{{feature_name}}`.

### templates/brainstorm.md

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

### templates/tech-spec.md

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

### templates/plan.md

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

### templates/review.md

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

### templates/completion.md

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

## Design Decisions

1. **Fork over layer** — Full control over skill content for company-specific customizations, no dependency on superpowers.
2. **Commands over auto-advance** — User explicitly controls all phase transitions. Agent suggests but never acts.
3. **YAML over database** — Simple, human-readable, version-controllable state files.
4. **Separate history file** — Keeps `state.yaml` clean and focused on current state. History is append-only.
5. **Per-feature directories** — Multiple features can be active simultaneously. Each is self-contained.
6. **Instruction-based validation over programmatic** — Commands are markdown prompts, not scripts. Simpler, can graduate to hooks/CLI later if needed.
7. **Shipped templates, no overrides** — YAGNI. Override mechanism can be added later if needed.
