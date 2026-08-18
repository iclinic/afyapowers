#!/usr/bin/env python3
"""afyapowers status line for Claude Code.

Reads the session JSON Claude Code pipes to stdin and prints up to three
lines: plugin version / model / context usage, active feature + phase +
Jira ticket, and git status + session cost/duration. Installed into the
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
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

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
            return "%s⚡ afyapowers v%s%s" % (CYAN, version, RESET)
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


def _yaml_line(text, key):
    """First `key: value` line of a state.yaml, quotes stripped."""
    match = re.search(r"^%s: *(.*)$" % key, text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value or None


def _active_state(cwd):
    """(feature_dir, state.yaml text) of the active feature, or None."""
    features_dir = Path(cwd) / ".afyapowers" / "features"
    try:
        slug = (features_dir / "active").read_text(encoding="utf-8").strip()
    except Exception:
        return None
    feature_dir = features_dir / slug
    if not slug or not feature_dir.is_dir():
        return None
    try:
        return feature_dir, (feature_dir / "state.yaml").read_text(encoding="utf-8")
    except Exception:
        return None


def seg_feature(cwd):
    active = _active_state(cwd)
    if not active:
        return None
    name = _yaml_line(active[1], "feature")
    return "\U0001f3af %s" % name if name else None


def seg_phase(cwd):
    active = _active_state(cwd)
    if not active:
        return None
    feature_dir, state = active
    phase = _yaml_line(state, "current_phase")
    if not phase:
        return None
    tasks = ""
    if phase == "implement":
        try:
            plan = (feature_dir / "artifacts" / "plan.md").read_text(encoding="utf-8")
            total = len(re.findall(r"^- \[", plan, re.MULTILINE))
            done = len(re.findall(r"^- \[x\]", plan, re.MULTILINE))
            if total:
                tasks = " (%d/%d)" % (done, total)
        except Exception:
            pass
    return "%s%s" % (phase, tasks)


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
    return "%s\U0001f3ab %s%s" % (MAGENTA, raw, RESET)


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
    return "\U0001f4b0 $%.2f" % cost


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

    # Feature, phase and Jira ticket share one line, each behind its own
    # gate: any subset of the three renders, joined by a middle dot.
    feature_line = " · ".join(
        s
        for s in (_safe(seg_feature, cwd), _safe(seg_phase, cwd), _safe(seg_jira, cwd))
        if s
    )

    lines = [
        [_safe(seg_version), _safe(seg_model, data), _safe(seg_context, data)],
        [feature_line],
        [_safe(seg_git, cwd), _safe(seg_cost, data), _safe(seg_duration, data)],
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
