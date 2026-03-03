# LocoLLM

<!-- BADGES:START -->
[![collaborative](https://img.shields.io/badge/-collaborative-blue?style=flat-square)](https://github.com/topics/collaborative) [![consumer-hardware](https://img.shields.io/badge/-consumer--hardware-blue?style=flat-square)](https://github.com/topics/consumer-hardware) [![fine-tuning](https://img.shields.io/badge/-fine--tuning-blue?style=flat-square)](https://github.com/topics/fine-tuning) [![jupyter-notebook](https://img.shields.io/badge/-jupyter--notebook-blue?style=flat-square)](https://github.com/topics/jupyter-notebook) [![language-model](https://img.shields.io/badge/-language--model-blue?style=flat-square)](https://github.com/topics/language-model) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![routing](https://img.shields.io/badge/-routing-blue?style=flat-square)](https://github.com/topics/routing) [![task-specific](https://img.shields.io/badge/-task--specific-blue?style=flat-square)](https://github.com/topics/task-specific)
<!-- BADGES:END -->

### Local Collaborative LLMs -- Frontier AI on a Student Budget

> *"Crazy enough to work."*

LocoLLM is an open-source framework for building a routed collection of task-specific fine-tuned small language models that run entirely on consumer hardware. Instead of relying on expensive frontier API access, LocoLLM combines a single quantized base model with lightweight LoRA adapters, each fine-tuned for a specific task domain, and a simple router that directs queries to the best-suited specialist.

The project is designed to be built collaboratively, semester by semester, by university students. Each cohort contributes new specialist adapters, improved evaluation benchmarks, and better routing logic. The result is a growing ecosystem of local AI capability that anyone can install on a laptop.

The goal is not to compete with frontier models. It is to understand how they work by building smaller versions of the same patterns. Students who build adapters, design evaluations, and reason about routing tradeoffs are learning the concepts that modern AI systems are built from — fine-tuning, specialisation, tool use, orchestration. Frameworks come and go. That understanding transfers.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michael-borck/loco-llm/blob/main/notebooks/train_math_adapter.ipynb) **Train your first adapter in 20 minutes — no GPU required.**

## The Problem

Frontier models require paid subscriptions or API access. Running large open-weight models locally demands expensive hardware. Research shows that small models fine-tuned for specific tasks can match or exceed general-purpose large models on those tasks — and routing architectures can direct queries to the right specialist without needing a massive generalist model.

The question LocoLLM investigates: can a system of routed, task-specific adapters on a single quantized small model approach frontier quality on well-defined tasks, running entirely on consumer hardware?

For the full argument, including the educational philosophy, the "AI Last" workflow, and why small models are better suited to the task than most people assume, see [Why LocoLLM Exists](docs/why-locollm.md).

## How It Works

```
                    +-------------------+
   User Query ----->|   LocoLLM Router  |
                    | (keyword v1,      |
                    |  classifier v2+)  |
                    +-------------------+
                           |
              +------------+-------------+
              |            |             |
              v            v             v
        +---------+  +---------+  +----------+
        |  math   |  |  code   |  | analysis |    ...future adapters
        +---------+  +---------+  +----------+
              |            |             |
              +------------+-------------+
                           |
                    +------+------+
                    | Base Model  |
                    | Qwen3-4B    |
                    | (Q4_K_M)    |
                    +-------------+
```

1. A user sends a query through the LocoLLM CLI (`loco chat` or `loco query`)
2. The router scores the query against each adapter's keywords and picks the best match
3. If no adapter matches, the base model handles the query directly
4. The selected adapter model generates the response via Ollama
5. Each adapter is a merged GGUF — LoRA weights baked into the base model at export time

## Quick Start

### Prerequisites

- Python 3.10+
- 8GB+ RAM (16GB recommended)
- [Ollama](https://ollama.com/) installed

### Installation

```bash
# Clone the repository
git clone https://github.com/michael-borck/loco-llm.git
cd loco-llm

# Install LocoLLM and all dependencies
uv sync

# Download the base model and register adapters
uv run loco setup

# List available adapters
uv run loco adapters list

# Start chatting
uv run loco chat
```

> **Tip:** If you activate the virtualenv (`source .venv/bin/activate`), you can run `loco` directly without the `uv run` prefix.

### Usage

```bash
# Interactive chat (router auto-selects adapter)
uv run loco chat

# Force a specific adapter
uv run loco chat --adapter math

# Single query mode
uv run loco query "Solve: If a store offers 30% off and then an additional 15% off the sale price, what is the total discount?"

# Check which adapter the router would pick
uv run loco route "Write a Python function to sort a list"

# Benchmark an adapter against the base model
uv run loco eval math
```

## Project Structure

```
loco-llm/
├── README.md
├── pyproject.toml
├── src/
│   └── locollm/
│       ├── __init__.py
│       ├── cli.py                  # Command-line interface
│       ├── chat_session.py         # Multi-turn chat state management
│       ├── router.py               # Keyword router (v1)
│       ├── adapter_manager.py      # Adapter loading, registry, Modelfiles
│       ├── ollama_client.py        # Ollama REST API wrapper
│       └── eval.py                 # Evaluation harness
├── adapters/
│   ├── registry.yaml               # Adapter metadata and versions
│   ├── math/
│   │   ├── gguf/                   # Merged GGUF model file
│   │   ├── training_data.jsonl
│   │   └── eval_dataset.jsonl
│   ├── code/
│   └── analysis/
├── docs/
│   ├── architecture.md
│   ├── adapter-guide.md
│   ├── training-new-adapters.md
│   ├── finetuning-primer.md
│   ├── evaluation-standards.md
│   └── adr/                        # Architecture Decision Records
├── scripts/
│   ├── train_adapter.py            # Generic fine-tuning script
│   ├── prepare_gsm8k.py            # Data prep for math adapter
│   ├── prepare_code_data.py
│   └── prepare_analysis_data.py
└── tests/
```

## Adapter Registry

Each adapter in the ecosystem is tracked in `adapters/registry.yaml`:

```yaml
adapters:
  math:
    version: "0.2.0"
    type: "merged-gguf"
    gguf_path: "math/gguf/unsloth.Q4_K_M.gguf"
    description: "Math reasoning adapter (LoRA merged, Q4_K_M)"
    authors: ["LocoLLM Team"]
    tags: ["math", "arithmetic", "reasoning"]
    eval_dataset: "eval_dataset.jsonl"
    eval_type: "numeric"
    router_keywords: ["solve", "calculate", "equation", "math", ...]
    training:
      method: "qlora"
      dataset: "GSM8K (200 examples)"
      lora_r: 16
      lora_alpha: 32
      epochs: 3
```

## Evaluation Standards

Every adapter must demonstrate measurable improvement over the base model. No exceptions. An adapter that doesn't beat the base model on its target task doesn't ship.

### Required for Every Adapter

1. **Evaluation dataset** (`eval_dataset.jsonl`): Minimum 50 test cases formatted as input/expected-output pairs
2. **Base model baseline**: The base model's score on the same dataset, run without any adapter (`loco eval <name>` does this automatically)
3. **Adapter score**: The adapter's score on the same dataset, showing measurable improvement
4. **Training log** (`TRAINING_LOG.md`): Dataset sources, size, hyperparameters, training duration, loss curves

### Scoring Metrics by Domain

| Domain Type | Primary Metric | Secondary |
|---|---|---|
| Math / Reasoning | Exact match accuracy | Step correctness |
| Code generation | Pass@1 (execution) | Syntax validity |
| Writing / Style | LLM-as-judge (rubric) | ROUGE-L |
| Classification | F1 score | Accuracy |
| Domain QA | Exact match / F1 | Retrieval overlap |

## Design Principles

**Local first.** Everything runs on consumer hardware. If it needs a cloud GPU to run inference, it doesn't belong here.

**Free compute is a superpower.** Local inference has no per-token cost. Techniques that are expensive through an API (multiple samples, longer prompts, re-reading) are effectively free here. LocoLLM exploits this aggressively.

**Measurably better.** Every adapter must demonstrate quantifiable improvement over the base model. Vibes don't count.

**Accumulative.** The project grows each semester. New adapters extend the ecosystem. Better adapters replace older ones. The evaluation harness is the source of truth.

**Simple over clever.** Start with keyword routing before building an ML classifier. Use Ollama before writing custom inference code. Complexity is earned, not assumed.

**Reproducible.** Every adapter includes its training data, config, and logs. Anyone should be able to retrain it and get comparable results.

## Roadmap

### Phase 1: Foundation (Semester 2, 2026)

- Standardize base model and quantization spec
- Build CLI tool and evaluation harness
- Create adapter development guide and templates
- Ship first 3-5 adapters from initial student cohort
- Implement keyword-based router (v1)
- Publish initial benchmark comparing LocoLLM vs base model vs frontier API
- Systematic Q4_K_M benchmarking of 3-4B models across standard tasks (filling a gap in the literature where most benchmarks only test full-precision models). See [benchmarking guide](docs/benchmarking-guide.md)

### Phase 2: Growth (Semester 1, 2027)

- ML-based router trained on accumulated query/adapter data
- Expand to 8-12 adapters covering core student task domains
- Adapter versioning and upgrade system
- Cross-adapter evaluation (does adding adapters degrade other domains?)

### Phase 3: Validation (Semester 2, 2027)

- Comprehensive benchmark paper: routed 4-bit specialists vs frontier APIs
- User study with students on quality perception and usage patterns
- Adapter composition (can two adapters cooperate on a query?)
- Explore ensemble voting within the framework
- **1.58-bit research track**: Port LocoLLM to BitNet/Falcon-Edge base models, comparing same task domains at 4-bit vs 1.58-bit (quality, memory, speed, energy)

### Phase 4: Community (2028+)

- Adapters contributed from other institutions
- Domain-specific distributions (LocoLLM-Business, LocoLLM-Health)
- Automated adapter quality testing in CI/CD
- Multi-base-model support as new small models emerge
- 1.58-bit as default pathway if tooling matures (0.4GB models on Raspberry Pi, Chromebooks, phones)

## Research Context

LocoLLM builds on several converging lines of research, and critically, these techniques are stackable rather than competing:

**Task-specific fine-tuning outperforms general models.** Predibase's LoRA Land showed fine-tuned Mistral-7B adapters beating GPT-4 on specific tasks. distil labs' 2025 benchmark of 12 small models confirmed this at the 3-4B scale: fine-tuned Qwen3-4B matched or exceeded a 120B+ teacher model on 7 of 8 tasks. Crucially, [smaller models show the largest gains from fine-tuning](https://www.distillabs.ai/blog/we-benchmarked-12-small-language-models-across-8-tasks-to-find-the-best-base-model-for-fine-tuning), meaning LocoLLM's adapter approach exploits a strength unique to the small model class, not just compensating for a weakness.

**Routing reduces cost without sacrificing quality.** RouteLLM (Ong et al., ICLR 2025) demonstrated 2x+ cost reduction by routing queries to appropriately-sized models. Routers generalize well even across model pairs they weren't trained on.

**Re-reading improves small model reasoning for free.** RE2 (Xu et al., EMNLP 2024) showed that simply repeating the question in the prompt enables pseudo-bidirectional attention in decoder-only models, improving reasoning accuracy. Reading twice is optimal. On a local model with no per-token cost, this is effectively free. This is LocoLLM's second layer, applied by default to every query.

**Ensembling small models scales performance.** "More Agents Is All You Need" (Li et al., TMLR 2024) showed majority voting across small model instances can match larger models. Llama2-13B with voting outperformed Llama2-70B on a single pass. On a local model, the only cost is time, not money. This is LocoLLM's third layer: opt-in self-consistency voting.

**Quantization preserves capability, and fine-tuning recovers the rest.** 4-bit methods (GPTQ, AWQ, GGUF) retain most model capability at a fraction of the memory, making 3-4B parameter models practical on 8GB laptops. An important caveat: most published benchmarks evaluate full-precision models, so systematic data on how 3-4B models perform specifically at Q4_K_M quantization is thin. Studies on larger models show 96-99% recovery (Red Hat), but an IJCAI 2025 study warned that smaller LLMs can see significant accuracy drops at 4-bit. LocoLLM's Phase 1 benchmarks will help fill this gap. Critically, QLoRA (Dettmers et al., NeurIPS 2023) demonstrated that fine-tuning through a frozen 4-bit base model fully recovers 16-bit performance, and newer methods like Q-BLoRA (TACL 2025) further close the gap, sometimes exceeding 16-bit baselines. Multiple domain-specific studies confirm that fine-tuned quantized small models can match or outperform larger general-purpose models in cybersecurity, medicine, mathematics, and language tasks. See [base model selection](docs/base-model-selection.md#research-viability-can-fine-tuning-make-quantized-small-models-good-specialists) for the full evidence review. Looking further ahead, [BitNet b1.58](https://github.com/microsoft/BitNet) demonstrates that models trained natively at 1.58-bit precision (ternary weights: -1, 0, +1) can match full-precision peers while using 6x less RAM and 2-3x faster inference on CPU. A 2B BitNet model fits in 0.4GB. The tooling is still maturing, but the trajectory points toward sub-1GB models running on phones and Raspberry Pis.

### The Stackable Advantage

The key insight is that local inference makes all of these techniques cheaper than they would be through an API:

| Enhancement | API Cost | Local Cost |
|---|---|---|
| Specialist adapter | Not available | Free (one-time training) |
| RE2 prompting | ~2x prompt tokens billed | Near zero |
| 5-sample voting | 5x generation cost | ~30 seconds of wall time |

A routed, prompt-enhanced, vote-verified 4-bit 4B model may genuinely approach frontier quality on well-defined tasks, running entirely on consumer hardware, for free. Testing that hypothesis is the project's central research question.

## FAQ

**Why not just use Ollama with a bigger model?**
A 70B model in 4-bit still needs around 40GB of RAM. Most student laptops have 8-16GB. LocoLLM targets the 3-4B parameter range, which fits comfortably in 4-8GB, and compensates for smaller size through task specialization. Recent benchmarks show that fine-tuned 4B models can match or exceed models 30x their size on specific tasks.

**Won't 4-bit quantization kill the fine-tuning gains?**
QLoRA (NeurIPS 2023) showed that fine-tuning through a frozen 4-bit base model matches 16-bit fine-tuning performance. Newer methods like Q-BLoRA (TACL 2025) go further, sometimes exceeding 16-bit baselines entirely. The LoRA adapters themselves stay at full precision and are small enough that this adds negligible overhead. That said, most QLoRA research targeted 7B+ models. Systematic benchmarks at the 3-4B scale with Q4_K_M quantization are sparse, which is why LocoLLM's own benchmarks are an early contribution to the field. The evidence from domain-specific studies (cybersecurity, medical QA, mathematics) consistently shows fine-tuned quantized small models matching or beating larger general-purpose models. See the [research viability analysis](docs/base-model-selection.md#research-viability-can-fine-tuning-make-quantized-small-models-good-specialists) for the full evidence chain.

**How does this compare to paying for ChatGPT?**
For many students, $20/month is a real barrier, and institutional licenses don't always cover everyone. LocoLLM is free, runs offline, keeps data private, and requires no internet connection. It won't match frontier models on everything, but for well-defined task domains, the combination of specialist fine-tuning, RE2 prompting, and self-consistency voting can get surprisingly close.

**Doesn't running 5 samples for voting make it slow?**
A 4B model on a modern laptop generates at roughly 15-30 tokens per second. A typical 200-token response takes 7-13 seconds. Five samples take 35-65 seconds. That's a real wait, but for a student working through a problem set, trading a minute for a significantly more reliable answer is a good trade. Voting is opt-in and off by default for interactive chat.

**Can I use a different base model?**
The framework is base-model-agnostic, but all adapters in the official registry target the current standard base model for a given academic year. Switching base models means retraining or verifying adapter compatibility.

**Is this only for university students?**
It started there, but the approach is general. Anyone in a resource-constrained environment can benefit from the same architecture.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Citation

```bibtex
@software{locollm2026,
  title={LocoLLM: Local Collaborative LLMs for Resource-Constrained AI Access},
  author={Michael Borck and Contributors},
  year={2026},
  url={https://github.com/michael-borck/loco-llm}
}
```
