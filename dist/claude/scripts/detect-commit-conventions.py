#!/usr/bin/env python3
"""afyapowers-dev commit-conventions detector.

Deterministic replacement for SDD Step 0: inspects the repo once (git log,
branch name, hook tooling, commitlint config) and prints a ready-to-store
`## Commit Conventions` markdown block in the exact format the
subagent-driven-development skill defines. The orchestrator stores the block
and uses it when committing completed tasks — no per-fact tool calls needed.

Run from the project root: `python3 detect-commit-conventions.py`.
Prints the markdown block on stdout; on a fatal error prints the
"no conventions detected" block (committing freely is the safe default).
"""

import io
import json
import os
import re
import subprocess
import sys

CONVENTIONAL_TYPES = [
    "feat", "fix", "chore", "refactor", "test", "docs",
    "style", "ci", "build", "perf", "revert",
]
CONVENTIONAL_RE = re.compile(
    r"^(%s)(\(([^)]*)\))?!?:\s" % "|".join(CONVENTIONAL_TYPES)
)
# Jira-style keys appear uppercase in branch names but often lowercase in
# commit scopes (e.g. `feat(devex-78): ...`), so match case-insensitively.
TICKET_RE = re.compile(r"\b([A-Za-z]{2,10}-\d{1,6})\b")
TICKET_PREFIX_RE = re.compile(r"^(\[[A-Za-z]{2,10}-\d+\]|[A-Za-z]{2,10}-\d+[:\s])")

NO_CONVENTIONS_BLOCK = """## Commit Conventions

**Message format:** no enforced convention detected
**Pre-commit hooks:** none detected
**Commit freely** using clear, descriptive messages. If a commit fails unexpectedly, read the error and retry up to 3 times before surfacing the error to the user."""

FAILURE_RULES = """**If a commit fails:**
1. Read the error output — it tells you exactly what's wrong
2. Commitlint rejection -> rewrite the message to match the format above and retry
3. Lint/format failure -> fix the reported issues or run the suggested fix command, re-stage **only the same task's files** (`git add -- <files>`), retry
4. Other hook failure -> read the error, apply the fix, re-stage the same task's files, retry
5. After 3 failed attempts -> leave the changes staged and surface the full error to the user
6. Never use `--no-verify` on your own initiative. Exception: if the failure is demonstrably pre-existing (files the task never touched) or environmental (hook tool missing/broken), offer the user the choice of committing with `commit-task.py --no-verify` — only with their explicit approval"""


def run_git(args):
    try:
        out = subprocess.run(
            ["git"] + args, capture_output=True, text=True, timeout=30
        )
        if out.returncode != 0:
            return ""
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def detect_hooks():
    tools = []
    if os.path.isfile(".lefthook.yml") or os.path.isfile("lefthook.yml"):
        tools.append("Lefthook (.lefthook.yml)")
    if os.path.isfile(os.path.join(".husky", "pre-commit")):
        tools.append("Husky (.husky/pre-commit)")
    if os.path.isfile(".pre-commit-config.yaml"):
        tools.append("pre-commit framework (.pre-commit-config.yaml)")
    if not tools and os.path.isfile("package.json"):
        try:
            pkg = json.loads(read_text("package.json"))
            prepare = (pkg.get("scripts") or {}).get("prepare", "")
            if "husky" in prepare:
                tools.append("Husky (package.json scripts.prepare)")
            elif "lefthook" in prepare:
                tools.append("Lefthook (package.json scripts.prepare)")
        except ValueError:
            pass
    return tools


def detect_commitlint():
    candidates = [
        "commitlint.config.js", "commitlint.config.cjs",
        "commitlint.config.mjs", "commitlint.config.ts",
        ".commitlintrc", ".commitlintrc.json",
        ".commitlintrc.yml", ".commitlintrc.js",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    if os.path.isfile("package.json"):
        try:
            pkg = json.loads(read_text("package.json"))
            if "commitlint" in pkg:
                return "package.json (commitlint field)"
        except ValueError:
            pass
    return ""


def main():
    log = run_git(["log", "--oneline", "-20"])
    messages = []
    for line in log.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            messages.append(parts[1].strip())

    hooks = detect_hooks()
    commitlint = detect_commitlint()

    if not messages and not hooks and not commitlint:
        print(NO_CONVENTIONS_BLOCK)
        return 0

    conventional = [m for m in messages if CONVENTIONAL_RE.match(m)]
    ticketed = [m for m in messages if TICKET_PREFIX_RE.match(m)]
    with_ticket_anywhere = [m for m in messages if TICKET_RE.search(m)]

    types_seen = []
    scoped = 0
    for m in conventional:
        match = CONVENTIONAL_RE.match(m)
        t = match.group(1)
        if t not in types_seen:
            types_seen.append(t)
        if match.group(2):
            scoped += 1

    n = len(messages)
    if n and len(conventional) >= max(2, n // 2):
        fmt = "conventional commits — type(scope): description"
        if scoped >= max(1, len(conventional) // 2):
            scope = "commonly used"
        elif scoped:
            scope = "rarely used"
        else:
            scope = "not used"
        types_line = ", ".join(types_seen) if types_seen else "none observed"
    elif n and len(ticketed) >= max(2, n // 2):
        fmt = "ticket-prefixed — [PROJ-123] description"
        scope = "not used"
        types_line = "none observed"
    elif n:
        fmt = "freeform (no consistent pattern in the last %d commits)" % n
        scope = "not used"
        types_line = "none observed"
    else:
        fmt = "no commit history yet"
        scope = "not used"
        types_line = "none observed"

    ticket_line = "none detected"
    if with_ticket_anywhere:
        branch = run_git(["branch", "--show-current"])
        m = TICKET_RE.search(branch or "")
        if m:
            ticket_line = "%s (from branch %s)" % (m.group(1), branch)
        else:
            ticket_line = (
                "commit history references ticket IDs, but none found in the "
                "current branch name (%s) — ask the user if one is required"
                % (branch or "detached")
            )

    examples = messages[:5]
    hooks_line = " + ".join(hooks) if hooks else "none detected"
    if commitlint:
        commitlint_line = (
            "yes — messages must follow conventional commits format (%s)" % commitlint
        )
    else:
        commitlint_line = "not detected"

    out = ["## Commit Conventions", ""]
    out.append("**Message format:** %s" % fmt)
    out.append("**Common types:** %s" % types_line)
    out.append("**Scope:** %s" % scope)
    out.append("**Ticket ID:** %s" % ticket_line)
    out.append("**Examples from this repo:**")
    if examples:
        for ex in examples:
            out.append("- %s" % ex)
    else:
        out.append("- (no commits yet)")
    out.append("")
    out.append("**Pre-commit hooks:** %s" % hooks_line)
    out.append("**Commitlint:** %s" % commitlint_line)
    out.append("")
    out.append(FAILURE_RULES)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        sys.stderr.write("detect-commit-conventions failed: %s\n" % exc)
        print(NO_CONVENTIONS_BLOCK)
        sys.exit(0)
