# Phase 2 Local Popular Keywords Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline local page showing up to 20 popular Korean Wikipedia page names for one completed UTC day, with honest source/date labels.

**Architecture:** One source-specific Python module reads one retained snapshot, validates it, and generates JSON. It then renders that JSON into self-contained HTML, publishing the page last. Existing collection and historical experiments remain unchanged.

**Tech Stack:** Python >=3.12 standard library, existing pytest and uv; no new dependency, JavaScript, or build tool.

## Global Constraints

- Follow `AGENTS.md`, `agent-instructions/codex.md`, and the approved [Phase 2 design](../specs/2026-08-31-phase2-local-popular-keywords-design.md).
- Default to the latest retained completed UTC day, not a 30-day average or growth Ranking B.
- Exact excluded prefixes: `위키백과:`, `특수:`, `파일:`; filter before selecting at most 20.
- Preserve source names and ranks; replace `_` with spaces only in display labels.
- Title: `인기 키워드`; explanation: `한국어 위키백과 조회수 기준`; show the actual one-day UTC data date.
- No collection during generation, public deployment, scheduler, database, NLP tuning, additional source, or general adapter framework.
- No raw data or generated artifacts in Git; preserve unrelated work, including `.DS_Store` if present.
- Phase 2 is not complete until the user has judged the actual daily page. Test success is not usefulness evidence.

## Why these boundaries matter

The user wants a small product, not another infrastructure or algorithm project.
Phase 1 produced recognizable topics across 30-day windows, but those results
cannot validate a daily list. This phase deliberately makes that product choice
visible without replacing the historical evidence. Fixed names remaining popular
are legitimate output; no novelty or perfect-top-20 gate is required.

Only two sequential tasks are needed. Use one low-cost execution agent/session;
do not spawn a reviewer for every step. The user prefers an external lower-cost
implementer with Codex reviewing the phase diff. If executing here is separately
requested, use Luna rather than Sol workers. Never implement files concurrently
because both tasks own the same module and test file.

For hosts without the named workflow skills, follow this plan's scope, focused
checks, and reporting contract directly; do not install tooling just to execute
the plan. No worker may decide source policy or cultural usefulness for the user.

## File map and reuse

- Create `scripts/build_wikimedia_page.py`: selection, stored-input validation,
  result projection, rendering, atomic output, CLI. Functions in one small module;
  no package restructuring.
- Create `tests/test_build_wikimedia_page.py`: synthetic inputs and focused
  behavioral checks for the two tasks. Use the existing pytest setup.
- Update `README.md`: generation command, local file location, date/source limits.
- Update `docs/experiment-log.md`: actual smoke observations and human review state.
- Update this plan's checkboxes as work is verified, not merely attempted.
- Read only: `scripts/collect_wikimedia.py`,
  `scripts/run_wikimedia_baseline.py`, and their tests.

Reuse collector constants `SOURCE`, `API_PROJECT`, and `endpoint_url(day)` without
network calls. Reuse baseline `rank_prominent(mean_cur, top_n)` only for its stable
descending-value/name ordering. Do not use `load_days`, `aggregate`, or
`split_windows`: they load/aggregate historical windows and are not the daily
product path. The collector's `validate_response` accepts an API envelope, not a
retained file; do not manufacture a fake API response just to reuse that parser.

Use `python -m scripts.build_wikimedia_page` from the repository root so imports
from the existing `scripts` namespace work without a `sys.path` workaround.

## Task 1 — Validated daily JSON generator

**Purpose:** Establish exactly which day and measurement the page will represent,
independently of presentation. A clean UI must not disguise incorrect provenance.

**Files:** Create the generator and its test file; update README with the JSON
command and this plan's verified checkboxes. Do not modify existing runtime files.

**Interfaces:**

- `select_snapshot(data_root: Path, requested: date | None, *, today: date) -> Path`
- `load_snapshot(path: Path) -> dict`: validates and returns the retained object.
- `build_result(snapshot: dict) -> dict`: consumes validated input only.
- `write_atomic(path: Path, content: str) -> None`
- `main(argv: list[str] | None = None) -> int`
- CLI: optional `--data-root` default `data/raw/wikimedia/ko.wikipedia.org`,
  optional `--date YYYY-MM-DD`, optional `--output-dir` default
  `artifacts/wikimedia_phase2`. Task 1 writes `results.json`.

- [ ] **1. Add these focused checks before implementation.**

```python
import json
from datetime import date

import pytest

from scripts import build_wikimedia_page as page
from scripts.collect_wikimedia import API_PROJECT, SOURCE, endpoint_url


def stored(day, articles):
    return {
        "source": SOURCE, "project": API_PROJECT,
        "snapshot_date": day.isoformat(), "time_zone": "UTC",
        "collected_at": "2026-08-31T01:00:00Z",
        "request_url": endpoint_url(day), "articles": articles,
    }


def test_daily_selection_projection_and_validation(tmp_path):
    day = date(2026, 8, 29)
    rows = [
        {"article": name, "views": 100, "rank": 1}
        for name in ["위키백과:대문", "특수:검색", "파일:그림.svg"]
    ] + [
        {"article": "나_주제", "views": 20, "rank": 4},
        {"article": "가:주제", "views": 20, "rank": 4},
    ] + [
        {"article": f"항목{i:02}", "views": 1, "rank": i + 6}
        for i in range(25)
    ]
    target = tmp_path / "2026-08-29.json"
    payload = stored(day, rows)
    target.write_text(json.dumps(payload), encoding="utf-8")
    # The current UTC day is ineligible; its contents must not be read.
    (tmp_path / "2026-08-30.json").write_text("invalid", encoding="utf-8")
    selected = page.select_snapshot(tmp_path, None, today=date(2026, 8, 30))
    assert selected == target
    result = page.build_result(page.load_snapshot(selected))
    assert result["snapshot_date"] == "2026-08-29"
    assert result["ranking"] == "daily_views"
    assert len(result["items"]) == 20
    assert result["items"][0] == {
        "rank": 1, "source_rank": 4, "page": "가:주제", "views": 20,
    }
    assert result["items"][1]["page"] == "나_주제"
    assert [r["rank"] for r in result["items"]] == list(range(1, 21))
    payload["source"] = "another_source"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        page.load_snapshot(selected)
    with pytest.raises(ValueError):
        page.select_snapshot(tmp_path, date(2026, 8, 30), today=date(2026, 8, 30))
    with pytest.raises(FileNotFoundError):
        page.select_snapshot(tmp_path, date(2026, 8, 28), today=date(2026, 8, 30))


def test_invalid_snapshot_does_not_replace_accepted_json(tmp_path):
    root, out = tmp_path / "raw", tmp_path / "out"
    root.mkdir()
    out.mkdir()
    (root / "2026-08-29.json").write_text("{}", encoding="utf-8")
    accepted = out / "results.json"
    accepted.write_text("accepted", encoding="utf-8")
    assert page.main(["--data-root", str(root), "--date", "2026-08-29",
                      "--output-dir", str(out)]) != 0
    assert accepted.read_text(encoding="utf-8") == "accepted"
```

- [ ] **2. Run the focused test and observe the expected missing-module failure.**

```bash
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run pytest -q tests/test_build_wikimedia_page.py
```

Do not rerun the whole repository at each small edit. Expected failure is an
absent implementation, not an environment error.

- [ ] **3. Implement selection and validation in the new module.**

For explicit dates, reject `requested >= today` and require that exact file.
Otherwise enumerate only dated `.json` filenames, choose the maximum date below
`today`, then read just that file. A `.json` filename not in canonical
`YYYY-MM-DD` format is an input error, not a reason to guess another file.
Never read the newest file, find it invalid, and silently select an older one.

`load_snapshot` uses `json.loads(path.read_text(encoding="utf-8"))`. Check the
object before `.get`, then exact `SOURCE`, `API_PROJECT`, `path.stem` date, `UTC`,
and `endpoint_url(date.fromisoformat(path.stem))`. Require an ISO string
`collected_at` with an aware UTC offset, without comparing it to the ranking
date. Require a nonempty articles list of objects, unique nonempty string names,
`type(views) is int and views >= 0`, and `type(rank) is int and rank > 0`.
Do not require distinct or consecutive ranks. Errors identify path and field;
do not print source contents. A small direct guard pattern is sufficient:

```python
if not isinstance(payload, dict):
    raise ValueError(f"{path}: snapshot must be an object")
for key, expected in {
    "source": SOURCE, "project": API_PROJECT,
    "snapshot_date": path.stem, "time_zone": "UTC",
    "request_url": endpoint_url(date.fromisoformat(path.stem)),
}.items():
    if payload.get(key) != expected:
        raise ValueError(f"{path}: {key} mismatch")
```

- [ ] **4. Implement the projection and atomic JSON output.**

The ranking core is deliberately small; retain integer views from the original
rows rather than producing an average through the historical aggregate function:

```python
EXCLUDED_PREFIXES = ("위키백과:", "특수:", "파일:")
META_KEYS = ("source", "project", "snapshot_date", "time_zone",
             "collected_at", "request_url")


def build_result(snapshot: dict) -> dict:
    # ponytail: exact Wikimedia prefixes only; extend on observed namespace noise.
    rows = {r["article"]: r for r in snapshot["articles"]
            if not r["article"].startswith(EXCLUDED_PREFIXES)}
    ranked = rank_prominent({name: r["views"] for name, r in rows.items()}, top_n=20)
    return {
        **{key: snapshot[key] for key in META_KEYS}, "ranking": "daily_views",
        "items": [{"rank": i, "source_rank": rows[name]["rank"],
                   "page": name, "views": rows[name]["views"]}
                  for i, (name, _) in enumerate(ranked, 1)],
    }


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
```

Use standard-library imports and the existing helpers identified in File map.
Do not extract the collector's inline writer into a shared framework just for
reuse. Serialize with `ensure_ascii=False, indent=2, sort_keys=True` and a final
newline. No generated-at timestamp; preserve input collection time instead.

Wire argparse and `main(argv=None)` with the declared flags; pass
`datetime.now(timezone.utc).date()` to `select_snapshot`. Catch `ValueError`,
`OSError`, and `UnicodeError` at the CLI boundary, print a concise error to stderr,
and return 1. Successful generation returns 0. Use `raise SystemExit(main())`
under the module's main guard. Input validation must finish before output writes.

- [ ] **5. Run the focused check, add the documented command, and commit Task 1.**

```bash
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run pytest -q tests/test_build_wikimedia_page.py
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run python -m scripts.build_wikimedia_page --date 2026-08-29
git diff --check
```

The real command requires the retained file; if absent, report that prerequisite
and keep synthetic verification. Do not start a backfill. README must explain
that this is one UTC day's local data and no automatic refresh occurs. Commit
only the named new files, README, and verified plan checkboxes, with message
`feat: generate validated daily Wikimedia keyword JSON`.

**Escalate:** changed raw schema, missing source metadata, or a need to alter the
existing collector/baseline. Do not guess mappings or expand file ownership.

## Task 2 — Static page, safe publication, and local acceptance

**Purpose:** Let the user inspect the actual daily product without a server or
new framework, and preserve an honest old page if regeneration fails.

**Files:** Modify the Task 1 generator/test file, README, experiment log, and this
plan. No other runtime files, dependency files, or generated artifacts in Git.

**Interfaces:** Consumes the validated JSON contract from Task 1. Add
`render_html(result: dict) -> str`; extend `main(argv=None)` to generate
`results.json` and `index.html` in the same output directory. CLI flags unchanged.

- [ ] **1. Add these checks to the same test file, then observe their failure.**

The `stored` helper and imports are defined in Task 1's test file; extend that
file rather than creating another fixture framework.

```python
def test_page_escapes_source_text_and_handles_empty_results():
    result = page.build_result(stored(date(2026, 8, 29), [
        {"article": "<script>_&_주제", "views": 20, "rank": 1},
    ]))
    html = page.render_html(result)
    for label in ["인기 키워드", "한국어 위키백과 조회수 기준", "2026-08-29", "UTC"]:
        assert label in html
    assert "<script>" not in html
    assert "&lt;script&gt; &amp; 주제" in html
    assert "<th" in html
    assert result["items"][0]["page"] == "<script>_&_주제"
    result["items"] = []
    assert "표시할 항목이 없습니다" in page.render_html(result)


def test_build_is_repeatable_and_failure_preserves_page(tmp_path, monkeypatch):
    root, out = tmp_path / "raw", tmp_path / "out"
    root.mkdir()
    raw = root / "2026-08-29.json"
    raw.write_text(json.dumps(stored(date(2026, 8, 29), [
        {"article": "가_주제", "views": 20, "rank": 1},
    ])), encoding="utf-8")
    args = ["--data-root", str(root), "--date", "2026-08-29", "--output-dir", str(out)]
    assert page.main(args) == 0
    files = [out / "results.json", out / "index.html"]
    accepted = [p.read_bytes() for p in files]
    assert page.main(args) == 0
    assert [p.read_bytes() for p in files] == accepted
    real_replace = page.os.replace

    def reject_html(source, destination):
        if destination == files[1]:
            raise OSError("simulated publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(page.os, "replace", reject_html)
    assert page.main(args) != 0
    assert files[1].read_bytes() == accepted[1]
    assert sorted(p.name for p in out.iterdir()) == ["index.html", "results.json"]
    raw.write_text("invalid", encoding="utf-8")
    assert page.main(args) != 0
    assert [p.read_bytes() for p in files] == accepted
```

Run the focused pytest command from Task 1. Missing `render_html` or missing
`index.html` is the expected initial failure; do not manufacture unrelated bugs.

- [ ] **2. Render the result and publish HTML last.**

Use `html.escape` for every dynamic string. Render semantic HTML with
`lang="ko"`, UTF-8, viewport metadata, a heading, date explanation, and a table
with column headers `순위`, `키워드`, `조회수`. Plain readable spacing is enough;
no design-system work or interactive sorting. Render numbers with thousands
separators. The rows can be built directly:

```python
rows = "".join(
    f'<tr><td>{item["rank"]}</td>'
    f'<td>{escape(item["page"].replace("_", " "))}</td>'
    f'<td>{item["views"]:,}</td></tr>'
    for item in result["items"]
)
```

For no rows, display `표시할 항목이 없습니다` with the same source/date labels.
No links, raw HTML insertion, browser fetch, or external assets. A document
string with minimal inline CSS is sufficient; no separate template dependency.

Inside `main`, after validation and projection, perform the following sequence:

```python
json_text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
html_text = render_html(json.loads(json_text))
write_atomic(output_dir / "results.json", json_text)
write_atomic(output_dir / "index.html", html_text)
```

Both strings exist before replacing any output; the page contains its own
values, so a newer JSON beside older HTML after interrupted publication cannot
change the old page's meaning. Do not add a two-file transaction manager. Print
the selected data date and the generated output paths on success.

- [ ] **3. Verify focused behavior and replay three actual retained days.**

Run the focused test first. Then generate the latest available snapshot and
two explicit historical snapshots into separate ignored directories:

```bash
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run python -m scripts.build_wikimedia_page --output-dir artifacts/wikimedia_phase2/latest
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run python -m scripts.build_wikimedia_page --date 2026-08-28 --output-dir artifacts/wikimedia_phase2/2026-08-28
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run python -m scripts.build_wikimedia_page --date 2026-08-27 --output-dir artifacts/wikimedia_phase2/2026-08-27
```

If these dates are unavailable on the implementer's machine, do not fetch more
data automatically. Record the missing prerequisite; the user can run these
commands where the retained input exists. Do not invent results.

Open each `index.html` in a real browser. On the user's Mac, for example:

```bash
open artifacts/wikimedia_phase2/latest/index.html
```

Confirm the displayed source/date, counts, readable names, and ordering against
that directory's JSON. Record whether browser inspection was actually performed.
Ask the user whether the daily list is understandable and worth browsing; do
not substitute the earlier 30-day judgment. If waiting for the user, report
implementation verification separately and leave phase acceptance pending.

- [ ] **4. Close documentation and the final verification gate.**

README: document the module command, optional date, output paths, opening the
HTML, no server/dependency requirement, UTC and latest-local semantics, and
failure preserving the last good page. Experiment log: append the actual dates,
observable list limitations, repeatability result, browser observation, and
human judgment or its pending status. Never change the historical experiment
numbers or claim a quality threshold passed.

```bash
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv sync --locked
env UV_CACHE_DIR=/tmp/trend-signal-uv-cache uv run pytest -q
git diff --check
git check-ignore data/raw/wikimedia/ko.wikipedia.org/2026-08-29.json artifacts/wikimedia_phase2/latest/index.html
git ls-files data/raw artifacts
git diff --stat
```

Expected: tests pass, diff check passes, ignored paths are reported, tracked raw/
artifact listing is empty. Do not assert test counts in advance. Inspect the
actual diff; update only verified plan checkboxes. Commit the owned files with
message `feat: render the local daily keyword page`. No merge or push.

**Escalate:** the daily list is unintelligible, permissions/source integrity are
uncertain, or improvement would require new ranking, filters, collection, or UI
features. Keep the output and ask; do not tune it to look successful.

## Phase-level handoff

Report base/head commits, changed files, commands with observed results,
artifact locations and actual data dates, browser and human review status,
deviations, and unresolved risks. Separate implemented, tested, observed, and
accepted. Do not leave a polling agent or background server running.

Short prompt for a low-cost external implementer:

```text
Trend Signal Lab의 Phase 2를 구현해줘.
먼저 Git 상태·브랜치·HEAD를 확인하고 기존 변경은 보존해.
AGENTS.md와 docs/superpowers/specs/2026-08-31-phase2-local-popular-keywords-design.md,
docs/superpowers/plans/2026-08-31-phase2-local-popular-keywords.md를 읽어.
계획의 Task 1 → Task 2를 순서대로 구현하고, 검증한 작업별로 커밋해.
새 의존성·수집·배포·알고리즘 튜닝·머지·푸시는 하지 마.
실제 raw 파일이나 브라우저가 없으면 결과를 추정하지 말고 그 한계를 보고해.
최종 보고는 base/head, 변경 파일, 검증 결과, 화면/데이터 경로, 남은 판단만 간결히.
Phase 2 인간 판정은 사용자에게 남겨두고, 완료 후 Codex가 phase diff를 검토할 거야.
```
