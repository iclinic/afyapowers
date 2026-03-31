---
name: afyapowers-auto-documentation
description: "Use after any implementation is finished to automatically generate or update feature documentation in docs/afyapowers/ — analyzes changes, matches to existing docs by domain area, and maintains living documentation with changelog"
---

# Auto-Documentation

Automatically generate or update living feature documentation after implementation work completes.

## When This Runs

- **Within the afyapowers workflow:** Invoked during the completing phase (Step 3.5), before generating the completion artifact.
- **Standalone:** After any implementation work finishes, even without the `/afyapowers:*` workflow. The agent invokes this skill when it recognizes implementation is complete.

## Process

### Step 1: Gather Changes

Determine what was changed by running a git diff:

```bash
# Detect default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ]; then
  # On default branch — diff the last commit
  git diff HEAD~1
else
  # On feature branch — diff against default branch
  git diff "$DEFAULT_BRANCH"..."$CURRENT_BRANCH"
fi
```

**If the diff is empty (no changes), skip documentation entirely.** Inform the user: "No changes detected — skipping documentation update." Stop here.

### Step 2: Prepare Documentation Directory

1. Check if `docs/afyapowers/` exists in the project root. If not, create it.
2. Ensure `docs/afyapowers/` is **not gitignored**. Check the project's `.gitignore` — if it contains a pattern that would exclude `docs/afyapowers/`, add a negation pattern:

```
!docs/afyapowers/
```

This ensures documentation files can be committed to the repository.

### Step 3: Scan Existing Docs

Read all `docs/afyapowers/*.md` files. For each file, extract:
- The feature name (from the `# Title` heading)
- The Overview section (to understand what domain area it covers)
- The Key Files section (to understand which parts of the codebase it documents)

If no docs exist yet, skip to Step 5 (create new doc).

### Step 4: Match Changes to Existing Docs

Analyze the git diff and compare it to the existing documentation:
- **Which files were changed?** Do they overlap with the Key Files listed in any existing doc?
- **What domain area do the changes touch?** Does it match the Overview of any existing doc?
- If a doc covers the same domain area → **update that doc** (go to Step 5a)
- If changes span multiple features → **update each relevant doc** (run Step 5a for each)
- If no existing doc matches → **create a new doc** (go to Step 5b)

This is a judgment call — use the diff content and existing docs to make the best match. Do not use keyword heuristics; reason about the semantic domain of the changes.

### Step 5a: Update Existing Doc

1. **Rewrite the documentation sections** (Overview, Business Rules, Usage, Technical Details) to reflect the current state of the feature. These sections are living docs — rewrite them completely based on the current code, not just the latest changes.
2. **Preserve the existing Changelog** section entirely.
3. **Prepend a new changelog entry** at the top of the Changelog section (newest first).

### Step 5b: Create New Doc

1. Use the template from `templates/feature-doc.md` as the starting structure.
2. Choose a descriptive filename based on the logical domain area (e.g., `session-hooks.md`, `authentication.md`, `auto-documentation.md`).
3. Fill in all relevant sections. Only include sections that are relevant — a simple utility might skip "Data Flow" or "Business Rules".
4. Add the first changelog entry.

### Step 6: Commit

Commit the documentation changes:

```bash
git add docs/afyapowers/
git commit -m "docs: update docs/afyapowers/<feature-name>.md"
```

If multiple docs were updated, adjust the commit message accordingly:

```bash
git commit -m "docs: update feature documentation"
```

## Document Format

Each `docs/afyapowers/FEATURE-NAME.md` follows this structure:

```markdown
# Feature Name

## Overview
Brief description of what this feature does and why it exists.

## Business Rules
- Rule 1: description
- Rule 2: description

## Usage
How to use the feature — configuration, API, commands, etc.

## Technical Details

### Architecture
Key components, how they connect, where they live.

### Key Files
- `path/to/file.ts` — purpose

### Data Flow
How data moves through the feature.

## Changelog

### 2026-03-13
- **What:** Detailed description of the changes made
- **Files:** `src/session/config.ts`, `src/session/middleware.ts`
```

### Key Rules

- **Sections are optional** — only include sections that are relevant to the feature.
- **Changelog is prepended** — newest entries first.
- **Documentation sections are rewritten** each time to reflect current state. They are living docs, not append-only.
- **Changelog is append-only** — never remove previous entries, only prepend new ones at the top.

### Changelog Entry Format

Each entry under a date heading contains:
- **What:** A detailed description of what changed — be specific about what was added, modified, or removed and the effect on the feature.
- **Files:** List of files that were created, modified, or deleted.

## Context Sources

When generating documentation, use these sources in priority order:

1. **Afyapowers artifacts** — If `.afyapowers/features/<feature>/artifacts/` exists, read `design.md`, `plan.md`, and `review.md` for rich context about requirements, architecture, and decisions. These are optional but produce significantly better docs.
2. **Git diff** — Always available. The primary source for understanding what changed.
3. **Existing docs** — Used for matching and understanding the current documented state of features.
