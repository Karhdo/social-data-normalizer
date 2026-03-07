# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Social data normalizer: converts raw social media data (Reddit, Facebook, Threads) into a unified CSV schema, pre-labels using OpenAI API, and trains classification models. Built with Python, pandas, and scikit-learn.

## Common Commands

```bash
# Create virtual environment and install dependencies (requires Python 3.13)
python3.13 -m venv .venv
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

### Step 4: Pre-label using OpenAI API
```bash
# Requires OPENAI_API_KEY in .env file (see .env.example)

# Using gpt-4o-mini
python3 scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt4omini.csv

# Using gpt-5-mini (better accuracy)
python3 scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt5mini.csv --model gpt-5-mini

# Using gpt-5-nano (cheapest, good for classification)
python3 scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt5nano.csv --model gpt-5-nano
```
Supports resume — if interrupted, re-run the same command to continue. Auto-saves progress every 100 tasks.

**Label classes**:
- `stress` — stress, pressure, overload, burnout, worry, anxiety, fear, nervousness, feeling overwhelmed
- `depression` — sadness, hopelessness, emotional exhaustion, loss of motivation, loneliness
- `political` — politics, government, social controversies, sensitive social issues, propaganda
- `neutral` — general discussion, opinions, jokes, entertainment, daily life, etc

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
├── results/
│   └── {DD_MM_YYYY}.csv                  # Filtered & shuffled output for labeling
└── prelabeled/                            # Pre-labeled output (gitignored)
    ├── {DD_MM_YYYY}_gpt4omini.csv              # Pre-labeled with gpt-4o-mini
    ├── {DD_MM_YYYY}_gpt5mini.csv              # Pre-labeled with gpt-5-mini
    └── {DD_MM_YYYY}_gpt5nano.csv              # Pre-labeled with gpt-5-nano
```

**Notebooks** (`notebooks/`):
- `01_eda.ipynb` — Exploratory data analysis & visualization (label distribution, platform distribution, text length)
- `02_training_baseline.ipynb` — Baseline models (TF-IDF + Logistic Regression / SVM / Random Forest)

**Raw column expectations per source**:
- praw-reddit-post-data: already in unified schema (pre-normalized)
- apify-fb-post-scraper-data: `postId`, `time` (ISO 8601), `text`, `url`, `pageName`
- apify-threads-keyword-search-data: `postCode`, `createdAt` (ISO 8601), `text`, `postUrl`, `username`
