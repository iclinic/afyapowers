#!/usr/bin/env bash
set -euo pipefail

D=".afyapowers"
AF="$D/features/active"

if [ ! -f "$AF" ]; then
  printf '{"error":"no_active_feature"}\n'
  exit 0
fi

SLUG=$(tr -d '[:space:]' < "$AF")
F="$D/features/$SLUG"
S="$F/state.yaml"

if [ ! -f "$S" ]; then
  printf '{"error":"no_state_file"}\n'
  exit 0
fi

PHASE=$(grep "^current_phase:" "$S" | sed 's/^current_phase: *//')
NAME=$(grep "^feature:" "$S" | sed 's/^feature: *//')
STATUS=$(grep "^status:" "$S" | head -1 | sed 's/^status: *//')
A="$F/artifacts"

VALID=false
ERR=""
TP=""

case "$PHASE" in
  design)
    [ -f "$A/design.md" ] && VALID=true || ERR="Design artifact missing. Complete the design phase first." ;;
  plan)
    [ -f "$A/plan.md" ] && VALID=true || ERR="Plan artifact missing. Complete the plan phase first." ;;
  implement)
    TOT=$(grep -c '^\- \[' "$A/plan.md" 2>/dev/null || echo 0)
    DONE=$(grep -c '^\- \[x\]' "$A/plan.md" 2>/dev/null || echo 0)
    REM=$((TOT - DONE))
    TP="$DONE/$TOT"
    [ "$REM" -eq 0 ] && VALID=true || ERR="$REM of $TOT tasks still unchecked." ;;
  review)
    if [ -f "$A/review.md" ] && grep -A5 '## Verdict' "$A/review.md" 2>/dev/null | grep -q 'Approved'; then
      VALID=true
    elif [ ! -f "$A/review.md" ]; then
      ERR="Review artifact missing."
    else
      ERR="Review verdict is not Approved. Check review.md for findings."
    fi ;;
  complete)
    [ -f "$A/completion.md" ] && VALID=true || ERR="Completion artifact missing." ;;
  *)
    ERR="Unknown phase: $PHASE" ;;
esac

case "$PHASE" in
  design) NXT=plan ;; plan) NXT=implement ;; implement) NXT=review ;;
  review) NXT=complete ;; complete) NXT=finalize ;; *) NXT="" ;;
esac

printf '{"slug":"%s","feature":"%s","current_phase":"%s","status":"%s","valid":%s,"next_phase":"%s","error":%s,"task_progress":"%s"}\n' \
  "$SLUG" "$NAME" "$PHASE" "$STATUS" "$VALID" "$NXT" \
  "$([ -n "$ERR" ] && printf '"%s"' "$ERR" || echo null)" "$TP"
