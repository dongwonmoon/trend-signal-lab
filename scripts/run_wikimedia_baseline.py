"""Phase 1: accept the Wikimedia signal.

Source-local baseline derived from the retained daily Wikipedia top-page
files. Views participate; the earlier document-frequency ranking is not
reused. The latest 60 consecutive retained dates form two adjacent 30-day
windows: first half is previous, second half is current.
"""

import argparse
import json
from datetime import date, timedelta
from math import log2
from pathlib import Path

WINDOW_DAYS = 30
TOP_N = 20
PSEUDO_COUNT = 1.0
PROJECT = "ko.wikipedia.org"


def load_days(data_root: Path) -> dict[date, list[dict[str, object]]]:
    days: dict[date, list[dict[str, object]]] = {}
    for path in sorted(data_root.glob("*.json")):
        if not path.is_file():
            continue
        day = date.fromisoformat(path.stem)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("project") != PROJECT:
            raise ValueError(f"{path}: project mismatch")
        if payload.get("snapshot_date") != path.stem:
            raise ValueError(f"{path}: snapshot_date mismatch")
        articles = payload.get("articles")
        if not isinstance(articles, list) or not articles:
            raise ValueError(f"{path}: empty article list")
        for article in articles:
            views = article.get("views")
            if not isinstance(article.get("article"), str) or not article["article"]:
                raise ValueError(f"{path}: invalid article name")
            if type(views) is not int or views < 0:
                raise ValueError(f"{path}: invalid views")
        days[day] = articles
    if not days:
        raise ValueError("no snapshots found")
    return days


def split_windows(days: list[date]) -> tuple[list[date], list[date]]:
    days = sorted(set(days))
    if len(days) < 2 * WINDOW_DAYS:
        raise ValueError(f"need at least {2 * WINDOW_DAYS} days, got {len(days)}")
    latest = days[-2 * WINDOW_DAYS:]
    if latest[-1] - latest[0] != timedelta(days=2 * WINDOW_DAYS - 1):
        raise ValueError("latest 60 days must be consecutive; missing snapshots")
    return latest[:WINDOW_DAYS], latest[WINDOW_DAYS:]


def aggregate(
    articles_by_day: dict[date, list[dict[str, object]]], window: list[date]
) -> dict[str, float]:
    present = [day for day in window if day in articles_by_day]
    if not present:
        raise ValueError("window contains no data")
    totals: dict[str, int] = {}
    for day in present:
        for article in articles_by_day[day]:
            name = article["article"]  # type: ignore[index]
            totals[name] = totals.get(name, 0) + int(article["views"])  # type: ignore[arg-type]
    return {name: total / len(present) for name, total in totals.items()}


def rank_prominent(
    mean_cur: dict[str, float], top_n: int = TOP_N
) -> list[tuple[str, float]]:
    return sorted(mean_cur.items(), key=lambda pair: (-pair[1], pair[0]))[:top_n]


def rank_increased(
    mean_prev: dict[str, float], mean_cur: dict[str, float], top_n: int = TOP_N
) -> list[tuple[str, float]]:
    names = set(mean_prev) | set(mean_cur)
    changes = {
        name: log2(
            (mean_cur.get(name, 0.0) + PSEUDO_COUNT)
            / (mean_prev.get(name, 0.0) + PSEUDO_COUNT)
        )
        for name in names
    }
    return sorted(
        changes.items(),
        key=lambda pair: (-pair[1], -mean_cur.get(pair[0], 0.0), pair[0]),
    )[:top_n]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/raw/wikimedia/ko.wikipedia.org")
    parser.add_argument("--output-dir", default="artifacts/wikimedia_phase1")
    args = parser.parse_args()

    days = load_days(Path(args.data_root))
    ordered = sorted(days)
    prev, cur = split_windows(ordered)
    mean_prev = aggregate(days, prev)
    mean_cur = aggregate(days, cur)

    def row(
        rank: int, name: str, change: float | None = None
    ) -> dict[str, object]:
        result = {
            "rank": rank,
            "page": name,
            "mean_views_previous": round(mean_prev.get(name, 0.0), 4),
            "mean_views_current": round(mean_cur.get(name, 0.0), 4),
        }
        if change is not None:
            result["change_score"] = round(change, 4)
        return result

    result = {
        "source": "wikimedia_pageviews_top",
        "project": PROJECT,
        "windows": {
            "previous_start": prev[0].isoformat(),
            "previous_end": prev[-1].isoformat(),
            "current_start": cur[0].isoformat(),
            "current_end": cur[-1].isoformat(),
            "window_days": WINDOW_DAYS,
        },
        "counts": {
            "days": len(ordered),
            "previous_days": len(prev),
            "current_days": len(cur),
            "missing_days": [
                (ordered[0] + timedelta(days=n)).isoformat()
                for n in range((ordered[-1] - ordered[0]).days + 1)
                if ordered[0] + timedelta(days=n) not in days
            ],
            "unique_pages": len(set(mean_prev) | set(mean_cur)),
        },
        "rankings": {
            "prominent": [
                row(r, n) for r, (n, _) in enumerate(rank_prominent(mean_cur), 1)
            ],
            "increased": [
                row(r, n, c)
                for r, (n, c) in enumerate(rank_increased(mean_prev, mean_cur), 1)
            ],
        },
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md = ["# Wikimedia Phase 1 baseline\n",
          f"- Project: {PROJECT}\n",
          f"- Previous window: {prev[0]}..{prev[-1]} ({len(prev)} days)\n",
          f"- Current window: {cur[0]}..{cur[-1]} ({len(cur)} days)\n",
          f"- Missing days: {result['counts']['missing_days'] or 'none'}\n",
          "\n## Currently prominent (mean views/day, current window)\n",
          "\n| rank | page | mean views/day |\n|---|---|---|\n"]
    for r in result["rankings"]["prominent"]:
        md.append(f"| {r['rank']} | {r['page']} | {r['mean_views_current']} |\n")
    md.append("\n## Increased attendance (previous -> current)\n\n")
    md.append("| rank | page | mean prev | mean current | log2 change |\n|---|---|---|---|---|\n")
    for r in result["rankings"]["increased"]:
        md.append(
            f"| {r['rank']} | {r['page']} | {r['mean_views_previous']} | "
            f"{r['mean_views_current']} | {r['change_score']} |\n"
        )
    (out / "results.md").write_text("".join(md), encoding="utf-8")
    print(f"wrote {out/'results.json'} and {out/'results.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
