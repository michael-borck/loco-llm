# Frequently Asked Questions

---

## The Basics

### Why not just give students API credits?

Because dependency on external APIs is the digital divide problem, not the solution. API credits run out. Subscriptions require credit cards. Rate limits throttle usage during assignment deadlines. And when the provider changes pricing, deprecates a model, or goes down, your curriculum breaks.

LocoLLM runs on hardware students already own. No subscription, no credit card, no dependency on any external service. The cost of inference is electricity.

### How is this different from just running Ollama?

Ollama gives you one model. LocoLLM gives you a *system*: a router that classifies your query, selects the best specialist adapter, applies inference enhancements (RE2 prompting, self-consistency voting), and returns a result. You ask a question and the system figures out which specialist should answer it.

Ollama is the engine. LocoLLM is the vehicle.

### Can I use a different base model instead of Qwen3-4B?

Not within the current ecosystem. All adapters target the same base model for a given academic year (see [ADR-0001](adr/0001-base-model-qwen3-4b.md)). This is deliberate: it ensures any adapter works on any LocoLLM installation and students can share work freely.

The base model is re-evaluated annually. If a better option emerges, a new ADR supersedes the current one and adapters are retrained.

---

## Architecture

### How is LocoLLM different from Mixture of Experts (MoE) or RouteLLM?

This is the most important distinction.

Every existing routing system treats the small model as the **floor** and a large model as the **ceiling**. RouteLLM routes easy queries to Llama-8B and hard queries to GPT-4. The optimisation is about minimising how often you need the expensive option. The big model is always there as the safety net.

**LocoLLM has no safety net.** The 4-bit quantized small model is all you have. There is no "escalate to the expensive model." That constraint changes the entire research question:

- RouteLLM asks: *"How often can we avoid using the big model?"*
- LocoLLM asks: *"Can specialisation depth compensate for the total absence of a big model?"*

That is a fundamentally different problem. The closest published work is Predibase's LoRA Land showing task-specific LoRAs on Mistral-7B beating GPT-4, but that is cherry-picked tasks on a 7B model with full cloud resources. LocoLLM asks whether you can do it at 3-4B, quantized to 4-bit, on a laptop, across a broad enough set of domains to be genuinely useful.

### Why call it an "LLM" if the models are small?

The individual models are small (3-4B parameters, 4-bit quantization). Technically they are SLMs. But "LLM" in LocoLLM describes what the ensemble *becomes*, not any single component.

Fifteen specialist adapters behind a router, each tuned to excel in its domain, collectively cover the breadth that only a large language model would normally handle. The "large" part is emergent from collaboration, not from parameter count.

This is the core claim: *large is a property of system design, not model size.* See [Why the Name "LocoLLM"](why-locollm.md#why-the-name-locollm) for more.

### What happens when the model gets it wrong?

The same thing that happens with any AI tool: you notice, because you understood the problem before you asked. This is the [AI Last](why-locollm.md#ai-last-smaller-problems-suit-smaller-models) principle. Students decompose their task, attempt it themselves, and use LocoLLM to augment — not replace — their reasoning.

LocoLLM is explicitly scoped to assist within defined task domains, not to be an oracle. A specialist adapter that is 72% accurate on GSM8K math problems is useful when you are checking your own work, not when you are blindly copying answers.

---

## Research Design

### What makes this a research project and not just a tool?

The tool is the instrument; the research question is whether a *routed swarm of constrained specialists* can match frontier model quality on scoped tasks. That question has not been systematically studied under LocoLLM's specific constraints:

1. **Hard ceiling**: 4-bit quantized small model with no fallback to larger models
2. **Broad coverage**: Not one cherry-picked task, but a growing set of domains
3. **Consumer hardware**: 8GB RAM, no GPU required
4. **Reproducible by anyone**: Every result can be verified on a laptop you can buy for under $200 AUD

The answer — whether positive or negative — is publishable.

### Why accumulate adapters over semesters instead of building everything at once?

Because the research question requires scale that no single team can achieve. One group cannot fine-tune 20 specialist adapters, build evaluation benchmarks for each, and iterate on a router. But five student groups per semester for three years can.

This is a deliberate research strategy, not a staffing convenience. Each semester adds:
- New specialist adapters (expanding domain coverage)
- Competing adapters for existing domains (testing whether different approaches improve the same domain)
- More benchmark data (strengthening evaluation rigour)
- Router improvements (better classification as domains multiply)

The accumulation *is* the experiment. System-level performance over time — measured against frontier models — is the primary result.

### Why are students both building and using the system?

Most MoE and routing research is built by ML engineers for deployment to end users. LocoLLM's student cohorts are simultaneously the development team and the target audience.

This is not just a nice story for a grant application. It means:
- **Evaluation criteria are grounded in real task needs**, not synthetic benchmarks. When a group fine-tunes an adapter for accounting problem formats, it is because they actually need that capability.
- **The feedback loop between builder and user is zero-length.** The person who notices the adapter fails on a certain problem type is the same person who can retrain it.
- **The learning is in the building.** Dependency on external APIs is the digital divide problem. Building your own tools is the pedagogical response.

### Is the adapter registry just a config file?

No. After a few semesters, the registry becomes something that does not really exist anywhere else: a curated, version-controlled collection of task-specific LoRA adapters all trained against the same base model, each with standardised evaluation benchmarks and documented training methodology.

That registry is a research artifact in its own right. Other researchers could use it to:
- Test new routing algorithms against a common adapter set
- Benchmark new quantization methods on established tasks
- Evaluate whether a new base model improves across all domains
- Study how adapter quality evolves over cohorts

The project is not just building a system. It is building a benchmark ecosystem.

---

## Privacy and Compliance

### Is the data really private?

Yes, structurally. Not by policy, by architecture. Nothing leaves the device because nothing *can* leave the device. There is no cloud fallback, no telemetry, no phone-home for hard queries. See [Privacy Is a Structural Choice](why-locollm.md#privacy-is-a-structural-choice) for the full argument.

For Australian university contexts where students work with case studies, client data in business units, or health data in related programs, this is not a nice-to-have. It is a compliance argument that gets stronger as data sovereignty regulation tightens.

---

## Reproducibility

### Can reviewers actually verify the results?

Yes. The entire training and inference pipeline runs on hardware you can buy on eBay for under $200 AUD. If we publish a paper claiming "routed 4-bit specialists on Qwen3-4B achieve X% of GPT-4 performance on these tasks," any reviewer can verify it on their own machine.

Academic ML has a massive reproducibility problem. Papers benchmark on A100 clusters that reviewers cannot access. LocoLLM's constraint — consumer hardware only — is a limitation that doubles as a methodological strength.

The entire training lab — a Ryzen desktop with two RTX 2060 SUPERs, an ex-enterprise IBM server with a P100, and a MacBook M1 for testing — cost well under $1,000 AUD. See [Meet the Lab](meet-the-lab.md) for the full hardware specs.
