# Auto-Documentation Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a cross-cutting auto-documentation skill that generates/updates living feature docs in `.afyapowers/docs/` after implementation work completes.

**Architecture:** A single SKILL.md prompt file that instructs the agent to gather git diffs, match changes to existing docs, and update or create feature documentation with changelog. Integrated into the completing phase as Step 3.5 and discoverable standalone via frontmatter description.

**Tech Stack:** Markdown (skill prompt + template), YAML frontmatter

---

## Chunk 1: Template and Skill

### Task 1: Create the feature-doc template

**Files:**
- Create: `templates/feature-doc.md`

- [ ] **Step 1: Create the template file**

```markdown
# {{feature_name}}

## Overview
<!-- Brief description of what this feature does and why it exists -->

## Business Rules
<!-- Business rules governing this feature -->

## Usage
<!-- How to use the feature — configuration, API, commands, etc. -->

## Technical Details

### Architecture
<!-- Key components, how they connect, where they live -->

### Key Files
<!-- List of key files with their purpose -->

### Data Flow
<!-- How data moves through the feature -->

## Changelog
<!-- Changelog entries prepended here, newest first -->
```

- [ ] **Step 2: Commit**

```bash
git add templates/feature-doc.md
git commit -m "feat: add feature-doc template for auto-documentation"
```

---

### Task 2: Create the auto-documentation skill

**Files:**
- Create: `skills/auto-documentation/SKILL.md`

- [ ] **Step 1: Create the skill directory and SKILL.md**

The skill file must include:
1. YAML frontmatter with `name: auto-documentation` and description
2. Overview explaining the two contexts (workflow + standalone)
3. Step-by-step process the agent must follow:
   - Step 1: Gather changes via git diff (current branch vs default branch; if on default branch, last commit). If diff is empty, skip documentation and inform the user — stop here.
   - Step 2: Check if `.afyapowers/docs/` exists, create if not. Ensure `.afyapowers/docs/` is not gitignored — if the project's `.gitignore` contains `.afyapowers/` or similar pattern, add `!.afyapowers/docs/` negation so docs can be committed.
   - Step 3: Read all existing `.afyapowers/docs/*.md` files
   - Step 4: Analyze the diff and match to existing docs. If changes span multiple features, update each relevant doc. If no existing doc matches, create a new `FEATURE-NAME.md`.
   - Step 5: For updates — rewrite documentation sections to reflect current state, preserve existing changelog, prepend new changelog entry
   - Step 6: For new docs — use `templates/feature-doc.md` as starting structure, fill in all sections, add first changelog entry
   - Step 7: Commit the doc changes with message `docs: update .afyapowers/docs/<feature-name>.md`
4. Document format reference (from spec)
5. Changelog entry format: date heading, `**What:**` with detailed description, `**Files:**` with list of affected files
6. Key rules: sections only included when relevant, changelog prepended (newest first), doc sections rewritten each time, changelog never removes previous entries
7. Context sources priority: afyapowers artifacts > git diff > existing docs
8. Note about reading afyapowers artifacts from `.afyapowers/<feature>/artifacts/` if they exist (optional, enriches docs)

```yaml
---
name: auto-documentation
description: "Use after any implementation is finished to automatically generate or update feature documentation in .afyapowers/docs/ — analyzes changes, matches to existing docs by domain area, and maintains living documentation with changelog"
---
```

- [ ] **Step 2: Commit**

```bash
git add skills/auto-documentation/SKILL.md
git commit -m "feat: add auto-documentation cross-cutting skill"
```

---

### Task 3: Integrate into completing phase

**Files:**
- Modify: `skills/completing/SKILL.md` (insert new step between Step 3 and Step 4)

- [ ] **Step 1: Add Step 3.5 to the completing skill**

Insert the following after `### Step 3: Execute Choice` and before `### Step 4: Produce Completion Artifact`:

```markdown
### Step 3.5: Update Documentation

Read and follow `skills/auto-documentation/SKILL.md`.

The following context is available from the current feature:
- Feature name from `.afyapowers/active`
- Artifacts: brainstorm.md, tech-spec.md, plan.md, review.md (in `.afyapowers/<feature>/artifacts/`)
- Git diff from the feature branch

After documentation is updated, proceed to Step 4.
```

- [ ] **Step 2: Commit**

```bash
git add skills/completing/SKILL.md
git commit -m "feat: integrate auto-documentation into completing phase"
```

---

## Chunk 2: Verification

### Task 4: Verify all files are in place and consistent

- [ ] **Step 1: Verify template exists and has correct structure**

```bash
cat templates/feature-doc.md
```

Expected: Template with `{{feature_name}}`, Overview, Business Rules, Usage, Technical Details (Architecture, Key Files, Data Flow), Changelog sections.

- [ ] **Step 2: Verify skill has correct frontmatter**

```bash
head -5 skills/auto-documentation/SKILL.md
```

Expected: YAML frontmatter with `name: auto-documentation` and description.

- [ ] **Step 3: Verify completing skill has the new step**

```bash
grep -A 10 "Step 3.5" skills/completing/SKILL.md
```

Expected: "Update Documentation" step referencing `skills/auto-documentation/SKILL.md`.

- [ ] **Step 4: Verify skill is discoverable alongside other cross-cutting skills**

```bash
ls skills/*/SKILL.md
```

Expected: `skills/auto-documentation/SKILL.md` appears in the list alongside existing skills.

- [ ] **Step 5: Verify template is alongside other templates**

```bash
ls templates/*.md
```

Expected: `templates/feature-doc.md` appears alongside brainstorm.md, tech-spec.md, plan.md, review.md, completion.md.

- [ ] **Step 6: Verify SKILL.md contains gitignore handling instructions**

```bash
grep -i "gitignore" skills/auto-documentation/SKILL.md
```

Expected: Instructions about ensuring `.afyapowers/docs/` is not gitignored (adding `!.afyapowers/docs/` negation).

- [ ] **Step 7: Verify SKILL.md contains empty diff early-exit**

```bash
grep -i "empty\|skip\|no changes" skills/auto-documentation/SKILL.md
```

Expected: Instructions to skip documentation and inform the user when diff is empty.
