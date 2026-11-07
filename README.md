# LocoLLM

<!-- BADGES:START -->
[![collaborative](https://img.shields.io/badge/-collaborative-blue?style=flat-square)](https://github.com/topics/collaborative) [![consumer-hardware](https://img.shields.io/badge/-consumer--hardware-blue?style=flat-square)](https://github.com/topics/consumer-hardware) [![lora-adapters](https://img.shields.io/badge/-lora--adapters-blue?style=flat-square)](https://github.com/topics/lora-adapters) [![language-model](https://img.shields.io/badge/-language--model-blue?style=flat-square)](https://github.com/topics/language-model) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![routing](https://img.shields.io/badge/-routing-blue?style=flat-square)](https://github.com/topics/routing)
<!-- BADGES:END -->

### Local Collaborative LLMs: Frontier AI on a Student Budget

LocoLLM is an open-source framework for a routed collection of task-specific small language models that run entirely on consumer hardware. One quantized base model, lightweight LoRA adapters per domain, and a router that sends each query to the best specialist.

**Live site:** [locollm.org](https://locollm.org) — why it exists, adapter guides, evaluation standards, architecture decisions.
**Train your first adapter in 20 minutes, no GPU:** [Colab notebook](https://colab.research.google.com/github/michael-borck/loco-llm/blob/main/notebooks/train_math_adapter.ipynb).

## Quick start

Requires Python 3.10+, 8 GB+ RAM, and [Ollama](https://ollama.com/).

```bash
git clone https://github.com/michael-borck/loco-llm.git
cd loco-llm
uv sync
uv run loco setup
uv run loco adapters list
uv run loco chat
```

```bash
# Force a specific adapter
uv run loco chat --adapter math

# Single query
uv run loco query "If a store offers 30% off then 15% off the sale price, what is the total discount?"

# See which adapter the router picks
uv run loco route "Write a Python function to sort a list"

# Benchmark an adapter against the base model
uv run loco eval math
```

If you activate the virtualenv (`source .venv/bin/activate`), run `loco` without the `uv run` prefix.

## Design principles

Local first. Measurably better than the base model or it does not ship. Accumulative across semesters. Simple over clever. Reproducible, with data, config, and logs.

## Licence

MIT. See [LICENSE](LICENSE).

## Citation

```bibtex
@software{locollm2026,
  title={LocoLLM: Local Collaborative LLMs for Resource-Constrained AI Access},
  author={Michael Borck and Contributors},
  year={2026},
  url={https://github.com/michael-borck/loco-llm}
}
```
