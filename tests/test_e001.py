from datetime import date
from math import log2

import pytest

from scripts.run_e001 import (
    CHANGE_RANKING,
    CURRENT_RANKING,
    collect_supports,
    extract_candidates,
    rank_candidates,
)
from trend_signal_lab.dataset import Snapshot


def test_extracts_korean_phrase_and_breaks_at_punctuation():
    assert "오징어 게임" in extract_candidates("오징어 게임 공식 예고편")
    assert "오징어 게임" not in extract_candidates("오징어, 게임 공식 예고편")


def test_preserves_surface_spans_for_compound_nouns_and_keeps_boundaries():
    candidates = extract_candidates("김부장 미니앨범 오징어 게임")
    assert "김부장" in candidates
    assert "미니앨범" in candidates
    assert "오징어 게임" in candidates
    assert "김 부장" not in candidates
    assert "오징어 게임" not in extract_candidates("오징어, 게임")


def test_candidate_ranking_counts_each_daily_snapshot_once():
    supports = {
        "지속 후보": {
            "current": {("video-1", date(2021, 9, 17)), ("video-1", date(2021, 9, 18))},
            "previous": set(),
            "videos": {"video-1"},
        }
    }
    result = rank_candidates(
        supports, current_total=2, previous_total=1, mode=CURRENT_RANKING, min_support=1
    )
    assert result[0]["current_snapshot_df"] == 2
    assert result[0]["current_share"] == 1.0
    assert result[0]["video_count"] == 1


def test_equal_support_prefers_longer_phrase():
    snapshots = [
        Snapshot("v1", "오징어 게임, BTS", 10, date(2021, 9, 17)),
        Snapshot("v2", "오징어 게임, BTS", 10, date(2021, 9, 18)),
    ]
    supports = collect_supports(snapshots)
    assert "오징어 게임" in supports
    assert "오징어" not in supports
    assert "bts" in supports


def test_evidence_shows_current_window_before_previous_window():
    supports = collect_supports(
        [
            Snapshot("old", "오징어 게임", 10, date(2021, 8, 18)),
            Snapshot("new", "오징어 게임", 10, date(2021, 9, 17)),
        ]
    )
    assert supports["오징어 게임"]["evidence"][0].video_id == "new"


def test_change_ranking_uses_fixed_smoothing_and_minimum_support():
    supports = {
        "지원 후보": {
            "current": {f"c{i}" for i in range(5)},
            "previous": {"p0"},
            "videos": {"v0"},
        },
        "희귀 후보": {
            "current": {"c0", "c1", "c2", "c3"},
            "previous": set(),
            "videos": {"v1"},
        },
    }
    result = rank_candidates(supports, current_total=10, previous_total=10, mode=CHANGE_RANKING)
    assert [row["candidate"] for row in result] == ["지원 후보"]
    assert result[0]["change_score"] == pytest.approx(log2(11 / 3))


def test_rank_and_render_order_are_deterministic():
    supports = {
        "나": {"current": {"a"}, "previous": set(), "videos": {"v1"}},
        "가": {"current": {"b"}, "previous": set(), "videos": {"v2"}},
    }
    first = rank_candidates(
        supports, current_total=1, previous_total=1, mode=CURRENT_RANKING, min_support=1
    )
    second = rank_candidates(
        dict(reversed(list(supports.items()))),
        current_total=1,
        previous_total=1,
        mode=CURRENT_RANKING,
        min_support=1,
    )
    assert first == second
    assert [row["candidate"] for row in first] == ["가", "나"]
