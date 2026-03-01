# ADR-0002: YAML-Based Adapter Registry with Domain Grouping

## Status

Proposed

## Date

2026-03-01

## Context

Multiple students may build adapters for the same domain (e.g., math) across semesters, using different training data, LoRA configurations, or strategies. The registry needs to:

1. Store all adapters as a library (not just the current best)
2. Group adapters by domain so the router can find candidates
3. Track which adapter is active for routing per domain
4. Record benchmark scores for automated leaderboard generation
5. Track provenance (which semester/cohort built it)

The current registry is flat — one adapter per name, no domain grouping.

## Decision

Extend `adapters/registry.yaml` with three new fields per adapter:

- **`domain`** (required): Groups adapters that cover the same task area (e.g., `math`, `code`, `summarization`). The router operates at the domain level.
- **`active`** (boolean, default `false`): At most one adapter per domain is active. The active adapter is what the router selects. Can be set manually or auto-promoted based on benchmark scores.
- **`semester`** (string): Academic semester when the adapter was created (e.g., `2026-fall`).
- **`benchmark_scores`** (dict): Named benchmark results enabling automated comparison.

Adapter names become more specific to distinguish within a domain: `math-gsm8k`, `math-competition`, `code-python`, etc.

## Consequences

- Students can freely build competing adapters without displacing previous work
- The "best wins" model is transparent — benchmark scores decide the active adapter
- Registry file grows over time; may need to split into per-domain files in later years
- Router logic becomes simpler — it routes to a domain, then the registry resolves which adapter
- Migration required: rename `math` -> `math-gsm8k` and add new fields
