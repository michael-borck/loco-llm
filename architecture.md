# LocoLLM Architecture

This document describes how LocoLLM's components fit together and the reasoning behind key technical decisions.

## System Overview

LocoLLM has five core components:

1. **Base Model**: A single quantized small language model (3B parameters, 4-bit) that stays loaded in memory
2. **Adapter Library**: A collection of LoRA adapters, each fine-tuned for a specific task domain
3. **Router**: A lightweight classifier that examines incoming queries and selects the most appropriate adapter
4. **Inference Enhancements**: Stackable techniques (RE2 prompting, self-consistency voting) that boost output quality at no financial cost
5. **CLI / Runtime**: The user-facing interface that ties everything together

The key insight is that LoRA adapters are tiny (typically 20-30MB) compared to the base model (1.5-2GB in 4-bit). Swapping an adapter takes milliseconds. This means LocoLLM can behave like a multi-model system while only ever keeping one model in memory.

## Base Model Selection

### Current Standard: Qwen2.5-3B-Instruct (Q4_K_M)

The base model is standardized for an entire academic year. All adapters must target the same base model and quantization spec. This ensures any adapter can be loaded onto any LocoLLM installation.

**Selection criteria:**

- Fits in 8GB RAM with room for the OS and adapter (practical ceiling: ~4GB for the model)
- Good instruction-following capability out of the box
- Active community and ongoing updates from the model provider
- Permissive license for academic and research use
- Available in GGUF format for Ollama compatibility

**Why 3B and not 7B?**

A 7B model in 4-bit quantization needs roughly 4-5GB of RAM for the model alone. With the OS, runtime overhead, and adapter, you're pushing past 8GB. Many student laptops, especially older ones or Chromebooks, have exactly 8GB. The 3B class gives us more headroom and faster inference, at the cost of weaker baseline capability, which is exactly what the adapters compensate for.

**Why 4-bit quantization?**

It's the sweet spot between size and quality for our target hardware. 8-bit would roughly double memory usage. 2-bit exists but quality degradation becomes significant. 4-bit (specifically Q4_K_M in GGUF) preserves most model capability while cutting memory requirements by roughly 75% compared to full precision.

### Changing the Base Model

The base model can be updated between academic years if a meaningfully better option becomes available. This requires:

1. Re-evaluating all existing adapters against the new base
2. Retraining adapters that don't transfer well
3. Updating all benchmark baselines
4. Maintaining the previous year's base model as a fallback until migration is complete

This is a significant effort, so base model changes should be infrequent and well-justified.

## Adapter Architecture

### LoRA (Low-Rank Adaptation)

Each adapter uses LoRA, which adds small trainable matrices to the base model's attention layers. During inference, these matrices modify the model's behavior for a specific task domain without changing the base weights.

**Standard configuration:**

```yaml
lora_rank: 16
lora_alpha: 32
lora_dropout: 0.05
target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
```

This produces adapters in the 20-30MB range, small enough to store dozens on disk and swap in milliseconds.

### Adapter Loading

Adapters are loaded through Ollama's Modelfile mechanism or directly through the llama.cpp LoRA loading API. The process:

1. Base model is loaded once at startup and stays in memory
2. When the router selects an adapter, only the LoRA weights are loaded
3. The LoRA weights are applied as a delta to the base model's forward pass
4. Switching adapters means unloading one set of LoRA weights and loading another
5. If no adapter is appropriate, the base model runs without any adapter

### Adapter Versioning

Adapters follow semantic versioning:

- **Major** (2.0.0): Breaking change, incompatible with previous base model
- **Minor** (1.1.0): Improved training, new training data, better scores
- **Patch** (1.0.1): Bug fixes, metadata corrections

The registry tracks the current best version for each domain. Previous versions are archived but available.

## Router Design

The router is intentionally simple in early versions and grows more sophisticated as the adapter library expands.

### v1: Keyword Router

The first router uses keyword and pattern matching:

```python
class KeywordRouter:
    def route(self, query: str) -> str | None:
        """Returns adapter name or None for base model."""
        query_lower = query.lower()
        
        for adapter_name, config in self.adapters.items():
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    return adapter_name
        
        return None  # Fall back to base model
```

Each adapter declares its trigger keywords in the registry:

```yaml
math-reasoning:
  router_keywords: ["solve", "calculate", "equation", "percent", "ratio", "probability"]
```

This is deliberately unsophisticated. It works well enough for a small adapter library (3-5 adapters) with clearly distinct domains, and it's completely transparent to students learning the system.

### v2: Classifier Router

Once there are enough adapters that keyword overlap becomes a problem (typically 6+ adapters), the router upgrades to a lightweight text classifier:

- A small model (e.g., a fine-tuned sentence transformer or even a logistic regression on TF-IDF features) trained on example queries for each domain
- Training data comes from the accumulated benchmark files: each adapter's benchmark examples serve as labeled training data for the router
- The classifier outputs a probability distribution over adapters plus a "none" class for queries best handled by the base model

This becomes a project in its own right, suitable for a student team in Semester 2 or 3.

### v3: Learned Router (Future)

Based on RouteLLM's approach, a more sophisticated router could:

- Use query embeddings from the base model itself (no additional model needed)
- Learn from user feedback which adapter produced the best results
- Apply confidence thresholds (if no adapter scores above threshold, use base model)
- Support adapter composition (route to multiple adapters and combine outputs)

This is Phase 3+ work.

## Inference Pipeline

### Runtime Options

LocoLLM supports two inference backends:

**Ollama (default):** Simplest setup. Ollama handles model loading, quantization, and inference. LocoLLM communicates via Ollama's REST API. LoRA support in Ollama is through custom Modelfiles that reference adapter weights.

**llama.cpp (advanced):** Direct integration for more control over LoRA loading and inference parameters. Lower overhead, more configuration options, but harder to set up.

### Query Flow

```
User Input
    |
    v
[Preprocessing]         Normalize whitespace, detect language, extract metadata
    |
    v
[Router]                Classify query, select adapter (or none)
    |
    v
[Adapter Manager]       Load/swap the selected LoRA adapter
    |
    v
[Prompt Construction]   Apply RE2 (re-read query), add system context
    |
    v
[Inference]             Generate response via Ollama or llama.cpp
    |                   (if voting enabled: generate N samples)
    v
[Voting / Aggregation]  If multiple samples: majority vote or best-of-N
    |
    v
[Postprocessing]        Format output, add metadata (adapter used, vote count)
    |
    v
User Output
```

### Prompt Template

The system prompt includes routing context and applies RE2 (Re-Reading) by default:

```
You are a helpful AI assistant specialized in {adapter.description}.
Focus on providing accurate, detailed responses within your area of expertise.
If a question falls outside your specialty, provide your best general answer
and note that it's outside your primary domain.

User question: {query}

Read the question again: {query}
```

The query is repeated at the end of the prompt. This is the RE2 technique (Xu et al., EMNLP 2024), which enables a form of pseudo-bidirectional attention in decoder-only models. The model processes the question once to build context, then encounters it again with that context already in its attention window. Research shows this improves reasoning accuracy, and reading exactly twice is optimal (more repetitions degrade performance). The cost is negligible: one extra copy of the query adds a few dozen tokens to the prompt, which on a local model with no per-token billing is effectively free.

## Inference Enhancements

One of LocoLLM's key advantages over API-based access is that local inference has no marginal cost. Every token is free. This makes techniques that trade compute time for quality practically viable in ways they aren't when you're paying per token.

LocoLLM supports a stack of inference enhancements that can be combined:

### Layer 1: Task-Specific Adaptation (Always On)

The router selects the best LoRA adapter for the query. This is the foundation. A fine-tuned specialist produces better starting points than the base model for its target domain.

### Layer 2: RE2 Prompting (On by Default)

The query is included twice in the prompt (see Prompt Template above). This is applied automatically to all queries. It adds minimal latency (a few extra tokens in the prompt) and consistently improves reasoning quality on small models.

Users can disable it for tasks where it's unnecessary:

```bash
loco chat --no-reread
```

### Layer 3: Self-Consistency Voting (Opt-In)

For tasks with verifiable answers (math, code, classification), LocoLLM can generate multiple responses and select the most common answer through majority voting.

```bash
# Generate 5 samples and majority vote
loco query "What is 15% of 340?" --votes 5

# Works with any adapter
loco query "Write a Python function to reverse a linked list" --adapter code-python --votes 3
```

**How it works:**

1. The same prompt (with RE2 applied) is sent to the model N times with temperature > 0 (default 0.7)
2. For exact-match tasks: extract the answer from each response, return the most common answer
3. For code tasks: execute each response, return the one that passes the most test cases
4. For open-ended tasks: use the model itself to pick the best response (best-of-N)

**Why this works on local hardware:**

With a frontier API, 5 samples costs 5x the money. On a 3B local model, 5 samples costs 5x the time, but no money. A 3B model on a modern laptop generates at roughly 20-40 tokens per second. A typical response of 200 tokens takes about 5-10 seconds. Five samples take 25-50 seconds. That's a meaningful wait, but for a student working through a problem set, trading 30 seconds of wall time for a significantly more reliable answer is an excellent deal.

**Research basis:**

"More Agents Is All You Need" (Li et al., TMLR 2024) demonstrated that simple majority voting across multiple samples from the same model scales performance predictably. In their experiments, Llama2-13B with majority voting achieved 59% accuracy on GSM8K, outperforming Llama2-70B's 54% on a single pass. The principle applies to any model where errors are somewhat random rather than systematic.

Self-consistency (Wang et al., 2023) showed the same effect: sampling diverse reasoning paths and taking the majority answer consistently outperforms greedy decoding on reasoning tasks.

**Limitations:**

Voting helps most when errors are diverse (different wrong answers each time). If the model consistently produces the same wrong answer due to a systematic gap in its training, voting won't fix it. That's what adapter fine-tuning is for. The two techniques are complementary: fine-tuning reduces systematic errors, voting reduces random errors.

### The Full Stack

When all three layers are active, the pipeline becomes:

```
Query arrives
    |
    v
[Router selects specialist adapter]     -- reduces systematic weakness
    |
    v
[RE2 prompt constructed]                -- improves reasoning at near-zero cost
    |
    v
[Generate N samples, temperature > 0]   -- creates answer diversity
    |
    v
[Majority vote / best-of-N]            -- filters random errors
    |
    v
Response returned
```

Each layer addresses a different failure mode:

| Layer | Addresses | Cost (API) | Cost (Local) |
|---|---|---|---|
| Adapter routing | Systematic domain weakness | N/A (not available) | Free (one-time training) |
| RE2 prompting | Shallow reasoning on first pass | ~2x prompt tokens billed | Near zero |
| Self-consistency voting | Random inference errors | Nx generation cost | Time only |

This is the core of LocoLLM's thesis: a routed, prompt-enhanced, vote-verified 4-bit 3B model may approach frontier quality on well-defined tasks, running entirely on consumer hardware, for free.

### Configuration

Enhancement settings are controlled via CLI flags or `~/.locollm/config.yaml`:

```yaml
inference:
  reread: true              # RE2 prompting (default: on)
  votes: 1                  # Self-consistency samples (default: 1 = off)
  vote_temperature: 0.7     # Temperature for voting samples
  vote_method: "majority"   # "majority" for exact-match, "best_of_n" for open-ended
```

Or per-query:

```bash
# Maximum quality mode (adapter + RE2 + 5 votes)
loco query "Solve: ..." --votes 5

# Fast mode (adapter + RE2, no voting)
loco query "Solve: ..."

# Minimal mode (adapter only, no enhancements)
loco query "Solve: ..." --no-reread --votes 1
```

## Evaluation Architecture

### Harness Design

The evaluation harness is a core piece of infrastructure, not an afterthought. It serves three purposes:

1. **Gating**: Adapters must pass evaluation to be included in the registry
2. **Comparison**: Standardized scoring lets us compare adapters, track improvement across versions, and benchmark against external models
3. **Router training**: Benchmark examples (with their domain labels) become training data for the classifier router

### Benchmark Format

```json
{
  "id": "math-001",
  "instruction": "Solve the following word problem step by step.",
  "input": "A store offers 30% off. During a sale, they take an additional 15% off the sale price. What is the total discount?",
  "expected_output": "The total discount is 40.5%.",
  "evaluation_type": "exact_match",
  "evaluation_config": {
    "extract_pattern": "\\d+\\.?\\d*%",
    "normalize": true
  }
}
```

### Evaluation Types

The harness supports pluggable evaluation methods:

- **exact_match**: Extract answer using a pattern, compare to expected
- **code_execution**: Run generated code, check output
- **llm_judge**: Use a separate LLM to score quality against a rubric
- **rouge**: Text similarity scoring for open-ended generation
- **custom**: Adapter-specific evaluation functions

### Benchmark Integrity

To prevent overfitting to benchmarks:

- Benchmark examples are held out from training data (never overlap)
- The harness tracks a hash of the benchmark file; if it changes, previous scores are flagged
- Each adapter's benchmark is reviewed during PR review
- A "surprise" benchmark (maintained by project leads, not published) provides an independent check

## Distribution

### Package Manager Model

LocoLLM uses a package-manager-style approach for adapter distribution:

```bash
# Search available adapters
loco adapters search "writing"

# Install specific adapter
loco adapters install writing-academic

# Update all installed adapters
loco adapters update

# Remove an adapter
loco adapters remove writing-academic
```

### Storage

Adapters are stored locally in `~/.locollm/adapters/`. The base model is managed by Ollama in its own storage. Total disk footprint for a typical installation (base model + 5 adapters) is approximately 2-3GB.

### Hosting

Adapters are hosted on:
- The project's HuggingFace organization (primary)
- GitHub releases (mirror)
- University-internal Git LFS (for campus network users)

## Technical Constraints and Trade-offs

**Memory ceiling dictates everything.** The 8GB RAM target is the single most important constraint. Every architectural decision flows from it. This is why we use 3B models, 4-bit quantization, and LoRA (which adds minimal runtime memory overhead).

**Adapter swapping adds latency, not memory.** Loading a LoRA adapter takes 50-200ms depending on size and disk speed. This is noticeable but acceptable for interactive use. It means we can have many adapters installed without increasing memory usage.

**Router accuracy matters more as the library grows.** With 3-5 adapters, even keyword routing works fine. With 15+, misrouting becomes a real issue and can produce worse results than no adapter at all. The router needs to scale with the adapter library.

**Base model quality sets the floor.** Adapters can improve specific capabilities but can't compensate for fundamental limitations in the base model's architecture or pretraining. If the 3B base can't do basic language understanding, no amount of LoRA fine-tuning will fix that. This is why base model selection matters so much.
