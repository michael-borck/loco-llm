# LocoLLM Research Roadmap

This document outlines the research questions, milestones, and evaluation criteria for the LocoLLM project.

## Core Research Question

> Can a routed swarm of fine-tuned small language models (4B parameters, 4-bit quantization) outperform a generalist model of equivalent size on real-world tasks, while running entirely on consumer hardware?

### Sub-Questions

1. **Specialisation vs generalisation**: At what point does a specialist adapter reliably beat the base model, and how much training data is needed?
2. **Routing accuracy**: How well can a lightweight router direct queries to the right specialist, and what is the cost of misrouting?
3. **Ensemble effects**: Does voting across multiple adapters for the same domain improve accuracy beyond the single best adapter?
4. **Inference-time enhancements**: How much do RE2 prompting and self-consistency voting improve results when compute is free (local inference)?
5. **Scaling the swarm**: How does system performance change as we add more domains (5 -> 10 -> 20 adapters)?

---

## Phased Milestones

### Phase 1: Foundation (Semester 1, 2026)
**Goal**: Prove the concept with 3-5 adapters in clearly distinct domains.

| Milestone | Deliverable | Success Criteria |
|-----------|------------|-----------------|
| Base model selected | ADR-0001, benchmarks | Model fits 8GB, strong baseline |
| First adapter (math) | Trained LoRA, eval results | Beats base model on GSM8K |
| Evaluation harness | `loco eval` command | Reproducible, automated benchmarks |
| Keyword router | v1 router implementation | Correct routing on 90%+ of test queries |
| 3 domain adapters | math, code, writing (minimum) | Each beats base model on domain benchmark |
| Registry v2 | Domain grouping, benchmark scores | Supports multiple adapters per domain |

### Phase 2: Scale & Compete (Semester 2, 2027)
**Goal**: 6-10 adapters, classifier router, first ensemble experiments.

| Milestone | Deliverable | Success Criteria |
|-----------|------------|-----------------|
| Classifier router | ML-based routing | Handles domain overlap, >85% accuracy |
| Multi-adapter domains | 2+ adapters per domain | Leaderboard shows ranking |
| Ensemble voting | Cross-adapter voting mode | Measurable accuracy gain vs single adapter |
| Out-of-domain testing | Automated regression checks | No adapter degrades base model by >5% |
| Adapter installer | `loco adapters install` | Students can share adapters easily |

### Phase 3: Research Depth (Semester 3+, 2027-2028)
**Goal**: Push the boundaries — confidence routing, adapter composition, sub-4-bit quantization.

| Milestone | Deliverable | Success Criteria |
|-----------|------------|-----------------|
| Confidence routing | Router with uncertainty estimation | Graceful fallback on ambiguous queries |
| Adapter composition | Multi-adapter inference | Meaningful quality gain on cross-domain tasks |
| 1.58-bit exploration | BitNet-style quantization | Feasibility study on quality vs memory |
| Learned router | Feedback-driven routing | Improves with usage data |

---

## Evaluation Framework

### Per-Adapter Acceptance Criteria

Every adapter submission must demonstrate:

1. **Domain improvement**: Statistically significant accuracy gain over base model on the target domain benchmark (minimum 50 test cases)
2. **No catastrophic forgetting**: Out-of-domain performance within 5% of base model
3. **Reproducibility**: Training script, data, config, and log all included
4. **Documentation**: Training log following `TRAINING_LOG_TEMPLATE.md`

### System-Level Metrics

Track these across the full system over time:

| Metric | Description | Target |
|--------|-------------|--------|
| **Routing accuracy** | % of queries routed to correct domain | >90% (Phase 1), >95% (Phase 2) |
| **Composite score** | Weighted average across all domain benchmarks | Higher than base model on every domain |
| **Latency** | Time to route + generate response | <5s on consumer hardware |
| **Memory footprint** | Peak RAM during inference | <8GB always |
| **Adapter swap time** | Time to switch between adapters | <500ms |

### Benchmark Suite

Each domain maintains its own benchmark. The system-level benchmark is the union:

| Domain | Benchmark | Metric | Baseline (base model) |
|--------|-----------|--------|----------------------|
| Math | GSM8K subset | Exact match accuracy | 0.41 |
| Code | HumanEval subset | pass@1 | TBD |
| Writing | Custom rubric | LLM-judge score | TBD |
| Summarisation | ROUGE-L | Token overlap | TBD |
| ... | ... | ... | ... |

---

## User Stories

LocoLLM serves three user types. While not a traditional application, framing requirements as user stories clarifies what we're building and defines acceptance criteria for testing.

### Student Developer

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| SD-01 | As a student, I want to train a new adapter for a domain so that I can contribute a specialist to the swarm | Adapter guide exists; training script template works end-to-end; adapter can be registered in registry.yaml |
| SD-02 | As a student, I want to evaluate my adapter against the base model so that I can prove it improves performance | `loco eval <adapter>` runs and produces a comparison report |
| SD-03 | As a student, I want to submit my adapter via PR so that it joins the library | PR template includes checklist; CI validates registry format |
| SD-04 | As a student, I want to see how my adapter ranks against others in the same domain | `loco leaderboard` shows per-domain rankings |
| SD-05 | As a student, I want to build a better router so that query classification improves | Router is a pluggable module with a defined interface; router accuracy benchmark exists |

### End User (Researcher / Tester)

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| EU-01 | As a user, I want to ask a question and get the best available answer without choosing an adapter manually | Router automatically selects the best adapter; response quality >= manual selection |
| EU-02 | As a user, I want to run LocoLLM on my laptop with 8GB RAM | Setup completes; inference runs without OOM; documented system requirements |
| EU-03 | As a user, I want to install a specific adapter from the library | `loco adapters install <name>` downloads and registers it |
| EU-04 | As a user, I want to see which adapter handled my query | CLI output includes adapter name and confidence (when available) |

### Project Lead / Instructor

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| PL-01 | As the project lead, I want to compare all adapters for a domain on a common benchmark | Leaderboard is auto-generated from registry benchmark scores |
| PL-02 | As the project lead, I want to promote the best adapter to "active" for a domain | `active` flag in registry; `loco promote <adapter>` command |
| PL-03 | As the project lead, I want to track system-level performance over semesters | Results archived per semester; trend report |
| PL-04 | As the project lead, I want to set the base model for the next academic year | ADR process for base model selection; migration guide |

---

## Open Research Questions

Tracked in `docs/ideas.md`. Key items:

- Ensemble voting across same-domain adapters — latency vs accuracy tradeoff
- Adapter composition (stacking two LoRAs) — feasibility and interference
- Confidence-based routing with fallback chains
- Adapter retirement policy for long-term registry management
- Sub-4-bit quantization (1.58-bit BitNet) viability

---

## Semester Planning Template

For each semester, create a plan covering:

1. **Domains to target**: Which new domains will students build adapters for?
2. **Infrastructure goals**: Which system features are prioritised (router upgrade, voting, installer)?
3. **Research experiments**: Which open questions will be investigated?
4. **Evaluation milestones**: What benchmarks and scores are we aiming for?
5. **Student allocation**: How many students per domain? Solo vs team?
