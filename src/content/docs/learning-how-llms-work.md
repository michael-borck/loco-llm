---
title: "Learning How LLMs Work"
---

LocoLLM's docs cover how to use and fine-tune small language models. This page is for contributors and students who want to go deeper -- to understand what's happening inside the model, not just how to prompt or train it.

The resources below are ordered roughly from foundational to advanced. You don't need any of this to contribute an adapter, but understanding the internals makes you a better debugger, a better data curator, and a more confident researcher.

---

## Start Here: Karpathy's "Zero to Hero"

Andrej Karpathy (former OpenAI, Tesla AI director) has produced the single best free resource for understanding neural networks and language models from first principles. His approach is to build everything from scratch in code, explaining the maths as it becomes necessary rather than front-loading theory.

**Neural Networks: Zero to Hero** (YouTube series)
https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ

The series progresses through:
1. Backpropagation and training basics (micrograd)
2. Language modelling fundamentals
3. Building a GPT from scratch
4. Tokenisation (BPE)
5. Pre-training and fine-tuning

Watch it at 1.5x, pause to run the code, and you'll understand more about how LLMs work than most people who use them professionally.

---

## Build It from Scratch

The best way to understand a system is to build one. These repos are designed for exactly that.

### micrograd
https://github.com/karpathy/micrograd

A tiny autograd engine -- automatic differentiation and backpropagation in ~100 lines of Python. This is the foundation. Every neural network, including every LLM, trains using the same principles implemented here. If you've never understood how gradients flow through a network, start with this.

### minbpe
https://github.com/karpathy/minbpe

A minimal implementation of Byte Pair Encoding (BPE) tokenisation. Tokenisation is the first thing that happens to your input and one of the most common sources of surprising model behaviour. This repo shows you exactly how text becomes tokens and why some words get split in unexpected ways.

### nanoGPT
https://github.com/karpathy/nanoGPT

A complete GPT implementation in ~300 lines of PyTorch. You can train a small character-level language model on your laptop and watch it learn to generate text. This is a GPT-2 architecture -- the same fundamental design that underlies modern LLMs, just smaller. If you can understand nanoGPT, you understand the core of every model LocoLLM runs.

### build-nanogpt
https://github.com/karpathy/build-nanogpt

The companion repo to the "Let's build GPT from scratch" video lecture. More structured than nanoGPT, designed to be followed step by step alongside the video.

### llm.c
https://github.com/karpathy/llm.c

GPT-2 training implemented in pure C and CUDA -- no PyTorch, no frameworks. This is for understanding what the frameworks abstract away: memory layout, kernel launches, GPU parallelism. Not a starting point, but a rewarding deep dive once you understand the Python-level implementations.

---

## Comprehensive Courses and Books

These are more structured than individual repos -- closer to textbooks or university courses.

### LLMs from Scratch
https://github.com/rasbt/LLMs-from-scratch

Sebastian Raschka's companion repo for *Build a Large Language Model (From Scratch)*. Walks through the complete process of building, pre-training, and fine-tuning a GPT-style model with detailed explanations at every step. More thorough and methodical than nanoGPT -- good for learners who prefer structured progression over "read the code."

### LLM Course
https://github.com/mlabonne/llm-course

Maxime Labonne's comprehensive course covering the full LLM lifecycle: architecture, pre-training, supervised fine-tuning, RLHF, quantisation, deployment, and evaluation. Particularly relevant to LocoLLM's work because it covers fine-tuning and quantisation in practical detail, with runnable notebooks. The quantisation section is one of the best free treatments of the topic.

### Smol Course
https://github.com/huggingface/smol-course

HuggingFace's practical course specifically focused on small language models. Covers instruction tuning, preference alignment, synthetic data generation, and efficient inference -- all in the context of models small enough to train on consumer hardware. Directly relevant to LocoLLM's mission. Uses HuggingFace's SmolLM models but the techniques transfer to any small model.

---

## Understanding Specific Architectures

### Llama 3 from Scratch
https://github.com/naklecha/llama3-from-scratch

Implements Llama 3 inference from scratch -- loading weights manually, implementing attention (including grouped query attention and rotary positional embeddings), and generating text token by token. If you want to understand what makes modern architectures different from the original GPT design, this is a clear and readable implementation.

---

## Connecting This to LocoLLM

If you work through even a subset of these resources, you'll have a much richer understanding of what LocoLLM's components are doing:

- **Tokenisation** (minbpe) explains why the same word sometimes gets different results depending on context, and why token count matters more than word count for context windows.
- **Attention** (nanoGPT, Llama 3 from scratch) explains why LoRA targets the attention projection layers (`q_proj`, `v_proj`, `k_proj`, `o_proj`) -- these are where the model decides what to pay attention to.
- **Training loops** (nanoGPT, LLMs from Scratch) explain the loss curves, learning rates, and overfitting discussed in the [fine-tuning primer](finetuning-primer.md).
- **Quantisation** (LLM Course) explains why Q4_K_M works as well as it does, and why the [quantisation cliff](base-model-selection.md#important-caveat-most-benchmarks-test-full-precision) gets steeper at smaller model sizes.

None of this is required reading. But the contributors who understand the internals consistently produce better adapters, catch data quality issues faster, and ask more productive questions when things go wrong.

---

*Resources listed here are free and open source. Last reviewed: March 2026.*
