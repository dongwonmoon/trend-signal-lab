from datetime import date
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from scripts.download_e001_data import (
    DATASET_FILENAME,
    DATASET_SLUG,
    DATASET_VERSION,
    ChecksumMismatchError,
    DatasetArchiveError,
    download_dataset,
    sha256_file,
)
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


def test_load_snapshots_rejects_wrong_single_csv_by_default(tmp_path):
    archive_path = tmp_path / "wrong-member.zip"
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        archive.write(FIXTURE, "wrong.csv")

    with pytest.raises(ValueError, match="KR_youtube_trending_data.csv"):
        load_snapshots(archive_path)

    assert load_snapshots(archive_path, csv_name="wrong.csv") == load_snapshots(FIXTURE)


def test_load_snapshots_parses_kaggle_iso_dates(tmp_path):
    source = tmp_path / "iso-date.csv"
    source.write_text(
        "video_id,title,categoryId,trending_date\nv1,title,1,2021-09-17T00:00:00Z\n",
        encoding="utf-8",
    )

    assert load_snapshots(source)[0].trending_date == date(2021, 9, 17)


def test_downloader_rejects_local_checksum_mismatch(tmp_path):
    output = tmp_path / "download.zip"

    with pytest.raises(ChecksumMismatchError):
        download_dataset(output, source=FIXTURE)

    assert not output.exists()


def test_downloader_rejects_invalid_zip_member(tmp_path):
    source = tmp_path / "wrong-member.zip"
    with ZipFile(source, "w", ZIP_DEFLATED) as archive:
        archive.writestr("wrong.csv", FIXTURE.read_bytes())

    with pytest.raises(DatasetArchiveError, match=DATASET_FILENAME):
        download_dataset(
            tmp_path / "download.zip",
            source=source,
            expected_sha256=sha256_file(source),
        )


def test_downloader_rejects_invalid_zip(tmp_path):
    source = tmp_path / "not-a-zip.zip"
    source.write_bytes(FIXTURE.read_bytes())

    with pytest.raises(DatasetArchiveError, match="valid ZIP"):
        download_dataset(
            tmp_path / "download.zip",
            source=source,
            expected_sha256=sha256_file(source),
        )


def test_downloader_writes_manifest_fields_for_local_archive(tmp_path):
    source = tmp_path / "source.zip"
    with ZipFile(source, "w", ZIP_DEFLATED) as archive:
        archive.writestr(DATASET_FILENAME, FIXTURE.read_bytes())
    output = tmp_path / "download.zip"

    download_dataset(output, source=source, expected_sha256=sha256_file(source))

    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert manifest == {
        "dataset_slug": DATASET_SLUG,
        "dataset_version": DATASET_VERSION,
        "filename": DATASET_FILENAME,
        "url": "https://www.kaggle.com/api/v1/datasets/download/"
        "rsrishav/youtube-trending-video-dataset?datasetVersionNumber=1346",
        "sha256": sha256_file(source),
        "archive": "download.zip",
    }


def test_downloader_preserves_existing_destination_when_validation_fails(tmp_path):
    source = tmp_path / "wrong-member.zip"
    with ZipFile(source, "w", ZIP_DEFLATED) as archive:
        archive.writestr("wrong.csv", FIXTURE.read_bytes())
    output = tmp_path / "download.zip"
    output.write_bytes(b"existing destination")

    with pytest.raises(DatasetArchiveError):
        download_dataset(output, source=source, expected_sha256=sha256_file(source))

    assert output.read_bytes() == b"existing destination"
