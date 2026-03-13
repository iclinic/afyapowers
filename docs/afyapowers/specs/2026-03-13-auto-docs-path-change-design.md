# Auto-Documentation Output Path Change

## Summary

Move the auto-documentation skill's output directory from `.afyapowers/docs/` to `docs/afyapowers/` so that living feature documentation lives in a visible, standard location in the project tree.

## Motivation

The `.afyapowers/docs/` path is hidden in a dotfolder, making documentation less discoverable. Moving to `docs/afyapowers/` places it alongside other project documentation in a conventional location.

## Scope

**Changed:** `skills/auto-documentation/SKILL.md` — all path references updated from `.afyapowers/docs/` to `docs/afyapowers/`.

**Not changed:**
- Phase artifact paths (remain in `.afyapowers/<feature>/artifacts/`)
- `.gitignore` (negation pattern for `.afyapowers/docs/` left as-is)
- Templates, commands, or other skills

## Details

The following references in the auto-documentation skill are updated:

1. **Step 2** (Prepare Documentation Directory): directory creation and gitignore check now reference `docs/afyapowers/`
2. **Step 3** (Scan Existing Docs): scan path changes to `docs/afyapowers/*.md`
3. **Step 6** (Commit): `git add` and commit messages reference `docs/afyapowers/`
4. **Document Format** section: file path pattern changes to `docs/afyapowers/FEATURE-NAME.md`
5. **Skill description** in frontmatter: updated to reference new path

Flat structure and all other behavior (matching, templates, changelog format) remain identical.
