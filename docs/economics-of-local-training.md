# The Economics of Local Training

LocoLLM runs on secondhand hardware. This document puts real numbers to the question of whether that makes financial sense compared to cloud GPU rental, API inference, or buying new equipment.

All figures use Australian dollars (AUD) and Perth electricity rates (Synergy Home Plan A1, ~$0.31/kWh).

---

## Power Draw

Both Cerebro and Burro run 24/7. Most of the time they're idle (SSH available, Ollama loaded, waiting for work). Training runs push power draw up significantly but only for a few hours at a time.

**Estimated draw by state:**

| Machine | Idle | Training Load |
|---|---|---|
| **Cerebro** (Ryzen + 2x 2060S) | ~120W | ~300W |
| **Burro** (x3500 M4 + P100) | ~150W | ~420W |

---

## Annual Electricity Cost

These estimates assume 24/7 operation. Two scenarios: a conservative one where the machines are under training load half the time, and a lighter one that reflects more typical usage patterns where training runs a few hours a day and the machines sit idle the rest.

**50% training / 50% idle (conservative):**

| Machine | Average Draw | Annual kWh | Annual Cost |
|---|---|---|---|
| **Cerebro** | ~210W | 1,840 kWh | ~$570 AUD |
| **Burro** | ~285W | 2,497 kWh | ~$774 AUD |
| **Combined** | | 4,337 kWh | ~$1,344 AUD |

**25% training / 75% idle (more typical):**

| Machine | Average Draw | Annual kWh | Annual Cost |
|---|---|---|---|
| **Cerebro** | ~165W | 1,445 kWh | ~$448 AUD |
| **Burro** | ~218W | 1,910 kWh | ~$592 AUD |
| **Combined** | | 3,355 kWh | ~$1,040 AUD |

Honest annual electricity cost for the full lab: roughly **$1,000-1,350 AUD per year**.

That's a real cost. It's not free. The question is what you get for it, and what the alternatives cost.

---

## Cost Per Training Run

| Scenario | Duration | Energy | Electricity Cost |
|---|---|---|---|
| Cerebro: one adapter via Unsloth QLoRA | 3 hours | 0.9 kWh | ~$0.28 AUD |
| Burro: one adapter via PEFT overnight | 8 hours | 3.4 kWh | ~$1.05 AUD |

A semester of adapter development (roughly 20 training runs across student groups) adds $6-20 AUD in marginal electricity on top of the idle baseline.

---

## Compared to Cloud GPU Rental

Cloud GPU pricing for a comparable 16 GB card (A4000/V100 class) on platforms like RunPod, Lambda, or Vast.ai runs roughly $0.75-1.15 AUD per hour.

| | Local (Burro) | Cloud GPU |
|---|---|---|
| 8-hour training run | ~$1.05 electricity | ~$6-9 rental |
| 20 runs per semester | ~$21 electricity | ~$120-180 rental |
| 60 runs per year (3 semesters) | ~$63 electricity | ~$360-540 rental |

Cloud wins on per-watt efficiency. Local wins on per-dollar cost by a factor of 6-8x for training, even before accounting for the idle power draw.

But the cloud comparison understates the local advantage in two ways.

First, cloud hours are use-it-or-lose-it. When a student is iterating on dataset formatting, debugging a training script, or just thinking about their approach, the cloud meter is running. Locally, that iteration happens on an idle machine at 120-150W. The "time spent not training" is nearly free locally and expensive on the cloud.

Second, cloud access introduces dependency. If the provider changes pricing, discontinues an instance type, or has an outage during assignment week, you have no fallback. The machines under the desk don't go away.

---

## Compared to New Hardware

The efficiency criticism often takes the form: "Why not just buy a modern GPU? An RTX 4090 trains faster per watt."

True. It also costs $3,000-4,000 AUD for the card alone, plus a system to put it in. Call it $5,000-6,000 AUD for a modern training workstation. A new enterprise-grade server with an A-series GPU starts well above that.

**Return on investment framing:**

The LocoLLM lab's annual electricity cost is roughly $1,000-1,350 AUD. A new workstation that halved the power consumption (generous assumption) would save perhaps $500-675 AUD per year in electricity. At a purchase price of $5,000-6,000 AUD, the payback period on the capital expenditure is **7-12 years** in electricity savings alone.

And new hardware has running costs too. It still draws power. A modern GPU under training load still pulls 300-450W. The idle draw might be lower, but the training draw is comparable or higher. You're paying $5,000+ upfront to save $500/year in power, on equipment that will itself be outdated in 3-5 years.

Meanwhile, the secondhand market continues to offer capable hardware at low cost. Patience and willingness to hunt for deals is the only requirement. The same class of GPUs and servers that LocoLLM uses are still available on eBay, Facebook Marketplace, and surplus dealers. Prices remain accessible for anyone willing to look.

**The AI hardware inflation factor:**

The economics are actually getting more favourable for secondhand buyers, not less. AI data centre demand is driving up prices across the board for new components. NAND flash prices have more than doubled in the past six months. GPU prices remain inflated at every tier. DRAM and even hard drives are affected. New hardware is getting more expensive to acquire, while the secondhand market for previous-generation enterprise equipment remains largely unaffected by that demand.

---

## Data Sovereignty and Ownership

There's a cost that doesn't appear on any invoice: control.

When you train on cloud infrastructure, your training data transits external networks and resides on hardware you don't own. For a university research project handling case study data, student work, or anything adjacent to sensitive domains, that's a compliance conversation at minimum.

When you run inference through a commercial API, every query leaves your network. For students working with business scenarios, client data in case studies, or health-adjacent content in related programs, "the data stays on this machine" is not a feature toggle. It's a structural property of running locally. Nothing leaves because nothing can leave.

Owning the hardware means:
- No terms of service changes that affect your workflow
- No vendor deciding to discontinue the model or instance type you depend on
- No per-query costs that scale with student numbers
- No data processing agreements to negotiate
- No surprise price increases mid-semester

This matters more as data sovereignty regulation tightens. The Australian Privacy Act reforms, sector-specific data handling requirements, and university ethics frameworks all favour architectures where data stays local. Building that into the infrastructure from the start is cheaper than retrofitting it later.

---

## The Real Comparison

| | Local Lab (Annual) | Cloud GPU (Annual) | New Workstation |
|---|---|---|---|
| **Capital cost** | Already acquired | $0 | $5,000-6,000 |
| **Electricity** | ~$1,000-1,350 | N/A | ~$700-900 (estimated) |
| **Compute rental** | $0 | $360-540+ | $0 |
| **API inference** | $0 | Scales with usage | $0 |
| **Data sovereignty** | Complete | Provider-dependent | Complete |
| **Availability** | 24/7, no booking | Subject to availability | 24/7, no booking |
| **Payback period** | Already past | Never (recurring) | 7-12 years |

The local lab costs more in electricity than a modern workstation would. It costs far less than cloud rental. And the hardware investment has already been made, at prices that are increasingly difficult to replicate for new equipment but remain available in the secondhand market for patient buyers.

---

## Summary

Running old hardware 24/7 costs roughly $1,000-1,350 AUD per year in electricity. That's the honest number.

For that, you get unlimited training runs, unlimited inference, complete data sovereignty, zero recurring subscription costs, and full reproducibility on hardware anyone can acquire secondhand.

The question isn't whether the lab is power-efficient. It isn't, compared to current-generation hardware. The question is whether the total cost of ownership, including capital expenditure, electricity, independence, and control, makes sense compared to the alternatives.

It does.
