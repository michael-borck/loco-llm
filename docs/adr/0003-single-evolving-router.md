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

## Consequences

- Simpler system architecture — one code path for routing
- Students must coordinate on router changes (PR review process)
- If the classifier router proves inadequate, the upgrade path to learned routing is clearer
- Revisit this decision if domain count exceeds ~20 and a hierarchical routing approach becomes necessary
