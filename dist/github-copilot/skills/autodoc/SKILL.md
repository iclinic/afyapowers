---
name: autodoc
description: "Generate or update living feature documentation under docs/{feature}/ (business-rules.md, architecture.md, optional data-models.md, CHANGELOG.md). Runs inside the afyapowers workflow to document the feature(s) just built, or standalone — ask the user what to document, explore the codebase, then create/update the docs."
---

# Autodoc

**Language:** Always write the documentation in Brazilian Portuguese (pt-BR) — prose, headings,
and explanations. Keep in English the technical and product terms that are conventionally used
in English in software/product work (e.g. Tech Stack, endpoint, deploy, queue, worker, cron,
payload, index, request/response, feature, design pattern, changelog, code identifiers, file
paths). Do not translate code, identifiers, or file paths.

Generate or update living feature documentation. Each feature gets a folder under `docs/`:

```
docs/<feature>/
  business-rules.md   # what the feature does, in product terms (always)
  architecture.md     # complete tech picture (always)
  data-models.md      # data shapes (only if the feature has them)
  CHANGELOG.md        # dated entries, newest first (always)
```

## Step 0: Detect Mode

Read `.afyapowers/features/active`.

- **Exists and non-empty** → **Workflow mode**. The target is that feature; rich context is
  available in `.afyapowers/features/<feature>/artifacts/` plus the git diff. This is also the
  case when the `completing` phase invokes this skill as a sub-skill.
- **Missing or empty** → **Standalone mode**. The user is running `/afyapowers:autodoc` (or
  asked for documentation) outside the workflow.

Follow the matching section below, then converge on the shared **Write Docs** and **Finish**
steps.

---

## Workflow Mode

### W1: Gather Changes

```bash
# Detect default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ]; then
  git diff HEAD~1
else
  git diff "$DEFAULT_BRANCH"..."$CURRENT_BRANCH"
fi
```

**If the diff is empty, skip documentation entirely.** Tell the user: "No changes detected —
skipping documentation update." Stop here.

### W2: Pull Rich Context

If `.afyapowers/features/<feature>/artifacts/` exists, read `design.md`, `plan.md`, and
`review.md` for requirements, architecture decisions, and scope. These are optional but
produce significantly better docs.

### W3: Determine Feature(s)

The changes usually map to the active feature. If the diff clearly spans multiple distinct
domain areas, document each one (run **Write Docs** per feature). Reason about the semantic
domain of the changes — do not keyword-match.

Then go to **Write Docs**, and **Finish**.

---

## Standalone Mode

### S1: Ask What to Document

If the user already named the feature/area in their request, use that. Otherwise ask with
AskUserQuestion: which feature or area to document, and any scope hints (paths, modules,
"the billing flow", a domain name, etc.).

### S2: Explore the Codebase

Locate the related code — use Explore / Glob / Grep to find entry points, modules, models,
integrations, events/workers for that feature. Build the same understanding that workflow mode
gets from a diff: what it does, how it's wired, what data it touches.

### S3: Check Existing Docs

Look for `docs/<slug>/` for the feature. If it exists, this is an **update** — read the
current files first so you rewrite from the true current state. Also scan sibling `docs/*/`
folders in case the feature is already documented under a different slug (reason semantically;
do not keyword-match). Reuse the existing folder rather than creating a near-duplicate.

Then go to **Write Docs**, and **Finish**.

---

## Write Docs (shared)

### Prepare the directory

1. Slugify the feature name to kebab-case → `<feature>`. Only allow lowercase letters,
   digits, and hyphens; reject or strip any other character (including `.`, `/`, and
   `..`). If the resulting slug is empty or starts with a dot or hyphen, abort and ask the
   user for a valid name.
2. Ensure `docs/` exists; create `docs/<feature>/` if missing.
3. Ensure `docs/<feature>/` is **not gitignored**. If a `.gitignore` pattern would exclude it,
   add a negation pattern so the docs can be committed:

   ```
   !docs/<feature>/
   ```

### Write the files

These are **living docs** — rewrite each file completely to reflect the current state of the
code, not just the latest change. Use the templates in `templates/` as the starting structure.
Within a file, only include sections that are relevant; drop ones that don't apply.

- **`business-rules.md`** (always) — from `templates/feature-business-rules.md`. Detailed,
  product-level: what the feature does and why, every business rule (behaviors, validations,
  states, edge cases), and the user/actor flows.
- **`architecture.md`** (always) — from `templates/feature-architecture.md`. The complete
  technical picture: tech stack and key libraries, components/abstractions and where they live
  (file paths), design patterns, integrations (external services, APIs, events, queues,
  workers, cron), data flow, and a Key Files list.
- **`data-models.md`** (only if the feature has data models) — from
  `templates/feature-data-models.md`. DB tables/collections/documents (fields, types,
  relations, indexes), external request/response contracts, and event/message schemas. Skip
  this file entirely for features with no meaningful data models.

### Update the changelog

`docs/<feature>/CHANGELOG.md` is **append-only**. **Prepend** a new dated entry at the top
(newest first); never remove or rewrite past entries. Create the file from
`templates/feature-changelog.md` with the first entry if it doesn't exist.

Each entry:

```markdown
### 2026-03-13
- **What:** Descrição detalhada do que mudou — seja específico sobre o que foi adicionado,
  modificado ou removido e o efeito na feature.
- **Files:** `src/session/config.ts`, `src/session/middleware.ts`
```

In standalone mode where there's no diff, base the **What** on the documentation action (e.g.,
"Documentado o fluxo de billing existente") and list the key files the docs cover.

---

## Finish

**Never commit automatically.** In both modes, leave the written docs in the working tree and
tell the user the docs are ready to review (list the files/folders written). The user decides
whether and when to commit.

## Key Rules

- **Sections within a file are optional** — only include relevant ones.
- **`data-models.md` is optional** — only create it when the feature has data models.
- **Docs are rewritten** each run to reflect current state (living docs).
- **The changelog is append-only** — prepend new entries, never remove old ones.
