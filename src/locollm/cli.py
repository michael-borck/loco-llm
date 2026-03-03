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
    elif not args.no_route:
        # Auto-route using keyword router
        from locollm.router import KeywordRouter

        router = KeywordRouter()
        routed = router.route(args.prompt)
        if routed:
            config = adapter_manager.get_adapter(routed)
            model = adapter_manager.adapter_model_name(routed)
            installed = ollama_client.list_models()
            installed_base = {m.split(":")[0] for m in installed}
            if model in installed_base:
                print(f"[router -> {routed}]")
            else:
                # Adapter not trained yet, fall back to base
                print(f"[router -> {routed} (not installed, using base model)]")
                registry = adapter_manager.load_registry()
                model = registry["base_model"].get("ollama_name", "qwen3:4b")
        else:
            print("[router -> base model]")
            registry = adapter_manager.load_registry()
            model = registry["base_model"].get("ollama_name", "qwen3:4b")
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

    # Read eval_type from adapter config
    eval_type = config.get("eval_type", "numeric")

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
    base_correct, base_total, _ = run_eval(base_model, dataset, eval_type=eval_type)

    # Run adapter eval
    print(f"\nEvaluating adapter model ({adapter_model})...")
    adapter_correct, adapter_total, _ = run_eval(adapter_model, dataset, eval_type=eval_type)

    format_results(base_correct, base_total, adapter_correct, adapter_total, adapter_name)


def cmd_route(args):
    """Show which adapter the router would pick for a query."""
    from locollm.router import KeywordRouter

    router = KeywordRouter()
    result = router.route(args.query)
    if result:
        print(result)
    else:
        print("base model")


def _handle_adapter_command(session, arg):
    """Handle /adapter slash command variants. Returns a message string."""
    if arg is None:
        return session.adapter_list_display()
    if arg == "auto":
        session.set_adapter("auto")
        return "[auto-routing enabled]"
    if arg == "none":
        session.set_adapter("none")
        return "[using base model]"
    try:
        session.set_adapter(arg)
        return f"[adapter: {arg}]"
    except ValueError:
        return f"Unknown adapter: {arg}"


_CHAT_HELP = """\
Commands:
  /help              Show this help
  /quit or /exit     Exit chat
  /clear             Clear conversation history
  /adapter           List available adapters
  /adapter <name>    Switch to a specific adapter
  /adapter auto      Auto-route based on your query
  /adapter none      Use base model directly
  /stats             Show session statistics

Tips:
  - Keep queries focused on one task — adapters are specialists
  - The router picks an adapter from your first message, then sticks with it
  - Use /clear to start fresh and let the router pick again
  - Use /adapter to lock in a specific adapter when you know what you need"""


def cmd_chat(args):
    """Interactive multi-turn chat session."""
    from locollm import ollama_client
    from locollm.chat_session import ChatSession

    if not ollama_client.check_running():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    session = ChatSession(
        adapter=args.adapter,
        context_limit=args.context_limit,
    )

    mode_info = f"adapter: {args.adapter}" if args.adapter != "auto" else "auto-routing"
    print(f"LocoLLM chat ({mode_info})")
    print("Type /help for commands, /quit to exit.\n")

    while True:
        try:
            user_input = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input.strip():
            continue

        command, arg = ChatSession.parse_slash_command(user_input)

        if command in ("/quit", "/exit"):
            print("Bye!")
            break
        elif command == "/help":
            print(_CHAT_HELP)
            continue
        elif command == "/clear":
            session.clear()
            print("[conversation cleared]")
            continue
        elif command == "/adapter":
            print(_handle_adapter_command(session, arg))
            continue
        elif command == "/stats":
            print(session.session_stats_display())
            continue
        elif command is not None:
            print(f"Unknown command: {command}")
            continue

        session.add_user_message(user_input)

        full_response = []
        meta = None
        for chunk, chunk_meta in session.send():
            print(chunk, end="", flush=True)
            full_response.append(chunk)
            if chunk_meta is not None:
                meta = chunk_meta
        print()

        response_text = "".join(full_response)
        session.add_assistant_message(response_text)

        if meta:
            session.record_turn(meta)
            print(ChatSession.format_stats(session.active_adapter, meta))
            notice = session.maybe_compact(meta.get("prompt_eval_count", 0))
            if notice:
                print(notice)


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
    sp_query.add_argument(
        "--no-route",
        action="store_true",
        help="Bypass router and use base model directly",
    )
    sp_query.set_defaults(func=cmd_query)

    # chat
    sp_chat = subparsers.add_parser("chat", help="Interactive multi-turn chat session")
    sp_chat.add_argument("--adapter", default="auto", help="Adapter to use (default: auto)")
    sp_chat.add_argument(
        "--context-limit", type=int, default=8192, help="Context window limit (default: 8192)"
    )
    sp_chat.set_defaults(func=cmd_chat)

    # eval
    sp_eval = subparsers.add_parser("eval", help="Run evaluation benchmark")
    sp_eval.add_argument("adapter_name", help="Name of adapter to evaluate")
    sp_eval.set_defaults(func=cmd_eval)

    # route
    sp_route = subparsers.add_parser("route", help="Show which adapter the router would pick")
    sp_route.add_argument("query", help="The query to route")
    sp_route.set_defaults(func=cmd_route)

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
