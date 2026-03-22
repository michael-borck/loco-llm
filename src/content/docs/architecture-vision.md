---
title: "Architecture Vision: Where This Could Go"
---

This document explores ideas that go beyond LocoLLM's current design. None of this is committed to. Some of it may never be built. But the ideas are worth recording because they connect the teaching project to real research questions, and because a student who understands these concepts can participate in conversations about where AI systems are heading.

The current system — one base model, keyword router, specialist adapters — is Step 1. This document sketches what Steps 2 through N might look like.

---

## From Routing to Decomposition

LocoLLM's router currently does one thing: pick the best adapter for a query. "Calculate the area of a circle" goes to the math adapter. "Write a Python function" goes to the code adapter. One query, one specialist.

But real queries are rarely that clean.

Consider: "Write a Python function that calculates compound interest, explain the formula step by step, and add unit tests." That query needs code generation, mathematical reasoning, and analytical explanation. The current router picks one adapter and hopes for the best. A more capable system would decompose the query into parts and route each part to the right specialist.

### What Decomposition Looks Like

```
User query
    |
    v
[Decomposer]           "This query has 3 parts"
    |
    +---> "Calculate compound interest formula"     --> math adapter
    +---> "Write Python implementation"              --> code adapter
    +---> "Explain the formula step by step"         --> analysis adapter
    |
    v
[Recombiner]           Assemble a coherent response from the parts
    |
    v
Response
```

This is fundamentally different from routing. Routing is selection. Decomposition is orchestration. The intelligence moves from "which adapter?" to "how do I break this problem down, and how do I put the pieces back together?"

### The Orchestration Problem

The decomposer and recombiner need to be smart enough to understand query structure and assemble coherent output. That requires a model with genuine language understanding — not just pattern matching. This is the "turtles all the way down" problem: who orchestrates the orchestrator?

One answer: use a more capable model (3-8B) as the orchestrator, and let smaller, cheaper specialists handle the subtasks. The orchestrator reasons about structure. The specialists execute. Not every layer in the stack needs the same capability. Understanding and pattern execution are different jobs.

This connects to a well-known result in neural network theory: the universal approximation theorem tells us that a sufficiently wide network can approximate any continuous function. The generalist *can* do anything. It is just wildly inefficient at most things. Specialisation is an efficiency strategy, not a capability limitation.

---

## Granularity of Specialisation

How narrow should each specialist be?

The current system has three broad domains: math, code, analysis. But "math" includes arithmetic, algebra, calculus, linear algebra, statistics, and number theory. "Code" includes Python, JavaScript, Rust, and also paradigms like functional programming, OOP, and systems programming.

Finer-grained adapters would perform better within their narrow lane. A linear algebra specialist would outperform a general math adapter on matrix problems. A functional programming specialist would write better Haskell than a generic code adapter.

### The Tradeoff Curve

```
Narrow adapters:   Better per-task quality
                   More adapters to manage
                   Smarter routing/decomposition needed
                   More training effort

Broad adapters:    Simpler routing
                   Fewer adapters to manage
                   Weaker per-task performance
                   Easier to train
```

There is a sweet spot that depends on the router's capability, the available hardware, and the diversity of queries the system handles. Nobody has definitively found this sweet spot for the constraints LocoLLM operates under (4-bit, 3-4B, consumer hardware). That is a research question worth investigating.

One approach: start broad, measure where the adapter struggles, and split. If the math adapter consistently fails on probability questions but handles arithmetic well, split off a probability specialist. Let benchmark data drive the granularity decisions rather than guessing up front.

---

## The Layered Stack

Not every part of a response requires the same level of capability. Consider a layered architecture where different models handle different cognitive tasks:

| Layer | Capability Needed | Model Size |
|-------|------------------|------------|
| Query understanding, decomposition | Genuine reasoning | 3-8B |
| Domain execution (math, code, etc.) | Learned patterns | 1-3B, specialised |
| Output formatting, assembly | Language fluency | 3-8B |

The insight is that "understanding" and "pattern execution" are different jobs. A 7B model that understands the query structure can delegate computational subtasks to smaller specialists that have been trained via LoRA adapters to execute specific patterns reliably.

This is analogous to how a senior engineer works with junior developers. The senior architect designs the system and reviews the output. The juniors write the specific modules. The juniors do not need to understand the full system architecture. The senior does not need to write every line of code. The skill requirement at each layer is different, and the labour allocation reflects that.

### Why Small Models Can Be Good Specialists

Small models (1-3B) have limited capacity for multi-step reasoning, but they can learn specific input-output patterns very effectively through adapter training. A TinyLlama trained on thousands of examples of "given matrix A and B, compute AB" may not *understand* linear algebra, but it can reproduce the mechanical steps reliably.

This works because adapter training teaches patterns, and patterns are enough for well-scoped subtasks. The understanding — knowing *when* matrix multiplication is needed — comes from the orchestration layer above.

There is a floor below which adapter training cannot compensate for architectural limitations. Current evidence suggests that floor is somewhere around 1-3B parameters, depending on the task. Below that, the model lacks the internal representations to learn even mechanical patterns reliably. Above 3B, adapter training gains are substantial and consistent.

---

## The Swarm: Parallel Specialists on Limited Hardware

Here is where the ideas get speculative and interesting.

Imagine a system with multiple GPUs — not expensive data centre cards, but commodity hardware. Four old GTX 1050 Ti cards with 4GB VRAM each, the kind you can find secondhand for the price of a textbook. Each card holds one small specialist model, permanently resident in VRAM. No swapping needed.

```
         [Orchestrator - GPU 0 or CPU]
            |         |         |
            v         v         v
         [Math]    [Code]  [Analysis]
         GPU 1     GPU 2    GPU 3
```

Queries arrive. The orchestrator decomposes them. Subtasks are dispatched to the relevant specialist in parallel. Results come back. The orchestrator assembles the final response.

### Why This Is Interesting

This is essentially a mixture-of-experts architecture implemented at the hardware level, with physical routing instead of learned gating. It trades model size for parallelism. Instead of one large model that does everything sequentially, you have many small models that do their parts simultaneously.

The economics are compelling. Four used 1050 Ti cards cost less than one current-generation GPU. The total VRAM (16GB across four cards) is comparable to a single T4, but each specialist has its own dedicated memory. No contention. No swapping latency.

### Why This Is Hard

- **Swap latency**: If the system *does* need to swap a model (query needs a specialist that is not resident), loading a GGUF from disk takes 1-2 seconds. Design the system to minimise swaps by keeping the most-used specialists resident.
- **Communication overhead**: Dispatching subtasks across GPUs and collecting results adds latency. For short responses, the orchestration overhead may dominate.
- **Orchestrator bottleneck**: The orchestrator model must be fast and capable. If it runs on CPU while specialists use GPUs, the CPU becomes the bottleneck. Dedicating one GPU to the orchestrator may be worth the tradeoff.
- **Recombination quality**: Stitching together outputs from multiple specialists into a coherent response is non-trivial. The recombiner needs enough context and language understanding to produce fluent, consistent output.

### Analogy to Modern Hardware Architecture

This is not a new idea. It is how CPUs and GPUs already work.

A modern CPU has multiple cores, each handling different threads. A GPU has thousands of small cores executing in parallel. The operating system's scheduler decides which core handles which task. The hardware interconnect handles communication.

The swarm architecture applies the same principle to language models. Multiple small "cores" (specialist models), a scheduler (router/decomposer), and a communication layer (the orchestration framework). Just as a many-core processor can outperform a single powerful core on parallelisable workloads, a swarm of specialists can potentially outperform a single large model on decomposable queries.

The key qualifier is "decomposable." Not all queries can be split into independent parts. Some require sustained, sequential reasoning where the output of step N depends on steps 1 through N-1. These queries need a single capable model, not a swarm. The research question is: what fraction of real-world queries are decomposable enough to benefit from parallel specialist execution?

---

## Tool Use: Let Models Do What Models Are Good At

There is a fundamental mismatch in LocoLLM's current math adapter. We are training a language model — a system that manipulates tokens, not numbers — to perform arithmetic. A 4-bit model doing multiplication is like asking a poet to do your taxes. They might get it right sometimes, but it is not what they were built for.

The insight is simple: language models are good at language. Computers are good at computation. Let each do what it is good at.

### Recognition, Not Execution

Instead of training the math adapter to *compute* "15% of 340", train it to:

1. **Recognise** that the query involves a calculation
2. **Extract** the mathematical operation as a structured expression
3. **Generate** a tool call (Python, sympy, a calculator API)
4. **Interpret** the result back into natural language

```
User:   "What's 15% of 340?"

Model recognises: this is arithmetic
Model generates:  {"tool": "python", "code": "340 * 0.15"}
Tool executes:    51.0
Model responds:   "15% of 340 is 51."
```

The model never does the multiplication. It recognises that multiplication is needed, writes the expression, and explains the result. Every part of that pipeline is a language task, which is exactly what a language model should be doing.

### This Reframes the Entire Adapter Strategy

If adapters delegate execution to tools, their job changes fundamentally:

| Domain | Current Job (Execution) | Better Job (Recognition + Delegation) |
|--------|------------------------|--------------------------------------|
| Math | Learn to calculate | Learn to recognise math and generate Python/sympy expressions |
| Code | Learn to write code | Learn to understand specs and generate structured implementations |
| Analysis | Learn to reason about text | Learn to extract claims, generate verification queries |

Each adapter becomes a translator between natural language and the appropriate tool. The "math adapter" is really a natural-language-to-computation translator. The "code adapter" is a spec-to-implementation translator. The quality ceiling rises dramatically because the hard part (computation, execution, verification) is handled by deterministic tools that do not make arithmetic errors.

### What Tools Are Available

Even on consumer hardware with no cloud dependencies, the tool ecosystem is rich:

- **Python interpreter**: Arithmetic, data manipulation, plotting (via subprocess)
- **sympy**: Symbolic math — algebra, calculus, equation solving
- **numpy**: Linear algebra, statistics, numerical computation
- **ast module**: Code syntax validation and analysis
- **Standard library**: File operations, string processing, datetime calculations

These are all local, free, and deterministic. A tool call adds milliseconds of latency, not seconds. And the result is *correct* — no hallucinated arithmetic, no approximate factoring, no confidently wrong matrix inversions.

### The Training Data Shift

This changes what adapter training data looks like. Instead of:

```json
{"role": "user", "content": "What is 23 × 47?"}
{"role": "assistant", "content": "23 × 47 = 1081"}
```

The training data becomes:

```json
{"role": "user", "content": "What is 23 × 47?"}
{"role": "assistant", "content": "<tool_call>{\"tool\": \"python\", \"code\": \"23 * 47\"}</tool_call>"}
{"role": "tool", "content": "1081"}
{"role": "assistant", "content": "23 × 47 = 1,081"}
```

The model learns the pattern "when you see multiplication, generate the expression and call Python." It does not need to learn multiplication itself. This is a much easier task for a small model, and it generalises: a model trained on 200 examples of "recognise arithmetic and generate Python" will handle novel arithmetic problems, because the pattern is consistent even when the numbers change.

### Implications for Domain Boundaries

Tool use also softens the fuzzy boundary problem between domains. "Is data analysis math or analysis?" becomes less important when both adapters can call the same Python tool. The math adapter recognises the calculation. The analysis adapter recognises that a claim needs verification. Both might generate `pandas` code. The domain distinction is about *what to recognise*, not *what tool to call*.

### Connection to Frontier Models

This is not a novel idea. It is exactly what frontier models do. ChatGPT's Code Interpreter, Claude's tool use, Gemini's function calling — they all follow the same pattern: the model reasons in language, delegates execution to tools, and interprets the results.

The difference is that frontier models learn tool use during pretraining and RLHF at massive scale. LocoLLM would need to teach it through adapter training at small scale. Whether a 4B model can learn reliable tool-call generation from hundreds (not millions) of examples is an open question. Early evidence from function-calling adapters (Gorilla, NexusRaven, Functionary) suggests it is feasible, but the reliability bar is high — a tool call that is almost right is worse than no tool call at all.

### A Practical Starting Point

Tool use does not require rebuilding the system. A minimal first step:

1. Add a Python sandbox that the model can call during inference
2. Fine-tune the math adapter on tool-call formatted training data (recognise → generate expression → interpret result)
3. Benchmark against the current approach (model does arithmetic directly)

If the tool-calling adapter outperforms the arithmetic adapter — and it almost certainly will on computation tasks — that validates the approach. Then extend to code (generate and test), analysis (extract and verify), and other domains.

---

## Distributed Training: The Annual Rebuild

When the base model changes (yearly or as needed), every adapter must be retrained. With 3 adapters this is manageable. With 15 or 30, it becomes a logistics problem.

But it is a *pleasantly parallel* logistics problem. Each adapter trains independently — different data, different LoRA weights, same base model. There is no need to distribute a single training job across machines (which is hard). You just need to run many independent jobs (which is easy).

### The Lab as a Build Farm

A teaching lab with 20 machines, each with a modest GPU, can retrain 20 adapters simultaneously. Each machine:

1. Pulls the new base model
2. Pulls its assigned adapter's training data
3. Runs the standard training script
4. Exports a GGUF
5. Uploads the result to a shared location

A simple task runner (even a spreadsheet mapping adapters to machines) is sufficient for coordination. No distributed training framework needed. No gradient synchronisation. Just embarrassingly parallel independent jobs.

This also solves the "who trains what" problem for a teaching project: each student or student team owns an adapter. When the base model changes, each team retrains their adapter. The annual rebuild becomes a teaching exercise in itself — students see firsthand how their adapter's performance changes on a new base, which is a concrete lesson in the relationship between base model capability and adapter training gains.

### What Actually Takes Time

The bottleneck is not compute. A LoRA fine-tune on a T4 takes 10-20 minutes per adapter. Even sequentially, 30 adapters would take a day. In parallel across a lab, it takes 20 minutes.

The real bottleneck is evaluation. Every retrained adapter needs to be benchmarked against the new base model to confirm it still adds value. Some adapters may need their training data or hyperparameters adjusted for the new base. This evaluation and adjustment loop is where the time goes, and it is inherently human work — deciding whether a 3% accuracy drop is acceptable or requires investigation.

Automating the rebuild-and-benchmark pipeline (train → export → evaluate → report) would reduce this to a review task rather than a hands-on task. That automation is a worthwhile infrastructure project.

---

## Yes, This Is an Agent Architecture

If you have been reading this document and thinking "this sounds like agents," you are right.

An orchestrator that receives a goal, decomposes it into subtasks, delegates to specialists, calls tools, and assembles a coherent result — that is an agent. The vocabulary differs depending on which community you learned it from (multi-agent systems, LLM agents, autonomous AI, agentic workflows), but the pattern is the same.

The difference between LocoLLM's vision and frontier agent systems like Claude Code or Devin is not the architecture. It is where the intelligence lives. Frontier agents put everything in one large model — planning, execution, self-correction, tool use — because a single 100B+ parameter model can handle all those tasks. LocoLLM's vision distributes those responsibilities across many small models and deterministic tools, coordinated by a moderately capable orchestrator. Same pattern. Different economics. Different constraints.

This is worth naming explicitly because the building blocks students work with in LocoLLM are the same building blocks that agent systems use at scale:

| LocoLLM Concept | Agent Concept |
|-----------------|---------------|
| Router | Task classifier / intent detector |
| Adapter | Specialist skill or capability |
| Tool call (Python, sympy) | Tool use / function calling |
| Decomposer | Planner |
| Recombiner | Response synthesiser |
| Evaluation harness | Self-assessment / reward model |
| The swarm | Multi-agent system |

A student who builds a math adapter that generates Python tool calls, hooks it to a router, and evaluates the output has built a tiny, single-domain agent. They just did not call it that. And understanding that connection — seeing how routing, specialisation, tool use, and evaluation compose into something larger — is more valuable than any individual adapter.

LocoLLM is not an agent framework. It is not trying to be one. But it teaches the concepts that agent frameworks are built from, one piece at a time, on hardware students can afford. That is a useful thing to know.

---

## What This Means for LocoLLM

None of the above changes what LocoLLM is today. The current system — one base model, keyword router, three adapters — is the right starting point. Students need to understand adapter training, evaluation, and routing before they can meaningfully engage with decomposition, granularity tradeoffs, and hardware-level parallelism.

But the ideas connect. Each piece of LocoLLM today is a simplified version of a piece in the larger vision:

| LocoLLM Today | Vision |
|---------------|--------|
| Keyword router picks one adapter | Decomposer splits query across multiple specialists |
| 3 broad domain adapters | Many fine-grained specialists |
| Model does arithmetic directly | Model recognises math, delegates to Python/sympy |
| Single base model, single GPU | Layered stack across multiple devices |
| Sequential query-response | Parallel specialist execution |
| Manual adapter retraining | Automated rebuild-and-benchmark pipeline |
| `loco eval` compares one adapter vs base | Domain benchmark suites comparing adapter+base combinations |

Each upgrade from the left column to the right column is a project in its own right. Some are suitable for a single semester's work. Others are multi-year research questions. The path from "keyword router on a laptop" to "orchestrated swarm on commodity hardware" is long, but each step is a meaningful and self-contained contribution.

---

## Open Questions

These are genuinely open. If you have ideas, that is what research is for.

1. **Decomposition strategy**: How do you decide whether to route a query whole or decompose it? What model is the decomposer, and how do you train it?
2. **Optimal granularity**: At what domain specificity do adapters stop improving? Is "linear algebra" the right grain, or is "3x3 matrix inversion" too narrow to be useful?
3. **Recombination quality**: Can you assemble specialist outputs into a coherent response without losing context or introducing contradictions?
4. **Hardware scheduling**: On a multi-GPU commodity setup, what is the optimal allocation of models to devices? Should the orchestrator share a GPU with a rarely-used specialist?
5. **Capability floor**: Below what parameter count does adapter training fail to produce useful specialists? How does this vary by domain?
6. **Economic crossover**: At what point does a swarm of small models on cheap hardware match the cost-performance of a single large model on expensive hardware? Does that crossover point even exist for most workloads?
7. **Tool-call reliability**: Can a 4B model learn to generate correct tool calls from hundreds of adapter training examples? What is the failure rate, and is an almost-right tool call worse than no tool call?
8. **Domain boundaries under tool use**: If multiple adapters delegate to the same tools (Python, sympy), does the adapter distinction still matter, or does tool use flatten the domain hierarchy?
9. **Rebuild automation**: What does a fully automated retrain-and-benchmark pipeline look like, and how much human judgement remains in the loop for evaluating retrained adapters?

---

## Further Reading

These are not endorsements. They are starting points for anyone who wants to dig deeper into the ideas explored here.

- **Mixture of Experts**: Shazeer et al. (2017), "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer" — the foundational MoE paper
- **Multi-agent systems**: Li et al. (2024), "More Agents Is All You Need" — majority voting as a simple multi-agent strategy
- **RouteLLM**: Ong et al. (2024) — learned routing between models of different capability
- **Universal approximation**: Cybenko (1989), Hornik (1991) — the theoretical basis for neural networks as general function approximators
- **LoRA composition**: Huang et al. (2023), "LoRAHub: Efficient Cross-Task Generalization via Dynamic LoRA Composition" — combining multiple LoRA adapters
- **Tool use in LLMs**: Schick et al. (2023), "Toolformer: Language Models Can Teach Themselves to Use Tools" — foundational work on training models to generate tool calls
- **Function calling at small scale**: Patil et al. (2023), "Gorilla: Large Language Model Connected with Massive APIs" — fine-tuning for API call generation

---

*This document is speculative by design. It records ideas worth thinking about, not commitments. If something here turns out to be wrong or impractical, update the document. That is how research works.*
