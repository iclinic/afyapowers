# afyapowers

A deterministic, phase-gated development workflow plugin for Claude Code, forked from [superpowers](https://github.com/obra/superpowers). Enforces structured feature development with persistent state, session continuity, and full auditability.

afyapowers builds on superpowers' skills (TDD, systematic debugging, subagent-driven development, etc.) and adapts them into a 5-phase gated workflow where each phase produces a persistent artifact before the next can begin.

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

Every feature progresses through 5 ordered phases:

| Phase | What Happens | Artifact |
|-------|-------------|----------|
| **Design** | Clarify requirements, explore approaches, define architecture. Optionally pulls context from JIRA issues and Figma designs. | `design.md` |
| **Plan** | Break design into implementation tasks with dependency graphs. Infers Figma component/screen tasks from the design's Node Map. Validates no file overlap between parallel tasks. | `plan.md` |
| **Implement** | Execute tasks via wave-based subagent dispatch with TDD. Respects dependency order and Figma rate limits (max 4 Figma tasks per wave). Each subagent self-reviews and flags concerns. | Updated `plan.md` |
| **Review** | 2-step code review: spec compliance then code quality. Iterates up to 5 times until verdict is "Approved". | `review.md` |
| **Complete** | Run test suite, merge/PR/cleanup, auto-generate living documentation. | `completion.md` |

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
| `/afyapowers:component` | Develop a Figma component (standalone, outside the 5-phase workflow) |

## Integrations

### JIRA

During the **Design** phase, you can optionally provide a JIRA issue key. afyapowers fetches the issue context (summary, description, acceptance criteria) via the Atlassian MCP server and incorporates it into the design spec.

### Figma

Figma integration spans multiple phases:

- **Design** — Detects UI-related keywords and prompts for Figma URLs. Performs a shallow metadata call to build a Node Map (page > section > component, up to depth 2).
- **Plan** — Infers Figma tasks from the Node Map without additional MCP calls. Layer 1 tasks cover reusable components; Layer 2 tasks cover screens that depend on them.
- **Implement** — Subagents call `get_design_context`, `get_screenshot`, and `get_variable_defs` for full design fidelity. Rate-limited to 4 Figma tasks per wave.

## Project Structure

```
.afyapowers/
  .gitignore                # Auto-created; gitignores features/active
  features/
    active                  # Current active feature slug (gitignored)
    <date>-<slug>/
      state.yaml            # Feature state (phase, status, timestamps)
      history.yaml          # Full event timeline (immutable)
      artifacts/
        design.md           # Design spec (requirements + architecture)
        plan.md             # Implementation plan with checkboxes
        review.md           # Code review findings and verdict
        completion.md       # Completion summary
```

### Source Layout

```
src/
  commands/                 # Slash command definitions (8 total)
  skills/                   # Phase and cross-cutting skills (13 total)
  config/                   # IDE-specific configuration (Claude, Cursor, Gemini)
  hooks/                    # Session start hook for context restoration
  manifests/                # Plugin manifests for Claude and Cursor
  templates/                # Markdown templates for artifacts
```

## Session Continuity

A session-start hook automatically detects the active feature and injects context into Claude Code — current phase, task progress, available artifacts — so you can resume work seamlessly across sessions.

## Skills

### Phase Skills
- **design** — Collaborative exploration + technical specification with optional JIRA/Figma context
- **writing-plans** — Implementation plan creation from design spec with dependency graphs and Figma task inference
- **implementing** — Wave-based subagent dispatch with dependency ordering and self-review gates
- **reviewing** — 2-step code review (spec compliance + code quality) with iterative fix cycles
- **completing** — Test suite execution, merge/PR/cleanup, and completion summary
- **figma-component** — Standalone Figma component development (outside 5-phase workflow)

### Cross-Cutting Skills
- **test-driven-development** — RED-GREEN-REFACTOR cycle
- **systematic-debugging** — Root cause investigation before fixes
- **verification-before-completion** — Evidence before claims
- **using-git-worktrees** — Isolated workspaces for feature work
- **dispatching-parallel-agents** — Parallel investigation of independent problems
- **subagent-driven-development** — Fresh subagent per task with wave execution and review gates
- **auto-documentation** — Living docs generation after implementation

## Detailed Workflow Documentation

For a comprehensive, in-depth description of the entire workflow — including phase gates, subagent patterns, artifact templates, hook mechanics, Figma/JIRA integrations, standalone skills, and the multi-IDE distribution pipeline — see [WORKFLOW.md](WORKFLOW.md).

## License

MIT
