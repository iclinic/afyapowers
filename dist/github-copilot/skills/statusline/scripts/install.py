#!/usr/bin/env python3
"""Install or remove the afyapowers status line for the current user.

Idempotent, run by the `/afyapowers:statusline` skill. Install writes the
user-level `~/.claude/afyapowers/plugin-root` pointer (kept fresh by the
session-start hook across plugin upgrades) and merges a `statusLine` entry
into the user's `~/.claude/settings.json` — never touching other keys, so
the status line applies to every project on this machine. `--remove`
deletes only that entry.

The status line script itself resolves per-project state (active feature,
Jira ticket) from the session's working directory at run time, so projects
without afyapowers simply omit those segments.

Prints `ok=true` on success, `ok=false` + stderr detail on failure.
"""

import argparse
import io
import json
import os
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SETTINGS = CLAUDE_DIR / "settings.json"
POINTER = CLAUDE_DIR / "afyapowers" / "plugin-root"

# The statusLine command resolves the plugin through the pointer at run
# time. Double guard: a missing/stale pointer yields a blank status line
# (and a drained stdin) instead of a visible error.
STATUSLINE_COMMAND = (
    'p=$(cat "$HOME/.claude/afyapowers/plugin-root" 2>/dev/null); '
    'if [ -n "$p" ] && [ -f "$p/scripts/statusline.py" ]; '
    'then exec python3 "$p/scripts/statusline.py" 2>/dev/null; fi; '
    "cat >/dev/null"
)


def plugin_root():
    # install.py -> scripts -> statusline -> skills -> <plugin root>.
    # Depth is identical under Cursor's `afyapowers-` skill dir prefix.
    return Path(__file__).resolve().parents[3]


def load_settings():
    """Existing settings, `{}` when absent. Invalid JSON aborts — never
    clobber a file the user hand-edited into a broken state."""
    if not SETTINGS.is_file():
        return {}
    with io.open(SETTINGS, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_settings(settings):
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    with io.open(SETTINGS, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def install():
    root = plugin_root()
    if not (root / "scripts" / "statusline.py").is_file():
        raise RuntimeError("statusline.py not found under plugin root: %s" % root)
    POINTER.parent.mkdir(parents=True, exist_ok=True)
    with io.open(POINTER, "w", encoding="utf-8") as fh:
        fh.write(str(root) + "\n")
    settings = load_settings()
    settings["statusLine"] = {
        "type": "command",
        "command": STATUSLINE_COMMAND,
    }
    save_settings(settings)


def remove():
    """Delete only the statusLine key. The pointer stays: it is harmless
    and the session-start hook would recreate it anyway."""
    if SETTINGS.is_file():
        settings = load_settings()
        if settings.pop("statusLine", None) is not None:
            save_settings(settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--remove", action="store_true", help="remove the status line entry"
    )
    args = parser.parse_args()
    if args.remove:
        remove()
    else:
        install()
    print("ok=true")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ok=false")
        sys.stderr.write("afyapowers statusline install failed: %s\n" % exc)
        sys.exit(1)
