# LocoLLM Ideas & Open Questions

Captured design discussions and future directions. Items here are **not committed to** — they are candidates for ADRs and the research roadmap.

---

## 1. Multiple Adapters Per Domain

**Context**: Students build specialist adapters each semester. Multiple students may target the same domain (e.g., math) using different training data, LoRA configs, or prompt strategies.

**Proposal**: Allow N adapters per domain. The system maintains a full library but only one is "active" for routing at any time.

### Registry schema changes

```yaml
adapters:
  math-gsm8k:
    domain: "math"            # NEW — groups adapters by domain
    active: true              # NEW — only one per domain is active for routing
    version: "0.2.0"
    type: "merged-gguf"
    gguf_path: "math-gsm8k/gguf/unsloth.Q4_K_M.gguf"
    description: "Math reasoning adapter trained on GSM8K"
    authors: ["Alice Smith"]
    semester: "2026-fall"     # NEW — tracks when adapter was built
    tags: ["math", "arithmetic", "reasoning"]
    eval_dataset: "eval_dataset.jsonl"
    benchmark_scores:         # NEW — structured scores for leaderboard
      gsm8k: 0.72
      math_hard: 0.31
    training:
      base_model: "unsloth/Qwen3-4B-unsloth-bnb-4bit"
      method: "qlora"
      dataset: "GSM8K (200 examples)"
      lora_r: 16
      lora_alpha: 32

  math-competition:
    domain: "math"
    active: false              # not currently used by router
    version: "0.1.0"
    type: "merged-gguf"
    gguf_path: "math-competition/gguf/unsloth.Q4_K_M.gguf"
    description: "Math adapter trained on competition problems"
    authors: ["Bob Jones"]
    semester: "2026-fall"
    tags: ["math", "competition", "olympiad"]
    eval_dataset: "eval_dataset.jsonl"
    benchmark_scores:
      gsm8k: 0.68
      math_hard: 0.45
    training:
      base_model: "unsloth/Qwen3-4B-unsloth-bnb-4bit"
      method: "qlora"
      dataset: "MATH competition subset (300 examples)"
      lora_r: 32
      lora_alpha: 64
```

### Key new fields

| Field | Purpose |
|-------|---------|
| `domain` | Groups adapters so router knows they cover the same territory |
| `active` | Only one adapter per domain is active for routing; rest are in the library |
| `semester` | Tracks provenance — which cohort built this adapter |
| `benchmark_scores` | Structured scores enabling automated leaderboard and "best wins" selection |

### Selection strategies (not mutually exclusive)

1. **Best-on-benchmarks (default)** — Router picks the single best adapter per domain based on eval scores. Zero latency cost.
2. **Ensemble voting** — Run query through 2-3 adapters for the same domain, majority vote on answer. Builds on the existing self-consistency voting design. Higher latency (multiple LoRA swaps).
3. **Fallback chain** — Try best adapter; if confidence is low, try second-best. Requires confidence estimation.

### Leaderboard concept

A CLI command or generated report that shows all adapters ranked per domain:

```
$ loco leaderboard
Domain: math
  Rank  Adapter             GSM8K   MATH-Hard  Active
  1     math-gsm8k          0.72    0.31       *
  2     math-competition    0.68    0.45

Domain: code
  Rank  Adapter             HumanEval  Active
  1     code-python         0.54       *
```

Active adapter is auto-selected as the one with the highest primary benchmark score, unless manually overridden.

---

## 2. Multiple Routers — Hold Off

A single router that evolves through phases (keyword -> classifier -> learned) is simpler and sufficient. If a student wants to improve routing, frame it as upgrading the existing router, not running competing routers in parallel. Revisit if domain overlap becomes severe (10+ domains with fuzzy boundaries).

---

## 3. Adapter Composition

Can two adapters be applied simultaneously? E.g., a "math" adapter + a "formal writing" adapter for a math proof writing task. This is non-trivial with LoRA (weight merging, interference) but worth investigating as a research question.

---

## 4. Confidence-Based Routing

Router outputs a confidence score. If below threshold:
- Fall back to base model (no adapter)
- Try multiple adapters and vote
- Flag the query as "uncertain" to the user

Ties into the ensemble voting idea above.

---

## 5. Adapter Retirement Policy

As new semesters produce better adapters, what happens to old ones?
- Keep in registry with `active: false` and `retired: true`?
- Archive to a separate file?
- How long do we keep GGUF files around? (storage cost)

---

## 6. Cross-Domain Evaluation

Every adapter should be tested on at least one out-of-domain benchmark to check for catastrophic forgetting. This is already in the evaluation standards but could be automated as part of the CI/registration process.
