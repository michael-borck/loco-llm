---
title: "RE2 (Re-Reading) on Qwen3-4B"
description: Does instructing the model to re-read the question before answering measurably help Qwen3-4B at Q4_K_M? An empirical study, planned.
---

**Status:** `planned`

## Claim under test

[RE2 (Re-Reading)](https://arxiv.org/abs/2309.06275), proposed by Xu et al. 2023, prepends a re-read instruction to the prompt:

> [Question]. Read the question again: [Question]. Now answer.

The published claim is that RE2 reduces errors caused by the model misreading or partially processing the input on the first pass, particularly when the model's first-pass attention misses important constraints.

## Hypothesis on small models

We expect RE2 to help Qwen3-4B *more* than it helps frontier models, for three reasons:

- **Smaller attention budgets** — fewer attention heads and layers; more likely to miss content on a single pass.
- **Tighter effective context** — re-reading is cheap when the question is short relative to the model's context window.
- **Asymmetric cost** — the technique cost (extra input tokens) is borne by both small and large models equally; the gain on small models should be larger.

We expect the effect to be largest on:

- Multi-constraint questions (e.g., "summarise X, but only the parts relevant to Y, in fewer than Z words")
- Word problems (maths, logic) where attention to detail matters
- Negation and edge cases ("which of these is *not* true...?")

We expect the effect to be smallest or absent on:

- Free-form generation (creative writing, brainstorming)
- Tasks where the answer is dictated by the first content words, regardless of subsequent constraints

## Methodology

(Draft — to be refined before running.)

- **Base model:** Qwen3-4B-Instruct at Q4_K_M (LocoLLM standard, per [ADR-0001](../adr/0001-base-model-qwen3-4b.md) and [ADR-0006](../adr/0006-gguf-ollama-inference-standard.md))
- **Comparison run:** Llama 3.1 8B Instruct at Q4_K_M, on a sub-sample, to test the asymmetric-effect hypothesis
- **Task suite:** *TBD.* Candidates:
  - A slice of MMLU (multi-choice with negation/constraint variants)
  - A slice of GSM8K (multi-step word problems)
  - A small constructed multi-constraint extraction set (closer to LocoLLM real use)
- **Sample count:** sized for a 95% CI on accuracy difference of ±2 percentage points (~600 items per condition, depending on baseline accuracy)
- **Sampling:** `temperature=0` for the primary run; an `N=5` rerun at `temperature=0.3` to characterise variance
- **Conditions:**
  - **Baseline** — plain prompt
  - **RE2** — baseline prompt with the re-read prefix and "Now answer" suffix
- **Pass criterion per item:** task-specific (exact match for multi-choice; numeric match for GSM8K; rubric-graded by a frozen judge model for the constructed set, with judge variance characterised separately)

## Results

*Pending. This page will be updated when the study runs.*

## Limitations (declared in advance)

- **Single base model in the primary condition.** The effect on Llama 3.2 3B, Phi-3 Mini, or other 3-4B models may differ.
- **Quantisation level fixed at Q4_K_M.** Effect may differ at Q8 or F16; not tested in this study.
- **A judge-model pass criterion** introduces a second source of variance and is avoided where possible. Where used, judge variance is reported alongside the primary effect.
- **"Reasoning" is a broad category.** Results on the chosen task suite do not generalise automatically to all reasoning tasks.
- **No interaction effects with adapters.** This study uses the base model only. Whether RE2 stacks with a math adapter, code adapter, or routing setup is a separate study.

## Invalidation condition

If RE2 produces an accuracy improvement of less than 1 percentage point on the chosen task suite, with overlapping 95% confidence intervals between baseline and RE2, the claim that RE2 reliably helps Qwen3-4B is not supported by this evidence.

If the effect is positive on Qwen3-4B but equal-or-larger on Llama 3.1 8B in the comparison run, the asymmetric-effect hypothesis is not supported (the technique helps, but not preferentially on small models).

## Practitioner takeaway (provisional)

Until results land, the [Small Model Strategies](../small-model-strategies.md) summary stands: RE2 is cheap, plausibly helps, and is worth using on questions with multiple constraints. This study will refine that summary with measurement.

## Cross-references

- [Small Model Strategies §2: Prompting Strategies](../small-model-strategies.md#2-prompting-strategies)
- [Scaffolding Studies index](index.md)
- [RE2 (general-audience version)](https://github.com/michael-borck/the-ai-skills-passport) — `ai-toolkit/downloads/re2-prompting.qmd` in the AI Skills Passport
