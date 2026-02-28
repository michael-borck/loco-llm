"""Adapter manager: loads registry, creates Modelfiles, manages adapters in Ollama."""

from pathlib import Path

import yaml

from locollm import ollama_client

# Locate the adapters directory relative to the project root.
# Walk up from this file: src/locollm/adapter_manager.py -> project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ADAPTERS_DIR = _PROJECT_ROOT / "adapters"
REGISTRY_PATH = ADAPTERS_DIR / "registry.yaml"

# Prefix used for Ollama model names created from adapters
ADAPTER_MODEL_PREFIX = "locollm-"


def load_registry():
    """Parse adapters/registry.yaml and return the full config dict."""
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def get_adapter(name):
    """Return the config dict for a single adapter, or None."""
    registry = load_registry()
    adapters = registry.get("adapters") or {}
    return adapters.get(name)


def list_adapters():
    """Return a list of (name, config) tuples for all registered adapters."""
    registry = load_registry()
    adapters = registry.get("adapters") or {}
    return list(adapters.items())


def _build_modelfile(adapter_config, registry):
    """Build a Modelfile string from an adapter config.

    Supports two adapter types:
    - system-prompt: layers a system prompt on the base model (MVP placeholder)
    - merged-gguf: uses a standalone GGUF with LoRA weights merged in
    """
    adapter_type = adapter_config.get("type", "system-prompt")

    if adapter_type == "system-prompt":
        base_model = adapter_config.get("ollama_base", "qwen3:4b")
        system_prompt = adapter_config.get("system_prompt", "")
        return f'FROM {base_model}\nSYSTEM """{system_prompt}"""'
    elif adapter_type == "merged-gguf":
        gguf_path = adapter_config.get("gguf_path")
        if not gguf_path:
            raise ValueError("merged-gguf adapter requires 'gguf_path' in config")
        # Resolve relative to adapters directory
        full_path = ADAPTERS_DIR / gguf_path
        if not full_path.exists():
            raise FileNotFoundError(f"GGUF file not found: {full_path}")
        return f"FROM {full_path}"
    else:
        raise ValueError(f"Unsupported adapter type: {adapter_type}")


def adapter_model_name(adapter_name):
    """Return the Ollama model name for a given adapter."""
    return f"{ADAPTER_MODEL_PREFIX}{adapter_name}"


def ensure_adapter_model(adapter_name):
    """Create the Ollama model for an adapter if it doesn't already exist.

    Returns the Ollama model name.
    """
    config = get_adapter(adapter_name)
    if config is None:
        raise ValueError(f"Adapter '{adapter_name}' not found in registry")

    model_name = adapter_model_name(adapter_name)

    # Check if it already exists
    installed = ollama_client.list_models()
    # Ollama model names may include :latest suffix
    installed_base = {m.split(":")[0] for m in installed}
    if model_name in installed_base:
        print(f"Adapter model '{model_name}' already exists.")
        return model_name

    registry = load_registry()
    modelfile = _build_modelfile(config, registry)
    print(f"Creating adapter model '{model_name}'...")
    ollama_client.create_model(model_name, modelfile)
    return model_name


def get_eval_dataset_path(adapter_name):
    """Return the path to the evaluation dataset for an adapter, or None."""
    config = get_adapter(adapter_name)
    if config is None:
        return None
    dataset_file = config.get("eval_dataset")
    if dataset_file:
        return ADAPTERS_DIR / adapter_name / dataset_file
    return None
