# Architecture Decision Records (ADRs)

We use ADRs to capture significant technical and research decisions in LocoLLM.

## What is an ADR?

An Architecture Decision Record is a short document that captures a single decision, including the context, the decision itself, and the consequences. ADRs are **immutable once accepted** — if a decision is reversed, a new ADR supersedes the old one.

## When to write an ADR

Write an ADR when a decision:
- Affects multiple components or the overall system architecture
- Constrains future student work (e.g., base model choice, adapter format)
- Is non-obvious and someone might later ask "why did we do it this way?"
- Changes a previous ADR

You do **not** need an ADR for routine implementation choices.

## Format

Use the template in `0000-template.md`. Key sections:

1. **Title** — short noun phrase (e.g., "Use Qwen3-4B as base model")
2. **Status** — `proposed` | `accepted` | `deprecated` | `superseded by ADR-NNNN`
3. **Context** — What is the issue? What forces are at play?
4. **Decision** — What we decided and why
5. **Consequences** — What becomes easier, harder, or different?

## Numbering

ADRs are numbered sequentially: `0001-`, `0002-`, etc.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-base-model-qwen3-4b.md) | Use Qwen3-4B-Instruct as base model for 2026-2027 | Accepted |
| [0002](0002-adapter-registry-design.md) | YAML-based adapter registry with domain grouping | Proposed |
| [0003](0003-single-evolving-router.md) | Single evolving router over parallel routers | Proposed |
