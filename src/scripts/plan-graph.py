#!/usr/bin/env python3
"""afyapowers-dev plan dependency-graph resolver.

Deterministic replacement for SDD Steps 1-4: parses the plan's tasks, detects
dependency cycles, computes the ready set, and filters it for file overlap —
without the orchestrator re-reading plan.md into context each wave.

Usage (from the project root):

    python3 plan-graph.py <path-to-plan.md> [--completed 1,2,5]

Output (`key=value` lines):

    task=N type=<Type> status=<pending|completed> deps=<csv> files=<csv>
    ...one line per task, then:
    ready=<csv of task numbers, already filtered for file overlap>

A task counts as completed when every checkbox in its block is `- [x]`
(or when its number is in `--completed`, which the orchestrator passes with
the tasks finished in previous waves of this session). On a circular
dependency the script prints `cycle=<N->M->...->N>` and exits 1; the
orchestrator must surface it and stop. Type-based concurrency caps and
implementer routing remain the orchestrator's judgment — this script only
resolves the graph.
"""

import io
import re
import sys

TASK_RE = re.compile(r"^### Task (\d+):|^### Tarefa (\d+):")
DEPS_RE = re.compile(r"^\*\*(Depends on|Depende de):\*\*\s*(.*)$")
TYPE_RE = re.compile(r"^\*\*Type:\*\*\s*(.*)$")
FILES_RE = re.compile(r"^\*\*Files:\*\*")
BACKTICK_RE = re.compile(r"`([^`]+)`")
CHECKBOX_RE = re.compile(r"^- \[( |x)\]")


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_tasks(text):
    """Return {n: {"deps": [..], "files": [..], "type": str, "boxes": (done, total)}}."""
    tasks = {}
    current = None
    in_files = False
    for line in text.splitlines():
        m = TASK_RE.match(line)
        if m:
            n = int(m.group(1) or m.group(2))
            tasks[n] = {"deps": [], "files": [], "type": "", "done": 0, "total": 0}
            current = tasks[n]
            in_files = False
            continue
        if line.startswith("## ") and current is not None:
            current = None
            in_files = False
            continue
        if current is None:
            continue
        dm = DEPS_RE.match(line)
        if dm:
            in_files = False
            value = dm.group(2).strip()
            if value.lower() not in ("none", "nenhuma", "nenhum", ""):
                current["deps"] = sorted(
                    {int(x) for x in re.findall(r"\d+", value)}
                )
            continue
        tm = TYPE_RE.match(line)
        if tm:
            in_files = False
            current["type"] = tm.group(1).strip()
            continue
        if FILES_RE.match(line):
            in_files = True
            continue
        if line.startswith("**"):
            in_files = False
        if in_files:
            for path in BACKTICK_RE.findall(line):
                if path not in current["files"]:
                    current["files"].append(path)
        cm = CHECKBOX_RE.match(line)
        if cm:
            current["total"] += 1
            if cm.group(1) == "x":
                current["done"] += 1
    return tasks


def find_cycle(tasks):
    """Return a cycle path like [3, 4, 3], or None."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in tasks}
    stack = []

    def visit(n):
        color[n] = GRAY
        stack.append(n)
        for dep in tasks[n]["deps"]:
            if dep not in tasks:
                continue
            if color[dep] == GRAY:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == WHITE:
                found = visit(dep)
                if found:
                    return found
        stack.pop()
        color[n] = BLACK
        return None

    for n in sorted(tasks):
        if color[n] == WHITE:
            found = visit(n)
            if found:
                return found
    return None


def main(argv):
    if not argv:
        sys.stderr.write("usage: plan-graph.py <plan.md> [--completed 1,2,5]\n")
        return 1
    plan_path = argv[0]
    completed_arg = set()
    if len(argv) >= 3 and argv[1] == "--completed":
        completed_arg = {int(x) for x in re.findall(r"\d+", argv[2])}
    elif len(argv) == 2 and argv[1].startswith("--completed="):
        completed_arg = {int(x) for x in re.findall(r"\d+", argv[1])}

    tasks = parse_tasks(read_text(plan_path))
    if not tasks:
        print("error=no_tasks_found")
        return 1

    cycle = find_cycle(tasks)
    if cycle:
        print("cycle=%s" % "->".join(str(n) for n in cycle))
        return 1

    status = {}
    for n, t in sorted(tasks.items()):
        done_by_boxes = t["total"] > 0 and t["done"] == t["total"]
        status[n] = "completed" if (done_by_boxes or n in completed_arg) else "pending"

    for n, t in sorted(tasks.items()):
        print("task=%d type=%s status=%s deps=%s files=%s" % (
            n,
            t["type"] or "?",
            status[n],
            ",".join(str(d) for d in t["deps"]),
            ",".join(t["files"]),
        ))

    ready = [
        n for n, t in sorted(tasks.items())
        if status[n] == "pending"
        and all(status.get(d) == "completed" for d in t["deps"])
    ]
    # File-overlap filter: keep the lower-numbered task, defer the other.
    kept = []
    for n in ready:
        files = set(tasks[n]["files"])
        if any(files & set(tasks[k]["files"]) for k in kept):
            continue
        kept.append(n)
    print("ready=%s" % ",".join(str(n) for n in kept))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except OSError as exc:
        print("error=io_failure")
        sys.stderr.write("plan-graph failed: %s\n" % exc)
        sys.exit(1)
