---
name: prompt-optimization
description: Use when the user wants a better prompt rather than direct task completion, including requests to 优化提示词, 优化 prompt, 润色/改写 prompt, 结构化 prompt, 帮我写个 prompt, 提示词优化, prompt 不够好, prompt 太模糊, prompt 不够精确, or when they paste a rough prompt and ask how to improve it. Also use when a vague natural-language ask should be turned into a reusable prompt. Not for cases where the user actually wants the task solved directly.
---

# Prompt Optimization

Turn vague intent into prompts that produce consistent outputs. Optimize for clarity, constraints, decomposition, and verifiable outputs, not ornate wording.

## Core Rules

1. Always return an improved, usable prompt. Do not only critique.
2. Preserve the user's original intent. Do not expand scope unless you label it as an assumption.
3. Do not block on missing information. Make the smallest reasonable assumption, mark it clearly, and still return a usable prompt.
4. If the user actually wants the task solved, solve the task instead of returning a prompt.

## Three-Step Workflow

### Step 1: Diagnose

Identify only the highest-value 2 to 3 prompt problems.

| Problem | Signal | Typical defect |
|---------|--------|----------------|
| Task is vague | `写好一点` `处理一下` | The model does not know what primary job to do |
| Missing boundary | `详细一些` `尽可能多` | No completion bar or scope limit |
| No output format | — | The model can answer in any shape |
| Mixed goals | `顺便也...` | Multiple tasks are tangled together |
| Missing audience/context | — | Tone, depth, and assumptions drift |
| No failure handling | — | The model guesses when inputs are missing |

### Step 2: Rewrite

Choose the lightest prompt shape that fits. Fill only the dimensions that materially improve output quality.

1. `Task`: one primary job, preferably verb-led
2. `Context`: audience, scenario, source boundary
3. `Input`: what materials the model receives
4. `Constraints`: tone, length, exclusions, scope
5. `Workflow`: ordered steps for multi-part tasks
6. `Output Format`: markdown, JSON, table, field order
7. `Quality Bar`: what makes the result acceptable
8. `Failure Handling`: what to do with uncertainty or missing data

Only add `角色` when it meaningfully changes output quality.

### Step 3: Self-check

Before returning the optimized prompt, check:

- Can someone use this prompt without extra explanation?
- Are the constraints observable and testable?
- Is the output format explicit enough to reuse?
- Have vague words been replaced with measurable instructions?
- Does the prompt tell the model what to do when information is missing?

## 中文适配

- Match the user's language by default. For Chinese input, return Simplified Chinese unless the user used Traditional Chinese or asked otherwise.
- Preserve mixed Chinese-English technical terms, product names, API names, file paths, and code identifiers. Do not translate them unless the user asks.
- Prefer Chinese section labels such as `任务` `背景` `输入` `要求` `输出格式` so the result can be copied directly into Chinese workflows.
- Recognize colloquial intents such as `帮我把这句话整理成给 AI 的指令`, `这个 prompt 不够好`, `怎么问会更准`, `改成大模型更容易理解的写法`.
- When the user input is short or口语化, normalize it into clear written Chinese without changing intent.

## 去模糊写法

| Vague wording | Better rewrite |
|---------------|----------------|
| `写好一点` | Replace with explicit quality dimensions |
| `详细一些` | Specify length, sections, or number of points |
| `专业点` | Specify audience and domain depth |
| `自由发挥` | Give a bounded decision space |
| `简单说` | Set an upper limit such as word count or bullet count |

## Prompt Shapes

Use this for simple one-shot tasks:

```text
任务：
背景：
输入：
要求：
输出格式：
信息不足时：
```

Use this for complex, reusable, or high-stakes tasks:

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

## Response Contract

Reply in the user's language by default. For Chinese requests, use Chinese section headings and Chinese explanations unless the user asked for English.

### 优化后的 Prompt

Return one ready-to-use prompt. For reusable asks, you may provide:

- `即用版`
- `结构化复用版`

### 优化说明

Use 3 to 5 short bullets covering the highest-value improvements.

### 建议与待补充

Give only actionable next steps. Prioritize:

- missing audience
- source boundaries
- examples or references
- acceptance criteria
- forbidden content

If assumptions were required, add:

- `默认假设`
- `待补充信息`

## Rules

- Keep the optimized prompt aligned with the user's original intent
- Prefer explicit positive instructions over long lists of prohibitions
- Split multi-goal requests into ordered steps
- Ask the model to state uncertainty instead of guessing
- For programmatic workflows, recommend structured outputs or schemas instead of plain-text formatting requests
- Do not ask clarifying questions unless a missing detail would make the prompt unsafe or unusable
