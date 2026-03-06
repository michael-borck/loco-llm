---
title: "Meet the Lab"
---

LocoLLM runs on four machines. None of them are new. All were sourced secondhand. Hardware was acquired opportunistically -- the right capability at the right price, not a planned procurement.

The naming follows a Spanish thread: Colmena (hive), Burro (donkey), Poco (a little), and Peque (little one). The hive coordinates many workers, the donkey carries heavy loads, the little one connects you to both, and the littlest one keeps the floor honest.

---

## Poco

**MacBook M1 -- Remote Terminal and Apple Silicon Testbed**

| | |
|---|---|
| **Chip** | Apple M1 |
| **Memory** | 16 GB unified (shared CPU/GPU) |
| **Storage** | 256 GB SSD |
| **OS** | macOS |
| **Role** | Remote access to lab machines, Apple Silicon compatibility testing |

Poco means "a little" in Spanish. It doesn't do the heavy lifting -- it's how you reach the machines that do.

Day to day it's a remote terminal. SSH into Colmena for inference and benchmarking, SSH into Burro for overnight jobs, monitor progress, pull results. Portable and works from anywhere on the network.

Its secondary role is Apple Silicon compatibility testing. LocoLLM needs to run on hardware students actually own, and a significant proportion carry MacBooks. Poco validates that installation, Ollama inference, and adapter loading all work cleanly on Apple Silicon with unified memory. A base M1 with 16 GB represents a reasonable lower bound for that user group.

Apple's MLX framework supports LoRA fine-tuning natively via `mlx_lm.lora`, so Poco can also verify the training-to-deployment pipeline on Apple hardware when needed. Memory bandwidth is 68 GB/s -- slow compared to the rest of the lab -- but functional.

**Best at:** Remote access. Validating the student experience on consumer Apple hardware.

---

## Colmena

**B250 Mining Expert -- Multi-GPU Inference Hive and Benchmark Rig**

| | |
|---|---|
| **Motherboard** | ASUS B250 Mining Expert (19 PCIe slots, LGA1151) |
| **CPU** | Intel Celeron G3930 2.9 GHz |
| **GPUs** | NVIDIA GTX 1050 Ti 4 GB, 3x RTX 2060 Super 8 GB, RTX 3060 12 GB (5 cards, 6th slot reserved) |
| **Memory** | 16 GB DDR4 |
| **OS** | Ubuntu 22.04 LTS |
| **Form** | Open air frame (3D printed, PETG) |
| **Role** | Multi-GPU inference, benchmarking, multi-GPU architecture research |

Colmena means "hive" in Spanish. Multiple workers, one coordinated system.

The B250 Mining Expert was designed for cryptocurrency mining -- 19 PCIe slots, each running a GPU via USB riser cable at x1 electrical bandwidth. x1 is enough for LLM inference. The bandwidth constraint matters for training; for inference it doesn't. Mining rig hardware turns out to be a reasonable fit for a multi-GPU research platform, and the entire machine was assembled from secondhand parts sourced opportunistically. Specialised in configuration, not in cost.

Colmena has three roles in priority order:

**1. smol-bench primary platform.** The main reason Colmena exists in this form. A standard desktop with one PCIe slot could never serve smol-bench's purpose -- you need simultaneous parallel runs across multiple cards to get robust comparative results, not sequential GPU swaps. The open frame makes card visibility and access practical rather than incidental.

**2. Multi-GPU architecture research.** Three 2060 Supers in the same machine enables load balancing, Mixture of Agents, and speculative decoding experiments that a two-card setup can't fully explore.

**3. Inference serving.** The 2060 Supers are the practical sweet spot for current 7B models. Colmena serves the CloudCore Networks simulation -- a virtual business populated with AI chatbot employees, each with unique backstories, which students interview to extract requirements and understand business problems as part of assessed work. Previously this ran on a single card in Cerebro. Colmena takes over that role. If inference load becomes an issue a 2060 Super can move back into a dedicated machine without disrupting the benchmarking setup.

The open frame design and card progression also works as a physical demonstration piece. The hardware tells the VRAM story visually in a way a conventional tower case never could.

The card lineup spans VRAM generations: 4 GB, 8 GB (x3), and 12 GB. A sixth slot is reserved for future expansion as the secondhand market matures. Each card runs its own Ollama instance, assigned via `CUDA_VISIBLE_DEVICES`.

**GPU progression:**

| Card | VRAM | Notes |
|------|------|-------|
| GTX 1050 Ti | 4 GB | Floor -- minimum viable inference node |
| RTX 2060 Super (x3) | 8 GB each | Turing, Tensor Cores, QLoRA capable |
| RTX 3060 | 12 GB | Comfortable headroom for 7B models at Q4 |
| (Future) | TBD | 40-series when affordable secondhand |

**A note on NVLink:** The 2060 Supers don't support NVLink -- true hardware VRAM pooling isn't available. This is a non-issue for this project. Consumer NVLink was briefly available on the RTX 2080 Ti and RTX 3090, but Nvidia removed it entirely from the 4090 and 5090. For consumer-grade hardware, NVLink is dead. Each card operates as an independent worker, which is the right architecture for this use case anyway.

**Multi-GPU operating modes:**

The three 2060 Supers don't support NVLink -- VRAM pooling at the hardware level isn't available. Each card operates as an independent worker. Three useful architectures are in scope:

*Load balancer:* Three Ollama instances, one per 2060 Super, behind an nginx or FastAPI router distributing requests round-robin. Triples concurrent throughput with no quality tradeoff. Relevant for multi-user AnythingLLM sessions and CloudCore Networks simulations.

*Mixture of Agents (MoA):* Two cards act as proposers, generating independent responses to the same query at slightly different temperatures. A third card acts as aggregator, synthesising the two outputs into a final response. Quality improvements are most noticeable on reasoning tasks. Adds roughly one generation cycle of latency. See [arxiv.org/abs/2406.04692](https://arxiv.org/abs/2406.04692).

*Speculative decoding:* A small draft model on one card generates candidate tokens rapidly. A larger verifier model on another card accepts or rejects token batches. Net result is lower latency from the large model. Supported natively by llama.cpp via `--model-draft`.

A meta-router can switch between modes depending on load and query type.

**Best at:** Benchmarking across VRAM tiers. Multi-user inference serving. Multi-GPU architecture experiments.

**A counterintuitive result:** For models that fit in 8 GB, the 2060 Supers will likely outperform the 3060 on tokens per second. LLM inference is memory bandwidth bound, not compute bound -- and the 2060 Super's 448 GB/s beats the 3060's 360 GB/s. The 3060's newer Ampere architecture and improved Tensor Cores don't help much when the bottleneck is getting weights off the card, not computing with them. The 3060's value in Colmena is VRAM capacity -- it's the only card that can load models larger than 8 GB. For everything that fits in 8 GB, the older cards are faster. A good thing to show students before they assume newer always means better.

---

## Burro

**IBM x3500 M4 -- Dedicated Training Server**

| | |
|---|---|
| **Chassis** | IBM System x3500 M4 (5U tower) |
| **CPU** | Intel Xeon E5-2660 (8 cores, 16 threads @ 2.2 GHz) |
| **GPU** | NVIDIA Tesla P100 16 GB (Pascal, HBM2) |
| **PSU** | 2x 750W redundant |
| **Memory** | 32 GB DDR3 ECC |
| **Storage** | 300 GB SAS (boot) + 5x 300 GB SAS |
| **OS** | Ubuntu Server 22.04 LTS |
| **Role** | Overnight training, large datasets, high-fidelity LoRA |

Burro means "donkey" in Spanish. Not fast, but it carries heavy loads reliably.

The P100's 16 GB of HBM2 at 732 GB/s opens training options that 8 GB cards can't reach: full 16-bit LoRA rather than 4-bit QLoRA, longer context windows (4096-8192 tokens), larger batch sizes, and higher LoRA ranks. These translate to higher-fidelity adapters for jobs where quality matters more than turnaround time.

Pascal architecture (compute capability 6.0) doesn't have Tensor Cores -- those arrived with Volta. Training runs through standard CUDA cores using vanilla PEFT or HuggingFace Trainer rather than Unsloth. Expect roughly 2-3x slower wall-clock time than a 2060 Super running Unsloth QLoRA for an equivalent job. A three-hour Unsloth run on a 2060 Super becomes a six-to-eight-hour PEFT run on Burro. That's an overnight job, not a multi-day one.

The P100 PCIe is passively cooled, designed for high-velocity rack airflow. The x3500's tower layout moves air more gently, so a 3D-printed fan shroud with a 92mm Noctua directs airflow across the heatsink. Printed in PETG on the lab's own Prusa fleet.

A small LCD monitor connects to the onboard Matrox G200 via IMM2, running a persistent tmux dashboard with GPU stats and training progress. Keyboard stays in the drawer; the display is the only regular interaction.

**Best at:** Long training runs on larger datasets. Higher-fidelity LoRA at 16-bit precision. Jobs where quality matters more than speed.

**A note on consolidation:** The P100 could physically move to Colmena -- it needs a PCIe slot, power, and airflow, all of which are available. The reason it stays in Burro is the B250 Mining Expert's riser cables run at x1 electrical bandwidth. For inference that's fine. For training, which is bandwidth sensitive, it would meaningfully degrade the P100's primary role. The x3500 also provides directed high-velocity airflow across the passive heatsink that an open frame can't replicate without a dedicated shroud redesign. The consolidation isn't worth the tradeoff.

---

## Peque

**Dell Optiplex 990 -- Reference Node**

| | |
|---|---|
| **Chassis** | Dell Optiplex 990 (DT) |
| **GPU** | NVIDIA GeForce GTX 1650 OC 4 GB |
| **Memory** | 16 GB DDR3 |
| **Storage** | 256 GB SSD |
| **OS** | Ubuntu 22.04 LTS |
| **Role** | Minimum viable inference node, reference testing |

Peque is informal Spanish for "little one." It represents the floor -- the least capable machine that can still participate meaningfully in the lab network.

The 1650 is Turing architecture (compute capability 7.5), 4 GB GDDR6, 192 GB/s memory bandwidth. 4 GB VRAM is the real constraint. It runs quantised 7B models at Q4 -- tightly, but it runs them. The question Peque answers is whether a node at the low end of the capability range can still serve useful inference. If a Q4_K_M model loads and runs here, it runs on comparable consumer hardware.

The Dell Optiplex 990 is the secondhand market's most common desktop chassis. Schools, offices, and government departments cycle through them at volume. Cheap, standardised, and the compact form factor is familiar to anyone who has worked in an office in the last decade. It represents a plausible "hardware a department already owns" scenario.

Ubuntu 22.04 LTS matches the rest of the fleet. Same CUDA toolkit, same driver stack, same Ollama installation path.

**Best at:** Validating inference on constrained hardware. Representing what a department's existing PC can actually run.

---

## Fleet at a Glance

| Machine | GPU | VRAM | Memory BW | Tensor Cores | Primary Role |
|---------|-----|------|-----------|--------------|--------------|
| **Poco** (MacBook M1) | Apple M1 GPU | 16 GB unified | 68 GB/s | No | Remote terminal, Apple Silicon testing |
| **Colmena** (B250 Mining Expert) | 1050 Ti + 3x 2060S + 3060 | 4/8/8/8/12 GB | 112-448 GB/s | Yes (2060S, 3060) | Multi-GPU inference, benchmarking |
| **Burro** (IBM x3500 M4 + P100) | Tesla P100 | 16 GB HBM2 | 732 GB/s | No | Overnight training, high-fidelity LoRA |
| **Peque** (Dell Optiplex + 1650) | GTX 1650 OC | 4 GB GDDR6 | 192 GB/s | Yes (Turing) | Reference node, minimum viable inference |

---

## Hardware Notes

The specific hardware here isn't prescriptive. The P100 doesn't require an IBM server -- it needs a PCIe x16 slot, adequate power, and airflow over a passively cooled card. The B250 Mining Expert doesn't require this exact GPU lineup -- any PCIe cards via risers work. The Optiplex doesn't require a 1650 -- any low-profile CUDA card with 4 GB fits the role.

What matters for replication is capability tier, not specific parts. Match the VRAM range and CUDA support, source whatever is available locally at the time.

The lab exists at this price point deliberately. Frontier model access on premium hardware -- cloud APIs, Apple Silicon, high-end workstations -- is available, but it concentrates AI capability around cost. A lab built from secondhand consumer hardware makes the same workflows accessible to anyone willing to learn the stack. Smaller models on modest hardware are genuinely useful for exploration, brainstorming, and iteration. That use case doesn't require a frontier model and doesn't require expensive hardware. It requires understanding what you're doing -- which is the point of the lab.

---

## A Note on Cerebro

An earlier version of the lab included Cerebro, a Ryzen 5 2600 desktop with two RTX 2060 Super GPUs. Colmena supersedes it -- same GPU generation, more cards, more flexibility, and a purpose-built motherboard for multi-GPU work. Cerebro is retired. The 2060 Supers moved to Colmena.
