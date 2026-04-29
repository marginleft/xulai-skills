<div align="center">

[中文](./README.md) | [English](./README.en.md)

# Xulai Skills

#### Reusable AI agent skills for Codex and Claude Code

[![GitHub stars](https://img.shields.io/github/stars/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/stargazers)
[![GitHub release](https://img.shields.io/github/v/release/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/releases)
[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#skills)

![Codex](https://img.shields.io/badge/Codex-Compatible-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Safety First](https://img.shields.io/badge/Cleanup-Preview_First-2563EB?style=flat-square)

</div>

`Xulai Skills` is a GitHub-first collection of practical, reusable skills for AI coding agents. The first public skill in this repo is `ai-tool-auditor`.

It solves a very specific problem:

**When your local Codex or Claude Code setup fills up with plugins, agents, skills, prompts, and MCP entries, how do you review everything clearly before cleaning it up?**

> Chinese version: [README.md](./README.md)

![AI Tool Auditor Demo](./assets/ai-tool-auditor-demo.gif)

## Quick Install

### Codex

```bash
git clone https://github.com/marginleft/xulai-skills.git
mkdir -p ~/.codex/skills
cp -R xulai-skills/ai-tool-auditor ~/.codex/skills/
```

### Claude Code

```bash
git clone https://github.com/marginleft/xulai-skills.git
mkdir -p ~/.claude/skills
cp -R xulai-skills/ai-tool-auditor ~/.claude/skills/
```

Restart your agent after installation, then try prompts like:

- `/audit`
- `Audit my local Codex skills`
- `Export CSVs for Claude Code plugins / agents / MCP`
- `Which AI tools have not been used recently?`
- `Preview deletion for recommended indexes 3,8`

## Why This Repo Is Worth Starring

- It targets a real maintenance problem for heavy AI-agent users
- It is safety-first by default: `audit -> preview -> confirm -> apply`
- It supports both `Codex` and `Claude Code`
- It produces actionable outputs, not just generic advice
- It treats "no recent usage found" carefully instead of pretending that means "safe forever"

## What `ai-tool-auditor` Does

`ai-tool-auditor` audits your local AI toolchain and turns the results into something you can actually act on.

Supported asset types:

- Plugin
- Agent
- Skill
- MCP server / MCP config

Supported workflows:

- inventory local installations
- count recent usage from logs
- export multiple CSV reports
- recommend low-risk cleanup candidates
- preview deletion before apply
- apply cleanup only after explicit confirmation

## 30-Second Example

Here is a real audit summary from a local Codex environment:

```text
tool=codex
days=30
usage_status=counted
plugins=18
agents=30
skills=177
mcps=4
recommended_plugins=7
recommended_agents=27
recommended_skills=119
recommended_mcps=2
```

The audit also writes:

- `plugins.csv`
- `agents.csv`
- `skills.csv`
- `mcps.csv`
- `combined.csv`
- `recommended_deletions.csv`

In practice, this gives you:

**a local AI toolchain inventory + recent usage view + conservative cleanup shortlist**

## Why It Exists

Most heavy AI-agent users eventually end up here:

- you installed many plugins, skills, agents, and MCP integrations
- some of them were added "just in case"
- after a while, you no longer remember what is still useful
- you want to clean up, but you do not want to delete something important by mistake

`ai-tool-auditor` exists for that exact stage.

The goal is not "delete faster."

The goal is:

**understand your local AI toolchain before you delete anything**

## Safety Boundaries

This skill is optimized for safe cleanup, not aggressive cleanup.

- `audit` never deletes anything
- no preview, no deletion
- no explicit confirmation, no apply
- assets with recent usage in the current log window are not deleted
- system skills under `.system` are not deleted
- plugin cache and bundled runtime plugins are skipped by default
- MCP configs are backed up before modification

Its recommendation language is intentionally conservative:

> No usage found in the current log window does not mean no long-term value.

## Default Workflow

The default flow is:

1. Run `audit`
2. Generate CSVs for plugins, agents, skills, and MCPs
3. Review the recommended cleanup list
4. Preview deletion for selected indexes
5. Apply only after explicit confirmation

Audit example:

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

Preview cleanup:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

Apply cleanup after review:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

Permanent deletion should only be used when you explicitly want it:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply --mode delete
```

## Repo Layout

```text
xulai-skills/
├── LICENSE
├── README.md
├── README.en.md
├── assets/
│   ├── ai-tool-auditor-demo.gif
│   └── social-preview.jpg
├── docs/
│   └── releases/
│       └── v0.1.0.md
└── ai-tool-auditor/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── scripts/
        ├── __main__.py
        ├── _claude.py
        ├── _codex.py
        ├── _shared.py
        └── ai_tool_auditor.py
```

## Skills

### [`ai-tool-auditor`](./ai-tool-auditor/SKILL.md)

Audit local Plugin / Agent / Skill / MCP assets, export CSV reports, and recommend safe cleanup candidates with a preview-confirm workflow.

Typical requests:

- `/audit`
- `Audit my local AI tools`
- `How many Codex skills do I have installed?`
- `Export CSVs for my Claude Code setup`
- `Which local AI tools have not been used recently?`
- `Help me preview cleanup for unused skills or MCP entries`

## Release Notes

- [v0.1.0 release notes](./docs/releases/v0.1.0.md)

## License

This repository is released under the [MIT License](./LICENSE).
