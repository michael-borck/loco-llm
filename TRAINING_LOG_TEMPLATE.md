# Training Log: [Adapter Name]

## Team

- **Team name:** [e.g., Team Alpha]
- **Members:** [Names and roles]
- **Unit:** [e.g., ISYS6020, Semester 2 2026]
- **Supervisor:** [Name]

## Domain Definition

### Target Task
[Describe what this adapter specializes in. Be specific.]

### Scope
- **In scope:** [What kinds of queries this adapter should handle]
- **Out of scope:** [What it's explicitly not designed for]

### Base Model Failure Analysis
[Describe how the base model performs on this task without the adapter. Include specific examples.]

| Query | Base Model Response | Problem | Ideal Response |
|---|---|---|---|
| [Example 1] | [What it said] | [What went wrong] | [What it should say] |
| [Example 2] | ... | ... | ... |
| [Example 3] | ... | ... | ... |

## Training Data

### Sources
[List all data sources with details]

| Source | Type | Count | Notes |
|---|---|---|---|
| [e.g., GSM8K subset] | Public dataset | 300 | Filtered for multi-step arithmetic only |
| [e.g., Synthetic via Claude] | Synthetic | 250 | Generated using prompt template below |
| [e.g., Expert-written] | Original | 50 | Created by team, reviewed by supervisor |

### Synthetic Data Generation
[If applicable, describe the generation process]

- **Model used:** [e.g., Claude Sonnet 4.5]
- **Prompt template:** [Include the exact prompt]
- **Batch size:** [How many per batch]
- **Review process:** [How you quality-checked]
- **Rejection rate:** [What % were discarded and why]

### Data Statistics

- **Total training examples:** [Number]
- **Total benchmark examples:** [Number, minimum 50]
- **Average input length:** [tokens]
- **Average output length:** [tokens]
- **Difficulty distribution:** [easy/medium/hard split]

### Data Quality Measures
[What steps did you take to ensure quality?]

- [ ] Manual review of X% of examples
- [ ] Deduplication check
- [ ] Format validation
- [ ] Benchmark/training overlap check (zero overlap confirmed)

## Training Runs

### Run 1: [Date]

**Configuration:**
```yaml
base_model: Qwen/Qwen2.5-3B-Instruct
quantization: Q4_K_M (QLoRA)
lora_rank: 16
lora_alpha: 32
learning_rate: 2e-4
epochs: 3
batch_size: 4
max_seq_length: 1024
warmup_steps: 50
```

**Hardware:** [e.g., Google Colab T4, 15GB VRAM]
**Training time:** [e.g., 2 hours 15 minutes]
**Final training loss:** [e.g., 0.85]

**Evaluation results:**
- Adapter score: [X]
- Base model score: [Y]
- Improvement: [Z%]

**Observations:**
[What did you notice? What worked? What didn't?]

### Run 2: [Date] (if applicable)

**Changes from Run 1:**
[What did you change and why?]

**Configuration:** [Only list changes]
**Evaluation results:**
- Adapter score: [X]
- Base model score: [Y]
- Improvement: [Z%]

**Observations:**
[Did the changes help? Why or why not?]

## Final Results

### Domain Benchmark

| Metric | Base Model | Adapter | Improvement |
|---|---|---|---|
| [Primary metric] | [Score] | [Score] | [+X%] |
| [Secondary metric] | [Score] | [Score] | [+X%] |

### Per-Difficulty Breakdown

| Difficulty | Base Model | Adapter | Improvement |
|---|---|---|---|
| Easy | [Score] | [Score] | [+X%] |
| Medium | [Score] | [Score] | [+X%] |
| Hard | [Score] | [Score] | [+X%] |

### Out-of-Domain Check

| Benchmark | Base Model | Adapter | Degradation |
|---|---|---|---|
| [Other domain] | [Score] | [Score] | [X points] |

### Qualitative Examples

**Example 1: Clear improvement**
- Query: [...]
- Base model: [...]
- Adapter: [...]
- Notes: [Why this is better]

**Example 2: Clear improvement**
- [Same format]

**Example 3: Remaining failure case**
- Query: [...]
- Base model: [...]
- Adapter: [...]
- Notes: [Why this still doesn't work well]

## Known Limitations

[What doesn't this adapter handle well? What are the edge cases?]

## Recommendations for Future Teams

[What would you tell the next team working on this domain?]

## Timeline

| Week | Activity | Status |
|---|---|---|
| 1-2 | Domain analysis and base model testing | Complete |
| 2-4 | Data curation and quality review | Complete |
| 4-5 | Fine-tuning and iteration | Complete |
| 5-6 | Evaluation and documentation | Complete |
| 6 | PR submission | Complete |
