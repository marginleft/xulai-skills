"""Shared types, utilities, and delete logic for ai-tool-auditor."""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


TS_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
MCP_TOOL_RE = re.compile(r"mcp__(?P<server>[A-Za-z0-9_-]+)__[A-Za-z0-9_-]+")


@dataclass(frozen=True)
class AssetItem:
    type: str
    name: str
    scope: str
    path: Path | None
    source: Path | None
    markers: tuple[str, ...] = field(default_factory=tuple)
    extra_paths: tuple[Path, ...] = field(default_factory=tuple)
    deletable: bool = False
    protected: bool = False
    delete_kind: str = "path"


def home() -> Path:
    return Path.home()


def env_path(name: str, fallback: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else fallback


def codex_home() -> Path:
    return env_path("CODEX_HOME", home() / ".codex")


def normalize_server(name: str) -> str:
    return name.replace("-", "_")


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_today(value: str | None) -> dt.datetime:
    if not value:
        return dt.datetime.now(dt.timezone.utc)
    parsed = dt.datetime.strptime(value, "%Y-%m-%d")
    return parsed.replace(tzinfo=dt.timezone.utc) + dt.timedelta(days=1)


def cutoff_for(days: int, today: str | None) -> dt.datetime:
    return parse_today(today) - dt.timedelta(days=days)


def parse_log_ts(line: str) -> dt.datetime | None:
    match = TS_RE.match(line)
    if not match:
        return None
    text = match.group("ts").replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def line_in_window(line: str, cutoff: dt.datetime) -> bool:
    timestamp_value = parse_log_ts(line)
    return timestamp_value is None or timestamp_value >= cutoff


def safe_read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            yield from handle
    except OSError:
        return


def safe_read_log_lines(path: Path, cutoff: dt.datetime, max_bytes: int) -> Iterable[str]:
    try:
        stat = path.stat()
    except OSError:
        return
    if dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc) < cutoff:
        return

    try:
        with path.open("rb") as handle:
            if max_bytes > 0 and stat.st_size > max_bytes:
                handle.seek(stat.st_size - max_bytes)
                handle.readline()
            for raw_line in handle:
                line = raw_line.decode("utf-8", errors="ignore")
                if line_in_window(line, cutoff):
                    yield line
    except OSError:
        return


def process_ancestors() -> list[str]:
    names: list[str] = []
    pid = os.getpid()
    seen: set[int] = set()
    for _ in range(20):
        if pid in seen or pid <= 1:
            break
        seen.add(pid)
        try:
            output = subprocess.check_output(
                ["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            break
        if not output:
            break
        parts = output.split(None, 1)
        if not parts:
            break
        try:
            ppid = int(parts[0])
        except ValueError:
            break
        command = parts[1] if len(parts) > 1 else ""
        names.append(Path(command).name.lower())
        pid = ppid
    return names


def detect_tool() -> str:
    forced = os.environ.get("AI_TOOL_AUDITOR_TOOL", "").strip().lower()
    if forced in {"codex", "claude"}:
        return forced

    ancestors = " ".join(process_ancestors())
    if "codex" in ancestors:
        return "codex"
    if "claude" in ancestors:
        return "claude"

    if codex_home().exists():
        return "codex"
    if (home() / ".claude").exists():
        return "claude"
    return "codex"


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def path_marker(path: Path | None) -> tuple[str, ...]:
    return (str(path),) if path else ()


def skill_name_from_path(skill_file: Path, root: Path, prefix: str) -> str:
    try:
        rel = skill_file.parent.relative_to(root)
        return str(rel)
    except ValueError:
        return f"{prefix}/{skill_file.parent.name}"


def dedupe_assets(items: list[AssetItem]) -> list[AssetItem]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[AssetItem] = []
    for item in items:
        path = str(item.path.resolve()) if item.path else ""
        key = (item.type, item.scope, item.name, path)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def collect_mcp_servers_from_json(data: object) -> set[str]:
    names: set[str] = set()
    if isinstance(data, dict):
        servers = data.get("mcpServers")
        if isinstance(servers, dict):
            names.update(str(key) for key in servers.keys())
        for value in data.values():
            names.update(collect_mcp_servers_from_json(value))
    elif isinstance(data, list):
        for value in data:
            names.update(collect_mcp_servers_from_json(value))
    return names


def marker_count(lines: list[str], markers: tuple[str, ...]) -> int:
    if not markers:
        return 0
    total = 0
    unique_markers = tuple(marker for marker in dict.fromkeys(markers) if marker)
    for line in lines:
        if any(marker in line for marker in unique_markers):
            total += 1
    return total


def mcp_count(lines: list[str], item: AssetItem) -> int:
    names = {normalize_server(item.name), item.name}
    total = 0
    for line in lines:
        for match in MCP_TOOL_RE.finditer(line):
            if match.group("server") in names:
                total += 1
    marker_total = marker_count(lines, item.markers)
    return max(total, marker_total)


def recommendation(item: AssetItem, count: int, usage_known: bool, days: int) -> tuple[bool, str, str]:
    if not usage_known:
        return False, "manual_review", "usage logs missing or unavailable"
    if item.protected:
        return False, "not_recommended", "protected asset"
    if not item.deletable:
        return False, "not_recommended", "not safely deletable by default"
    if count > 0:
        return False, "not_recommended", "usage found in current log window"
    if item.type == "plugin" and item.scope.endswith("-plugin-cache"):
        return False, "manual_review", "plugin cache is not deleted by default"
    return (
        True,
        "recommend_delete",
        f"no usage found in current {days}-day log window; recent usage pattern suggests low future usage likelihood",
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sort_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    def key(row: dict[str, object]) -> tuple[bool, int, str, str, str]:
        return (
            str(row["recommend_delete"]) != "true",
            -int(row["count_last_n_days"]),
            str(row["type"]),
            str(row["scope"]),
            str(row["name"]),
        )
    return sorted(rows, key=key)


def reindex(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(row, index=index) for index, row in enumerate(rows, start=1)]


def row_for_item(
    index: int,
    item: AssetItem,
    count: int,
    tool: str,
    days: int,
    usage_known: bool,
    log_source: str,
) -> dict[str, object]:
    recommend, status, reason = recommendation(item, count, usage_known, days)
    return {
        "index": index,
        "type": item.type,
        "name": item.name,
        "scope": item.scope,
        "count_last_n_days": count,
        "days": days,
        "tool": tool,
        "usage_status": "counted" if usage_known else "logs_missing",
        "recommend_delete": str(recommend).lower(),
        "recommendation": status,
        "reason": reason,
        "deletable": str(item.deletable).lower(),
        "delete_kind": item.delete_kind,
        "path": str(item.path) if item.path else "",
        "extra_paths": "|".join(str(path) for path in item.extra_paths),
        "source": str(item.source) if item.source else "",
        "log_source": log_source,
    }


def count_recommended(rows: list[dict[str, object]]) -> int:
    return sum(1 for row in rows if str(row["recommend_delete"]) == "true")


def parse_indexes(value: str) -> set[int]:
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            start = int(left)
            end = int(right)
            result.update(range(min(start, end), max(start, end) + 1))
        else:
            result.add(int(part))
    return result


def claude_supported_roots() -> dict[str, list[Path]]:
    return {
        "plugin": [
            home() / ".claude" / "plugins",
            home() / ".claude" / "plugins" / "marketplaces",
            Path.cwd() / ".claude" / "plugins",
        ],
        "agent": [
            home() / ".claude" / "agents",
            home() / ".claude" / "plugins" / "marketplaces",
            Path.cwd() / ".claude" / "agents",
        ],
        "skill": [
            home() / ".claude" / "skills",
            home() / ".claude" / "plugins" / "marketplaces",
            Path.cwd() / ".claude" / "skills",
        ],
    }


def codex_supported_roots() -> dict[str, list[Path]]:
    chome = codex_home()
    return {
        "plugin": [chome / "plugin-roots"],
        "agent": [chome / "agents", chome / "prompts"],
        "skill": [chome / "skills", home() / ".agents" / "skills"],
    }


def supported_roots() -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    for d in (codex_supported_roots(), claude_supported_roots()):
        for key, paths in d.items():
            result.setdefault(key, []).extend(paths)
    return result


def safe_destination(base: Path, scope: str, path: Path) -> Path:
    destination: Path | None = None
    for roots in supported_roots().values():
        for root in roots:
            if not is_under(path, root):
                continue
            try:
                relative = path.resolve().relative_to(root.resolve())
            except (ValueError, OSError):
                continue
            destination = base / scope / root.name / relative
            break
        if destination is not None:
            break
    if destination is None:
        destination = base / scope / path.name
    if destination.exists():
        destination = destination.with_name(f"{destination.name}-{timestamp()}")
    return destination


def validate_path_row(row: dict[str, str], roots: list[Path]) -> tuple[Path | None, str | None]:
    path_text = row.get("path", "")
    if not path_text:
        return None, "missing path"
    path = Path(path_text).expanduser()
    if not path.exists():
        return None, "path not found"
    if not any(is_under(path, root) for root in roots):
        return None, "path outside supported roots"
    return path, None


def read_selected_rows(csv_path: Path, indexes: set[int]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                index = int(row.get("index", "0"))
            except ValueError:
                continue
            if index in indexes:
                rows.append(row)
    return rows


def should_refuse_row(row: dict[str, str]) -> str | None:
    if row.get("recommend_delete") != "true":
        return "entry is not recommended for deletion"
    if row.get("deletable") != "true":
        return "entry is not deletable"
    if row.get("usage_status") != "counted":
        return "usage logs were not counted"
    if row.get("count_last_n_days") != "0":
        return "usage count is not zero"
    return None


def remove_mcp_from_json(data: object, name: str) -> tuple[object, int]:
    removed = 0
    if isinstance(data, dict):
        servers = data.get("mcpServers")
        if isinstance(servers, dict) and name in servers:
            servers = dict(servers)
            servers.pop(name, None)
            data = dict(data)
            data["mcpServers"] = servers
            removed += 1
        new_data: dict[object, object] = {}
        for key, value in data.items():
            new_value, child_removed = remove_mcp_from_json(value, name)
            removed += child_removed
            new_data[key] = new_value
        return new_data, removed
    if isinstance(data, list):
        new_items: list[object] = []
        for value in data:
            new_value, child_removed = remove_mcp_from_json(value, name)
            removed += child_removed
            new_items.append(new_value)
        return new_items, removed
    return data, 0
