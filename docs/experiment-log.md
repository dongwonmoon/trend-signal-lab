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

# Phase 1 Wikimedia signal acceptance

## Execution — 2026-08-30

- Input: retained `data/raw/wikimedia/ko.wikipedia.org/*.json`, 60 daily
  snapshots 2026-07-01..2026-08-29, missing days none. July 29, which
  temporarily returned 404, is present in the retained set.
- Windows: previous 2026-07-01..07-30, current 2026-07-31..08-29, both 30
  days, split as first/last half of the retained day list.
- Process: per page, mean daily views inside each window (views summed, divided
  by present-day count). Prominence = current-window mean. Increase = log2
  smoothed change with a 1.0 pseudo-count. Top 20 lists each. No threshold,
  stopword, or system-page filtering.
- Script `scripts/run_wikimedia_baseline.py`, tests
  `tests/test_wikimedia_baseline.py` (5 tests, suite total 30 passed).
- Determinism: two clean runs produced identical JSON
  (`e2190031...591f`) and Markdown (`7a54dc49...d9c2`) SHA-256 hashes.
- Output: ignored `artifacts/wikimedia_phase1/results.{json,md}`.

## Observed top 20 — prominence (mean views/day, current window)

```text
위키백과:대문, 문화방송, 특수:검색, 한국방송공사, 안상호, 한국교육방송공사,
하영, 5·18_광주_민주화_운동, 트로이_전쟁, 오디세이_(영화), 친일반민족행위_705인_명단,
리센느, 유튜브, 이완용, 파일:XHamster_logo.svg, 특수:최근바뀜, 오디세이아,
정해인, 여성_사정, 사랑이_온다_(드라마)
```

## Observed top 20 — increased attendance (prev -> current)

```text
안상호, 친일반민족행위_705인_명단, 아가멤논, 위키백과:2026년_아시안_게임_에디터톤/럭비_챌린지,
이런_엿_같은_사랑, 친일파_708인_명단, 안병문, 네팔, 안정호, 맷_데이먼,
대정실업친목회, 트로이, 헬레네, 민족문제연구소의_친일인명사전_수록자_명단,
친일파_명단, 안건영, 유리의_성_(드라마), 여한구, 백인천, 박찬홍
```

## Provisional interpretation

- The prominence list is readable and plausible and already surfaces an
  anticipated anchor (`리센느` at rank 12). Every increased-attendance top-20
  page was absent from the previous window's retained top-page lists. The
  baseline encodes this absence as `mean prev = 0`; it does not establish zero
  actual views. With the same zero baseline, ordering follows current observed
  mean views. The log-ratio has no fixed maximum, and the result must not be
  described as a measured growth rate from zero actual audience interest.
- System pages (`위키백과:대문`, `특수:검색`, `특수:최근바뀜`, Ediathon
  namespace, the `파일:` media page) and `_`-joined page names remain visible
  as source-local artifacts; they are recorded, not tuned away.
- This is a source-local baseline inside Korean Wikipedia readership. It is not
  a measure of Korean culture-wide prevalence and does not fix a final score,
  UI, or product contract.
- At the time of this run, Phase 2 was awaiting human judgment on these lists.

## Human judgment and Phase 2 direction — 2026-08-31

- The user judged Phase 1 broadly positive and approved the Phase 2 design
  direction: a local static `인기 키워드` page using the latest retained
  completed UTC day's views, with limited Wikimedia prefix exclusions and
  visible source/date information.
- This closes the pending qualitative judgment for proceeding to a local
  product slice. It does not validate daily output quality, approve a final
  trend score, or resolve historical top-list censoring.
- The two 30-day baseline results remain historical evidence. Phase 2 will
  inspect daily outputs separately rather than relabel the existing averages
  as today's trend or silently change the baseline.
- The [Phase 2 design](superpowers/specs/2026-08-31-phase2-local-popular-keywords-design.md)
  records the accepted direction and deferred decisions. This update contains
  no new run, runtime change, or deployment. The user subsequently approved the
  written spec and requested its implementation handoff plan; daily-output
  acceptance remains pending until the actual page is inspected.

## Baseline corrections before integration — 2026-08-31

- Fixed window selection to use the latest 60 consecutive retained dates,
  divided into adjacent 30-day windows. More history no longer separates the
  previous and current windows; a missing date in the required interval fails
  rather than silently changing the comparison period.
- Removed the uncomputed `change_score: 0` field from prominence JSON rows.
  Ranking B retains its existing formula and score field. This is an artifact
  correction, not a new ranking experiment.
- The regression checks first reproduced the old-window selection, accepted
  gap, and fabricated score. The focused suite then passed all seven tests;
  the full suite passed all 32 tests. Locked dependency synchronization and
  diff checks also passed; no dependency or collection changes were made.
- Replayed the retained 2026-07-01..08-29 input once into ignored
  `artifacts/wikimedia_phase1_premerge/`. Comparison with the original artifact
  confirmed identical windows, prominence names/order/view means, and complete
  Ranking B rows. Only the unused prominence score field differs. The original
  artifacts remain untouched.
- Phase 2 runtime implementation and daily-page human acceptance remain
  separate follow-up work under the approved design and implementation plan.

# Phase 2 Local daily popular-keyword page

## Execution — 2026-08-31

- Integrated after Phase 1 human judgment: the user approved a local static
  `인기 키워드` page using one completed UTC day ranked by views.
- Generator `scripts/build_wikimedia_page.py` selects the latest retained
  snapshot strictly before the current UTC date, validates the stored
  contract (source/project/snapshot_date/UTC/request_url/collected_at,
  article rows, unique names, integer views/ranks), excludes exact
  `위키백과:`, `특수:`, `파일:` prefixes, ranks by daily views with name
  tiebreak, and writes `results.json` then `index.html` atomically.
- Smoke generated for the latest retained day (2026-08-29) and two earlier
  retained days (2026-08-28, 2026-08-27) into ignored
  `artifacts/wikimedia_phase2/` directories. Re-running produced byte-identical
  JSON and HTML for a fixed day.
- Observed top-10, daily views (latest first): 문화방송 16,157; 한국방송공사
  10,222; 한국교육방송공사 8,685; 이용주 (배우) 6,235; 네팔 4,569; 이용주
  (희극인) 4,108; 5·18 광주 민주화 운동 3,673; 비비 (대한민국의 가수) 3,087;
  트로이 전쟁 2,858; 사랑이 온다 (드라마) 2,733.
- The 2026-08-29 page was opened in a real browser for layout and readability;
  actual human usefulness judgment remains the user's call and is the closing
  condition for Phase 2.

## Limitations

- Two distinct `이용주` pages (배우/희극인) both appear; no alias merging.
- Broadcasting names (문화방송/한국방송공사/한국교육방송공사) dominate the
  top of daily lists; they are not removed by the approved prefix policy.
- `5·18 광주 민주화 운동` shows the `_` replaced by spaces in display only;
  source identity remains the underscore title.
- These are smoke observations, not preregistered quality evidence. Phase 2 is
  complete when the user judges a daily list worth browsing.

## Product review and sequencing decision — 2026-08-31

- Review found that the page follows its approved daily-view design, but the
  user expected the temporal signal explored earlier to reach the product.
  Technical implementation is not acceptance of that narrower product scope.
- Focused Phase 2 tests passed (4 tests). Direct replay through the current
  generator matched all three retained JSON artifacts for August 27, 28, and
  29. Their first three entries were the same broadcasting organizations. This
  demonstrates the observed daily rankings, not their cause or wider prevalence.
- The review did not repeat a browser inspection. The implementation report
  records only August 29's browser check; the earlier two dates' visual checks
  and the original plan's checkbox reconciliation remain unverified. No new
  full-suite run or product-acceptance claim is implied here.
- The user approved holding deployment/page auto-refresh and preparing two
  parallel tasks: daily temporal-ranking design and a complementary second-
  source investigation with one bounded sample. Periods, missing-observation
  policy, source choice, and new runtime work are not approved by this decision.
- Immediate 60-day backfill is no longer a universal candidate gate. Acquisition,
  storage, event-time, and permission boundaries remain. A future-only source
  may require periodic capture, which must be proposed separately rather than
  silently equated with public page refresh.
- Keep the existing collector, daily page, A reference, and historical B
  artifacts. Source-local development may proceed in parallel without fusing
  data or requiring final Process quality first. The [roadmap](superpowers/specs/2026-08-30-product-roadmap-design.md)
  owns the revised priorities and two handoff prompts. This decision update
  makes no code change and performs no new source collection.
