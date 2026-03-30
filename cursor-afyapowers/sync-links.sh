#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PREFIX="afyapowers"
added=0
removed=0

sync_dir() {
  local src_dir="$1"
  local dest_dir="$2"
  local pattern="$3"

  mkdir -p "$dest_dir"
  local expected=""

  # Create missing symlinks
  for item in $src_dir/$pattern; do
    [ -e "$item" ] || continue
    name="$(basename "$item")"
    link="${dest_dir}/${PREFIX}-${name}"
    expected="${expected}${PREFIX}-${name}"$'\n'
    if [ -L "$link" ]; then
      continue
    fi
    ln -s "../../$(basename "$src_dir")/${name}" "$link"
    echo "added: $link"
    added=$((added + 1))
  done

  # Remove stale symlinks
  for link in "${dest_dir}/${PREFIX}"-*; do
    [ -L "$link" ] || continue
    linkname="$(basename "$link")"
    if ! echo "$expected" | grep -qx "$linkname"; then
      rm "$link"
      echo "removed: $link"
      removed=$((removed + 1))
    fi
  done
}

sync_dir "../commands" "commands" "*.md"
sync_dir "../skills" "skills" "*/"

echo "done: ${added} added, ${removed} removed"
