"""Tests for platform normalizers."""

from pathlib import Path

import pandas as pd
import pytest

from src.registry import set_registry_path
from src.normalizers import RedditNormalizer, FacebookNormalizer, ThreadsNormalizer


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path):
    """Use a temporary registry for each test to avoid production data interference."""
    set_registry_path(tmp_path / "registry.csv")
    yield
    set_registry_path(Path("data/normalized/registry.csv"))


class TestRedditNormalizer:
    def test_basic_normalization(self):
        raw = pd.DataFrame(
            {
                "id": ["abc123"],
                "created_utc": [1700000000],
                "selftext": ["Hello world"],
                "url": ["https://reddit.com/r/test/abc123"],
            }
        )
        result = RedditNormalizer().run(raw)
        assert len(result) == 1
        assert result.iloc[0]["id"] == "reddit:abc123"
        assert result.iloc[0]["platform"] == "reddit"
        assert result.iloc[0]["text_clean"] == "Hello world"

    def test_empty_text_removed(self):
        raw = pd.DataFrame(
            {
                "id": ["a", "b"],
                "created_utc": [1700000000, 1700000001],
                "selftext": ["valid text", "   "],
                "url": ["http://a", "http://b"],
            }
        )
        result = RedditNormalizer().run(raw)
        assert len(result) == 1


class TestFacebookNormalizer:
    def test_basic_normalization(self):
        raw = pd.DataFrame(
            {
                "postId": ["fb_001"],
                "time": ["2024-01-01T00:00:00+00:00"],
                "text": ["Test post"],
                "url": ["https://facebook.com/post/fb_001"],
            }
        )
        result = FacebookNormalizer().run(raw)
        assert len(result) == 1
        assert result.iloc[0]["id"] == "facebook:fb_001"
        assert result.iloc[0]["text_clean"] == "Test post"


class TestThreadsNormalizer:
    def test_basic_normalization(self):
        raw = pd.DataFrame(
            {
                "postCode": ["th_001"],
                "createdAt": ["2024-01-01T12:00:00+00:00"],
                "text": ["Threads post"],
                "postUrl": ["https://threads.net/@user/post/th_001"],
            }
        )
        result = ThreadsNormalizer().run(raw)
        assert len(result) == 1
        assert result.iloc[0]["id"] == "threads:th_001"
        assert result.iloc[0]["text_clean"] == "Threads post"


class TestDeduplication:
    def test_duplicate_ids_removed(self):
        raw = pd.DataFrame(
            {
                "id": ["dup", "dup"],
                "created_utc": [1700000000, 1700000001],
                "selftext": ["first", "second"],
                "url": ["http://a", "http://b"],
            }
        )
        result = RedditNormalizer().run(raw)
        assert len(result) == 1
        assert result.iloc[0]["text_clean"] == "first"
