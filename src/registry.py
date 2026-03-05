"""Registry for tracking normalized record IDs across batches."""

from pathlib import Path

import pandas as pd

_registry_path = Path("data/normalized/registry.csv")


def set_registry_path(path: Path) -> None:
    """Override the registry path (useful for testing)."""
    global _registry_path
    _registry_path = path


def load_registry() -> set[str]:
    """Load all known IDs from the registry file."""
    if not _registry_path.exists():
        return set()
    df = pd.read_csv(_registry_path)
    return set(df["id"])


def save_registry(ids: set[str]) -> None:
    """Save IDs to the registry file."""
    _registry_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(sorted(ids), columns=["id"])
    df.to_csv(_registry_path, index=False)


def dedup_against_registry(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows whose IDs already exist in the registry."""
    known_ids = load_registry()
    if not known_ids:
        return df
    mask = ~df["id"].isin(known_ids)
    return df[mask].reset_index(drop=True)


def update_registry(new_ids: set[str]) -> None:
    """Add new IDs to the registry."""
    known_ids = load_registry()
    known_ids.update(new_ids)
    save_registry(known_ids)
