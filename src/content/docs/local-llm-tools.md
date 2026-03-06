---
title: "Tools for Running Small Language Models Locally"
---

This is a survey of tools that let you run, interact with, and build on small language models on your own hardware. It is not exhaustive. It will date. It was accurate as of March 2026.

LocoLLM is not a replacement for any of these. Several of them may be exactly what you need, and if one of them solves your problem without the complexity of adapters, routers, and training pipelines, use it. LocoLLM exists for a specific niche -- educational research into adapter-based specialisation on consumer hardware -- and makes no claim beyond that.

This page exists so you can make an informed choice.

---

## Model Runners

These tools download, manage, and run language models locally. They handle quantisation formats, GPU acceleration, and expose models for interaction.

### Ollama

**What it is:** A local model runner with a simple CLI and REST API. Pull a model, run it, query it. LocoLLM uses Ollama as its backend.

**Why it matters:** Ollama made local inference accessible. Before Ollama, running a quantised model required manual GGUF downloads, llama.cpp builds, and command-line incantations. Ollama wraps all of that into `ollama pull` and `ollama run`. It handles model management, GPU detection, and serves a local API that other tools can connect to.

**Best for:** Anyone who wants to run models locally without thinking about the plumbing. The CLI is enough for exploration. The API enables everything else on this page.

**Limitations:** No built-in web interface. No fine-tuning. Model library is curated -- you can import custom GGUFs via Modelfiles, but discoverability favours what's in the official library.

[ollama.com](https://ollama.com)

### LM Studio

**What it is:** A desktop application for downloading and running local models, with a built-in chat interface and an OpenAI-compatible API server.

**Why it matters:** LM Studio is the most polished desktop experience for local inference. It has a model browser that searches Hugging Face directly, handles quantisation variant selection visually, and provides a chat interface that feels like a commercial product. The built-in API server means other tools can use it as a backend, similar to Ollama.

**Best for:** Users who prefer a graphical interface over a CLI. Good for exploring what models are available and comparing them side by side. The model browser makes it easier to find and try new models than Ollama's curated library.

**Limitations:** Closed source. macOS, Windows, and Linux support, but the experience varies by platform. Heavier resource footprint than Ollama when idle.

[lmstudio.ai](https://lmstudio.ai)

### llamafile

**What it is:** A single executable file that contains both the inference engine and a model. Download one file, run it, get a local model with a web interface. No installation.

**Why it matters:** llamafile solves the "how do I get this running" problem more completely than anything else. There is no installation step. No Python. No package manager. No GPU driver configuration. One file, one click. Mozilla backs the project, which gives it unusual institutional support for an open-source inference tool.

**Best for:** Demonstrations, workshops, and situations where you need a model running on a machine you don't control. Hand someone a USB drive with a llamafile and they have a working local LLM.

**Limitations:** Model selection is limited to what has been packaged as llamafiles. You can create your own, but most users won't. Performance is competitive with llama.cpp (it's built on it) but not configurable in the way Ollama or LM Studio allow.

[github.com/Mozilla-Ocho/llamafile](https://github.com/Mozilla-Ocho/llamafile)

### GPT4All

**What it is:** A desktop application from Nomic AI for running local models with a chat interface. Includes a local document search feature that lets you chat with your own files.

**Why it matters:** GPT4All was one of the earliest "run it locally" projects and has maintained momentum. The document chat feature (LocalDocs) is built in rather than requiring a separate RAG pipeline. It bundles its own inference backend, so it works without Ollama or any other runtime.

**Best for:** Users who want document chat out of the box without configuring a retrieval pipeline. The LocalDocs feature is genuinely useful for exploring your own files with a local model.

**Limitations:** Smaller model selection than Ollama or LM Studio. The interface is functional but less polished than LM Studio. LocalDocs quality depends heavily on document type and model capability.

[gpt4all.io](https://gpt4all.io)

### LocalAI

**What it is:** An OpenAI API-compatible server that runs models locally. Drop-in replacement for OpenAI's API endpoints using local models.

**Why it matters:** If you have existing code that calls the OpenAI API, LocalAI lets you point it at a local server instead. No code changes beyond the base URL. Supports text generation, embeddings, image generation, and audio transcription through a unified API.

**Best for:** Developers migrating from cloud APIs to local inference. Teams that want to keep their OpenAI-compatible toolchain but run models locally.

**Limitations:** More complex to set up than Ollama. Configuration is powerful but verbose. Better suited to developers than end users.

[localai.io](https://localai.io)

---

## Chat Interfaces

These provide a web-based or desktop chat experience on top of a model runner like Ollama.

### Open WebUI

**What it is:** A self-hosted web interface for interacting with local models. Connects to Ollama or any OpenAI-compatible API. Formerly known as Ollama WebUI.

**Why it matters:** Open WebUI is the most feature-complete open-source chat interface for local models. Multi-user support, conversation history, document upload, web search integration, model switching, system prompt management, and a plugin system. It looks and feels like a self-hosted ChatGPT.

**Best for:** Teams or labs that want a shared chat interface over local models. Multi-user support makes it practical for classrooms or small organisations. The admin controls allow you to manage which models are available and set default system prompts.

**Limitations:** Requires Docker or a Python environment to run. Heavier than simpler alternatives. Feature density can be overwhelming if you just want a chat box.

[openwebui.com](https://openwebui.com)

### AnythingLLM

**What it is:** An all-in-one desktop and server application for local AI. Chat interface, document embedding, RAG pipeline, multi-user workspaces, and agent capabilities in a single install.

**Why it matters:** AnythingLLM bundles what would otherwise require three or four separate tools: a chat interface, a vector database, a document processor, and a workspace manager. It connects to Ollama, LM Studio, or cloud APIs as backends. The workspace model -- separate conversations with separate document collections and separate system prompts -- maps well to project-based work.

**Best for:** Users who want document-grounded chat (RAG) without assembling a pipeline from components. The workspace model is particularly useful for keeping different projects or topics separated with their own context.

**Limitations:** The breadth of features means some are shallower than dedicated tools. Embedding quality depends on the embedding model chosen. Desktop app is Electron-based, which some users find resource-heavy.

[anythingllm.com](https://anythingllm.com)

### Jan

**What it is:** An open-source desktop chat application that runs models locally. Designed as a local-first alternative to ChatGPT.

**Why it matters:** Jan has a clean, focused interface that prioritises the chat experience over feature density. It bundles its own inference engine (based on llama.cpp) and can also connect to remote APIs. The extensions system allows adding functionality without bloating the core experience.

**Best for:** Users who want a simple, clean chat interface without the configuration overhead of Open WebUI or AnythingLLM. Good default experience out of the box.

**Limitations:** Smaller community than Open WebUI. Extension ecosystem is still developing. Less suitable for multi-user or team deployments.

[jan.ai](https://jan.ai)

---

### Msty

**What it is:** A desktop application that provides a unified interface to multiple local and cloud models. Supports Ollama, LM Studio, and cloud providers through a single chat interface.

**Why it matters:** Msty's differentiator is model comparison -- you can send the same prompt to multiple models simultaneously and compare responses side by side. It also supports local RAG with document upload and has a prompt library system.

**Best for:** Comparing model outputs. Useful for evaluation and for understanding how different models handle the same task differently.

**Limitations:** Closed source. Smaller community than Open WebUI or AnythingLLM. Some features require a paid tier.

[msty.ai](https://msty.ai)

---

## CLI and Automation Tools

These are command-line tools for integrating local models into workflows, scripts, and pipelines.

### llm

**What it is:** A command-line tool and Python library by Simon Willison for interacting with language models. Supports both cloud APIs and local models via plugins. The `llm-ollama` plugin connects it to Ollama.

**Why it matters:** `llm` treats language models as Unix-style utilities. Pipe text in, get text out. Conversation logs are stored in a SQLite database, making them queryable and exportable. The plugin architecture means it works with Ollama, OpenAI, Claude, Gemini, and others through a single interface. Fragments allow reusable prompt components.

**Best for:** Developers and power users who work in the terminal. Scripting and automation. Building LLM interactions into shell pipelines. The SQLite log is genuinely useful for reviewing and analysing past conversations.

**Limitations:** CLI-first design means no graphical interface. The plugin ecosystem is broad but some plugins are better maintained than others. Local model support depends on the Ollama plugin rather than being native.

[llm.datasette.io](https://llm.datasette.io)

### fabric

**What it is:** A command-line framework by Daniel Miessler for augmenting human capability with AI. Organised around "patterns" -- reusable prompt templates for specific tasks like summarisation, code review, or extracting insights.

**Why it matters:** fabric's contribution is the pattern library. Rather than writing prompts from scratch each time, you select a pattern that encodes best practices for that task. Patterns are community-contributed and cover a wide range of use cases. It connects to local models via Ollama or to cloud APIs.

**Best for:** Users who find themselves repeating similar prompts. The pattern library is a practical prompt engineering resource even if you don't use fabric itself. Good for building repeatable AI-augmented workflows.

**Limitations:** The value depends heavily on pattern quality, which varies. Learning the pattern system takes time. Some patterns are opinionated about output format.

[github.com/danielmiessler/fabric](https://github.com/danielmiessler/fabric)

---

## How LocoLLM Relates

LocoLLM uses Ollama as its inference backend. It does not replace any of the tools above -- it builds on top of them.

The tools on this page solve the problem of **running and interacting with models**. LocoLLM addresses a different problem: **what happens when you want to specialise a small model for a specific task, benchmark it across hardware tiers, and understand why the results look the way they do?**

If you want to chat with a local model, use any of the tools above. If you want to fine-tune an adapter, evaluate it against the base model, route queries to specialised adapters, and benchmark across consumer GPUs -- that's where LocoLLM operates.

Most of the tools above are complementary rather than competitive:

- **Ollama** is LocoLLM's runtime. LocoLLM registers adapter models with Ollama and queries them through its API.
- **Open WebUI** or **AnythingLLM** can serve as a frontend for models that LocoLLM has trained and registered with Ollama.
- **llm** can query LocoLLM's adapter models via the Ollama plugin, integrating them into shell pipelines.
- **LM Studio** can load the same GGUF files that LocoLLM produces, providing an alternative way to interact with trained adapters.

The honest assessment: for most people exploring local AI, the tools on this page are sufficient. LocoLLM is for the subset who want to go further -- to train, evaluate, and understand small models on hardware they own.

---

*Last reviewed: March 2026. Tools in this space move fast. If something here is outdated, it probably is.*
