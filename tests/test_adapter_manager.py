"""Tests for the adapter manager — registry loading, modelfile building."""

import pytest

from locollm import adapter_manager


class TestRegistry:
    """Tests for loading and querying the adapter registry."""

    def test_load_registry(self):
        registry = adapter_manager.load_registry()
        assert "base_model" in registry
        assert "adapters" in registry

    def test_list_adapters(self):
        adapters = adapter_manager.list_adapters()
        assert len(adapters) >= 1
        names = [name for name, _ in adapters]
        assert "math" in names

    def test_get_adapter_exists(self):
        config = adapter_manager.get_adapter("math")
        assert config is not None
        assert config["type"] == "merged-gguf"

    def test_get_adapter_missing(self):
        assert adapter_manager.get_adapter("nonexistent") is None


class TestModelfile:
    """Tests for Modelfile generation."""

    def test_build_system_prompt_modelfile(self):
        config = {
            "type": "system-prompt",
            "ollama_base": "qwen3:4b",
            "system_prompt": "You are a math tutor.",
        }
        mf = adapter_manager._build_modelfile(config, {})
        assert mf.startswith("FROM qwen3:4b")
        assert "You are a math tutor." in mf

    def test_build_merged_gguf_modelfile(self, tmp_path):
        # Create a fake GGUF file
        gguf_file = tmp_path / "model.gguf"
        gguf_file.write_text("fake")
        config = {
            "type": "merged-gguf",
            "gguf_path": str(gguf_file),
        }
        # Patch ADAPTERS_DIR so the relative path resolves correctly
        import locollm.adapter_manager as am

        original = am.ADAPTERS_DIR
        am.ADAPTERS_DIR = tmp_path.parent  # gguf_path is relative to ADAPTERS_DIR
        try:
            # Use an absolute-style path by making gguf_path the filename
            # and ADAPTERS_DIR the parent
            config["gguf_path"] = tmp_path.name + "/model.gguf"
            mf = am._build_modelfile(config, {})
            assert mf.startswith("FROM ")
            assert "model.gguf" in mf
        finally:
            am.ADAPTERS_DIR = original

    def test_build_merged_gguf_missing_file(self):
        config = {
            "type": "merged-gguf",
            "gguf_path": "nonexistent/model.gguf",
        }
        with pytest.raises(FileNotFoundError):
            adapter_manager._build_modelfile(config, {})

    def test_build_modelfile_unsupported_type(self):
        config = {"type": "lora", "ollama_base": "qwen3:4b"}
        with pytest.raises(ValueError, match="Unsupported adapter type"):
            adapter_manager._build_modelfile(config, {})


class TestAdapterModelName:
    """Tests for adapter model naming."""

    def test_adapter_model_name(self):
        assert adapter_manager.adapter_model_name("math") == "locollm-math"

    def test_adapter_model_name_prefix(self):
        name = adapter_manager.adapter_model_name("custom")
        assert name.startswith(adapter_manager.ADAPTER_MODEL_PREFIX)


class TestEvalDatasetPath:
    """Tests for eval dataset path resolution."""

    def test_get_eval_dataset_path(self):
        path = adapter_manager.get_eval_dataset_path("math")
        assert path is not None
        assert path.name == "eval_dataset.jsonl"
        assert path.exists()

    def test_get_eval_dataset_path_missing(self):
        assert adapter_manager.get_eval_dataset_path("nonexistent") is None
