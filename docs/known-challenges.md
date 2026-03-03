# Known Challenges

This document names the risks, tensions, and open questions that could undermine LocoLLM's thesis. They are recorded here not because they have been resolved, but because pretending they do not exist would be worse than confronting them honestly.

A project that cannot articulate its own weaknesses is not rigorous. It is promotional.

---

## The Moving Target Problem

Every generation of small models gets better out of the box. The fine-tuned Qwen3-4B adapter that beats the base model on GSM8K today may be outperformed by Qwen4-4B's base model in twelve months. This is not a hypothetical risk. It is the predictable consequence of the scaling and distillation trends that make LocoLLM possible in the first place.

The implications are serious:

- **Adapters have a shelf life.** A LoRA trained against Qwen3-4B cannot be applied to Qwen4-4B. When the base model changes, every adapter must be retrained. The semester-by-semester accumulation story is not "we accumulate adapters." It is "we accumulate datasets, methodology, and evaluation infrastructure that survive base model transitions."
- **The goalposts move.** A result showing "our fine-tuned 4B model achieves 85% of frontier performance on task X" may be unimpressive by the time it is published, because the next base model achieves 90% without fine-tuning.
- **The research question shifts.** The interesting question is not "can we make this specific model better?" It is: **how good can 4-bit models in the 1-4B range actually get, and what is the ceiling when you combine fine-tuning, prompting techniques, and routing?** That question survives model generations.

### Why This Is Not Fatal

The moving target cuts both ways. If base models improve, then the *fine-tuned* versions of those base models also improve. The gap between "base 4B" and "fine-tuned 4B" may narrow, but the absolute capability of the fine-tuned system rises with each generation. The methodology — identify weakness, curate data, fine-tune, evaluate, route — remains valid regardless of which specific model sits underneath.

The durable contributions are:

1. **Evaluation datasets** that can be re-run against any future base model
2. **Training pipelines** that work with any LoRA-compatible model
3. **The routing architecture** and the question of whether specialist dispatch adds value
4. **The benchmark data** showing how quantized small models actually perform (not how leaderboards say they should)

If the project is framed around methodology and infrastructure rather than any specific adapter, the moving target becomes a feature: each annual base model switch is a natural experiment measuring how much the floor has risen.

### The F1 and the Sedan

Frontier models are Formula 1 cars. They push the absolute limits of what is possible. They cost millions. Nobody drives one to work.

Small models are sedans. They are built from technology that trickled down from the frontier: better architectures, improved training recipes, distillation techniques, more efficient attention mechanisms. Each year, the sedan gets better because the F1 team solved a problem that eventually made it into production vehicles.

LocoLLM is not trying to build an F1 car. It is trying to build the best possible sedan from this year's parts, and to measure how close the sedan gets to the track car on specific stretches of road. The sedan will never win the Grand Prix. But it does not need to. It needs to get you to work reliably, safely, and cheaply.

The moving target means next year's sedan will be better. That is not a threat to the project. It is the trend the project depends on.

---

## The Good Enough Threshold

A 4-bit 4B model will sometimes produce confident, fluent, wrong output. In an educational context, this is not just an inconvenience. A student who trusts a wrong answer because it sounds authoritative has been actively harmed by the tool.

This is a real risk and it deserves honest treatment.

### But This Is an AI Literacy Problem, Not a Model Problem

The danger of confidently wrong output exists at every scale. Frontier models hallucinate. Published papers contain errors. Textbooks go out of date. Lecturers misspeak. The question is not "does this source ever produce wrong output?" The question is: **does the user have the skills to notice?**

If a student reads an article, hears a claim, or receives AI output, it should pass their BS meter. They should be able to:

- Verify key claims against a second source
- Recognise when an answer feels too clean for a genuinely hard problem
- Distinguish between "I don't know enough to evaluate this" and "this checks out"
- Understand that no single source — AI or otherwise — is the final word

This is not a new skill that AI demands. It is the same critical thinking that education has always been about. AI just makes the need more urgent because the output is fluent enough to bypass the usual signals of unreliability (poor grammar, obvious hedging, lack of citations).

### The Dependency Trap

The deeper concern is not model accuracy. It is the mindset that AI is *the answer* rather than *part of the journey*.

A student who treats any AI output — from GPT-4 or from a fine-tuned 4B model — as authoritative has a dependency problem, not a model quality problem. The difference between "I need the latest frontier model" and "I need any model at all" is often less about capability and more about the belief that AI should be doing the thinking.

This connects directly to the [Conversation, Not Delegation](why-locollm.md#conversation-not-delegation) philosophy. The purpose of AI in learning is to *amplify* thinking, not replace it. A student who uses a small model to brainstorm, draft, and iterate — and then applies their own judgement to the result — is developing capability. A student who pastes a question into a frontier model and submits the output is developing dependency, regardless of how good the model is.

The "must have the latest model" impulse is worth examining. How much of it is about genuine capability gaps, and how much is about wanting the AI to do more of the work? If the task is "think with me about this problem," a 4B model is sufficient. If the task is "produce a polished final answer I can submit without reading," then yes, you need a better model — but that is the wrong task.

### Human-in-the-Loop Is Not Optional

None of this excuses poor model output. LocoLLM has a responsibility to:

- **Make confidence visible.** If the model is uncertain, that should be surfaced, not hidden. Confidence-based routing (Phase 3) should be accelerated, not deferred.
- **Set expectations clearly.** Users should know they are working with a 4-bit quantized small model, not a frontier system. The interface should never imply otherwise.
- **Evaluate honestly.** The benchmarking framework exists precisely to measure where the model fails, not just where it succeeds. Adapters that score 60% on hard problems should say so.

But the broader point stands: the "good enough" threshold is as much about the user as the model. A critical user with a mediocre model will outperform an uncritical user with a frontier model. Investing in AI literacy — teaching students *how* to work with AI, not just *which* AI to use — has higher returns than chasing model quality.

If the model gets the easy questions right and struggles with the hard ones, and the student knows this, that is a useful tool. If the student does not know this, no model is safe.

---

## The Free Tier Reality

LocoLLM does not exist in a vacuum. Students have options.

Google's free tier of Gemini is, as of early 2026, remarkably capable when managed well. OpenAI offers free ChatGPT access. Anthropic's Claude has a free tier. OpenRouter frequently offers free models. Services like GitHub Copilot have student programmes. The "students have zero AI access" framing overstates the problem.

### What Is Honest

- **Free tiers exist and are often good.** A student using free Gemini for brainstorming and drafting is well-served. LocoLLM should not pretend otherwise.
- **Cheap API models are competitive.** Haiku, GPT-4o-mini, Gemini Flash — these cost fractions of a cent per query and outperform any 4B model on most tasks today. For students with modest budgets, they are strong options.
- **LocoLLM cannot compete on raw quality** with free-tier frontier models for general tasks. Not now, and possibly not ever.

### What Is Also True

- **Free tiers are getting tighter.** As the financial realities of inference compute bite, providers are capping usage, degrading free-tier model quality, and pushing toward paid plans. What is generous today may not be generous in two years.
- **Rate limits hit at the worst times.** A student hitting their free-tier cap the night before an assignment deadline has effectively lost access. Local inference has no rate limits.
- **API access requires technical literacy.** Using OpenRouter or cheap API models requires understanding API keys, endpoints, rate limiting, and billing. This is a meaningful barrier for many students.
- **Dependency is structural.** Every student using a free tier is one pricing decision away from losing access. That is not paranoia; it is the business model. Free tiers exist to convert users to paid plans, not as a public service.

### The Honest Recommendation

LocoLLM's position should be: **use the best tools available to you, including free tiers.** We are not competing with Google's free Gemini offering. We are building something that works when the free tier runs out, when the internet is unreliable, when the provider changes terms, or when the task requires unlimited iteration without cost anxiety.

If the free tiers get better, the old models from providers become cheap enough, and local alternatives become unnecessary — that is a good outcome for students. LocoLLM should welcome that future, not fear it.

But giving up and saying "just use the free tiers" has a cost too. As a society, complete dependency on a handful of AI companies for cognitive tools is a fragile position. LocoLLM is a small bet that local capability has value even when cloud capability is available. Not because it is better, but because it is *yours*.

---

## The AI Landscape: We Do Not Stand Alone

LocoLLM is part of a broader ecosystem of local AI tools, and the documentation should acknowledge rather than ignore them. See [AI Landscape](ai-landscape.md) for an honest positioning of where LocoLLM sits relative to alternatives.

The short version: a student running Ollama with a good system prompt already gets most of the way to what LocoLLM provides. The question is whether the adapter routing system, evaluation framework, and specialist fine-tuning add enough value to justify the additional complexity. That is an empirical question, and the answer may turn out to be "not much for general use, but interesting as research."

---

## The Router Question

A student running Qwen3-4B through Ollama with a good system prompt gets roughly 80% of the way to useful AI assistance. LocoLLM's adapter and routing system adds complexity on top of that. The honest question is: **is the marginal improvement worth the additional complexity?**

For *practical use* — brainstorming, drafting, iterating ideas — the answer might be no. A single well-prompted base model handles these tasks adequately. Students do not need the latest and greatest model for this work, and they do not necessarily need specialist routing either. This is more about AI literacy than about model architecture.

For *research* — the answer is genuinely unknown, and that is what makes it interesting.

- Can classifier-based routing to specialist adapters outperform a single generalist on aggregate?
- Does the routing overhead (classification latency, adapter swap time) eat into the quality gains?
- At what number of domains does routing become essential versus optional?
- Does the adapter approach scale, or does it plateau after a few specialists?

These are real questions without published answers under LocoLLM's specific constraints (4-bit, 3-4B, consumer hardware, no fallback to larger models). The router may turn out to be the most interesting research contribution, or it may turn out to be unnecessary overhead. We will not know until we try.

It is worth being explicit about this: **the router is the research, not necessarily the product.** If the research shows that a well-prompted base model performs within a few points of the routed specialist system, that is a publishable negative result and a useful finding. It means the complexity is not justified for practical deployment, and students should just use the base model. If routing shows clear gains, that validates the architecture. Either outcome advances understanding.

The project should be designed so that both results are valuable, not structured so that only a positive result justifies the work.

---

## The 50K Question

If someone handed the project $50,000 in cloud GPU credits tomorrow, would we still do this?

The honest answer is: probably yes, but differently. $50K sounds like a lot until you price A100 hours for training. The large labs spend millions. $50K would let us do the same work with bigger models (7B, 13B) and more thorough hyperparameter sweeps, but it would not fundamentally change the research question. It would just move the constraint boundary.

And that is revealing. The project is not defined by its constraints the way a hobby project is defined by whatever parts are lying around. The constraints are *part of the research design*. Studying what works at the bottom of the capability curve is a different and complementary question to studying what works at the top. TinyML is a legitimate field not because researchers cannot afford bigger chips, but because embedded devices exist and need ML too. LocoLLM occupies an analogous position: consumer hardware exists, students have it, and understanding what AI capability it can deliver is a question worth answering regardless of budget.

That said, the project should be honest about the interplay between conviction and circumstance. The constraints are real, the hardware is secondhand, and the budget is near zero. That is not a weakness to hide. It is a methodological choice that happens to align with financial reality. Both things are true.

The throwaway culture deserves a brief mention: the instinct to always buy the newest hardware and discard the old misses the total cost of ownership and the environmental cost of e-waste. Secondhand enterprise hardware is absurdly capable for the price. A Tesla P100 that cost $5,000 new can be had for under $100 and still trains LoRA adapters effectively. There is a quiet argument here about sustainability that the project embodies without needing to make it loudly.

---

## Scope and Identity

LocoLLM risks trying to be too many things at once:

- A research project (routing, benchmarking, quantized fine-tuning)
- A teaching framework (semester-based student contributions)
- A product for students (local AI assistant)
- A statement about the digital divide

These are all legitimate, but they serve different audiences and should not be collapsed into a single narrative.

**The primary identity is a teaching project.** Each semester, students learn about fine-tuning, evaluation, data curation, and system design by contributing to a real system. The learning is in the building.

**The secondary identity is a research project.** The benchmarking data, the routing experiments, and the methodology are genuine research contributions. If they lead to publications, that is a welcome outcome, not the driving purpose.

**Everything else is a byproduct.** The CLI tool, the digital divide argument, the privacy story — these are real and they matter, but they are consequences of the primary and secondary goals, not goals in their own right.

Keeping this hierarchy clear prevents scope creep and ensures that each output is evaluated against the right success criteria. A teaching project succeeds when students learn. A research project succeeds when it generates replicable findings. A product succeeds when users prefer it to alternatives. These are different standards, and conflating them leads to a project that is mediocre at all three.

---

## Summary

| Challenge | Status | Mitigation |
|-----------|--------|------------|
| Moving target (base models improve) | Ongoing, structural | Frame contributions as methodology + data, not adapters |
| Good enough threshold (wrong answers) | Real risk | AI literacy education, confidence surfacing, honest benchmarks |
| Free tier competition | Current and strong | Acknowledge openly; position as complement, not replacement |
| Router value unclear | Unknown (that is the point) | Design research so negative results are also publishable |
| Scope creep | Risk | Teaching first, research second, everything else is byproduct |
| Constraint-driven framing | Honest tension | Own it — constraints are real AND part of the research design |

These challenges do not invalidate the project. They define its boundaries. A project that cannot name its risks is not ambitious. It is careless.
