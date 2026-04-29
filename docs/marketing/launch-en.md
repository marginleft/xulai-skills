# English Launch Copy

I just published a small GitHub repo for reusable AI-agent skills:

[`Xulai Skills`](https://github.com/marginleft/xulai-skills)

The first public skill is:

[`ai-tool-auditor`](https://github.com/marginleft/xulai-skills/tree/main/ai-tool-auditor)

It solves a very specific problem:

If you use Codex or Claude Code heavily, your local setup eventually fills up with plugins, agents, skills, prompts, and MCP entries. At some point you want to clean things up, but you no longer remember what is still useful and what is just sitting there.

`ai-tool-auditor` helps with that by:

1. inventorying local AI tool assets
2. counting recent usage from logs
3. exporting CSV reports
4. recommending low-risk cleanup candidates
5. enforcing a preview-before-apply deletion flow

It is intentionally conservative. The goal is not "delete faster." The goal is "understand the local toolchain before you delete anything."

Current scope includes:

- Codex
- Claude Code
- plugins
- agents
- skills
- MCP servers and config entries

If this is a problem you have run into yourself, I would love a star and any feedback on what else should be added next:

https://github.com/marginleft/xulai-skills
