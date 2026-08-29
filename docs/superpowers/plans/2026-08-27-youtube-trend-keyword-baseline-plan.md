# E001 YouTube Trend Keyword Baseline Implementation Plan

> **For Codex:** Use a Luna subagent for the bounded implementation, then verify the real result. Ponytail full applies: keep only the code and checks needed to answer E001.

**Goal:** Reproduce two deterministic top-20 Korean cultural candidate rankings from a fixed historical Korean YouTube trending dataset, then generate reviewable local Markdown and JSON results without committing the raw dataset.

**Architecture:** The existing dataset boundary validates the fixed input. One experiment script contains candidate extraction, the two rankings, and Markdown/JSON rendering. One small test file protects the non-trivial scoring and phrase behavior. Raw data and generated reports remain ignored.

**Tech Stack:** Python 3.12+, `uv`, `kiwipiepy==0.23.2`, `pytest`; standard-library CSV, ZIP, JSON, datetime, hashlib, urllib, argparse.

---

## Task 1: Reproducible dataset boundary

**Files:**

- Modify: `.gitignore`
- Create: `pyproject.toml`
- Create: `uv.lock`
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

## Task 2: Minimal ranking experiment and result artifact

**Files:**

- Create: `scripts/run_e001.py`
- Create: `tests/test_e001.py`
- Create: `docs/experiment-log.md`
- Modify: `README.md`

**Behavior contract:**

- One script performs NFKC normalization, Kiwi tokenization, consecutive 1–3-gram extraction, per-snapshot uniqueness, equal-support phrase preference, Ranking A, Ranking B, deterministic ordering, and Markdown/JSON rendering.
- One small test file protects readable `오징어 게임` extraction, punctuation boundaries, daily persistence counting, the fixed smoothed formula/minimum support, and deterministic output.
- The fixed CLI writes ignored `artifacts/e001/results.json` and `artifacts/e001/results.md` with both top-20 tables, counts, parameters, source manifest, and up to three evidence rows.
- The committed experiment log records only provenance, parameters, technical execution facts, anchor presence, and that the final usefulness labels await the user's review.

**Implementation sequence:**

1. Implement the single script and one compact test file; do not add abstractions for hypothetical experiments.
2. Run `uv run pytest -q`.
3. Run `uv run python scripts/run_e001.py --input data/raw/kr_youtube_trending_data.zip --output-dir artifacts/e001` and inspect both generated files.
4. Update README and experiment log from the actual run, without declaring the human usefulness threshold passed.
5. Run the CLI twice to separate ignored directories and compare file hashes.
6. Commit the task.

## Task 3: Whole-experiment verification and handoff

**Files:**

- Modify only files required by findings from independent review.

**Verification:**

1. Inspect the whole diff against the approved design, especially snapshot-vs-video counting, temporal leakage, phrase extraction, raw-data Git safety, and unsupported success claims.
2. Run `uv sync --locked`, `uv run pytest -q`, `git check-ignore data/raw/kr_youtube_trending_data.zip`, and the fixed E001 CLI.
3. Compare SHA-256 of two independently generated result JSON and Markdown files.
4. Inspect `git status --short` and `git diff --check`; confirm no raw dataset, secret, or large generated artifact is tracked.
5. Present both top-20 tables to the user for the preregistered three-way labeling. The experiment remains technically executed but product verdict pending until that review is complete.
