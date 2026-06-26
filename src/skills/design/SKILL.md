---
claude:
  name: afyapowers:design
  description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and produces a full technical design."
  model: claude-opus-4-6
  effort: high
cursor:
  name: afyapowers-design
  description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and produces a full technical design."
  model: claude-4-6-opus
github-copilot:
  name: design
  description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements, and produces a full technical design."
---

# Design Phase

Help turn ideas into fully formed technical designs through natural collaborative dialogue.

Start by gathering the **requirements** — JIRA, Figma, and clarifying questions — *before* looking at any existing code. Only once the requirement is locked do you explore the codebase. Then present the full design — from requirements through architecture — and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

<REQUIREMENTS-BEFORE-CODE>
Do NOT read project files, docs, or git history before requirements are gathered (JIRA + Figma + clarifying questions). Exploring existing code first anchors the design on what already exists and biases it toward reusing whatever you happen to find — the exact failure mode where a design reuses a component that doesn't match the actual requirement. Gather the requirement first; explore the codebase only afterward, and evaluate any reuse candidate **against** the requirement, never as the starting point. You may rely on what the user's request, JIRA, and Figma tell you to frame questions — but no codebase reads until the dedicated exploration step.
</REQUIREMENTS-BEFORE-CODE>

## Phase Gate

1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `design`
3. If not in design phase, tell the user the current phase and stop

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST complete these items in order. **Requirements first (1-3), code exploration only after (4).**

1. **JIRA discovery (offer-based)** — offer the user the chance to provide a JIRA issue key; if provided, fetch and summarize the issue (see below)
2. **Figma discovery (trigger-based)** — check user request against trigger keywords (see below); if match, ask about Figma and run discovery
3. **Ask clarifying questions** — if JIRA and/or Figma data is available, use confirmation-style questions (see below); otherwise, standard one-at-a-time clarifying questions
4. **Explore the codebase** — ONLY now, with the requirement locked. Read files, docs, recent commits. Identify reuse candidates and evaluate each against the requirement/Figma — never let existing code become the starting point (see REQUIREMENTS-BEFORE-CODE). Apply the **Component Reuse Gate**: ask the user before reusing any candidate unless it is an exact match (name + layout + behavior)
5. **Propose 2-3 approaches** — with trade-offs and your recommendation
6. **Present design** — in sections scaled to their complexity, get user approval after each section
7. **Write design doc** — save to `.afyapowers/features/<feature>/artifacts/design.md`
8. **Design review loop** — dispatch @"design-reviewer (agent)"; fix issues and re-dispatch until approved (max 5 iterations, then surface to human)
9. **User reviews written spec** — ask user to review the spec file before proceeding

## Process Flow

```dot
digraph design {
    "Offer JIRA issue key" [shape=box];
    "JIRA issue provided?" [shape=diamond];
    "Fetch JIRA issue" [shape=box];
    "Trigger keywords match?" [shape=diamond];
    "Ask Figma question" [shape=box];
    "Figma discovery" [shape=box];
    "Confirmation-style questions" [shape=box];
    "Standard clarifying questions" [shape=box];
    "Explore codebase (requirement locked)" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write design doc" [shape=box];
    "Design review loop" [shape=box];
    "Design review passed?" [shape=diamond];
    "User reviews design?" [shape=diamond];
    "Suggest /afyapowers:next" [shape=doublecircle];

    "Offer JIRA issue key" -> "JIRA issue provided?";
    "JIRA issue provided?" -> "Fetch JIRA issue" [label="yes"];
    "JIRA issue provided?" -> "Trigger keywords match?" [label="no"];
    "Fetch JIRA issue" -> "Trigger keywords match?";
    "Trigger keywords match?" -> "Ask Figma question" [label="yes"];
    "Trigger keywords match?" -> "Standard clarifying questions" [label="no"];
    "Ask Figma question" -> "Figma discovery" [label="user provides URLs"];
    "Ask Figma question" -> "Standard clarifying questions" [label="no Figma designs"];
    "Figma discovery" -> "Confirmation-style questions";
    "Confirmation-style questions" -> "Explore codebase (requirement locked)";
    "Standard clarifying questions" -> "Explore codebase (requirement locked)";
    "Explore codebase (requirement locked)" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write design doc" [label="yes"];
    "Write design doc" -> "Design review loop";
    "Design review loop" -> "Design review passed?";
    "Design review passed?" -> "Design review loop" [label="issues found,\nfix and re-dispatch"];
    "Design review passed?" -> "User reviews design?" [label="approved"];
    "User reviews design?" -> "Write design doc" [label="changes requested"];
    "User reviews design?" -> "Suggest /afyapowers:next" [label="approved"];
}
```

**The terminal state is suggesting `/afyapowers:next`.** Do NOT invoke any implementation skill or advance phases. The `/afyapowers:next` command handles phase transitions.

## The Process

**Understanding the idea:**

- Do NOT read project files, docs, or git history yet (see REQUIREMENTS-BEFORE-CODE). Work from the user's request, JIRA, and Figma until the dedicated codebase-exploration step.
- Before asking detailed questions, assess scope from the request/JIRA: if it describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then design the first sub-project through the normal flow. Each sub-project gets its own design → plan → implementation cycle.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**JIRA discovery (offer-based):**

This is the FIRST step — before any codebase exploration. Offer the user:

> "Is there a JIRA issue associated with this feature? If so, share the issue key (e.g., PROJ-123)."

If the user provides a JIRA issue key:

1. **Resolve the Atlassian cloud ID:**
   - Call `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` (no parameters)
   - If exactly one site is returned, use its `id` as the `cloudId`
   - If multiple sites are returned, present them as a multiple-choice question and let the user pick

2. **Fetch the issue:**
   ```
   mcp__claude_ai_Atlassian__getJiraIssue(
     cloudId: "<resolved_cloud_id>",
     issueIdOrKey: "<user_provided_key>",
     responseContentFormat: "markdown"
   )
   ```

3. **Build the JIRA context summary** from the response:
   - **Summary:** issue summary field
   - **Issue Type:** story, bug, task, epic, etc.
   - **Description:** full description in markdown
   - **Acceptance Criteria:** extracted from description or custom fields if present
   - **Linked Issues:** dependencies, blockers, related issues
   - **Labels / Components:** for categorization context

   Present this summary to the user for confirmation before proceeding.

4. **Proceed to Figma discovery** (the JIRA summary and description text is now part of the context when evaluating Figma trigger keywords)

If no JIRA issue is provided, proceed directly to Figma discovery.

**If the Atlassian MCP server is unavailable:** Warn the user and **stop the JIRA discovery flow**. Do not attempt to proceed without it — the user asked for JIRA context, so a silent fallback would undermine the purpose. Suggest the user check their MCP server connection and retry.

**Figma discovery (trigger-based):**

After JIRA discovery (and still before any codebase exploration), check the user's request for these trigger keywords (case-insensitive, word-level matching):

> page, landing page, screen, view, layout, header, footer, navbar, sidebar, UI component, form, modal, dialog, card, hero, section, banner, responsive, breakpoint, mobile, desktop, dashboard, panel, widget

If any keyword matches, ask the user:

> "Does this feature have Figma designs? If so, please share the Figma URL(s)."

If a keyword matches but the request is clearly not UI work (e.g., "write unit tests for the landing page API endpoint"), use judgment — when in doubt, ask.

If no keywords match, skip Figma discovery and proceed to clarifying questions.

If the user provides Figma URL(s), invoke `{{skill:reading-figma-designs}}`. It parses each URL,
builds the shallow Node Map via a single `get_metadata` call, and extracts **all** Dev Mode data
annotations via a read-only `use_figma` call. It returns the complete `## Figma Resources` section
— file info, breakpoints, Node Map, and a `### Design Annotations` subsection — ready to drop into
the design doc (template: `templates/design.md`).

Annotations carry semantic intent: business rules, responsive rules, interactive-state behavior,
animations, accessibility rules, content rules, development-specific instructions, spacing, and
more. Treat them as real requirements — business rules flow into the design's requirements, and
the rest into the relevant design sections. Carry them into the clarifying questions below so the
user can confirm them before the design is written.

No `get_screenshot` or `get_design_context` calls during the design phase — these are deferred to
implementation, where the subagent already calls them per-task.

**If no Figma designs:** Proceed normally. Do not include the Figma Resources section in the design doc.

**Design tokens are NOT extracted during design phase.** They are deferred to implementation time — the implementer subagent will fetch them via `get_variable_defs` when needed.

**Component Reuse Gate (always — Figma or not):**

**NEVER adopt an existing codebase or design-system (DS) component into the design without the user's explicit approval — UNLESS it is the exact same component the requirement needs.** Reuse is not a default; it is a gated decision. Every time you find a component you *might* reuse, you must stop and ask the user first.

The **only** case where you may reuse without asking is an **exact match on all three axes**:

- **Name** — the component's name corresponds to the component the requirement/Figma calls for. A name mismatch (e.g. reusing `DropdownPicker` for a Figma "Specialty Chip") is never an exact match.
- **Layout / visuals** — colors, shape, sizing, and states are identical to what the requirement/Figma shows.
- **Behavior / interaction model** — runtime behavior is identical: popover vs drawer, inline vs modal, anchored vs full-screen, search vs no-search. This is the axis most often missed — a DS component can look adjustable but behave fundamentally differently.

Exact match on all three → reuse silently. **Anything else — a different name, any visual difference, any behavior difference, a "close enough" / "good enough" near-match, or any uncertainty — you MUST ask the user before adopting it.** Present the candidate, name every difference, and reuse only on explicit approval (e.g. "Figma shows an inline chip + anchored popover; the DS `DropdownPicker` renders a bottom drawer with a search field — reuse it anyway, or build a custom chip to match Figma?"). When in doubt, ask.

Record every reuse in the `## Component Reuse Decisions` section of the design doc (template: `templates/design.md`): mark it either **exact match** (no approval needed) or the user's explicit decision. *"If it's different, it's wrong"* unless the user has explicitly accepted the divergence.

**Clarifying questions (JIRA and/or Figma-informed):**

When JIRA data and/or Figma data was gathered in previous steps, replace open-ended clarifying questions with confirmation-style:

- If JIRA data is available: present the ticket's requirements, acceptance criteria, and scope, and ask the user to confirm, correct, or extend
- If Figma data is available: present what the design shows (structure, breakpoints, component hierarchy) and ask the user to confirm or correct. If the design carries data annotations, surface them explicitly — they encode business rules, behavior, animations, accessibility, and development instructions the user should validate (e.g. "The Figma annotations specify: CTA disabled until the form is valid; cards collapse to a single column < 768px; error summary receives focus on submit. Confirm these?")
- If both are available: confirm JIRA requirements first, then Figma structural details
- Then only ask about things not covered by either source: technical constraints, architecture preferences, performance requirements, edge cases

Examples:
- **Open-ended (without JIRA/Figma):** "What problem are we solving?"
- **With JIRA:** "The JIRA ticket PROJ-123 describes: '[summary]'. The acceptance criteria include [X, Y, Z]. Does this capture the full scope, or are there additions?"
- **With Figma:** "The Figma design shows a hero section, a 3-column feature grid, and a CTA footer across 3 breakpoints (mobile/tablet/desktop). Does this match what you want, or do you need changes?"
- **With JIRA + Figma:** "JIRA describes [requirements]. The Figma design shows [structure]. Do these align with what you want to build?"

When neither JIRA nor Figma data is available, use the standard approach: ask questions one at a time to understand purpose, constraints, and success criteria.

**Explore the codebase (only after the requirement is locked):**

Now — and only now — read the project: files, docs, recent commits, existing patterns and components. Doing this *after* requirements keeps the requirement, not the existing code, as the anchor (see REQUIREMENTS-BEFORE-CODE).

- Explore the current structure and conventions so the design fits the project.
- Identify reuse candidates (existing components, utilities, patterns) — but treat each as a *candidate measured against the requirement*, not as the thing the design must bend toward. A candidate that doesn't match the requirement/Figma is not a fit; prefer building to the requirement over retrofitting a near-match.
- Run the **Component Reuse Gate** above on every candidate you would reuse: unless it is an exact match (name + layout + behavior), ask the user before adopting it. Never settle on a reuse the user hasn't approved.
- Where existing code has problems that affect the work (a file grown too large, tangled responsibilities), note targeted improvements — but don't propose unrelated refactoring.

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the full design
- Start with requirements and constraints, then move into architecture and technical details
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover all sections from the design template: problem statement, requirements, constraints, chosen approach, architecture, data flow, interfaces, error handling, testing strategy, dependencies
- If JIRA discovery was performed, include the `## JIRA Context` section with issue key, summary, acceptance criteria, and linked issues
- If Figma discovery was performed, include the `## Figma Resources` section with file info, breakpoints, node map, and the `### Design Annotations` list. Reflect the annotations in the relevant design sections too — business rules in Requirements, the rest wherever they fit (Constraints, Architecture, Error Handling, Testing Strategy) — not just the annotations list.
- If the design reuses any existing codebase/DS component, include the `## Component Reuse Decisions` section recording each reuse, its name/layout/behavior parity verdict, and whether it was an exact match or carries the user's explicit approval (per the Component Reuse Gate above).
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## Required Sub-Skills

**REQUIRED:** Dispatch @"design-reviewer (agent)" after writing the design artifact.

- Announce: "Using design-reviewer to validate the design."
- Dispatch @"design-reviewer (agent)":
  - Provide the design document content (the file just written to `.afyapowers/features/<feature>/artifacts/design.md`)
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: resume the parent flow (user review gate)

## After the Design

**Documentation:**

- Write the validated design to `.afyapowers/features/<feature>/artifacts/design.md`
  - Use the template from `templates/design.md`
- Commit the design document to git

**Design Review Loop:**
After writing the design document:

1. Dispatch @"design-reviewer (agent)":
   - Provide the design document file path or content
2. If Issues Found: fix, re-dispatch, repeat until Approved
3. If loop exceeds 5 iterations, surface to human for guidance

**User Review Gate:**
After the design review loop passes, ask the user to review the written design before proceeding:

> "Design written to `.afyapowers/features/<feature>/artifacts/design.md`. Please review it and let me know if you want to make any changes."

Wait for the user's response. If they request changes, make them and re-run the design review loop. Only proceed once the user approves.

**Completion:**

- Update `state.yaml` to add `design.md` to the design phase's artifacts list
- Append `artifact_created` event to `history.yaml`
- Tell the user: "Design phase complete. Run `/afyapowers:next` to proceed to **plan**."

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Never reuse a component without asking** - The only silent reuse is an exact match (name + layout + behavior). Any near-match, name/visual/behavior difference, or uncertainty → ask the user and reuse only on explicit approval
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense
