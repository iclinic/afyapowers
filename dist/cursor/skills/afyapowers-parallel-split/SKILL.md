---
name: afyapowers-parallel-split
description: "Split independent task groups into parallel worktrees with territory-based file isolation"
---

# Parallel Split — Territory-Based Worktree Parallelization

Split a plan with independent task groups into N parallel git worktrees, each with its own territory (file ownership), plan subset, and afyapowers workflow. This enables multiple agents to implement different parts of a feature simultaneously without merge conflicts.

**Invoked by:** `implementing` skill (when user chooses parallel execution)
**NOT a standalone command** — only triggered as a choice during the plan → implement transition.

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
- `willImport`: files referenced in task descriptions but not in Files: section

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
2. No file is both `ownedFiles` in one group and `ownedFiles` in another
3. Shared files have assigned strategies

If validation fails, adjust by:
- Moving conflicting files to `deferred` strategy
- Assigning to the group whose tasks mention it most
- If truly inseparable, merge the two groups and reduce N

### 1D. Determine merge order

Analyze cross-group dependencies:
- If group B imports/uses files that group A creates → A merges before B
- If no cross-group dependencies → merge in any order (parallel merge)
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

For each worktree, do the following:

### 3A. Create afyapowers feature state

Create the feature directory structure in the worktree:

```bash
WT="<worktree_path>"
SLUG="<feature_slug>-wt<N>"

mkdir -p "${WT}/.afyapowers/features/${SLUG}/artifacts"
echo "${SLUG}" > "${WT}/.afyapowers/features/active"
```

Write `state.yaml`:

```yaml
feature: "<feature_name> (Group <N>: <group_description>)"
status: active
created_at: "<ISO_TIMESTAMP>"
current_phase: implement
phases:
  design:
    status: completed
    started_at: "<parent_design_started_at>"
    completed_at: "<parent_design_completed_at>"
    artifacts: [design.md]
  plan:
    status: completed
    started_at: "<ISO_TIMESTAMP>"
    completed_at: "<ISO_TIMESTAMP>"
    artifacts: [plan.md]
  implement:
    status: in_progress
    started_at: "<ISO_TIMESTAMP>"
    completed_at: null
    artifacts: []
  review:
    status: pending
    artifacts: []
  complete:
    status: pending
    artifacts: []
```

Write `history.yaml` with initial events:

```yaml
- event: feature_created
  timestamp: "<ISO_TIMESTAMP>"
  details: "Split from parent feature '<feature_slug>' — Group <N>"
- event: phase_started
  timestamp: "<ISO_TIMESTAMP>"
  phase: implement
  details: "Parallel split — tasks: <task_numbers>"
```

### 3B. Copy design.md

Copy the parent feature's `design.md` to the worktree:

```bash
cp ".afyapowers/features/<feature_slug>/artifacts/design.md" \
   "${WT}/.afyapowers/features/${SLUG}/artifacts/design.md"
```

### 3C. Generate subset plan.md

Create a `plan.md` containing ONLY this group's tasks:

1. Copy the plan header (Goal, Architecture, Tech Stack)
2. Include ONLY the `### Task N:` blocks assigned to this group
3. Renumber tasks sequentially (Task 1, Task 2, ...) for clarity
4. Update `**Depends on:**` references to use new task numbers
5. Preserve all step details, file lists, and Figma metadata

Save to `${WT}/.afyapowers/features/${SLUG}/artifacts/plan.md`

### 3D. Generate PROMPT.md with territory rules

Read `skills/parallel-split/territory-protocol.md` as template.

Replace placeholders:
- `{{WORKTREE_ID}}` → `wt<N>`
- `{{OWNED_FILES}}` → list of ownedFiles + ownedDirs for this group
- `{{READ_ONLY_FILES}}` → list of readOnlyFiles
- `{{FORBIDDEN_DIRS}}` → list of forbiddenDirs
- `{{SHARED_FILES}}` → list with strategies
- `{{MERGE_ORDER}}` → merge order description

Write to `${WT}/PROMPT.md`:

```markdown
# Parallel Worktree wt<N> — <feature_name>

## Context

You are implementing a subset of the feature "<feature_name>" in a parallel worktree.
This worktree handles tasks: <task_list>
Focus area: <group_description>

## Active Feature

Your afyapowers feature is ready at:
`.afyapowers/features/<slug>/`

The design and plan artifacts are pre-populated. You are starting at the **implement** phase.

## Instructions

1. Read PROMPT.md (this file) completely
2. Run the implement phase: the plan at `.afyapowers/features/<slug>/artifacts/plan.md` has your tasks
3. Follow TDD and subagent-driven-development as usual
4. **Respect territory rules below** — do NOT edit files outside your territory
5. After implement: run `/afyapowers:next` to proceed to review
6. After review: run `/afyapowers:next` to proceed to complete
7. At complete phase: choose **"Keep as-is"** — do NOT merge or create PR
8. After completion, create `WORKTREE_COMPLETE.md` to signal you are done

<territory-protocol content here>
```

### 3E. Provision MCP servers (Claude Code only)

```bash
cd "${WT_ABS_PATH}"
claude mcp remove serena -s project 2>/dev/null
claude mcp remove sequential-thinking -s project 2>/dev/null
claude mcp add -s project serena -- uvx --from 'git+https://github.com/oraios/serena' serena start-mcp-server --context ide-assistant --project "${WT_ABS_PATH}"
claude mcp add -s project sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

Copy settings if they exist:

```bash
[ -f ".claude/settings.local.json" ] && mkdir -p "${WT}/.claude" && cp ".claude/settings.local.json" "${WT}/.claude/"
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
      "featureSlug": "<feature_slug>-wt1",
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

1. Update `state.yaml`: set implement phase to `in_progress`, add note about parallel split
2. Append to `history.yaml`:

```yaml
- event: parallel_split
  timestamp: "<ISO_TIMESTAMP>"
  details: "Split into <N> parallel worktrees: <wt_list>"
  territory_map: "territory_map.json"
```

---

## Step 6: Launch Terminals

Detect available terminal multiplexer and launch:

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
                    - exec: "<MCP_SETUP> && claude 'Read PROMPT.md and execute the afyapowers workflow starting from implement phase. Respect territory rules.'"
                - cwd: "<wt2_abs_path>"
                  commands:
                    - exec: "<MCP_SETUP> && claude 'Read PROMPT.md and execute the afyapowers workflow starting from implement phase. Respect territory rules.'"
```

Write to `~/.warp/launch_configurations/afyapowers-parallel.yaml`

Open: `open "warp://launch/afyapowers%20Parallel"`

### 6B. tmux (fallback)

```bash
SESSION="afyapowers-parallel"
tmux new-session -d -s "${SESSION}" -x 200 -y 50
tmux send-keys -t "${SESSION}:0.0" "cd '<wt1_path>' && claude 'Read PROMPT.md...'" Enter
# Split + send-keys for each additional worktree
tmux select-layout -t "${SESSION}" tiled
tmux attach -t "${SESSION}"
```

### 6C. Manual (no multiplexer)

Print commands for user to copy-paste:

```
Parallel split complete! Open one terminal per worktree:

  cd <wt1_path> && claude 'Read PROMPT.md and execute the afyapowers workflow starting from implement phase.'
  cd <wt2_path> && claude 'Read PROMPT.md and execute the afyapowers workflow starting from implement phase.'
```

---

## Step 7: Display Summary

```
Parallel Split Complete

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
Shared files: <count> (all deferred)

Agents launched in <terminal_type>.

After all worktrees complete:
  1. Merge in order: git merge <branch> for each worktree
  2. Consolidate _deferred/ files
  3. Run full test suite
  4. Continue with /afyapowers:next in parent feature (review phase)
```

---

## CLEANUP

After all worktrees complete and are merged:

```bash
# Remove worktrees
git worktree list | grep "afyapowers.*wt" | awk '{print $1}' | xargs -I {} git worktree remove {}

# Clean up branches
git branch | grep "afyapowers.*wt" | xargs git branch -d

# Remove territory map
rm territory_map.json

# Clean up deferred files
rm -rf _deferred/

# Remove launch config
rm ~/.warp/launch_configurations/afyapowers-parallel.yaml 2>/dev/null
```
