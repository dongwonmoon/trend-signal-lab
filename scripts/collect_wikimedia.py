import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


API_PROJECT = "ko.wikipedia.org"
RESPONSE_PROJECT = "ko.wikipedia"
ACCESS = "all-access"
SOURCE = "wikimedia_pageviews_top"
USER_AGENT = (
    "trend-signal-lab/0.1 "
    "(https://github.com/dongwonmoon/trend-signal-lab)"
)


class WikimediaCollectionError(ValueError):
    pass


def endpoint_url(day: date) -> str:
    return (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
        f"{API_PROJECT}/{ACCESS}/{day:%Y/%m/%d}"
    )


def fetch_day(day: date) -> bytes:
    request = Request(
        endpoint_url(day),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read()


def _error(message: str) -> WikimediaCollectionError:
    return WikimediaCollectionError(message)


def validate_response(raw: bytes, requested_day: date) -> list[dict[str, object]]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error("invalid JSON response") from exc
    if not isinstance(payload, dict):
        raise _error("response must be an object")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 1:
        raise _error("items must be a one-element list")
    item = items[0]
    if not isinstance(item, dict):
        raise _error("item must be an object")
    if item.get("project") != RESPONSE_PROJECT:
        raise _error("project does not match")
    if item.get("access") != ACCESS:
        raise _error("access does not match")
    expected = {"year": f"{requested_day.year:04d}", "month": f"{requested_day.month:02d}", "day": f"{requested_day.day:02d}"}
    for field, value in expected.items():
        if item.get(field) != value:
            raise _error(f"{field} does not match requested day")
    articles = item.get("articles")
    if not isinstance(articles, list) or not articles:
        raise _error("articles must be a non-empty list")
    result: list[dict[str, object]] = []
    names: set[str] = set()
    for article in articles:
        if not isinstance(article, dict):
            raise _error("article entry must be an object")
        name = article.get("article")
        views = article.get("views")
        rank = article.get("rank")
        if not isinstance(name, str) or not name:
            raise _error("article must be a non-empty string")
        if type(views) is not int or views < 0:
            raise _error("views must be a non-negative integer")
        if type(rank) is not int or rank <= 0:
            raise _error("rank must be a positive integer")
        if name in names:
            raise _error("article names repeat")
        names.add(name)
        result.append({"article": name, "views": views, "rank": rank})
    return sorted(result, key=lambda entry: entry["rank"])


def _collected_at(now: Callable[[], datetime]) -> str:
    value = now()
    if value.tzinfo is None or value.utcoffset() is None:
        raise WikimediaCollectionError("now() must return an aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def collect_day(
    day: date,
    output_root: Path,
    *,
    fetcher: Callable[[date], bytes] = fetch_day,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> str:
    target = output_root / API_PROJECT / f"{day.isoformat()}.json"
    if target.exists():
        return "skipped"
    try:
        raw = fetcher(day)
    except HTTPError as exc:
        if exc.code == 404:
            return "missing"
        raise
    articles = validate_response(raw, day)
    stored = {
        "source": SOURCE,
        "project": API_PROJECT,
        "snapshot_date": day.isoformat(),
        "time_zone": "UTC",
        "collected_at": _collected_at(now),
        "request_url": endpoint_url(day),
        "articles": articles,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False
        ) as handle:
            temporary = handle.name
            json.dump(stored, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, target)
    except Exception:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        raise
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end")
    parser.add_argument("--output-dir", default="data/raw/wikimedia")
    args = parser.parse_args()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end) if args.end else start
    if end < start:
        parser.error("--end must not be before --start")
    current = start
    available = 0
    while current <= end:
        status = collect_day(current, Path(args.output_dir))
        print(f"{current.isoformat()} {status}")
        if status != "missing":
            available += 1
        current = date.fromordinal(current.toordinal() + 1)
    if available == 0:
        print("error: no Wikimedia data was available for the requested range", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
