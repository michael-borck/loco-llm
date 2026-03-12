---
title: "ADR-0006: GGUF and Ollama as Inference Standard"
---

## Status

Accepted

## Date

2026-03-07

## Context

Multiple quantisation formats and inference runtimes exist for running local LLMs. The main contenders as of early 2026:

| Format | Runtime | Platform Support | Notes |
|--------|---------|-----------------|-------|
| **GGUF** | Ollama, llama.cpp, LM Studio, GPT4All | macOS, Windows, Linux, CPU+GPU | llama.cpp native format |
| **EXL2** | ExLlamaV2, TabbyAPI | NVIDIA GPU only | Fastest tok/s on NVIDIA hardware |
| **AWQ** | vLLM, TGI, some llama.cpp support | Primarily NVIDIA GPU | Good perplexity at 4-bit |
| **GPTQ** | AutoGPTQ, vLLM, TGI | Primarily NVIDIA GPU | Older standard, being superseded |

LocoLLM targets students on diverse hardware -- MacBooks, office PCs, lab machines, personal laptops. The project also needs a deployment path simple enough that students focus on the AI problem, not the infrastructure problem.

## Decision

Standardise on **GGUF** as the model format and **Ollama** as the primary inference runtime.

### Why GGUF

**Portability.** GGUF runs on any hardware Ollama supports: NVIDIA GPUs via CUDA, Apple Silicon via Metal, AMD GPUs via ROCm, and pure CPU fallback. A student with a MacBook Air and a student with a desktop GTX 1650 use the same model file. EXL2 and AWQ are effectively NVIDIA-only, which excludes the Apple Silicon users (Poco, and a significant proportion of students).

**CPU+GPU hybrid inference.** GGUF via llama.cpp can split model layers between GPU VRAM and system RAM. On a 4 GB GPU card, layers that don't fit in VRAM spill to CPU. Performance degrades gracefully rather than failing entirely. This matters for the 4 GB floor (GTX 1050 Ti, GTX 1650) where VRAM is tight. EXL2 requires the entire model in GPU VRAM.

**Quantisation granularity.** GGUF's k-quant variants (Q4_K_M, Q5_K_M, Q3_K_M, etc.) offer fine-grained control over the quality/size tradeoff. Q4_K_M is the project standard -- it retains the vast majority of model quality while fitting comfortably in 8 GB with headroom for context. The k-quant approach uses mixed precision per tensor group, preserving quality in sensitive layers while compressing less critical ones.

**Ecosystem breadth.** GGUF models work in Ollama, LM Studio, GPT4All, llama.cpp directly, and Simon Willison's `llm` CLI. Students aren't locked into one tool. A merged GGUF adapter produced by LocoLLM's training pipeline can be loaded in any of these.

### Why Ollama

**Simplicity.** One command to install. `ollama pull` to download models. `ollama run` to chat. `ollama serve` for an API. Custom models via a two-line Modelfile pointing at a GGUF. The cognitive overhead is minimal.

**Cross-platform consistency.** Same commands, same API, same behaviour on macOS, Windows, and Linux. Students helping each other across different operating systems aren't fighting platform differences.

**Local API.** Ollama serves an OpenAI-compatible API at `localhost:11434`. AnythingLLM, Open WebUI, and other tools connect to it directly. This makes Ollama infrastructure rather than an endpoint -- other tools build on top of it.

**GPU detection.** Ollama auto-detects CUDA, Metal, and ROCm and uses the best available backend without user configuration. On Colmena, `CUDA_VISIBLE_DEVICES` assigns specific GPUs to specific instances. On a student laptop, it just works.

### Why not EXL2

EXL2 (ExLlamaV2) is genuinely faster on NVIDIA GPUs -- it saturates memory bandwidth more efficiently than llama.cpp and produces higher tok/s at equivalent quantisation. On a 2060 Super, EXL2 at 5.0 bpw would noticeably outperform GGUF Q4_K_M.

The tradeoff is portability. EXL2 is NVIDIA-only. No Apple Silicon, no CPU fallback, no AMD. The runtime (ExLlamaV2 or TabbyAPI) requires more setup than Ollama. There's no equivalent of `ollama pull` -- you download models manually from Hugging Face and configure the runtime.

For a project optimising inference speed on a known NVIDIA card, EXL2 is the right choice. For a project where students bring unknown hardware and the deployment path must be frictionless, it's the wrong choice.

### Why not AWQ

AWQ (Activation-aware Weight Quantisation) produces slightly better perplexity than GGUF at the same bit width. The quality advantage is real but small -- typically 0.5-1.5% on benchmarks. AWQ's primary runtime is vLLM, which is production-grade server software designed for high-throughput serving, not student laptops.

llama.cpp has partial AWQ support, but GGUF remains its native format and gets the most testing and optimisation. Choosing AWQ would mean either running vLLM (heavy) or running AWQ through llama.cpp (second-class support).

## Consequences

- All LocoLLM adapters are exported as merged GGUF files (Q4_K_M standard)
- Students install Ollama once and use it for all models and adapters
- Apple Silicon users (MacBook, Mac Mini, etc.) are first-class participants
- Students on 4 GB GPUs get graceful CPU+GPU hybrid rather than hard failure
- Inference speed on NVIDIA hardware is not optimal -- EXL2 would be faster. This is an accepted tradeoff for portability
- LM Studio, GPT4All, and `llm` CLI all work with LocoLLM's model files as alternative interfaces
- If Ollama adds native EXL2 support in future, the benefit becomes available without changing the project's deployment path
- LocoBench benchmarks use GGUF/Ollama, which means results reflect what Ollama users will actually experience rather than peak theoretical throughput
