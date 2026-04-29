"""Codex-specific asset discovery and log loading."""
from __future__ import annotations

import json
import re
from pathlib import Path

from ._shared import (
    AssetItem,
    codex_home,
    dedupe_assets,
    home,
    path_marker,
    safe_read_lines,
)


CODEX_MCP_RE = re.compile(r"^\[mcp_servers\.(?P<name>[A-Za-z0-9_-]+)\]$")
CODEX_PLUGIN_RE = re.compile(r"^\[plugins\.\"(?P<name>[^\"]+)\"\]$")


def discover_plugins() -> list[AssetItem]:
    chome = codex_home()
    items: list[AssetItem] = []

    root_dir = chome / "plugin-roots"
    if root_dir.exists():
        for path in sorted(root_dir.iterdir()):
            if path.is_dir():
                items.append(
                    AssetItem(
                        type="plugin",
                        name=path.name,
                        scope="codex-plugin-root",
                        path=path,
                        source=path,
                        markers=path_marker(path),
                        deletable=True,
                        delete_kind="directory",
                    )
                )

    cache_dir = chome / "plugins" / "cache"
    for plugin_json in sorted(cache_dir.rglob(".codex-plugin/plugin.json")) if cache_dir.exists() else []:
        plugin_root = plugin_json.parent.parent
        version = plugin_root.name
        plugin_name = plugin_root.parent.name
        publisher = plugin_root.parent.parent.name
        name = f"{plugin_name}@{publisher}/{version}"
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
            json_name = data.get("name") or data.get("id")
            if isinstance(json_name, str) and json_name:
                name = f"{json_name}@{publisher}/{version}"
        except (OSError, json.JSONDecodeError):
            pass
        items.append(
            AssetItem(
                type="plugin",
                name=name,
                scope="codex-plugin-cache",
                path=plugin_root,
                source=plugin_json,
                markers=path_marker(plugin_root),
                deletable=False,
                delete_kind="directory",
            )
        )

    config = chome / "config.toml"
    for line in safe_read_lines(config):
        match = CODEX_PLUGIN_RE.match(line.strip())
        if match:
            name = match.group("name")
            items.append(
                AssetItem(
                    type="plugin",
                    name=name,
                    scope="codex-config",
                    path=None,
                    source=config,
                    markers=(name,),
                    deletable=False,
                    delete_kind="config",
                )
            )
    return dedupe_assets(items)


def discover_agents() -> list[AssetItem]:
    chome = codex_home()
    agent_dir = chome / "agents"
    prompt_dir = chome / "prompts"
    items: list[AssetItem] = []
    seen_names: set[str] = set()

    if agent_dir.exists():
        for agent_file in sorted(agent_dir.glob("*.md")):
            name = agent_file.stem
            prompt_file = prompt_dir / f"{name}.md"
            extra = (prompt_file,) if prompt_file.exists() else ()
            markers = (str(agent_file),) + tuple(str(path) for path in extra)
            items.append(
                AssetItem(
                    type="agent",
                    name=name,
                    scope="codex",
                    path=agent_file,
                    source=agent_file,
                    markers=markers,
                    extra_paths=extra,
                    deletable=True,
                    delete_kind="file",
                )
            )
            seen_names.add(name)

    if prompt_dir.exists():
        for prompt_file in sorted(prompt_dir.glob("*.md")):
            name = prompt_file.stem
            if name in seen_names:
                continue
            items.append(
                AssetItem(
                    type="agent",
                    name=name,
                    scope="codex-prompt",
                    path=prompt_file,
                    source=prompt_file,
                    markers=path_marker(prompt_file),
                    deletable=True,
                    delete_kind="file",
                )
            )
    return dedupe_assets(items)


def discover_skills() -> list[AssetItem]:
    chome = codex_home()
    roots = [
        (chome / "skills", "codex", True),
        (home() / ".agents" / "skills", "agents", True),
        (chome / "plugins" / "cache", "plugin-cache", False),
    ]
    items: list[AssetItem] = []
    for root, scope, root_deletable in roots:
        if not root.exists():
            continue
        for skill_file in sorted(root.rglob("SKILL.md")):
            from ._shared import skill_name_from_path
            if scope == "plugin-cache" and "/skills/" not in str(skill_file):
                continue
            name = skill_name_from_path(skill_file, root, scope)
            protected = name == "ai-tool-auditor" or "/.system/" in str(skill_file)
            deletable = root_deletable and not protected and ".system" not in skill_file.relative_to(root).parts
            items.append(
                AssetItem(
                    type="skill",
                    name=name,
                    scope=scope,
                    path=skill_file.parent,
                    source=skill_file,
                    markers=path_marker(skill_file),
                    deletable=deletable,
                    protected=protected,
                    delete_kind="directory",
                )
            )
    return dedupe_assets(items)


def discover_mcps() -> list[AssetItem]:
    from ._shared import normalize_server
    config = codex_home() / "config.toml"
    items: list[AssetItem] = []
    for line in safe_read_lines(config):
        match = CODEX_MCP_RE.match(line.strip())
        if not match:
            continue
        name = match.group("name")
        items.append(
            AssetItem(
                type="mcp",
                name=name,
                scope="codex",
                path=None,
                source=config,
                markers=(f"mcp__{normalize_server(name)}__", f"mcp__{name}__"),
                deletable=True,
                delete_kind="mcp-config",
            )
        )
    return dedupe_assets(items)


def codex_mcp_sections(lines: list[str], name: str) -> tuple[list[str], list[tuple[int, str]]]:
    kept: list[str] = []
    removed_sections: list[tuple[int, str]] = []
    removing = False
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            removing = section == f"mcp_servers.{name}" or section.startswith(f"mcp_servers.{name}.")
            if removing:
                removed_sections.append((index, section))
        if not removing:
            kept.append(line)
    return kept, removed_sections


def discover_all() -> list[AssetItem]:
    return discover_plugins() + discover_agents() + discover_skills() + discover_mcps()


def load_log_lines(cutoff, args):
    from ._shared import safe_read_log_lines
    log_file = codex_home() / "log" / "codex-tui.log"
    if not log_file.exists():
        return [], False, str(log_file)
    max_log_bytes = args.max_log_bytes or 64 * 1024 * 1024
    return list(safe_read_log_lines(log_file, cutoff, max_log_bytes)), True, str(log_file)
