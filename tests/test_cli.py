"""Tests for the CLI — argument parsing and help output."""

import subprocess
import sys


def run_loco(*args):
    """Run loco CLI and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "locollm.cli", *args],
        capture_output=True,
        text=True,
    )


class TestCLI:
    """Tests for CLI subcommands and argument parsing."""

    def test_version(self):
        result = run_loco("--version")
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_help(self):
        result = run_loco("--help")
        assert result.returncode == 0
        assert "setup" in result.stdout
        assert "query" in result.stdout
        assert "eval" in result.stdout
        assert "adapters" in result.stdout

    def test_no_args_shows_help(self):
        result = run_loco()
        assert result.returncode == 1
        assert "usage" in result.stderr.lower() or "usage" in result.stdout.lower()

    def test_adapters_list(self):
        result = run_loco("adapters", "list")
        assert result.returncode == 0
        assert "math" in result.stdout
        assert "merged-gguf" in result.stdout
