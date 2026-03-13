# Features Directory Restructure — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move feature directories from `.afyapowers/<slug>/` to `.afyapowers/features/<slug>/` and add dynamic `.gitignore` creation.

**Architecture:** Pure path-string replacement across markdown commands, skills, a bash hook, and README. No logic changes except adding `.gitignore` creation in `new.md`.

**Tech Stack:** Markdown, Bash, YAML (no code — all prompt/doc changes)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `commands/new.md` | Modify | Feature dir creation, active file, .gitignore logic |
| `commands/next.md` | Modify | State/artifact read/write paths |
| `commands/status.md` | Modify | Active file + state read paths |
| `commands/history.md` | Modify | Active file + history read paths |
| `commands/features.md` | Modify | Feature scan path + active file read path |
| `commands/switch.md` | Modify | Feature scan glob + active file write path |
| `commands/abort.md` | Modify | Active file + state read/write paths |
| `hooks/session-start` | Modify | Active file path + feature scan glob in bash |
| `skills/design/SKILL.md` | Modify | Artifact write path |
| `skills/design/spec-document-reviewer-prompt.md` | Modify | Artifact path reference |
| `skills/writing-plans/SKILL.md` | Modify | Active file + artifact read/write paths |
| `skills/implementing/SKILL.md` | Modify | Active file + artifact read/write paths |
| `skills/reviewing/SKILL.md` | Modify | Active file + artifact read/write paths |
| `skills/completing/SKILL.md` | Modify | Active file + artifact read/write paths |
| `skills/auto-documentation/SKILL.md` | Modify | Artifact read path |
| `skills/subagent-driven-development/SKILL.md` | Modify | Artifact path reference |
| `README.md` | Modify | Directory structure docs |

---

## Chunk 1: Commands

### Task 1: Update `commands/new.md`

**Files:**
- Modify: `commands/new.md`

This is the most complex change — adds `.gitignore` creation logic and updates all paths.

- [ ] **Step 1: Add .gitignore creation logic to Step 2**

In `commands/new.md`, replace Step 2 content. The new Step 2 should:

1. Generate slug (unchanged)
2. Get date (unchanged)
3. Construct directory name (unchanged)
4. Check if `.afyapowers/features/<directory-name>/` already exists (was `.afyapowers/<directory-name>/`)
5. **NEW:** Ensure `.afyapowers/features/` directory exists (mkdir -p)
6. **NEW:** If `.afyapowers/.gitignore` does not exist, create it with content: `features/active`
7. Create the directory structure:
   - `.afyapowers/features/<directory-name>/`
   - `.afyapowers/features/<directory-name>/artifacts/`

Replace the current Step 2 section with:

```markdown
## Step 2: Create Feature Directory

Using the feature name provided:

1. Generate a slug: lowercase the name, replace spaces with hyphens, strip any characters that aren't letters, numbers, or hyphens, truncate to 50 characters
2. Get today's date in YYYY-MM-DD format
3. Construct the directory name: `<date>-<slug>`
4. Check if `.afyapowers/features/<directory-name>/` already exists. If so, append `-2` (then `-3`, etc.) until unique
5. Ensure `.afyapowers/features/` directory exists (create it if not)
6. If `.afyapowers/.gitignore` does not exist, create it with the following content:
   ```
   features/active
   ```
7. Create the directory structure:
   - `.afyapowers/features/<directory-name>/`
   - `.afyapowers/features/<directory-name>/artifacts/`
```

- [ ] **Step 2: Update remaining path references in `new.md`**

Replace all remaining `.afyapowers/<directory-name>` with `.afyapowers/features/<directory-name>` in:

- Step 3 heading: `Create .afyapowers/features/<directory-name>/state.yaml`
- Step 3 history: `Create .afyapowers/features/<directory-name>/history.yaml`
- Step 4: Write to `.afyapowers/features/active` (was `.afyapowers/active`)
- Step 5 confirmation message: `.afyapowers/features/<directory-name>/`
- Step 5 artifact save: `.afyapowers/features/<directory-name>/artifacts/design.md`

- [ ] **Step 3: Commit**

```bash
git add commands/new.md
git commit -m "feat: update new.md paths to .afyapowers/features/ with .gitignore creation"
```

---

### Task 2: Update `commands/next.md`

**Files:**
- Modify: `commands/next.md`

- [ ] **Step 1: Update all path references**

Replace all occurrences of `.afyapowers/active` with `.afyapowers/features/active` (line 7).

Replace all occurrences of `.afyapowers/<slug>` with `.afyapowers/features/<slug>`:
- Line 9: `Read .afyapowers/features/<slug>/state.yaml`
- Line 17: `.afyapowers/features/<slug>/artifacts/design.md`
- Line 18: `.afyapowers/features/<slug>/artifacts/plan.md`
- Line 19: `.afyapowers/features/<slug>/artifacts/plan.md`
- Line 20: `.afyapowers/features/<slug>/artifacts/review.md`
- Line 21: `.afyapowers/features/<slug>/artifacts/completion.md`
- Line 61: `.afyapowers/features/<slug>/artifacts/`

- [ ] **Step 2: Commit**

```bash
git add commands/next.md
git commit -m "feat: update next.md paths to .afyapowers/features/"
```

---

### Task 3: Update `commands/status.md`

**Files:**
- Modify: `commands/status.md`

- [ ] **Step 1: Update path references**

- Line 7: `.afyapowers/active` → `.afyapowers/features/active`
- Line 9: `.afyapowers/<slug>/state.yaml` → `.afyapowers/features/<slug>/state.yaml`

- [ ] **Step 2: Commit**

```bash
git add commands/status.md
git commit -m "feat: update status.md paths to .afyapowers/features/"
```

---

### Task 4: Update `commands/history.md`

**Files:**
- Modify: `commands/history.md`

- [ ] **Step 1: Update path references**

- Line 7: `.afyapowers/active` → `.afyapowers/features/active`
- Line 9: `.afyapowers/<slug>/history.yaml` → `.afyapowers/features/<slug>/history.yaml`

- [ ] **Step 2: Commit**

```bash
git add commands/history.md
git commit -m "feat: update history.md paths to .afyapowers/features/"
```

---

### Task 5: Update `commands/features.md`

**Files:**
- Modify: `commands/features.md`

- [ ] **Step 1: Update path references**

- Line 7: `Scan all directories under .afyapowers/` → `Scan all directories under .afyapowers/features/` and update to skip `active` file reference
- Line 19: `.afyapowers/active` → `.afyapowers/features/active`
- Line 21: `No .afyapowers/ directory` → `No .afyapowers/features/ directory`

- [ ] **Step 2: Commit**

```bash
git add commands/features.md
git commit -m "feat: update features.md paths to .afyapowers/features/"
```

---

### Task 6: Update `commands/switch.md`

**Files:**
- Modify: `commands/switch.md`

- [ ] **Step 1: Update path references**

- Line 9: `.afyapowers/*/state.yaml` → `.afyapowers/features/*/state.yaml`
- Line 16: `under .afyapowers/` → `under .afyapowers/features/`
- Line 18: `.afyapowers/active` → `.afyapowers/features/active`

- [ ] **Step 2: Commit**

```bash
git add commands/switch.md
git commit -m "feat: update switch.md paths to .afyapowers/features/"
```

---

### Task 7: Update `commands/abort.md`

**Files:**
- Modify: `commands/abort.md`

- [ ] **Step 1: Update path references**

- Line 7: `.afyapowers/active` → `.afyapowers/features/active`
- Line 9: `.afyapowers/<slug>/state.yaml` → `.afyapowers/features/<slug>/state.yaml`
- Line 20: `.afyapowers/active` → `.afyapowers/features/active`

- [ ] **Step 2: Commit**

```bash
git add commands/abort.md
git commit -m "feat: update abort.md paths to .afyapowers/features/"
```

---

## Chunk 2: Hooks

### Task 8: Update `hooks/session-start`

**Files:**
- Modify: `hooks/session-start`

- [ ] **Step 1: Update ACTIVE_FILE path**

Line 14: Change `ACTIVE_FILE="$AFYA_DIR/active"` to `ACTIVE_FILE="$AFYA_DIR/features/active"`

- [ ] **Step 2: Update feature directory validation**

Line 20: Change `if [ ! -d "$AFYA_DIR/$ACTIVE_FEATURE" ]` to `if [ ! -d "$AFYA_DIR/features/$ACTIVE_FEATURE" ]`

- [ ] **Step 3: Update feature scan glob**

Line 28: Change `for state_file in "$AFYA_DIR"/*/state.yaml` to `for state_file in "$AFYA_DIR"/features/*/state.yaml`

- [ ] **Step 4: Update STATE_FILE path**

Line 60: Change `STATE_FILE="$AFYA_DIR/$ACTIVE_FEATURE/state.yaml"` to `STATE_FILE="$AFYA_DIR/features/$ACTIVE_FEATURE/state.yaml"`

- [ ] **Step 5: Update ARTIFACT_DIR path**

Line 74: Change `ARTIFACT_DIR="$AFYA_DIR/$ACTIVE_FEATURE/artifacts"` to `ARTIFACT_DIR="$AFYA_DIR/features/$ACTIVE_FEATURE/artifacts"`

- [ ] **Step 6: Commit**

```bash
git add hooks/session-start
git commit -m "feat: update session-start hook paths to .afyapowers/features/"
```

---

## Chunk 3: Skills

### Task 9: Update `skills/design/SKILL.md`

**Files:**
- Modify: `skills/design/SKILL.md`

- [ ] **Step 1: Update all `.afyapowers/<feature>` references to `.afyapowers/features/<feature>`**

Lines to update: 18, 19, 34, 123, 137. Also update `.afyapowers/active` → `.afyapowers/features/active` on line 18.

- [ ] **Step 2: Commit**

```bash
git add skills/design/SKILL.md
git commit -m "feat: update design skill paths to .afyapowers/features/"
```

---

### Task 10: Update `skills/design/spec-document-reviewer-prompt.md`

**Files:**
- Modify: `skills/design/spec-document-reviewer-prompt.md`

- [ ] **Step 1: Update artifact path reference**

Line 7: `.afyapowers/<feature>/artifacts/` → `.afyapowers/features/<feature>/artifacts/`

- [ ] **Step 2: Commit**

```bash
git add skills/design/spec-document-reviewer-prompt.md
git commit -m "feat: update spec-document-reviewer paths to .afyapowers/features/"
```

---

### Task 11: Update `skills/writing-plans/SKILL.md`

**Files:**
- Modify: `skills/writing-plans/SKILL.md`

- [ ] **Step 1: Update all path references**

- Line 18: `.afyapowers/active` → `.afyapowers/features/active`
- Line 19: `.afyapowers/<feature>/state.yaml` → `.afyapowers/features/<feature>/state.yaml`
- Line 21: `.afyapowers/<feature>/artifacts/design.md` → `.afyapowers/features/<feature>/artifacts/design.md`
- Line 23: `.afyapowers/<feature>/artifacts/plan.md` → `.afyapowers/features/<feature>/artifacts/plan.md`

- [ ] **Step 2: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat: update writing-plans skill paths to .afyapowers/features/"
```

---

### Task 12: Update `skills/implementing/SKILL.md`

**Files:**
- Modify: `skills/implementing/SKILL.md`

- [ ] **Step 1: Update all path references**

- Line 14: `.afyapowers/active` → `.afyapowers/features/active`
- Line 15: `.afyapowers/<feature>/state.yaml` → `.afyapowers/features/<feature>/state.yaml`
- Line 17: `.afyapowers/<feature>/artifacts/plan.md` → `.afyapowers/features/<feature>/artifacts/plan.md`
- Line 18: `.afyapowers/<feature>/artifacts/design.md` → `.afyapowers/features/<feature>/artifacts/design.md`

- [ ] **Step 2: Commit**

```bash
git add skills/implementing/SKILL.md
git commit -m "feat: update implementing skill paths to .afyapowers/features/"
```

---

### Task 13: Update `skills/reviewing/SKILL.md`

**Files:**
- Modify: `skills/reviewing/SKILL.md`

- [ ] **Step 1: Update all path references**

- Line 12: `.afyapowers/active` → `.afyapowers/features/active`
- Line 13: `.afyapowers/<feature>/state.yaml` → `.afyapowers/features/<feature>/state.yaml`
- Line 20: `.afyapowers/<feature>/artifacts/design.md` → `.afyapowers/features/<feature>/artifacts/design.md`
- Line 21: `.afyapowers/<feature>/artifacts/plan.md` → `.afyapowers/features/<feature>/artifacts/plan.md`
- Line 55: `.afyapowers/<feature>/artifacts/review.md` → `.afyapowers/features/<feature>/artifacts/review.md`

- [ ] **Step 2: Commit**

```bash
git add skills/reviewing/SKILL.md
git commit -m "feat: update reviewing skill paths to .afyapowers/features/"
```

---

### Task 14: Update `skills/completing/SKILL.md`

**Files:**
- Modify: `skills/completing/SKILL.md`

- [ ] **Step 1: Update all path references**

- Line 12: `.afyapowers/active` → `.afyapowers/features/active`
- Line 13: `.afyapowers/<feature>/state.yaml` → `.afyapowers/features/<feature>/state.yaml`
- Line 32: `.afyapowers/<feature>/artifacts/review.md` → `.afyapowers/features/<feature>/artifacts/review.md`
- Line 62: `.afyapowers/active` → `.afyapowers/features/active`
- Line 63: `.afyapowers/<feature>/artifacts/` → `.afyapowers/features/<feature>/artifacts/`
- Line 76: `.afyapowers/<feature>/artifacts/completion.md` → `.afyapowers/features/<feature>/artifacts/completion.md`

- [ ] **Step 2: Commit**

```bash
git add skills/completing/SKILL.md
git commit -m "feat: update completing skill paths to .afyapowers/features/"
```

---

### Task 15: Update `skills/auto-documentation/SKILL.md`

**Files:**
- Modify: `skills/auto-documentation/SKILL.md`

- [ ] **Step 1: Update artifact path reference**

Line 148: `.afyapowers/<feature>/artifacts/` → `.afyapowers/features/<feature>/artifacts/`

- [ ] **Step 2: Commit**

```bash
git add skills/auto-documentation/SKILL.md
git commit -m "feat: update auto-documentation skill paths to .afyapowers/features/"
```

---

### Task 16: Update `skills/subagent-driven-development/SKILL.md`

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md`

- [ ] **Step 1: Update artifact path reference**

Line 134: `.afyapowers/<feature>/artifacts/plan.md` → `.afyapowers/features/<feature>/artifacts/plan.md`

- [ ] **Step 2: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat: update subagent-driven-development skill paths to .afyapowers/features/"
```

---

## Chunk 4: Documentation

### Task 17: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the Project Structure section**

Replace the current structure block (lines 54-65) with:

```markdown
## Project Structure

```
.afyapowers/
  .gitignore                # Auto-created; gitignores features/active
  features/
    active                  # Current active feature slug (gitignored)
    <date>-<slug>/
      state.yaml            # Feature state (phase, status, artifacts)
      history.yaml          # Full event timeline
      artifacts/
        design.md           # Design spec (requirements + architecture)
        plan.md             # Implementation plan with checkboxes
        review.md           # Code review findings and verdict
        completion.md       # Completion summary
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README project structure for .afyapowers/features/ layout"
```
