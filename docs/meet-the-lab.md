# Meet the Lab

LocoLLM is built, trained, and tested on three machines. None of them are new. All of them were sourced secondhand. That's the point.

The naming follows the project's Spanish thread: Cerebro (brain), Burro (donkey), and Poco (a little). The brain thinks fast, the donkey carries heavy loads, and the little one connects you to both.

---

## Poco

**The MacBook M1 -- Remote Terminal and Apple Silicon Testbed**

| | |
|---|---|
| **Chip** | Apple M1 |
| **Memory** | 16 GB unified (shared CPU/GPU) |
| **Storage** | 256 GB SSD |
| **OS** | macOS |
| **Role** | Remote access to Cerebro and Burro, Apple Silicon compatibility testing |

Poco means "a little" in Spanish. It doesn't do the heavy lifting, but it's how you reach the machines that do.

Day to day, Poco is a remote terminal. SSH into Cerebro for training and inference, SSH into Burro for overnight jobs, monitor progress, pull results. Portable, silent, works from anywhere.

Its secondary role is as an Apple Silicon testbed. LocoLLM needs to run on the hardware students actually own, and a lot of them carry MacBooks. Poco validates that the installation process, Ollama inference, and adapter loading all work cleanly on Apple Silicon with unified memory. If it works on a base M1 with 16 GB, it works on anything a student is likely to have.

Apple's MLX framework also supports LoRA fine-tuning natively via `mlx_lm.lora`, so Poco can verify the training-to-deployment pipeline on Apple hardware when needed. It's slow (68 GB/s memory bandwidth versus 448 GB/s on Cerebro), but "does it work" matters more than "how fast" for compatibility testing.

**Best at:** Remote access. Verifying the student experience on consumer Apple hardware.

---

## Cerebro

**The Ryzen Build -- Primary Training and Inference**

| | |
|---|---|
| **CPU** | AMD Ryzen 5 2600 (12 threads @ 3.4 GHz) |
| **GPU** | 2x NVIDIA RTX 2060 SUPER (8 GB VRAM each) |
| **Memory** | 32 GB DDR4 |
| **OS** | Ubuntu 22.04.5 LTS |
| **Role** | Production training, benchmarking, inference serving |

Cerebro is the brain of the operation. The name is Spanish for "brain," and it fits: this is where adapters get trained, benchmarked, and served. Two RTX 2060 SUPERs with Turing architecture Tensor Cores, fully supported by Unsloth's optimised Triton kernels.

Unsloth uses a single GPU for QLoRA training, so the dual-card setup creates a useful split: one GPU trains while the other runs Ollama for inference and benchmarking. You can evaluate an adapter on GPU 1 while the next one trains on GPU 0.

**Practical training specs for Qwen3-4B QLoRA:**
- VRAM usage: ~7-8 GB per card
- Sequence length: 2048 tokens (up to 4096 if needed)
- Batch size: 1 with gradient accumulation of 8
- LoRA rank: 16 across all linear layers (q, k, v, o, gate, up, down)
- Precision: float16 (Turing doesn't support bfloat16 natively; Unsloth auto-detects)
- Typical training time: 2-4 hours per adapter on 1,000-2,000 examples

**The pipeline from dataset to deployment runs entirely on this machine:**
1. Prepare dataset (JSONL, question/answer pairs)
2. QLoRA fine-tune with Unsloth
3. Export to GGUF (Unsloth has built-in llama.cpp export)
4. Load in Ollama
5. Benchmark against base model

32 GB of system RAM handles dataset preprocessing and model loading comfortably. The Ryzen 5 2600 isn't flashy, but twelve threads keep data pipelines fed without bottlenecking.

**Best at:** Full training runs. Side-by-side adapter evaluation. Running the LocoLLM inference stack as it would appear to end users.

---

## Burro

**The IBM x3500 M4 -- Dedicated Training Server**

| | |
|---|---|
| **Chassis** | IBM System x3500 M4 (5U tower) |
| **CPU** | Intel Xeon E5-2660 (8 cores, 16 threads @ 2.2 GHz) |
| **GPU** | NVIDIA Tesla P100 16 GB (Pascal, HBM2) |
| **PSU** | 2x 750W redundant |
| **Memory** | 32 GB DDR3 ECC (8x 4 GB) |
| **Storage** | 300 GB SAS (boot) + 5x 300 GB SAS (available) |
| **OS** | Ubuntu Server 22.04 LTS |
| **Role** | Overnight training, large datasets, "set and forget" |

Burro means "donkey" in Spanish. Donkeys aren't fast, but they carry heavy loads without stopping. That's exactly what this server does.

The P100 is the sole GPU. A small LCD monitor sits on the desk connected to the onboard Matrox G200 (via the IMM2), running a persistent tmux dashboard with GPU stats, training progress, and adapter registry status. Day to day it's a status display; when needed, a keyboard comes out of the drawer for direct access.

Pascal architecture, compute capability 6.0, fully supported by current PyTorch and CUDA. The P100's 16 GB of HBM2 memory at 732 GB/s bandwidth opens up training options that Cerebro's 8 GB cards can't touch: full 16-bit LoRA (instead of 4-bit QLoRA), longer context windows (4096-8192 tokens), bigger batch sizes, and higher LoRA ranks. All of those translate to potentially better adapter quality. With 16 GB of VRAM, the P100 also handles inference and benchmarking after a training run completes, just sequentially rather than simultaneously like Cerebro's dual-card split.

The P100 doesn't have Tensor Cores (those arrived with Volta), so it won't benefit from Unsloth's mixed-precision acceleration. Training runs through standard CUDA cores using vanilla PEFT or HuggingFace Trainer instead. Expect roughly 2-3x slower than Cerebro's 2060 SUPER for the same job. A three-hour Unsloth run on Cerebro becomes a six-to-eight-hour PEFT run on Burro. That's overnight, not days.

The P100 PCIe is a passively cooled card designed for high-velocity rack airflow. The x3500's tower layout moves air more gently, so a 3D-printed fan shroud with a 92mm Noctua is fitted to direct airflow across the heatsink. Printed in PETG on the project's own Prusa fleet.

The x3500 M4 is enterprise tower hardware from 2012. Dual Xeon sockets, redundant power supplies, ECC memory, hot-swap drive bays. Built to run 24/7. The tower form factor keeps things practical: quieter fan profile, full-height PCIe slots that fit the P100 without compromise, and it lives under a desk without anyone needing to worry about it. You give it a training job at 6pm, and the adapter is ready when you walk in the next morning.

**Best at:** Long training runs on larger datasets. Higher-fidelity LoRA training at 16-bit. Jobs where time isn't the constraint but quality is.

---

## The Fleet at a Glance

| Machine | GPU VRAM | Memory BW | Tensor Cores | Primary Role | Training Tool |
|---|---|---|---|---|---|
| **Poco** (MacBook M1) | 16 GB unified | 68 GB/s | No | Remote terminal, Apple Silicon testing | MLX (when needed) |
| **Cerebro** (Ryzen + 2x 2060S) | 8 GB per card | 448 GB/s | Yes (Turing) | Fast training, inference, benchmarking | Unsloth QLoRA |
| **Burro** (IBM x3500 M4 + P100) | 16 GB HBM2 | 732 GB/s | No | Overnight training, high-fidelity LoRA | PEFT / HF Trainer |

---

## A Note on Hardware

Nothing about this specific hardware is prescriptive. The P100 doesn't require an IBM server. It needs a PCIe x16 slot, a power supply that can handle the extra 250W draw, and enough airflow over a passively cooled card. That could be an old Dell workstation, an HP tower, a custom build from spare parts, or whatever you find on your local secondhand market. The x3500 M4 is just what happened to be in the workshop already.

The same goes for Cerebro. Any mid-range desktop with an NVIDIA GPU and 8+ GB of VRAM runs the same Unsloth pipeline. The RTX 2060 SUPER isn't special. It's just what was available.

If you're building your own LocoLLM lab, your hardware will look different from ours. That's fine. The architecture doesn't care about the brand on the case. It cares about VRAM, CUDA support, and whether the software stack runs. Match the capability, not the specific parts list.

---

## Running Costs

Old enterprise hardware draws more power per FLOP than current-generation GPUs. That's true. But when you do the maths on actual training runs, the electricity cost is measured in cents, not dollars. A single adapter training run on Cerebro costs roughly the price of a coffee pod. An overnight run on Burro costs about the price of a bus fare.

The full cost analysis, including idle power draw, cloud GPU comparisons, capital expenditure versus running costs, and total cost of ownership, is covered in [The Economics of Local Training](economics-of-local-training.md).

---

## Why This Matters

Every machine in this lab was sourced secondhand through patient marketplace hunting, the same approach that built the rest of The 80-20 Workshop. No premium prices. No enterprise procurement. Just consumer-grade and ex-enterprise hardware, acquired opportunistically.

Every result LocoLLM publishes is reproducible on hardware that anyone can acquire the same way. No A100 clusters. No cloud credits. No asterisks.

That's not a limitation. That's the thesis.
