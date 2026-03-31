# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

afyapowers is a deterministic, phase-gated development workflow plugin for Claude Code (forked from [superpowers](https://github.com/obra/superpowers)). It enforces a 5-phase workflow (Design → Plan → Implement → Review → Complete) with persistent YAML-based state and markdown artifacts. It supports multiple AI IDEs: Claude Code, Cursor, Gemini, and GitHub Copilot.

## Build / Sync

There is no traditional build system. The project uses a single bash script (`sync.sh`) to generate per-agent distributions from a shared source:

```bash
./sync.sh                  # Sync all agents
./sync.sh claude           # Sync specific agent
./sync.sh --clean          # Clean output directories before syncing
./sync.sh cursor --clean   # Clean + specific agent
```

The script reads JSON configs from `src/config/` and produces customized output in `dist/<agent>/`. It handles agent-specific file prefixes, directory prefixes, frontmatter injection, and plugin manifest copying. Requires `jq` (falls back to Python 3 if unavailable).

There are no tests or linting configured for this repository.

## Architecture

### Source → Distribution Pipeline

All canonical content lives in `src/`. The `sync.sh` script transforms it into agent-specific distributions in `dist/`:

- **`src/config/<agent>.json`** — Per-agent config controlling prefixes, output paths, and which features to include
- **`src/commands/*.md`** + **`*.frontmatter.yaml`** — Slash commands with per-agent frontmatter overrides
- **`src/skills/*/SKILL.md`** + **`frontmatter.yaml`** — Phase and cross-cutting skills with per-agent frontmatter
- **`src/templates/*.md`** — Markdown artifact templates (copied as-is)
- **`src/hooks/`** — Session-start hook for context restoration (copied with execute permissions preserved)
- **`src/manifests/<agent>/`** — Plugin manifests per IDE

The frontmatter system uses `.frontmatter.yaml` files with top-level keys matching agent names. Each agent's section becomes the `---` delimited YAML frontmatter in that distribution's output. If an agent has no section, the source file is copied unchanged.

### Feature State (Runtime)

When the plugin runs in a project, it creates `.afyapowers/features/<date>-<slug>/` directories containing:
- `state.yaml` — Current phase, status, timestamps
- `history.yaml` — Immutable event timeline
- `artifacts/` — Phase artifacts (design.md, plan.md, review.md, completion.md)

The `features/active` file tracks which feature is current (gitignored).

### Session Continuity

The hook at `src/hooks/session-start` is a bash script that detects the active feature from `.afyapowers/features/active`, reads its `state.yaml`, and injects context (feature name, phase, task progress) via JSON `additionalContext` so new sessions can resume seamlessly.

## Key Conventions

- **Never edit files in `dist/`** — they are generated. Always edit the source in `src/` and run `./sync.sh`.
- When adding a new command: create `src/commands/<name>.md` and `src/commands/<name>.frontmatter.yaml` with sections for each agent that needs custom frontmatter.
- When adding a new skill: create `src/skills/<name>/SKILL.md` and `src/skills/<name>/frontmatter.yaml`. Supporting prompt files go alongside SKILL.md.
- When adding a new agent/IDE: create `src/config/<agent>.json`, add `<agent>:` sections to relevant frontmatter files, optionally add a manifest in `src/manifests/<agent>/`, then run `./sync.sh <agent>`.
- Plugin version is maintained in `src/manifests/*/plugin.json` files (currently 0.5.0).
