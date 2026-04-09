---
name: parallel-split
description: "Split independent task groups into parallel worktrees with territory-based file isolation"
---

# Parallel Split — Territory-Based Worktree Parallelization

Split a plan with independent task groups into N parallel git worktrees. Each worktree implements its task group, then merges back so the parent feature continues with unified review and completion.

**Invoked by:** `implementing` skill (when user chooses parallel execution)
**NOT a standalone command** — only triggered as a choice within the implementing phase.

**Key constraint:** Worktrees run ONLY the implement phase. Review and complete happen on the parent branch after all worktrees merge back. This ensures review sees the consolidated diff and completion reflects the full feature.

---

## Input

This skill receives from the caller:

- `feature_slug`: active feature directory name
- `plan_content`: full plan.md content
- `design_content`: full design.md content
- `task_groups`: array of disconnected task groups (computed by caller)
- `all_tasks`: parsed tasks with deps, files, status

---

## Step 1: Build Territory Map

For each task group, compute file ownership:

### 1A. Collect files per group

For each group, aggregate:
- `willCreate`: all files in `Create:` lines of the group's tasks
- `willModify`: all files in `Modify:` lines of the group's tasks
- `willTest`: all files in `Test:` lines of the group's tasks

### 1B. Assign territories

For each group:

- **ownedFiles**: `willCreate` + `willModify` + `willTest` that are NOT in any other group
- **ownedDirs**: directories where ALL files belong to this group
- **readOnlyFiles**: files this group imports that are owned by another group
- **forbiddenDirs**: directories owned entirely by other groups
- **sharedFiles**: files that appear in multiple groups, with strategies:
  - `package.json`, `requirements.txt`, lock files → `deferred`
  - Barrel exports (`index.ts`, `__init__.py`) → `deferred`
  - Config files → `single_owner` (assign to group that modifies most)
  - Entry points (`App.tsx`, `main.py`) → `single_owner`

### 1C. Validate territory

Check that:
1. Every `willCreate`/`willModify` file has exactly one owner (no double-ownership)
2. Shared files have assigned strategies

If validation fails, adjust by:
- Moving conflicting files to `deferred` strategy
- Assigning to the group whose tasks mention it most
- If truly inseparable, merge the two groups and reduce N

### 1D. Determine merge order

Analyze cross-group dependencies:
- If group B imports/uses files that group A creates → A merges before B
- If no cross-group dependencies → merge in any order
- Generate ordered list: `["wt1", "wt3", "wt2"]`

---

## Step 2: Create Git Worktrees

For each task group:

```bash
PROJECT_NAME=$(basename "$(pwd)")
FEATURE_SHORT=$(echo "{{feature_slug}}" | sed 's/^[0-9-]*//' | cut -c1-20)
BRANCH_NAME="${PROJECT_NAME}-${FEATURE_SHORT}-wt<N>"
WT_PATH="../${PROJECT_NAME}-${FEATURE_SHORT}-wt<N>"

git worktree add -b "${BRANCH_NAME}" "${WT_PATH}" HEAD
```

---

## Step 3: Prepare Each Worktree

### 3A. Copy canonical plan.md

Copy the parent feature's canonical plan artifact into the worktree:

```bash
mkdir -p "${WT_PATH}/.afyapowers/features/<feature_slug>/artifacts"
cp ".afyapowers/features/<feature_slug>/artifacts/plan.md" \
   "${WT_PATH}/.afyapowers/features/<feature_slug>/artifacts/plan.md"
```

This is the file that must be updated during implementation so checkbox changes merge back cleanly into the parent feature.

### 3B. Generate task scope summary

Create `TASK_SCOPE.md` in the worktree root containing ONLY this group's task blocks:

1. Copy the plan header (Goal, Architecture, Tech Stack)
2. Include ONLY the `### Task N:` blocks assigned to this group
3. Preserve original task numbers (do NOT renumber)
4. Preserve all step details, file lists, and Figma metadata

Save to `${WT_PATH}/TASK_SCOPE.md`

### 3C. Copy design.md for context

```bash
cp ".afyapowers/features/<feature_slug>/artifacts/design.md" \
   "${WT_PATH}/.afyapowers/features/<feature_slug>/artifacts/design.md"
cp ".afyapowers/features/<feature_slug>/artifacts/design.md" "${WT_PATH}/DESIGN_CONTEXT.md"
```

### 3D. Generate PROMPT.md with territory rules

Read `skills/parallel-split/territory-protocol.md` as template. Replace placeholders with this group's territory data.

Write to `${WT_PATH}/PROMPT.md`:

```markdown
# Parallel Worktree wt<N> — <feature_name>

## Context

You are implementing a subset of the feature "<feature_name>" in a parallel worktree.
This worktree handles tasks: <original_task_numbers>
Focus area: <group_description>

## Instructions

1. Read this file completely
2. Read `DESIGN_CONTEXT.md` for the full design spec
3. Read `TASK_SCOPE.md` for your assigned tasks
4. Read `.afyapowers/features/<feature_slug>/artifacts/plan.md` for the canonical feature plan
5. Implement ALL tasks following TDD (test first → implement → refactor → commit)
6. For each completed assigned task, mark its checkbox: `- [ ]` → `- [x]` in `.afyapowers/features/<feature_slug>/artifacts/plan.md`
7. Do NOT mark or edit tasks outside your assigned group
8. **Respect territory rules below** — do NOT edit files outside your territory
9. After ALL assigned tasks are complete: create `WORKTREE_COMPLETE.md` with a summary of what was done
10. Do NOT run /afyapowers:next — do NOT start review or complete phases

## IMPORTANT: Implement Only

This worktree handles ONLY the implement phase. Review and completion happen on
the parent branch after all worktrees merge back. When done, just create
WORKTREE_COMPLETE.md and stop.

<territory-protocol content>
```

### 3E. Host-Specific Setup

Use the normal project or plugin setup for the host running in each worktree.

- Claude Code: you may provision project MCP servers for each worktree if needed
- Other hosts: do not assume the `claude` CLI exists; use the host's normal setup flow instead

Optional Claude Code setup example:

```bash
WT_ABS_PATH="$(cd "${WT_PATH}" && pwd)"
cd "${WT_ABS_PATH}"
claude mcp remove serena -s project 2>/dev/null
claude mcp remove sequential-thinking -s project 2>/dev/null
claude mcp add -s project serena -- uvx --from 'git+https://github.com/oraios/serena' serena start-mcp-server --context ide-assistant --project "${WT_ABS_PATH}"
claude mcp add -s project sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

Copy settings if they exist:

```bash
[ -f ".claude/settings.local.json" ] && mkdir -p "${WT_PATH}/.claude" && cp ".claude/settings.local.json" "${WT_PATH}/.claude/"
```

---

## Step 4: Write territory_map.json

Write `territory_map.json` in the parent project root:

```json
{
  "generated": "<ISO_DATE>",
  "source": "afyapowers-parallel-split",
  "parentFeature": "<feature_slug>",
  "worktrees": [
    {
      "id": "wt1",
      "path": "<worktree_path>",
      "branch": "<branch_name>",
      "tasks": [1, 2, 5],
      "taskNames": ["Task 1: ...", "Task 2: ...", "Task 5: ..."],
      "ownedFiles": [],
      "ownedDirs": [],
      "readOnlyFiles": [],
      "forbiddenDirs": [],
      "sharedFiles": []
    }
  ],
  "mergeOrder": ["wt1", "wt3", "wt2"],
  "sharedFiles": []
}
```

---

## Step 5: Update Parent Feature State

In the parent project's `.afyapowers/features/<feature_slug>/`:

Append to `history.yaml` under the `events:` key:

```yaml
  - timestamp: "<ISO_TIMESTAMP>"
    event: parallel_split
    phase: implement
    details: "Split into <N> parallel worktrees: <wt_list>"
    command: parallel-split
```

---

## Step 6: Launch Terminals

### 6A. Warp (default on macOS)

Generate Warp Launch Configuration:

```yaml
---
name: afyapowers Parallel
windows:
  - tabs:
      - title: "afyapowers - <N> Worktrees"
        layout:
          split_direction: vertical
          panes:
            - split_direction: horizontal
              panes:
                - cwd: "<wt1_abs_path>"
                  commands:
                    - exec: "<MCP_SETUP> && claude 'Read PROMPT.md and implement all assigned tasks following TDD. Create WORKTREE_COMPLETE.md when done.'"
                - cwd: "<wt2_abs_path>"
                  commands:
                    - exec: "<MCP_SETUP> && claude 'Read PROMPT.md and implement all assigned tasks following TDD. Create WORKTREE_COMPLETE.md when done.'"
```

Where `<MCP_SETUP>` chains the optional Claude Code setup commands from Step 3E.

Write to `~/.warp/launch_configurations/afyapowers-parallel.yaml`
Open: `open "warp://launch/afyapowers%20Parallel"`

### 6B. Generic Manual Launch

If automated launch is unavailable or you are using a non-Claude host, open one agent session per worktree manually and tell it to read `PROMPT.md`.

Example:

```text
cd <wt1_path> && <your-agent-host>
cd <wt2_path> && <your-agent-host>
```

Use tmux, Warp, separate terminals, or separate IDE windows according to your host environment.

---

## Step 7: Display Summary and Post-Merge Instructions

```
Parallel Split — Implement Phase

Feature: <feature_name>
Worktrees: <N>
Territory map: territory_map.json

  wt1 (Tasks <nums>): <group_description>
    Owns: <key_dirs>
    Branch: <branch_name>

  wt2 (Tasks <nums>): <group_description>
    Owns: <key_dirs>
    Branch: <branch_name>

Merge order: wt1 → wt2 → wt3
Shared files: <count> (deferred)

Agents launched.

After ALL worktrees create WORKTREE_COMPLETE.md:

  1. Merge in order:
     git merge <wt1_branch>
     git merge <wt2_branch>
     ...

  2. Consolidate deferred files (if any in _deferred/)

  3. Verify the canonical feature plan:
     .afyapowers/features/<feature_slug>/artifacts/plan.md
     Each worktree updated its assigned task checkboxes in that file.
     After the merges, confirm every task is [x].

  4. If every task is [x], run /afyapowers:next to proceed to review
     If some tasks are still [ ], stay in implement and continue from there

  5. Clean up:
     git worktree list | grep "<feature_short>.*wt" | awk '{print $1}' | xargs -I {} git worktree remove {}
     rm territory_map.json _deferred/ 2>/dev/null
```

**IMPORTANT:** This skill does not implicitly resume later. After merges are finished, continue from the parent feature:
- If the canonical plan is fully checked off, run `/afyapowers:next`
- If work remains, stay in implement and continue from the remaining unchecked tasks
