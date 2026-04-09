---
description: Advance to Next Phase
name: afyapowers:next
---
# /afyapowers:next — Advance to Next Phase

You are advancing the active feature to the next workflow phase. Follow these steps exactly:

## Step 1: Identify Active Feature

1. Read `.afyapowers/features/active` to get the active feature slug
2. If no active feature, tell the user: "No active feature. Run `/afyapowers:new` to start one, or `/afyapowers:switch` to select an existing feature."
3. Read `.afyapowers/features/<slug>/state.yaml`

## Step 2: Validate Current Phase Completion

Check that the current phase has produced its required artifacts:

| Current Phase | Validation |
|--------------|------------|
| design | `.afyapowers/features/<slug>/artifacts/design.md` exists |
| plan | `.afyapowers/features/<slug>/artifacts/plan.md` exists |
| implement | Zero unchecked `- [ ]` items in `.afyapowers/features/<slug>/artifacts/plan.md` |
| review | `.afyapowers/features/<slug>/artifacts/review.md` exists AND its Verdict section contains "Approved" |
| complete | `.afyapowers/features/<slug>/artifacts/completion.md` exists |

If validation fails:
- Tell the user what's still needed (e.g., "The design artifact is missing. Complete the design phase first.")
- For implement: list the remaining unchecked tasks
- For review: if verdict is "Changes Requested", report the findings and explain what needs fixing
- Do NOT advance.

## Step 3: Handle Terminal Phase

If the current phase is `complete` and validation passes:
1. Update `state.yaml`: set `phases.complete.status` to `completed`, set `phases.complete.completed_at`, set feature-level `status` to `completed`
2. Append to `history.yaml`: `phase_completed` event for `complete`, then `feature_completed` event
3. Tell the user: "Feature '<feature-name>' is complete!"
4. Stop here — do not advance further.

## Step 4: Advance Phase

Determine the next phase from the ordered list: design → plan → implement → review → complete.

1. Update `state.yaml`:
   - Set current phase's `status` to `completed` and `completed_at` to current timestamp
   - Set next phase's `status` to `in_progress` and `started_at` to current timestamp
   - Set `current_phase` to the next phase name
2. Append to `history.yaml`:
   - `phase_completed` event for the current phase (include `command: /afyapowers:next`)
   - `phase_started` event for the next phase

## Step 5: Invoke Next Phase Skill

Tell the user which phase is starting, then invoke the appropriate skill.

**Special case: plan → implement transition** — Before invoking the implementing skill, run the Parallel Split Analysis (Step 5A).

| Next Phase | Skill to Invoke | What It Does |
|-----------|----------------|--------------|
| plan | **writing-plans** skill | Break design into implementation tasks |
| implement | **(see Step 5A first)** → **implementing** skill | Execute tasks with TDD + subagents |
| review | **reviewing** skill | 2-step code review (spec compliance + quality) |
| complete | **completing** skill | Merge/PR/cleanup, produce completion summary |

### Step 5A: Parallel Split Analysis (plan → implement ONLY)

**This step runs ONLY when transitioning from plan to implement.** For all other transitions, skip to Step 5B.

1. Read the plan from `.afyapowers/features/<slug>/artifacts/plan.md`
2. Parse all tasks: extract task numbers, `**Depends on:**` lines, and `**Files:**` sections
3. Build the dependency graph
4. Find **disconnected components** — groups of tasks with NO dependencies between them

**How to find disconnected components:**
- Start with each task as its own group
- If Task A depends on Task B, merge their groups
- If Task A and Task B share files (overlap), merge their groups
- After processing all deps and overlaps, count remaining distinct groups

5. **If only 1 group exists** (all tasks are connected): skip to Step 5B — no split possible.

6. **If 2+ disconnected groups exist**, analyze each group:
   - List tasks in the group
   - Describe the group by its primary domain (infer from file paths and task names)
   - List key files/directories the group touches

7. **Present the choice to the user:**

```
Your plan has <N> independent task groups with no dependencies between them:

  Group A (Tasks 1, 2, 5): <domain_description>
    Files: <key_directories>

  Group B (Tasks 3, 4): <domain_description>
    Files: <key_directories>

  Group C (Tasks 6, 7): <domain_description>
    Files: <key_directories>

How would you like to execute?

  1) Sequential (default) — one agent implements all tasks using wave execution
  2) Parallel worktrees — creates <N> worktrees with territory-based file isolation,
     each runs the full afyapowers workflow (implement → review → complete)
```

8. **If user chooses 1 (Sequential):** proceed to Step 5B normally.

9. **If user chooses 2 (Parallel):**
   - Invoke `parallel-split` skill with:
     - `feature_slug`: the active feature slug
     - `plan_content`: full plan.md content
     - `design_content`: full design.md content (read from artifacts)
     - `task_groups`: the disconnected groups with task assignments
     - `all_tasks`: parsed tasks with deps, files, status
   - The parallel-split skill handles worktree creation, territory mapping, and terminal launch
   - After the skill completes, tell the user:
     "Parallel worktrees created. Each worktree will run implement → review → complete independently.
      After all worktrees finish, merge them in order and run `/afyapowers:next` to proceed with the parent feature's review."
   - **STOP** — do not invoke the implementing skill (worktree agents handle it)

### Step 5B: Normal Phase Invocation

Invoke the skill for the next phase:

| Next Phase | Skill to Invoke |
|-----------|----------------|
| plan | **writing-plans** |
| implement | **implementing** |
| review | **reviewing** |
| complete | **completing** |

When the skill completes and produces its artifact:
1. Save the artifact to `.afyapowers/features/<slug>/artifacts/`
2. Update `state.yaml` to add the artifact to the current phase's artifacts list
3. Append an `artifact_created` event to `history.yaml`
4. Tell the user: "Phase '<current-phase>' complete. Run `/afyapowers:next` to proceed to **<next-phase>**."

For the `complete` phase, instead say: "Phase complete. Run `/afyapowers:next` to finalize the feature."
