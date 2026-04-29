# 中文分发文案

我把自己一直想要、但很少见有人认真做的一个 Skill 放到 GitHub 了:

[`ai-tool-auditor`](https://github.com/marginleft/xulai-skills/tree/main/ai-tool-auditor)

它解决的是一个很具体的问题:

当你给 Codex / Claude Code 装了越来越多 plugin、agent、skill、MCP 之后，已经不太记得哪些真的在用，想清理又怕误删。

这个 Skill 会先帮你做 3 件事:

1. 盘点本地 AI 工具链资产
2. 结合最近日志统计使用情况
3. 导出 CSV，并给出低风险清理候选

它默认不是“直接帮你删”，而是严格走:

`audit -> preview -> confirm -> apply`

也就是说，如果你只是想先搞清楚“我到底装了多少东西、最近哪些没用过”，它会很顺手；如果你真的要清理，它也会尽量把风险压低。

目前支持:

- Codex
- Claude Code
- Plugin
- Agent
- Skill
- MCP server / MCP config

这次我把仓库首版整理成了一个独立的 GitHub repo:

`Xulai Skills`

第一项公开出来的 Skill 就是 `ai-tool-auditor`。后面也会继续往里面补更多偏实战、偏高频的技能。

如果你也是重度折腾 Agent / MCP / Skills 的用户，欢迎试试，也欢迎给个 star 帮我验证一下这类工具到底有没有共鸣:

https://github.com/marginleft/xulai-skills
