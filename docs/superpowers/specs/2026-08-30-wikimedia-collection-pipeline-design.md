# Wikimedia collection pipeline design

**Date:** 2026-08-30
**Status:** Approved for implementation

## Goal

Build the smallest source-specific collection slice that can bootstrap a public
Trend Signal Lab v0 with replayable Korean Wikipedia daily pageview inputs.
The slice collects one explicit UTC date range locally. It does not define the
final ranking, UI, deployment runtime, or multi-source product contract.

The selected source is Wikimedia Analytics API daily top pages for
`ko.wikipedia.org`. This measures attention within Korean Wikipedia readership,
not Korean-population interest or culture-wide prevalence. Analytics API data is
CC0 and requests must use an identifying User-Agent; those source facts and the
broader candidate comparison are recorded in
`2026-08-30-public-culture-source-research.md`.

## Approved slice

- Fetch the `all-access` daily top-page response for an explicit inclusive
  `--start` and optional `--end` date.
- Make requests sequentially with an identifying User-Agent.
- Store one validated source-local JSON file per UTC day under
  `data/raw/wikimedia/ko.wikipedia.org/`.
- Skip an already accepted day so reruns resume rather than duplicate work.
- Stop on the first failed or invalid day without damaging accepted files.
- Verify one live day before the user runs the 60-day backfill.

Ranking, a scheduler, UI, deployment, and additional sources are outside this
slice.

## Stored record

The file path is the authoritative daily partition:

```text
data/raw/wikimedia/ko.wikipedia.org/YYYY-MM-DD.json
```

Each file stores:

```json
{
  "source": "wikimedia_pageviews_top",
  "project": "ko.wikipedia.org",
  "snapshot_date": "2026-08-29",
  "time_zone": "UTC",
  "collected_at": "2026-08-30T01:23:45Z",
  "request_url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/...",
  "articles": [
    {
      "article": "article_title",
      "views": 12345,
      "rank": 1
    }
  ]
}
```

The source-local observation identity is
`(project, snapshot_date, article)`. `snapshot_date` is the source's UTC metric
date; `collected_at` is the acquisition time. Article titles, views, and ranks
remain source data and are not declared to be a universal trend score.

Raw daily files remain ignored by Git even though the Analytics API data is
CC0. The public repository records code, provenance, and derived evidence, not
bulk raw inputs.

## Collection behavior

The collector is one Python script and uses only the standard library. A run
looks like:

```bash
uv run python scripts/collect_wikimedia.py \
  --start 2026-07-01 \
  --end 2026-08-29
```

`--end` defaults to `--start`, making a one-day compatibility check the same
code path as a backfill. Dates are explicit; the collector does not guess a
local "yesterday" or silently fall back to an older available day.

For each day the collector:

1. skips the day if its final file already exists;
2. requests the official daily endpoint with a finite timeout;
3. parses and validates the complete response in memory;
4. wraps the accepted source response with acquisition metadata;
5. writes a temporary file in the destination directory;
6. atomically replaces the final path.

There is no automatic retry or concurrency. A failed run exits non-zero; a
later rerun skips accepted days and resumes at the missing day. This is enough
for a 60-request local bootstrap and avoids a retry or job framework.

## Validation and failure boundary

Before writing, require:

- exactly one response item for the requested project and date;
- a non-empty article list;
- non-empty article names;
- integer, non-negative view counts;
- positive integer ranks;
- unique article names and ranks within the day;
- ranks forming a contiguous sequence starting at one.

HTTP errors, timeouts, invalid JSON, date mismatches, or validation failures
must not create or replace the final file. An existing accepted file is never
refreshed in this slice.

## Verification

Leave one focused test using a fake response path. It must demonstrate that a
valid day is stored, rerunning skips it, and invalid input does not overwrite
accepted data. Then run the existing suite and repository checks.

A live one-day request confirms current endpoint compatibility. The user runs
the longer 60-day backfill separately so the main session does not wait on a
background terminal process.

## Source expansion boundary

This design intentionally does not create a source adapter, common raw schema,
or universal trend score. A future source gets its own collector, source-local
storage, and source-appropriate ranking. Common code is extracted only after a
second implementation demonstrates actual duplication. Cross-source comparison
or fusion remains a separate evidence-gated product decision.

## Deferred decisions and revisit triggers

- **Ranking:** design after observing the collected 60-day Wikimedia fields and
  coverage; current title-document-frequency code must not silently discard
  views and rank.
- **Scheduler:** add after the local collector and ranking produce a useful
  daily artifact.
- **Database or object storage:** add when per-day local files block deployment
  or concurrent access.
- **Historical refresh:** add only if source revisions are directly observed.
- **Retries and backoff:** add when transient failures make manual reruns
  materially unreliable.
- **Generic source interface:** add only with the second implemented source.
- **Source fusion and weighting:** revisit only after two source-local outputs
  exist and their signals can be compared honestly.
- **Evidence content, UI, and public API:** specify in their own product slices;
  this collector does not approve article content display or a stable API.
