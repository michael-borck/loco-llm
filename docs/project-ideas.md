# LocoLLM Project Ideas

A catalogue of self-contained projects for capstone students and contributors. Each project is scoped to be achievable in one semester by a team of 2-4 people. Projects are grouped by discipline focus, but most are cross-disciplinary — a web interface project needs both design thinking and technical implementation.

**How to read this page:** Pick a project that interests you. Read the description and deliverables. If it sounds like something you want to work on, talk to the project lead. Most of the skills listed are learnable during the project — attitude and curiosity matter more than existing expertise.

---

## Adapters: New Domains

Build a new specialist adapter that extends the LocoLLM system. Each adapter project follows the same cycle: curate data, train the adapter, evaluate it, document the results, and submit a PR.

### A1. Statistics & Data Analysis Adapter

Train an adapter that handles descriptive statistics, hypothesis testing, and data interpretation. Data sources: statistics textbook problems, Kaggle dataset descriptions, introductory stats course materials.

**Why it matters:** Statistics sits at the intersection of math and analysis — the current router has no good home for "what does this p-value mean?" questions. This adapter tests whether domain specialisation helps at the boundary between existing domains.

**Deliverables:** Trained adapter (GGUF), evaluation dataset (50+ problems), training log, benchmark comparison vs base model and vs math adapter on statistics queries.

**Discipline fit:** Information Systems, Data Analysis, Business Analytics

**Skills:** Data curation (most important), basic Python, statistical literacy, technical writing

---

### A2. Business Writing Adapter

Train an adapter for business communication: emails, proposals, executive summaries, meeting agendas. Training data from business writing guides, style manuals, and curated examples.

**Why it matters:** Most AI writing tools optimise for generic fluency. A business writing specialist could learn conventions (brevity, action orientation, audience awareness) that a general model handles poorly.

**Deliverables:** Trained adapter, evaluation rubric (scored by LLM-judge or human evaluation), style guide for the training data, benchmark results.

**Discipline fit:** Marketing, Management, Business Communication

**Skills:** Strong writing ability, data curation, understanding of business communication norms, basic Python

---

### A3. Security & Risk Analysis Adapter

Train an adapter for cybersecurity concepts: risk assessment, vulnerability analysis, policy interpretation, incident response. Data from NIST frameworks, OWASP guides, and security case studies.

**Why it matters:** Security is a high-value domain where incorrect answers are dangerous. This project tests whether a small model can learn to be cautious and accurate in a domain where confidence calibration matters.

**Deliverables:** Trained adapter, evaluation dataset covering multiple security sub-domains, analysis of failure modes (where does the adapter give dangerously wrong answers?), comparison with base model.

**Discipline fit:** Information Systems, Cybersecurity, IT Management

**Skills:** Security domain knowledge, data curation, evaluation design, Python

---

### A4. Legal / Compliance Adapter

Train an adapter for plain-language explanation of legal and compliance concepts: privacy law (GDPR, Australian Privacy Act), contract interpretation, regulatory compliance. Not for legal advice — for understanding.

**Why it matters:** Business students encounter legal concepts constantly but legal language is opaque. An adapter that translates legalese into plain language has clear educational value. Also tests the "good enough threshold" — how accurate must a legal adapter be to be useful rather than harmful?

**Deliverables:** Trained adapter, evaluation dataset with expert-verified answers, explicit limitations document (what the adapter should NOT be used for), benchmark results.

**Discipline fit:** Law, Business Law, Compliance, Information Systems

**Skills:** Legal literacy, careful data curation (accuracy is critical), evaluation design, technical writing

---

## Infrastructure: Making the System Better

Improve LocoLLM's core infrastructure. These projects work on the system itself rather than individual adapters.

### I1. Classifier Router

Replace the keyword router with a machine learning classifier. The current router matches keywords — it works for 3 adapters but will not scale to 10+. Build a router that uses text classification (TF-IDF + logistic regression, or a small sentence transformer) to route queries.

**Why it matters:** This is the core research question — does intelligent routing add value over a well-prompted base model? The classifier router is the first step toward answering it with real data.

**Deliverables:** Working classifier router (pluggable, same interface as keyword router), training pipeline using existing benchmark examples as labelled data, routing accuracy benchmark, comparison with keyword router.

**Discipline fit:** Information Systems, Data Analysis, AI/ML

**Skills:** Python, basic ML concepts (classification, train/test split), evaluation methodology

---

### I2. Web Chat Interface

Build a browser-based chat interface for LocoLLM. The current CLI works but is not approachable for non-technical users. A web UI would make the system accessible to students who are not comfortable in a terminal.

**Why it matters:** If LocoLLM is a teaching tool, it needs to be usable by the people it is meant to teach. Not everyone learns best in a terminal. A web interface also opens the door to features like conversation history, adapter selection dropdowns, and visual feedback on routing decisions.

**Deliverables:** Working web chat UI (Flask/FastAPI + simple frontend), adapter selection, routing indicator (shows which adapter is handling the query), conversation history, deployment documentation.

**Discipline fit:** Information Systems, Web Development, UX Design

**Skills:** Python (Flask or FastAPI), basic HTML/CSS/JavaScript, API design, UX thinking

---

### I3. Leaderboard & Adapter Dashboard

Build an automated leaderboard that ranks adapters by domain using benchmark scores. Display training metadata, version history, and performance trends across semesters.

**Why it matters:** As the adapter library grows, students need to see where their work stands relative to others. A leaderboard creates healthy competition and makes the project's progress visible. It also provides the data needed to decide which adapters to activate for routing.

**Deliverables:** Leaderboard CLI command (`loco leaderboard`), generated static report (HTML or markdown), integration with registry benchmark scores, semester-over-semester trend tracking.

**Discipline fit:** Information Systems, Data Analysis, Data Visualisation

**Skills:** Python, data processing, basic web or reporting (static site generation), registry/YAML understanding

---

### I4. Tool Use Integration

Add a Python sandbox that adapters can call during inference. Train a proof-of-concept adapter (math) that generates tool calls instead of computing answers directly. Benchmark tool-calling vs direct computation.

**Why it matters:** Language models are bad at arithmetic. Computers are good at it. This project tests whether small models can learn to delegate computation to tools — the same pattern that frontier models use with code interpreter. See [Architecture Vision](architecture-vision.md#tool-use-let-models-do-what-models-are-good-at) for the full rationale.

**Deliverables:** Python sandbox (safe subprocess execution), tool-call training data for math adapter, retrained math adapter, benchmark comparison (tool-calling vs direct), latency analysis.

**Discipline fit:** Information Systems, Software Engineering, AI/ML

**Skills:** Python, subprocess/sandboxing, training data design, evaluation methodology

---

### I5. Automated Rebuild Pipeline

Build a pipeline that retrains all adapters when the base model changes. Automate: pull new base model, retrain each adapter, export GGUFs, run benchmarks, generate comparison report.

**Why it matters:** The base model changes yearly. With 3 adapters, manual retraining is fine. With 15, it is a day of manual work. Automation turns the annual rebuild into a one-command operation and makes base model migration decisions evidence-based.

**Deliverables:** Pipeline script (or Makefile), parameterised training configs, automated benchmark runner, comparison report generator (old base vs new base for each adapter).

**Discipline fit:** Information Systems, DevOps, Software Engineering

**Skills:** Python, scripting/automation, CI/CD concepts, testing methodology

---

## Evaluation & Research

Projects focused on understanding how well the system works and generating publishable findings.

### R1. Domain Benchmark Suite

Design and build comprehensive evaluation benchmarks for each adapter domain. The current benchmarks are minimal (50 questions). Production-quality benchmarks need 200+ questions per domain, difficulty tiers, and cross-domain contamination checks.

**Why it matters:** Benchmarks are the foundation of every claim the project makes. Weak benchmarks mean weak conclusions. This project directly improves the rigour of every other project's results.

**Deliverables:** Expanded benchmark datasets for each domain, difficulty-tiered questions, contamination analysis (do benchmark questions appear in training data?), benchmark methodology document.

**Discipline fit:** Data Analysis, Research Methods, Information Systems

**Skills:** Domain knowledge (for question quality), data analysis, research methodology, attention to detail

---

### R2. Base Model Comparison Study

Systematically compare 3-5 candidate base models across all adapter domains. For each base model: train all adapters, run all benchmarks, measure quality, speed, and memory. Produce an evidence-based recommendation for the next academic year's base model.

**Why it matters:** The base model decision is the highest-impact choice in the project. Currently it is made by reviewing published benchmarks and community consensus. This project would generate first-party evidence under LocoLLM's specific constraints (4-bit, consumer hardware, LoRA fine-tuned).

**Deliverables:** Comparison report covering quality (benchmark scores per domain), speed (tokens/second), memory (peak RAM), and fine-tuning responsiveness (how much does each base model improve with LoRA?). Recommendation with supporting data.

**Discipline fit:** Data Analysis, Research Methods, Information Systems

**Skills:** Systematic evaluation, data analysis, technical writing, basic Python

---

### R3. User Experience Study

How do students actually use LocoLLM? Observe students using the system for real tasks. Document usage patterns, pain points, feature requests, and whether the "conversation not delegation" philosophy holds in practice.

**Why it matters:** The project makes assumptions about how students will use AI tools. This project tests those assumptions with real users. The findings inform both the technical roadmap and the pedagogical framing.

**Deliverables:** Study design (ethics approval if required), observation protocol, user interviews or surveys, findings report, actionable recommendations for the project.

**Discipline fit:** Marketing (consumer behaviour), Management (organisational behaviour), Information Systems (technology adoption)

**Skills:** Research design, qualitative analysis, interviewing, report writing

---

### R4. Cost-Benefit Analysis: Local vs Cloud AI

Quantify the total cost of ownership for LocoLLM vs cloud AI alternatives across a semester. Include hardware, electricity, setup time, maintenance, and the value of capabilities that are hard to price (privacy, no rate limits, offline access).

**Why it matters:** "It's free" is an oversimplification. Students' time has value. Hardware has cost. This project produces an honest economic analysis that either supports or challenges the local-first thesis.

**Deliverables:** Cost model (spreadsheet or tool), sensitivity analysis (what if electricity costs X? what if free tiers improve?), comparison across student personas (budget-constrained, time-constrained, privacy-conscious), written report.

**Discipline fit:** Business Analytics, Economics, Information Systems, Management

**Skills:** Financial modelling, cost analysis, research methodology, clear writing

---

## Documentation & Communication

Projects that improve how the project communicates with its audiences.

### D1. Onboarding Experience

Redesign the getting-started experience for new users and contributors. Current docs are thorough but assume technical comfort. Create a guided pathway that takes someone from "what is this?" to "I have a working adapter" with minimal friction.

**Why it matters:** The best system in the world is useless if people cannot get started with it. The onboarding experience determines whether a new student contributes or gives up in the first hour.

**Deliverables:** Revised getting-started guide, quick-start tutorial (15 minutes to first result), troubleshooting FAQ, user testing with 3-5 new users, before/after comparison of setup success rate.

**Discipline fit:** Marketing (communications), Information Systems, UX Design

**Skills:** Clear writing, empathy for beginners, user testing, basic familiarity with git/CLI

---

### D2. Project Website & Marketing

Design and build a public-facing project website that communicates what LocoLLM is, why it matters, and how to get involved. Current landing page exists but could be more compelling. Consider audience: prospective students, academic colleagues, open-source contributors.

**Why it matters:** The project needs to attract contributors and communicate its value to stakeholders (faculty, potential collaborators, funding bodies). The website is the first impression.

**Deliverables:** Redesigned website (static site), clear messaging for each audience, visual design, analytics setup, content strategy document.

**Discipline fit:** Marketing, Communications, Web Design, Information Systems

**Skills:** Web design (static site generators), copywriting, visual design, audience analysis, basic analytics

---

### D3. Video Tutorials & Demos

Create a series of short video tutorials (3-5 minutes each) covering key workflows: setup, training an adapter, running evaluation, using chat, contributing a PR.

**Why it matters:** Not everyone learns from documentation. Video lowers the barrier for visual learners and creates shareable content that can be used in lectures, social media, and conference presentations.

**Deliverables:** 4-6 short videos, scripts, screen recordings with narration, published to YouTube or equivalent, linked from project docs.

**Discipline fit:** Marketing (content creation), Communications, Education

**Skills:** Screencasting, clear narration, basic video editing, understanding of the workflows being demonstrated

---

## A Note on Skills

Every project lists relevant skills, but here is the honest truth: **most of these skills are learnable during the project.** Nobody arrives at a capstone knowing everything they need. The projects are designed so that the learning *is* the work.

What matters more than any specific skill:

- **Curiosity** — willingness to figure out how things work, not just follow instructions
- **Persistence** — things will break, results will be unexpected, the first attempt will not work
- **Communication** — the ability to explain what you did and what you found, clearly and honestly
- **Collaboration** — these are team projects; showing up and contributing consistently matters more than brilliance

If a project interests you but you are not sure you have the skills, that is probably the right project. The one that stretches you is the one you will learn the most from.

---

## How Projects Connect

These projects are not isolated. They feed into each other:

```
New adapters (A1-A4)
    |
    +--> need benchmarks (R1) to prove they work
    +--> appear on the leaderboard (I3)
    +--> benefit from tool use (I4)
    |
Router upgrade (I1)
    |
    +--> uses benchmark data as training labels
    +--> tested by the UX study (R3)
    |
Web interface (I2)
    |
    +--> makes UX study (R3) possible at scale
    +--> benefits from onboarding work (D1)
    |
Rebuild pipeline (I5)
    |
    +--> uses base model comparison (R2) to decide what to rebuild against
    +--> retrains all adapters (A1-A4) automatically
```

A team working on any one project benefits from and contributes to the others. This is by design — it mirrors how real software projects work.
