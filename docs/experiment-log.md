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

## Observed top 20

Ranking A, current snapshot share:

```text
게임, ep., 오징어, 오징어 게임, the, sub, eng, official, bts, 이유,
mv, 한국, squid game, game, vs, 친구, 스우파, nct, tv, my
```

Ranking B, smoothed change from the previous window:

```text
squid game, itzy, savage, loco, 에스, aespa, my universe, coldplay,
오징어게임, 해외 반응, aespa 에스, 더듬이 tv, 안테나, 공범, 아이돌,
이정재, the feels, 특집, 부부, 추석 맞이
```

## Provisional interpretation — 2026-08-28

- The user judged Ranking B qualitatively strong and interesting. This is an
  observation, not a final success classification.
- Ranking A and B used the same input, yet B produced a much more period-specific
  list. This suggests the temporal comparison contributes useful separation
  inside the selected input.
- The input already consists of videos selected by YouTube as trending. A live
  hypothesis is therefore that upstream platform selection supplies much of the
  signal and Ranking B primarily summarizes or reranks that curated pool.
- E001 does not establish that Ranking B can discover trends from unfiltered
  videos, general public text, or another source. It also does not measure how
  much of its apparent quality comes from YouTube's selection.
- A date-shuffle or random-window control was discussed as the smallest way to
  observe whether B depends on real temporal order. It is only a candidate next
  experiment and has not been approved or run.

## Session close

E001 is technically executed and reproducible. Its output is promising enough
to continue thinking about, but the product and algorithm verdicts remain open.
No follow-up experiment, new input, or implementation is approved at this point.
