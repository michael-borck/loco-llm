"""LocoLLM command-line interface."""

import argparse
import sys

from locollm import __version__


def cmd_setup(args):
    """Pull base model and register adapters."""
    from locollm import adapter_manager, ollama_client

    if not ollama_client.check_running():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    # Pull base model
    registry = adapter_manager.load_registry()
    base_model = registry["base_model"].get("ollama_name", "qwen3:4b")
    installed = ollama_client.list_models()
    installed_base = {m.split(":")[0] for m in installed}

    if base_model.split(":")[0] in installed_base:
        print(f"Base model '{base_model}' already installed.")
    else:
        print(f"Pulling base model '{base_model}'...")
        ollama_client.pull_model(base_model)
        print(f"Base model '{base_model}' ready.")

    # Create adapter models
    for name, _ in adapter_manager.list_adapters():
        try:
            adapter_manager.ensure_adapter_model(name)
        except FileNotFoundError as e:
            print(f"Skipping adapter '{name}': {e}")
            print("  (Train the adapter first, then re-run setup.)")

    print("\nSetup complete!")


def cmd_query(args):
    """Query a model, optionally with an adapter."""
    from locollm import adapter_manager, ollama_client

    if not ollama_client.check_running():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if args.adapter:
        config = adapter_manager.get_adapter(args.adapter)
        if config is None:
            print(f"Error: Adapter '{args.adapter}' not found in registry.")
            sys.exit(1)
        model = adapter_manager.adapter_model_name(args.adapter)
        # Ensure the adapter model exists
        installed = ollama_client.list_models()
        installed_base = {m.split(":")[0] for m in installed}
        if model not in installed_base:
            print("Adapter model not found. Run 'loco setup' first.")
            sys.exit(1)
        print(f"[adapter: {args.adapter}]")
    else:
        registry = adapter_manager.load_registry()
        model = registry["base_model"].get("ollama_name", "qwen3:4b")

    for chunk in ollama_client.generate(model, args.prompt):
        print(chunk, end="", flush=True)
    print()


def cmd_eval(args):
    """Run evaluation benchmark comparing base model vs adapter."""
    from locollm import adapter_manager, ollama_client
    from locollm.eval import format_results, load_dataset, run_eval

    if not ollama_client.check_running():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    adapter_name = args.adapter_name
    config = adapter_manager.get_adapter(adapter_name)
    if config is None:
        print(f"Error: Adapter '{adapter_name}' not found in registry.")
        sys.exit(1)

    dataset_path = adapter_manager.get_eval_dataset_path(adapter_name)
    if dataset_path is None or not dataset_path.exists():
        print(f"Error: No evaluation dataset found for adapter '{adapter_name}'.")
        sys.exit(1)

    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} problems from {dataset_path.name}")

    # Get model names
    registry = adapter_manager.load_registry()
    base_model = registry["base_model"].get("ollama_name", "qwen3:4b")
    adapter_model = adapter_manager.adapter_model_name(adapter_name)

    # Check adapter model exists
    installed = ollama_client.list_models()
    installed_base = {m.split(":")[0] for m in installed}
    if adapter_model not in installed_base:
        print("Adapter model not found. Run 'loco setup' first.")
        sys.exit(1)

    # Run base model eval
    print(f"\nEvaluating base model ({base_model})...")
    base_correct, base_total, _ = run_eval(base_model, dataset)

    # Run adapter eval
    print(f"\nEvaluating adapter model ({adapter_model})...")
    adapter_correct, adapter_total, _ = run_eval(adapter_model, dataset)

    format_results(base_correct, base_total, adapter_correct, adapter_total, adapter_name)


def cmd_adapters_list(args):
    """List all registered adapters."""
    from locollm import adapter_manager

    adapters = adapter_manager.list_adapters()
    if not adapters:
        print("No adapters registered.")
        return

    print(f"{'Name':<15} {'Type':<15} {'Description'}")
    print(f"{'-' * 15} {'-' * 15} {'-' * 30}")
    for name, config in adapters:
        atype = config.get("type", "unknown")
        desc = config.get("description", "")
        print(f"{name:<15} {atype:<15} {desc}")


def main():
    parser = argparse.ArgumentParser(
        prog="loco",
        description="LocoLLM: Local Collaborative LLMs",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    # setup
    sp_setup = subparsers.add_parser("setup", help="Pull base model and register adapters")
    sp_setup.set_defaults(func=cmd_setup)

    # query
    sp_query = subparsers.add_parser("query", help="Query a model")
    sp_query.add_argument("prompt", help="The prompt to send")
    sp_query.add_argument("--adapter", help="Name of adapter to use")
    sp_query.set_defaults(func=cmd_query)

    # eval
    sp_eval = subparsers.add_parser("eval", help="Run evaluation benchmark")
    sp_eval.add_argument("adapter_name", help="Name of adapter to evaluate")
    sp_eval.set_defaults(func=cmd_eval)

    # adapters
    sp_adapters = subparsers.add_parser("adapters", help="Manage adapters")
    adapters_sub = sp_adapters.add_subparsers(dest="adapters_command")
    sp_adapters_list = adapters_sub.add_parser("list", help="List registered adapters")
    sp_adapters_list.set_defaults(func=cmd_adapters_list)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
