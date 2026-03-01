# Why LocoLLM Exists

This document describes the problem LocoLLM responds to, the assumptions it makes, and the philosophy that shapes its design. It is not a manifesto. It is a practical argument for a specific technical approach, grounded in evidence and experience.

## The Problem Is Access, Not Capability

There is a conversation happening in higher education about how AI will transform learning. It is an important conversation, and it has a blind spot.

In any given tutorial, some students walk in with frontier AI subscriptions and capable hardware. Others are working with whatever free tier they can get on a phone with a prepaid data plan. This is not hypothetical. This is Tuesday.

The gap is structural, not temporary. Students who can afford $20-30 USD per month for a frontier model operate with fundamentally different cognitive tools than those who cannot. The institutional version of the same problem is just as sharp: a well-funded university with a dedicated AI strategy unit operates in a different reality than a regional provider where reliable broadband is still a challenge (Perkins & Roe, 2025). The divide runs through a single country, let alone across the globe.

We have seen this pattern before. The internet, learning management systems, COVID and online learning. Same script every time: early adoption by the well-resourced, defensive reaction by the under-resourced, widening gap dressed up as "digital transformation." The difference this time is speed. Previous technology cycles gave institutions years to catch up. AI capabilities advance quarterly.

LocoLLM is a practical response to this. Not a complete solution. Not a substitute for institutional investment in equitable access. But a working tool that makes AI-assisted learning available to students who would otherwise be excluded from it, running on hardware they already own, at zero ongoing cost.

## Small Models Do Not Need to Beat Frontier Models

The implicit assumption in most AI discourse is that bigger is better. That the only models worth using are the ones with the most parameters, the largest context windows, the highest benchmark scores. This assumption is wrong for most of the tasks that matter in education.

A student brainstorming essay topics does not need GPT-4. A student working through a statistics problem does not need Claude Opus. A student drafting a business plan does not need a model that can process 200,000 tokens of context. They need a model that is good enough to be a useful thinking partner for the specific task in front of them.

"Good enough" is not a compromise. It is a design target. And the evidence supports it: a fine-tuned 4B parameter model matched or exceeded a 120B+ teacher model on 7 of 8 benchmarks in recent testing (distil labs, 2025). A 13B model with majority voting outperformed a 70B model on a single pass (Li et al., 2024). The gap between small specialist and large generalist is narrower than most people assume, and it is closing.

LocoLLM's thesis is not "small models are as good as frontier models." They are not, and pretending otherwise would be dishonest. The thesis is: for well-defined tasks where the model is fine-tuned, prompted well, and given structured context, a 4B model running free on a student's laptop can provide meaningfully useful AI assistance. Not perfect. Useful.

The difference between "no AI access" and "useful AI access" matters far more than the difference between "useful AI access" and "frontier AI access."

## Conversation, Not Delegation

The way LocoLLM is designed to be used matters as much as its technical architecture.

There are two ways to use AI: delegation ("do this for me") and conversation ("think with me"). Delegation develops dependency. You get output without understanding. Over time, you become less capable because you have outsourced the thinking, not just the typing. Conversation builds capability. You learn to ask better questions, spot weaknesses in reasoning, and develop judgement about what is good enough and what needs more work.

This distinction is especially important for small models. A frontier model can sometimes produce a polished final output on the first pass. A smaller model is less likely to. But that is not necessarily a disadvantage in an educational context, because the first-pass output was never the point.

When a student uses LocoLLM to brainstorm approaches to a problem, the model does not need to produce the perfect answer. It needs to produce something worth reacting to. Something the student can push back on, refine, disagree with, and build upon. The conversation is the learning. The iteration is the skill being developed.

A smaller model that requires the student to think critically about its output may actually be pedagogically superior to a frontier model that produces something so polished the student just submits it. This is not a rationalization for inferior technology. It is a recognition that the goal is building human capability, not producing AI output.

Process literacy, knowing how to work with AI effectively rather than just what to ask for, does not require a frontier model. It requires a model that responds, iterates, and engages. A well-tuned 4B model does that.

## AI Last: Smaller Problems Suit Smaller Models

There is a complementary principle that shapes how LocoLLM expects users to work: solve what you can with conventional tools first, then bring AI to the parts you genuinely cannot handle alone.

This is not anti-AI. It is pro-efficiency. Most tasks in a typical workflow have well-understood solutions. Formatting, linting, file organisation, boilerplate structure, simple refactors. These do not need a large language model. They need a competent practitioner using the tools already on their machine.

The practical implication for LocoLLM is significant. If you follow the "AI Last" principle:

- Your problems are already scoped down before the model sees them.
- Your context windows are smaller because you have done the groundwork.
- Your prompts are more focused because you know exactly what you are stuck on.
- Your ability to evaluate the output is stronger because you understand the surrounding work.

This is exactly the usage pattern where small models excel. A 4B model with a 4-8K effective context window is not a limitation if the user brings a well-scoped problem with relevant context. It is only a limitation if the user dumps an entire project and says "fix this."

For code-heavy tasks specifically, the ecosystem already provides powerful non-AI tools for navigating and managing large codebases: grep, ctags, language servers, dependency analysers, linters, test harnesses. These tools are fast, deterministic, and free. The AI model's job is not to replace them. It is to handle the specific cognitive tasks they cannot: explaining unfamiliar patterns, suggesting approaches to novel problems, helping reason through complex interactions. Scoped tasks on small code segments, not whole-repository comprehension.

The "AI Last" workflow and the small model constraint reinforce each other. Users who work this way get better results from small models. Small models that require focused input teach users to work this way. It is a virtuous cycle rather than a compromise.

## Privacy Is a Structural Choice

LocoLLM runs locally. All of it. The model, the adapters, the router, the data. Nothing leaves the user's machine unless they choose to send it somewhere.

This is not primarily a philosophical stance, though the philosophy matters. It is a practical response to real constraints:

- University students produce work that is their intellectual property. Routing it through third-party cloud services creates ambiguity about data ownership, processing, and retention that most students are not equipped to evaluate and most institutions have not resolved.
- Many universities have procurement and data-sovereignty policies that prohibit sending student or academic content to external platforms without formal review. A local-first tool sidesteps this entirely.
- Internet access is not universal, not reliable, and not free. A tool that requires a persistent cloud connection excludes exactly the users who most need access.
- API costs compound. Even modest per-token pricing becomes a barrier when multiplied across a semester of daily use. Local inference after a one-time setup has zero marginal cost.

The BYOK (Bring Your Own Key) model provides an escape valve for users who want cloud model access: they supply their own API keys, the tool calls the provider directly, and we are not a proxy or middleman. But the default path, the one that works for the student with a $300 laptop and no credit card, is fully local.

Privacy in this context is not a feature. It is a structural property of the architecture. The code is open source and auditable. There is no telemetry, no analytics, no call-home. The application functions completely offline when using local models. This is not a policy claim. It is a verifiable technical fact.

## What LocoLLM Actually Provides

Given all of the above, LocoLLM's contribution is not a single breakthrough. It is the integration of several known techniques into a coherent system designed for a specific, underserved population:

**Task-specific fine-tuning** narrows the gap between small and large models on defined tasks. A routed adapter hits the right specialist for each query without the user needing to know or care which adapter is active.

**RE2 prompting** (repeating the question in the prompt) improves reasoning quality at zero cost on local inference. On an API this doubles your prompt tokens. On a local model, it is free.

**Self-consistency voting** (generating multiple answers and taking the majority) lets a small model trade wall-clock time for reliability. On an API, five samples cost five times as much. On a local model, it costs 60 seconds of waiting.

**Structured context** (via learning design specifications, rubrics, and task templates) compensates for smaller context windows by giving the model exactly what it needs, nothing more.

**The "AI Last" workflow** means users bring focused problems, which is where small models perform best.

None of these techniques are novel individually. The contribution is showing that they stack, that the combination is practically viable on consumer hardware, and that the result is good enough to be genuinely useful for the people who have the fewest alternatives.

## What LocoLLM Does Not Claim

Honesty about limitations matters more than optimism about potential.

- LocoLLM will not match frontier models on open-ended, general-purpose tasks. It is not designed to.
- A 4B quantized model will sometimes produce mediocre or wrong output. The conversation-based workflow and self-consistency voting mitigate this but do not eliminate it.
- Local-first means no seamless multi-device sync, more setup friction, and a wider troubleshooting surface than a managed cloud service.
- The "AI Last" principle requires discipline and skill development that some users will resist. Not everyone will use the tool in the way it is designed to be used.
- This is not a substitute for institutional investment in equitable AI access. Universities should be providing AI tools and training. LocoLLM exists partly because many do not, and waiting for them to start is not an option for students who need help now.

## The Bigger Picture

LocoLLM is a small project with modest ambitions. It will not solve the AI divide. It will not democratize artificial intelligence. Those are problems that require policy, funding, and institutional will at scales far beyond what an open-source adapter framework can provide.

What it can do is demonstrate that the technical floor is lower than most people assume. That useful AI assistance does not require a $20/month subscription, a high-speed internet connection, or a $2,000 laptop. That the combination of task-specific fine-tuning, smart prompting, and local inference produces results that are good enough to make a real difference for students who would otherwise have nothing.

If the benchmarks confirm the hypothesis, and the evaluation data shows that routed specialist adapters on a 4B model approach frontier quality on well-defined tasks, that is a finding worth publishing. Not because it is a technical breakthrough, but because it changes the economics of who gets access to AI-assisted learning.

The research questions are real. The technical contributions are genuine. But they sit inside a larger argument: that the most important gap in AI is not between good and great, but between nothing and something. LocoLLM is an attempt to close the second gap for the people who need it most.

## References

Perkins, M., & Roe, J. (2025). The end of assessment as we know it: GenAI, inequality and the future of knowing. In *AI and the future of education: Disruptions, dilemmas and directions* (pp. 76-80). https://durham-repository.worktribe.com/output/4472558

Roe, J., Furze, L., & Perkins, M. (2025). Digital plastic: A metaphorical framework for Critical AI Literacy in the multiliteracies era. *Pedagogies: An International Journal*. Advance online publication. https://doi.org/10.1080/1554480X.2025.2557491

Li, J., Zhang, T., Shao, W., Peng, Z., Liu, W., & Luo, P. (2024). More agents is all you need. *Transactions on Machine Learning Research (TMLR)*. https://arxiv.org/abs/2402.05120

Xu, X., Tao, C., Shen, T., Xu, C., Xu, H., Long, G., & Lou, J. (2024). RE2: Re-Reading Improves Reasoning in Large Language Models. *Proceedings of EMNLP 2024*. https://arxiv.org/abs/2309.06275

Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *Advances in Neural Information Processing Systems (NeurIPS 2023)*. https://arxiv.org/abs/2305.14314

Borck, M. (2026). Conversation, Not Delegation: Mastering Human-AI Development. https://michael-borck.github.io/conversation-not-delegation/

## Why the Name "LocoLLM"

The name packs three meanings into one word:

- **Local** — everything runs on hardware you own
- **Low-cost** — zero API fees, zero subscriptions
- **Loco** (Spanish: *crazy*) — because attempting frontier-quality AI on a student laptop is a little crazy

The self-deprecating humour is deliberate. "Yes, we're a little loco" signals that we know this is an ambitious bet, and we're making it anyway.

### The LLM Paradox

A fair objection: the individual models in the stack are small (3-4B parameters, quantized to 4-bit). They are SLMs by any standard definition. So why call the project LocoLLM?

Because "large" describes the system, not any single component. Fifteen specialist adapters behind a router, each tuned to excel in its domain, collectively cover the breadth that only a large language model would normally handle. The "large" part is emergent from the collaboration, not from the parameter count.

This is the core research claim: that *large* is a property of system design, not model size. If routed 4-bit specialists can match frontier API quality on scoped tasks, that is a genuinely publishable insight.

### The Backronyms

If LocoLLM ever needs to sound serious for a grant application:

- **L**ocal **Co**llaborative **LLM**s
- **Lo**w-**Co**st **LLM** Framework

### Name Candidates Considered

For the record, the alternatives we weighed:

| Name | Concept | Why we passed |
|------|---------|---------------|
| HydraLM | Many heads, one body | Cool but overpromises; Hydra implies one model, not a swarm |
| SwarmLite | Collective small-model intelligence | Too generic; doesn't suggest local execution |
| AdapterForge | Forging specialised tools | Focuses on the build process, not the runtime |
| REALM | Routed Expert Adapters for Local Models | Strong but poor searchability; conflicts with Google's REALM |
| MOSAIC | Multiple Optimised Specialists with Adaptive Inference Coordination | Accurate but forgettable as acronyms go |
| FrontierLocal | Frontier quality at the edge | Descriptive but no personality |

LocoLLM won because it was memorable, searchable, self-deprecating, and carried a real technical claim in disguise.
