# Trend Signal Lab

Trend Signal Lab is a small research workspace for reproducible experiments
on emerging Korean keywords and cultural phenomena. It is not a production
service.

## E001 dataset boundary

E001 uses version 1346 of Kaggle's `rsrishav/youtube-trending-video-dataset`,
specifically `KR_youtube_trending_data.csv`. The loader keeps only YouTube
trending snapshots from 2021-08-18 through 2021-10-16, the five approved
category IDs (`1`, `10`, `22`, `23`, `24`), and unique `(video_id,
trending_date)` pairs. The raw ZIP stays under the ignored `data/raw/`
directory; the downloader records its SHA-256 and source details in a sidecar
manifest.

## Development

```sh
uv sync
uv run pytest -q
```

Download the fixed dataset into the ignored raw-data directory with:

```sh
uv run python scripts/download_e001_data.py
```

## E001 result artifact

Run the title-only baseline with:

```sh
uv run python scripts/run_e001.py \
  --input data/raw/kr_youtube_trending_data.zip \
  --output-dir artifacts/e001
```

The 2021-09-17–2021-10-16 current window contains 4,286 in-scope snapshots;
the preceding 30-day window contains 4,040. The run applies Kiwi noun/proper-
noun/foreign-token extraction, fixed stopwords, 1–3-grams, five-snapshot
minimum support, current-share ranking, and smoothed log2 change ranking. The
anchor (`오징어 게임`, `오징어게임`, or `squid game`) appears in both output
top-20 lists. The generated lists are noisy and the human usefulness labels
remain pending review; this is not a claim that the preregistered usefulness
threshold passed. See [the experiment log](docs/experiment-log.md) and the
ignored `artifacts/e001/results.{json,md}` files.

## E002 SBS metadata baseline

Run the source-local SBS entertainment backfill with an explicit completed-day
endpoint:

```sh
uv run python scripts/run_e002_sbs.py --end-date 2026-08-28
```

The run covers that completed day and its preceding 29 days, compared with the
immediately preceding 30 days. It retains only `title`, `published_at`,
`news_id`, and `link`, deduplicated by `news_id`; article bodies, descriptions,
and images are not fetched. Raw metadata stays under ignored `data/raw/`, and
generated results under ignored `artifacts/e002_sbs/`.

Ranking B reuses E001's candidate extraction, minimum support of five, and
0.5-smoothed log2 share ratio. SBS unique-article support is not directly
comparable with YouTube daily-snapshot support. This is an SBS editorial lens,
not a representative measure of overall cultural attention, and no scores are
combined across sources.

## Wikimedia Phase 2 daily page

Generate the local daily popular-keyword JSON for the latest retained completed
UTC day:

```sh
uv run python -m scripts.build_wikimedia_page
```

Or replay an explicit completed UTC date:

```sh
uv run python -m scripts.build_wikimedia_page --date 2026-08-29
```

The default picks the newest retained snapshot strictly before the current UTC
date; there is no automatic collection, refresh, or server. The result lives in
the ignored `artifacts/wikimedia_phase2/` directory. The page shows one UTC
day's views inside Korean Wikipedia readership, not Korean population attention,
and older experiments remain historical evidence rather than the current list.
