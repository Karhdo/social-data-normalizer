#!/usr/bin/env python3
"""Generate a filtered & shuffled results CSV from normalized data.

Filters: remove nulls, remove short text (<=30 chars), keep Vietnamese only.
Output: data/results/{DD_MM_YYYY}.csv

Usage:
    python scripts/generate_results.py --date 2026-03-05
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from langdetect import detect

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def is_vietnamese(text):
    try:
        return detect(str(text)) == "vi"
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate filtered results CSV.")
    parser.add_argument(
        "--date",
        required=True,
        help="Date folder name in normalized/ (YYYY-MM-DD).",
    )
    args = parser.parse_args()

    norm_dir = Path("data/normalized") / args.date
    if not norm_dir.exists():
        print(f"Error: normalized directory not found: {norm_dir}", file=sys.stderr)
        sys.exit(1)

    files = list(norm_dir.glob("*.csv"))
    if not files:
        print(f"Error: no CSV files found in {norm_dir}", file=sys.stderr)
        sys.exit(1)

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.drop_duplicates(subset=["id"])
    total = len(df)
    print(f"Loaded {total} records from {len(files)} files")

    # Remove nulls
    df = df.dropna(subset=["text_clean"])
    print(f"After remove null: {len(df)}")

    # Remove short text
    df = df[df["text_clean"].str.len() > 30]
    print(f"After remove short (<=30 chars): {len(df)}")

    # Filter Vietnamese
    df = df[df["text_clean"].apply(is_vietnamese)]
    print(f"After filter Vietnamese: {len(df)}")

    # Log stats
    print(f"\nPlatform breakdown:")
    print(df["platform"].value_counts().to_string())
    print(f"\nText length stats:")
    print(df["text_clean"].str.len().describe().to_string())

    # Shuffle and save
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    parsed = datetime.strptime(args.date, "%Y-%m-%d")
    output_name = parsed.strftime("%d_%m_%Y") + ".csv"
    output_dir = Path("data/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} records -> {output_path}")


if __name__ == "__main__":
    main()
