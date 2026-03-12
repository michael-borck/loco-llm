---
title: "Nvidia GPU Generations -- An AI Inference Perspective"
---

A reference for understanding Nvidia's consumer GPU lineup through the lens of local LLM inference rather than gaming performance. The two use cases share hardware but reward different specifications.

This document serves two distinct purposes and it is worth being clear about both upfront.

**For readers choosing hardware:** each generation section identifies the best-in-class card per VRAM tier -- the card that delivers the most inference performance for that memory capacity. These are acquisition targets. If you are buying, this is what you should be aiming for.

**For LocoLLM and Colmena:** the benchmark lab deliberately inverts this. Colmena runs the *worst-in-class* card per VRAM tier -- the floor, not the ceiling. This is a constraint-based research discipline. By benchmarking the slowest representative of each tier, results are honest baselines that readers with better hardware can only improve on. More importantly, it keeps the research focused on optimisation rather than hardware. If a technique only works on a top-tier card, it is not a useful technique for most people. If it works on the floor card, it works everywhere in that tier.

The constraint is intentional. "Just buy a better card" is not a solution. The goal is to find out what is actually achievable within a given VRAM budget, using whatever card represents the worst realistic starting point. That discipline surfaces optimisations that comfortable hardware conceals.

---

## What Actually Matters for LLM Inference

Before the tables, the metrics worth understanding:

**Memory bandwidth** -- how fast weights move from VRAM to compute units. This is the primary bottleneck for LLM inference. More bandwidth = more tokens per second.

**VRAM** -- how large a model you can load. The hard ceiling. A model that doesn't fit in VRAM doesn't run (or runs agonisingly slowly via system RAM offload).

**Tensor Cores** -- dedicated hardware for mixed-precision matrix operations. Enable QLoRA fine-tuning and accelerate inference on supported frameworks. Arrived with Turing (RTX 2000 series). Absent from GTX cards including the GTX 1600 series.

**CUDA Compute Capability** -- the version floor that frameworks require. Ollama's minimum is Compute 5.0 (Maxwell). Modern tools like bitsandbytes, Unsloth, and current quantisation kernels require 6.0+ (Pascal). Cards below Compute 5.0 are unsupported by any current inference framework. Maxwell (5.x) works for basic Ollama inference but is excluded from advanced tooling.

**CUDA Core count** -- largely irrelevant for inference. Matters for gaming and rendering. Don't optimise for this.

---

## Pre-Maxwell (600/700 Kepler Series) -- Not Supported

Kepler (600 series and most 700 series) sits at Compute 3.x. No current inference framework supports it. These cards will not run Ollama, bitsandbytes, or any modern AI tooling. There is no workaround. If you own one, it is not useful for inference.

**Exception within the 700 series:** The GTX 750 and GTX 750 Ti are Maxwell architecture (Compute 5.0) despite carrying a 700 series number. They are covered in the Maxwell section below.

---

## GTX 700 Maxwell / GTX 900 Series -- Maxwell (2014--2016)

The true compute floor for Ollama is Compute 5.0, which means Maxwell qualifies. No Tensor Cores, GDDR5 memory throughout, and bitsandbytes/Unsloth will not run here -- but Ollama does, and that makes these cards legitimate LocoBench data points for the bottom of each VRAM tier.

The GTX 750 Ti is technically a 700 series card but Maxwell architecture, making it the single lowest-compute card that Ollama will use. The 900 series is fully Maxwell.

**Note on the GTX 970:** Avoid for inference. The advertised 4 GB is actually 3.5 GB of full-speed VRAM plus 0.5 GB of slow VRAM accessed via a narrower bus. Models that exceed 3.5 GB will suffer a severe performance cliff. It is not a true 4 GB card.

| Card | VRAM | Memory BW | Compute | AI Notes |
|------|------|-----------|---------|----------|
| GTX 750 Ti | 2 GB GDDR5 | 86 GB/s | 5.0 | True floor. Minimum compute Ollama accepts. TinyLlama only. |
| GTX 950 | 2 GB GDDR5 | 105 GB/s | 5.2 | 2 GB ceiling -- TinyLlama, Phi-2 territory only. |
| GTX 960 2 GB | 2 GB GDDR5 | 112 GB/s | 5.2 | Same VRAM ceiling as 950, slightly more bandwidth. |
| GTX 960 4 GB | 4 GB GDDR5 | 112 GB/s | 5.2 | Floor of 4 GB tier in this generation. Low bandwidth. |
| GTX 970 | 3.5 GB GDDR5 | 196 GB/s | 5.2 | Avoid -- memory architecture defect. Not a true 4 GB card. |
| GTX 980 | 4 GB GDDR5 | 224 GB/s | 5.2 | Better 4 GB option than 960. Twice the bandwidth. |
| GTX 980 Ti | 6 GB GDDR5 | 336 GB/s | 5.2 | Only 6 GB card in this generation. Reasonable bandwidth. |
| GTX Titan X | 12 GB GDDR5 | 336 GB/s | 5.2 | 12 GB VRAM is the headline. Bandwidth modest for the tier. |

**AI sweet spot in this generation:** There isn't one for acquisition purposes. These cards are useful as LocoBench floor representatives -- particularly the GTX 960 4 GB (floor of 4 GB Maxwell), GTX 980 Ti (only 6 GB option), and GTX Titan X (floor of 12 GB tier predating Pascal). The Titan X's 12 GB at $150--200 AUD secondhand is marginal value given Pascal alternatives, but as a benchmark data point for the absolute bandwidth floor of the 12 GB tier it has research utility.

**Colmena relevance:** Maxwell cards are worth acquiring cheaply as tier floor representatives. None should be prioritised over Pascal or later equivalents. If a GTX 960 4 GB or GTX 980 Ti appears for under $30--40 AUD, it rounds out the Maxwell tier data. The Titan X at current secondhand prices ($150--200 AUD) does not represent good value when a Pascal 1080 Ti offers more bandwidth for a similar outlay.

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

**A note on scope:** For a lab focused on small models -- 3B to 13B quantised -- 12 GB is the practical ceiling where new VRAM headroom stops unlocking meaningfully different use cases. The 3060 is the workhorse tier. The 3090 is documented for completeness and to answer the question of whether results scale predictably to larger VRAM, not because 24 GB is necessary for the lab's primary purpose. Everything above 12 GB in this document is reference material, not a recommendation.

---

## RTX 4000 and 5000 Series -- Reference Only

The sections below cover Ada Lovelace (40-series) and Blackwell (50-series). They are included as a reference for bandwidth progression and VRAM tiers, not as acquisition targets for a lab built on opportunistic secondhand purchasing.

Two things make these generations practically out of scope. First, pricing: 40-series secondhand values remain elevated, and 50-series has no meaningful secondhand market at all. Second, and more fundamentally, Nvidia has changed its approach to consumer memory. High-bandwidth GDDR6X and GDDR7 is increasingly allocated to datacenter products, while consumer cards -- particularly in the 60-class -- receive narrower memory buses and lower bandwidth than their predecessors. The 4060 Ti is slower for inference than a 2060 Super from 2019. The 5060 Ti 16 GB launched, sold out, and was quietly designated end of life by major AIB partners within months. This is not an accident; it reflects where Nvidia's memory supply priorities sit.

The 40 and 50 series tables are here so readers with newer hardware can locate themselves in the bandwidth progression and extrapolate from Colmena's floor-card results. They are not recommendations.

---

## RTX 4000 Series -- Ada Lovelace (2022--2024)

Third generation Tensor Cores, DLSS 3, AV1 encode. Compute capability 8.9. The generation where Nvidia made memory bus decisions that directly penalise LLM inference on the lower-end cards -- and introduced 16 GB as a meaningful new VRAM tier at the high end.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| RTX 4060 | 8 GB GDDR6 | 272 GB/s | Narrower bandwidth than a 2060 Super. Not recommended for inference. |
| RTX 4060 Ti 8 GB | 8 GB GDDR6 | 288 GB/s | Same bus problem. Skip unless price is exceptional. |
| RTX 4060 Ti 16 GB | 16 GB GDDR6 | 288 GB/s | The 16 GB VRAM is tempting; the 288 GB/s is not. Slowest path to 16 GB. |
| RTX 4070 | 12 GB GDDR6X | 504 GB/s | Returns to reasonable bandwidth. Solid 12 GB card. |
| RTX 4070 Super | 12 GB GDDR6X | 504 GB/s | Same bandwidth as 4070, slightly more CUDA cores -- irrelevant for inference. |
| RTX 4070 Ti | 12 GB GDDR6X | 504 GB/s | No bandwidth gain over 4070. Premium for gaming features that don't help here. |
| RTX 4070 Ti Super | 16 GB GDDR6X | 672 GB/s | First 16 GB card with meaningful bandwidth. Good inference card at the right price. |
| RTX 4080 | 16 GB GDDR6X | 717 GB/s | Strong 16 GB card. 34% more bandwidth than the 4080 Super's predecessor. |
| RTX 4080 Super | 16 GB GDDR6X | 736 GB/s | Modest step over 4080. Same tier, modest premium. |
| RTX 4090 | 24 GB GDDR6X | 1008 GB/s | Ada ceiling. 24 GB VRAM, 1 TB/s+ bandwidth. Powerful and expensive accordingly. |

**AI sweet spots in this generation:**

RTX 4070 Super -- the lowest Ada card where the bandwidth story holds up. Matches the 3070 Ti on bandwidth while bringing Ada efficiency and longer framework support horizon.

RTX 4070 Ti Super -- opens the 16 GB tier without the bandwidth penalty of the 4060 Ti 16 GB. If 16 GB is the target and budget is flexible, this is the floor to look for.

RTX 4080 / 4080 Super -- the practical 16 GB high watermark for Ada. Not meaningfully different from each other; buy whichever is cheaper.

**What to avoid:** The 4060 and 4060 Ti in any configuration. The 128-bit memory bus makes them slower for inference than cards released years earlier. The 4060 Ti 16 GB is particularly frustrating -- the VRAM is there, the bandwidth is not.

---

## RTX 5000 Series -- Blackwell (2025--)

Fourth generation RT Cores, fifth generation Tensor Cores. GDDR7 memory across the range -- the first consumer generation where the memory technology itself is a step change. Compute capability 10.0. FP4 precision support is new to this generation, with potential benefits for quantised inference as frameworks mature to use it.

The 50-series has no meaningful secondhand market at time of writing. This section is included as a reference for the bandwidth ceiling and VRAM tiers the generation introduces, and for future reference as pricing eventually normalises.

| Card | VRAM | Memory BW | AI Notes |
|------|------|-----------|----------|
| RTX 5070 | 12 GB GDDR7 | 672 GB/s | Same VRAM as 4070, substantially more bandwidth. Matches the 4070 Ti Super. |
| RTX 5070 Ti | 16 GB GDDR7 | 896 GB/s | Strong 16 GB card. Better bandwidth than the 4090 for token generation. |
| RTX 5080 | 16 GB GDDR7 | 960 GB/s | 16 GB at near 1 TB/s. Outperforms the 4090 in token throughput. |
| RTX 5090 | 32 GB GDDR7 | 1792 GB/s | First consumer 32 GB card. 1.79 TB/s -- 77% more than the 4090. |

**AI notes on this generation:**

The bandwidth gains from GDDR7 are real and inference-relevant. The 5090 leads every consumer card on token generation throughput by a meaningful margin. The 5080 at 960 GB/s exceeds the 4090's 1008 GB/s -- near enough to be comparable with the advantage of 16 GB rather than 24 GB.

The 5070's 12 GB VRAM is a missed opportunity. Nvidia held VRAM constant while doubling bandwidth -- a deliberate segmentation decision. For 12 GB workloads it is fast; for 13B+ models it still can't load them.

The 5090's 32 GB tier is genuinely new. No previous consumer card has reached it. It opens 30B-class models in quantised form and enables larger context windows on 13B models that previously fit but ran out of KV-cache headroom.

FP4 inference support lands in this generation but framework maturity lags. As bitsandbytes, llama.cpp, and Unsloth add FP4 kernels, 50-series cards will see throughput gains that 40-series cannot match architecturally. This is the long-term reason to prefer Blackwell, ahead of any near-term secondhand market.

**The 5060 Ti 16 GB situation:** This card launched in April 2025 at around AUD $750-850, with GDDR7 on a 128-bit bus yielding approximately 448 GB/s -- the same as a 2060 Super, but with GDDR7 efficiency gains. It sold quickly and was designated end of life by major AIB partners within months, with Nvidia apparently halting GPU supply to that SKU. Production has shifted to 8 GB variants. The 16 GB version may reappear secondhand but treat any remaining new stock with caution regarding long-term availability of drivers and support. It is a better 16 GB option than the 4060 Ti 16 GB on bandwidth, but the EOL status complicates it as a Colmena acquisition.

---

## The Counterintuitive Results

A few things this data shows that contradict the obvious assumption that newer = better for AI:

**The 3060 is slower than the 2060 Super** for any model that fits in 8 GB. 360 GB/s vs 448 GB/s. The 3060's only advantage is VRAM capacity.

**The 2060 Super matches the 2070, 2070 Super, and 2080** on every inference-relevant metric. Three generations of naming and pricing separate them; inference performance does not.

**The 1080 Ti's bandwidth (484 GB/s) still competes** with cards released years later. Pascal architecture limits its future, but the raw numbers hold up.

**CUDA core count predicts nothing** about inference speed. The 2080's 2944 cores vs the 2060 Super's 2176 produces identical inference throughput on identical bandwidth.

**The 4060 Ti 16 GB is slower than the 2060 Super** despite being four years newer and having twice the VRAM. 288 GB/s vs 448 GB/s. The VRAM is real; the inference performance is not. It is the starkest example of Nvidia's memory bus decisions working against this use case.

**Nvidia is increasingly treating high-bandwidth memory as a datacenter resource.** The pattern across 40 and 50 series consumer cards is narrower buses, lower bandwidth, and deliberate segmentation of VRAM. The 5060 Ti 16 GB being quietly discontinued months after launch is consistent with this. For local inference, the secondhand 30-series market remains better value per GB/s than new consumer hardware in the 60-class.

---

## The Quality Cliff -- A Research Output

Most inference guides recommend a "4 GB minimum" as received wisdom. Colmena will produce the evidence behind that claim by running a fixed evaluation set across every tier in the stack.

The same 15 prompts -- spanning reasoning, factual recall, instruction following, and multi-step tasks -- will be run at every VRAM tier using the best-fit model for that tier at Q4 quantisation. Results will be scored for coherence and accuracy and published as a comparable chart.

The expected finding, and what the data should confirm:

| VRAM | Model | Expected quality |
|------|-------|-----------------|
| 2 GB | TinyLlama 1.1B Q4 | Functional for simple tasks. Reasoning gaps. Narrow use cases. |
| 3 GB | Phi-2 2.7B Q4 | Noticeably better. Still limited on complex reasoning. |
| 4 GB | Phi-3 Mini 3.8B Q4 | Meaningful step up. Usable for most everyday tasks. |
| 6 GB | Qwen2 4B Q4 | Solid general capability. |
| 8 GB | Llama3 8B Q4 | Comfortable general purpose. Most users stop here. |
| 12 GB | Llama3 13B Q4 | Clear quality improvement. Longer coherent context. |
| 24 GB | Llama3 70B Q4 | Ceiling of consumer hardware usefulness. |

The goal is not to confirm the obvious -- it is to show *where* the cliff is steep and where it is gradual. The 2GB to 3GB jump and the 3GB to 4GB jump may tell very different stories. That granularity is what makes running the full tier stack worthwhile.

This data is also relevant to fine-tuned model evaluation. If Burro produces a fine-tuned 1.1B model that outperforms the base Phi-2 2.7B on domain tasks despite running on a 2 GB card, that is a meaningful finding about what fine-tuning can recover at the quality floor.

---

Colmena's card selection isn't arbitrary -- each card is the floor of its VRAM tier, not the best available. Conservative baselines mean: if it runs here, it runs on your card. Community submissions extend each tier upward.

The tier stack deliberately extends down to 2 GB. This is not because 2 GB is a useful inference target -- it isn't -- but because documenting where quality degrades and why is a research output in its own right. Most inference guides assert a "4 GB minimum" without evidence. Colmena will show the data behind that claim.

| Card in Colmena | VRAM | Bandwidth | Status | Tier Role |
|-----------------|------|-----------|--------|-----------|
| GTX 950 | 2 GB | 105 GB/s | Watching | Floor of 2 GB tier (Maxwell). TinyLlama 1.1B only. Quality cliff reference point. |
| GTX 1060 3 GB | 3 GB | 192 GB/s | Watching | Floor of 3 GB tier (Pascal). Phi-2 2.7B territory. Quality cliff reference point. |
| GTX 960 4 GB | 4 GB | 112 GB/s | Watching | Floor of 4 GB tier (Maxwell, Compute 5.2, Ollama only) |
| GTX 980 Ti | 6 GB | 336 GB/s | Watching | Floor of 6 GB Maxwell tier (Ollama only) |
| GTX Titan X | 12 GB | 336 GB/s | Watching | Floor of 12 GB Maxwell tier (Ollama only) |
| GTX 1050 Ti | 4 GB | 112 GB/s | Acquired | Floor of 4 GB tier (Pascal, no Tensor Cores) |
| GTX 1060 6 GB | 6 GB | 192 GB/s | Pending | Floor of 6 GB tier (Pascal, no Tensor Cores) |
| RTX 2060 Super (x3) | 8 GB | 448 GB/s | Acquired | Floor of 8 GB Turing bandwidth (Tensor Cores) |
| RTX 3060 AORUS Elite | 12 GB | 360 GB/s | Acquired | Floor of 12 GB tier (Ampere, Tensor Cores) |
| RTX 3090 | 24 GB | 936 GB/s | Pending | Reference only -- 24 GB scaling data, not a recommendation |
| RTX 4060 Ti 16 GB | 16 GB | 288 GB/s | Pending | Floor of 16 GB tier -- documents the bandwidth penalty, not the ideal |

Three 2060 Supers in the 8 GB tier is intentional. Running identical hardware in parallel validates that LocoBench results are consistent and not an artefact of a single card's condition.

The 4060 Ti 16 GB is acquired as the bandwidth floor of the 16 GB tier precisely because it is the worst representative -- readers with a 4070 Ti Super or 4080 know their card is substantially faster, and the delta is documented clearly. The same logic that makes the 3060 useful despite being slower than the 2060 Super applies here.

The 3090 sits outside the lab's small-model focus. It is included to answer one question: do results from the lower tiers scale predictably when VRAM is no longer the constraint? Once that question is answered, the 24 GB tier has limited ongoing relevance for this project.

The bandwidth delta within each tier allows readers to extrapolate to their specific card. Colmena runs LocoBench sequentially due to host RAM constraints (8 GB DDR3) -- results are identical to parallel runs, the benchmarks just don't happen simultaneously.

---

*Part of the LocoLLM documentation. For hardware acquisition context see meet-the-lab.md.*
