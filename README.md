<div align="center">

# Xulai Skills

#### 一个独立维护的 AI Skill 仓库，当前收录 `ai-tool-auditor`

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)

</div>

这个仓库用来存放可直接给 Agent 安装的 Skills。当前只有一个偏实用、偏运维的 Skill：`ai-tool-auditor`。

---

## 为什么会有这个 Skill

你是不是也遇到过这种情况：

- 装了一堆 plugin、skill、agent、MCP
- 当时觉得“以后可能会用”
- 用久了以后已经忘了哪些真的在用，哪些只是躺着
- 想清理，但又怕误删真正还需要的东西

`ai-tool-auditor` 就是为这个场景设计的。

它会帮你盘点本地 AI 工具链资产，结合最近使用日志，告诉你：

- 你到底装了多少东西
- 分别是什么类型
- 最近有没有被使用过
- 哪些更像是“当前窗口内未发现使用、后续使用概率较低”的清理候选

它不是“直接帮你暴力删除”的工具，而是一个带安全边界的盘点与清理助手。

---

## 它能做什么

`ai-tool-auditor` 主要覆盖本地 AI 工具链资产的审计与安全清理，支持：

- Plugin
- Agent
- Skill
- MCP server / MCP config

它可以：

- 盘点本地安装情况
- 统计最近使用情况
- 导出多份 CSV 报表
- 生成清理建议
- 先做删除预览，再在你确认后执行清理

它特别适合这些请求：

- `/audit`
- `盘点一下我本地装了多少 Codex skills`
- `帮我导出 Claude Code plugins / agents / MCP 的 CSV`
- `看看哪些 AI 工具最近没用过`
- `帮我清理没用的 skills 或 MCP`
- `按推荐索引 3,8 先预览删除`

---

## 它不做什么

为了避免误用，这个 Skill 不负责：

- `package.json` / `Podfile` / Gradle / pip / cargo 这类项目依赖审计
- 通用磁盘清理、重复文件清理、系统缓存清理
- plugin / skill / agent / MCP 的安装、升级、同步、排障
- 安全审计、源码审查、合规检查

如果你的目标是“清理本地 AI 工具链资产”，它适合。
如果你的目标是“清理项目依赖”或“清理电脑磁盘”，它不适合。

---

## 支持环境

当前支持两类本地环境：

- `Codex`
- `Claude Code`

其中：

- Codex 会审计 `~/.codex`、`~/.agents/skills`、plugin roots、plugin cache、agents、prompts 和 MCP 配置
- Claude Code 会审计 `~/.claude`、marketplace assets，以及当前项目里的 `.claude/skills`、`.claude/agents`、`.mcp.json`

---

## 工作方式

`ai-tool-auditor` 的默认流程是：

1. 先 `audit`
2. 生成 Plugin / Agent / Skill / MCP 的 CSV
3. 输出推荐清理项
4. 如果你选择若干索引，先做 preview
5. 只有你明确确认后，才 apply

这意味着它默认不会因为一句“帮我清理一下”就直接删文件。

默认命令示例：

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

删除预览示例：

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

确认执行示例：

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

永久删除只有在你明确要求时才应该使用：

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply --mode delete
```

---

## 安全边界

这个 Skill 的设计重点不是“删得快”，而是“删得明白”：

- `audit` 阶段绝不删除
- 没有 preview 不删除
- 没有明确确认不删除
- 当前日志窗口内有使用记录的不删
- `.system` 下的系统 skills 不删
- plugin cache 和 bundled runtime plugins 默认不删
- MCP 配置修改前会先备份

另外，它对“0 usage”的解释也很克制：

> 当前窗口内未发现使用，不等于永远没价值。

---

## 输出结果

执行审计后，通常会得到这些文件：

- Plugin CSV
- Agent CSV
- Skill CSV
- MCP CSV
- combined CSV
- recommended deletions CSV

你可以把它当成一份“本地 AI 工具链资产台账 + 清理候选清单”。

---

## 📦 目录

| 名字 | 一句话 |
|---|---|
| [**ai-tool-auditor**](./ai-tool-auditor/SKILL.md) | 审计本地 Plugin / Agent / Skill / MCP 资产，导出 CSV 报表，并给出带预览确认流程的安全清理建议 |

仓库内主要结构：

```text
xulai-skills/
├── LICENSE
├── README.md
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

---

## 📥 安装

发布到 GitHub 后，在支持 Skill 的 Agent 里直接提供 skill 路径即可，例如：

```text
帮我安装这个 skill：https://github.com/marginleft/xulai-skills/tree/main/ai-tool-auditor
```

如果是本地使用，直接把 `ai-tool-auditor/` 目录放到对应 Agent 的 skills 目录即可。

---

## ✨ Skills

### ai-tool-auditor

更多触发方式、范围边界、输出约定和安全规则，见 [ai-tool-auditor/SKILL.md](./ai-tool-auditor/SKILL.md)。

---

## 📄 License

本仓库使用 [MIT License](./LICENSE)。
