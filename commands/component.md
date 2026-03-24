# /afyapowers:component — Develop a Figma Component

You are developing a standalone Figma component. This is **not** part of the 5-phase workflow — it is an independent command for implementing individual components from Figma.

Invoke the **component** skill to handle the entire process. The skill will:

1. Ask for the Figma component URL (if not already provided)
2. Run a 3-phase pre-flight check (parse & validate, dependencies & location, present & confirm)
3. After user confirmation, dispatch an implementer subagent to translate the Figma design into production code
4. Hard stop on any issue — no partial results, no workarounds

Pass along any Figma URL or component reference the user has already provided.
