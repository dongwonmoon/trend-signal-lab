# Trend Signal Lab Product Roadmap Design

**Date:** 2026-08-30
**Status:** Approved roadmap; priorities revised with the user on 2026-08-31

## Purpose

This document defines the path from the current research and collection
workspace to a small public product. It explains why each phase exists, what
decision it must enable, and what evidence permits the next phase to begin.

It is deliberately not a backlog for the whole product. Later task lists would
encode assumptions that have not yet been tested. Only explicitly active work
gets a detailed plan. Phase numbers are stable references, not an obligation to
execute every phase serially; the current priorities below govern sequencing.

## Current evidence and stage transition

The repository has already established that:

- fixed historical YouTube and SBS inputs can produce recognizable Korean
  candidates, although candidate specificity and ranking views remain open;
- a source-selected input is a lens, not a culture-wide prevalence measure;
- collection can proceed without freezing a final ranking or product contract;
- the Wikimedia daily-top collector preserves 60 replayable UTC snapshots from
  `2026-07-01` through `2026-08-29`, including page title, source rank, views,
  event date, collection time, and request provenance;
- Wikimedia can temporarily return `404` for a valid day and later recover it,
  so absence must remain visible and retryable rather than becoming an empty
  accepted snapshot.

This evidence is enough to leave pure feasibility research and build a narrow
product path. It is not evidence that detection quality, source coverage, or
the final user experience is solved.

## Product north star

The eventual product should:

> Show Korean-language users which keywords and names are receiving attention
> now, update that view daily, and later help them understand the source-backed
> signals and cultural phenomena connected to a selected item.

The keyword may already be familiar to the user. The value is not restricted
to discovering an unknown word; seeing that a known name is still prominent
can itself be interesting.

The product begins with observable keyword and name outputs. Cultural-phenomenon
interpretation is a later layer built from related candidates and evidence, not
a replacement for the observable list.

## BlackKiwi as a product analogy

[BlackKiwi](https://blackkiwi.net/) describes itself as a keyword search-volume
lookup and analysis service. It is a useful analogy for a later detailed
keyword-analysis experience, but it is neither a data source nor a product
contract for Trend Signal Lab.

The intended distinction is the starting point:

- BlackKiwi-like experience: the user supplies a keyword and inspects it;
- Trend Signal Lab: the product first presents a daily discovery list, then
  lets the user inspect an item more deeply.

No BlackKiwi feature, metric, taxonomy, layout, or business model is approved
for imitation merely because the analogy is useful.

## Delivery strategy

Three broad sequences were considered:

1. **Vertical slice first — selected, sequence revised.** Keep one source's
   usable local path, address observed ranking and coverage limits, then publish
   when the user accepts the list's purpose and limitations. A second-source
   investigation need not wait for deployment or keyword detail.
2. **Data platform first — rejected for now.** A generic multi-source pipeline
   would be tidy but would freeze abstractions before a second source and user
   need prove them necessary.
3. **Ranking research first — rejected as the delivery sequence.** Ranking
   experiments remain valuable, but requiring a clean final ranking before any
   product work would turn an open-ended quality problem into a launch blocker.

The selected strategy optimizes for a reversible product path, not automatic
promotion from a working page to public deployment. It does not lower the
evidence standard for data integrity or source claims.

## Current priorities — 2026-08-31

The daily-view page implements its approved narrow design, but the user expected
the temporal signal explored earlier to reach the product. The page currently
uses no previous-period comparison. A working data-to-page path is useful
engineering progress, not acceptance that its list is the intended product.
Preserve the page, collector, and historical outputs rather than restarting.

Two bounded workstreams may now proceed independently:

- **List refinement design (Phase 2 follow-up):** define how daily interest is
  compared with a preceding baseline and how unobserved historical top-list
  entries are handled. Reuse the existing B approach where its assumptions fit;
  do not equate top-list absence with zero actual views. Keep A as a reference
  rather than declaring sustained popularity irrelevant. The comparison period,
  missing-observation policy, and final presentation still require approval.
- **Second-source investigation (Phase 5 discovery only):** reuse prior research,
  assess complementary coverage, and inspect a small permitted sample from one
  promising candidate. This is not approval for a collector, source fusion, or
  a generic ingestion platform. No particular candidate has been selected.

Phase 3 public deployment and page auto-refresh are on hold. Phase 4 detail is
not a prerequisite for these workstreams; Phases 6 and 7 remain later outcomes.
Reconsider deployment after inspecting an actual list whose purpose and limits
the user accepts, or if the user explicitly chooses an earlier limited release.
Neither a perfect top 20 nor a mandatory number of sources is an exit gate.

Source expansion need not wait for a finished Process. A sufficient starting
point is understood measurement semantics, replayable records, known collection
failure/coverage limits, and at least some interpretable source-local output.
This does not claim long-term operational stability. Keep the existing input
fixed when assessing a processing change; evaluate a new source with its own
appropriate simple process. Parallel development is allowed, but changing both
and attributing the output difference to only one is not valid evidence.

Immediate 60-day backfill is no longer a universal source-selection gate; it
came from the earlier 30-day-versus-30-day experiment. Record actual history,
retention, freshness, and time until a useful comparison can be made. Keep
identity, event time, acquisition, storage, and public-use conditions explicit;
postponing deployment does not waive permission checks. If a candidate cannot
be backfilled, report whether a small periodic capture is needed to avoid losing
future history. That collection decision is separate from page auto-refresh
and requires approval before implementation.

The two handoff prompts below prepare decisions, not runtime changes. Detailed
implementation plans follow only after the relevant design/source approval.

## Phase map

### Phase 1 — Accept the Wikimedia signal

**Purpose:** Determine whether the collected source can produce a minimally
interesting product input and whether the stored contract is sufficient for
replay.

**Smallest output:** Two source-local lists derived from the same 60-day input:

- currently prominent page names;
- page names whose normalized attention increased from the previous window to
  the current window.

Wikimedia `views` must participate in this baseline. Reusing the earlier
document-frequency Ranking B unchanged would discard the source's direct
attention measure and would test the wrong process.

**Exit evidence:**

- every available daily file is readable and its coverage and gaps are
  reported;
- the calculation is deterministic and preserves the two 30-day windows;
- a human can inspect the actual top results and identify at least some
  plausible names or topics;
- limitations such as Wikipedia system pages, one-day spikes, and source scope
  are recorded without tuning them away after seeing the list.

**Stop or revise when:** the stored schema cannot support the calculation, the
source contains too little usable Korean topical content, or an apparent result
depends on silently discarding `views`, dates, or missing-day information.

### Phase 2 — Build the single-source local product slice

**Purpose:** Test the experience of viewing a daily list rather than continuing
to judge only tables and experiment artifacts.

**Smallest output:** A local read-only page that consumes generated source-local
JSON and presents one plainly named `인기 키워드` list. The phase may show
minimal supporting numbers needed to understand the list, but it does not add
accounts, search, personalization, editorial tools, or a database.

**Selected design — 2026-08-31:** Use the most recent retained completed UTC
day, rank by that day's views, apply only the approved Wikimedia prefix
exclusions, and generate a static HTML page from source-local JSON. Display the
actual measurement date; this is neither a 30-day mean nor real-time growth.
See the [Phase 2 design](2026-08-31-phase2-local-popular-keywords-design.md) for
the approved direction, failure behavior, and deferred decisions. The user
approved the written spec; its linked implementation plan defines the two
sequential tasks. Track execution there and daily-output acceptance in the
experiment log, separately from design approval.

**Current follow-up:** The daily-view implementation remains a baseline. The
current-priorities section now advances temporal-ranking design before treating
the list as ready for public release; it does not retroactively change what the
original implementation was asked to do.

**Exit evidence:** A user can open the page, understand what is current, and
judge whether browsing the list is interesting. The generation path is
repeatable from retained input without manual data editing.

**Stop or revise when:** the list is not understandable outside the research
report, or the UI requires a product contract that Phase 1 did not establish.

### Phase 3 — Publish and refresh daily

**Sequencing:** On hold under the current priorities; not the automatic next
step after a technically working Phase 2 page.

**Purpose:** Turn the local slice into a real product and observe operational
failures that a local demonstration cannot reveal.

**Smallest output:** A public URL and one daily path that collects, calculates,
and publishes the latest generated result. The deployment must expose failure
rather than silently serving a falsely current list.

**Exit evidence:** The public list updates without manual data modification,
the displayed data date is visible, and a failed or missing refresh can be
noticed and safely replayed.

**Deferred:** queues, distributed workers, multi-region deployment, general job
orchestration, and production databases remain unnecessary until the single
daily job demonstrates a concrete limit.

### Phase 4 — Add a keyword detail experience

**Purpose:** Learn whether opening one item provides additional value beyond
the list.

**Smallest output:** A source-specific history for the selected page name,
including its attention trajectory and previous/current comparison. This is the
first phase that may explore a BlackKiwi-like detail interaction.

It must not claim to explain *why* attention changed unless the displayed
source evidence actually supports that claim.

**Exit evidence:** Users can answer a concrete question from the detail view
that the list alone cannot answer, such as whether attention is persistent or a
short spike.

### Phase 5 — Add a second source without fusion

**Sequencing:** Candidate research and a bounded permitted sample may run in
parallel with Phase 2 refinement, before Phases 3 and 4. Collector/ranking
implementation requires a separate source-specific approval afterward.

**Purpose:** Test whether another lens adds useful information and learn the
first real cross-source boundary before designing a generic pipeline.

**Smallest output:** A second source-local collector and ranking whose result is
shown alongside Wikimedia. Raw records and incomparable scores remain separate.

**Exit evidence:** The second source reveals useful candidates or context that
Wikimedia misses, and its acquisition rights, event time, identity, replay, and
failure behavior are explicit.

**Stop or revise when:** the source adds volume but no distinct information, or
its rights and operational assumptions cannot support a public product.

### Phase 6 — Synthesize source-local signals

**Purpose:** Connect evidence about the same candidate without hiding source
differences behind a premature universal score.

**Smallest output:** Conservative name and alias matching, grouped source-local
signals, and visible agreement or disagreement between sources.

**Exit evidence:** The grouped result is more useful than two parallel lists,
and errors from aliasing or incompatible time windows are observable and
reversible.

Source weighting, a unified trend score, and confidence labels require their
own evidence. They are not implied by grouping.

### Phase 7 — Interpret cultural phenomena

**Purpose:** Move from observable names to a higher-level account of what may be
happening in culture.

**Smallest output:** Related candidate groups and short interpretations that
separate source facts, algorithmic associations, and human- or model-generated
inference.

**Exit evidence:** Repeated human review finds the grouping useful and not
merely plausible-sounding; unsupported explanations are identifiable; rejected
or uncertain interpretations are preserved rather than silently promoted.

This phase completes the current product north star. It does not make the
service a complete measure of Korean culture.

## Cross-phase rules

- Change Input, Process, and Output together only when a phase explicitly tests
  their interaction.
- Preserve source identity and source-local record identity throughout.
- Distinguish event time, collection time, and displayed data freshness.
- Retain replayable inputs so later ranking versions do not require recollection.
- Never present a source-selected list as culture-wide prevalence.
- Keep raw source records and incomparable scores separate until evidence
  supports synthesis.
- Do not commit secrets, personal data, large raw inputs, or content with
  unclear redistribution rights.
- A visually attractive list is not evidence that its interpretation is true.
- A failed phase may reject or revise the next phase; completing code is not a
  reason to proceed.

## Phase planning and handoff contract

Only explicitly active, approved implementation work receives a task-level
implementation plan. Research/design briefs may proceed in parallel without
authorizing code. Each implementation task must state:

- its user- or decision-facing purpose;
- owned files and explicit non-goals;
- input and output contracts;
- the smallest runnable verification;
- its commit boundary;
- conditions that require escalation rather than invention.

An execution agent receives a short prompt pointing to the repository
instructions, the approved phase design, and one task number. Context is kept
in versioned documents rather than repeated in a large chat prompt.

Each task or coherent checkpoint reports:

- base and head commit IDs;
- files changed;
- commands and observed results;
- generated output worth human inspection;
- deviations from the plan and why they occurred;
- remaining risks and unverified assumptions.

A higher-cost reviewer is most valuable at an irreversible structural boundary
and at the final phase diff. Routine implementation does not require that
reviewer when the task contract, evidence, and rollback boundary are clear.

### Handoff A — Daily temporal-ranking design

Owner: main/product-design session. Runtime code and raw files are read-only;
return a proposal for discussion, then update the Phase 2 design only after
approval. Do not let this workstream edit the source-research owner's document.

```text
Trend Signal Lab의 기존 일별 화면에 관심 변화 B를 연결할 최소 설계를 검토해줘.
AGENTS.md, docs/superpowers/specs/2026-08-30-product-roadmap-design.md의 Current priorities,
docs/superpowers/specs/2026-08-31-phase2-local-popular-keywords-design.md,
scripts/build_wikimedia_page.py와 scripts/run_wikimedia_baseline.py를 먼저 읽어.
목적은 단순 조회수 순위와 평소 대비 관심 변화를 구분하는 것이다.
기존 수집기·화면·A 결과는 보존하고, 새 NLP나 통합 점수를 만들지 마.
핵심 결정은 비교 기간과 이전 상위 목록 미관측 처리다.
미관측을 실제 조회수 0으로 취급하지 말고, 보관 데이터로 가능한 범위를 확인해.
비교 기준 후보를 2개 이내로 제시하고, 각각의 의미·한계·필요 데이터를 설명해.
A를 참조로 유지하면서 B를 보여줄 최소안과, 그 안이 틀렸음을 확인할 방법을 제안해.
기간·정책·표현을 임의로 확정하거나 코드를 수정하지 마.
짧은 추천안과 사용자가 결정해야 할 사항을 반환하고, 승인 후에만 구현 계획을 작성해.
```

### Handoff B — Complementary second-source investigation

Owner: one low-cost researcher (Luna if delegated here). May append dated findings
only to `docs/superpowers/specs/2026-08-30-public-culture-source-research.md`;
no runtime/roadmap edits.
Final product and source-permission decisions remain with the main session/user.

```text
Trend Signal Lab에서 위키백과가 놓치는 정보를 줄 두 번째 소스를 조사해줘.
AGENTS.md, docs/superpowers/specs/2026-08-30-product-roadmap-design.md의 Current priorities와
docs/superpowers/specs/2026-08-30-public-culture-source-research.md부터 읽어.
기존 조사를 재사용하고, 후보 검토는 최대 3개, 실제 작은 샘플 확인은 후보 1개로 제한해.
60일 즉시 확보는 필수가 아니다. 실제 제공 기간·보존 기간·관측 주기를 기록해.
무엇을 측정하는지(조회·검색·언급·판매 등), 위키와 다른 정보가 무엇인지 구분해.
행별 식별자·이벤트 시각·출처, 수집 및 보관 조건, 향후 공개 이용 조건을 확인해.
현재 1차 출처 링크와 확인 날짜를 남기고, 과거 조사 결론을 영구적인 허가/금지로 단정하지 마.
접근·검토가 허용되는 후보라면 5~20행 정도만 확인해 필드·중복·시간 범위를 보고해.
샘플은 접근성과 구조의 증거이지 대표성이나 트렌드 품질의 증거가 아니다.
키·승인이 없으면 우회하지 말고 한계를 보고해. 새 가입·비용·수집기·대량 다운로드는 금지한다.
검토하지 않은 원문·개인정보·비밀값을 저장하거나 커밋하지 마.
과거 데이터가 없다면 최소 주기 수집이 필요한지만 보고하고 직접 시작하지 마.
소스별 Process 변경 필요성도 적되, 기존 점수와 합치거나 전체 구조를 설계하지 마.
기존 조사 문서에 새 날짜의 근거·샘플 관찰·가설·남은 조건을 구분해 추가하고,
추천 후보 하나 또는 적합한 후보 없음으로 간결히 보고해. 소스 채택은 사용자가 결정한다.
```

## Roadmap revision triggers

This roadmap must be reconsidered when:

- Phase 1 cannot produce an intelligible source-local result;
- public deployment requires a materially different data or licensing model;
- user observation contradicts the discovery-first product hypothesis;
- a second source proves that source-local boundaries are insufficient;
- evidence shows that a later phase should be removed, reordered, or split.

Revising the roadmap after such evidence is correct operation, not failure.
