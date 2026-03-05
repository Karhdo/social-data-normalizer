#!/usr/bin/env python3
"""Merge multiple raw CSV files from a source folder into a single _merged.csv.

Usage:
    python scripts/merge_raw.py --date 2026-03-05 --source apify-fb-post-scraper-data
    python scripts/merge_raw.py --date 2026-03-05 --source apify-threads-keyword-search-data
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Merge raw CSV files from a source folder.")
    parser.add_argument("--date", required=True, help="Date folder name (YYYY-MM-DD).")
    parser.add_argument("--source", required=True, help="Source folder name under raw/{date}/.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    source_dir = project_root / "data" / "raw" / args.date / args.source
    if not source_dir.exists():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    files = [f for f in source_dir.glob("*.csv") if f.name != "_merged.csv"]
    if not files:
        print(f"Error: no CSV files found in {source_dir}", file=sys.stderr)
        sys.exit(1)

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    output_path = source_dir / "_merged.csv"
    df.to_csv(output_path, index=False)
    print(f"Merged {len(files)} files ({len(df)} rows) -> {output_path}")


if __name__ == "__main__":
    main()
