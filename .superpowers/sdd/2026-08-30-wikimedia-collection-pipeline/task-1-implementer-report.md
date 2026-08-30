# Task 1 implementation report

## Status

Implemented the minimal Wikimedia daily top-pages collector in
`scripts/collect_wikimedia.py` and its focused test in
`tests/test_collect_wikimedia.py`.

## Implemented contract

- Builds the official `ko.wikipedia.org/all-access/YYYY/MM/DD` endpoint.
- Sends the required identified `User-Agent` and `Accept: application/json`.
- Validates the one-item response, project/access/date, article shape, exact
  integer types, non-negative views, positive contiguous unique ranks, and
  duplicate article names.
- Stores only the approved article fields plus source/date/provenance wrapper.
- Validates before creating the destination directory or file.
- Uses a same-directory temporary file and `os.replace()` for atomic writes;
  temporary files are removed on write/replace failure.
- Skips an existing date file without refetching.
- Rejects naive collection timestamps and formats aware timestamps as UTC `Z`.
- Provides sequential `--start`, optional `--end`, and `--output-dir` CLI flags.

## Verification

- Focused test: `1 passed`.
- Full suite: `24 passed in 30.16s`.
- `git diff --check`: passed.
- `git check-ignore data/raw/wikimedia/ko.wikipedia.org/2026-08-29.json`:
  confirmed ignored.

## Bounded live smoke

The one-day command reached Wikimedia, but the 2024-01-01 response contains
tied ranks (for example multiple rows at rank 29), which violates the brief’s
strict requirement that ranks be exactly `1..N`. The collector raised
`WikimediaCollectionError: ranks must be exactly 1..N` and wrote no output.
No normalization or retry behavior was added; this is an intentional strict
validation boundary and should be resolved by the owning task if real API
payloads are expected to contain ties.

