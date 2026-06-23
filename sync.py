#!/usr/bin/env python3
"""afyapowers sync — generate per-agent distributions from source."""

import argparse
import json
import os
import re
import shutil
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

TOP_LEVEL_KEY_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*:$")


@dataclass
class AgentConfig:
    agent: str
    output_dir: Path
    skills_dir_prefix: str
    agents_file_prefix: str
    templates: bool
    hooks: bool
    plugin_manifest: Optional[dict]


def parse_agent_config(config_path: Path, repo_root: Path) -> AgentConfig:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON config file: {config_path}")
        print(f"  {e}")
        sys.exit(1)

    for key in ("agent", "outputDir"):
        if key not in data:
            print(f"ERROR: Required field '{key}' missing in config: {config_path}")
            sys.exit(1)

    return AgentConfig(
        agent=data["agent"],
        output_dir=repo_root / data["outputDir"],
        skills_dir_prefix=data.get("skills", {}).get("dirPrefix", ""),
        agents_file_prefix=data.get("agents", {}).get("filePrefix", ""),
        templates=bool(data.get("templates", False)),
        hooks=bool(data.get("hooks", False)),
        plugin_manifest=data.get("pluginManifest"),
    )


def parse_embedded_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse multi-agent frontmatter from a markdown file.

    Returns (agent_sections, body) where agent_sections maps agent name
    to its de-indented YAML string, and body is everything after the
    closing --- marker.
    """
    if not text.startswith("---\n"):
        return {}, text

    rest = text[4:]
    marker = "\n---\n"
    close_pos = rest.find(marker)

    if close_pos == -1:
        if rest.endswith("\n---"):
            fm_text = rest[: len(rest) - 4]
            body = ""
        else:
            return {}, text
    else:
        fm_text = rest[:close_pos]
        body = rest[close_pos + len(marker) :]

    agent_sections: dict[str, str] = {}
    current_agent: Optional[str] = None
    current_lines: list[str] = []

    for line in fm_text.split("\n"):
        stripped = line.rstrip()
        if TOP_LEVEL_KEY_RE.match(stripped):
            if current_agent is not None:
                section = _format_section(current_lines)
                if section is not None:
                    agent_sections[current_agent] = section
            current_agent = stripped[:-1]
            current_lines = []
        elif current_agent is not None:
            current_lines.append(line)

    if current_agent is not None:
        section = _format_section(current_lines)
        if section is not None:
            agent_sections[current_agent] = section

    return agent_sections, body


def _format_section(lines: list[str]) -> Optional[str]:
    """De-indent agent section by 2 spaces and strip surrounding blank lines."""
    result: list[str] = []
    for line in lines:
        if line.startswith("  "):
            result.append(line[2:])
        elif line.strip() == "":
            result.append("")

    while result and result[0] == "":
        result.pop(0)
    while result and result[-1] == "":
        result.pop()

    return "\n".join(result) if result else None


def render_frontmatter(yaml_str: str) -> str:
    return f"---\n{yaml_str}\n---\n"


# ---------------------------------------------------------------------------
# Processors
# ---------------------------------------------------------------------------


def process_single_files(
    src_dir: Path,
    output_subdir: str,
    file_prefix: str,
    agent_name: str,
    output_dir: Path,
) -> tuple[int, int]:
    out_dir = output_dir / output_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    if src_dir.is_dir():
        for src_file in sorted(src_dir.glob("*.md")):
            file_text = src_file.read_text(encoding="utf-8")
            agent_sections, body = parse_embedded_frontmatter(file_text)

            out_file = out_dir / f"{file_prefix}{src_file.name}"
            agent_yaml = agent_sections.get(agent_name)
            if agent_yaml:
                out_file.write_text(
                    render_frontmatter(agent_yaml) + body, encoding="utf-8"
                )
            else:
                out_file.write_text(body, encoding="utf-8")
            count += 1

    removed = 0
    if out_dir.is_dir():
        for out_file in sorted(out_dir.glob("*.md")):
            original_name = out_file.name.removeprefix(file_prefix)
            if not (src_dir / original_name).is_file():
                out_file.unlink()
                removed += 1

    return count, removed


def process_skills(
    config: AgentConfig,
    src_dir: Path,
    output_dir: Path,
) -> tuple[int, int]:
    skills_out = output_dir / "skills"
    skills_out.mkdir(parents=True, exist_ok=True)
    skills_src = src_dir / "skills"

    count = 0
    if skills_src.is_dir():
        for skill_dir in sorted(d for d in skills_src.iterdir() if d.is_dir()):
            out_skill_dir = skills_out / f"{config.skills_dir_prefix}{skill_dir.name}"
            out_skill_dir.mkdir(parents=True, exist_ok=True)

            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                file_text = skill_file.read_text(encoding="utf-8")
                agent_sections, body = parse_embedded_frontmatter(file_text)
                agent_yaml = agent_sections.get(config.agent)
                if agent_yaml:
                    (out_skill_dir / "SKILL.md").write_text(
                        render_frontmatter(agent_yaml) + body, encoding="utf-8"
                    )
                else:
                    (out_skill_dir / "SKILL.md").write_text(body, encoding="utf-8")

            for item in sorted(skill_dir.iterdir()):
                if item.name == "SKILL.md":
                    continue
                dest = out_skill_dir / item.name
                if item.is_dir():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

            for item in list(out_skill_dir.iterdir()):
                if not (skill_dir / item.name).exists():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            count += 1

    removed = 0
    if skills_out.is_dir():
        for entry in sorted(skills_out.iterdir()):
            if entry.is_dir():
                original_name = entry.name.removeprefix(config.skills_dir_prefix)
                if not (skills_src / original_name).is_dir():
                    shutil.rmtree(entry)
                    removed += 1

    return count, removed


def process_templates(
    config: AgentConfig, src_dir: Path, output_dir: Path
) -> Optional[int]:
    if not config.templates:
        return None
    templates_src = src_dir / "templates"
    if not templates_src.is_dir():
        return None
    templates_out = output_dir / "templates"
    if templates_out.is_dir():
        shutil.rmtree(templates_out)
    shutil.copytree(templates_src, templates_out)
    return sum(1 for _ in templates_out.rglob("*") if _.is_file())


def process_hooks(
    config: AgentConfig, src_dir: Path, output_dir: Path
) -> Optional[int]:
    if not config.hooks:
        return None
    hooks_src = src_dir / "hooks"
    if not hooks_src.is_dir():
        return None
    hooks_out = output_dir / "hooks"
    if hooks_out.is_dir():
        shutil.rmtree(hooks_out)
    shutil.copytree(hooks_src, hooks_out)
    for src_file in hooks_src.iterdir():
        if src_file.is_file() and os.access(src_file, os.X_OK):
            out_file = hooks_out / src_file.name
            if out_file.is_file():
                st = out_file.stat()
                out_file.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    # Each agent has its own `hooks.<agent>.json` source file. Emit only that
    # agent's config as a single `hooks.json`; drop the other agents' configs.
    for out_file in hooks_out.glob("hooks*.json"):
        out_file.unlink()
    agent_hooks = hooks_src / f"hooks.{config.agent}.json"
    if agent_hooks.is_file():
        shutil.copy2(agent_hooks, hooks_out / "hooks.json")
    return sum(1 for _ in hooks_out.rglob("*") if _.is_file())


def process_manifest(
    config: AgentConfig, repo_root: Path, output_dir: Path
) -> Optional[str]:
    if not config.plugin_manifest:
        return None
    from_val = config.plugin_manifest.get("from", "")
    to_val = config.plugin_manifest.get("to", "")
    if not from_val or not to_val:
        print(
            f'  Manifest: missing required "from" or "to" keys in manifest configuration, skipped'
        )
        return None
    from_path = repo_root / from_val
    to_path = output_dir / to_val
    if not from_path.exists():
        print(f"  Manifest: source {config.plugin_manifest['from']} not found, skipped")
        return None
    to_path.parent.mkdir(parents=True, exist_ok=True)
    if from_path.is_dir():
        to_path.mkdir(parents=True, exist_ok=True)
        for item in from_path.iterdir():
            dest = to_path / item.name
            if item.is_dir():
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
    else:
        shutil.copy2(from_path, to_path)
    return from_val


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def clean_output_dir(output_dir: Path) -> None:
    if not output_dir.is_dir():
        return
    if (output_dir / ".git").is_dir():
        for item in output_dir.iterdir():
            if item.name != ".git":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    else:
        shutil.rmtree(output_dir)


def sync_agent(
    config: AgentConfig, repo_root: Path, src_dir: Path, do_clean: bool
) -> None:
    print(f"[{config.agent}] → {config.output_dir}")

    if do_clean:
        clean_output_dir(config.output_dir)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    count, removed = process_skills(config, src_dir, config.output_dir)
    msg = f"  Skills: {count} directories"
    if removed:
        msg += f" ({removed} stale removed)"
    print(msg)

    count, removed = process_single_files(
        src_dir / "agents",
        "agents",
        config.agents_file_prefix,
        config.agent,
        config.output_dir,
    )
    msg = f"  agents: {count} files"
    if removed:
        msg += f" ({removed} stale removed)"
    print(msg)

    result = process_templates(config, src_dir, config.output_dir)
    print(
        f"  Templates: {result} files" if result is not None else "  Templates: skipped"
    )

    result = process_hooks(config, src_dir, config.output_dir)
    print(f"  Hooks: {result} files" if result is not None else "  Hooks: skipped")

    manifest_src = process_manifest(config, repo_root, config.output_dir)
    if manifest_src is not None:
        print(f"  Manifest: copied from {manifest_src}")
    elif config.plugin_manifest is None:
        print("  Manifest: skipped")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="afyapowers sync — generate per-agent distributions from source"
    )
    parser.add_argument(
        "agents", nargs="*", help="Agent names to sync (default: all from src/config/)"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Remove output directories before syncing"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    src_dir = repo_root / "src"
    config_dir = src_dir / "config"

    agent_names = args.agents or sorted(f.stem for f in config_dir.glob("*.json"))

    print("=== afyapowers sync ===")
    print()

    for agent_name in agent_names:
        config_path = config_dir / f"{agent_name}.json"
        if not config_path.is_file():
            print(f"ERROR: Config not found: {config_path}")
            continue
        config = parse_agent_config(config_path, repo_root)
        sync_agent(config, repo_root, src_dir, args.clean)
        print()

    print("=== sync complete ===")


if __name__ == "__main__":
    main()
