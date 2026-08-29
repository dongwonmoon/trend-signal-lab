#!/usr/bin/env python3
"""Download and verify the fixed E001 YouTube dataset archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DATASET_SLUG = "rsrishav/youtube-trending-video-dataset"
DATASET_VERSION = 1346
DATASET_FILENAME = "KR_youtube_trending_data.csv"
EXPECTED_SHA256 = "cba7ebd0597da96c5dcd933be9469e58a74e148bb4fbb87e535442d8b51f4aa0"
DOWNLOAD_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    f"{DATASET_SLUG}?datasetVersionNumber={DATASET_VERSION}"
)
DEFAULT_OUTPUT = Path("data/raw/kr_youtube_trending_data.zip")


class ChecksumMismatchError(ValueError):
    """Raised when the downloaded archive is not the registered version."""


class DatasetArchiveError(ValueError):
    """Raised when the archive does not contain the registered CSV member."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_archive(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            if DATASET_FILENAME not in archive.namelist():
                raise DatasetArchiveError(
                    f"archive does not contain {DATASET_FILENAME!r}"
                )
    except zipfile.BadZipFile as exc:
        raise DatasetArchiveError(f"not a valid ZIP archive: {path}") from exc


def _copy_or_download(destination: Path, source: Path | None) -> None:
    if source is not None:
        with source.open("rb") as source_stream, destination.open("wb") as destination_stream:
            shutil.copyfileobj(source_stream, destination_stream)
        return

    with urllib.request.urlopen(DOWNLOAD_URL, timeout=120) as response, destination.open(
        "wb"
    ) as destination_stream:
        shutil.copyfileobj(response, destination_stream)


def _manifest_path(archive_path: Path) -> Path:
    return archive_path.with_suffix(".manifest.json")


def download_dataset(
    output: str | Path = DEFAULT_OUTPUT,
    *,
    source: str | Path | None = None,
    expected_sha256: str = EXPECTED_SHA256,
) -> Path:
    """Download or copy, verify, and manifest the registered dataset archive."""

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_path = Path(source) if source is not None else None
    if source_path is not None and not source_path.is_file():
        raise FileNotFoundError(source_path)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        _copy_or_download(temporary_path, source_path)

        actual_sha256 = sha256_file(temporary_path)
        if actual_sha256 != expected_sha256:
            raise ChecksumMismatchError(
                f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
            )
        _validate_archive(temporary_path)
        temporary_path.replace(output_path)
        temporary_path = None

        manifest = {
            "dataset_slug": DATASET_SLUG,
            "dataset_version": DATASET_VERSION,
            "filename": DATASET_FILENAME,
            "url": DOWNLOAD_URL,
            "sha256": actual_sha256,
            "archive": output_path.name,
        }
        _manifest_path(output_path).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return output_path
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"destination ZIP (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="optional local archive to verify and install instead of downloading",
    )
    args = parser.parse_args()
    output = download_dataset(args.output, source=args.source)
    print(f"verified {output} and wrote {_manifest_path(output)}")


if __name__ == "__main__":
    main()
