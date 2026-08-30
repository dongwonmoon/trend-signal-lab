import json
import sys
from datetime import date, timedelta

import pytest

from scripts.run_wikimedia_baseline import (
    aggregate,
    main,
    rank_prominent,
    split_windows,
)

DAY = date.fromisoformat


def _article(name: str, views: int) -> dict[str, object]:
    return {"article": name, "views": views, "rank": 1}


def test_split_windows_uses_latest_adjacent_30_day_windows():
    days = [DAY("2026-07-01") + timedelta(days=i) for i in range(61)]
    prev, cur = split_windows(days)
    assert len(prev) == 30 and len(cur) == 30
    assert prev[0] == DAY("2026-07-02")
    assert prev[-1] == DAY("2026-07-31")
    assert cur[0] == DAY("2026-08-01")
    assert cur[-1] == DAY("2026-08-30")


def test_split_windows_rejects_a_gap_in_latest_60_days():
    days = [DAY("2026-07-01") + timedelta(days=i) for i in range(61) if i != 30]
    with pytest.raises(ValueError, match="consecutive"):
        split_windows(days)


def test_split_windows_rejects_short_sequences():
    with pytest.raises(ValueError):
        split_windows([DAY("2026-07-01")] * 10)


def test_aggregate_means_over_present_days_only():
    days = {
        DAY("2026-07-01"): [_article("가", 100), _article("나", 10)],
        DAY("2026-07-02"): [_article("가", 200), _article("나", 20)],
    }
    means = aggregate(days, [DAY("2026-07-01"), DAY("2026-07-02")])
    assert means["가"] == 150.0
    assert means["나"] == 15.0


def test_prominent_ranks_by_current_mean_with_name_tiebreak():
    means = {"가": 10.0, "나": 20.0, "다": 20.0}
    assert [name for name, _ in rank_prominent(means)] == ["나", "다", "가"]


def test_prominent_omits_days_missing_from_any_window():
    days = {
        DAY("2026-07-01"): [_article("가", 100)],
        DAY("2026-07-02"): [_article("가", 200)],
    }
    means = aggregate(days, [DAY("2026-07-01"), DAY("2026-07-02")])
    assert means["가"] == 150.0


def test_artifact_omits_unmeasured_change_from_prominence(tmp_path, monkeypatch):
    raw, out = tmp_path / "raw", tmp_path / "out"
    raw.mkdir()
    for i in range(60):
        day = DAY("2026-07-01") + timedelta(days=i)
        payload = {
            "source": "wikimedia_pageviews_top", "project": "ko.wikipedia.org",
            "snapshot_date": day.isoformat(), "time_zone": "UTC",
            "collected_at": "2026-08-30T01:00:00Z",
            "request_url": f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ko.wikipedia.org/all-access/{day:%Y/%m/%d}",
            "articles": [_article("가", 1 if i < 30 else 3)],
        }
        (raw / f"{day}.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["baseline", "--data-root", str(raw), "--output-dir", str(out)])
    assert main() == 0
    rankings = json.loads((out / "results.json").read_text(encoding="utf-8"))["rankings"]
    assert rankings["prominent"][0] == {
        "rank": 1, "page": "가", "mean_views_previous": 1.0, "mean_views_current": 3.0,
    }
    assert rankings["increased"][0]["change_score"] == 1.0
