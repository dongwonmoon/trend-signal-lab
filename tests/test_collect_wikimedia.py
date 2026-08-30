import json
from datetime import date, datetime, timezone

import pytest

from scripts.collect_wikimedia import WikimediaCollectionError, collect_day


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
                        {"article": "오징어_게임", "views": 10, "rank": 1},
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
    assert stored["articles"][1] == {"article": "오징어_게임", "views": 10, "rank": 1}

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
