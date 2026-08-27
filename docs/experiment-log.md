# E001 experiment log

## Execution

- Input: Kaggle `rsrishav/youtube-trending-video-dataset`, API version `1346`,
  member `KR_youtube_trending_data.csv`, recorded in the ignored sidecar
  manifest.
- Archive SHA-256: `cba7ebd0597da96c5dcd933be9469e58a74e148bb4fbb87e535442d8b51f4aa0`.
- Current window: 2021-09-17 through 2021-10-16; previous window: 2021-08-18
  through 2021-09-16; categories: 1, 10, 22, 23, 24.
- Loaded 8,326 snapshots: 4,286 current and 4,040 previous, representing
  1,078 unique videos after exact `(video_id, trending_date)` deduplication.
- Extracted 3,510 candidates. Two clean runs produced identical JSON
  (`1171fa0e...f92`) and Markdown (`3e510123...4c6`) SHA-256 hashes.
- Candidate extraction used NFKC normalization, Kiwi tags `NNB`, `NNG`,
  `NNP`, `SH`, `SL`, fixed stopwords, consecutive 1–3-grams, per-snapshot
  uniqueness, and equal-support longer-phrase preference. Ranking B used the
  preregistered 0.5-smoothed log2 share ratio and current support of at least
  five snapshots.
- Output: ignored `artifacts/e001/results.json` and `artifacts/e001/results.md`.

## Anchor and review status

The preregistered anchor variants (`오징어 게임`, `오징어게임`, `squid game`)
are present in the generated top-20 output. The top-20 lists contain noisy
generic and format terms, especially in current-share ranking. The three-way
human usefulness labels (`specific cultural signal`, `generic/artifact`,
`unclear`) have not been assigned, so the usefulness threshold is intentionally
not declared passed or failed here.
