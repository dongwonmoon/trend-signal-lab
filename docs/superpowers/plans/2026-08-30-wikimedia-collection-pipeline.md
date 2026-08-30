# Wikimedia Collection Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collect explicit UTC date ranges of Korean Wikipedia daily top-page data into validated, atomic, Git-ignored source-local JSON files.

**Architecture:** One source-specific standard-library script fetches and validates one day at a time, writes one file per day, and skips accepted days on rerun. The API request project is `ko.wikipedia.org`, while the documented response project is `ko.wikipedia`; no ranking, database, scheduler, or generic source abstraction is added.

**Tech Stack:** Python 3.12 standard library, pytest, uv

## Global Constraints

- Follow `AGENTS.md`, `agent-instructions/codex.md`, and `docs/superpowers/specs/2026-08-30-wikimedia-collection-pipeline-design.md`.
- Create no dependency, notebook, database, scheduler, source adapter, ranking code, UI, or deployment configuration.
- Do not commit raw responses; `data/raw/` remains ignored.
- Use an identifying User-Agent containing `https://github.com/dongwonmoon/trend-signal-lab`.
- Make each accepted daily write atomic; a failed day must not damage accepted files.
- Do not run the 60-day backfill. Return its command for the user to run.

---

### Task 1: Source-specific Wikimedia daily collector

**Files:**
- Create: `scripts/collect_wikimedia.py`
- Create: `tests/test_collect_wikimedia.py`

**Interfaces:**
- Consumes: Wikimedia daily-top JSON from `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ko.wikipedia.org/all-access/YYYY/MM/DD`.
- Produces: `endpoint_url(day: date) -> str`.
- Produces: `validate_response(raw: bytes, requested_day: date) -> list[dict[str, object]]`.
- Produces: `collect_day(day: date, output_root: Path, *, fetcher: Callable[[date], bytes] = fetch_day, now: Callable[[], datetime] = utc_now) -> str`, returning `"written"` or `"skipped"`.
- Produces: CLI flags `--start YYYY-MM-DD`, optional `--end YYYY-MM-DD`, and optional `--output-dir` defaulting to `data/raw/wikimedia`.

- [x] **Step 1: Write the focused failing test**

Create `tests/test_collect_wikimedia.py` with one test covering accepted storage,
rerun skipping, and invalid-response isolation:

```python
import json
from datetime import date, datetime, timezone

import pytest

from scripts.collect_wikimedia import (
    WikimediaCollectionError,
    collect_day,
)


DAY = date(2026, 8, 29)
NOW = datetime(2026, 8, 30, 1, 23, 45, tzinfo=timezone.utc)


def response(*, project: str = "ko.wikipedia") -> bytes:
    return json.dumps(
        {
            "items": [
                {
                    "project": project,
                    "access": "all-access",
                    "year": "2026",
                    "month": "08",
                    "day": "29",
                    "articles": [
                        {"article": "리센느", "views": 20, "rank": 1},
                        {"article": "오징어_게임", "views": 10, "rank": 2},
                    ],
                }
            ]
        }
    ).encode()


def test_collect_day_is_atomic_idempotent_and_validated(tmp_path):
    calls = 0

    def fetcher(_: date) -> bytes:
        nonlocal calls
        calls += 1
        return response()

    assert collect_day(DAY, tmp_path, fetcher=fetcher, now=lambda: NOW) == "written"

    target = tmp_path / "ko.wikipedia.org" / "2026-08-29.json"
    stored = json.loads(target.read_text())
    assert stored["project"] == "ko.wikipedia.org"
    assert stored["snapshot_date"] == "2026-08-29"
    assert stored["time_zone"] == "UTC"
    assert stored["collected_at"] == "2026-08-30T01:23:45Z"
    assert stored["articles"][0] == {"article": "리센느", "views": 20, "rank": 1}

    assert collect_day(DAY, tmp_path, fetcher=fetcher, now=lambda: NOW) == "skipped"
    assert calls == 1

    invalid_root = tmp_path / "invalid"
    with pytest.raises(WikimediaCollectionError, match="project"):
        collect_day(
            DAY,
            invalid_root,
            fetcher=lambda _: response(project="wrong.project"),
            now=lambda: NOW,
        )
    assert not (invalid_root / "ko.wikipedia.org" / "2026-08-29.json").exists()
```

- [x] **Step 2: Run the focused test and confirm the expected failure**

Run:

```bash
uv run pytest -q tests/test_collect_wikimedia.py
```

Expected: collection fails because `scripts.collect_wikimedia` does not exist.

- [x] **Step 3: Implement only the daily collector and explicit range CLI**

Create `scripts/collect_wikimedia.py` with these constants and behaviors:

```python
API_PROJECT = "ko.wikipedia.org"
RESPONSE_PROJECT = "ko.wikipedia"
ACCESS = "all-access"
SOURCE = "wikimedia_pageviews_top"
USER_AGENT = (
    "trend-signal-lab/0.1 "
    "(https://github.com/dongwonmoon/trend-signal-lab)"
)
```

`endpoint_url()` must format the requested UTC date into the official endpoint.
`fetch_day()` must create `urllib.request.Request` with `User-Agent` and
`Accept: application/json`, call `urllib.request.urlopen(..., timeout=30)`, and
return the response bytes.

`validate_response()` must decode JSON and raise `WikimediaCollectionError` for
invalid JSON or any of these conditions:

```text
items is not a one-element list
project != ko.wikipedia
access != all-access
year/month/day do not match requested_day
articles is empty or not a list
article is empty or not a string
views has exact type other than int, or is negative
rank has exact type other than int, or is not positive
article names repeat
```

Return new article dictionaries containing only `article`, `views`, and `rank`,
sorted by source rank. Preserve tied or skipped source rank values; do not
normalize them.

`collect_day()` must:

```python
target = output_root / API_PROJECT / f"{day.isoformat()}.json"
if target.exists():
    return "skipped"
```

Otherwise fetch and validate before creating the final file. Use this wrapper:

```python
stored = {
    "source": SOURCE,
    "project": API_PROJECT,
    "snapshot_date": day.isoformat(),
    "time_zone": "UTC",
    "collected_at": collected_at,
    "request_url": endpoint_url(day),
    "articles": articles,
}
```

Serialize with `ensure_ascii=False`, `indent=2`, and a trailing newline, write a
temporary file in `target.parent`, and use
`os.replace()` for the final atomic move. Remove the temporary file if writing
or replacement fails. Format an aware UTC `now()` value as ISO 8601 ending in
`Z`; reject a naive `now()` value.

The CLI must parse ISO dates with `date.fromisoformat`, default `--end` to
`--start`, reject `end < start`, process days sequentially, print one concise
`written` or `skipped` line per date, and exit non-zero on the first exception.

- [x] **Step 4: Run the focused test and confirm it passes**

Run:

```bash
uv run pytest -q tests/test_collect_wikimedia.py
```

Expected: `1 passed`.

- [x] **Step 5: Run the short repository verification**

Run:

```bash
uv run pytest -q
git diff --check
git check-ignore data/raw/wikimedia/ko.wikipedia.org/2026-08-29.json
```

Expected: the complete test suite passes, the diff check is clean, and the raw
path is reported as ignored.

- [x] **Step 6: Run one bounded live compatibility check outside repository raw data**

Run:

```bash
uv run python scripts/collect_wikimedia.py \
  --start 2024-01-01 \
  --output-dir /tmp/trend-signal-wikimedia-smoke
```

Expected: one file is written with a non-empty ranked article list; source rank
ties or gaps are preserved.
If network access fails, report the exact failure without weakening validation
or adding retry infrastructure. Do not run the 60-day backfill.

- [x] **Step 7: Review and commit the implementation**

Review only the two owned files and confirm no raw data is tracked, then run:

```bash
git add scripts/collect_wikimedia.py tests/test_collect_wikimedia.py
git commit -m "feat: collect wikimedia daily pageviews"
```

### Verification record (2026-08-30)

- Focused test: `1 passed`; full suite: `24 passed`.
- Bounded live smoke for `2024-01-01` wrote 996 articles and preserved 200
  tied-rank groups; no 60-day run was performed.
- `data/raw/wikimedia/ko.wikipedia.org/2026-08-29.json` is ignored, and the
  branch diff check is clean.
