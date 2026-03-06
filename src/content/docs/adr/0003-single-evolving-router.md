---
title: "ADR-0003: Single Evolving Router Over Parallel Routers"
---

# ADR-0003: Single Evolving Router Over Parallel Routers

## Status

Proposed

## Date

2026-03-01

## Context

As the adapter library grows, routing becomes more important. One question is whether to support multiple competing routers (e.g., a student builds a "math router v2" alongside the existing one) or maintain a single router that evolves through planned phases.

The planned phases are:
1. **Keyword router** — pattern matching, suitable for 3-5 clearly distinct domains
2. **Classifier router** — lightweight ML classifier, needed at 6+ domains with overlap
3. **Learned router** — embeddings, feedback, confidence scores

## Decision

Maintain a **single router** that evolves through the planned phases. If a student wants to improve routing, they upgrade the existing implementation rather than running a parallel one.

**Rationale**:
- The router is a thin dispatch layer, not a domain-specific model — there's little value in maintaining alternatives
- A single router avoids the meta-problem of "which router should route to which router"
- Students get more impact by improving the shared router than by building an isolated one
- Benchmark improvements to routing are measurable (routing accuracy on a held-out query set)

## Open Design Problems

### Base-model fallback lacks a confidence signal

The v1 keyword router returns `None` (base model) only when zero keywords match. A single keyword hit routes with full confidence — there is no threshold or margin check. As adapter keyword lists grow, fewer queries fall through to base, even when the match is weak.

The v2 classifier should route on **confidence margin**, not just top score. If the top adapter scores 0.52 and the runner-up scores 0.48, the router should signal low confidence. That signal can mean: fall back to base, or flag the output ("routed to X, but confidence was low").

### Compound queries

A query like "Write a Python function to solve this quadratic equation and explain the math" spans code, math, and analysis. Three possible strategies:

1. **Winner-take-all** — pick the highest-scoring adapter. Simple, current behavior. Loses the secondary intent.
2. **Decompose and dispatch** — split the query into sub-queries, route each to a specialist, stitch responses together. Powerful but requires a decomposition step (which itself needs a model or heuristic).
3. **Fall back to base** — if no adapter wins clearly, use the base model. Safe but wastes the adapters.

Decomposition is harder than it looks because sub-queries can be independent ("What's 15+27? Also write a haiku"), dependent ("Write the function and explain the math behind it"), or entangled ("Analyze this code for mathematical correctness"). Detecting which case applies is itself a classification problem.

**For v1/v2**: winner-take-all is the right call. The confidence margin above gives a signal that a query *might* be compound — a narrow gap between the top two adapters suggests overlapping domains. For now, `loco chat` can note this: "routed to X (low confidence) — try /adapter to pick manually, or split your query."

**For v3**: decompose-and-dispatch becomes feasible once the router produces per-adapter probabilities rather than hard classifications.

## Consequences

- Simpler system architecture — one code path for routing
- Students must coordinate on router changes (PR review process)
- If the classifier router proves inadequate, the upgrade path to learned routing is clearer
- Revisit this decision if domain count exceeds ~20 and a hierarchical routing approach becomes necessary
