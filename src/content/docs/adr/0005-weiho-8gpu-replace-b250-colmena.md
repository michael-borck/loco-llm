---
title: "ADR-0005: WEIHO 8-GPU Enclosed Chassis Replaces B250 Open Frame for Colmena"
---

## Status

Accepted

## Date

2026-03-07

## Context

ADR-0004 adopted a B250 Mining Expert motherboard in an open air frame as the multi-GPU platform (Colmena), fully retiring Cerebro. During hardware sourcing, the plan changed substantially:

1. A WEIHO 8-GPU enclosed mining rig (72x42x18cm, steel chassis, integrated 2000-3300W PSU) became available. It provides 8 native PCIe slots without riser cables in an enclosed, cooled chassis -- a better fit than an open frame with USB risers.
2. Cerebro should not be fully retired. It continues to run CloudCore Networks, a separate project from LocoLLM and LocoBench. One RTX 2060 Super remains dedicated to CloudCore inference in Cerebro.
3. LocoBench's benchmarking philosophy crystallised around floor cards per VRAM tier rather than multiple identical cards. Three matched 2060 Supers are no longer needed -- one 2060 Super represents the 8 GB Turing floor.
4. The host system is deliberately constrained (i3-3220, 8 GB DDR3) because LocoBench benchmarks GPU capability on modest hardware, which is what most users actually have.

## Decision

Replace the B250 Mining Expert open frame design with the **WEIHO 8-GPU enclosed chassis** for Colmena. Supersedes ADR-0004.

**Hardware:**
- Chassis: WEIHO 8-GPU enclosed mining rig
- Motherboard: Intel LGA1155 (likely B75/H61 chipset)
- CPU: Intel i3-3220 (Ivy Bridge, dual core)
- RAM: 8 GB DDR3 SODIMM (board maximum)
- Storage: 128 GB mSATA (OS) + WD Scorpio Blue 750 GB SATA (model storage)
- PSU: Integrated 2000-3300W
- Cooling: 4x 120mm fans (to be replaced with Arctic P12 PWM)
- 8 native PCIe slots, no risers

**GPU lineup -- floor cards per VRAM tier:**

| Card | VRAM | Tier Role |
|------|------|-----------|
| GTX 1050 Ti | 4 GB | Floor of 4 GB tier |
| GTX 1060 6 GB | 6 GB | Floor of 6 GB tier (pending acquisition) |
| RTX 2060 Super | 8 GB | Floor of 8 GB Turing tier |
| RTX 3060 AORUS Elite | 12 GB | Floor of 12 GB tier |
| RTX 3090 (reserved) | 24 GB | Reference ceiling (work budget) |
| 3 slots reserved | TBD | Future expansion |

**Cerebro stays active:**
- One RTX 2060 Super remains in Cerebro for CloudCore Networks (separate project)
- Second 2060 Super (Michael's testing card) migrates to Colmena

**Three distinct projects with distinct hardware:**
- LocoLLM (Burro + Colmena) -- infrastructure, architecture research, fine-tuning
- LocoBench (Colmena primary) -- benchmarking platform, community results
- CloudCore Networks + Cerebro (standalone) -- student assessment simulation

## Consequences

- LocoBench benchmarks use floor cards per tier, producing conservative baselines -- if it runs here, it runs on your card
- Enclosed chassis replaces open frame; card visibility is traded for better cooling and a smaller footprint
- 8 native PCIe slots (no risers) simplify the build and avoid x1 electrical bandwidth concerns
- Deliberately constrained host (i3-3220, 8 GB RAM) means sequential benchmarking rather than parallel, but results are identical
- Cerebro is no longer retired -- it remains active for CloudCore Networks with a dedicated 2060 Super
- CloudCore Networks is cleanly separated from LocoLLM and LocoBench infrastructure
- RTX 3090 reserved as reference ceiling validates whether floor-tier results scale predictably across the VRAM range
- ADR-0004 is superseded; the B250 Mining Expert open frame design is not being built
