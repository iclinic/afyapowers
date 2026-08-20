#!/usr/bin/env python3
"""afyapowers-dev /next preflight validation.

Validates the active feature's current phase WITHOUT reading artifact files into
the model's context. Emits `key=value` lines (one per line) that the
`/afyapowers-dev:next` skill parses:

    slug, feature, current_phase, status, valid, next_phase, error, task_progress

Two early-exit cases print a single line only: `error=no_active_feature` and
`error=no_state_file`. Run from the project root: `python3 preflight.py`.
Mirrors the original preflight.sh contract exactly.
"""

import io
import os
import re
import sys

AFYA = ".afyapowers"
NEXT_PHASE = {
    "design": "plan",
    "plan": "implement",
    "implement": "review",
    "review": "complete",
    "complete": "finalize",
}


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def grep_value(text, key):
    """Return the value of the first `^key: ...` line, or '' if absent."""
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return line[len(key) + 1:].strip()
    return ""


def strip_quotes(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def review_approved(review_text):
    """Match both pt-BR and English verdict headers and approval patterns."""
    lines = review_text.splitlines()
    pat = re.compile(r"^\s*\*{0,2}(aprovad|approved)", re.IGNORECASE)
    for i, line in enumerate(lines):
        if "## Veredito" in line or "## Verdict" in line:
            for candidate in lines[i:i + 6]:
                if pat.match(candidate):
                    return True
    return False


def unaccepted_impedimentos(concerns_text):
    """Return blocking-concern lines from implementation-concerns.md that carry no
    [ACCEPTED BY USER: ...] marker.

    The implement phase must not advance on an unresolved divergence from the design.
    That gate lived only in the implementing skill's prose, so a skipped step let the
    workflow move to review with open visual/behavioral divergences. This makes it
    deterministic, like every other phase gate.

    Only the `## Impedimentos` section counts; `## Ressalvas` are non-blocking by design.
    """
    lines = concerns_text.splitlines()
    in_section = False
    pending = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            # Any new h2 ends the Impedimentos section.
            in_section = "Impedimento" in stripped
            continue
        if not in_section:
            continue
        # Concern entries are list items; "### Task N:" subheadings and prose are not.
        if not re.match(r"^\s*[-*]\s+\S", line):
            continue
        if "[ACCEPTED BY USER:" in line:
            continue
        pending.append(stripped)
    return pending


def emit(**fields):
    order = ["slug", "feature", "current_phase", "status",
             "valid", "next_phase", "error", "task_progress"]
    out = "".join("%s=%s\n" % (k, fields.get(k, "")) for k in order)
    sys.stdout.write(out)


def main():
    active = os.path.join(AFYA, "features", "active")
    if not os.path.isfile(active):
        print("error=no_active_feature")
        return

    slug = read_text(active).strip()
    if not slug or slug in (".", "..") or os.path.basename(slug) != slug:
        print("error=no_active_feature")
        return
    feature_dir = os.path.join(AFYA, "features", slug)
    state_file = os.path.join(feature_dir, "state.yaml")
    if not os.path.isfile(state_file):
        print("error=no_state_file")
        return

    state = read_text(state_file)
    phase = grep_value(state, "current_phase")
    name = strip_quotes(grep_value(state, "feature"))
    status = grep_value(state, "status")
    artifacts = os.path.join(feature_dir, "artifacts")

    valid = False
    err = ""
    task_progress = ""

    def has(filename):
        return os.path.isfile(os.path.join(artifacts, filename))

    if phase == "design":
        valid = has("design.md")
        if not valid:
            err = "Design artifact missing. Complete the design phase first."
    elif phase == "plan":
        valid = has("plan.md")
        if not valid:
            err = "Plan artifact missing. Complete the plan phase first."
    elif phase == "implement":
        plan_path = os.path.join(artifacts, "plan.md")
        if not os.path.isfile(plan_path):
            err = "Plan artifact missing. Complete the plan phase first."
        else:
            plan = read_text(plan_path)
            total = len(re.findall(r"(?m)^- \[", plan))
            done = len(re.findall(r"(?m)^- \[x\]", plan))
            rem = total - done
            task_progress = "%d/%d" % (done, total)
            if total == 0:
                err = "No tasks found in plan.md."
            elif rem > 0:
                err = "%d of %d tasks still unchecked." % (rem, total)
            else:
                concerns_path = os.path.join(artifacts, "implementation-concerns.md")
                pending = []
                if os.path.isfile(concerns_path):
                    pending = unaccepted_impedimentos(read_text(concerns_path))
                if pending:
                    err = (
                        "%d blocking concern(s) in implementation-concerns.md are neither "
                        "fixed nor accepted. Resolve each one, or record acceptance with "
                        "[ACCEPTED BY USER: <reason>] on its line. First: %s"
                        % (len(pending), pending[0][:120])
                    )
                else:
                    valid = True
    elif phase == "review":
        review_path = os.path.join(artifacts, "review.md")
        if os.path.isfile(review_path) and review_approved(read_text(review_path)):
            valid = True
        elif not os.path.isfile(review_path):
            err = "Review artifact missing."
        else:
            err = "Review verdict is not Approved. Check review.md for findings."
    elif phase == "complete":
        valid = has("completion.md")
        if not valid:
            err = "Completion artifact missing."
    else:
        err = "Unknown phase: %s" % phase

    emit(
        slug=slug,
        feature=name,
        current_phase=phase,
        status=status,
        valid="true" if valid else "false",
        next_phase=NEXT_PHASE.get(phase, ""),
        error=err,
        task_progress=task_progress,
    )


if __name__ == "__main__":
    main()
