# Fine-Tuning Primer

A conceptual foundation for contributors who are new to fine-tuning. Read this before diving into the [Adapter Development Guide](adapter-guide.md).

## What Is Fine-Tuning?

When you use a language model, you're working with a neural network that has billions of **parameters** — numerical weights learned during a massive initial training phase called **pretraining**. Pretraining is what makes the model "know" language: it has read billions of words and learned patterns for generating coherent, relevant text.

**Prompting** is when you give the model instructions at inference time — "solve this math problem step by step" — and hope it follows them. This works surprisingly well for many tasks, but it has limits. The model's behavior is constrained by what it learned during pretraining, and you're limited to what you can fit in a single prompt. You can't teach it new skills or consistently change how it approaches a problem class.

**Fine-tuning** goes further. It takes a pretrained model and continues training it on a smaller, task-specific dataset, actually updating the model's parameters so it internalizes new patterns. After fine-tuning, the model doesn't need elaborate prompting to perform well on the target task — the behavior is baked in.

There are two broad approaches:

| Approach | What changes | Cost | When to use |
|---|---|---|---|
| **Full fine-tuning** | All parameters | Very high (needs large GPU, lots of memory) | When you have massive data and compute |
| **Parameter-efficient fine-tuning (PEFT)** | A small subset of parameters | Low (runs on consumer hardware) | When you want specialist behavior without the cost |

LocoLLM uses PEFT exclusively, specifically a technique called **LoRA**. This is why adapters are only 20-30MB instead of several gigabytes — you're training a small addition to the model rather than rewriting the whole thing.

### Why LocoLLM Uses Adapters

The adapter approach gives LocoLLM a key architectural advantage: the base model stays loaded in memory, and swapping a LoRA adapter takes milliseconds. You get the effect of multiple specialist models while only keeping one model in RAM. For a system targeting 8GB laptops, this is the difference between "possible" and "impossible." See [architecture.md](architecture.md) for the full design.

## LoRA in Plain English

**LoRA (Low-Rank Adaptation)** is the technique behind every LocoLLM adapter. Here's the intuition.

A pretrained model's knowledge lives in large weight matrices — tables of numbers that determine how the model transforms input into output. During full fine-tuning, you'd update every number in these matrices. LoRA's insight is that the *change* you need to make for a specific task can be represented by much smaller matrices.

Think of it like this: the base model is a detailed city map. Fine-tuning for math reasoning doesn't require redrawing the entire map — it's more like adding a transparent overlay that highlights the math-relevant routes. LoRA creates that overlay.

Technically, LoRA decomposes the weight update into two small matrices whose product approximates the full update. The size of these matrices is controlled by a parameter called **rank**.

### Rank and Alpha: The Capacity Knobs

Two hyperparameters define a LoRA adapter's capacity:

- **Rank** (`lora_rank`): Controls how much the adapter can learn. Higher rank = more capacity to capture complex patterns, but also a larger adapter file and more risk of overfitting. LocoLLM defaults to rank 16, which is a solid middle ground. If your domain needs the model to learn many distinct new behaviors, you might try rank 32. If it's a narrow formatting task, rank 8 might suffice.

- **Alpha** (`lora_alpha`): A scaling factor that controls how strongly the adapter influences the base model. The ratio alpha/rank determines the effective learning rate for the adapter weights. LocoLLM defaults to alpha 32 (with rank 16), giving a scaling factor of 2. You rarely need to change this.

The standard LocoLLM configuration targets the model's attention layers (`q_proj`, `v_proj`, `k_proj`, `o_proj`), which is where most task-specific behavior lives. See the [architecture doc](architecture.md#lora-low-rank-adaptation) for the exact config.

### QLoRA: LoRA on Quantized Models

LocoLLM's base model is stored in **4-bit quantized** format (Q4_K_M) to fit in limited RAM. You might wonder: can you fine-tune a model that's been compressed this aggressively?

Yes. **QLoRA** (Quantized LoRA) keeps the base model frozen in 4-bit while training the LoRA adapter weights at full precision. The key finding from the original QLoRA paper (Dettmers et al., NeurIPS 2023) is that this matches the performance of fine-tuning a full-precision model. The quantized base provides the foundation; the full-precision adapter provides the task-specific refinement.

This is why LocoLLM can train adapters on Google Colab's free T4 GPU or even on a Mac with MPS — the memory footprint during training is dramatically smaller than full fine-tuning.

## Data Is the Bottleneck

If there's one thing to internalize from this primer, it's this: **the quality of your training data matters more than anything else you'll decide during adapter development**. More than rank, more than learning rate, more than the number of epochs.

The QLoRA paper demonstrated that a model fine-tuned on just 9,000 high-quality examples outperformed one trained on 450,000 lower-quality examples on human evaluation. Quality isn't just "slightly better" — it's the dominant factor.

### What Makes a Good Training Example

Every example in your dataset is teaching the model what "good" looks like for your domain. Each one should be something you'd be satisfied receiving as a response. Specifically:

- **The output should be correct.** Obvious, but easy to let slip when generating or curating at scale. One wrong answer in your training data teaches the model to produce wrong answers.
- **The output should demonstrate the reasoning style you want.** If you want step-by-step math solutions, every training output should show steps. The model learns the pattern, not just the answer.
- **Difficulty should be varied.** A dataset of only easy problems produces a model that's confident on easy problems and lost on hard ones. Include a realistic distribution.
- **Edge cases matter.** The model will encounter them in the real world, so it needs to have seen them in training.

The [Adapter Development Guide](adapter-guide.md#data-quality-checklist) has a concrete checklist. Use it.

### Synthetic Data: Powerful but Risky

Using a frontier model (like GPT-4 or Claude) to generate training examples is practical and common. LocoLLM explicitly supports this workflow. But synthetic data has specific risks:

- **Homogeneity**: A single model tends to produce examples in a similar style and at a similar difficulty level. You get breadth without true diversity. Vary your generation prompts aggressively.
- **Inherited errors**: The generating model has its own biases and mistakes. Always review a sample of generated examples manually — the [contributing guide](https://github.com/michael-borck/loco-llm/blob/main/CONTRIBUTING.md#synthetic-data-generation) recommends at least 10%.
- **Subtle incorrectness**: For technical domains (math, code), synthetic outputs can look plausible but be wrong. Verify outputs, especially for tasks where you can check correctness programmatically.

### Data Contamination

**Data contamination** occurs when examples from your evaluation benchmark leak into your training set. This makes your benchmark scores meaningless — the model isn't generalizing, it's memorizing.

This is easy to do accidentally, especially when pulling from public datasets that overlap. LocoLLM's evaluation harness tracks benchmark file hashes to detect changes, and PR reviewers check for contamination. Keep your training set and benchmark set strictly separate. The [evaluation standards](evaluation-standards.md) explain the integrity requirements.

## The Training Loop

You don't need to understand the math of gradient descent to fine-tune an adapter, but having a mental model of what happens during training helps you diagnose problems.

### What Happens During Training

1. The training script loads a batch of examples from your dataset.
2. For each example, it feeds the instruction and input to the model and compares the model's output to the expected output.
3. The difference between the model's output and the expected output is measured as **loss** — a number that represents how wrong the model is.
4. The LoRA adapter weights are adjusted slightly to reduce that loss (the base model weights stay frozen).
5. This repeats for every batch in the dataset. One complete pass through the entire dataset is called an **epoch**.

### Reading Loss Curves

The training script logs the loss over time. Learning to read this curve is one of the most useful diagnostic skills:

- **Healthy convergence**: Loss drops steeply early on, then gradually flattens. This means the model is learning the easy patterns first, then making smaller refinements. This is what you want.
- **Overfitting**: Training loss keeps decreasing, but when you test on held-out examples, performance degrades. The model is memorizing your specific training examples instead of learning generalizable patterns. Fix: more diverse training data, fewer epochs, or add dropout.
- **Underfitting**: Loss barely decreases from start to finish. The model isn't learning. Fix: increase learning rate, check that your data format matches what the training script expects, or increase LoRA rank.
- **Instability**: Loss jumps around erratically. Fix: reduce learning rate.

The [Adapter Development Guide](adapter-guide.md#monitoring-training) covers what to watch for in more detail.

### Epochs and Learning Rate Intuition

**Epochs**: How many times the model sees the full dataset. With a small dataset (500 examples), you typically need 3-5 epochs — the model needs multiple passes to learn the patterns. With a large dataset (5000+), 1-2 epochs may suffice because there's enough variety in a single pass.

**Learning rate**: How big a step the model takes when adjusting weights. Too high and training is unstable (overshooting). Too low and the model barely learns (tiny steps that never get anywhere). LocoLLM defaults to 2e-4, which is the standard starting point for QLoRA. You almost never need to increase it; occasionally you need to decrease it.

The [contributing guide](https://github.com/michael-borck/loco-llm/blob/main/CONTRIBUTING.md#hyperparameter-guidance) has a table of defaults and when to adjust them.

## Hardware Realities

Fine-tuning with QLoRA is designed for consumer hardware, but "consumer hardware" still has constraints.

### Memory Math

For a 4B parameter model at 4-bit quantization:
- **Base model in memory**: ~2.5GB (4B params x 4 bits / 8 bits per byte, plus overhead)
- **LoRA adapter weights**: ~50-100MB at rank 16 (these are full precision)
- **Optimizer states and gradients**: ~200-500MB
- **Activations and batch data**: Varies with batch size and sequence length

**Total training footprint**: Roughly 4-6GB of GPU/accelerator memory. This fits on:

| Hardware | VRAM/Memory | Training time (500 examples, 3 epochs) | Notes |
|---|---|---|---|
| NVIDIA T4 (Colab free) | 16GB | 2-4 hours | Most accessible option |
| RTX 3060/4060 | 8-12GB | 1-2 hours | Good consumer GPU |
| RTX 3090/4090 | 24GB | 30-60 min | Fast, handles larger batches |
| Apple M1/M2 (MPS) | Shared RAM | 3-6 hours | Works, but slower than CUDA GPUs |

### Batch Size Impact

**Batch size** is how many training examples the model processes before updating weights. Larger batches give more stable gradient estimates but use more memory.

- **Batch size 1-2**: Minimal memory, noisier updates, slower convergence
- **Batch size 4** (LocoLLM default): Good balance for 8-12GB GPUs
- **Batch size 8-16**: Smoother training, but needs 16GB+ VRAM

If you run out of memory during training, the first thing to try is reducing batch size. The training will take longer but will still work.

## When Things Go Wrong

Most first-time adapters don't pass the evaluation bar on the first try. Expect 2-3 training iterations. This is normal, not a sign of failure.

### Diagnosing Underperformance

When your adapter doesn't beat the base model by enough (or at all), work through this decision tree:

**1. Is it a data problem?** (Most likely — check this first)
- Are training outputs actually correct? Spot-check 20 random examples.
- Is the dataset diverse enough, or is it 500 variations of the same thing?
- Do training examples match the style and format you're evaluating on?
- Is the dataset large enough for the domain complexity?

**2. Is it a hyperparameter problem?**
- Did the loss curve look healthy? (If not, see the loss curve section above)
- Was the learning rate too high (instability) or too low (underfitting)?
- Is the LoRA rank too low for the domain complexity? Try rank 32.
- Too many epochs (overfitting) or too few (underfitting)?

**3. Is it a scope problem?**
- Is the domain too broad? "All of mathematics" is a PhD thesis. "Multi-step arithmetic word problems" is an adapter.
- Does the base model fundamentally lack the capability you're trying to build on? Adapters amplify existing abilities; they can't create entirely new ones from scratch.

### Iteration Is the Process

The [Adapter Development Guide](adapter-guide.md#iteration-cycle) walks through the specific iteration workflow: analyze failures, add targeted training data, retrain, re-evaluate. Each cycle should be informed by the previous one's failure analysis — don't just "add more data" without understanding *why* the model is failing.

## Next Steps

You now have the conceptual foundation. Here's where to go from here:

- **[Adapter Development Guide](adapter-guide.md)**: The step-by-step practical guide for building your first adapter, from baseline testing through submission.
- **[Contributing Guide](https://github.com/michael-borck/loco-llm/blob/main/CONTRIBUTING.md)**: The full contribution workflow including proposal, data requirements, evaluation bar, and PR checklist.
- **[Architecture](architecture.md)**: How LocoLLM's components (router, adapter manager, inference pipeline, evaluation harness) fit together.
- **[Evaluation Standards](evaluation-standards.md)**: What "good enough" means, how benchmarks work, and how scoring varies by domain type.
- **[Benchmarking Guide](benchmarking-guide.md)**: Methodology for comparing adapters, base models, and quantization levels.
- **[Base Model Selection](base-model-selection.md)**: Why LocoLLM uses the current base model, the research evidence for fine-tuning quantized small models, and the decision framework for future model changes.
