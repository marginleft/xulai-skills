<div align="center">

[中文](./README.md) | [English](./README.en.md)

# Xulai Skills

#### High-signal, reusable AI skills for Codex and Claude Code

[![GitHub stars](https://img.shields.io/github/stars/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/stargazers)
[![GitHub release](https://img.shields.io/github/v/release/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/releases)
[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-2-10B981?style=for-the-badge)](#skills)

![Codex](https://img.shields.io/badge/Codex-Compatible-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Workflow First](https://img.shields.io/badge/Workflow-Reusable-2563EB?style=flat-square)

</div>

`Xulai Skills` is a practical repository of reusable AI skills for `Codex` and `Claude Code`. The focus here is not generic prompt collections. The focus is workflow-ready skills with clear triggers, constraints, and outputs that people can actually reuse.

This repository currently includes 2 public skills:

- [`ai-tool-auditor`](./ai-tool-auditor/SKILL.md): audit and safely clean up local AI toolchain assets
- [`prompt-optimization`](./prompt-optimization/SKILL.md): turn vague requests into stable, reusable, verifiable prompts

> If this repo saves you time, a Star helps more Codex and Claude Code users discover it.

## Why Follow This Repo

- Real problems, not demo-only examples
- Reusable workflows instead of one-off answers
- Clear boundaries: what each skill does, does not do, and how it handles missing information
- Bilingual docs that work for both Chinese and English readers
- Useful for individuals today and for team knowledge systems later

## Skills

| Skill | What it solves | Best for | Key value |
|------|------|------|------|
| [`ai-tool-auditor`](./ai-tool-auditor/SKILL.md) | Local plugins, agents, skills, and MCP entries pile up over time, but cleanup feels risky | Heavy Codex / Claude Code users | Audit, CSV exports, conservative cleanup recommendations, preview-before-apply |
| [`prompt-optimization`](./prompt-optimization/SKILL.md) | Prompts are vague, outputs drift, and good requests are hard to reuse | Anyone who wants more reliable AI outputs | Diagnose weak spots, rewrite structure, specify output format, preserve user intent |

## Which Skill Should I Start With

Use `ai-tool-auditor` if you want to govern your local AI toolchain safely.

Use `prompt-optimization` if you want to turn rough natural language into a prompt that produces more consistent results.

## Quick Install

### Codex

```bash
git clone https://github.com/marginleft/xulai-skills.git
mkdir -p ~/.codex/skills
cp -R xulai-skills/ai-tool-auditor ~/.codex/skills/
cp -R xulai-skills/prompt-optimization ~/.codex/skills/
```

### Claude Code

```bash
git clone https://github.com/marginleft/xulai-skills.git
mkdir -p ~/.claude/skills
cp -R xulai-skills/ai-tool-auditor ~/.claude/skills/
cp -R xulai-skills/prompt-optimization ~/.claude/skills/
```

Restart your agent after installation, then trigger the skills with natural-language requests.

## `ai-tool-auditor`

`ai-tool-auditor` audits your local AI toolchain and turns the results into something you can act on immediately.

Typical requests:

- `/audit`
- `Audit my local Codex skills`
- `Export CSVs for Claude Code plugins / agents / MCP`
- `Which AI tools have not been used recently?`
- `Preview deletion for recommended indexes 3,8`

Core capabilities:

- inventory local Plugin / Agent / Skill / MCP assets
- count recent usage
- export multiple CSV reports
- recommend low-risk cleanup candidates
- require preview before deletion
- apply cleanup only after explicit confirmation

Default workflow:

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

Apply cleanup:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

## `prompt-optimization`

`prompt-optimization` turns rough intent into prompts that are clearer, easier to reuse, and more likely to produce consistent model outputs. Its goal is not prettier wording. Its goal is better structure, boundaries, and verifiable results.

Typical requests:

- `Optimize this prompt`
- `Help me turn this sentence into an AI instruction`
- `This prompt is too vague, make it more precise`
- `How should I ask this more clearly?`
- `Write a structured prompt for me`

How it works:

1. Diagnose the highest-value 2 to 3 prompt problems
2. Rewrite using structures like `Task / Context / Input / Constraints / Output Format / When Information Is Missing`
3. Add workflow, checks, and failure handling for more complex tasks
4. Make the smallest reasonable assumption when context is incomplete instead of stalling or guessing wildly

It is especially good at fixing:

- vague task framing
- missing boundaries
- missing output format
- mixed goals inside one request
- missing audience or context

Common structure for simple tasks:

```text
Task:
Context:
Input:
Constraints:
Output Format:
When Information Is Missing:
```

Common structure for more complex tasks:

```text
Role:
Goal:
Background / Context:
Input Materials:
Workflow:
Constraints:
Output Format:
Checks:
When Information Is Missing:
```

Typical output from the skill includes:

- one improved prompt that is ready to use
- 3 to 5 short notes explaining the highest-value improvements
- assumptions, missing context, and next details to add

## Why These Skills Keep Paying Off

- They package repeatable workflows instead of one-time outputs
- They define boundaries and failure handling, which makes them safer to reuse
- They help on the first run and continue to help on repeated runs
- They are useful building blocks for team-level AI workflows

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
├── ai-tool-auditor/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   └── scripts/
│       ├── __main__.py
│       ├── _claude.py
│       ├── _codex.py
│       ├── _shared.py
│       └── ai_tool_auditor.py
└── prompt-optimization/
    └── SKILL.md
```

## Release Notes

- [v0.1.0 release notes](./docs/releases/v0.1.0.md)

## Roadmap

- add more high-signal skills built from real workflows
- publish more examples and demos
- improve installation ergonomics and repo navigation
- welcome issues and PRs around useful agent workflows

## License

This repository is released under the [MIT License](./LICENSE).
