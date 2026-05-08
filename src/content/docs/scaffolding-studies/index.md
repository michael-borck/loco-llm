---
title: "Scaffolding Studies: Does X Help Small Models?"
description: Empirical studies of single-turn scaffolding techniques on the LocoLLM target models. Each technique is tested as a claim with an invalidation condition.
---

[Small Model Strategies](../small-model-strategies.md) is a landscape overview — it surveys the techniques practitioners apply to make small models more useful. This section is the empirical companion: each named technique becomes a claim, each claim gets a study, and each study reports what we measured rather than what the literature implies.

## Why a separate section

The landscape doc says *"RE2 reduces errors caused by the model misreading or partially processing the input on the first pass."* That is a reasonable summary of the published claim. It is not yet a measurement on Qwen3-4B, the LocoLLM standard base model, on tasks of interest to LocoLLM users.

The honest answer to *"does technique X help on a 4B model in 2026?"* is sometimes:

- **Yes, more than it helps frontier models** — the small-model thesis: lower attention budgets and shorter contexts make scaffolding asymmetrically valuable.
- **Yes, but only on specific task families** — narrower than the literature implies.
- **Negligible** — the technique is already absorbed into modern post-training.
- **Slightly negative** — the technique adds tokens without adding signal.

All four answers are useful. None of them are derivable from reading frontier-model papers.

## Methodology

Each study follows the [LocoLab epistemic stance](https://locolabo.org/the-loco-thesis): honest baselines, surfaced uncertainty, status markers. A study includes:

1. **Claim under test** — exactly what the technique is alleged to do, with the citation it comes from.
2. **Hypothesis on small models** — what we expect on Qwen3-4B specifically, and why.
3. **Methodology** — task suite, sample count, sampling parameters, and how the prompt-with-technique differs from the baseline prompt.
4. **Status marker** — `planned` / `running` / `measured` / `published`. Nothing is promoted up the ladder without evidence.
5. **Results** — measured effect with confidence interval. Null and negative results are reported.
6. **Limitations** — what the study does not show.
7. **Invalidation condition** — what evidence would change the claim.

Studies are run on Qwen3-4B-Instruct at Q4_K_M as the canonical configuration (per [ADR-0001](../adr/0001-base-model-qwen3-4b.md) and [ADR-0006](../adr/0006-gguf-ollama-inference-standard.md)). Where useful, a single comparison run against a 7B-class model is included to test whether the small-model effect is asymmetric.

## Studies

| Technique | Origin | Status |
|---|---|---|
| [RE2 (Re-Reading)](re2.md) | [Xu et al. 2023](https://arxiv.org/abs/2309.06275) | `planned` |
| Chain of Thought | [Wei et al. 2022](https://arxiv.org/abs/2201.11903) | `planned` |
| Few-shot example count (zero / one / three / five) | classical | `planned` |
| Structured output (JSON) prompting | community practice | `planned` |
| Prompt chaining (decomposition into sub-tasks) | community practice | `planned` |

Studies appear here once they have at least a draft methodology. They reach `measured` status when the experiment has been run and results recorded. They reach `published` only if the result is written up for an external venue.

## What this is not

- **Not a benchmark suite.** [LocoBench](https://locobench.org) characterises hardware tiers and engines. Scaffolding studies characterise prompt-level interventions on a fixed base.
- **Not a frontier-model replication.** Where a technique has been validated on GPT-4-class models, that is the *prior*; the question here is whether the effect transfers down.
- **Not a critique of the original work.** A null result on Qwen3-4B does not invalidate a finding on a frontier model. It bounds the result's scope.

## Adjacent work

- [Small Model Strategies](../small-model-strategies.md) — narrative landscape this section measures against
- [Adapter Guide](../adapter-guide.md) — when training beats prompting
- [Benchmarking Guide](../benchmarking-guide.md) — broader LocoLLM evaluation infrastructure
- [Evaluation Standards](../evaluation-standards.md) — measurement conventions used across LocoLLM
- The [AI Skills Passport](https://github.com/michael-borck/the-ai-skills-passport) AI Toolkit — general-audience versions of the same techniques (different audience, different framing)
