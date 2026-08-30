from datetime import date

import pytest

from scripts.run_wikimedia_baseline import (
    aggregate,
    rank_increased,
    rank_prominent,
    split_windows,
)

DAY = date.fromisoformat


def _article(name: str, views: int) -> dict[str, object]:
    return {"article": name, "views": views, "rank": 1}


def test_split_windows_two_30_day_halves():
    days = list(
        map(
            DAY,
            [f"2026-07-{d:02d}" for d in range(1, 31)]
            + [f"2026-08-{d:02d}" for d in range(1, 31)],
        )
    )
    prev, cur = split_windows(days)
    assert len(prev) == 30 and len(cur) == 30
    assert prev[-1] == DAY("2026-07-30")
    assert cur[0] == DAY("2026-08-01")


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
