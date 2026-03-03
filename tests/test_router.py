"""Tests for the keyword router."""

from locollm.router import KeywordRouter


class TestKeywordRouter:
    """Tests for keyword-based query routing."""

    def setup_method(self):
        self.router = KeywordRouter()

    def test_routes_math_query(self):
        assert self.router.route("solve 2+2") == "math"

    def test_routes_math_calculate(self):
        assert self.router.route("calculate the average of 10 and 20") == "math"

    def test_routes_code_query(self):
        assert self.router.route("write a python function to reverse a string") == "code"

    def test_routes_code_implement(self):
        assert self.router.route("implement a binary search algorithm") == "code"

    def test_routes_analysis_query(self):
        assert self.router.route("analyze this passage about climate change") == "analysis"

    def test_routes_analysis_explain(self):
        assert self.router.route("explain why the sky is blue") == "analysis"

    def test_routes_analysis_summarize(self):
        assert self.router.route("summarize the evidence in this text") == "analysis"

    def test_no_match_returns_none(self):
        assert self.router.route("hello there") is None

    def test_empty_query_returns_none(self):
        assert self.router.route("") is None

    def test_case_insensitive(self):
        assert self.router.route("SOLVE this EQUATION") == "math"

    def test_case_insensitive_code(self):
        assert self.router.route("Write a PYTHON script") == "code"

    def test_highest_score_wins(self):
        # "calculate the sum total average" hits 4 math keywords
        assert self.router.route("calculate the sum total average") == "math"

    def test_code_multiple_keywords(self):
        assert self.router.route("write a function to implement a class in python") == "code"
