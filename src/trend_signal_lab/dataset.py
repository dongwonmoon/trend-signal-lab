"""Streaming access to the fixed E001 YouTube trending snapshots."""

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

CURRENT_START = date(2021, 9, 17)
CURRENT_END = date(2021, 10, 16)
PREVIOUS_START = date(2021, 8, 18)
PREVIOUS_END = date(2021, 9, 16)
ALLOWED_CATEGORY_IDS = frozenset({1, 10, 22, 23, 24})
REQUIRED_COLUMNS = frozenset({"video_id", "title", "categoryId", "trending_date"})


class DatasetError(ValueError):
    """Base error for malformed or unsupported dataset input."""


class MissingColumnsError(DatasetError):
    """Raised when the source does not provide the required fields."""


class InvalidDateError(DatasetError):
    """Raised when a source row has an unparseable trending date."""


@dataclass(frozen=True, slots=True)
class Snapshot:
    """One video appearance in one dated trending-list snapshot."""

    video_id: str
    title: str
    category_id: int
    trending_date: date


def _parse_date(value: str) -> date:
    normalized = value.strip()
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%y.%m.%d", "%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid trending_date: {value!r}")


@contextmanager
def _csv_stream(source: Path, csv_name: str | None) -> Iterator[io.TextIOBase]:
    if source.suffix.lower() != ".zip":
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            yield stream
        return

    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        canonical_name = "KR_youtube_trending_data.csv"
        selected = csv_name or canonical_name
        if selected not in names:
            expected = csv_name or canonical_name
            raise DatasetError(f"CSV member not found in ZIP: {expected}")
        with archive.open(selected, "r") as binary_stream:
            with io.TextIOWrapper(binary_stream, encoding="utf-8-sig", newline="") as text_stream:
                yield text_stream


def load_snapshots(
    source: str | Path,
    *,
    csv_name: str | None = None,
    current_start: date = CURRENT_START,
    current_end: date = CURRENT_END,
    previous_start: date = PREVIOUS_START,
    previous_end: date = PREVIOUS_END,
    category_ids: Iterable[int] = ALLOWED_CATEGORY_IDS,
) -> list[Snapshot]:
    """Load in-scope snapshots from a CSV or a ZIP containing a CSV."""

    allowed_categories = frozenset(category_ids)
    snapshots: list[Snapshot] = []
    seen: set[tuple[str, date]] = set()
    path = Path(source)

    with _csv_stream(path, csv_name) as stream:
        reader = csv.DictReader(stream)
        fieldnames = frozenset(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise MissingColumnsError(f"missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            try:
                trending_date = _parse_date(row["trending_date"])
            except ValueError as exc:
                raise InvalidDateError(
                    f"invalid trending_date on CSV row {row_number}: {row['trending_date']!r}"
                ) from exc
            if not (
                previous_start <= trending_date <= previous_end
                or current_start <= trending_date <= current_end
            ):
                continue
            category_id = int(row["categoryId"])
            if category_id not in allowed_categories:
                continue
            video_id = row["video_id"]
            key = (video_id, trending_date)
            if key in seen:
                continue
            seen.add(key)
            snapshots.append(
                Snapshot(
                    video_id=video_id,
                    title=row["title"],
                    category_id=category_id,
                    trending_date=trending_date,
                )
            )

    return snapshots
