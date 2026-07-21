#!/usr/bin/env python3
"""afyapowers project scaffolding.

Idempotently create the content-free `.afyapowers/` structure for the current
working directory: the state dir, `features/`, `history/`, and a `.gitignore`
that keeps the active-feature pointer and conversation logs out of version
control. Feature-specific files (state.yaml, history.yaml, features/active) are
written by the `/afyapowers:new` skill, which needs timestamps and the feature
name, so this script deliberately does not touch them.

Run from the project root: `python3 setup.py`. Prints `ok=true` on success.
"""

import io
import os
import subprocess
import sys

AFYA = ".afyapowers"
GITIGNORE_LINES = ["features/active", "history/"]


def ensure_dirs():
    os.makedirs(os.path.join(AFYA, "features"), exist_ok=True)
    os.makedirs(os.path.join(AFYA, "history"), exist_ok=True)


def ensure_gitignore():
    """Create or top up `.afyapowers/.gitignore`, adding only missing lines."""
    path = os.path.join(AFYA, ".gitignore")
    existing = ""
    if os.path.isfile(path):
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            existing = fh.read()
    present = {
        ln.strip()
        for ln in existing.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    }
    missing = [ln for ln in GITIGNORE_LINES if ln not in present]
    if not missing:
        return
    with io.open(path, "a", encoding="utf-8") as fh:
        if existing and not existing.endswith("\n"):
            fh.write("\n")
        for ln in missing:
            fh.write(ln + "\n")


def emit_devex_event(trigger):
    """Fire-and-forget DevEx context event; must never affect the workflow."""
    try:
        root = os.path.abspath(__file__)
        for _ in range(4):  # skills/<skill>/scripts/<file> -> plugin root
            root = os.path.dirname(root)
        script = os.path.join(root, "hooks", "devex-context")
        if os.path.isfile(script):
            subprocess.Popen(
                [sys.executable, script, trigger],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass


def main():
    ensure_dirs()
    ensure_gitignore()
    emit_devex_event("setup")
    print("ok=true")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("ok=false")
        sys.stderr.write("afyapowers setup failed: %s\n" % exc)
        sys.exit(1)
