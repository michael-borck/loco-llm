---
title: "Meet the Lab"
---

LocoLLM runs across three projects on five machines. None of them are new. All were sourced secondhand. Hardware was acquired opportunistically -- the right capability at the right price, not a planned procurement.

The naming follows a Spanish thread: Colmena (hive), Burro (donkey), Poco (a little), Peque (little one), and Cerebro (brain). The hive coordinates many workers, the donkey carries heavy loads, the little one connects you to both, the littlest one keeps the floor honest, and the brain runs the simulation.

**Three separate projects, distinct hardware roles:**

- **LocoLLM** (Burro + Colmena) -- infrastructure, architecture research, fine-tuning
- **LocoBench** (Colmena primary) -- benchmarking platform, community results
- **CloudCore Networks + Cerebro** (standalone, untouched) -- student assessment simulation

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

**WEIHO 8-GPU Enclosed Chassis -- Multi-GPU Inference Hive and Benchmark Rig**

| | |
|---|---|
| **Chassis** | WEIHO 8-GPU enclosed mining rig (72x42x18cm, steel, blue lid) |
| **Motherboard** | Intel LGA1155, likely B75/H61 chipset |
| **CPU** | Intel i3-3220 (Ivy Bridge, dual core) |
| **GPUs** | GTX 1050 Ti 4 GB, RTX 2060 Super 8 GB, RTX 3060 12 GB (3 cards installed, 1 pending acquisition, 4 slots reserved) |
| **Memory** | 8 GB DDR3 SODIMM (board maximum) |
| **Storage** | 128 GB mSATA (OS) + WD Scorpio Blue 750 GB SATA (model storage via `OLLAMA_MODELS`) |
| **PSU** | Integrated 2000-3300W unit |
| **Cooling** | 4x 120mm fans (to be replaced with Arctic P12 PWM) |
| **GPU slots** | 8 native PCIe slots, no risers needed |
| **OS** | Ubuntu 22.04 LTS |
| **Form** | Enclosed chassis |
| **Role** | Multi-GPU inference, LocoBench benchmarking, multi-GPU architecture research |

Colmena means "hive" in Spanish. Multiple workers, one coordinated system.

Colmena is a deliberately constrained machine. The i3-3220 CPU, 8 GB RAM ceiling, and modest storage exist by design, not accident. The CPU's job is to boot the OS and manage the PCIe bus. The GPUs do the work. Over-speccing the host system would make Colmena a worse research instrument -- LocoBench benchmarks GPU capability on modest hardware, which is what most users actually have.

RAM constraints mean sequential rather than fully parallel benchmarking for LocoBench. Results are identical -- same hardware, same models -- the runs just don't happen simultaneously. For inference serving, one or two active instances at a time is realistic for student load anyway.

The WEIHO chassis was designed for cryptocurrency mining -- 8 native PCIe slots in an enclosed steel case with integrated high-wattage PSU and fan cooling. No riser cables needed. Mining rig hardware turns out to be a reasonable fit for a multi-GPU research platform, and the entire machine was assembled from secondhand parts sourced opportunistically.

Colmena has two roles in priority order:

**1. LocoBench primary platform.** The main reason Colmena exists in this form. Each VRAM tier is represented by the floor card for that tier, not the best available. Conservative baselines mean: if it runs here, it runs on your card. Community submissions extend each tier upward. The bandwidth delta within each tier is documented in nvidia-gpu-reference.md, allowing readers to extrapolate to their specific card.

**2. Multi-GPU architecture research.** Multiple cards in the same machine enables load balancing, Mixture of Agents, and speculative decoding experiments. Each card runs its own Ollama instance, assigned via `CUDA_VISIBLE_DEVICES`.

**GPU progression -- LocoBench floor cards:**

| Card | VRAM | Bandwidth | Architecture | Tensor Cores | Tier Role |
|------|------|-----------|-------------|--------------|-----------|
| GTX 1050 Ti | 4 GB | 112 GB/s | Pascal | No | Floor of 4 GB tier |
| GTX 1060 6 GB | 6 GB | 192 GB/s | Pascal | No | Floor of 6 GB tier (pending acquisition) |
| RTX 2060 Super | 8 GB | 448 GB/s | Turing | Yes | Floor of 8 GB Turing bandwidth |
| RTX 3060 AORUS Elite | 12 GB | 360 GB/s | Ampere | Yes | Floor of 12 GB tier |
| (Reserved) RTX 3090 | 24 GB | 936 GB/s | Ampere | Yes | Reference ceiling (work budget, patient hunt) |
| 3 slots reserved | TBD | | | | Future expansion |

The RTX 2060 Super is one of two cards previously in Cerebro. Michael's testing card migrates to Colmena; the other remains in Cerebro dedicated to CloudCore inference.

The RTX 3090 24 GB is a reserved slot via work research budget. It's positioned as the reference ceiling for LocoBench, not a user recommendation. It sits in an awkward market position -- too old for enthusiasts, too expensive for budget builders -- but 24 GB VRAM is the consumer ceiling for secondhand hardware and validates whether floor-tier results scale predictably. A research instrument, not an aspirational purchase.

**A note on NVLink:** Consumer NVLink was briefly available on the RTX 2080 Ti and RTX 3090, but Nvidia removed it entirely from the 4090 and 5090. For consumer-grade hardware, NVLink is dead. Each card operates as an independent worker, which is the right architecture for this use case anyway.

**Multi-GPU operating modes:**

Cards don't support NVLink -- VRAM pooling at the hardware level isn't available. Each card operates as an independent worker. Three useful architectures are in scope:

*Load balancer:* Multiple Ollama instances behind an nginx or FastAPI router distributing requests round-robin. Increases concurrent throughput with no quality tradeoff. Relevant for multi-user AnythingLLM sessions.

*Mixture of Agents (MoA):* Two cards act as proposers, generating independent responses to the same query at slightly different temperatures. A third card acts as aggregator, synthesising the two outputs into a final response. Quality improvements are most noticeable on reasoning tasks. Adds roughly one generation cycle of latency. See [arxiv.org/abs/2406.04692](https://arxiv.org/abs/2406.04692).

*Speculative decoding:* A small draft model on one card generates candidate tokens rapidly. A larger verifier model on another card accepts or rejects token batches. Net result is lower latency from the large model. Supported natively by llama.cpp via `--model-draft`.

A meta-router can switch between modes depending on load and query type.

**Best at:** Benchmarking across VRAM tiers. Multi-GPU architecture experiments. Sequential LocoBench runs on deliberately constrained host hardware.

**A counterintuitive result:** For models that fit in 8 GB, the 2060 Super will likely outperform the 3060 on tokens per second. LLM inference is memory bandwidth bound, not compute bound -- and the 2060 Super's 448 GB/s beats the 3060's 360 GB/s. The 3060's newer Ampere architecture and improved Tensor Cores don't help much when the bottleneck is getting weights off the card, not computing with them. The 3060's value in Colmena is VRAM capacity -- it's the only card that can load models larger than 8 GB (until the 3090 arrives). For everything that fits in 8 GB, the older card is faster. A good thing to show students before they assume newer always means better.

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

**A note on consolidation:** The P100 could physically move to Colmena -- it needs a PCIe slot, power, and airflow, all of which are available. The reason it stays in Burro is that training is bandwidth sensitive, and the x3500 provides directed high-velocity airflow across the passive heatsink that the enclosed WEIHO chassis isn't designed for. The consolidation isn't worth the tradeoff.

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

## Cerebro

**Ryzen 5 2600 Desktop -- CloudCore Networks Simulation Host**

| | |
|---|---|
| **Chassis** | Desktop tower |
| **CPU** | AMD Ryzen 5 2600 |
| **GPU** | RTX 2060 Super 8 GB |
| **OS** | Ubuntu 22.04 LTS |
| **Role** | CloudCore Networks simulation (standalone project) |

Cerebro means "brain" in Spanish. It runs the thinking behind CloudCore Networks.

Cerebro previously housed two RTX 2060 Super GPUs and served as the lab's primary inference machine. That role has moved to Colmena. One 2060 Super (Michael's testing card) migrated to Colmena for LocoBench duties. The other remains in Cerebro, dedicated to CloudCore Networks inference.

CloudCore Networks is a separate project from LocoLLM and LocoBench -- a virtual business populated with AI chatbot employees, each with unique backstories, which students interview to extract requirements and understand business problems as part of assessed work. It runs independently and is not part of the benchmarking or fine-tuning infrastructure.

**Best at:** Running CloudCore Networks. Staying out of the way.

---

## Fleet at a Glance

| Machine | Project | GPU | VRAM | Memory BW | Tensor Cores | Primary Role |
|---------|---------|-----|------|-----------|--------------|--------------|
| **Poco** (MacBook M1) | LocoLLM | Apple M1 GPU | 16 GB unified | 68 GB/s | No | Remote terminal, Apple Silicon testing |
| **Colmena** (WEIHO 8-GPU) | LocoLLM / LocoBench | 1050 Ti + 2060S + 3060 | 4/8/12 GB | 112-448 GB/s | Yes (2060S, 3060) | Benchmarking, multi-GPU research |
| **Burro** (IBM x3500 M4 + P100) | LocoLLM | Tesla P100 | 16 GB HBM2 | 732 GB/s | No | Overnight training, high-fidelity LoRA |
| **Peque** (Dell Optiplex + 1650) | LocoLLM | GTX 1650 OC | 4 GB GDDR6 | 192 GB/s | Yes (Turing) | Reference node, minimum viable inference |
| **Cerebro** (Ryzen 5 2600) | CloudCore | RTX 2060 Super | 8 GB | 448 GB/s | Yes (Turing) | CloudCore Networks simulation |

---

## Hardware Notes

The specific hardware here isn't prescriptive. The P100 doesn't require an IBM server -- it needs a PCIe x16 slot, adequate power, and airflow over a passively cooled card. Colmena doesn't require this exact GPU lineup -- any PCIe cards work. The Optiplex doesn't require a 1650 -- any low-profile CUDA card with 4 GB fits the role.

What matters for replication is capability tier, not specific parts. Match the VRAM range and CUDA support, source whatever is available locally at the time.

**Why Nvidia only?** The entire local LLM toolchain -- Ollama, llama.cpp, PyTorch, bitsandbytes, Unsloth -- targets CUDA first. AMD's ROCm stack exists and is improving, but driver support is narrower, community troubleshooting is thinner, and the tooling friction is meaningfully higher. Intel Arc is earlier still. For a lab that needs to work reliably with minimal sysadmin overhead, CUDA is the only practical choice today.

The secondhand market reinforces this. The cryptocurrency mining boom flooded resale channels with Nvidia consumer cards at accessible prices. AMD equivalents at the same VRAM tiers are rarer and less standardised. And the overwhelming majority of users running local LLMs on consumer hardware are on Nvidia -- LocoBench floor cards need to represent what people actually have.

Apple Silicon is the exception, and Poco covers that path via Metal and MLX. If ROCm matures to the point where an AMD card is a genuine drop-in for Ollama inference, it becomes a candidate for a Colmena slot. That day isn't today.

The lab exists at this price point deliberately. Frontier model access on premium hardware -- cloud APIs, Apple Silicon, high-end workstations -- is available, but it concentrates AI capability around cost. A lab built from secondhand consumer hardware makes the same workflows accessible to anyone willing to learn the stack. Smaller models on modest hardware are genuinely useful for exploration, brainstorming, and iteration. That use case doesn't require a frontier model and doesn't require expensive hardware. It requires understanding what you're doing -- which is the point of the lab.
