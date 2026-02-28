"""Tests for the evaluation harness — answer extraction and dataset loading."""

from locollm.eval import extract_number, load_dataset


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
