#!/usr/bin/env python3
"""afyapowers-dev per-task commit cycle.

Deterministic replacement for SDD Step 6.5: one call per completed task does
selective staging, staging verification, the commit, and the plan.md checkbox
flip — collapsing 3-5 orchestrator turns into one.

Usage (from the project root):

    python3 commit-task.py --files "src/a.ts,src/a.test.ts" \
        [--assets "public/icon.svg"] --message "feat(X): ..." \
        [--task N --plan .afyapowers/features/<slug>/artifacts/plan.md]

    python3 commit-task.py --flip-only --task N --plan <plan.md>   # repair mode

Behavior and output (`key=value` lines):

  - Stages ONLY the given files/assets (`git add -- ...`), then verifies with
    `git diff --cached --name-only`. Any staged path outside the list aborts
    with `error=unexpected_staged_file:<path>` plus `staged=<csv>` — surface
    that to the user; nothing is committed and staging is left as-is.
  - Commits with the given message. On a hook/commitlint failure prints
    `hook_error=<combined output, tail-truncated>` and leaves the task's files
    staged: the RETRY is the model's judgment (max 3 attempts, fix what the
    hook reported, re-stage only this task's files, NEVER `--no-verify`).
  - On success prints `ok=true` and `sha=<sha>`; when `--task`/`--plan` are
    given, first flips every `- [ ]` to `- [x]` inside that task's block in
    plan.md (`checkboxes_flipped=<n>`). plan.md itself stays uncommitted,
    exactly as the manual flow left it.

Expected failures exit 0 with `error=`/`hook_error=`; only I/O faults exit 1.
"""

import io
import re
import subprocess
import sys

TAIL = 2500


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def run_git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def parse_args(argv):
    opts = {"files": "", "assets": "", "message": "", "task": "",
            "plan": "", "flip_only": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--flip-only":
            opts["flip_only"] = True
            i += 1
            continue
        key = a.lstrip("-").replace("-", "_")
        if key not in opts or i + 1 >= len(argv):
            return None
        opts[key] = argv[i + 1]
        i += 2
    return opts


def split_paths(csv):
    return [p.strip() for p in csv.split(",") if p.strip()]


def flip_checkboxes(plan_path, task_n):
    """Flip `- [ ]` to `- [x]` inside the `### Task N:`/`### Tarefa N:` block."""
    text = read_text(plan_path)
    lines = text.splitlines()
    header = re.compile(r"^### (Task|Tarefa) %s:" % re.escape(task_n))
    any_task = re.compile(r"^### (Task|Tarefa) \d+:|^## ")
    start = None
    for i, line in enumerate(lines):
        if header.match(line):
            start = i
            break
    if start is None:
        return -1
    flipped = 0
    for i in range(start + 1, len(lines)):
        if any_task.match(lines[i]):
            break
        if lines[i].startswith("- [ ]"):
            lines[i] = "- [x]" + lines[i][5:]
            flipped += 1
    ending = "\n" if text.endswith("\n") else ""
    write_text(plan_path, "\n".join(lines) + ending)
    return flipped


def main(argv):
    opts = parse_args(argv)
    if opts is None:
        print("ok=false")
        print("error=bad_arguments")
        sys.stderr.write(
            "usage: commit-task.py --files <csv> [--assets <csv>] --message <msg>"
            " [--task N --plan <plan.md>] | --flip-only --task N --plan <plan.md>\n"
        )
        return 1

    if opts["flip_only"]:
        if not (opts["task"] and opts["plan"]):
            print("ok=false")
            print("error=bad_arguments")
            return 1
        flipped = flip_checkboxes(opts["plan"], opts["task"])
        if flipped < 0:
            print("ok=false")
            print("error=task_not_found_in_plan:%s" % opts["task"])
            return 0
        print("ok=true")
        print("checkboxes_flipped=%d" % flipped)
        return 0

    files = split_paths(opts["files"])
    assets = split_paths(opts["assets"])
    if not files or not opts["message"]:
        print("ok=false")
        print("error=bad_arguments")
        return 1
    allowed = files + assets

    add = run_git(["add", "--"] + allowed)
    if add.returncode != 0:
        print("ok=false")
        print("error=git_add_failed")
        sys.stdout.write("git_error=%s\n" % (add.stderr.strip()[-TAIL:].replace("\n", " | ")))
        return 0

    staged_out = run_git(["diff", "--cached", "--name-only"])
    staged = [p for p in staged_out.stdout.splitlines() if p.strip()]
    unexpected = [p for p in staged if p not in allowed]
    if unexpected:
        print("ok=false")
        print("error=unexpected_staged_file:%s" % unexpected[0])
        print("staged=%s" % ",".join(staged))
        return 0

    commit = run_git(["commit", "-m", opts["message"]])
    if commit.returncode != 0:
        combined = (commit.stdout + "\n" + commit.stderr).strip()
        print("ok=false")
        print("hook_error=%s" % combined[-TAIL:].replace("\n", " | "))
        return 0

    sha = run_git(["rev-parse", "--short", "HEAD"]).stdout.strip()

    flipped = ""
    if opts["task"] and opts["plan"]:
        n = flip_checkboxes(opts["plan"], opts["task"])
        flipped = str(n) if n >= 0 else "task_not_found"

    print("ok=true")
    print("sha=%s" % sha)
    if flipped != "":
        print("checkboxes_flipped=%s" % flipped)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except OSError as exc:
        print("ok=false")
        sys.stderr.write("commit-task failed: %s\n" % exc)
        sys.exit(1)
