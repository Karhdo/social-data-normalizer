"""Normalizer for Facebook data."""

import pandas as pd

from .base import BaseNormalizer


class FacebookNormalizer(BaseNormalizer):
    platform = "facebook"

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()
        out["source_id"] = df["postId"].astype(str)
        out["platform"] = self.platform
        out["id"] = out["platform"] + ":" + out["source_id"]
        out["created_at"] = pd.to_datetime(df["time"], utc=True)
        out["collected_at"] = df.get("collected_at", pd.NaT)
        out["text_clean"] = df.get("text", "")
        out["url"] = df.get("url", "")
        return out
