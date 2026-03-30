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
    python3 -c "import json,sys; d=json.load(open('$file')); v=$( echo "$path" | sed 's/^\./d/' | sed 's/\.\([a-zA-Z_]*\)/["\1"]/g' ); print(v if v is not None else '')"
  fi
}

json_keys() {
  local file="$1" path="$2"
  if command -v jq &>/dev/null; then
    jq -r "$path | keys[]" "$file" 2>/dev/null || true
  else
    python3 -c "
import json
d=json.load(open('$file'))
obj=$(echo "$path" | sed 's/^\./d/' | sed 's/\.\([a-zA-Z_]*\)/[\"\1\"]/g')
if isinstance(obj, dict):
    for k in obj: print(k)
" 2>/dev/null || true
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

# --- Template variable resolution ---

resolve_template() {
  local template="$1"
  shift
  local result="$template"
  while [[ $# -ge 2 ]]; do
    local key="$1" val="$2"
    result="${result//\{\{$key\}\}/$val}"
    shift 2
  done
  echo "$result"
}

# --- Extract heading title from command file ---
# Parses: # /afyapowers:abort — Abort Current Feature
# Returns: Abort Current Feature

extract_heading_title() {
  local file="$1"
  local first_line
  first_line=$(head -1 "$file")
  # Match after em-dash (U+2014) or regular dash
  if [[ "$first_line" =~ —[[:space:]]*(.*) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$first_line" =~ --[[:space:]]*(.*) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    # Fallback: strip the heading prefix
    echo "${first_line#\# }"
  fi
}

# --- YAML frontmatter helpers ---

# Extract frontmatter content (between --- markers) from a file
extract_frontmatter() {
  local file="$1"
  local in_frontmatter=false
  local line_num=0
  while IFS= read -r line; do
    line_num=$((line_num + 1))
    if [[ "$line" == "---" ]]; then
      if $in_frontmatter; then
        return
      elif [[ $line_num -eq 1 ]]; then
        in_frontmatter=true
        continue
      fi
    fi
    if $in_frontmatter; then
      echo "$line"
    fi
  done < "$file"
}

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

# Get a simple top-level YAML value (handles quoted and unquoted)
yaml_get() {
  local key="$1"
  local frontmatter="$2"
  echo "$frontmatter" | grep -E "^${key}:" | head -1 | sed "s/^${key}:[[:space:]]*//" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/"
}

# Replace or add a top-level YAML key-value pair
# Only replaces simple key: value lines (not nested/multi-line)
yaml_set() {
  local key="$1" value="$2" frontmatter="$3"
  if echo "$frontmatter" | grep -qE "^${key}:"; then
    echo "$frontmatter" | sed "s|^${key}:.*|${key}: ${value}|"
  else
    if [[ -n "$frontmatter" ]]; then
      echo "${frontmatter}"$'\n'"${key}: ${value}"
    else
      echo "${key}: ${value}"
    fi
  fi
}

# --- Build frontmatter block ---

build_frontmatter() {
  local content="$1"
  if [[ -n "$content" ]]; then
    echo "---"
    echo "$content"
    echo "---"
  fi
}

# --- Process commands for an agent ---

process_commands() {
  local config_file="$1" output_dir="$2"

  local file_prefix
  file_prefix=$(json_get "$config_file" '.commands.filePrefix')
  [[ "$file_prefix" == "null" ]] && file_prefix=""

  local prefix
  prefix=$(json_get "$config_file" '.prefix')

  local has_frontmatter=false
  local fm_keys
  fm_keys=$(json_keys "$config_file" '.commands.frontmatter')
  [[ -n "$fm_keys" ]] && has_frontmatter=true

  mkdir -p "$output_dir/commands"
  local count=0

  for src_file in "$SRC_DIR/commands/"*.md; do
    [[ -f "$src_file" ]] || continue
    local filename
    filename=$(basename "$src_file")
    local slug="${filename%.md}"
    local heading_title
    heading_title=$(extract_heading_title "$src_file")

    local out_file="$output_dir/commands/${file_prefix}${filename}"

    if $has_frontmatter; then
      # Build frontmatter from config fields
      local fm_content=""
      for key in $fm_keys; do
        local template
        template=$(json_get "$config_file" ".commands.frontmatter.${key}")
        local value
        value=$(resolve_template "$template" \
          "prefix" "$prefix" \
          "slug" "$slug" \
          "heading_title" "$heading_title" \
          "filename" "$filename")
        if [[ -n "$fm_content" ]]; then
          fm_content="${fm_content}"$'\n'"${key}: ${value}"
        else
          fm_content="${key}: ${value}"
        fi
      done

      {
        build_frontmatter "$fm_content"
        cat "$src_file"
      } > "$out_file"
    else
      cp "$src_file" "$out_file"
    fi

    count=$((count + 1))
  done

  echo "  Commands: $count files"
}

# --- Process skills for an agent ---

process_skills() {
  local config_file="$1" output_dir="$2"

  local dir_prefix
  dir_prefix=$(json_get "$config_file" '.skills.dirPrefix')
  [[ "$dir_prefix" == "null" ]] && dir_prefix=""

  local prefix
  prefix=$(json_get "$config_file" '.prefix')

  local transform
  transform=$(json_get "$config_file" '.skills.frontmatter.transform')
  [[ "$transform" == "null" ]] && transform="keep"

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
      local existing_fm
      existing_fm=$(extract_frontmatter "$skill_file")
      local body
      body=$(extract_body "$skill_file")

      case "$transform" in
        keep)
          cp "$skill_file" "$out_skill_dir/SKILL.md"
          ;;
        replace)
          local fm_content=""
          local fm_field_keys
          fm_field_keys=$(json_keys "$config_file" '.skills.frontmatter.fields')
          for key in $fm_field_keys; do
            local template
            template=$(json_get "$config_file" ".skills.frontmatter.fields.${key}")
            local value
            value=$(resolve_template "$template" \
              "prefix" "$prefix" \
              "name" "$dirname" \
              "description" "$(yaml_get 'description' "$existing_fm")")
            if [[ -n "$fm_content" ]]; then
              fm_content="${fm_content}"$'\n'"${key}: ${value}"
            else
              fm_content="${key}: ${value}"
            fi
          done
          {
            build_frontmatter "$fm_content"
            echo "$body"
          } > "$out_skill_dir/SKILL.md"
          ;;
        merge)
          local merged_fm="$existing_fm"
          local fm_field_keys
          fm_field_keys=$(json_keys "$config_file" '.skills.frontmatter.fields')
          for key in $fm_field_keys; do
            local template
            template=$(json_get "$config_file" ".skills.frontmatter.fields.${key}")
            local orig_name
            orig_name=$(yaml_get 'name' "$existing_fm")
            local orig_desc
            orig_desc=$(yaml_get 'description' "$existing_fm")
            local value
            value=$(resolve_template "$template" \
              "prefix" "$prefix" \
              "name" "$orig_name" \
              "description" "$orig_desc")
            merged_fm=$(yaml_set "$key" "$value" "$merged_fm")
          done
          {
            build_frontmatter "$merged_fm"
            echo "$body"
          } > "$out_skill_dir/SKILL.md"
          ;;
      esac
    fi

    # Copy all other files in skill directory
    for src_file in "$src_skill_dir"*; do
      local fname
      fname=$(basename "$src_file")
      [[ "$fname" == "SKILL.md" ]] && continue
      if [[ -d "$src_file" ]]; then
        cp -R "$src_file" "$out_skill_dir/$fname"
      else
        cp "$src_file" "$out_skill_dir/$fname"
      fi
    done

    count=$((count + 1))
  done

  echo "  Skills: $count directories"
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
    local dest_dir
    dest_dir=$(dirname "$output_dir/$to")
    mkdir -p "$dest_dir"
    if [[ -d "$REPO_ROOT/$from" ]]; then
      mkdir -p "$output_dir/$to"
      cp -R "$REPO_ROOT/$from/"* "$output_dir/$to/"
    else
      mkdir -p "$(dirname "$output_dir/$to")"
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
    process_templates "$config_file" "$output_dir"
    process_hooks "$config_file" "$output_dir"
    process_manifest "$config_file" "$output_dir"

    echo ""
  done

  echo "=== sync complete ==="
}

main "$@"
