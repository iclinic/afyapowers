# /afyapowers:component — Develop a Figma Component

You are developing a standalone Figma component. This is **not** part of the 5-phase workflow — it is an independent command for implementing individual components from Figma.

Invoke the **component** skill to handle the entire process. The skill will:

1. Ask for the Figma component URL (if not already provided)
2. Run 8 sequential validation gates (URL parsing, MCP availability, node type, variant structure, Code Connect dedup, dependency detection, output location, Storybook detection)
3. Dispatch an implementer subagent to translate the Figma design into production code
4. Hard stop on any issue — no partial results, no workarounds

Pass along any Figma URL or component reference the user has already provided.
