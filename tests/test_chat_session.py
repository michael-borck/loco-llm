"""Tests for ChatSession — all mocked, no Ollama required."""

from unittest.mock import MagicMock, patch

import pytest

from locollm.chat_session import ChatSession


# ---------------------------------------------------------------------------
# Fixtures — mock Ollama + adapter_manager so tests run without a server
# ---------------------------------------------------------------------------

FAKE_REGISTRY = {
    "base_model": {"ollama_name": "qwen3:4b"},
    "adapters": {
        "math": {"router_keywords": ["solve", "calculate", "math"]},
        "code": {"router_keywords": ["code", "python", "function"]},
        "analysis": {"router_keywords": ["analyze", "explain"]},
    },
}

FAKE_INSTALLED = ["qwen3:4b", "locollm-math:latest", "locollm-code:latest"]


def _make_session(adapter="auto", context_limit=8192):
    """Create a ChatSession with mocked external dependencies."""
    with (
        patch("locollm.chat_session.adapter_manager.load_registry", return_value=FAKE_REGISTRY),
        patch("locollm.chat_session.ollama_client.list_models", return_value=FAKE_INSTALLED),
    ):
        return ChatSession(adapter=adapter, context_limit=context_limit)


# ===========================================================================
# Slash command parsing (static, no mocks needed)
# ===========================================================================


class TestSlashCommandParsing:
    def test_help(self):
        assert ChatSession.parse_slash_command("/help") == ("/help", None)

    def test_quit(self):
        assert ChatSession.parse_slash_command("/quit") == ("/quit", None)

    def test_exit(self):
        assert ChatSession.parse_slash_command("/exit") == ("/exit", None)

    def test_clear(self):
        assert ChatSession.parse_slash_command("/clear") == ("/clear", None)

    def test_adapter_no_arg(self):
        assert ChatSession.parse_slash_command("/adapter") == ("/adapter", None)

    def test_adapter_with_arg(self):
        assert ChatSession.parse_slash_command("/adapter math") == ("/adapter", "math")

    def test_adapter_auto(self):
        assert ChatSession.parse_slash_command("/adapter auto") == ("/adapter", "auto")

    def test_adapter_none(self):
        assert ChatSession.parse_slash_command("/adapter none") == ("/adapter", "none")

    def test_non_command(self):
        assert ChatSession.parse_slash_command("hello world") == (None, None)

    def test_empty(self):
        assert ChatSession.parse_slash_command("") == (None, None)

    def test_whitespace(self):
        assert ChatSession.parse_slash_command("   ") == (None, None)

    def test_case_insensitive(self):
        assert ChatSession.parse_slash_command("/HELP") == ("/help", None)

    def test_case_insensitive_adapter(self):
        assert ChatSession.parse_slash_command("/ADAPTER math") == ("/adapter", "math")


# ===========================================================================
# Stats formatting (static)
# ===========================================================================


class TestStatsFormatting:
    def test_basic_format(self):
        meta = {
            "eval_count": 147,
            "eval_duration": 6_277_000_000,  # ~6.3s
            "total_duration": 6_300_000_000,
        }
        result = ChatSession.format_stats("math", meta)
        assert result.startswith("[math")
        assert "147 tokens" in result
        assert "tok/s" in result

    def test_base_model_label(self):
        meta = {"eval_count": 50, "eval_duration": 1_000_000_000, "total_duration": 1_000_000_000}
        result = ChatSession.format_stats(None, meta)
        assert result.startswith("[base")

    def test_zero_duration(self):
        meta = {"eval_count": 0, "eval_duration": 0, "total_duration": 0}
        result = ChatSession.format_stats("code", meta)
        assert "0 tokens" in result
        assert "0.0 tok/s" in result


# ===========================================================================
# Conversation history
# ===========================================================================


class TestConversationHistory:
    def test_add_messages(self):
        session = _make_session()
        session.add_user_message("hello")
        session.add_assistant_message("hi there")
        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"

    def test_clear_resets(self):
        session = _make_session()
        session.add_user_message("hello")
        session.add_assistant_message("hi")
        session.clear()
        assert len(session.messages) == 0

    def test_message_ordering(self):
        session = _make_session()
        session.add_user_message("first")
        session.add_user_message("second")
        session.add_assistant_message("reply")
        assert session.messages[0]["content"] == "first"
        assert session.messages[1]["content"] == "second"
        assert session.messages[2]["content"] == "reply"


# ===========================================================================
# Context compaction
# ===========================================================================


class TestContextCompaction:
    def test_no_compaction_below_threshold(self):
        session = _make_session(context_limit=1000)
        for i in range(10):
            session._messages.append({"role": "user", "content": f"msg {i}"})
        result = session.maybe_compact(800)  # 80% < 90%
        assert result is None
        assert len(session.messages) == 10

    def test_compaction_above_threshold(self):
        session = _make_session(context_limit=1000)
        for i in range(10):
            session._messages.append({"role": "user", "content": f"msg {i}"})
        result = session.maybe_compact(950)  # 95% > 90%
        assert result is not None
        assert "dropped 6" in result
        assert len(session.messages) == 4

    def test_minimum_4_messages_preserved(self):
        session = _make_session(context_limit=100)
        for i in range(4):
            session._messages.append({"role": "user", "content": f"msg {i}"})
        result = session.maybe_compact(95)
        assert result is None  # already at minimum, can't compact further
        assert len(session.messages) == 4


# ===========================================================================
# Adapter switching
# ===========================================================================


class TestAdapterSwitching:
    def test_set_adapter_locks_mode(self):
        session = _make_session()
        session.set_adapter("math")
        assert session.mode == "locked"
        assert session.active_adapter == "math"

    def test_auto_resets(self):
        session = _make_session()
        session.set_adapter("math")
        session.set_adapter("auto")
        assert session.mode == "auto"
        assert session.active_adapter is None

    def test_none_locks_to_base(self):
        session = _make_session()
        session.set_adapter("none")
        assert session.mode == "locked"
        assert session.active_adapter is None
        assert session.model == "qwen3:4b"

    def test_invalid_raises_valueerror(self):
        session = _make_session()
        with pytest.raises(ValueError, match="Unknown adapter"):
            session.set_adapter("nonexistent")


# ===========================================================================
# Auto-routing
# ===========================================================================


class TestAutoRouting:
    def test_routes_on_first_message(self):
        session = _make_session()
        session.add_user_message("solve 2+2")
        assert session.active_adapter == "math"

    def test_sticks_after_first_route(self):
        session = _make_session()
        session.add_user_message("solve 2+2")
        assert session.active_adapter == "math"
        # Second message should not re-route
        session.add_user_message("write python code")
        assert session.active_adapter == "math"

    def test_clear_resets_for_rerouting(self):
        session = _make_session()
        session.add_user_message("solve 2+2")
        assert session.active_adapter == "math"
        session.clear()
        assert session.active_adapter is None
        session.add_user_message("write a python function")
        assert session.active_adapter == "code"

    def test_no_match_stays_base(self):
        session = _make_session()
        session.add_user_message("hello there")
        assert session.active_adapter is None
        assert session.model == "qwen3:4b"

    def test_locked_mode_skips_routing(self):
        session = _make_session(adapter="math")
        assert session.active_adapter == "math"
        session.add_user_message("write python code")
        # Should stay on math, not route to code
        assert session.active_adapter == "math"
