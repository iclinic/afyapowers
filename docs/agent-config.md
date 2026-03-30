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
| `prefix` | `string` | Namespace prefix, available as `{{prefix}}` in templates |
| `commands` | `object` | Command file generation settings |
| `skills` | `object` | Skill directory generation settings |
| `templates` | `boolean` | Whether to copy `src/templates/` to output |
| `hooks` | `boolean` | Whether to copy `src/hooks/` to output (preserves execute permissions) |
| `pluginManifest` | `object \| null` | Plugin manifest copy settings, or `null` to skip |

---

### `commands`

Controls how command markdown files from `src/commands/` are processed.

| Field | Type | Description |
|-------|------|-------------|
| `filePrefix` | `string` | String prepended to each command filename. `""` keeps original name. |
| `frontmatter` | `object` | Key-value pairs to inject as YAML frontmatter. `{}` means no frontmatter is added. |

**`frontmatter` object**: Each key becomes a YAML field name, each value is a template string resolved at sync time.

Example:

```json
{
  "filePrefix": "afyapowers-",
  "frontmatter": {
    "name": "{{prefix}}:{{slug}}",
    "description": "{{heading_title}}"
  }
}
```

Given `src/commands/abort.md` starting with `# /afyapowers:abort — Abort Current Feature`, this produces `dist/<agent>/commands/afyapowers-abort.md`:

```markdown
---
name: afyapowers:abort
description: Abort Current Feature
---
# /afyapowers:abort — Abort Current Feature
...
```

To copy commands as-is (no prefix, no frontmatter):

```json
{
  "filePrefix": "",
  "frontmatter": {}
}
```

---

### `skills`

Controls how skill directories from `src/skills/` are processed. Each skill directory is copied with its `SKILL.md` frontmatter optionally transformed. All other files in the skill directory (prompts, resources) are always copied as-is.

| Field | Type | Description |
|-------|------|-------------|
| `dirPrefix` | `string` | String prepended to each skill directory name. `""` keeps original name. |
| `frontmatter` | `object` | Frontmatter transformation settings |

#### `skills.frontmatter`

| Field | Type | Description |
|-------|------|-------------|
| `transform` | `string` | Transform mode: `"keep"`, `"merge"`, or `"replace"` |
| `fields` | `object` | Key-value pairs for frontmatter fields (used by `merge` and `replace` modes) |

**Transform modes:**

#### `"keep"` — No changes

Copies `SKILL.md` as-is. The `fields` object is ignored.

```json
{
  "transform": "keep",
  "fields": {}
}
```

#### `"merge"` — Overlay fields onto existing frontmatter

Replaces only the specified top-level fields in the existing frontmatter. All other fields (including nested/multi-line ones like `metadata` or `allowed-tools`) are preserved.

```json
{
  "transform": "merge",
  "fields": {
    "name": "{{prefix}}-{{name}}"
  }
}
```

Given a source `SKILL.md` with:
```yaml
---
name: figma-component
description: Develop Figma components...
metadata:
  mcp-server: figma
allowed-tools:
  - Read
  - Bash
---
```

The output becomes:
```yaml
---
name: afyapowers-figma-component
description: Develop Figma components...
metadata:
  mcp-server: figma
allowed-tools:
  - Read
  - Bash
---
```

Only `name` is overwritten; everything else stays.

#### `"replace"` — Discard existing frontmatter

Removes the original frontmatter entirely and writes only the fields from config.

```json
{
  "transform": "replace",
  "fields": {
    "name": "{{prefix}}-{{name}}",
    "description": "{{description}}"
  }
}
```

The same source would become:
```yaml
---
name: afyapowers-figma-component
description: Develop Figma components...
---
```

All other fields (`metadata`, `allowed-tools`) are dropped.

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

## Template Variables

Available in `commands.frontmatter` values and `skills.frontmatter.fields` values.

### In command context

| Variable | Resolves to | Example |
|----------|-------------|---------|
| `{{prefix}}` | The top-level `prefix` field | `afyapowers` |
| `{{slug}}` | Command filename without `.md` | `abort` |
| `{{filename}}` | Full original filename | `abort.md` |
| `{{heading_title}}` | Text after the em-dash in the first `#` heading | `Abort Current Feature` |

### In skill context

| Variable | Resolves to | Example |
|----------|-------------|---------|
| `{{prefix}}` | The top-level `prefix` field | `afyapowers` |
| `{{name}}` | `name` field from the source `SKILL.md` frontmatter | `design` |
| `{{description}}` | `description` field from the source `SKILL.md` frontmatter | `You MUST use this before...` |

---

## Full Examples

### Minimal config (clean copy, no transforms)

```json
{
  "agent": "vanilla",
  "outputDir": "dist/vanilla",
  "prefix": "afyapowers",
  "commands": {
    "filePrefix": "",
    "frontmatter": {}
  },
  "skills": {
    "dirPrefix": "",
    "frontmatter": {
      "transform": "keep",
      "fields": {}
    }
  },
  "templates": true,
  "hooks": true,
  "pluginManifest": null
}
```

### Full transform config

```json
{
  "agent": "cursor",
  "outputDir": "dist/cursor",
  "prefix": "afyapowers",
  "commands": {
    "filePrefix": "afyapowers-",
    "frontmatter": {
      "name": "{{prefix}}:{{slug}}",
      "description": "{{heading_title}}"
    }
  },
  "skills": {
    "dirPrefix": "afyapowers-",
    "frontmatter": {
      "transform": "merge",
      "fields": {
        "name": "{{prefix}}-{{name}}"
      }
    }
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
2. Optionally add a manifest in `src/manifests/<agent>/`
3. Run `./sync.sh <agent>` to generate output
4. Output appears in `dist/<agent>/`
