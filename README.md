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
