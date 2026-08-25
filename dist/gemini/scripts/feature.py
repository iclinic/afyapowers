#!/usr/bin/env python3
"""afyapowers-dev feature state machine.

Deterministic replacement for the state mutations the workflow skills used to
describe in prose: scaffolding, state.yaml/history.yaml edits, phase gates and
phase transitions all happen here, WITHOUT reading artifact files into the
model's context. Emits `key=value` lines the skills parse.

Subcommands (run from the project root):

    feature.py new "<feature name>"   -> ok, slug
    feature.py check                  -> slug, feature, current_phase, status,
                                         valid, next_phase, error, task_progress
    feature.py advance                -> check keys + advanced   (mutates when valid)
    feature.py gate <expected-phase>  -> slug, current_phase, match
    feature.py record-artifact <file> -> ok, phase
    feature.py abort ["reason"]       -> ok

`check` mirrors the retired preflight.py contract exactly, including the two
single-line early exits `error=no_active_feature` and `error=no_state_file`
(also used by gate/record-artifact/advance/abort). `advance` emits the
PRE-transition keys (`next_phase` is the phase that just started when
`advanced=true`). Unexpected I/O failures print `ok=false` and exit 1.
"""

import io
import os
import re
import sys
from datetime import datetime, timezone

AFYA = ".afyapowers"
GITIGNORE_LINES = ["features/active", "history/", "otel-debug.jsonl", "current-jira-ticket"]
PHASES = ["design", "plan", "implement", "review", "complete"]
NEXT_PHASE = {
    "design": "plan",
    "plan": "implement",
    "implement": "review",
    "review": "complete",
    "complete": "finalize",
}


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


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


# ---------------------------------------------------------------------------
# Scaffolding (absorbed from the retired new/scripts/setup.py)
# ---------------------------------------------------------------------------

def ensure_dirs():
    os.makedirs(os.path.join(AFYA, "features"), exist_ok=True)
    os.makedirs(os.path.join(AFYA, "history"), exist_ok=True)


def ensure_jira_pointer():
    """Create `current-jira-ticket` EMPTY when absent, never touching an
    existing one.

    Empty is the "nobody has been asked yet" state: the afyapowers-core
    plugin's jira-context hook reads an empty/garbage/missing pointer the same
    way and asks the user, while the literal `none` means the user explicitly
    works without a ticket and must not be asked again."""
    path = os.path.join(AFYA, "current-jira-ticket")
    if os.path.exists(path):
        return
    with io.open(path, "w", encoding="utf-8"):
        pass


def ensure_gitignore():
    """Create or top up `.afyapowers/.gitignore`, adding only missing lines."""
    path = os.path.join(AFYA, ".gitignore")
    existing = ""
    if os.path.isfile(path):
        existing = read_text(path)
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


# ---------------------------------------------------------------------------
# Active-feature resolution
# ---------------------------------------------------------------------------

def resolve_active():
    """Return (slug, feature_dir, state_file) or print a sentinel and return None."""
    active = os.path.join(AFYA, "features", "active")
    if not os.path.isfile(active):
        print("error=no_active_feature")
        return None
    slug = read_text(active).strip()
    if not slug or slug in (".", "..") or os.path.basename(slug) != slug:
        print("error=no_active_feature")
        return None
    feature_dir = os.path.join(AFYA, "features", slug)
    state_file = os.path.join(feature_dir, "state.yaml")
    if not os.path.isfile(state_file):
        print("error=no_state_file")
        return None
    return slug, feature_dir, state_file


# ---------------------------------------------------------------------------
# state.yaml textual edits (schema is fixed and script-generated)
# ---------------------------------------------------------------------------

def set_top_key(lines, key, value):
    for i, line in enumerate(lines):
        if line.startswith(key + ":"):
            lines[i] = "%s: %s" % (key, value)
            return
    lines.append("%s: %s" % (key, value))


def phase_span(lines, phase):
    """Return (start, end) of the `  <phase>:` block under `phases:` —
    start is the header line index, end is one past the last body line."""
    header = "  %s:" % phase
    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == header:
            start = i
            break
    if start is None:
        return None
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line.startswith("    "):
            break
        end += 1
    return start, end


def set_phase_key(lines, phase, key, value):
    span = phase_span(lines, phase)
    if span is None:
        return False
    start, end = span
    for i in range(start + 1, end):
        if lines[i].startswith("    %s:" % key):
            lines[i] = "    %s: %s" % (key, value)
            return True
    lines.insert(end, "    %s: %s" % (key, value))
    return True


def add_artifact(lines, phase, filename):
    """Idempotently add `filename` to the phase's artifacts list (block style,
    matching what the manual flow produced at runtime)."""
    span = phase_span(lines, phase)
    if span is None:
        return False
    start, end = span
    art = None
    for i in range(start + 1, end):
        if lines[i].startswith("    artifacts:"):
            art = i
            break
    if art is None:
        lines.insert(end, "    artifacts:")
        lines.insert(end + 1, "      - %s" % filename)
        return "added"
    rest = lines[art][len("    artifacts:"):].strip()
    if rest in ("[]", ""):
        items = []
    else:
        # Flow style `["a.md", "b.md"]` written by older manual runs.
        items = [strip_quotes(x.strip()) for x in rest.strip("[]").split(",") if x.strip()]
    # Collect any existing block-style items.
    j = art + 1
    while j < end and re.match(r"^      - \S", lines[j]):
        items.append(strip_quotes(lines[j].strip()[2:].strip()))
        j += 1
    if filename in items:
        return "present"
    items.append(filename)
    block = ["    artifacts:"] + ["      - %s" % item for item in items]
    lines[art:j] = block
    return "added"


def append_events(feature_dir, events):
    """Append event dicts (ordered key/value pairs) to history.yaml."""
    path = os.path.join(feature_dir, "history.yaml")
    existing = read_text(path) if os.path.isfile(path) else "events:\n"
    if not existing.endswith("\n"):
        existing += "\n"
    out = []
    for ev in events:
        first = True
        for k, v in ev:
            prefix = "  - " if first else "    "
            out.append("%s%s: %s" % (prefix, k, v))
            first = False
    write_text(path, existing + "\n".join(out) + "\n")


# ---------------------------------------------------------------------------
# Validation (ported from the retired next/scripts/preflight.py)
# ---------------------------------------------------------------------------

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
    Only the `## Impedimentos` section counts; `## Ressalvas` are non-blocking by design.
    """
    lines = concerns_text.splitlines()
    in_section = False
    pending = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = "Impedimento" in stripped
            continue
        if not in_section:
            continue
        if not re.match(r"^\s*[-*]\s+\S", line):
            continue
        if "[ACCEPTED BY USER:" in line:
            continue
        pending.append(stripped)
    return pending


def run_check(slug, feature_dir, state_file):
    """Return the preflight result dict (keys of the `check` contract)."""
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

    return {
        "slug": slug,
        "feature": name,
        "current_phase": phase,
        "status": status,
        "valid": valid,
        "next_phase": NEXT_PHASE.get(phase, ""),
        "error": err,
        "task_progress": task_progress,
    }


def emit_check(result, extra=None):
    order = ["slug", "feature", "current_phase", "status",
             "valid", "next_phase", "error", "task_progress"]
    out = ""
    for k in order:
        v = result.get(k, "")
        if isinstance(v, bool):
            v = "true" if v else "false"
        out += "%s=%s\n" % (k, v)
    for k, v in (extra or []):
        out += "%s=%s\n" % (k, v)
    sys.stdout.write(out)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_new(name):
    ensure_dirs()
    ensure_jira_pointer()
    ensure_gitignore()

    slug = name.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)[:50].strip("-")
    if not slug:
        print("ok=false")
        print("error=empty_slug")
        return 1
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = "%s-%s" % (date, slug)
    dirname = base
    n = 2
    while os.path.isdir(os.path.join(AFYA, "features", dirname)):
        dirname = "%s-%d" % (base, n)
        n += 1
    feature_dir = os.path.join(AFYA, "features", dirname)
    os.makedirs(os.path.join(feature_dir, "artifacts"))

    ts = now_iso()
    state = (
        "feature: %s\n"
        "status: active\n"
        "created_at: %s\n"
        "current_phase: design\n"
        "phases:\n"
        "  design:\n"
        "    status: in_progress\n"
        "    started_at: %s\n"
        "    artifacts: []\n"
        "  plan:\n"
        "    status: pending\n"
        "  implement:\n"
        "    status: pending\n"
        "  review:\n"
        "    status: pending\n"
        "  complete:\n"
        "    status: pending\n"
    ) % (name, ts, ts)
    write_text(os.path.join(feature_dir, "state.yaml"), state)
    write_text(
        os.path.join(feature_dir, "history.yaml"),
        (
            "events:\n"
            "  - timestamp: %s\n"
            "    event: feature_created\n"
            "    phase: design\n"
            "    command: /afyapowers-dev:new\n"
            "    details: \"Feature '%s' created\"\n"
            "  - timestamp: %s\n"
            "    event: phase_started\n"
            "    phase: design\n"
        ) % (ts, name, ts),
    )
    write_text(os.path.join(AFYA, "features", "active"), dirname + "\n")
    print("ok=true")
    print("slug=%s" % dirname)
    return 0


def cmd_check():
    resolved = resolve_active()
    if resolved is None:
        return 0
    emit_check(run_check(*resolved))
    return 0


def cmd_advance():
    resolved = resolve_active()
    if resolved is None:
        return 0
    slug, feature_dir, state_file = resolved
    result = run_check(slug, feature_dir, state_file)
    if not result["valid"]:
        emit_check(result, extra=[("advanced", "false")])
        return 0

    phase = result["current_phase"]
    ts = now_iso()
    lines = read_text(state_file).splitlines()
    if phase == "complete":
        set_phase_key(lines, "complete", "status", "completed")
        set_phase_key(lines, "complete", "completed_at", ts)
        set_top_key(lines, "status", "completed")
        events = [
            [("timestamp", ts), ("event", "phase_completed"),
             ("phase", "complete"), ("command", "/afyapowers-dev:next")],
            [("timestamp", ts), ("event", "feature_completed"), ("phase", "complete")],
        ]
    else:
        nxt = NEXT_PHASE[phase]
        set_phase_key(lines, phase, "status", "completed")
        set_phase_key(lines, phase, "completed_at", ts)
        set_phase_key(lines, nxt, "status", "in_progress")
        set_phase_key(lines, nxt, "started_at", ts)
        set_top_key(lines, "current_phase", nxt)
        events = [
            [("timestamp", ts), ("event", "phase_completed"),
             ("phase", phase), ("command", "/afyapowers-dev:next")],
            [("timestamp", ts), ("event", "phase_started"), ("phase", nxt)],
        ]
    write_text(state_file, "\n".join(lines) + "\n")
    append_events(feature_dir, events)
    emit_check(result, extra=[("advanced", "true")])
    return 0


def cmd_gate(expected):
    resolved = resolve_active()
    if resolved is None:
        return 0
    slug, _feature_dir, state_file = resolved
    phase = grep_value(read_text(state_file), "current_phase")
    print("slug=%s" % slug)
    print("current_phase=%s" % phase)
    print("match=%s" % ("true" if phase == expected else "false"))
    return 0


def cmd_record_artifact(filename):
    resolved = resolve_active()
    if resolved is None:
        return 0
    slug, feature_dir, state_file = resolved
    phase = grep_value(read_text(state_file), "current_phase")
    if phase not in PHASES:
        print("ok=false")
        print("error=unknown_phase:%s" % phase)
        return 1
    lines = read_text(state_file).splitlines()
    added = add_artifact(lines, phase, filename)
    if added == "added":
        write_text(state_file, "\n".join(lines) + "\n")
        ts = now_iso()
        append_events(feature_dir, [
            [("timestamp", ts), ("event", "artifact_created"),
             ("phase", phase), ("details", "\"%s criado\"" % filename)],
        ])
    print("ok=true")
    print("phase=%s" % phase)
    if added == "present":
        print("already_recorded=true")
    return 0


def cmd_abort(reason):
    resolved = resolve_active()
    if resolved is None:
        return 0
    slug, feature_dir, state_file = resolved
    text = read_text(state_file)
    phase = grep_value(text, "current_phase")
    lines = text.splitlines()
    set_top_key(lines, "status", "aborted")
    if phase in PHASES:
        set_phase_key(lines, phase, "status", "aborted")
    write_text(state_file, "\n".join(lines) + "\n")
    ts = now_iso()
    event = [("timestamp", ts), ("event", "feature_aborted"), ("phase", phase)]
    if reason:
        event.append(("details", "\"%s\"" % reason.replace('"', "'")))
    append_events(feature_dir, [event])
    os.remove(os.path.join(AFYA, "features", "active"))
    print("ok=true")
    return 0


USAGE = (
    "usage: feature.py new \"<name>\" | check | advance | gate <phase> | "
    "record-artifact <file> | abort [\"reason\"]"
)


def main(argv):
    if len(argv) < 1:
        print("ok=false")
        print("error=missing_subcommand")
        sys.stderr.write(USAGE + "\n")
        return 1
    cmd, args = argv[0], argv[1:]
    if cmd == "new" and len(args) == 1 and args[0].strip():
        return cmd_new(args[0].strip())
    if cmd == "check" and not args:
        return cmd_check()
    if cmd == "advance" and not args:
        return cmd_advance()
    if cmd == "gate" and len(args) == 1:
        return cmd_gate(args[0])
    if cmd == "record-artifact" and len(args) == 1:
        return cmd_record_artifact(os.path.basename(args[0]))
    if cmd == "abort" and len(args) <= 1:
        return cmd_abort(args[0] if args else "")
    print("ok=false")
    print("error=bad_arguments")
    sys.stderr.write(USAGE + "\n")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except OSError as exc:
        print("ok=false")
        sys.stderr.write("afyapowers-dev feature.py failed: %s\n" % exc)
        sys.exit(1)
