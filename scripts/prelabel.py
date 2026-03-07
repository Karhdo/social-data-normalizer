#!/usr/bin/env python3
"""Pre-label tasks using OpenAI API for text classification.

Reads a results CSV, classifies each text using OpenAI models, and outputs
a new CSV with a `label` column.

Supports resume: if interrupted, re-run the same command to continue from
where it left off (already-labeled rows are skipped). Auto-saves every 100 tasks.

Labels: stress, depression, political, neutral

Usage:
    # Using gpt-4o-mini (default)
    python scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026.csv

    # Using gpt-5-mini (better accuracy)
    python scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt5mini.csv --model gpt-5-mini

    # Using gpt-5-nano (cheapest, good for classification)
    python scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt5nano.csv --model gpt-5-nano
"""

import argparse
import os
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

SYSTEM_PROMPT = """You are a text classifier for Vietnamese social media posts.

Classify each post into exactly ONE of these labels:

- stress: The author expresses stress, pressure, overload, burnout, worry, anxiety, fear, uncertainty, nervousness, or feeling overwhelmed.
- depression: The author expresses sadness, hopelessness, emotional exhaustion, loss of motivation, loneliness, or feeling that life has no meaning.
- political: The post discusses politics, government, social controversies, sensitive social issues, propaganda, or political conflict.
- neutral: The post does not fit any of the above categories (general discussion, opinions, jokes, entertainment, daily life, etc).

Respond with ONLY the label (one word, lowercase). No explanation."""

VALID_LABELS = {"stress", "depression", "political", "neutral"}


def classify(client, text, model, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0,
                max_tokens=10,
            )
            label = response.choices[0].message.content.strip().lower()
            if label not in VALID_LABELS:
                label = "neutral"
            return label
        except RateLimitError:
            wait = 2 ** attempt
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)


def main():
    parser = argparse.ArgumentParser(description="Pre-label tasks using OpenAI API.")
    parser.add_argument("--input", required=True, help="Path to results CSV file.")
    parser.add_argument("--output", required=True, help="Path for output pre-labeled CSV file.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (default: gpt-4o-mini).")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume support: load output file if it exists
    if output_path.exists():
        df = pd.read_csv(output_path)
        already_done = df["label"].notna().sum()
        print(f"Resuming: loaded {len(df)} rows from {output_path} ({already_done} already labeled)")
    else:
        df = pd.read_csv(input_path)
        if "label" not in df.columns:
            df["label"] = None
        already_done = 0
        print(f"Loaded {len(df)} rows from {input_path}")

    remaining = len(df) - already_done
    print(f"Using model: {args.model}")
    print(f"Remaining: {remaining} tasks\n")

    if remaining == 0:
        print("All tasks already labeled!")
        return

    client = OpenAI(api_key=api_key)
    labeled_count = 0

    for idx, row in df.iterrows():
        if pd.notna(row["label"]) and row["label"] != "":
            continue

        text = row["text_clean"]
        label = classify(client, text, args.model)

        df.at[idx, "label"] = label
        labeled_count += 1
        print(f"[{already_done + labeled_count}/{len(df)}] {label:<12} {str(text)[:80]}...")

        # Save progress every 100 tasks
        if labeled_count % 100 == 0:
            df.to_csv(output_path, index=False)
            print(f"  -> Progress saved ({already_done + labeled_count}/{len(df)})")

        # Rate limiting
        if labeled_count % 50 == 0:
            time.sleep(1)

    df.to_csv(output_path, index=False)

    # Print summary
    counts = Counter(df["label"])
    print(f"\nDone! Saved {len(df)} pre-labeled rows -> {output_path}")
    print("Distribution:")
    for label, count in counts.most_common():
        print(f"  {label}: {count} ({count / len(df) * 100:.1f}%)")


if __name__ == "__main__":
    main()
