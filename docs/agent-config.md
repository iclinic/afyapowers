# Agent Configuration Reference

Each agent has a JSON config file in `src/config/`. The sync script (`sync.sh`) reads these configs and generates agent-specific output in `dist/<agent>/`.

## Usage

```bash
# Sync all agents
./sync.sh

# Sync a specific agent
./sync.sh cursor

# Clean output before syncing
./sync.sh --clean

# Clean + specific agent
./sync.sh cursor --clean
```

---

## Config Schema

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `agent` | `string` | Agent identifier (e.g., `"cursor"`, `"claude"`, `"gemini"`) |
| `outputDir` | `string` | Output directory relative to repo root (e.g., `"dist/cursor"`) |
| `prefix` | `string` | Namespace prefix used in naming conventions |
| `commands` | `object` | Command file generation settings |
| `skills` | `object` | Skill directory generation settings |
| `agents` | `object` | Agent file generation settings |
| `templates` | `boolean` | Whether to copy `src/templates/` to output |
| `hooks` | `boolean` | Whether to copy `src/hooks/` to output (preserves execute permissions) |
| `pluginManifest` | `object \| null` | Plugin manifest copy settings, or `null` to skip |

---

### `commands`

Controls how command markdown files from `src/commands/` are processed.

| Field | Type | Description |
|-------|------|-------------|
| `filePrefix` | `string` | String prepended to each command filename. `""` keeps original name. |

Example:

```json
{
  "filePrefix": "afyapowers-"
}
```

Given `src/commands/abort.md`, this produces `dist/<agent>/commands/afyapowers-abort.md`.

---

### `skills`

Controls how skill directories from `src/skills/` are processed. Each skill directory is copied with its `SKILL.md` frontmatter optionally replaced via a frontmatter file. All other files in the skill directory (prompts, resources) are always copied as-is.

| Field | Type | Description |
|-------|------|-------------|
| `dirPrefix` | `string` | String prepended to each skill directory name. `""` keeps original name. |

---

### `agents`

Controls how agent markdown files from `src/agents/` are processed. Works identically to `commands`.

| Field | Type | Description |
|-------|------|-------------|
| `filePrefix` | `string` | String prepended to each agent filename. `""` keeps original name. |

---

### `pluginManifest`

Copies a plugin manifest directory or file into the output.

| Field | Type | Description |
|-------|------|-------------|
| `from` | `string` | Source path relative to repo root |
| `to` | `string` | Destination path relative to the agent's output directory |

```json
{
  "from": "src/manifests/cursor/.cursor-plugin",
  "to": ".cursor-plugin"
}
```

Set to `null` to skip manifest copying entirely:

```json
"pluginManifest": null
```

---

## Frontmatter Files

Frontmatter for each command, skill, or agent is configured via `.frontmatter.yaml` files. These files define per-distribution frontmatter that gets prepended to the output.

### Location

| Source type | Frontmatter file |
|-------------|------------------|
| Commands | `src/commands/<slug>.frontmatter.yaml` |
| Skills | `src/skills/<name>/frontmatter.yaml` |
| Agents | `src/agents/<slug>.frontmatter.yaml` |

### Format

Each `.frontmatter.yaml` file has top-level keys matching agent names from `src/config/`. The content under each key becomes the YAML frontmatter for that distribution's output.

```yaml
claude:
  name: afyapowers:design
  description: "Design phase skill"
cursor:
  name: afyapowers-design
  description: "Design phase skill"
```

This produces for **claude**:

```markdown
---
name: afyapowers:design
description: "Design phase skill"
---

# Design Phase
...
```

And for **cursor**:

```markdown
---
name: afyapowers-design
description: "Design phase skill"
---

# Design Phase
...
```

### Fallback behavior

If an agent has **no section** in the frontmatter file (or no frontmatter file exists), the source file is copied as-is, preserving any existing frontmatter from the source.

For example, if `gemini` is not listed in a frontmatter file, the gemini distribution gets the original source frontmatter unchanged.

### Complex frontmatter

Frontmatter files support nested YAML structures. Any valid YAML under an agent key will be output as frontmatter:

```yaml
cursor:
  name: afyapowers-figma-component
  description: Figma component skill
  metadata:
    mcp-server: figma
  allowed-tools:
    - Read
    - Bash
    - mcp__figma__get_metadata
```

---

## Full Examples

### Minimal config (clean copy, no transforms)

```json
{
  "agent": "gemini",
  "outputDir": "dist/gemini",
  "prefix": "afyapowers",
  "commands": {
    "filePrefix": ""
  },
  "skills": {
    "dirPrefix": ""
  },
  "agents": {
    "filePrefix": ""
  },
  "templates": true,
  "hooks": true,
  "pluginManifest": null
}
```

### Config with prefixes

```json
{
  "agent": "cursor",
  "outputDir": "dist/cursor",
  "prefix": "afyapowers",
  "commands": {
    "filePrefix": "afyapowers-"
  },
  "skills": {
    "dirPrefix": "afyapowers-"
  },
  "agents": {
    "filePrefix": "afyapowers-"
  },
  "templates": true,
  "hooks": true,
  "pluginManifest": {
    "from": "src/manifests/cursor/.cursor-plugin",
    "to": ".cursor-plugin"
  }
}
```

---

## Adding a New Agent

1. Create `src/config/<agent>.json` following the schema above
2. Add a `<agent>:` section to the relevant `.frontmatter.yaml` files for any commands/skills/agents that need custom frontmatter
3. Optionally add a manifest in `src/manifests/<agent>/`
4. Run `./sync.sh <agent>` to generate output
5. Output appears in `dist/<agent>/`

## Adding a New Command / Skill / Agent

1. Create the source file (`src/commands/<name>.md`, `src/skills/<name>/SKILL.md`, or `src/agents/<name>.md`)
2. Create a `.frontmatter.yaml` file alongside it with sections for each distribution that needs custom frontmatter
3. Run `./sync.sh` to regenerate all distributions
