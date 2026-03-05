"""Base normalizer class that all platform normalizers extend."""

from abc import ABC, abstractmethod

import pandas as pd

from src.registry import dedup_against_registry, update_registry
from src.schema import UNIFIED_COLUMNS
from src.utils.cleaning import clean_dataframe


class BaseNormalizer(ABC):
    """Abstract base class for platform-specific normalizers."""

    platform: str = ""

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform platform-specific data into the unified schema.

        Must return a DataFrame with columns matching UNIFIED_COLUMNS.
        """

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize, clean, and dedup against the registry."""
        normalized = self.normalize(df)
        normalized = normalized[UNIFIED_COLUMNS]
        cleaned = clean_dataframe(normalized)
        deduped = dedup_against_registry(cleaned)
        update_registry(set(deduped["id"]))
        return deduped
