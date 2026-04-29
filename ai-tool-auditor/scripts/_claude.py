"""Claude Code-specific asset discovery and log loading."""
from __future__ import annotations

import json
from pathlib import Path

from ._shared import (
    AssetItem,
    collect_mcp_servers_from_json,
    dedupe_assets,
    home,
    normalize_server,
    path_marker,
    safe_read_log_lines,
)


def _plugins_dir() -> Path:
    return home() / ".claude" / "plugins"


def discover_plugins() -> list[AssetItem]:
    items: list[AssetItem] = []
    plugins_dir = _plugins_dir()
    if not plugins_dir.exists():
        return items

    installed_json = plugins_dir / "installed_plugins.json"
    if installed_json.exists():
        try:
            data = json.loads(installed_json.read_text(encoding="utf-8"))
            plugins_map = data.get("plugins", {})
            if isinstance(plugins_map, dict):
                for plugin_key, versions in plugins_map.items():
                    if not isinstance(versions, list):
                        continue
                    for entry in versions:
                        if not isinstance(entry, dict):
                            continue
                        install_path = entry.get("installPath", "")
                        if not install_path:
                            continue
                        path = Path(install_path).expanduser()
                        if not path.exists():
                            continue
                        scope = entry.get("scope", "claude")
                        items.append(
                            AssetItem(
                                type="plugin",
                                name=plugin_key,
                                scope=f"claude-{scope}",
                                path=path,
                                source=installed_json,
                                markers=(plugin_key, str(path)),
                                deletable=False,
                                delete_kind="directory",
                            )
                        )
        except (OSError, json.JSONDecodeError):
            pass

    cache_dir = plugins_dir / "cache"
    if cache_dir.exists():
        for marketplace_dir in sorted(cache_dir.iterdir()):
            if not marketplace_dir.is_dir():
                continue
            for plugin_dir in sorted(marketplace_dir.iterdir()):
                if not plugin_dir.is_dir():
                    continue
                for version_dir in sorted(plugin_dir.iterdir()):
                    if not version_dir.is_dir():
                        continue
                    name = f"{plugin_dir.name}@{marketplace_dir.name}/{version_dir.name}"
                    if any(str(version_dir) == str(item.path) for item in items):
                        continue
                    items.append(
                        AssetItem(
                            type="plugin",
                            name=name,
                            scope="claude-plugin-cache",
                            path=version_dir,
                            source=version_dir,
                            markers=path_marker(version_dir),
                            deletable=False,
                            delete_kind="directory",
                        )
                    )

    for path in sorted(plugins_dir.iterdir()):
        if not path.is_dir():
            continue
        if path.name in ("cache", "marketplaces"):
            continue
        if any(str(path) == str(item.path) for item in items):
            continue
        items.append(
            AssetItem(
                type="plugin",
                name=path.name,
                scope="claude",
                path=path,
                source=path,
                markers=path_marker(path),
                deletable=True,
                delete_kind="directory",
            )
        )

    return dedupe_assets(items)


def discover_agents() -> list[AssetItem]:
    from ._shared import skill_name_from_path

    roots = [
        (home() / ".claude" / "agents", "claude", True),
        (Path.cwd() / ".claude" / "agents", "project", True),
    ]
    items: list[AssetItem] = []
    for root, scope, root_deletable in roots:
        if not root.exists():
            continue
        for agent_file in sorted(root.glob("*.md")):
            items.append(
                AssetItem(
                    type="agent",
                    name=agent_file.stem,
                    scope=scope,
                    path=agent_file,
                    source=agent_file,
                    markers=path_marker(agent_file),
                    deletable=root_deletable,
                    delete_kind="file",
                )
            )

    cache_dir = _plugins_dir() / "cache"
    if cache_dir.exists():
        for agents_dir in sorted(cache_dir.rglob("agents")):
            if not agents_dir.is_dir():
                continue
            for agent_file in sorted(agents_dir.glob("*.md")):
                name = f"{agent_file.stem}@{agents_dir.parent.parent.parent.name}"
                items.append(
                    AssetItem(
                        type="agent",
                        name=name,
                        scope="plugin-cache",
                        path=agent_file,
                        source=agent_file,
                        markers=path_marker(agent_file),
                        deletable=False,
                        delete_kind="file",
                    )
                )

    return dedupe_assets(items)


def discover_skills() -> list[AssetItem]:
    from ._shared import skill_name_from_path

    roots = [
        (home() / ".claude" / "skills", "claude", True),
        (Path.cwd() / ".claude" / "skills", "project", True),
    ]
    items: list[AssetItem] = []
    for root, scope, root_deletable in roots:
        if not root.exists():
            continue
        for skill_file in sorted(root.rglob("SKILL.md")):
            name = skill_name_from_path(skill_file, root, scope)
            protected = name == "ai-tool-auditor"
            items.append(
                AssetItem(
                    type="skill",
                    name=name,
                    scope=scope,
                    path=skill_file.parent,
                    source=skill_file,
                    markers=path_marker(skill_file),
                    deletable=root_deletable and not protected,
                    protected=protected,
                    delete_kind="directory",
                )
            )

    cache_dir = _plugins_dir() / "cache"
    if cache_dir.exists():
        for skill_file in sorted(cache_dir.rglob("SKILL.md")):
            name = skill_name_from_path(skill_file, cache_dir, "plugin-cache")
            items.append(
                AssetItem(
                    type="skill",
                    name=name,
                    scope="plugin-cache",
                    path=skill_file.parent,
                    source=skill_file,
                    markers=path_marker(skill_file),
                    deletable=False,
                    protected=False,
                    delete_kind="directory",
                )
            )

    return dedupe_assets(items)


def discover_mcps() -> list[AssetItem]:
    candidates = [
        home() / ".claude.json",
        home() / ".claude" / "settings.json",
        home() / ".claude" / "settings.local.json",
        home() / ".claude" / "mcp.json",
        Path.cwd() / ".mcp.json",
        Path.cwd() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.local.json",
    ]
    items: list[AssetItem] = []
    for source in candidates:
        if not source.exists():
            continue
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for name in sorted(collect_mcp_servers_from_json(data)):
            items.append(
                AssetItem(
                    type="mcp",
                    name=name,
                    scope="claude",
                    path=None,
                    source=source,
                    markers=(f"mcp__{normalize_server(name)}__", f"mcp__{name}__"),
                    deletable=True,
                    delete_kind="mcp-json",
                )
            )
    return dedupe_assets(items)


def _marketplaces_dir() -> Path:
    return _plugins_dir() / "marketplaces"


def discover_marketplace_plugins() -> list[AssetItem]:
    items: list[AssetItem] = []
    mp_dir = _marketplaces_dir()
    if not mp_dir.exists():
        return items

    for plugin_json in sorted(mp_dir.rglob("plugin.json")):
        parent = plugin_json.parent
        if parent.name not in (".claude-plugin", ".codex-plugin"):
            continue
        plugin_root = parent.parent
        if plugin_root.parent.parent != mp_dir:
            continue
        marketplace = plugin_root.parent.name
        plugin_name = plugin_root.name
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
            display_name = data.get("name", plugin_name)
        except (OSError, json.JSONDecodeError):
            display_name = plugin_name
        items.append(
            AssetItem(
                type="plugin",
                name=f"{display_name}@{marketplace}",
                scope="marketplace",
                path=plugin_root,
                source=plugin_json,
                markers=(plugin_name, str(plugin_root)),
                deletable=False,
                delete_kind="directory",
            )
        )

    return dedupe_assets(items)


def discover_marketplace_agents() -> list[AssetItem]:
    from ._shared import skill_name_from_path

    mp_dir = _marketplaces_dir()
    if not mp_dir.exists():
        return []

    items: list[AssetItem] = []
    for agents_dir in sorted(mp_dir.rglob("agents")):
        if not agents_dir.is_dir():
            continue
        for agent_file in sorted(agents_dir.glob("*.md")):
            parts = agent_file.parts
            try:
                mp_idx = parts.index("marketplaces")
                marketplace = parts[mp_idx + 1]
            except (ValueError, IndexError):
                marketplace = "unknown"
            name = f"{agent_file.stem}@{marketplace}"
            items.append(
                AssetItem(
                    type="agent",
                    name=name,
                    scope="marketplace",
                    path=agent_file,
                    source=agent_file,
                    markers=path_marker(agent_file),
                    deletable=False,
                    delete_kind="file",
                )
            )
    return dedupe_assets(items)


def discover_marketplace_skills() -> list[AssetItem]:
    from ._shared import skill_name_from_path

    mp_dir = _marketplaces_dir()
    if not mp_dir.exists():
        return []

    items: list[AssetItem] = []
    for skill_file in sorted(mp_dir.rglob("SKILL.md")):
        skill_dir = skill_file.parent
        parts = skill_file.parts
        try:
            mp_idx = parts.index("marketplaces")
            marketplace = parts[mp_idx + 1]
        except (ValueError, IndexError):
            marketplace = "unknown"
        name = skill_name_from_path(skill_file, mp_dir, f"marketplace-{marketplace}")
        items.append(
            AssetItem(
                type="skill",
                name=name,
                scope="marketplace",
                path=skill_dir,
                source=skill_file,
                markers=path_marker(skill_file),
                deletable=False,
                protected=False,
                delete_kind="directory",
            )
        )
    return dedupe_assets(items)


def discover_all() -> list[AssetItem]:
    return (
        discover_plugins()
        + discover_marketplace_plugins()
        + discover_agents()
        + discover_marketplace_agents()
        + discover_skills()
        + discover_marketplace_skills()
        + discover_mcps()
    )


def _claude_log_files(cutoff, max_files):
    base = home() / ".claude"
    if not base.exists():
        return []
    roots = [base / "projects", base / "logs", base / "tasks"]
    files: list[Path] = [path for path in base.glob("*.jsonl")] + [path for path in base.glob("*.log")]
    for root in roots:
        if not root.exists():
            continue
        files.extend(root.rglob("*.jsonl"))
        files.extend(root.rglob("*.log"))

    import datetime as dt
    recent: list[tuple[float, Path]] = []
    for path in {path for path in files if path.is_file()}:
        try:
            stat = path.stat()
            modified = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
        except OSError:
            continue
        if modified >= cutoff:
            recent.append((stat.st_mtime, path))
    recent.sort(reverse=True)
    if max_files > 0:
        recent = recent[:max_files]
    return [path for _, path in recent]


def load_log_lines(cutoff, args):
    max_log_bytes = args.max_log_bytes or 256 * 1024
    max_log_files = args.max_log_files or 50
    files = _claude_log_files(cutoff, max_log_files)
    if not files:
        return [], False, str(home() / ".claude")
    lines: list[str] = []
    for log_file in files:
        lines.extend(safe_read_log_lines(log_file, cutoff, max_log_bytes))
    return lines, True, ",".join(str(path) for path in files)
