# afyapowers

A deterministic, phase-gated development workflow plugin for Claude Code, forked from [superpowers](https://github.com/obra/superpowers). Enforces structured feature development with persistent state, session continuity, and full auditability.

afyapowers builds on superpowers' skills (brainstorming, TDD, systematic debugging, subagent-driven development, etc.) and adapts them into a 6-phase gated workflow where each phase produces a persistent artifact before the next can begin.

## Installation

```bash
claude plugin install afyapowers
```

## Quick Start

```bash
# Start a new feature
/afyapowers:new

# Work through each phase, advancing with:
/afyapowers:next

# Check current status at any time
/afyapowers:status
```

## Workflow Phases

Every feature progresses through 6 ordered phases:

| Phase | What Happens | Artifact |
|-------|-------------|----------|
| **Brainstorm** | Clarify requirements, explore approaches, reach alignment | `brainstorm.md` |
| **Design** | Produce detailed technical specification | `tech-spec.md` |
| **Plan** | Break design into bite-sized implementation tasks | `plan.md` |
| **Implement** | Execute tasks with TDD and subagent-driven development | Updated `plan.md` |
| **Review** | 2-step code review (spec compliance + quality) | `review.md` |
| **Complete** | Merge/PR/cleanup and completion summary | `completion.md` |

Phases are gated — you must complete the current phase's artifact before advancing to the next.

## Commands

| Command | Description |
|---------|-------------|
| `/afyapowers:new` | Start a new feature workflow |
| `/afyapowers:next` | Advance to the next phase (validates current phase completion) |
| `/afyapowers:status` | Show current feature status and phase progress |
| `/afyapowers:features` | List all features and their states |
| `/afyapowers:switch` | Switch the active feature context |
| `/afyapowers:history` | Show the full event timeline for the active feature |
| `/afyapowers:abort` | Abandon the active feature (irreversible) |

## Project Structure

```
.afyapowers/
  active                    # Current active feature slug
  <date>-<slug>/
    state.yaml              # Feature state (phase, status, artifacts)
    history.yaml            # Full event timeline
    artifacts/
      brainstorm.md         # Brainstorm output
      tech-spec.md          # Technical specification
      plan.md               # Implementation plan with checkboxes
      review.md             # Code review findings and verdict
      completion.md         # Completion summary
```

## Skills

### Phase Skills
- **brainstorming** — Collaborative design exploration
- **design** — Tech spec production from brainstorm output
- **writing-plans** — Implementation plan creation from tech specs
- **implementing** — Subagent-driven task execution with two-stage review
- **reviewing** — Spec compliance + code quality review
- **completing** — Merge/PR/cleanup and summary

### Cross-Cutting Skills
- **test-driven-development** — RED-GREEN-REFACTOR cycle
- **systematic-debugging** — Root cause investigation before fixes
- **verification-before-completion** — Evidence before claims
- **using-git-worktrees** — Isolated workspaces for feature work
- **dispatching-parallel-agents** — Parallel investigation of independent problems
- **subagent-driven-development** — Fresh subagent per task with review gates

## License

MIT
