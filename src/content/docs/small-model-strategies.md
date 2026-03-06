---
title: "Making Small Models More Useful: A Landscape Overview"
---

# Making Small Models More Useful: A Landscape Overview

Small language models running on consumer hardware are genuinely capable -- but capability is not evenly distributed. A 7B model used well can outperform a much larger model used passively. This piece maps the strategies, techniques, and architectures that close the gap between what a small model is and what it can do in practice.

The framing throughout is practical: what can an educator, researcher, or practitioner actually do with modest hardware and reasonable effort?

---

## 1. The Baseline Problem

A small model has three hard constraints:

**Context window** -- smaller models typically support shorter contexts. Less room for instructions, examples, and conversation history simultaneously.

**Knowledge** -- training data cutoffs, potential gaps in specialist domains, higher hallucination rates on edge cases.

**Reasoning depth** -- complex multi-step reasoning is harder for smaller models. They can lose the thread across long chains of logic.

Everything that follows is a response to one or more of these constraints.

---

## 2. Prompting Strategies

Prompting is the lowest-cost intervention. No fine-tuning, no infrastructure, just better instructions.

### RE2 Prompting (Re-Reading)

A simple but effective technique: instruct the model to re-read the question before answering. The prompt structure is:

> [Question]. Read the question again: [Question]. Now answer.

RE2 reduces errors caused by the model misreading or partially processing the input on the first pass. Particularly effective on small models where attention mechanisms are less robust. The cost is a few extra tokens. The gain is measurable accuracy improvement on reasoning tasks.

### Chain of Thought (CoT)

Instruct the model to show its reasoning before giving a final answer. "Think step by step" or a more structured variant with explicit reasoning stages. Forces the model to externalise intermediate steps, which both improves accuracy and makes errors visible and correctable.

### Few-Shot Prompting

Provide 2-3 examples of the desired input/output format before the actual query. Small models are more sensitive to format than large ones -- a well-chosen example set significantly improves output consistency. Particularly useful for structured extraction tasks.

### Structured Output Prompting

Instruct the model to return JSON, XML, or a specific template. Reduces post-processing effort and makes outputs machine-readable. Combine with schema validation to catch malformed responses. Small models are less reliable at this than large ones -- few-shot examples of the target schema help significantly.

### System Prompt Design

The system prompt is the highest-leverage prompt real estate. A well-crafted system prompt that defines role, constraints, output format, and tone can compensate for significant model capability gaps. The CloudCore Networks chatbot employees demonstrate this -- unique backstories and constrained knowledge domains make a 7B model behave like a specific character rather than a generic assistant.

### Prompt Chaining

Break complex tasks into sequential smaller tasks, each with its own prompt. The output of one step becomes the input of the next. Particularly effective for tasks that exceed the model's reasoning depth in a single pass -- document summarisation, multi-step analysis, requirement extraction.

---

## 3. Conversation Not Delegation

A framework for the human side of the interaction rather than the technical side.

**Delegation** treats the model as an answer machine. Submit query, accept response, done. The model's limitations become the ceiling of the outcome. Errors go undetected. The user develops dependency rather than capability.

**Conversation** treats the model as a thinking partner. Query, evaluate, push back, iterate. The model's limitations become visible and correctable because the user is actively engaged. A 3B model used conversationally can produce better thinking outcomes than a 70B model used passively.

This distinction matters more for small models than large ones. A frontier model can compensate for passive use with raw capability. A small model cannot. Conversation is not optional for small model users -- it is the method.

**Practical implication:** the quality of the human's engagement is more important than the quality of the model for most everyday use cases. This transfers the locus of improvement from hardware procurement to skill development.

---

## 4. Interface-Level Nudging

An extension of Conversation not Delegation implemented at the interface rather than the instructional level.

Append a conversational prompt to every AI response:

> "Does that match what you expected? If something seems off, tell me what seems wrong."

This structurally reduces passive acceptance by making the follow-up question the path of least resistance. The user doesn't have to decide to engage critically -- the interface assumes they will.

Testable hypothesis: nudge-prompted students extract more requirements, ask more follow-up questions, and show better calibration between confidence and accuracy than students using a standard interface. See the companion research proposal for study design.

The nudge also functions as a scaffold that can potentially be faded -- students who internalise the conversational pattern may not need the prompt indefinitely.

---

## 5. Retrieval Augmented Generation (RAG)

RAG addresses the knowledge constraint directly. Rather than relying on what the model was trained on, inject relevant documents into the context at query time.

**How it works:** user query → retrieve relevant chunks from a document store → prepend chunks to the prompt → model answers with access to current, specific information.

**Why it helps small models specifically:** a small model with accurate source material in context outperforms a large model guessing from training data. RAG converts a knowledge problem into a reasoning problem, which is a better trade for small models.

**Practical implementations:** AnythingLLM, LlamaIndex, LangChain all support RAG pipelines against local document collections. The `llm-fragments-folder` plugin enables persistent CLI chat against local document collections using Simon Willison's `llm` tool.

**Limitations:** retrieval quality determines answer quality. If the wrong chunks are retrieved, the model confidently answers from irrelevant material. Chunk size, embedding model choice, and retrieval strategy all affect outcomes significantly.

---

## 6. Fine-Tuning

Fine-tuning adapts the model's weights to a specific domain, task, or style. More expensive than prompting but produces a model that has internalised the target behaviour rather than being instructed toward it at each query.

### QLoRA

Quantised Low-Rank Adaptation. Fine-tune a large model on consumer hardware by:
- Quantising the base model to 4-bit (reduces VRAM from ~14GB to ~5GB for 7B)
- Training only small low-rank adapter matrices rather than full weights
- Merging or loading adapters at inference time

A 7B model QLoRA fine-tune on a domain-specific dataset of 1,000-2,000 examples takes 2-4 hours on an RTX 2060 Super with Unsloth. The resulting adapter produces a model that speaks the domain language, follows domain-specific formats, and makes fewer domain-specific errors.

### When Fine-Tuning Is and Isn't Appropriate

Fine-tuning helps when: the task is well-defined and consistent, you have quality training examples, the base model consistently fails on the target behaviour despite good prompting.

Fine-tuning doesn't help when: the problem is knowledge gaps (use RAG), the task varies widely (prompting is more flexible), you don't have quality training data (garbage in, garbage out).

### LoRA vs QLoRA

Full LoRA at 16-bit precision (requires 16GB VRAM -- Burro's P100 territory) produces higher-fidelity adapters than 4-bit QLoRA. For most practical applications QLoRA is sufficient. For research-grade adapter quality where the difference matters, the P100's 16GB HBM2 is the right tool.

---

## 7. Tool Use and Function Calling

Give the model access to external tools -- web search, calculators, code execution, database queries, APIs. The model decides when to call a tool, calls it, and incorporates the result into its response.

**Why this matters for small models:** tool use offloads tasks the model is bad at (precise arithmetic, current information, structured data retrieval) to systems that are good at them. The model's job becomes orchestration and synthesis rather than computation and retrieval.

**Practical implementations:** Ollama supports tool calling for models that include function calling in their training (Llama 3.1, Qwen2.5, Mistral Nemo). AnythingLLM has agent mode with tool integrations. The model needs to be capable enough to use tools reliably -- very small models (1B-3B) tend to misfire on tool calls.

**In the CloudCore context:** a chatbot employee with access to a structured knowledge base via tool calls can answer specific questions accurately without hallucinating, even on a 7B base model.

---

## 8. Multi-GPU Routing Architectures

When multiple GPUs are available, the question shifts from "how capable is this model" to "how do I orchestrate multiple models to produce better outcomes."

### Load Balancing

Run multiple instances of the same model, one per GPU. A router distributes incoming requests round-robin. Triples (or more) concurrent throughput without any quality change. Relevant for multi-user environments -- CloudCore Networks with multiple students querying simultaneously, AI Exchange demos, any production inference serving scenario.

Implementation: nginx upstream load balancing or a small FastAPI proxy. Each Ollama instance assigned to a specific GPU via `CUDA_VISIBLE_DEVICES`.

### Mixture of Agents (MoA)

Two proposer models generate independent responses to the same query at slightly different temperatures. A third aggregator model synthesises the best elements of both into a final response.

Quality improvements are most noticeable on reasoning and analysis tasks where diversity of approach matters. Adds roughly one generation cycle of latency. The mechanism mirrors cognitive ensemble strategies -- diverse inputs improve collective output quality.

See: [arxiv.org/abs/2406.04692](https://arxiv.org/abs/2406.04692)

### Speculative Decoding

A small fast draft model generates candidate tokens. A larger verifier model checks and accepts or rejects batches. Net result: faster output from the large model because the drafter handles predictable continuations.

Supported natively in llama.cpp via `--model-draft`. Reduces latency without sacrificing quality on the verifier model's outputs.

### Model Cascading / Intelligent Routing

Route queries to different models based on complexity. A lightweight classifier (or even simple heuristics) determines whether a query is simple (short context, factual, low stakes) or complex (multi-step, ambiguous, high stakes). Simple queries go to a fast small model. Complex queries go to the best available model.

Reduces average latency and resource consumption while preserving quality where it matters. Less explored in open-source tooling but straightforward to implement with a custom router.

---

## 9. Quantisation

Reduce model precision to fit larger models in available VRAM.

| Format | Precision | Notes |
|--------|-----------|-------|
| F16 | 16-bit float | Full quality, 2x VRAM of Q8 |
| Q8_0 | 8-bit | Near-lossless, good for production |
| Q4_K_M | 4-bit | Sweet spot -- good quality, half the VRAM of Q8 |
| Q3_K_M | 3-bit | Noticeable quality drop, emergency VRAM saving |
| Q2_K | 2-bit | Significant degradation, last resort |

Q4_K_M is the practical standard for 8GB VRAM cards. A 7B model at Q4_K_M fits in ~4.5GB, leaving headroom for context. A 13B model at Q4_K_M requires ~8GB -- right at the edge for an 8GB card.

Quantisation is the main mechanism by which VRAM tier translates to model tier. The 12GB 3060's value in Colmena is that it can run Q4_K_M 13B models that 8GB cards can't touch.

---

## 10. Context Management

Small models have shorter effective context windows and degrade faster at the edges of those windows than large models. Active context management compensates.

**Summarisation:** periodically summarise the conversation history and replace raw history with the summary. Preserves key information while reclaiming context space.

**Sliding window:** drop the oldest turns from context as new ones are added. Simpler than summarisation but loses older information entirely.

**Structured context:** separate system context (stable instructions) from conversation context (variable). Keep system context tight and well-specified so variable conversation content has maximum headroom.

**RAG as context management:** rather than keeping documents in context, retrieve only the relevant chunks at query time. Effectively infinite document context on a finite context window.

---

## 11. Model Selection

The right model for the task is often smaller than assumed.

For instruction following and conversation: Qwen2.5 7B, Llama 3.1 8B, Mistral 7B are well-established and capable.

For coding: Qwen2.5-Coder 7B punches significantly above its weight for code generation and explanation.

For very constrained hardware (4GB VRAM): Phi-3 Mini 3.8B, Qwen2.5 3B, Gemma 2B. Surprisingly capable for focused tasks despite small parameter counts.

For tool use: Llama 3.1 8B and Qwen2.5 7B have explicit tool calling training. Smaller models tend to misfire.

Model selection interacts with all other strategies -- a well-prompted Qwen2.5 7B with RAG on relevant documents will outperform a larger model guessing from training data on most domain-specific tasks.

---

## 12. The Compounding Effect

These strategies are not mutually exclusive. The most capable small model deployments combine multiple layers:

- Right model for the task (model selection)
- Domain-adapted weights (fine-tuning)
- Current information injected at query time (RAG)
- Clear structured instructions with examples (prompting)
- Active human engagement and iteration (Conversation not Delegation)
- Interface design that scaffolds that engagement (nudging)
- Infrastructure that scales throughput (multi-GPU routing)

Each layer compounds the others. A fine-tuned model responds better to prompts. A RAG-augmented model has less hallucination for the human to catch. A nudged interface produces the human engagement that makes all of it work.

The ceiling for a small model used with all of these strategies is significantly higher than the ceiling for a large model used with none of them.

---

## 13. What This Means for the Research

The landscape above suggests several directions that remain underexplored:

**Benchmarking small models on small hardware** (smol-bench) -- systematic characterisation of what each VRAM tier can actually do across model families, quantisation levels, and task types. Currently absent from the literature.

**The nudge as intervention** -- testable hypothesis that interface design changes engagement behaviour independently of instruction. Connects pedagogy to HCI research.

**Compounding strategy evaluation** -- does combining RAG + fine-tuning + CoT produce additive gains on small models? The interaction effects are not well characterised.

**The floor as the focus** -- most research optimises from the middle up. The 4GB card user, the staff member with an old office PC, the student on a free tier -- these users are underserved by current benchmarking and underrepresented in the literature. That is the gap this project occupies.

---

*Part of the LocoLLM research documentation. Related: research-proposal-nudging.md, nvidia-gpu-reference.md, meet-the-lab.md*
