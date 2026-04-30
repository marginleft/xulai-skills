<div align="center">

[中文](./README.md) | [English](./README.en.md)

# Xulai Skills

#### 为 Codex / Claude Code 准备的高信号、可复用 AI Skills 仓库

[![GitHub stars](https://img.shields.io/github/stars/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/stargazers)
[![GitHub release](https://img.shields.io/github/v/release/marginleft/xulai-skills?style=for-the-badge)](https://github.com/marginleft/xulai-skills/releases)
[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-2-10B981?style=for-the-badge)](#skills)

![Codex](https://img.shields.io/badge/Codex-Compatible-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Workflow First](https://img.shields.io/badge/Workflow-Reusable-2563EB?style=flat-square)

</div>

`Xulai Skills` 是一个面向 `Codex` 和 `Claude Code` 的实用型 AI Skills 仓库。这里收录的不是泛泛的提示词堆砌，而是可以直接进入真实工作流、能复用、能落地、边界清楚的技能模块。

当前仓库公开了 2 个 Skills：

- [`ai-tool-auditor`](./ai-tool-auditor/SKILL.md): 审计并安全清理本地 AI 工具链资产
- [`prompt-optimization`](./prompt-optimization/SKILL.md): 把模糊请求重写成稳定、可复用、可验证的高质量 Prompt

> 如果这个仓库帮你省下了时间，欢迎点一个 Star。它会直接帮助更多重度 Agent 用户发现这些可以马上开工的 Skills。

## 为什么值得关注

- 面向真实问题：解决的是 Agent 工作流里的重复劳动，不是演示型样例
- 直接可用：每个 Skill 都带有清晰职责、触发条件、工作流和输出约束
- 中英双语：仓库首页与说明对中英文使用者都友好
- 强调边界：能做什么、不能做什么、信息不足时怎么办，都写清楚
- 适合复用：既能给个人用，也适合团队沉淀为内部工作流资产

## Skills

| Skill | 解决什么问题 | 适合场景 | 关键价值 |
|------|------|------|------|
| [`ai-tool-auditor`](./ai-tool-auditor/SKILL.md) | 本地插件、agents、skills、MCP 越装越多，想盘点又不敢乱删 | Codex / Claude Code 重度用户 | 审计、CSV 导出、保守型清理建议、preview-before-apply |
| [`prompt-optimization`](./prompt-optimization/SKILL.md) | Prompt 太模糊、输出不稳定、复用性差 | 想把自然语言请求整理成高质量 AI 指令的人 | 诊断问题、结构化重写、明确输出格式、保留原意 |

## 先用哪个

如果你想处理本地 AI 工具链治理问题，用 `ai-tool-auditor`。

如果你想把一句“说得不够准的话”改造成一个稳定可复用的 Prompt，用 `prompt-optimization`。

## 快速安装

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

安装后重启 Agent，然后直接用自然语言触发即可。

## `ai-tool-auditor`

`ai-tool-auditor` 用来审计当前本地 AI 工具链，并把结果变成可以立刻行动的输出。

它适合这些请求：

- `/audit`
- `盘点一下我本地装了多少 Codex skills`
- `帮我导出 Claude Code plugins / agents / MCP 的 CSV`
- `看看哪些 AI 工具最近没用过`
- `按推荐索引 3,8 先预览删除`

它的核心能力：

- 盘点本地 Plugin / Agent / Skill / MCP 资产
- 统计最近使用情况
- 导出多份 CSV 报表
- 生成低风险清理建议
- 删除前必须先 preview
- 只有明确确认后才 apply

默认工作流：

1. 先运行 `audit`
2. 生成 Plugin / Agent / Skill / MCP 的 CSV
3. 查看推荐清理项
4. 对指定索引先做 preview
5. 明确确认后才 apply

审计示例：

```bash
python3 scripts/ai_tool_auditor.py audit --tool auto --days 30
```

预览清理：

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8
```

确认执行：

```bash
python3 scripts/ai_tool_auditor.py delete --csv /path/to/recommended_deletions.csv --indexes 3,8 --apply
```

## `prompt-optimization`

`prompt-optimization` 用来把模糊意图整理成更稳定、更容易复用的 Prompt。它优化的重点不是“文案更花哨”，而是让模型更容易产出一致结果。

它适合这些请求：

- `优化这个 prompt`
- `帮我把这句话整理成给 AI 的指令`
- `这个 prompt 不够好，帮我改得更准`
- `怎么问会更准`
- `帮我写一个结构化 prompt`

它的工作方式：

1. 先诊断最关键的 2 到 3 个问题
2. 再按 `任务 / 背景 / 输入 / 要求 / 输出格式 / 信息不足时` 等结构重写
3. 对复杂任务补充工作流、校验点和失败处理
4. 在信息缺失时做最小合理假设，而不是卡住或乱猜

它特别适合解决这些常见问题：

- 任务太模糊，模型不知道主任务是什么
- 范围没收住，回答忽长忽短
- 没有输出格式，结果每次都长得不一样
- 一个请求里掺了多个目标，导致输出发散
- 缺少受众和上下文，语气、深度、假设容易漂移

简单任务常用结构：

```text
任务：
背景：
输入：
要求：
输出格式：
信息不足时：
```

复杂任务常用结构：

```text
角色：
目标：
背景/上下文：
输入材料：
工作流：
约束：
输出格式：
校验点：
信息不足时：
```

它最终返回的重点通常包括：

- 一个可以直接复制使用的优化后 Prompt
- 3 到 5 条高价值优化说明
- 缺失信息、默认假设和待补充项

## 为什么这类 Skill 容易被持续使用

- 不是只给一段答案，而是沉淀成可复用工作流
- 有边界和失败处理，适合长期放进 Agent 环境
- 同时兼顾“第一次使用”和“后续重复调用”
- 既能解决当前问题，也能帮你把团队经验产品化

## 仓库结构

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

- 持续增加面向真实工作流的高复用 Skills
- 补充更多使用示例和演示素材
- 优化安装体验和仓库导航
- 欢迎围绕高价值 Agent 工作流提交 Issue 或 PR

## License

本仓库使用 [MIT License](./LICENSE)。
