#!/usr/bin/env python3
"""CLI script to normalize raw social media data into a unified CSV format.

Usage:
    python scripts/normalize.py --platform facebook --input data/raw/2026-03-05/apify-fb-post-scraper-data/_merged.csv --output data/normalized/2026-03-05/facebook.csv
    python scripts/normalize.py --platform threads --input data/raw/2026-03-05/apify-threads-keyword-search-data/_merged.csv --output data/normalized/2026-03-05/threads.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.normalizers import NORMALIZERS


def main():
    parser = argparse.ArgumentParser(description="Normalize social media data.")
    parser.add_argument(
        "--platform",
        required=True,
        choices=list(NORMALIZERS.keys()),
        help="Source platform name.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw input CSV file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path for normalized output CSV. Defaults to data/normalized/<platform>.csv.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = (
        Path(args.output)
        if args.output
        else Path("data/normalized") / f"{args.platform}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    normalizer = NORMALIZERS[args.platform]()
    result = normalizer.run(df)
    result.to_csv(output_path, index=False)
    print(f"Normalized {len(result)} records -> {output_path}")


if __name__ == "__main__":
    main()
