"""Chat session state management for loco chat.

Handles conversation history, adapter routing, context compaction,
and stats formatting. Does no IO (never calls print/input).
"""

import random

from locollm import adapter_manager, ollama_client
from locollm.router import KeywordRouter

NUDGE_PHRASES = [
    "Does that make sense? If something seems off, ask me to explain differently.",
    "What part of that would you like to explore further?",
    "Does that match what you expected? If not, tell me what seems wrong.",
    "Want to dig deeper into any part of that?",
    "Anything there you'd push back on?",
]


class ChatSession:
    """Manages multi-turn chat state, routing, and compaction."""

    def __init__(self, adapter="auto", context_limit=8192, nudge=True):
        self._messages: list[dict] = []
        self._context_limit = context_limit
        self._total_tokens = 0
        self._total_duration_ns = 0
        self._turn_count = 0
        self._nudge_enabled = nudge
        self._nudge_index = random.randrange(len(NUDGE_PHRASES))

        # Load adapter info
        registry = adapter_manager.load_registry()
        self._base_model = registry["base_model"]["ollama_name"]
        self._adapter_names = list((registry.get("adapters") or {}).keys())
        self._installed = {m.split(":")[0] for m in ollama_client.list_models()}

        # Set initial mode
        if adapter == "auto":
            self._mode = "auto"
            self._active_adapter = None
        elif adapter == "none":
            self._mode = "locked"
            self._active_adapter = None
        else:
            if adapter not in self._adapter_names:
                raise ValueError(f"Unknown adapter: {adapter}")
            self._mode = "locked"
            self._active_adapter = adapter

    @property
    def mode(self):
        return self._mode

    @property
    def active_adapter(self):
        return self._active_adapter

    @property
    def messages(self):
        return list(self._messages)

    @property
    def model(self):
        """Return the Ollama model name to use for the next request."""
        if self._active_adapter:
            return adapter_manager.adapter_model_name(self._active_adapter)
        return self._base_model

    def set_adapter(self, name):
        """Switch adapter mode.

        "auto" → auto-routing, "none" → base model, anything else → locked.
        """
        if name == "auto":
            self._mode = "auto"
            self._active_adapter = None
        elif name == "none":
            self._mode = "locked"
            self._active_adapter = None
        else:
            if name not in self._adapter_names:
                raise ValueError(f"Unknown adapter: {name}")
            self._mode = "locked"
            self._active_adapter = name

    def add_user_message(self, text):
        """Append a user message. Triggers auto-routing if needed."""
        self._messages.append({"role": "user", "content": text})
        if self._mode == "auto" and self._active_adapter is None:
            self._auto_route(text)

    def add_assistant_message(self, text):
        """Append an assistant message."""
        self._messages.append({"role": "assistant", "content": text})

    def send(self):
        """Return a generator of (text, meta) from ollama_client.chat()."""
        return ollama_client.chat(self.model, self._messages)

    def clear(self):
        """Reset conversation history. In auto mode, also reset adapter."""
        self._messages.clear()
        if self._mode == "auto":
            self._active_adapter = None

    def record_turn(self, meta):
        """Record stats from a completed turn."""
        if meta:
            self._total_tokens += meta.get("eval_count", 0)
            self._total_duration_ns += meta.get("total_duration", 0)
            self._turn_count += 1

    def maybe_compact(self, prompt_eval_count):
        """If tokens exceed 90% of context limit, drop oldest messages.

        Keeps at least the last 4 messages. Returns a notice string or None.
        """
        if prompt_eval_count < self._context_limit * 0.9:
            return None
        if len(self._messages) <= 4:
            return None
        dropped = len(self._messages) - 4
        self._messages = self._messages[-4:]
        return f"[compacted: dropped {dropped} oldest messages to fit context window]"

    def adapter_list_display(self):
        """Return a formatted string listing adapters with active one marked."""
        lines = []
        for name in self._adapter_names:
            marker = " *" if name == self._active_adapter else ""
            lines.append(f"  {name}{marker}")
        if self._mode == "auto" and self._active_adapter is None:
            lines.append("  (auto-routing, no adapter selected yet)")
        elif self._active_adapter is None:
            lines.append("  (using base model)")
        return "\n".join(lines)

    def session_stats_display(self):
        """Return a formatted string with session statistics."""
        duration_s = self._total_duration_ns / 1e9 if self._total_duration_ns else 0
        avg_tps = self._total_tokens / (duration_s) if duration_s > 0 else 0
        return (
            f"Session: {self._turn_count} turns | "
            f"{self._total_tokens} tokens | "
            f"{avg_tps:.1f} avg tok/s | "
            f"{duration_s:.1f}s total"
        )

    @staticmethod
    def format_stats(adapter_name, meta):
        """Format a stats line for a single turn.

        Returns e.g. '[math | 147 tokens | 23.4 tok/s | 6.3s]'
        """
        label = adapter_name if adapter_name else "base"
        eval_count = meta.get("eval_count", 0)
        eval_duration = meta.get("eval_duration", 0)
        total_duration = meta.get("total_duration", 0)

        if eval_duration > 0:
            tok_s = eval_count / (eval_duration / 1e9)
        else:
            tok_s = 0.0

        total_s = total_duration / 1e9 if total_duration else 0.0
        return f"[{label} | {eval_count} tokens | {tok_s:.1f} tok/s | {total_s:.1f}s]"

    @staticmethod
    def parse_slash_command(text):
        """Parse a slash command. Returns (command, arg) or (None, None)."""
        stripped = text.strip()
        if not stripped.startswith("/"):
            return (None, None)
        parts = stripped.split(None, 1)
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else None
        return (command, arg)

    @property
    def nudge_enabled(self):
        return self._nudge_enabled

    def toggle_nudge(self):
        self._nudge_enabled = not self._nudge_enabled
        return self._nudge_enabled

    def next_nudge(self):
        """Return the next nudge phrase, cycling through the pool."""
        phrase = NUDGE_PHRASES[self._nudge_index % len(NUDGE_PHRASES)]
        self._nudge_index += 1
        return phrase

    def _auto_route(self, text):
        """Route a message using KeywordRouter. Only called in auto mode."""
        router = KeywordRouter()
        result = router.route(text)
        if result:
            model_name = adapter_manager.adapter_model_name(result)
            if model_name in self._installed:
                self._active_adapter = result
