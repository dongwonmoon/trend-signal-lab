# Trend Signal Lab Product Roadmap Design

**Date:** 2026-08-30
**Status:** Approved roadmap; only the current phase may be planned in detail

## Purpose

This document defines the path from the current research and collection
workspace to a small public product. It explains why each phase exists, what
decision it must enable, and what evidence permits the next phase to begin.

It is deliberately not a backlog for the whole product. Later task lists would
encode assumptions that have not yet been tested. Only the active phase gets an
implementation plan; later phases remain outcome and gate descriptions until
the preceding phase closes.

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

1. **Vertical slice first — selected.** Make one source produce one real user
   experience, publish it, then expand only where observed limitations require
   it.
2. **Data platform first — rejected for now.** A generic multi-source pipeline
   would be tidy but would freeze abstractions before a second source and user
   need prove them necessary.
3. **Ranking research first — rejected as the delivery sequence.** Ranking
   experiments remain valuable, but requiring a clean final ranking before any
   product work would turn an open-ended quality problem into a launch blocker.

The selected strategy optimizes for a reversible public vertical slice. It
does not lower the evidence standard for data integrity or source claims.

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
the approved direction, failure behavior, and deferred decisions. Its written
spec is awaiting user review before implementation planning.

**Exit evidence:** A user can open the page, understand what is current, and
judge whether browsing the list is interesting. The generation path is
repeatable from retained input without manual data editing.

**Stop or revise when:** the list is not understandable outside the research
report, or the UI requires a product contract that Phase 1 did not establish.

### Phase 3 — Publish and refresh daily

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

Only the active phase receives a task-level implementation plan. Each task must
state:

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

## Roadmap revision triggers

This roadmap must be reconsidered when:

- Phase 1 cannot produce an intelligible source-local result;
- public deployment requires a materially different data or licensing model;
- user observation contradicts the discovery-first product hypothesis;
- a second source proves that source-local boundaries are insufficient;
- evidence shows that a later phase should be removed, reordered, or split.

Revising the roadmap after such evidence is correct operation, not failure.
