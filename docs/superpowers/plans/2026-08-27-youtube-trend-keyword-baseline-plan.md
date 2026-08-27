# E001 YouTube Trend Keyword Baseline Implementation Plan

> **For Codex:** Use subagent-driven-development to execute this plan. Every implementation task follows strict TDD: add one behavior test, run it and observe the expected failure, add the smallest implementation, run the focused test, then commit. Use only `gpt-5.6-luna` subagents for implementation and review.

**Goal:** Reproduce two deterministic top-20 Korean cultural candidate rankings from a fixed historical Korean YouTube trending dataset, then generate reviewable local Markdown and JSON results without committing the raw dataset.

**Architecture:** A small `src` package separates dataset snapshots, title candidate extraction, ranking, and report rendering. A thin downloader records the fixed Kaggle version and checksum; a thin experiment CLI composes the pure modules. Raw data and generated reports remain ignored, while the experiment contract, manifest fields, tests, and an outcome summary are committed.

**Tech Stack:** Python 3.12+, `uv`, `kiwipiepy==0.23.2`, `pytest`; standard-library CSV, ZIP, JSON, datetime, hashlib, urllib, argparse.

---

## Task 1: Reproducible dataset boundary

**Files:**

- Modify: `.gitignore`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/trend_signal_lab/__init__.py`
- Create: `src/trend_signal_lab/dataset.py`
- Create: `scripts/download_e001_data.py`
- Create: `tests/fixtures/youtube_trending_tiny.csv`
- Create: `tests/test_dataset.py`

**Behavior contract:**

- Raw data, `.venv`, Python caches, and disposable artifacts cannot be committed accidentally.
- The project installs reproducibly with `uv sync`.
- The dataset reader streams either the CSV or the named CSV inside a ZIP, validates required columns, parses `trending_date`, restricts the two fixed windows and five category IDs, and removes only exact duplicate `(video_id, trending_date)` rows.
- The same video on different dates remains as two snapshots.
- The downloader targets dataset version 1346 and `KR_youtube_trending_data.csv`, refuses a checksum mismatch, and writes a manifest beside the ignored raw file.

**TDD sequence:**

1. Add a literal fixture containing in-range, out-of-range, excluded-category, exact-duplicate, and repeated-on-another-day rows.
2. Write `test_load_snapshots_filters_scope_and_preserves_cross_day_persistence`; run `uv run pytest tests/test_dataset.py::test_load_snapshots_filters_scope_and_preserves_cross_day_persistence -v` and observe import/behavior failure.
3. Implement the smallest streaming loader; rerun the focused test and observe pass.
4. Write and fail tests for missing required columns and invalid dates; add explicit errors; rerun.
5. Write and fail a ZIP parity test using a temporary ZIP around the same fixture; implement ZIP input; rerun.
6. Add the downloader and manifest code without faking the network in unit tests. Exercise it against the already downloaded fixed file during integration, including SHA-256 `cba7ebd0597da96c5dcd933be9469e58a74e148bb4fbb87e535442d8b51f4aa0`.
7. Run `uv run pytest tests/test_dataset.py -v` and `uv run pytest -q`.
8. Commit the task.

## Task 2: Candidate extraction, rankings, and result artifact

**Files:**

- Create: `src/trend_signal_lab/candidates.py`
- Create: `src/trend_signal_lab/ranking.py`
- Create: `src/trend_signal_lab/report.py`
- Create: `scripts/run_e001.py`
- Create: `tests/test_candidates.py`
- Create: `tests/test_ranking.py`
- Create: `tests/test_report.py`
- Create: `docs/experiment-log.md`
- Modify: `README.md`

**Behavior contract:**

- NFKC normalization and Kiwi analysis preserve readable Korean proper/common nouns and foreign terms.
- Candidate generation emits 1–3 consecutive eligible tokens, breaks across ineligible tokens or punctuation, counts a candidate once per snapshot, and favors an equally supported longer phrase over its component.
- Ranking A uses current snapshot document share.
- Ranking B uses the preregistered smoothed log2 share ratio, with current df at least 5.
- Ordering is deterministic: score, current df, longer candidate, lexical order.
- The fixed CLI writes ignored `artifacts/e001/results.json` and `artifacts/e001/results.md` containing both top-20 tables, counts, parameters, source manifest, and up to three evidence rows.
- The committed experiment log records only provenance, parameters, technical execution facts, anchor presence, and that the final usefulness labels await the user's review.

**TDD sequence:**

1. Write `test_extracts_readable_unigrams_and_squid_game_phrase` with hand-written expected candidates; run the focused test and observe import/behavior failure.
2. Implement normalization, Kiwi token selection, and consecutive 1–3-grams; rerun and observe pass.
3. Add failing tests for punctuation boundaries, per-snapshot uniqueness, stopwords, and equal-support phrase subsumption; implement each smallest behavior and rerun after each.
4. Write `test_current_share_counts_daily_persistence` with literal snapshot sets; fail it, implement Ranking A, rerun.
5. Write `test_change_score_uses_fixed_smoothing_and_minimum_support` with hand-calculated values; fail it, implement Ranking B, rerun.
6. Add a deterministic tie-order test and implement the ordering.
7. Write a report test against a tiny in-memory result, asserting parsed JSON fields and semantic Markdown content; fail it, implement renderer, rerun.
8. Add the thin CLI, run `uv run python scripts/run_e001.py --input data/raw/kr_youtube_trending_data.zip --output-dir artifacts/e001`, and inspect both generated files.
9. Update README and experiment log from the actual run, without declaring the human usefulness threshold passed.
10. Run `uv run pytest -q` and rerun the CLI once from a clean artifact directory to verify determinism by file hashes.
11. Commit the task.

## Task 3: Whole-experiment verification and handoff

**Files:**

- Modify only files required by findings from independent review.

**Verification:**

1. Review the whole branch against the approved design, with special attention to snapshot-vs-video counting, temporal leakage, phrase extraction, raw-data Git safety, and unsupported success claims.
2. Run `uv sync --locked`, `uv run pytest -q`, `git check-ignore data/raw/kr_youtube_trending_data.zip`, and the fixed E001 CLI.
3. Compare SHA-256 of two independently generated result JSON and Markdown files.
4. Inspect `git status --short` and `git diff --check`; confirm no raw dataset, secret, or large generated artifact is tracked.
5. Present both top-20 tables to the user for the preregistered three-way labeling. The experiment remains technically executed but product verdict pending until that review is complete.
