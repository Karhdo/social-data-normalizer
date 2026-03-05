"""Normalizer for Reddit data."""

import pandas as pd

from .base import BaseNormalizer


class RedditNormalizer(BaseNormalizer):
    platform = "reddit"

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()
        out["source_id"] = df["id"].astype(str)
        out["platform"] = self.platform
        out["id"] = out["platform"] + ":" + out["source_id"]
        out["created_at"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)
        out["collected_at"] = df.get("collected_at", pd.NaT)
        out["text_clean"] = df.get("selftext", df.get("body", ""))
        out["url"] = df.get("url", df.get("permalink", ""))
        return out
