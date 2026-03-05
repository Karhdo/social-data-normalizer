"""Tests for cleaning utilities."""

import pandas as pd

from src.utils.cleaning import normalize_whitespace, clean_dataframe


class TestNormalizeWhitespace:
    def test_collapses_spaces(self):
        assert normalize_whitespace("hello   world") == "hello world"

    def test_strips_edges(self):
        assert normalize_whitespace("  hello  ") == "hello"

    def test_handles_newlines_and_tabs(self):
        assert normalize_whitespace("hello\n\tworld") == "hello world"

    def test_handles_non_string(self):
        assert normalize_whitespace(None) == ""
        assert normalize_whitespace(123) == ""


class TestCleanDataframe:
    def test_removes_empty_and_deduplicates(self):
        df = pd.DataFrame(
            {
                "id": ["a", "b", "a"],
                "platform": ["x", "x", "x"],
                "source_id": ["1", "2", "1"],
                "created_at": [None, None, None],
                "collected_at": [None, None, None],
                "text_clean": ["good", "", "duplicate"],
                "url": ["", "", ""],
            }
        )
        result = clean_dataframe(df)
        assert len(result) == 1
        assert result.iloc[0]["text_clean"] == "good"
