#!/usr/bin/env python3
"""AI toolchain auditor — CLI entry point.

Discovers Plugin, Agent, SKILL, and MCP assets for Codex or Claude Code,
counts usage from log files, generates CSV reports, and supports safe deletion.

Platform-specific discovery lives in ``_codex.py`` and ``_claude.py``.
Shared types and utilities live in ``_shared.py``.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    import os
    __package__ = "scripts"
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ._shared import (
    cutoff_for,
    count_recommended,
    detect_tool,
    mcp_count,
    marker_count,
    normalize_server,
    parse_indexes,
    read_selected_rows,
    reindex,
    remove_mcp_from_json,
    row_for_item,
    safe_destination,
    should_refuse_row,
    sort_rows,
    supported_roots,
    timestamp,
    validate_path_row,
    write_csv,
)


def _load_modules(tool: str):
    if tool == "codex":
        from . import _codex as mod
    else:
        from . import _claude as mod
    return mod


def audit(args: argparse.Namespace) -> int:
    tool = args.tool if args.tool != "auto" else detect_tool()
    mod = _load_modules(tool)
    cutoff = cutoff_for(args.days, args.today)
    lines, usage_known, log_source = mod.load_log_lines(cutoff, args)
    assets = mod.discover_all()

    rows_by_type: dict[str, list[dict]] = {"plugin": [], "agent": [], "skill": [], "mcp": []}
    for item in assets:
        count = mcp_count(lines, item) if item.type == "mcp" else marker_count(lines, item.markers)
        rows_by_type[item.type].append(
            row_for_item(index=0, item=item, count=count, tool=tool, days=args.days,
                         usage_known=usage_known, log_source=log_source)
        )

    for key, rows in rows_by_type.items():
        rows_by_type[key] = reindex(sort_rows(rows))

    combined_rows = reindex(sort_rows([row for rows in rows_by_type.values() for row in rows]))
    recommendation_rows = reindex([row for row in combined_rows if str(row["recommend_delete"]) == "true"])

    out_dir = Path(args.output_dir).expanduser()
    run_id = timestamp()
    base = f"ai_tool_auditor_{tool}_{run_id}"
    plugins_csv = out_dir / f"{base}_plugins.csv"
    agents_csv = out_dir / f"{base}_agents.csv"
    skills_csv = out_dir / f"{base}_skills.csv"
    mcps_csv = out_dir / f"{base}_mcps.csv"
    combined_csv = out_dir / f"{base}_combined.csv"
    recommendations_csv = out_dir / f"{base}_recommended_deletions.csv"

    fields = ["index", "type", "name", "scope", "count_last_n_days", "days", "tool",
              "usage_status", "recommend_delete", "recommendation", "reason",
              "deletable", "delete_kind", "path", "extra_paths", "source", "log_source"]
    write_csv(plugins_csv, fields, rows_by_type["plugin"])
    write_csv(agents_csv, fields, rows_by_type["agent"])
    write_csv(skills_csv, fields, rows_by_type["skill"])
    write_csv(mcps_csv, fields, rows_by_type["mcp"])
    write_csv(combined_csv, fields, combined_rows)
    write_csv(recommendations_csv, fields, recommendation_rows)

    print(f"tool={tool}")
    print(f"days={args.days}")
    print(f"usage_status={'counted' if usage_known else 'logs_missing'}")
    print(f"log_source={log_source}")
    print(f"plugins={len(rows_by_type['plugin'])}")
    print(f"agents={len(rows_by_type['agent'])}")
    print(f"skills={len(rows_by_type['skill'])}")
    print(f"mcps={len(rows_by_type['mcp'])}")
    print(f"recommended_plugins={count_recommended(rows_by_type['plugin'])}")
    print(f"recommended_agents={count_recommended(rows_by_type['agent'])}")
    print(f"recommended_skills={count_recommended(rows_by_type['skill'])}")
    print(f"recommended_mcps={count_recommended(rows_by_type['mcp'])}")
    print(f"plugins_csv={plugins_csv}")
    print(f"agents_csv={agents_csv}")
    print(f"skills_csv={skills_csv}")
    print(f"mcps_csv={mcps_csv}")
    print(f"combined_csv={combined_csv}")
    print(f"recommended_deletions_csv={recommendations_csv}")
    print("recommendations")
    print("index,type,count,scope,name,path,reason")
    for row in recommendation_rows:
        print(f"{row['index']},{row['type']},{row['count_last_n_days']},"
              f"{row['scope']},{row['name']},{row['path']},{row['reason']}")
    return 0


def delete(args: argparse.Namespace) -> int:
    csv_path = Path(args.csv).expanduser()
    indexes = parse_indexes(args.indexes)
    if not indexes:
        print("No indexes selected.", file=sys.stderr)
        return 2
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        return 2

    selected_rows = read_selected_rows(csv_path, indexes)
    quarantine = Path(args.quarantine_dir).expanduser() / timestamp()
    roots = supported_roots()
    actions: list[tuple[str, dict, Path | None, Path | None]] = []
    mcp_actions: list[tuple[dict, Path, list[str] | int]] = []
    refused: list[str] = []

    for row in selected_rows:
        row_id = f"{row.get('index')} {row.get('type')} {row.get('name')}"
        reason = should_refuse_row(row)
        if reason:
            refused.append(f"{row_id}: {reason}")
            continue

        item_type = row.get("type", "")
        if item_type in {"plugin", "agent", "skill"}:
            path, error = validate_path_row(row, roots.get(item_type, []))
            if error or path is None:
                refused.append(f"{row_id}: {error}")
                continue
            destination = safe_destination(quarantine, row.get("scope", "unknown"), path)
            actions.append((item_type, row, path, destination))
            if item_type == "agent":
                for extra_text in row.get("extra_paths", "").split("|"):
                    if not extra_text:
                        continue
                    extra_path = Path(extra_text).expanduser()
                    if not extra_path.exists():
                        continue
                    if not any(validate_path_row({"path": str(extra_path)}, roots["agent"])[0] is not None for _ in [1]):
                        from ._shared import is_under
                        if not any(is_under(extra_path, root) for root in roots["agent"]):
                            refused.append(f"{row_id}: extra path outside supported roots: {extra_path}")
                            continue
                    actions.append((item_type, row, extra_path, safe_destination(quarantine, row.get("scope", "unknown"), extra_path)))
            continue

        if item_type == "mcp":
            import json
            source_text = row.get("source", "")
            source = Path(source_text).expanduser()
            if not source.exists():
                refused.append(f"{row_id}: source config not found")
                continue
            delete_kind = row.get("delete_kind", "")
            if delete_kind == "mcp-config":
                from ._codex import codex_mcp_sections
                lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
                _, removed_sections = codex_mcp_sections(lines, row.get("name", ""))
                if not removed_sections:
                    refused.append(f"{row_id}: MCP TOML sections not found")
                    continue
                mcp_actions.append((row, source, [section for _, section in removed_sections]))
            elif delete_kind == "mcp-json":
                try:
                    data = json.loads(source.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    refused.append(f"{row_id}: cannot read JSON config: {exc}")
                    continue
                _, removed_count = remove_mcp_from_json(data, row.get("name", ""))
                if removed_count == 0:
                    refused.append(f"{row_id}: MCP JSON key not found")
                    continue
                mcp_actions.append((row, source, removed_count))
            else:
                refused.append(f"{row_id}: unsupported MCP delete kind")
            continue

        refused.append(f"{row_id}: unsupported type")

    print("planned_actions")
    for item_type, row, path, destination in actions:
        verb = "delete" if args.mode == "delete" else "move"
        print(f"{row.get('index')},{verb},{item_type},{row.get('name')},{path},{destination}")
    for row, source, details in mcp_actions:
        print(f"{row.get('index')},edit_config,mcp,{row.get('name')},{source},{details}")

    if refused:
        print("refused")
        for item in refused:
            print(item)

    if not args.apply:
        print("dry_run=true")
        return 0 if actions or mcp_actions else 1

    import json
    for item_type, row, path, destination in actions:
        assert path is not None
        assert destination is not None
        if args.mode == "delete":
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(destination))

    for row, source, _details in mcp_actions:
        backup = quarantine / "mcp-config-backups" / f"{source.name}.{timestamp()}.bak"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
        if row.get("delete_kind") == "mcp-config":
            from ._codex import codex_mcp_sections
            lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
            kept, _ = codex_mcp_sections(lines, row.get("name", ""))
            source.write_text("".join(kept), encoding="utf-8")
            print(f"backup={backup}")
        elif row.get("delete_kind") == "mcp-json":
            data = json.loads(source.read_text(encoding="utf-8"))
            new_data, _ = remove_mcp_from_json(data, row.get("name", ""))
            source.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"backup={backup}")

    print("applied=true")
    if args.mode != "delete":
        print(f"quarantine={quarantine}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit AI toolchain Plugin, Agent, SKILL, and MCP usage.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Generate asset CSV reports and cleanup recommendations.")
    audit_parser.add_argument("--tool", choices=["auto", "codex", "claude"], default="auto")
    audit_parser.add_argument("--days", type=int, default=30)
    audit_parser.add_argument("--today", help="Override current date as YYYY-MM-DD for deterministic windows.")
    audit_parser.add_argument("--output-dir", default="/tmp/ai-tool-auditor")
    audit_parser.add_argument("--max-log-bytes", type=int)
    audit_parser.add_argument("--max-log-files", type=int)
    audit_parser.set_defaults(func=audit)

    delete_parser = subparsers.add_parser("delete", help="Preview or apply cleanup for recommended assets.")
    delete_parser.add_argument("--csv", required=True, help="CSV generated by audit, typically recommended_deletions CSV.")
    delete_parser.add_argument("--indexes", required=True, help="Comma-separated indexes or ranges, e.g. 1,3,5-7.")
    delete_parser.add_argument("--apply", action="store_true", help="Apply the planned cleanup.")
    delete_parser.add_argument("--mode", choices=["trash", "delete"], default="trash")
    delete_parser.add_argument("--quarantine-dir", default="/tmp/ai-tool-auditor-deleted")
    delete_parser.set_defaults(func=delete)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
