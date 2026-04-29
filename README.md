<div align="center">

# Xulai Skills

#### 一个独立维护的 AI Skill 仓库，当前收录 `ai-tool-auditor`

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)

</div>

这个仓库用来存放可直接给 Agent 安装的 Skills。当前只有一个实用工具型 Skill：`ai-tool-auditor`，用于盘查本地 AI 工具链资产，并生成清理建议。

---

## 📦 目录

| 名字 | 一句话 |
|---|---|
| [**ai-tool-auditor**](./ai-tool-auditor/SKILL.md) | 审计本地 Plugin / Agent / SKILL / MCP 资产，导出 CSV 报表，并给出安全的清理建议 |

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

`ai-tool-auditor` 用来审计本地 AI 工具链资产，覆盖：

- Plugin
- Agent
- SKILL
- MCP

它会扫描本地安装情况和最近使用日志，输出多份 CSV 报表，并给出带安全边界的清理建议。删除流程默认先预览，再确认执行；未确认前不会实际删除。

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

更多触发方式、输出约定和安全规则见 [ai-tool-auditor/SKILL.md](./ai-tool-auditor/SKILL.md)。

---

## 📄 License

本仓库使用 [MIT License](./LICENSE)。
