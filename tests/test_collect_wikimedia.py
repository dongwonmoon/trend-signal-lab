import json
import sys
from datetime import date, datetime, timezone
from urllib.error import HTTPError

import pytest

import scripts.collect_wikimedia as collector


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
                        {"article": "오징어_게임", "views": 10, "rank": 3},
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

    assert collector.collect_day(DAY, tmp_path, fetcher=fetcher, now=lambda: NOW) == "written"

    target = tmp_path / "ko.wikipedia.org" / "2026-08-29.json"
    stored = json.loads(target.read_text())
    assert stored["project"] == "ko.wikipedia.org"
    assert stored["snapshot_date"] == "2026-08-29"
    assert stored["time_zone"] == "UTC"
    assert stored["collected_at"] == "2026-08-30T01:23:45Z"
    assert stored["articles"][0] == {"article": "리센느", "views": 20, "rank": 1}
    assert stored["articles"][1] == {"article": "오징어_게임", "views": 10, "rank": 3}

    assert collector.collect_day(DAY, tmp_path, fetcher=fetcher, now=lambda: NOW) == "skipped"
    assert calls == 1

    invalid_root = tmp_path / "invalid"
    with pytest.raises(collector.WikimediaCollectionError, match="project"):
        collector.collect_day(
            DAY,
            invalid_root,
            fetcher=lambda _: response(project="wrong.project"),
            now=lambda: NOW,
        )
    assert not (invalid_root / "ko.wikipedia.org" / "2026-08-29.json").exists()

    missing_root = tmp_path / "missing"

    def missing_fetcher(_: date) -> bytes:
        raise HTTPError(collector.endpoint_url(DAY), 404, "Not Found", {}, None)

    assert collector.collect_day(DAY, missing_root, fetcher=missing_fetcher) == "missing"
    assert not missing_root.exists()


def test_main_continues_missing_days_but_rejects_an_all_missing_range(monkeypatch, tmp_path, capsys):
    statuses = {
        date(2026, 7, 28): "written",
        date(2026, 7, 29): "missing",
        date(2026, 7, 30): "written",
    }
    monkeypatch.setattr(collector, "collect_day", lambda day, _: statuses[day])
    monkeypatch.setattr(
        sys,
        "argv",
        ["collect_wikimedia.py", "--start", "2026-07-28", "--end", "2026-07-30", "--output-dir", str(tmp_path)],
    )

    assert collector.main() == 0
    assert capsys.readouterr().out.splitlines() == [
        "2026-07-28 written",
        "2026-07-29 missing",
        "2026-07-30 written",
    ]

    monkeypatch.setattr(collector, "collect_day", lambda *_: "missing")
    monkeypatch.setattr(sys, "argv", ["collect_wikimedia.py", "--start", "2026-07-29"])
    assert collector.main() == 1
    missing_output = capsys.readouterr()
    assert missing_output.out == "2026-07-29 missing\n"
    assert missing_output.err == "error: no Wikimedia data was available for the requested range\n"
