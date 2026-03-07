# Social Mental Health Classifier

Converts raw social media data (Reddit, Facebook, Threads) into a unified CSV schema, pre-labels using OpenAI API, and trains classification models. Built with Python, pandas, and scikit-learn.

## Unified Schema

All normalized output follows this schema:

| Column | Description |
|---|---|
| `id` | Unique ID: `<platform>:<source_id>` |
| `platform` | Source platform (reddit, facebook, threads) |
| `source_id` | Original post ID from the platform |
| `created_at` | Post creation timestamp (UTC) |
| `collected_at` | Data collection timestamp |
| `text_clean` | Cleaned post text |
| `url` | Original post URL |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data Processing Pipeline

### Step 1: Merge raw CSV files

Place raw CSV files in `data/raw/{YYYY-MM-DD}/{source-name}/`, then merge:

```bash
python3 scripts/merge_raw.py --date 2026-03-05 --source apify-fb-post-scraper-data
python3 scripts/merge_raw.py --date 2026-03-05 --source apify-threads-keyword-search-data
```

### Step 2: Normalize into unified schema

```bash
python3 scripts/normalize.py --platform facebook --input data/raw/2026-03-05/apify-fb-post-scraper-data/_merged.csv --output data/normalized/2026-03-05/facebook.csv
python3 scripts/normalize.py --platform threads --input data/raw/2026-03-05/apify-threads-keyword-search-data/_merged.csv --output data/normalized/2026-03-05/threads.csv
```

> Note: `praw-reddit-post-data` is already in unified schema — copy directly to `data/normalized/{date}/reddit.csv`.

### Step 3: Generate filtered results for labeling

```bash
python3 scripts/generate_results.py --date 2026-03-05
```

Applies filters: remove nulls, remove short text (<=30 chars), keep Vietnamese only.
Output: `data/results/{DD_MM_YYYY}.csv`

### Step 4: Pre-label using OpenAI API

```bash
# Requires OPENAI_API_KEY in .env file (see .env.example)

# Using gpt-4o-mini
python3 scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt4omini.csv

# Using gpt-5-mini
python3 scripts/prelabel.py --input data/results/05_03_2026.csv --output data/prelabeled/05_03_2026_gpt5mini.csv --model gpt-5-mini
```

Supports resume — if interrupted, re-run the same command to continue. Auto-saves every 100 tasks.

**Label classes**: `stress`, `depression`, `political`, `neutral`

## Data Folder Structure

```
data/
├── raw/{YYYY-MM-DD}/{source-name}/       # Raw data by date and source
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
└── prelabeled/                            # Pre-labeled output
    ├── {DD_MM_YYYY}_gpt4omini.csv         # Pre-labeled with gpt-4o-mini
    ├── {DD_MM_YYYY}_gpt5mini.csv          # Pre-labeled with gpt-5-mini
    └── {DD_MM_YYYY}_gpt5nano.csv          # Pre-labeled with gpt-5-nano
```

## Notebooks

| Notebook | Description |
|---|---|
| `01_eda.ipynb` | Exploratory data analysis — label distribution, platform distribution, text length |
| `02_training_baseline.ipynb` | Baseline models — TF-IDF + Logistic Regression / SVM / Random Forest |

## Supported Data Sources

| Source | Platform | Raw Columns |
|---|---|---|
| praw-reddit-post-data | reddit | Already in unified schema |
| apify-fb-post-scraper-data | facebook | `postId`, `time`, `text`, `url`, `pageName` |
| apify-threads-keyword-search-data | threads | `postCode`, `createdAt`, `text`, `postUrl`, `username` |

## Adding a New Platform

1. Create a normalizer in `src/normalizers/` extending `BaseNormalizer`
2. Implement `normalize()` to map raw columns to the unified schema
3. Register it in `src/normalizers/__init__.py` → `NORMALIZERS` dict

## Tests

```bash
python3 -m pytest tests/ -v
```
