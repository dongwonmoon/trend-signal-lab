#!/usr/bin/env python3
"""Backfill SBS entertainment title metadata and run source-local Ranking B."""

from __future__ import annotations

import argparse
import json
import math
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

if __package__:
    from scripts.run_e001 import MIN_SUPPORT, SMOOTHING, extract_candidates, normalize_title
else:
    from run_e001 import MIN_SUPPORT, SMOOTHING, extract_candidates, normalize_title


SECTION_TYPE = 14
BASE_URL = "https://news.sbs.co.kr/news/newsSection.do"
KST = ZoneInfo("Asia/Seoul")
PAGE_RE = re.compile(r"pageIdx=(\d+)", re.IGNORECASE)
NEWS_ID_RE = re.compile(r"[?&]news_id=([A-Za-z0-9_-]+)", re.IGNORECASE)
VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"})


class SBSFetchError(RuntimeError):
    """The SBS archive could not be fetched."""


class SBSParseError(RuntimeError):
    """The SBS archive no longer matches the observed metadata contract."""


def window_dates(end_date: date) -> dict[str, date]:
    current_start = end_date - timedelta(days=29)
    previous_end = current_start - timedelta(days=1)
    return {
        "current_start": current_start,
        "current_end": end_date,
        "previous_start": previous_end - timedelta(days=29),
        "previous_end": previous_end,
    }


def build_page_url(day: date, page_idx: int) -> str:
    query = urllib.parse.urlencode(
        {
            "pageDate": day.strftime("%Y%m%d"),
            "pageIdx": page_idx,
            "sectionType": SECTION_TYPE,
        }
    )
    return f"{BASE_URL}?{query}"


class _SectionPageParser(HTMLParser):
    """Read only Schema.org metadata inside the latest-news list."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.list_depth: int | None = None
        self.item_depth: int | None = None
        self.saw_list = False
        self.current: dict[str, str] | None = None
        self.articles: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in VOID_TAGS:
            self.depth += 1
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if (
            tag == "div"
            and self.list_depth is None
            and {"w_news_list", "type_issue2"}.issubset(classes)
        ):
            self.list_depth = self.depth
            self.saw_list = True
            return

        if self.list_depth is None:
            return
        if tag == "li" and self.current is None:
            self.item_depth = self.depth
            self.current = {}
            return
        if self.current is None:
            return

        itemprop = attributes.get("itemprop")
        if tag == "meta" and itemprop == "headline" and attributes.get("content"):
            self.current["title"] = normalize_title(attributes["content"] or "")
        elif tag == "meta" and itemprop == "datePublished" and attributes.get("content"):
            self.current["published_at"] = attributes["content"] or ""
        elif tag == "link" and itemprop == "url" and attributes.get("href"):
            self.current["link"] = urllib.parse.urljoin(BASE_URL, attributes["href"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "li" and self.current is not None and self.depth == self.item_depth:
            self._finish_item()
        if self.list_depth is not None and self.depth == self.list_depth:
            self.list_depth = None
        self.depth -= 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.depth -= 1

    def _finish_item(self) -> None:
        assert self.current is not None
        required = {"title", "published_at", "link"}
        if not required.issubset(self.current):
            missing = ", ".join(sorted(required.difference(self.current)))
            raise SBSParseError(f"SBS article metadata is missing: {missing}")
        match = NEWS_ID_RE.search(self.current["link"])
        if not match:
            raise SBSParseError("SBS article URL has no news_id")
        try:
            published = datetime.fromisoformat(self.current["published_at"])
        except ValueError as exc:
            raise SBSParseError("SBS article has an invalid datePublished value") from exc
        if published.tzinfo is None:
            raise SBSParseError("SBS article datePublished has no timezone")
        self.current["published_at"] = published.isoformat()
        self.current["news_id"] = match.group(1)
        self.articles.append(self.current)
        self.current = None
        self.item_depth = None


def parse_sbs_page(html: str) -> list[dict[str, str]]:
    parser = _SectionPageParser()
    parser.feed(html)
    parser.close()
    if not parser.saw_list:
        raise SBSParseError("SBS latest-news list was not found")
    return parser.articles


def page_count(html: str) -> int:
    count = max((int(value) for value in PAGE_RE.findall(html)), default=1)
    if count > 100:
        raise SBSParseError(f"implausible SBS page count: {count}")
    return count


def fetch_page(url: str, timeout: float = 30.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "trend-signal-lab/0.1 SBS-metadata-research"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise SBSFetchError(f"SBS returned HTTP {response.status}: {url}")
            return response.read().decode("utf-8")
    except SBSFetchError:
        raise
    except Exception as exc:
        raise SBSFetchError(f"failed to fetch SBS section page: {url}") from exc


def dedupe_articles(articles: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for article in articles:
        by_id.setdefault(article["news_id"], dict(article))
    return sorted(by_id.values(), key=lambda item: (item["published_at"], item["news_id"]))


def crawl_day(
    day: date,
    *,
    fetcher: Callable[[str], str] = fetch_page,
) -> tuple[list[dict[str, str]], int]:
    first_url = build_page_url(day, 1)
    first_html = fetcher(first_url)
    pages = page_count(first_html)
    articles = parse_sbs_page(first_html)
    for page_idx in range(2, pages + 1):
        url = build_page_url(day, page_idx)
        page_articles = parse_sbs_page(fetcher(url))
        if not page_articles:
            raise SBSParseError(f"advertised SBS page is empty: {url}")
        articles.extend(page_articles)

    exact_day = [
        article
        for article in articles
        if datetime.fromisoformat(article["published_at"]).astimezone(KST).date() == day
    ]
    return dedupe_articles(exact_day), pages


def collect_historical(
    end_date: date,
    *,
    fetcher: Callable[[str], str] = fetch_page,
) -> tuple[list[dict[str, str]], dict[str, date], dict[str, int]]:
    windows = window_dates(end_date)
    day = windows["previous_start"]
    rows: list[dict[str, str]] = []
    pages_fetched = 0
    empty_days = 0
    while day <= windows["current_end"]:
        day_rows, page_total = crawl_day(day, fetcher=fetcher)
        rows.extend(day_rows)
        pages_fetched += page_total
        empty_days += not day_rows
        day += timedelta(days=1)
    articles = dedupe_articles(rows)
    if not articles:
        raise SBSParseError("SBS historical collection returned no articles")
    return articles, windows, {"pages_fetched": pages_fetched, "empty_days": empty_days}


def _article_date(article: Mapping[str, str]) -> date:
    return datetime.fromisoformat(article["published_at"]).astimezone(KST).date()


def _prefer_longer_phrases(
    supports: Mapping[str, Mapping[str, set[str]]],
) -> dict[str, Mapping[str, set[str]]]:
    retained: dict[str, Mapping[str, set[str]]] = {}
    for term in sorted(supports, key=lambda value: (-len(value), value)):
        support = supports[term]
        if any(
            len(longer) > len(term)
            and term in longer
            and supports[longer]["current"] == support["current"]
            and supports[longer]["previous"] == support["previous"]
            for longer in supports
        ):
            continue
        retained[term] = support
    return retained


def rank_sbs_articles(
    articles: Sequence[Mapping[str, str]],
    windows: Mapping[str, date],
    *,
    min_support: int = MIN_SUPPORT,
) -> tuple[list[dict], int]:
    unique_articles = dedupe_articles(articles)
    current = [
        item
        for item in unique_articles
        if windows["current_start"] <= _article_date(item) <= windows["current_end"]
    ]
    previous = [
        item
        for item in unique_articles
        if windows["previous_start"] <= _article_date(item) <= windows["previous_end"]
    ]
    if not current or not previous:
        raise ValueError("both SBS comparison windows must contain articles")

    supports: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"current": set(), "previous": set()}
    )
    by_id = {item["news_id"]: item for item in unique_articles}
    for article in unique_articles:
        article_day = _article_date(article)
        if windows["current_start"] <= article_day <= windows["current_end"]:
            period = "current"
        elif windows["previous_start"] <= article_day <= windows["previous_end"]:
            period = "previous"
        else:
            continue
        for candidate in extract_candidates(article["title"]):
            supports[candidate][period].add(article["news_id"])

    preferred = _prefer_longer_phrases(supports)
    rows: list[dict] = []
    for candidate, support in preferred.items():
        current_df = len(support["current"])
        if current_df < min_support:
            continue
        previous_df = len(support["previous"])
        change_score = math.log2(
            ((current_df + SMOOTHING) / (len(current) + 1))
            / ((previous_df + SMOOTHING) / (len(previous) + 1))
        )
        evidence_ids = sorted(
            support["current"] | support["previous"],
            key=lambda news_id: (
                not (
                    windows["current_start"]
                    <= _article_date(by_id[news_id])
                    <= windows["current_end"]
                ),
                by_id[news_id]["published_at"],
                news_id,
            ),
        )[:3]
        rows.append(
            {
                "candidate": candidate,
                "current_article_df": current_df,
                "current_share": current_df / len(current),
                "previous_article_df": previous_df,
                "previous_share": previous_df / len(previous),
                "change_score": change_score,
                "article_count": len(support["current"] | support["previous"]),
                "evidence": [by_id[news_id] for news_id in evidence_ids],
            }
        )
    rows.sort(
        key=lambda row: (
            -row["change_score"],
            -row["current_article_df"],
            -len(row["candidate"]),
            row["candidate"],
        )
    )
    for rank, row in enumerate(rows[:20], start=1):
        row["rank"] = rank
    return rows[:20], len(preferred)


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result: Mapping) -> str:
    params = result["parameters"]
    lines = [
        "# E002 SBS entertainment metadata baseline",
        "",
        "Source-local Ranking B; SBS editorial selection is not a culture-wide gold label.",
        "",
        "## Parameters",
        "",
        f"- Current window: `{params['current_start']}` to `{params['current_end']}`",
        f"- Previous window: `{params['previous_start']}` to `{params['previous_end']}`",
        f"- Minimum current support: `{params['min_support']}` unique articles",
        "",
        "## Ranking B — smoothed log2 change",
        "",
        "| rank | candidate | current df/share | previous df/share | change | articles | evidence |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["ranking_b"]:
        evidence = "<br>".join(
            f"{item['published_at']} {item['news_id']}: {item['title']}"
            for item in row["evidence"]
        )
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["rank"]),
                    _markdown_cell(row["candidate"]),
                    f"{row['current_article_df']} / {row['current_share']:.6f}",
                    f"{row['previous_article_df']} / {row['previous_share']:.6f}",
                    f"{row['change_score']:.6f}",
                    str(row["article_count"]),
                    _markdown_cell(evidence),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def run_experiment(
    end_date: date,
    *,
    output_dir: str | Path = "artifacts/e002_sbs",
    raw_dir: str | Path = "data/raw",
    fetcher: Callable[[str], str] = fetch_page,
) -> dict:
    articles, windows, collection = collect_historical(end_date, fetcher=fetcher)
    current_count = sum(
        windows["current_start"] <= _article_date(item) <= windows["current_end"]
        for item in articles
    )
    previous_count = sum(
        windows["previous_start"] <= _article_date(item) <= windows["previous_end"]
        for item in articles
    )
    ranking, candidate_count = rank_sbs_articles(articles, windows)

    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    raw_file = raw_path / f"sbs_section14_{end_date.isoformat()}.json"
    raw_payload = {
        "source": {"endpoint": BASE_URL, "section_type": SECTION_TYPE},
        "parameters": {key: value.isoformat() for key, value in windows.items()},
        "collection": collection,
        "articles": articles,
    }
    raw_file.write_text(
        json.dumps(raw_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = {
        "experiment": "E002",
        "source": {
            "endpoint": BASE_URL,
            "section_type": SECTION_TYPE,
            "stored_fields": ["title", "published_at", "news_id", "link"],
            "raw_metadata": str(raw_file),
        },
        "parameters": {
            **{key: value.isoformat() for key, value in windows.items()},
            "smoothing": SMOOTHING,
            "min_support": MIN_SUPPORT,
        },
        "counts": {
            "articles": len(articles),
            "current_articles": current_count,
            "previous_articles": previous_count,
            "candidate_count": candidate_count,
            **collection,
        },
        "ranking_b": ranking,
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (destination / "results.md").write_text(render_markdown(result), encoding="utf-8")
    return result


def _default_end_date() -> date:
    return datetime.now(KST).date() - timedelta(days=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end-date", type=date.fromisoformat, default=_default_end_date())
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/e002_sbs"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    result = run_experiment(
        args.end_date,
        output_dir=args.output_dir,
        raw_dir=args.raw_dir,
    )
    print(
        f"wrote {args.output_dir / 'results.json'} and {args.output_dir / 'results.md'}; "
        f"articles={result['counts']['articles']}"
    )


if __name__ == "__main__":
    main()
