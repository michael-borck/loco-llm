"""Adapter manager: loads registry, creates Modelfiles, manages adapters in Ollama."""

import os
from pathlib import Path

import yaml

from locollm import ollama_client


def _locate_adapters_dir():
    """Find the adapters directory.

    Checked in order:
    1. $LOCOLLM_ADAPTERS_DIR, for installed copies and student workspaces
    2. ./adapters relative to the working directory, if it holds a registry
    3. The source checkout layout: src/locollm/adapter_manager.py -> project root

    Without 1 and 2 the package only works from a source clone, since an
    installed copy resolves step 3 to somewhere inside site-packages.
    """
    override = os.environ.get("LOCOLLM_ADAPTERS_DIR")
    if override:
        return Path(override).expanduser().resolve()

    cwd_adapters = Path.cwd() / "adapters"
    if (cwd_adapters / "registry.yaml").is_file():
        return cwd_adapters.resolve()

    return Path(__file__).resolve().parent.parent.parent / "adapters"


ADAPTERS_DIR = _locate_adapters_dir()
REGISTRY_PATH = ADAPTERS_DIR / "registry.yaml"

# Prefix used for Ollama model names created from adapters
ADAPTER_MODEL_PREFIX = "locollm-"


def load_registry():
    """Parse adapters/registry.yaml and return the full config dict."""
    if not REGISTRY_PATH.is_file():
        raise FileNotFoundError(
            f"No adapter registry found at {REGISTRY_PATH}\n"
            "Run loco from a directory containing adapters/registry.yaml, "
            "or set LOCOLLM_ADAPTERS_DIR to point at your adapters directory."
        )
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def get_base_model_name():
    """Return the Ollama model name for the base model from the registry.

    Reads base_model.ollama_name from registry.yaml.
    Raises KeyError if the registry is missing required fields.
    """
    registry = load_registry()
    return registry["base_model"]["ollama_name"]


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
        base_model = adapter_config.get("ollama_base") or get_base_model_name()
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
