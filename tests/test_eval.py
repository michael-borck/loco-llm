"""Tests for the evaluation harness — answer extraction, checkers, and dataset loading."""

from locollm.eval import (
    check_code_syntax,
    check_contains_answer,
    check_keywords,
    extract_number,
    load_dataset,
)


class TestExtractNumber:
    """Tests for numeric answer extraction from model output."""

    def test_the_answer_is(self):
        assert extract_number("So the answer is 42") == 42

    def test_answer_is_case_insensitive(self):
        assert extract_number("The Answer Is 7") == 7

    def test_answer_colon(self):
        assert extract_number("Answer: 15") == 15

    def test_boxed_latex(self):
        assert extract_number("Therefore \\boxed{36}") == 36

    def test_equals_at_end(self):
        assert extract_number("2 + 2 = 4") == 4

    def test_equals_with_dollar(self):
        assert extract_number("x = $12$") == 12

    def test_last_number_fallback(self):
        assert extract_number("We compute 3 times 5 which gives us 15") == 15

    def test_negative_number(self):
        assert extract_number("The answer is -8") == -8

    def test_decimal(self):
        assert extract_number("The answer is 0.625") == 0.625

    def test_comma_separated(self):
        assert extract_number("The answer is 1,000") == 1000

    def test_no_number(self):
        assert extract_number("I don't know") is None

    def test_empty_string(self):
        assert extract_number("") is None

    def test_multiple_numbers_prefers_answer_is(self):
        text = "First we get 10, then 20. The answer is 30."
        assert extract_number(text) == 30


class TestCheckCodeSyntax:
    """Tests for Python syntax checking."""

    def test_valid_function(self):
        code = "def hello():\n    return 'world'"
        assert check_code_syntax(code) is True

    def test_invalid_syntax(self):
        code = "def hello(\n    return"
        assert check_code_syntax(code) is False

    def test_markdown_code_block(self):
        text = "Here's the code:\n```python\ndef add(a, b):\n    return a + b\n```"
        assert check_code_syntax(text) is True

    def test_markdown_block_invalid(self):
        text = "```python\ndef add(a, b)\n    return a + b\n```"
        assert check_code_syntax(text) is False

    def test_empty_string(self):
        # Empty string is valid Python (no statements)
        assert check_code_syntax("") is True


class TestCheckKeywords:
    """Tests for keyword presence checking."""

    def test_all_present(self):
        text = "def add(a, b):\n    return a + b"
        assert check_keywords(text, ["def ", "return"]) is True

    def test_missing_keyword(self):
        text = "x = 42"
        assert check_keywords(text, ["def ", "return"]) is False

    def test_empty_keywords(self):
        assert check_keywords("anything", []) is True

    def test_partial_match(self):
        text = "def hello():\n    pass"
        assert check_keywords(text, ["def ", "return"]) is False


class TestCheckContainsAnswer:
    """Tests for case-insensitive answer substring matching."""

    def test_exact_match(self):
        assert check_contains_answer("chlorophyll", "chlorophyll") is True

    def test_case_insensitive(self):
        assert check_contains_answer("The answer is Chlorophyll.", "chlorophyll") is True

    def test_substring_match(self):
        assert check_contains_answer(
            "The pigment chlorophyll is responsible for the green color.",
            "chlorophyll",
        ) is True

    def test_not_present(self):
        assert check_contains_answer("The answer is hemoglobin.", "chlorophyll") is False

    def test_empty_answer(self):
        assert check_contains_answer("some text", "") is True


class TestLoadDataset:
    """Tests for JSONL dataset loading."""

    def test_load_valid_jsonl(self, tmp_path):
        data = tmp_path / "test.jsonl"
        data.write_text('{"question": "2+2?", "answer": 4}\n{"question": "3+3?", "answer": 6}\n')
        problems = load_dataset(data)
        assert len(problems) == 2
        assert problems[0]["answer"] == 4
        assert problems[1]["question"] == "3+3?"

    def test_load_with_blank_lines(self, tmp_path):
        data = tmp_path / "test.jsonl"
        data.write_text('{"question": "q1", "answer": 1}\n\n{"question": "q2", "answer": 2}\n')
        problems = load_dataset(data)
        assert len(problems) == 2
