---
title: "Nvidia GPU Generations -- An AI Inference Perspective"
---

A reference for understanding Nvidia's consumer GPU lineup through the lens of local LLM inference rather than gaming performance. The two use cases share hardware but reward different specifications.

---

## What Actually Matters for LLM Inference

Before the tables, the metrics worth understanding:

**Memory bandwidth** -- how fast weights move from VRAM to compute units. This is the primary bottleneck for LLM inference. More bandwidth = more tokens per second.

**VRAM** -- how large a model you can load. The hard ceiling. A model that doesn't fit in VRAM doesn't run (or runs agonisingly slowly via system RAM offload).

**Tensor Cores** -- dedicated hardware for mixed-precision matrix operations. Enable QLoRA fine-tuning and accelerate inference on supported frameworks. Arrived with Turing (RTX 2000 series). Absent from GTX cards including the GTX 1600 series.

**CUDA Compute Capability** -- the version floor that frameworks require. Modern tools (bitsandbytes, Unsloth, some quantisation kernels) require 6.0+. Anything below Pascal is effectively unsupported.

**CUDA Core count** -- largely irrelevant for inference. Matters for gaming and rendering. Don't optimise for this.

---

## Pre-Pascal (600, 700, 900 Series) -- Not Relevant

Kepler (600/700 series) and Maxwell (900 series) predate the compute capability floor that modern AI frameworks require. Kepler sits at compute 3.x, Maxwell at 5.x. Tools like bitsandbytes, Unsloth, and current quantisation kernels require 6.0 minimum. Even where drivers technically work, these cards are effectively unsupported and will become more so as frameworks move forward.

Maxwell also has no Tensor Cores and GDDR5 memory bandwidth that makes inference impractically slow on anything larger than small 3B models. The GTX 980 Ti's 336 GB/s and 6 GB GDDR5 might look interesting on paper but the architecture ceiling makes it a dead end.

If you own one of these cards it will run Ollama in a pinch. It is not worth acquiring for this purpose.

---

## GTX 1000 Series -- Pascal (2016--2017)

Compute capability 6.x. No Tensor Cores. Still functional for inference but heading toward framework deprecation. The floor for anything worth running today.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| GTX 1050 Ti | 4 GB GDDR5 | 112 GB/s | Minimum viable. Runs Q4 3B-4B models. Reference floor. |
| GTX 1060 6 GB | 6 GB GDDR5 | 192 GB/s | Useful step up from 4 GB. Fits most Q4 7B models. |
| GTX 1070 | 8 GB GDDR5 | 256 GB/s | 8 GB headroom but low bandwidth hurts token speed. |
| GTX 1080 | 8 GB GDDR5X | 320 GB/s | Better bandwidth, still no Tensor Cores. |
| GTX 1080 Ti | 11 GB GDDR5X | 484 GB/s | Interesting: 11 GB and high bandwidth. Aging fast. |
| Titan X Pascal | 12 GB GDDR5X | 480 GB/s | 12 GB VRAM attractive but Pascal lifespan limited. |

**AI sweet spot in this generation:** GTX 1060 6 GB for minimum viable 7B inference. GTX 1080 Ti if you find one cheaply -- the bandwidth still holds up. Everything else is either too little VRAM or too little bandwidth to be worth acquiring now.

---

## GTX 1600 Series -- Turing Without Tensor Cores (2019)

Turing architecture but deliberately stripped of RT Cores and Tensor Cores to protect RTX pricing. Compute capability 7.5. Better efficiency than Pascal, GDDR6 memory on top models.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| GTX 1650 | 4 GB GDDR5/6 | 128/192 GB/s | Budget floor. 75W, no external power. |
| GTX 1650 Super | 4 GB GDDR6 | 192 GB/s | Better than base 1650, same VRAM ceiling. |
| GTX 1660 | 6 GB GDDR5 | 192 GB/s | Fine, but 1660 Super/Ti are better. |
| GTX 1660 Super | 6 GB GDDR6 | 336 GB/s | Big bandwidth jump over base 1660. Good value. |
| GTX 1660 Ti | 6 GB GDDR6 | 288 GB/s | Top of GTX line. Turing efficiency, no Tensor Cores. |

**AI sweet spot in this generation:** GTX 1660 Super -- same VRAM as the Ti but higher bandwidth. The GTX 1660 Ti is the better-known card but the Super edges it on the metric that matters. No Tensor Cores means inference only, no QLoRA training.

**Note on the 1650:** Low power draw and no external connector makes it practical in office machines (Optiplex, ThinkCentre). That's its value, not inference performance.

---

## RTX 2000 Series -- Turing With Tensor Cores (2018--2019)

The RTX brand debut. First generation Tensor Cores enable mixed-precision training and accelerated inference. Compute capability 7.5. The first generation worth considering for QLoRA fine-tuning.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| RTX 2060 | 6 GB GDDR6 | 336 GB/s | Tensor Cores but 6 GB is tight for 7B models. |
| RTX 2060 Super | 8 GB GDDR6 | 448 GB/s | The sleeper. 8 GB + 448 GB/s + Tensor Cores. Excellent value secondhand. |
| RTX 2070 | 8 GB GDDR6 | 448 GB/s | Identical to 2060 Super on inference metrics. |
| RTX 2070 Super | 8 GB GDDR6 | 448 GB/s | Same again. CUDA cores irrelevant for inference. |
| RTX 2080 | 8 GB GDDR6X | 448 GB/s | Minimal gain over 2060 Super for inference. |
| RTX 2080 Super | 8 GB GDDR6X | 496 GB/s | Only meaningful step up in this tier. |
| RTX 2080 Ti | 11 GB GDDR6 | 616 GB/s | Good bandwidth, 11 GB useful. Premium pricing. |
| Titan RTX | 24 GB GDDR6 | 672 GB/s | 24 GB VRAM, high bandwidth. Rare and expensive. |

**AI sweet spot in this generation:** RTX 2060 Super. Punches well above its name and price. Matches the 2070 Super and 2080 on inference-relevant specs while trading on a lower reputation. The 2080 Super is the only card in this range that meaningfully improves on it -- and the price gap rarely justifies the modest bandwidth gain.

---

## RTX 3000 Series -- Ampere (2020--2022)

Second generation Tensor Cores, significant efficiency gains, DLSS 2.0. Compute capability 8.6. The generation where VRAM choices became fragmented -- Nvidia made some unusual decisions.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| RTX 3050 | 8 GB GDDR6 | 224 GB/s | Low bandwidth hurts. Not recommended. |
| RTX 3060 | 12 GB GDDR6 | 360 GB/s | Key card: 12 GB unlocks a larger model tier. Bandwidth lower than 2060 Super. |
| RTX 3060 Ti | 8 GB GDDR6 | 448 GB/s | Faster than 3060 for 8 GB models, less VRAM headroom. |
| RTX 3070 | 8 GB GDDR6 | 448 GB/s | Same bandwidth as 2060 Super, newer architecture. |
| RTX 3070 Ti | 8 GB GDDR6X | 608 GB/s | Meaningful bandwidth step. Still 8 GB ceiling. |
| RTX 3080 10 GB | 10 GB GDDR6X | 760 GB/s | Large bandwidth jump. 10 GB is an awkward VRAM amount. |
| RTX 3080 12 GB | 12 GB GDDR6X | 912 GB/s | Better: 12 GB + near 1 TB/s bandwidth. Strong card. |
| RTX 3090 | 24 GB GDDR6X | 936 GB/s | Prosumer ceiling. 24 GB enables 13B+ models at speed. |
| RTX 3090 Ti | 24 GB GDDR6X | 1008 GB/s | Marginal gain over 3090 at significant cost premium. |

**AI sweet spots in this generation:**

RTX 3060 -- the cheapest path to 12 GB VRAM. Counterintuitively slower than the 2060 Super for models that fit in 8 GB due to lower bandwidth. Its value is entirely in the VRAM headroom.

RTX 3080 12 GB -- if budget allows. Near 1 TB/s bandwidth plus 12 GB VRAM is a genuinely strong combination.

RTX 3090 -- the consumer ceiling worth waiting for. 24 GB VRAM handles 13B models comfortably. Secondhand pricing is elevated while demand from AI workloads keeps it high, but will fall as 40-series supply increases.

---

## RTX 4000 and 5000 Series -- Out of Scope

The 40-series (Ada Lovelace) and 50-series (Blackwell) are current generation hardware. Performance is strong and architecture support will be long. They are not covered here for a simple reason: secondhand pricing remains out of range for a lab built on opportunistic acquisition.

Beyond price, the 40-series made some choices that are counterproductive for this use case. The 4060 and 4060 Ti use a narrow 128-bit memory bus, giving them bandwidth (272 GB/s and 288 GB/s respectively) that is actually lower than a 2060 Super. Nvidia prioritised cache efficiency and power consumption over raw bandwidth -- a reasonable tradeoff for gaming, a poor one for LLM inference. The 4070 and above are more competitive on bandwidth but priced well beyond what secondhand consumer hardware justifies for a small model lab.

The 50-series is too new to have a meaningful secondhand market.

When 40-series cards begin appearing at prices comparable to current 30-series secondhand values -- likely a 12-24 month horizon as 50-series supply normalises -- specific models will be worth revisiting. The 4070 Super (504 GB/s, 12 GB) and 4080 (717 GB/s, 16 GB) are the first cards in that generation worth considering for this use case.

Until then the 30-series, particularly the 3060, 3080 12 GB, and 3090, represents the practical ceiling for this project.

---

## The Counterintuitive Results

A few things this data shows that contradict the obvious assumption that newer = better for AI:

**The 3060 is slower than the 2060 Super** for any model that fits in 8 GB. 360 GB/s vs 448 GB/s. The 3060's only advantage is VRAM capacity.

**The 2060 Super matches the 2070, 2070 Super, and 2080** on every inference-relevant metric. Three generations of naming and pricing separate them; inference performance does not.

**The 1080 Ti's bandwidth (484 GB/s) still competes** with cards released years later. Pascal architecture limits its future, but the raw numbers hold up.

**CUDA core count predicts nothing** about inference speed. The 2080's 2944 cores vs the 2060 Super's 2176 produces identical inference throughput on identical bandwidth.

---

## How Colmena Represents This

Colmena's card selection isn't arbitrary -- each card is the floor of its VRAM tier, not the best available. Conservative baselines mean: if it runs here, it runs on your card. Community submissions extend each tier upward.

| Card in Colmena | VRAM | Bandwidth | Tier Role |
|-----------------|------|-----------|-----------|
| GTX 1050 Ti | 4 GB | 112 GB/s | Floor of 4 GB tier (Pascal, no Tensor Cores) |
| GTX 1060 6 GB | 6 GB | 192 GB/s | Floor of 6 GB tier (Pascal, no Tensor Cores) -- pending acquisition |
| RTX 2060 Super | 8 GB | 448 GB/s | Floor of 8 GB Turing bandwidth (Tensor Cores) |
| RTX 3060 AORUS Elite | 12 GB | 360 GB/s | Floor of 12 GB tier (Ampere, Tensor Cores) |
| RTX 3090 (reserved) | 24 GB | 936 GB/s | Reference ceiling -- not a user recommendation |

Each card answers a different question. The 1050 Ti: can this even run? The 1060: what does 6 GB without Tensor Cores look like? The 2060 Super: what's the practical floor for 8 GB inference? The 3060: what does 12 GB unlock that 8 GB can't do? The 3090: do floor-tier results scale predictably to the consumer VRAM ceiling?

The bandwidth delta within each tier allows readers to extrapolate to their specific card. Colmena runs smol-bench sequentially due to host RAM constraints (8 GB DDR3) -- results are identical to parallel runs, the benchmarks just don't happen simultaneously.

---

*Part of the LocoLLM documentation. For hardware acquisition context see meet-the-lab.md.*
