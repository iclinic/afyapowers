#!/usr/bin/env python3
"""afyapowers status line for Claude Code.

Reads the session JSON Claude Code pipes to stdin and prints up to three
lines: plugin version / model / context usage, Jira ticket + git status,
and session cost/duration. Installed into the
project's `.claude/settings.json` by the `/afyapowers:statusline` skill,
which resolves this script through the `.afyapowers/plugin-root` pointer
maintained by the session-start hook (the install path changes on every
plugin version upgrade).

Every field is optional: absent segments are dropped, empty lines are not
printed, and any unexpected error results in silence rather than a
traceback — a non-zero exit or stderr noise would blank the status line.

No caching for now: the single `git status` subprocess is the only
non-trivial cost (~10-40ms). If huge repositories ever make this laggy,
cache its output in a session_id-keyed temp file as the official docs
suggest.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RESET = "\033[0m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
AFYA_PINK = "\033[38;2;196;4;84m"
JIRA_BLUE = "\033[38;5;33m"

SEPARATOR = DIM + " │ " + RESET

# Same lookup the otel-context hook uses: the manifest sits beside this
# script's parent directory, whatever the host IDE's layout calls it.
MANIFEST_RELATIVE_PATHS = (
    Path(".claude-plugin") / "plugin.json",
    Path(".cursor-plugin") / "plugin.json",
    Path("plugin.json"),
)

JIRA_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
GIT_TIMEOUT = 1.5


def read_stdin_json():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_cwd(data):
    workspace = data.get("workspace") or {}
    return (
        workspace.get("current_dir")
        or workspace.get("project_dir")
        or os.getcwd()
    )


def seg_version():
    root = Path(__file__).resolve().parent.parent
    for relative in MANIFEST_RELATIVE_PATHS:
        try:
            manifest = json.loads((root / relative).read_text(encoding="utf-8"))
        except Exception:
            continue
        version = manifest.get("version") if isinstance(manifest, dict) else None
        if version:
            return "%s⚡ afyapowers v%s%s" % (AFYA_PINK, version, RESET)
    return None


def seg_model(data):
    name = (data.get("model") or {}).get("display_name")
    return "\U0001f916 %s" % name if name else None


def seg_context(data):
    pct = (data.get("context_window") or {}).get("used_percentage")
    if pct is None:
        return None
    pct = int(pct)
    color = RED if pct >= 90 else YELLOW if pct >= 70 else GREEN
    return "%s\U0001f9e0 %d%%%s" % (color, pct, RESET)


def seg_jira(cwd):
    try:
        raw = (Path(cwd) / ".afyapowers" / "current-jira-ticket").read_text(
            encoding="utf-8"
        ).strip()
    except Exception:
        return None
    if raw.lower() == "none":
        return None
    raw = raw.upper()
    if not JIRA_KEY_RE.match(raw):
        return None
    return "%s\U0001f3af %s%s" % (JIRA_BLUE, raw, RESET)


def seg_git(cwd):
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain=v1", "--branch"],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    branch = None
    staged = 0
    modified = 0
    for line in result.stdout.splitlines():
        if line.startswith("## "):
            branch = line[3:].split("...")[0].strip()
        elif line.startswith("??"):
            modified += 1
        elif len(line) >= 2:
            if line[0] in "MADRC":
                staged += 1
            if line[1] != " ":
                modified += 1
    if not branch:
        return None
    color = GREEN if staged == 0 and modified == 0 else YELLOW
    parts = ["%s\U0001f33f %s%s" % (color, branch, RESET)]
    if staged:
        parts.append("%s+%d%s" % (GREEN, staged, RESET))
    if modified:
        parts.append("%s~%d%s" % (YELLOW, modified, RESET))
    return " ".join(parts)


def seg_cost(data):
    cost = (data.get("cost") or {}).get("total_cost_usd")
    if cost is None:
        return None
    return "%s\U0001f4b0 $%.2f%s" % (GREEN, cost, RESET)


def seg_duration(data):
    ms = (data.get("cost") or {}).get("total_duration_ms")
    if ms is None:
        return None
    seconds = int(ms) // 1000
    if seconds < 60:
        text = "%ds" % seconds
    elif seconds < 3600:
        text = "%dm" % (seconds // 60)
    else:
        text = "%dh%02dm" % (seconds // 3600, (seconds % 3600) // 60)
    return "⏱ %s" % text


def _safe(builder, *args):
    """One broken segment must not blank the whole status line."""
    try:
        return builder(*args)
    except Exception:
        return None


def main():
    data = read_stdin_json()
    cwd = resolve_cwd(data)

    lines = [
        [_safe(seg_version), _safe(seg_model, data), _safe(seg_context, data)],
        [_safe(seg_jira, cwd), _safe(seg_git, cwd)],
        [_safe(seg_cost, data), _safe(seg_duration, data)],
    ]
    for segments in lines:
        segments = [s for s in segments if s]
        if segments:
            print(SEPARATOR.join(segments))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
