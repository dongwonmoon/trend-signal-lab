from datetime import date
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from trend_signal_lab.dataset import (
    InvalidDateError,
    MissingColumnsError,
    load_snapshots,
)


FIXTURE = Path(__file__).parent / "fixtures" / "youtube_trending_tiny.csv"


def test_load_snapshots_filters_scope_and_preserves_cross_day_persistence():
    snapshots = load_snapshots(FIXTURE)

    assert [(snapshot.video_id, snapshot.trending_date) for snapshot in snapshots] == [
        ("v-current", date(2021, 9, 17)),
        ("v-current", date(2021, 9, 18)),
        ("v-previous", date(2021, 9, 16)),
        ("v-duplicate", date(2021, 9, 20)),
        ("v-cross-day", date(2021, 9, 17)),
        ("v-cross-day", date(2021, 9, 18)),
    ]


def test_load_snapshots_rejects_missing_required_columns(tmp_path):
    source = tmp_path / "missing.csv"
    source.write_text("video_id,title,categoryId\nv1,title,1\n", encoding="utf-8")

    with pytest.raises(MissingColumnsError, match="trending_date"):
        load_snapshots(source)


def test_load_snapshots_rejects_invalid_dates(tmp_path):
    source = tmp_path / "invalid-date.csv"
    source.write_text(
        "video_id,title,categoryId,trending_date\nv1,title,1,not-a-date\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidDateError, match="not-a-date"):
        load_snapshots(source)


def test_load_snapshots_has_csv_and_zip_parity(tmp_path):
    archive_path = tmp_path / "youtube-data.zip"
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        archive.write(FIXTURE, "KR_youtube_trending_data.csv")
        archive.writestr("unrelated.csv", "not,the,dataset\n")

    assert load_snapshots(archive_path) == load_snapshots(FIXTURE)


def test_load_snapshots_parses_kaggle_iso_dates(tmp_path):
    source = tmp_path / "iso-date.csv"
    source.write_text(
        "video_id,title,categoryId,trending_date\nv1,title,1,2021-09-17T00:00:00Z\n",
        encoding="utf-8",
    )

    assert load_snapshots(source)[0].trending_date == date(2021, 9, 17)
