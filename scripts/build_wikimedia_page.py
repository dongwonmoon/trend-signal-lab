"""Phase 2: validated daily popular-keyword JSON generator.

Selects one retained completed UTC day, validates the stored Wikimedia
snapshot, projects a daily-views ranking, and writes it atomically. No
network access, no 30-day aggregation, and no growth score.
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from scripts.collect_wikimedia import API_PROJECT, SOURCE, endpoint_url
from scripts.run_wikimedia_baseline import rank_prominent

EXCLUDED_PREFIXES = ("위키백과:", "특수:", "파일:")
META_KEYS = (
    "source",
    "project",
    "snapshot_date",
    "time_zone",
    "collected_at",
    "request_url",
)


def select_snapshot(
    data_root: Path, requested: date | None, *, today: date
) -> Path:
    if requested is not None:
        if requested >= today:
            raise ValueError(f"requested date {requested} is not a completed UTC day")
        target = data_root / f"{requested.isoformat()}.json"
        if not target.exists():
            raise FileNotFoundError(f"no snapshot for {requested}")
        return target
    candidates: list[Path] = []
    for path in data_root.glob("*.json"):
        try:
            day = date.fromisoformat(path.stem)
        except ValueError:
            raise ValueError(f"{path}: filename is not a canonical date") from None
        if day < today:
            candidates.append(path)
    if not candidates:
        raise FileNotFoundError("no retained snapshot before the current UTC date")
    return max(candidates, key=lambda path: date.fromisoformat(path.stem))


def load_snapshot(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: snapshot is not UTF-8 text") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: snapshot must be an object")
    for key, expected in {
        "source": SOURCE,
        "project": API_PROJECT,
        "snapshot_date": path.stem,
        "time_zone": "UTC",
        "request_url": endpoint_url(date.fromisoformat(path.stem)),
    }.items():
        if payload.get(key) != expected:
            raise ValueError(f"{path}: {key} mismatch")
    collected_at = payload.get("collected_at")
    if not isinstance(collected_at, str):
        raise ValueError(f"{path}: collected_at must be an ISO string")
    try:
        stamp = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path}: collected_at is not an ISO string") from exc
    if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
        raise ValueError(f"{path}: collected_at must be an aware UTC offset")
    articles = payload.get("articles")
    if not isinstance(articles, list) or not articles:
        raise ValueError(f"{path}: articles must be a non-empty list")
    names: set[str] = set()
    for article in articles:
        if not isinstance(article, dict):
            raise ValueError(f"{path}: article entry must be an object")
        name = article.get("article")
        views = article.get("views")
        rank = article.get("rank")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{path}: article must be a non-empty string")
        if name in names:
            raise ValueError(f"{path}: article names repeat")
        names.add(name)
        if type(views) is not int or views < 0:
            raise ValueError(f"{path}: views must be a non-negative integer")
        if type(rank) is not int or rank <= 0:
            raise ValueError(f"{path}: rank must be a positive integer")
    return payload


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_result(snapshot: dict) -> dict:
    # ponytail: exact Wikimedia prefixes only; extend on observed namespace noise.
    rows = {
        r["article"]: r
        for r in snapshot["articles"]
        if not r["article"].startswith(EXCLUDED_PREFIXES)
    }
    ranked = rank_prominent(
        {name: r["views"] for name, r in rows.items()}, top_n=20
    )
    return {
        **{key: snapshot[key] for key in META_KEYS},
        "ranking": "daily_views",
        "items": [
            {
                "rank": i,
                "source_rank": rows[name]["rank"],
                "page": name,
                "views": rows[name]["views"],
            }
            for i, (name, _) in enumerate(ranked, 1)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/raw/wikimedia/ko.wikipedia.org")
    parser.add_argument("--date")
    parser.add_argument("--output-dir", default="artifacts/wikimedia_phase2")
    args = parser.parse_args(argv)

    requested = None
    if args.date:
        try:
            requested = date.fromisoformat(args.date)
        except ValueError:
            print(f"error: --date must be YYYY-MM-DD, got {args.date!r}", file=sys.stderr)
            return 1
    try:
        path = select_snapshot(
            Path(args.data_root), requested, today=datetime.now(timezone.utc).date()
        )
        result = build_result(load_snapshot(path))
        json_text = (
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
        write_atomic(Path(args.output_dir) / "results.json", json_text)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {Path(args.output_dir) / 'results.json'} for {result['snapshot_date']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
