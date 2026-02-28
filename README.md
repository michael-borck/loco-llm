# LocoLLM

### Local Collaborative LLMs -- Frontier AI on a Student Budget

> *"Crazy enough to work."*

LocoLLM is an open-source framework for building a routed collection of task-specific fine-tuned small language models that run entirely on consumer hardware. Instead of relying on expensive frontier API access, LocoLLM combines a single quantized base model with lightweight LoRA adapters, each fine-tuned for a specific task domain, and a simple router that directs queries to the best-suited specialist.

The project is designed to be built collaboratively, semester by semester, by university students. Each cohort contributes new specialist adapters, improved evaluation benchmarks, and better routing logic. The result is a growing ecosystem of local AI capability that anyone can install on a laptop.

## The Problem

Access to capable AI is becoming a digital divide issue. Frontier models require paid subscriptions or API access. Running large open-weight models locally demands expensive hardware. Students, researchers, and practitioners in resource-constrained settings are left behind.

Meanwhile, research shows that small models fine-tuned for specific tasks can match or exceed general-purpose large models on those tasks. And routing architectures can direct queries to the right specialist without needing a massive general-purpose model for everything.

LocoLLM connects these ideas into a practical, local-first system. For the full argument, including the educational philosophy, the "AI Last" workflow, and why small models are better suited to the task than most people assume, see [Why LocoLLM Exists](docs/why-locollm.md).

## How It Works

```
                    +-------------------+
   User Query ----->|   LocoLLM Router  |
                    | (lightweight      |
                    |  classifier)      |
                    +-------------------+
                           |
              +------------+-------------+------------+
              |            |             |            |
              v            v             v            v
        +---------+  +---------+  +---------+  +---------+
        | Adapter |  | Adapter |  | Adapter |  | Adapter |
        |  Math   |  |  Code   |  | Writing |  | Domain  |
        | Reason. |  |  Gen.   |  | Assist. |  |   QA    |
        +---------+  +---------+  +---------+  +---------+
              |            |             |            |
              +------------+-------------+------------+
                           |
                    +------+------+
                    | Base Model  |
                    | (4-bit      |
                    |  quantized) |
                    +-------------+
                           |
                    +------+------+
                    | Inference   |
                    | Enhancements|
                    | RE2 + Vote  |
                    +-------------+
```

1. A user sends a query through the LocoLLM CLI
2. The router classifies the query and selects the most appropriate LoRA adapter
3. The adapter is hot-swapped onto the base model (the base stays in memory)
4. The prompt is constructed with RE2 (query re-reading) applied by default
5. The response is generated (optionally: multiple samples with majority voting)
6. Only the small adapter file changes between queries, not the full model

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

# Install LocoLLM
pip install -e .

# Download the base model
loco setup

# List available adapters
loco adapters list

# Install adapters relevant to your coursework
loco adapters install math-reasoning code-python writing-academic

# Start chatting
loco chat
```

### Usage

```bash
# Interactive chat (router auto-selects adapter, RE2 prompting on by default)
loco chat

# Force a specific adapter
loco chat --adapter math-reasoning

# Single query mode
loco query "Solve: If a store offers 30% off and then an additional 15% off the sale price, what is the total discount?"

# Maximum quality: adapter + RE2 + self-consistency voting (5 samples)
loco query "Solve: ..." --votes 5

# Benchmark an adapter against the base model
loco eval math-reasoning --benchmark standard
```

## Project Structure

```
locollm/
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
├── src/
│   └── locollm/
│       ├── __init__.py
│       ├── cli.py                  # Command-line interface
│       ├── router/
│       │   ├── __init__.py
│       │   ├── base.py             # Router base class
│       │   ├── keyword.py          # Simple keyword router (v1)
│       │   └── classifier.py       # ML-based router (v2+)
│       ├── adapter_manager.py      # Adapter loading, swapping, registry
│       ├── inference.py            # Ollama / llama.cpp integration
│       └── eval/
│           ├── __init__.py
│           ├── harness.py          # Standard evaluation framework
│           └── benchmarks/         # Per-domain test sets
├── adapters/
│   ├── registry.yaml               # Adapter metadata and versions
│   ├── math-reasoning/
│   │   ├── adapter_config.json
│   │   ├── adapter_model.safetensors
│   │   ├── training/
│   │   │   ├── dataset.jsonl
│   │   │   ├── train_config.yaml
│   │   │   └── TRAINING_LOG.md
│   │   └── eval/
│   │       ├── benchmark.jsonl     # 50+ test cases
│   │       └── results.json
│   └── ...
├── docs/
│   ├── why-locollm.md
│   ├── architecture.md
│   ├── adapter-guide.md
│   ├── evaluation-standards.md
│   ├── base-model-selection.md
│   ├── benchmarking-guide.md
│   └── semester-reports/
└── scripts/
    ├── fine_tune.py                # Standardized training script
    ├── evaluate.py                 # Run benchmarks
    └── export_adapter.py           # Package adapter for distribution
```

## Adapter Registry

Each adapter in the ecosystem is tracked in `adapters/registry.yaml`:

```yaml
adapters:
  math-reasoning:
    version: "1.2.0"
    base_model: "Qwen/Qwen3-4B-Instruct"
    quantization: "Q4_K_M"
    lora_rank: 16
    created: "2026-S2"
    authors: ["Team Alpha, ISYS6020"]
    benchmark_score: 0.72
    base_model_score: 0.41
    improvement: "+75.6%"
    description: "Arithmetic and word problem reasoning"
    tags: ["math", "reasoning", "word-problems"]
    size_mb: 24
```

## Evaluation Standards

Every adapter must demonstrate measurable improvement over the base model. No exceptions. An adapter that doesn't beat the base model on its target task doesn't ship.

### Required for Every Adapter

1. **Domain benchmark** (`eval/benchmark.jsonl`): Minimum 50 test cases formatted as input/expected-output pairs
2. **Base model baseline**: The base model's score on the same benchmark, run without any adapter
3. **Adapter score**: The adapter's score on the same benchmark
4. **Out-of-domain check**: Score on at least one other domain's benchmark to confirm the adapter doesn't degrade general capability
5. **Training log** (`TRAINING_LOG.md`): Dataset sources, size, hyperparameters, training duration, loss curves

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
  author={The 80-20 Workshop and Curtin University Contributors},
  year={2026},
  url={https://github.com/michael-borck/loco-llm}
}
```
