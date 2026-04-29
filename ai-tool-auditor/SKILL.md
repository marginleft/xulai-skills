---
name: ai-tool-auditor
description: Audit the local AI toolchain inventory and recent usage for Plugin, Agent, SKILL, and MCP assets. Use when the user enters /audit, asks to audit installed AI tools, wants CSV reports for plugins/agents/skills/MCP servers, asks for cleanup recommendations, or confirms deletion of recommended toolchain assets in Codex or Claude Code.
---

# AI Tool Auditor

Audit the current agent toolchain across Plugin, Agent, SKILL, and MCP assets. Generate separate CSV reports for each asset type, recommend safe cleanup candidates, and require an explicit preview before any deletion is applied.

Keep deterministic inventory, usage counting, recommendation, and deletion logic in `scripts/ai_tool_auditor.py`. Use this Skill for orchestration and deletion safety.

## Trigger Handling

Use this Skill when the user enters:
- `/audit`
- `AI工具审计`
- `Plugin盘查`
- `Agent盘查`
- `SKILL盘查`
- `MCP盘查`
- any request to count installed Plugin, Agent, SKILL, or MCP assets
- any request to recommend or confirm cleanup of unused AI toolchain assets

Current tool means:
- Codex: audit `$CODEX_HOME` when set, otherwise `~/.codex`, plus `~/.agents/skills`, Codex plugin roots, Codex plugin cache, Codex agents, Codex prompts, and Codex MCP config.
- Claude Code: audit `~/.claude` (including `~/.claude/plugins/marketplaces/` for available-but-not-installed marketplace assets) and the current project's `.claude/skills`, `.claude/agents`, and `.mcp.json` when present.

## Workflow

### 1. Run the audit

Run from the Skill directory:

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

Use `--tool codex` or `--tool claude` if auto-detection is wrong. The script writes:
- Plugin CSV
- Agent CSV
- SKILL CSV
- MCP CSV
- combined CSV
- recommended deletions CSV

Return the CSV paths, asset counts, and recommendation counts to the user.

### 2. Present recommended deletions

After the audit, show the recommended deletion list grouped by asset type:
- Plugin
- Agent
- SKILL
- MCP

Do not paginate. Show every recommended entry. Add a prominent header section so the user can immediately see the recommendations — do not bury them in metadata output.

**Recommendation basis wording** (use exactly this phrasing, substituting the actual window length):

> 依据：当前 N 天日志窗口未发现使用，并基于该窗口推断后续使用概率较低；这不是确定无价值。

When logs are missing or incomplete, the script marks assets as `manual_review` instead of recommending deletion.

### 3. Preview deletion

When the user confirms one or more recommended entries, use the `index` values from the recommendations CSV or the relevant asset CSV.

Always preview first:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

Preview must show the planned action and any refused entries. For MCP deletion, preview must show the config file and sections or JSON keys that would be modified.

### 4. Apply deletion only after explicit confirmation

Only after the user explicitly confirms the preview, run with `--apply`:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

By default deletion moves files and directories into a timestamped quarantine under `/tmp/ai-tool-auditor-deleted`. Permanent deletion is allowed only when the user explicitly asks for permanent deletion:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply --mode delete
```

## Safety Rules

- Never delete during `audit`.
- Never delete without a successful preview and explicit user confirmation.
- Never recommend deletion when usage logs are missing.
- Never delete an asset with `count_last_n_days > 0`.
- Never delete system Skills under `.system`.
- Never delete plugin cached Skills by default.
- Never recommend or delete the `ai-tool-auditor` Skill itself.
- Never delete plugin cache or bundled runtime plugins by default.
- Never delete anything outside supported roots.
- Treat "0 usage" only as "no usage found in the current log window, with low future usage likelihood inferred from that window." Do not present this as certainty.
- For MCP config cleanup, back up the config file into quarantine before applying edits.

## Output Contract

For `/audit` or equivalent audit requests, respond with:
- detected tool
- Plugin, Agent, SKILL, and MCP CSV paths
- combined CSV path and recommended deletions CSV path
- total installed counts by type
- recommended deletion counts by type
- recommended deletion entries grouped by type, presented in a clear table format
- a brief disclaimer using the exact recommendation basis wording above
- a short note that the user can select recommendation indexes for deletion preview

For deletion requests, respond with:
- preview command result first
- refused entries, if any
- exact quarantine destination or config backup path when applied
- whether the operation was preview-only or applied
