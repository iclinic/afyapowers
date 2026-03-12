---
name: design
description: "Use when the current afyapowers phase is design — produces a tech spec from brainstorm output"
---

# Design Phase

Produce a detailed technical specification from the brainstorm artifact.

## Phase Gate

1. Read `.afyapowers/active` to get the active feature
2. Read `.afyapowers/<feature>/state.yaml` — confirm `current_phase` is `design`
3. If not in design phase, tell the user the current phase and stop

## Process

### Step 1: Review Brainstorm Output

Read `.afyapowers/<feature>/artifacts/brainstorm.md` to understand:
- Problem statement and requirements
- Constraints
- Chosen approach

### Step 2: Produce Tech Spec

Read the template from `templates/tech-spec.md`. Work through each section with the user:

1. **Overview** — Summarize the feature in 1-2 sentences
2. **Architecture** — Define components and how they interact. Ask the user clarifying questions if the brainstorm doesn't fully specify architecture.
3. **Data Flow** — How data moves through the system
4. **API / Interface Changes** — New or modified interfaces
5. **Error Handling** — Failure modes and recovery strategies
6. **Testing Strategy** — What to test and how (unit, integration, e2e)
7. **Dependencies** — External dependencies or prerequisites

Present each section for validation. Scale detail to complexity — a few sentences if straightforward, more detail if nuanced.

### Step 3: Spec Review

After the user approves the tech spec:

1. Save it to `.afyapowers/<feature>/artifacts/tech-spec.md`
2. Dispatch a spec-document-reviewer subagent using `skills/brainstorming/spec-document-reviewer-prompt.md`
3. If issues found: fix and re-dispatch (max 5 iterations)
4. If approved: proceed to user review

### Step 4: User Review

Ask the user to review the written tech spec:
> "Tech spec saved to `.afyapowers/<feature>/artifacts/tech-spec.md`. Please review and let me know if you'd like any changes."

Wait for approval.

### Step 5: Complete

Update `state.yaml` to add `tech-spec.md` to the design phase's artifacts list.
Append `artifact_created` event to `history.yaml`.

Tell the user: "Design phase complete. Run `/afyapowers:next` to proceed to **plan**."

## Key Principles

- Build on the brainstorm output — don't re-ask questions already answered
- Focus on technical decisions, not requirements (those are in the brainstorm)
- Be specific about interfaces and data flow
- YAGNI — only design what's needed for the chosen approach
