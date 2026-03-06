---
title: "ADR-0004: Retire Cerebro, Adopt B250 Mining Expert as Multi-GPU Platform"
---

# ADR-0004: Retire Cerebro, Adopt B250 Mining Expert as Multi-GPU Platform

## Status

Accepted

## Date

2026-03-06

## Context

The lab included Cerebro, a Ryzen 5 2600 desktop with two RTX 2060 Super GPUs. It served as the primary inference machine and ran CloudCore Networks simulations. However, two PCIe slots limited what could be explored -- smol-bench needs simultaneous parallel runs across multiple cards, and multi-GPU architectures like Mixture of Agents and speculative decoding benefit from three or more identical cards.

An ASUS B250 Mining Expert motherboard (19 PCIe slots, LGA1151) became available secondhand. Originally designed for cryptocurrency mining, its USB riser cables run each slot at x1 electrical bandwidth -- adequate for inference, inadequate for training. This made it a candidate for a dedicated multi-GPU inference and benchmarking platform.

## Decision

Retire Cerebro. Build **Colmena**, a new machine based on the B250 Mining Expert in an open air frame, consolidating the two 2060 Supers from Cerebro and adding a GTX 1050 Ti (4 GB) and RTX 3060 (12 GB) to span a range of VRAM tiers. A sixth slot is reserved for future expansion.

Colmena takes over three roles in priority order:

1. **smol-bench primary platform** -- simultaneous benchmarking across multiple VRAM tiers, which a single- or dual-slot machine cannot support.
2. **Multi-GPU architecture research** -- load balancing, Mixture of Agents, and speculative decoding experiments using three matched 2060 Supers.
3. **Inference serving** -- CloudCore Networks and multi-user AnythingLLM sessions, previously hosted on Cerebro.

Training remains on Burro (P100 in the IBM x3500 M4). The B250's x1 riser bandwidth would degrade training throughput, and the x3500 provides the directed airflow the passively-cooled P100 requires.

## Consequences

- smol-bench can run parallel benchmarks across 4-12 GB VRAM cards simultaneously, which was not possible before
- Multi-GPU inference patterns (load balancing, MoA, speculative decoding) become testable with three identical 2060 Supers
- CloudCore Networks inference moves from Cerebro to Colmena with no disruption -- same GPU generation, more capacity
- The open frame makes the VRAM progression physically visible, useful as a teaching aid
- Cerebro's Ryzen platform is fully retired -- no orphaned hardware to maintain
- x1 PCIe bandwidth means Colmena is inference-only; any training workload requiring GPU bandwidth must stay on Burro
- If inference load grows, a 2060 Super can move back into a standalone machine without affecting the benchmarking setup
