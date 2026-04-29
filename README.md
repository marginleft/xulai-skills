<div align="center">

# Xulai Skills

#### 为 Codex / Claude Code 准备的可复用 AI Skills 仓库

[![GitHub stars](https://img.shields.io/github/stars/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/stargazers)
[![GitHub release](https://img.shields.io/github/v/release/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/releases)
[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#skills)

![Codex](https://img.shields.io/badge/Codex-Compatible-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Safety First](https://img.shields.io/badge/Cleanup-Preview_First-2563EB?style=flat-square)

</div>

`Xulai Skills` 目前主打一个高实用性的 Skill: `ai-tool-auditor`。  
它不是再造一个“万能提示词合集”，而是解决一个很具体的问题:

**当你给 Codex / Claude Code 装了越来越多 plugin、agent、skill、MCP 之后，如何先盘点清楚，再安全清理。**

> English summary: `Xulai Skills` is a GitHub-first collection of reusable AI agent skills. The first skill, `ai-tool-auditor`, inventories local Codex / Claude Code assets, counts recent usage from logs, exports CSV reports, and enforces a preview-before-apply cleanup workflow.

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

安装后重启你的 Agent，然后直接这样用:

- `/audit`
- `盘点一下我本地装了多少 Codex skills`
- `帮我导出 Claude Code plugins / agents / MCP 的 CSV`
- `看看哪些 AI 工具最近没用过`
- `按推荐索引 3,8 先预览删除`

## Why This Repo Is Worth Starring

- 解决的是重度 Agent 用户很常见、但很少有人认真做的“本地工具链治理”问题
- 默认偏安全: `audit -> preview -> confirm -> apply`
- 同时覆盖 `Codex` 和 `Claude Code`
- 不是只给一句建议，而是真的生成 `CSV` 和清理候选
- 对“0 usage”保持克制，不把“当前窗口没看到使用”误写成“永远没价值”

## What `ai-tool-auditor` Does

它会审计本地 AI 工具链资产，并把结果整理成能行动的输出。

支持资产类型:

- Plugin
- Agent
- Skill
- MCP server / MCP config

支持能力:

- 盘点本地安装情况
- 统计最近使用情况
- 导出多份 CSV 报表
- 生成低风险清理建议
- 删除前先 preview
- 确认后再 apply

## 30-Second Example

下面是一份真实运行过的审计结果摘要:

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

它还会输出:

- `plugins.csv`
- `agents.csv`
- `skills.csv`
- `mcps.csv`
- `combined.csv`
- `recommended_deletions.csv`

你可以把它理解成:

**本地 AI 工具链资产台账 + 最近使用视角 + 安全清理候选清单**

## Why It Exists

很多人都会遇到这个阶段:

- 装了一堆 plugin、skill、agent、MCP
- 当时觉得“以后会用”
- 用久以后，已经不记得哪些真的在用
- 想清理，但又怕误删

`ai-tool-auditor` 就是为这个阶段准备的。

它的目标不是“帮你删快一点”，而是:

**先让你知道自己到底装了什么，再决定删什么。**

## Safety Boundaries

这个 Skill 的设计重点不是“删得快”，而是“删得明白”。

- `audit` 阶段绝不删除
- 没有 preview 不删除
- 没有明确确认不删除
- 当前日志窗口内有使用记录的不删
- `.system` 下的系统 skills 不删
- plugin cache 和 bundled runtime plugins 默认不删
- MCP 配置修改前会先备份

它对推荐结果的解释也很克制:

> 当前窗口内未发现使用，不等于永远没价值。

## Default Workflow

默认流程如下:

1. `audit`
2. 生成 Plugin / Agent / Skill / MCP 的 CSV
3. 输出推荐清理项
4. 选择若干索引，先做 preview
5. 只有你明确确认后，才 apply

默认命令示例:

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

删除预览示例:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

确认执行示例:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

永久删除只有在你明确要求时才应该使用:

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply --mode delete
```

## Repo Layout

```text
xulai-skills/
├── LICENSE
├── README.md
├── assets/
│   ├── ai-tool-auditor-demo.gif
│   └── social-preview.jpg
├── docs/
│   ├── marketing/
│   └── releases/
├── scripts/
│   └── render_marketing_assets.sh
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

审计本地 Plugin / Agent / Skill / MCP 资产，导出 CSV 报表，并给出带 preview-confirm 流程的安全清理建议。

适合这些请求:

- `/audit`
- `AI 工具审计`
- `盘点一下我本地装了多少 Codex skills`
- `帮我导出 Claude Code plugins / agents / MCP 的 CSV`
- `看看哪些本地 AI 工具最近没用过`
- `帮我清理没用的 skills 或 MCP`

## Release Notes And Promo Copy

仓库里已经附带:

- [v0.1.0 release notes](./docs/releases/v0.1.0.md)
- [中文分发文案](./docs/marketing/launch-zh.md)
- [English launch copy](./docs/marketing/launch-en.md)
- [渠道版文案](./docs/marketing/channels.md)

## License

本仓库使用 [MIT License](./LICENSE)。
