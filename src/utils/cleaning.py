"""Text cleaning and deduplication utilities."""

import re

import pandas as pd


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space and strip."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text).strip()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning steps: normalize whitespace, remove empty texts, deduplicate."""
    df = df.copy()
    df["text_clean"] = df["text_clean"].apply(normalize_whitespace)
    df = df[df["text_clean"].str.len() > 0]
    df = df.drop_duplicates(subset=["id"], keep="first")
    df = df.reset_index(drop=True)
    return df
