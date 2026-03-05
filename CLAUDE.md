# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Social data normalizer: converts raw social media data (Reddit, Facebook, Threads) into a unified CSV schema. Built with Python and pandas.

## Common Commands

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run all tests
python3 -m pytest tests/ -v

# Run a single test file
python3 -m pytest tests/test_normalizers.py -v

# Run a single test class or method
python3 -m pytest tests/test_normalizers.py::TestRedditNormalizer::test_basic_normalization -v
```

## Data Processing Pipeline

### Step 1: Merge raw CSV files from a source folder
```bash
python3 scripts/merge_raw.py --date 2026-03-05 --source apify-fb-post-scraper-data
python3 scripts/merge_raw.py --date 2026-03-05 --source apify-threads-keyword-search-data
```

### Step 2: Normalize merged data into unified schema
```bash
python3 scripts/normalize.py --platform facebook --input data/raw/2026-03-05/apify-fb-post-scraper-data/_merged.csv --output data/normalized/2026-03-05/facebook.csv
python3 scripts/normalize.py --platform threads --input data/raw/2026-03-05/apify-threads-keyword-search-data/_merged.csv --output data/normalized/2026-03-05/threads.csv
```
Note: praw-reddit-post-data is already in unified schema, copy directly to `data/normalized/{date}/reddit.csv`.

### Step 3: Generate filtered results for labeling
```bash
python3 scripts/generate_results.py --date 2026-03-05
```
Filters: remove nulls, remove short text (<=30 chars), keep Vietnamese only. Output: `data/results/DD_MM_YYYY.csv`.

## Architecture

**Unified schema** (`src/schema.py`): All normalized data outputs these columns:
`id, platform, source_id, created_at, collected_at, text_clean, url`

**Normalizer pattern** (`src/normalizers/`): Each platform has a normalizer class extending `BaseNormalizer`. The base class provides `run()` which calls the platform's `normalize()` method then applies cleaning/deduplication. The `id` field is `<platform>:<source_id>`.

**Registry** (`src/normalizers/__init__.py`): `NORMALIZERS` dict maps platform name strings to normalizer classes. The CLI script and any future code should use this registry to look up normalizers.

**Adding a new platform**: Create a new normalizer in `src/normalizers/`, extend `BaseNormalizer`, implement `normalize()` to map raw columns to the unified schema, and register it in `NORMALIZERS`.

**Cleaning pipeline** (`src/utils/cleaning.py`): `clean_dataframe()` normalizes whitespace, removes rows with empty `text_clean`, and deduplicates by `id`. Applied automatically by `BaseNormalizer.run()`.

**Dedup registry** (`src/registry.py`): `data/normalized/registry.csv` tracks all processed record IDs. `BaseNormalizer.run()` automatically deduplicates against the registry and updates it with new IDs, preventing duplicates across batches/dates.

**Data folder structure**:
```
data/
├── raw/{YYYY-MM-DD}/{source-name}/       # Raw data organized by date and source
│   ├── apify-fb-post-scraper-data/
│   ├── apify-threads-keyword-search-data/
│   └── praw-reddit-post-data/
├── normalized/
│   ├── registry.csv                      # Global dedup registry
│   └── {YYYY-MM-DD}/                     # Normalized output by date
│       ├── facebook.csv
│       ├── reddit.csv
│       └── threads.csv
└── results/
    └── {DD_MM_YYYY}.csv                  # Filtered & shuffled output for labeling
```

**Raw column expectations per source**:
- praw-reddit-post-data: already in unified schema (pre-normalized)
- apify-fb-post-scraper-data: `postId`, `time` (ISO 8601), `text`, `url`, `pageName`
- apify-threads-keyword-search-data: `postCode`, `createdAt` (ISO 8601), `text`, `postUrl`, `username`
