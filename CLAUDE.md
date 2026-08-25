# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

afyapowers-dev is a deterministic, phase-gated development workflow plugin for Claude Code (forked from [superpowers](https://github.com/obra/superpowers)). It enforces a 5-phase workflow (Design → Plan → Implement → Review → Complete) with persistent YAML-based state and markdown artifacts. It supports multiple AI IDEs: Claude Code, Cursor, Gemini, and GitHub Copilot.

## Build / Sync

There is no traditional build system. The project uses a Python script (`sync.py`) to generate per-agent distributions from a shared source:

```bash
python3 sync.py                  # Sync all agents (stale files removed automatically)
python3 sync.py claude           # Sync specific agent
python3 sync.py --clean          # Nuke output directories before syncing
python3 sync.py cursor --clean   # Nuke + specific agent
```

The script reads JSON configs from `src/config/` and produces customized output in `dist/<agent>/`. It handles agent-specific file prefixes, directory prefixes, frontmatter extraction, and plugin manifest copying. Requires Python 3.9+ (stdlib only, no pip dependencies).

There are no tests or linting configured for this repository.

**Runtime requirement:** the plugin itself also needs Python 3.9+ at runtime, not just for `sync.py`. The workflow's deterministic scripts (`src/scripts/feature.py`, `plan-graph.py`, `detect-commit-conventions.py`, `commit-task.py`) are Python. The `session-start` hook warns when `python3` is absent, and `/afyapowers-dev:new` stops rather than scaffolding into a broken state.

## Architecture

### Source → Distribution Pipeline

All canonical content lives in `src/`. The `sync.py` script transforms it into agent-specific distributions in `dist/`:

- **`src/config/<agent>.json`** — Per-agent config controlling prefixes, output paths, and which features to include
- **`src/skills/*/SKILL.md`** — Skills with embedded multi-agent frontmatter (workflow commands and phase skills alike)
- **`src/agents/*.md`** — Subagents with embedded multi-agent frontmatter, one flat `.md` per agent (no subdirectories — the processor only globs `*.md`)
- **`src/templates/*.md`** — Markdown artifact templates (copied as-is)
- **`src/scripts/`** — Supporting scripts copied verbatim to `dist/<agent>/scripts/`. Referenced from skills and agents by the plugin-root-relative path `scripts/<file>`, which is identical for every agent (no prefixing, no frontmatter parsing)
- **`src/hooks/`** — Session-start hook for context restoration (copied with execute permissions preserved)
- **`src/manifests/<agent>/`** — Plugin manifests per IDE

Each source `.md` file contains `---` delimited YAML frontmatter with agent names as top-level keys (e.g., `claude:`, `cursor:`, `github-copilot:`). The sync script extracts each agent's section and outputs it as the file's frontmatter in the corresponding distribution. If an agent has no section, the file is output without frontmatter.

### Feature State (Runtime)

When the plugin runs in a project, it creates `.afyapowers/features/<date>-<slug>/` directories containing:
- `state.yaml` — Current phase, status, timestamps
- `history.yaml` — Immutable event timeline
- `artifacts/` — Phase artifacts (design.md, plan.md, review.md, completion.md)

The `features/active` file tracks which feature is current (gitignored).

### Session Continuity

The hook at `src/hooks/session-start` is a bash script that detects the active feature from `.afyapowers/features/active`, reads its `state.yaml`, and injects context (feature name, phase, task progress) via JSON `additionalContext` so new sessions can resume seamlessly.

## Key Conventions

- **Never edit files in `dist/`** — they are generated. Always edit the source in `src/` and run `python3 sync.py`.
- When adding a new skill: create `src/skills/<name>/SKILL.md` with multi-agent frontmatter. Supporting prompt files go alongside SKILL.md. For manual-only skills (user must type `/name`), add `disable-model-invocation: true` to each agent's frontmatter section.
- When adding a new agent/IDE: create `src/config/<agent>.json`, add `<agent>:` sections to the frontmatter in relevant source files, optionally add a manifest in `src/manifests/<agent>/`, then run `python3 sync.py <agent>`.
- Plugin version is maintained in `src/manifests/*/plugin.json` files.
