---
name: ai-tool-auditor
description: Audit and safely clean up the local AI agent toolchain in Codex or Claude Code, including plugins, agents, skills, MCP servers/configs, and marketplace assets. Use this whenever the user wants to inventory, count, export CSV for, review recent usage of, recommend cleanup for, preview deletion of, or remove unused local AI tooling; trigger on requests like `/audit`, “盘点/梳理/清理 Codex 或 Claude Code 的插件、skills、agents、MCP”, even if the user never says “audit”. Do not use this for repo dependency audits, npm/pip/package cleanup, or general disk cleanup.
---

# AI Tool Auditor

Audit the current local AI toolchain, generate per-asset CSV reports, recommend low-risk cleanup candidates, and enforce a preview-before-apply deletion flow.

Keep discovery, usage counting, recommendation logic, and deletion behavior in `scripts/ai_tool_auditor.py`. Use this skill to choose the right command, present results clearly, and keep cleanup safe.

## Scope

This skill owns:
- local Codex and Claude Code toolchain inventory
- recent-usage-based cleanup recommendations
- preview and confirmed cleanup for supported assets

Supported asset types:
- plugins
- agents
- skills
- MCP servers and MCP config entries

Typical requests that should trigger this skill:
- `/audit`
- `AI 工具审计`
- `盘点一下我本地装了多少 Codex skills`
- `帮我导出 Claude Code plugins / agents / MCP 的 CSV`
- `看看哪些本地 AI 工具最近没用过`
- `帮我清理没用的 skills 或 MCP`
- `按推荐索引 3,8 先预览删除`

## Do Not Use For

- auditing repo dependencies such as `package.json`, `Podfile`, Gradle, pip, or cargo
- general disk cleanup, duplicate-file cleanup, or cache cleanup unrelated to Codex or Claude Code assets
- installing, upgrading, syncing, or troubleshooting plugins, skills, agents, or MCP servers
- security, compliance, or source-code review work

## Tool Coverage

Current tool means:
- Codex: audit `$CODEX_HOME` when set, otherwise `~/.codex`, plus `~/.agents/skills`, Codex plugin roots, Codex plugin cache, Codex agents, Codex prompts, and Codex MCP config.
- Claude Code: audit `~/.claude`, including `~/.claude/plugins/marketplaces/` for available-but-not-installed marketplace assets, plus the current project's `.claude/skills`, `.claude/agents`, and `.mcp.json` when present.

## Default Behavior

- If the request mixes inventory and cleanup, start with `audit`.
- If the user names `codex` or `claude`, pass `--tool` explicitly.
- If the user specifies a time window, use it; otherwise default to 30 days.
- Never jump straight to deletion, even if the user asks to clean up "unused" items. Generate or use a CSV, then preview, then wait for explicit confirmation.

## Workflow

### 1. Run the audit

Run from the skill directory:

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

Adjust as needed:
- use `--tool codex` or `--tool claude` if auto-detection is wrong or the user asked for a specific toolchain
- use `--days N` when the user provides a different window

The script writes:
- plugin CSV
- agent CSV
- skill CSV
- MCP CSV
- combined CSV
- recommended deletions CSV

Return the CSV paths, installed counts, recommendation counts, and the detected tool.

### 2. Present the recommendations

After the audit, show the recommended deletion list grouped by:
- plugin
- agent
- skill
- MCP

Do not paginate or bury the recommendations in metadata. Put them near the top so the user can act on them quickly.

Use this exact disclaimer, substituting the actual window length:

> 依据：当前 N 天日志窗口未发现使用，并基于该窗口推断后续使用概率较低；这不是确定无价值。

If logs are missing or incomplete, explain that those entries require manual review rather than deletion.

### 3. Preview cleanup

When the user confirms one or more entries, use the `index` values from the recommendations CSV or the relevant asset CSV.

Always preview first:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

Preview must show:
- planned actions
- refused entries, if any
- for MCP cleanup, the config file and the sections or JSON keys that would change

### 4. Apply cleanup only after explicit confirmation

Only after the user explicitly approves the preview, apply it:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

Default mode moves files and directories into a timestamped quarantine under `/tmp/ai-tool-auditor-deleted`.

Permanent deletion is allowed only when the user explicitly asks for it:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply --mode delete
```

## Safety Rules

- Never delete during `audit`.
- Never delete without a successful preview and explicit user confirmation.
- Never recommend deletion when usage logs are missing; report manual review instead.
- Never delete an asset with `count_last_n_days > 0`.
- Never delete system skills under `.system`.
- Never delete plugin-cached skills by default.
- Never recommend or delete the `ai-tool-auditor` skill itself.
- Never delete plugin cache or bundled runtime plugins by default.
- Never delete anything outside supported roots.
- Treat "0 usage" as "no usage found in the current log window," not proof of no value.
- For MCP config cleanup, back up the config file into quarantine before applying edits.

## Output Contract

For `/audit` or equivalent requests, respond with:
- detected tool
- plugin, agent, skill, and MCP CSV paths
- combined CSV path and recommended deletions CSV path
- installed counts by type
- recommended deletion counts by type
- recommended entries grouped by type in a clear table
- the exact recommendation disclaimer above
- a short note that the user can choose indexes for preview

For cleanup requests, respond with:
- preview result first
- refused entries, if any
- exact quarantine destination or config backup path when applied
- whether the operation was preview-only or applied
