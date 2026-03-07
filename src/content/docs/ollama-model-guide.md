---
title: "Ollama Model Guide for 8GB VRAM"
---

A practical guide to choosing and running models with Ollama on an 8GB VRAM card. This covers general inference use -- if you're here to fine-tune adapters, see the [fine-tuning primer](finetuning-primer.md) and [base model selection](base-model-selection.md) instead.

## The 8GB Sweet Spot

An 8GB card like an RTX 4060 comfortably handles 7-9B models at Q4_K_M quantisation, delivering 40+ tokens/second. This is the sweet spot for most users: large enough for genuine reasoning ability, small enough to leave headroom for context and OS overhead.

If you're unsure what quantisation format to use, Q4_K_M is almost always the right answer. It uses the K-quant method (mixed precision per tensor group) for significantly better accuracy than legacy formats at a similar file size. See [small model strategies](small-model-strategies.md#9-quantisation) for the full breakdown.

---

## Top Picks by Use Case

### General Purpose / Chat

| Model | Size (Q4_K_M) | Notes |
|---|---|---|
| **Llama 3.1 8B** | ~4.4GB (~6.9GB memory) | Best all-rounder for chat, knowledge, and instruction following. Apache 2.0 licensed. |
| **Mistral 7B** | ~4.1GB | Reliable workhorse. Fast inference, great for assistants. |
| **Qwen2.5 7B** | ~4.4GB | Strong multilingual and reasoning performance. |

### Reasoning / Thinking

| Model | Size (Q4_K_M) | Notes |
|---|---|---|
| **DeepSeek-R1 8B** | ~6.2GB VRAM | ~68 tok/s. Thinking is enabled by default in Ollama. |
| **Qwen3 8B** | ~5.6GB VRAM | ~41 tok/s on RTX 4060. Leads maths reasoning benchmarks at this size. Also has thinking mode. |

Both models have built-in chain-of-thought reasoning -- they think through problems before answering, which significantly improves accuracy on analytical tasks at the cost of some latency.

### Coding

| Model | Size (Q4_K_M) | Notes |
|---|---|---|
| **NVIDIA Nemotron Nano 9B** | ~5.5GB | Leads LiveCodeBench among 8GB-class models. |
| **Qwen2.5-Coder 7B** | ~4.4GB | Solid code generation, tight VRAM fit. |
| **DeepSeek-Coder 6.7B** | ~3.8GB | Specialised and efficient. |

### Compact Models (Leaves Headroom for Context)

These fit well under the 8GB ceiling, leaving room for larger context windows or running alongside other applications.

| Model | Size (Q4_K_M) | Notes |
|---|---|---|
| **Gemma 3 4B** | ~2.5GB | Google's compact model, excellent quality-to-size ratio. |
| **Phi-3 Mini 3.8B** | ~2.3GB | ~28 tok/s. Particularly strong for coding on constrained hardware. |
| **Qwen3-4B** | ~2.5GB | LocoLLM's base model. See [why we chose it](base-model-selection.md#why-qwen3-4b). |

---

## Quick Start

```bash
ollama run qwen3:8b          # reasoning + general
ollama run deepseek-r1:8b    # reasoning/thinking
ollama run llama3.1:8b       # reliable all-rounder
ollama run qwen2.5-coder:7b  # coding
```

Each command downloads the model on first run (one-time, typically 4-5GB) and starts an interactive chat session. Type `/bye` to exit.

---

## Practical Tips

**Start with two models.** `deepseek-r1:8b` and `qwen3:8b` are complementary: Qwen3 8B for maths and structured reasoning, DeepSeek-R1 8B for creative and general tasks. Both have built-in thinking capabilities and get you running in under five minutes.

**Watch your VRAM.** Only one model loads at a time by default. If you switch models frequently, Ollama keeps the previous model in memory for fast switching -- this can exceed 8GB with two large models. Use `ollama stop <model>` to unload explicitly.

**Context window matters.** A 7B model at Q4_K_M uses ~4.5GB for weights, but the KV cache grows with conversation length. On 8GB cards, keep context windows at 4,096-8,192 tokens to avoid spilling to system RAM. See [KV cache](small-model-strategies.md#kv-cache-the-hidden-vram-cost) for details.

**Bigger model at lower quant beats smaller model at higher quant** for general inference. More parameters give better reasoning ability. If your card can fit a 7B at Q4_K_M, that's almost always better than a 3B at Q8. The exception is fine-tuning workflows (like LocoLLM's) where VRAM headroom for adapters and training matters more -- see [base model selection](base-model-selection.md#why-not-7b).

---

## Relation to LocoLLM

LocoLLM standardises on **Qwen3-4B** at Q4_K_M -- deliberately smaller than the models above. This isn't because 4B is "best" for inference. It's because LocoLLM's architecture requires headroom for adapter swapping, KV cache, and training on 8GB machines. The [tunability inversion](base-model-selection.md#the-tunability-inversion) means fine-tuned 4B models close the gap to larger general-purpose models anyway.

If you're exploring local AI for personal use (not fine-tuning), the 7-9B models on this page are the right starting point.

---

## What's Installed on the Lab Machines

These are the models currently pulled on the LocoLLM lab machines, categorised by primary use case. Use `ollama list` to see what's available on your machine.

### General Purpose / Chat

| Model | Size | Notes |
|---|---|---|
| `mistral:latest` | 4.4 GB | **Best in class.** Reliable workhorse. Fast, great for assistants. |
| `llama3.2:latest` | 2.0 GB | Compact Meta model. Good general capability at small size. |
| `gemma3:latest` | 3.3 GB | Google's compact model. Also has built-in vision capability. |
| `granite3.2:latest` | 4.9 GB | IBM's open model. Strong on enterprise and structured tasks. |
| `granite3.3:latest` | 4.9 GB | Updated Granite. Improved reasoning over 3.2. |
| `tinyllama:latest` | 637 MB | Tiny 1.1B model. Very fast, useful for testing pipelines and quick prototyping. |

### Reasoning / Thinking

| Model | Size | Notes |
|---|---|---|
| `qwen3:latest` | 5.2 GB | **Best in class.** Leads maths reasoning benchmarks at this size. Has thinking mode. |
| `qwen3.5:4b` | 3.4 GB | Newer Qwen generation. Compact with strong reasoning. |
| `deepseek-r1:8b` | 4.9 GB | Built-in chain-of-thought. Strong on analytical and creative tasks. |
| `phi4-mini-reasoning:3.8b` | 3.2 GB | Microsoft's reasoning-optimised Phi-4. Compact and capable. |
| `cogito:latest` | 4.9 GB | Deep Cogito model with thinking capability. |
| `phi4-mini:3.8b` | 2.5 GB | General-purpose Phi-4. Solid reasoning for its size. |
| `phi3:3.8b` | 2.2 GB | Previous-generation Phi. Still capable, slightly smaller footprint. |

### Coding

| Model | Size | Notes |
|---|---|---|
| `qwen2.5-coder:7b` | 4.7 GB | **Best in class.** Strong code generation, tight VRAM fit. |
| `deepseek-coder:6.7b` | 3.8 GB | Specialised and efficient. Good for code explanation. |
| `deepseek-coder:1.3b` | 776 MB | Tiny code model. Fast completions, useful for lightweight tasks. |
| `nemotron-mini:latest` | 2.7 GB | NVIDIA's compact model. Good at coding and structured output. |

### Vision / Image Understanding

| Model | Size | Notes |
|---|---|---|
| `moondream:latest` | 1.7 GB | Tiny vision model. Fast image description and visual QA. |
| `qwen2.5vl:3b` | 3.2 GB | Compact Qwen vision-language model. Good quality for the size. |
| `qwen2.5vl:7b` | 6.0 GB | **Best in class.** Strong image reasoning and document understanding. |
| `llava:7b` | 4.7 GB | The original open vision-language model. Solid general image understanding. |
| `llava-llama3:8b` | 5.5 GB | LLaVA built on Llama 3. Newer base model than original LLaVA. |
| `bakllava:7b` | 4.7 GB | LLaVA variant built on Mistral. |

### Best Overall

If you only install one model, make it **`qwen3:latest`**. It has the strongest reasoning of anything installed, handles general chat well, and its thinking mode means it can work through complex problems step by step. At 5.2 GB it fits comfortably on 8GB cards with room for context.

If you install two, add **`qwen2.5-coder:7b`** for dedicated coding work. The combination covers most use cases well.

### Quick Reference by Size

For choosing based on available memory:

| Size tier | Models |
|---|---|
| **Under 1 GB** | `tinyllama` (637 MB), `deepseek-coder:1.3b` (776 MB) |
| **1-2 GB** | `moondream` (1.7 GB), `llama3.2` (2.0 GB) |
| **2-3 GB** | `phi3` (2.2 GB), `phi4-mini` (2.5 GB), `nemotron-mini` (2.7 GB) |
| **3-4 GB** | `phi4-mini-reasoning` (3.2 GB), `qwen2.5vl:3b` (3.2 GB), `gemma3` (3.3 GB), `qwen3.5:4b` (3.4 GB), `deepseek-coder:6.7b` (3.8 GB) |
| **4-5 GB** | `mistral` (4.4 GB), `qwen2.5-coder:7b` (4.7 GB), `llava:7b` (4.7 GB), `bakllava` (4.7 GB), `cogito` (4.9 GB), `granite3.2` (4.9 GB), `granite3.3` (4.9 GB), `deepseek-r1:8b` (4.9 GB) |
| **5+ GB** | `qwen3` (5.2 GB), `llava-llama3:8b` (5.5 GB), `qwen2.5vl:7b` (6.0 GB) |

---

## Image Models on 8GB VRAM

### Image Understanding (Vision / Multimodal)

Vision-language models accept images as input alongside text -- describe what's in a photo, answer questions about a diagram, extract text from a screenshot. Ollama supports these natively.

| Model | Size (Q4_K_M) | Notes |
|---|---|---|
| **Moondream** | ~1.8B | Tiny and fast. Good for basic image description and visual QA. Fits easily alongside other workloads. |
| **Gemma 3 4B** | ~2.5GB | Built-in vision capability -- processes images natively without a separate vision encoder. Strong quality-to-size ratio. |
| **MiniCPM-V** | ~3-4GB | Compact multimodal model. Punches above its weight on visual reasoning. |
| **LLaVA 7B** | ~4.5GB | The original open vision-language model. Solid general image understanding. |
| **BakLLaVA** | ~4.5GB | LLaVA variant built on Mistral. Similar capability, different base model strengths. |
| **Qwen2.5-VL 7B** | ~4.5GB | Qwen's vision-language model. Strong reasoning about images and document understanding. |

```bash
ollama run moondream        # tiny, fast image understanding
ollama run gemma3:4b        # compact with built-in vision
ollama run llava:7b         # solid general vision
```

To use vision models, pass an image path in the chat:

```
>>> What's in this image? /path/to/photo.jpg
```

**Practical note:** Vision models use more memory than text-only models of the same parameter count because they include a vision encoder alongside the language model. Moondream and Gemma 3 4B are the safest choices on 8GB cards if you need headroom.

### Image Generation

Image generation uses a different model architecture (diffusion models) and does not run through Ollama. These tools have their own ecosystems but share the same GPU.

| Tool | Notes |
|---|---|
| **ComfyUI** | Node-based workflow editor for Stable Diffusion and Flux models. Powerful and flexible. The standard for advanced users. |
| **Stable Diffusion WebUI (Forge)** | Fork of Automatic1111's WebUI optimised for lower VRAM. Simpler interface than ComfyUI. Good starting point. |
| **Fooocus** | Minimal interface inspired by Midjourney. Designed for users who want results without configuration. |
| **Draw Things** | Native macOS/iOS app for Stable Diffusion. Uses Metal acceleration on Apple Silicon. |

**Models that fit 8GB VRAM:**

| Model | VRAM | Notes |
|---|---|---|
| **Stable Diffusion 1.5** | ~4GB | Fast, huge community of fine-tunes and LoRAs. Lower resolution (512x512 native). |
| **SDXL** | ~6-7GB | Higher quality, 1024x1024 native. Tight fit on 8GB -- use Forge or ComfyUI with memory optimisations enabled. |
| **SDXL Turbo / Lightning** | ~6-7GB | Distilled SDXL variants that generate in 1-4 steps instead of 20-50. Much faster, slightly lower quality. |
| **Flux Schnell** | ~6-8GB | Latest generation. High quality, fast. Fits on 8GB with quantisation and offloading. |
| **Stable Diffusion 3.5 Medium** | ~6GB | Multimodal Diffusion Transformer (MMDiT) architecture. Good balance of quality and VRAM. |

**Practical note:** Image generation and LLM inference compete for the same VRAM. Don't run both simultaneously on an 8GB card -- unload your Ollama model first (`ollama stop <model>`) before generating images, and vice versa.

---

*Performance figures are approximate and vary by hardware, driver version, and Ollama release. Last reviewed: March 2026.*
