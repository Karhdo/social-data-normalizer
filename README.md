# Social Data Normalizer

Converts raw social media data (Reddit, Facebook, Threads) into a unified CSV schema for downstream labeling and analysis. Built with Python and pandas.

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
└── results/
    └── {DD_MM_YYYY}.csv                  # Filtered & shuffled output for labeling
```

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
