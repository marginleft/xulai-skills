# Channel-Specific Promo Copy

## X

I published a small but practical GitHub repo for reusable AI-agent skills:

`Xulai Skills`

First skill: `ai-tool-auditor`

It inventories local Codex / Claude Code assets, counts recent usage from logs, exports CSVs, and forces a preview-before-apply cleanup flow.

Useful if your local agent setup is getting crowded with plugins, skills, agents, prompts, and MCP configs.

Repo:
https://github.com/marginleft/xulai-skills

## GitHub Discussion

I just open-sourced a small repo called `Xulai Skills`.

The first skill in it is `ai-tool-auditor`, built for people who use Codex or Claude Code heavily and eventually lose track of what is actually installed and still being used locally.

What it does:

- inventories plugins, agents, skills, and MCP entries
- counts recent usage from logs
- exports CSV reports
- recommends low-risk cleanup candidates
- requires preview before apply

The project is intentionally conservative. It does not assume that "not used recently" means "safe to delete forever." It is meant to help people review their toolchain before cleanup, not blindly automate deletion.

Repo:
https://github.com/marginleft/xulai-skills

If you try it, I would love feedback on what kinds of local AI-tooling maintenance workflows are still missing.

## 掘金

最近我把一个自己真正在用的 Agent Skill 整理后放到 GitHub 了:

`Xulai Skills`

第一个公开出来的 Skill 叫 `ai-tool-auditor`，主要解决一个重度 Agent 用户很容易遇到的问题:

本地装了越来越多 Codex / Claude Code 的 plugin、agent、skill、MCP，想清理，但已经说不清哪些还在用、哪些只是躺着。

这个 Skill 会先做本地盘点，再结合最近日志统计使用情况，输出 CSV 报表和推荐清理项。更关键的是，它默认不是直接删，而是严格走:

`audit -> preview -> confirm -> apply`

也就是说，它更像一个“本地 AI 工具链资产审计和安全清理助手”。

仓库地址:
https://github.com/marginleft/xulai-skills

如果你也在折腾这类 Agent 工作流，欢迎来拍砖，也欢迎顺手点个 star。

## 即刻

把一个我自己挺需要的 Skill 放到 GitHub 了。

场景很简单:

Codex / Claude Code 用久了以后，本地会堆很多 plugin、skill、agent、MCP。想清理的时候，最大的问题不是“怎么删”，而是“我已经不知道哪些还在用”。

所以我做了个 `ai-tool-auditor`:

- 先盘点
- 再看最近使用
- 导出 CSV
- 给推荐清理项
- 删除前必须 preview

仓库在这:
https://github.com/marginleft/xulai-skills

如果你也有类似痛点，欢迎试试，顺手给个 star。
