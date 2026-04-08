#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$REPO_ROOT/src"
CONFIG_DIR="$SRC_DIR/config"

# --- JSON helpers ---

json_get() {
  local file="$1" path="$2"
  if command -v jq &>/dev/null; then
    jq -r "$path" "$file"
  else
    file="$file" path="$path" python3 -c "
import os, json, functools
d = json.load(open(os.environ['file']))
keys = os.environ['path'].lstrip('.').split('.')
v = functools.reduce(lambda o, k: o[k] if isinstance(o, dict) else None, keys, d)
print(v if v is not None else '')
"
  fi
}

json_is_null() {
  local file="$1" path="$2"
  local val
  val=$(json_get "$file" "$path")
  [[ "$val" == "null" || -z "$val" ]]
}

json_is_true() {
  local file="$1" path="$2"
  local val
  val=$(json_get "$file" "$path")
  [[ "$val" == "true" ]]
}

# --- YAML frontmatter helpers ---

# Extract body (everything after frontmatter) from a file
extract_body() {
  local file="$1"
  local in_frontmatter=false
  local past_frontmatter=false
  local line_num=0
  while IFS= read -r line; do
    line_num=$((line_num + 1))
    if $past_frontmatter; then
      echo "$line"
      continue
    fi
    if [[ "$line" == "---" ]]; then
      if $in_frontmatter; then
        past_frontmatter=true
        continue
      elif [[ $line_num -eq 1 ]]; then
        in_frontmatter=true
        continue
      fi
    fi
    if ! $in_frontmatter; then
      # No frontmatter in file, return everything
      echo "$line"
      past_frontmatter=true
    fi
  done < "$file"
}

# Extract an agent's section from a .frontmatter.yaml file and output as a --- delimited block.
# Returns 0 (success) if the agent section exists, 1 otherwise.
# The YAML files have a simple structure: top-level keys are agent names,
# and their contents (indented lines) become the frontmatter.
# Usage: yaml_get_agent_frontmatter "file.frontmatter.yaml" "cursor"
yaml_get_agent_frontmatter() {
  local yaml_file="$1" agent_name="$2"
  local in_section=false
  local found=false
  local content=""

  while IFS= read -r line; do
    # Top-level key (no leading whitespace, ends with colon)
    if [[ "$line" =~ ^[a-zA-Z_][a-zA-Z0-9_-]*:$ ]]; then
      if $in_section; then
        # We were in our section and hit another top-level key — stop
        break
      fi
      local key="${line%:}"
      if [[ "$key" == "$agent_name" ]]; then
        in_section=true
        found=true
      fi
      continue
    fi

    if $in_section; then
      # Remove exactly 2 spaces of indentation (agent section content)
      if [[ "$line" =~ ^\ \ (.*) ]]; then
        content+="${BASH_REMATCH[1]}"$'\n'
      elif [[ -z "$line" ]]; then
        content+=$'\n'
      fi
    fi
  done < "$yaml_file"

  if $found && [[ -n "$content" ]]; then
    echo "---"
    # Remove trailing blank lines
    printf '%s' "$content" | awk 'NF{p=1} p' | awk '{lines[NR]=$0} END{for(i=NR;i>=1;i--) if(lines[i]!="") {last=i; break} for(i=1;i<=last;i++) print lines[i]}'
    echo "---"
    return 0
  fi

  return 1
}

# --- Process single-file items (commands or agents) ---

process_single_files() {
  local src_dir="$1" output_subdir="$2" file_prefix="$3" agent_name="$4" output_dir="$5"

  if [[ ! -d "$src_dir" ]]; then
    echo "  $(basename "$output_subdir"): 0 files (no source directory)"
    return
  fi

  mkdir -p "$output_dir/$output_subdir"
  local count=0

  for src_file in "$src_dir/"*.md; do
    [[ -f "$src_file" ]] || continue
    local filename
    filename=$(basename "$src_file")
    local slug="${filename%.md}"
    local out_file="$output_dir/$output_subdir/${file_prefix}${filename}"

    # Look for .frontmatter.yaml file
    local fm_yaml="$src_dir/${slug}.frontmatter.yaml"

    if [[ -f "$fm_yaml" ]]; then
      local fm_block
      if fm_block=$(yaml_get_agent_frontmatter "$fm_yaml" "$agent_name"); then
        # Agent section found: use it as frontmatter + source body
        local body
        body=$(extract_body "$src_file")
        {
          echo "$fm_block"
          echo "$body"
        } > "$out_file"
      else
        # No section for this agent: copy source as-is
        cp "$src_file" "$out_file"
      fi
    else
      # No frontmatter yaml: copy source as-is
      cp "$src_file" "$out_file"
    fi

    count=$((count + 1))
  done

  # Remove stale files from output directory
  local removed=0
  for out_file in "$output_dir/$output_subdir/"*.md; do
    [[ -f "$out_file" ]] || continue
    local out_filename
    out_filename=$(basename "$out_file")
    # Strip file prefix to get the original slug
    local original_name="${out_filename#"$file_prefix"}"
    if [[ ! -f "$src_dir/$original_name" ]]; then
      rm "$out_file"
      removed=$((removed + 1))
    fi
  done

  local msg="  $(basename "$output_subdir"): $count files"
  [[ $removed -gt 0 ]] && msg+=" ($removed stale removed)"
  echo "$msg"
}

# --- Process commands for an agent ---

process_commands() {
  local config_file="$1" output_dir="$2"

  local file_prefix
  file_prefix=$(json_get "$config_file" '.commands.filePrefix')
  [[ "$file_prefix" == "null" ]] && file_prefix=""

  local agent_name
  agent_name=$(json_get "$config_file" '.agent')

  process_single_files "$SRC_DIR/commands" "commands" "$file_prefix" "$agent_name" "$output_dir"
}

# --- Process skills for an agent ---

process_skills() {
  local config_file="$1" output_dir="$2"

  local dir_prefix
  dir_prefix=$(json_get "$config_file" '.skills.dirPrefix')
  [[ "$dir_prefix" == "null" ]] && dir_prefix=""

  local agent_name
  agent_name=$(json_get "$config_file" '.agent')

  mkdir -p "$output_dir/skills"
  local count=0

  for src_skill_dir in "$SRC_DIR/skills/"*/; do
    [[ -d "$src_skill_dir" ]] || continue
    local dirname
    dirname=$(basename "$src_skill_dir")
    local out_skill_dir="$output_dir/skills/${dir_prefix}${dirname}"
    mkdir -p "$out_skill_dir"

    # Process SKILL.md
    local skill_file="$src_skill_dir/SKILL.md"
    if [[ -f "$skill_file" ]]; then
      local fm_yaml="$src_skill_dir/frontmatter.yaml"

      if [[ -f "$fm_yaml" ]]; then
        local fm_block
        if fm_block=$(yaml_get_agent_frontmatter "$fm_yaml" "$agent_name"); then
          # Agent section found: use it as frontmatter + skill body
          local body
          body=$(extract_body "$skill_file")
          {
            echo "$fm_block"
            echo "$body"
          } > "$out_skill_dir/SKILL.md"
        else
          # No section for this agent: copy as-is
          cp "$skill_file" "$out_skill_dir/SKILL.md"
        fi
      else
        # No frontmatter yaml: copy as-is
        cp "$skill_file" "$out_skill_dir/SKILL.md"
      fi
    fi

    # Copy all other files in skill directory (skip SKILL.md and frontmatter files)
    for src_file in "$src_skill_dir"*; do
      local fname
      fname=$(basename "$src_file")
      [[ "$fname" == "SKILL.md" ]] && continue
      [[ "$fname" == "frontmatter.yaml" ]] && continue
      if [[ -d "$src_file" ]]; then
        cp -R "$src_file" "$out_skill_dir/$fname"
      else
        cp "$src_file" "$out_skill_dir/$fname"
      fi
    done

    # Remove stale files within this skill directory
    for out_file in "$out_skill_dir/"*; do
      [[ -e "$out_file" ]] || continue
      local out_fname
      out_fname=$(basename "$out_file")
      # Check if this file exists in the source skill dir (frontmatter.yaml is never copied)
      if [[ ! -e "$src_skill_dir/$out_fname" ]] || [[ "$out_fname" == "frontmatter.yaml" ]]; then
        rm -rf "$out_file"
      fi
    done

    count=$((count + 1))
  done

  # Remove stale skill directories from output
  local removed=0
  for out_skill_dir in "$output_dir/skills/"*/; do
    [[ -d "$out_skill_dir" ]] || continue
    local out_dirname
    out_dirname=$(basename "$out_skill_dir")
    # Strip dir prefix to get the original dirname
    local original_name="${out_dirname#"$dir_prefix"}"
    if [[ ! -d "$SRC_DIR/skills/$original_name" ]]; then
      rm -rf "$out_skill_dir"
      removed=$((removed + 1))
    fi
  done

  local msg="  Skills: $count directories"
  [[ $removed -gt 0 ]] && msg+=" ($removed stale removed)"
  echo "$msg"
}

# --- Process agents ---

process_agents() {
  local config_file="$1" output_dir="$2"

  local file_prefix
  file_prefix=$(json_get "$config_file" '.agents.filePrefix')
  [[ "$file_prefix" == "null" ]] && file_prefix=""

  local agent_name
  agent_name=$(json_get "$config_file" '.agent')

  process_single_files "$SRC_DIR/agents" "agents" "$file_prefix" "$agent_name" "$output_dir"
}

# --- Process templates ---

process_templates() {
  local config_file="$1" output_dir="$2"

  if json_is_true "$config_file" '.templates'; then
    if [[ -d "$SRC_DIR/templates" ]]; then
      rm -rf "$output_dir/templates"
      cp -R "$SRC_DIR/templates" "$output_dir/templates"
      local count
      count=$(find "$output_dir/templates" -type f | wc -l | tr -d ' ')
      echo "  Templates: $count files"
    fi
  else
    echo "  Templates: skipped"
  fi
}

# --- Process hooks ---

process_hooks() {
  local config_file="$1" output_dir="$2"

  if json_is_true "$config_file" '.hooks'; then
    if [[ -d "$SRC_DIR/hooks" ]]; then
      rm -rf "$output_dir/hooks"
      cp -R "$SRC_DIR/hooks" "$output_dir/hooks"
      # Preserve execute permissions
      for f in "$SRC_DIR/hooks/"*; do
        if [[ -x "$f" ]]; then
          chmod +x "$output_dir/hooks/$(basename "$f")"
        fi
      done
      local count
      count=$(find "$output_dir/hooks" -type f | wc -l | tr -d ' ')
      echo "  Hooks: $count files"
    fi
  else
    echo "  Hooks: skipped"
  fi
}

# --- Process plugin manifest ---

process_manifest() {
  local config_file="$1" output_dir="$2"

  if json_is_null "$config_file" '.pluginManifest'; then
    echo "  Manifest: skipped"
    return
  fi

  local from to
  from=$(json_get "$config_file" '.pluginManifest.from')
  to=$(json_get "$config_file" '.pluginManifest.to')

  if [[ -e "$REPO_ROOT/$from" ]]; then
    mkdir -p "$(dirname "$output_dir/$to")"
    if [[ -d "$REPO_ROOT/$from" ]]; then
      mkdir -p "$output_dir/$to"
      cp -R "$REPO_ROOT/$from/"* "$output_dir/$to/"
    else
      cp "$REPO_ROOT/$from" "$output_dir/$to"
    fi
    echo "  Manifest: copied from $from"
  else
    echo "  Manifest: source $from not found, skipped"
  fi
}

# --- Main ---

main() {
  local agents=()

  if [[ $# -gt 0 ]]; then
    # Process specific agents
    for arg in "$@"; do
      if [[ "$arg" == "--clean" ]]; then
        continue
      fi
      agents+=("$arg")
    done
  else
    # Process all agents
    for config_file in "$CONFIG_DIR"/*.json; do
      [[ -f "$config_file" ]] || continue
      local agent
      agent=$(basename "$config_file" .json)
      agents+=("$agent")
    done
  fi

  local do_clean=false
  for arg in "$@"; do
    [[ "$arg" == "--clean" ]] && do_clean=true
  done

  # If no agents specified (only --clean or no args), process all
  if [[ ${#agents[@]} -eq 0 ]]; then
    for config_file in "$CONFIG_DIR"/*.json; do
      [[ -f "$config_file" ]] || continue
      local agent
      agent=$(basename "$config_file" .json)
      agents+=("$agent")
    done
  fi

  echo "=== afyapowers sync ==="
  echo ""

  for agent in "${agents[@]}"; do
    local config_file="$CONFIG_DIR/${agent}.json"
    if [[ ! -f "$config_file" ]]; then
      echo "ERROR: Config not found: $config_file"
      continue
    fi

    local output_dir
    output_dir=$(json_get "$config_file" '.outputDir')
    output_dir="$REPO_ROOT/$output_dir"

    echo "[$agent] → $output_dir"

    # Clean output dir if requested
    if $do_clean && [[ -d "$output_dir" ]]; then
      # Preserve .git if it exists
      if [[ -d "$output_dir/.git" ]]; then
        find "$output_dir" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
      else
        rm -rf "$output_dir"
      fi
    fi

    mkdir -p "$output_dir"

    process_commands "$config_file" "$output_dir"
    process_skills "$config_file" "$output_dir"
    process_agents "$config_file" "$output_dir"
    process_templates "$config_file" "$output_dir"
    process_hooks "$config_file" "$output_dir"
    process_manifest "$config_file" "$output_dir"

    echo ""
  done

  echo "=== sync complete ==="
}

main "$@"
