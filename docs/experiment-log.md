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

# E002 SBS entertainment metadata log

## Execution — 2026-08-29

- Source: official SBS News entertainment archive, `sectionType=14`.
- Previous window: 2026-06-30 through 2026-07-29; current window: 2026-07-30
  through 2026-08-28. The current calendar day was excluded.
- Traversed 117 archive pages across 60 requested dates. Nine dates had no
  exact-date article after filtering.
- Collected 844 unique articles by native `news_id`: 450 previous and 394
  current. Only `title`, `published_at`, `news_id`, and `link` were retained;
  article pages, bodies, descriptions, and images were not fetched.
- Extracted 3,077 preferred candidates. Ranking B reused E001's normalization,
  Kiwi token selection, fixed stopwords, consecutive 1–3-grams, longer-phrase
  preference, five-current-item minimum, and 0.5-smoothed log2 share ratio.
- Raw metadata and generated outputs remain ignored at
  `data/raw/sbs_section14_2026-08-28.json` and
  `artifacts/e002_sbs/results.{json,md}`.

## Observed Ranking B top 20

```text
타짜, 뮤지컬, 기안, 김선호, 스파이더맨4, 제작, 블랙 핑크, 데이트,
사생활, 정예지, 차태현, 후손, 유재석, 오디세이, 기이안 연애, 해명,
수상, 연애, 빅뱅, 런닝
```

## Provisional interpretation

- Coherent work, person, and event clusters are visible: `타짜` accompanies
  coverage of the new film, `오디세이` and `스파이더맨4` reflect theatrical
  coverage, and `기이안 연애`, `블랙핑크`, and `빅뱅` have multiple related
  article titles. This is qualitative evidence that the fixed Ranking B process
  can produce interpretable output inside a second source lens.
- The list also contains broad or editorial vocabulary (`뮤지컬`, `제작`,
  `데이트`, `사생활`, `해명`, `수상`) and the truncated candidate `런닝`.
  Candidate quality and tokenization remain unresolved rather than passed.
- An SBS support count is the number of distinct articles. E001 support counted
  repeated daily YouTube trending snapshots. Multiple SBS articles about one
  work may represent coverage intensity, but are not independent audience
  observations. The score magnitudes are therefore not directly comparable.
- SBS and E001 use different calendar periods, so this run tests qualitative
  transfer of the process, not cross-source agreement, overlap, or lead/lag.
- SBS editorial selection and YouTube Trending selection are both source lenses,
  not defects to remove. This run does not estimate culture-wide prevalence and
  does not justify raw-data or score fusion.

## Current status

The historical backfill and source-local Ranking B execution succeeded
technically. Human usefulness labels and a success threshold were not fixed in
advance, so E002 is not declared a product or algorithm success. The most useful
new observation is narrower: B produced several recognizable signals on unique
SBS article titles while exposing different noise and support semantics from
the YouTube snapshot input.

# E003 held-out SBS window

## Execution — 2026-08-30

- Reused the unchanged E002 input and Ranking B process on two non-overlapping
  windows: 2026-05-01 through 2026-05-30 and 2026-05-31 through 2026-06-29.
- Ranked 825 unique articles: 395 previous and 430 current. The baseline
  extraction produced 3,029 preferred candidates.
- The observed top 20 was:

```text
부장, 소지섭, 송치, 가짜, 검찰, 법원, 산골 총각, 젠슨 황, 윤경호,
인생, 축구, 합숙, 시즌, 사실, 아빠, 얼굴, 임영웅, pd 수첩, 미니, 반박
```

The preliminary review found recognizable signals but also substantial legal,
editorial, and generic vocabulary. In particular, evidence titles contained the
work name `김부장`, while the candidate was truncated to `부장`. The provisional
gate of at least 10 specific results and at most five generic/artifact results
was not met; this is evidence of window sensitivity, not a verdict that Ranking
B has no value.

# E004 surface-span candidate comparison

## Execution — 2026-08-30

- Reused the stored E002 and E003 raw article metadata without network
  collection. Input windows, stopwords, minimum support, and Ranking B were
  unchanged.
- Changed only candidate boundaries: eligible Kiwi tokens retain their original
  `start`/`len` offsets, one-character tokens may participate in a longer phrase,
  and each 1–3-token candidate is sliced from the normalized source title.
- Generated ignored comparison artifacts under
  `artifacts/e004_surface_span/{e002,e003}/results.{json,md}`. Repeated ranking
  produced identical result objects. E002 produced 3,560 preferred candidates;
  E003 produced 3,513.

## Observed changes

- In E003, `부장` became `김부장` at the same rank and support (14 current, zero
  previous). `산골 총각` became the source spelling `산골총각`; `pd 수첩`
  (rank 18, 5/1) became `pd수첩` (rank 13, 8/1); and `차가원` entered the top 20.
  `미니` and `반박` left the top 20, but `pd` remained a partial candidate.
- In E002, `블랙 핑크` (rank 7, 5/0) became `블랙핑크` (rank 4, 6/0). However,
  the components `블랙` and `핑크` also entered ranks 12 and 13, displacing
  `빅뱅` and `런닝` from the top 20.

## Interpretation

Original-span reconstruction fixes the observed `김부장→부장` boundary loss
and consolidates some attached spellings such as `PD수첩` and `블랙핑크`. It does
not by itself solve shorter-component or generic-term ranking. E004 therefore
supports retaining source spans as the more faithful candidate representation,
but it does not make the overall usefulness gate pass or justify adding NER,
new stopwords, or a fixed product-ranking contract. It does not prevent a
source-local collection pipeline that preserves raw inputs for later replay.

## Human review and strengthened questions

- The reviewer found the trend quality of both the baseline and surface-span
  versions broadly acceptable. The surface-span change should therefore be
  evaluated as a boundary correction, not as proof that Ranking B became
  categorically better.
- SBS officially labels `sectionType=14` as its entertainment (`연예`) section,
  so `검찰`, `법원`, and `송치` are not evidence that the collector accidentally
  used a general-news section. Their evidence titles concern entertainers and
  entertainment-industry disputes, including Psy, Kim Soo-hyun, VIVIZ, and
  agency settlement cases. They can summarize a real burst of legal coverage
  while still being too broad to identify the particular cultural subject or
  incident the product should show. The stored rows do not include a separate
  per-article category field, so section membership is established by the SBS
  listing from which they were collected rather than an independently retained
  row label. Whether these are useful phenomenon-level signals or
  entertainment-editorial vocabulary remains unresolved; they must not be
  removed with an ad-hoc stopword decision from this window alone.
- Most E003 top-20 candidates have little or no previous-window support. This is
  consistent with Ranking B's purpose: its smoothed share ratio rewards sharp
  increases, especially from zero. It may consequently hide a candidate that
  was already frequent and remains frequent, even if a user would regard that
  persistent attention as an obvious current trend.
- The product question is therefore wider than Ranking B alone: users may want
  both `currently large/persistent` signals and `newly accelerating` signals.
  A current-share list, a second ranking, or a combined presentation is a
  candidate follow-up, not an approved algorithm change. The next comparison
  should first observe how much the existing current-share ranking recovers
  from the same fixed SBS input.

## Stage-boundary review

Continuing to require a clean top 20 before any pipeline work would now risk
turning an open-ended quality problem into a blocker. Across YouTube and two SBS
windows, the fixed process repeatedly produced recognizable candidates, and the
remaining failures concern ranking views and candidate specificity rather than
whether collectable input can produce any signal at all.

A minimal data-collection stage is therefore reasonable in parallel with later
ranking experiments, provided it stays algorithm-agnostic and reversible:

- preserve source-local item ID, title, row timestamp, URL, source identity, and
  collection metadata;
- retain source boundaries rather than fusing raw records or scores;
- make stored inputs replayable by multiple ranking versions;
- do not yet freeze a single `trend` score, production API response, source
  weighting scheme, or UI contract.

This is a recommendation to graduate from pure feasibility research into data
collection, not a claim that detection quality is finished. The distinction is
important: accumulating replayable data helps the remaining experiments,
whereas prematurely fixing the product output would make them harder.
