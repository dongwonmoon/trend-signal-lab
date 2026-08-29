from datetime import date
from math import log2

import pytest

from scripts.run_e002_sbs import (
    crawl_day,
    dedupe_articles,
    page_count,
    parse_sbs_page,
    rank_sbs_articles,
    window_dates,
)


PAGE_1 = """
<div class="w_news_list type_issue2"><ul>
  <li><span>
    <link itemprop="url" href="https://news.sbs.co.kr/news/endPage.do?news_id=N100001">
    <meta itemprop="datePublished" content="2026-08-20T13:20:00+09:00">
    <meta itemprop="headline" content="첫 번째 기사">
  </span><a class="news"><span class="read">저장하지 않을 설명</span></a></li>
  <li><span>
    <link itemprop="url" href="https://news.sbs.co.kr/news/endPage.do?news_id=N100002">
    <meta itemprop="datePublished" content="2026-08-20T11:00:00+09:00">
    <meta itemprop="headline" content="두 번째 기사">
  </span></li>
</ul></div>
<a href="?pageDate=20260820&amp;pageIdx=1&amp;sectionType=14">1</a>
<a href="?pageDate=20260820&amp;pageIdx=2&amp;sectionType=14">2</a>
"""

PAGE_2 = """
<div class="w_news_list type_issue2"><ul><li><span>
  <link itemprop="url" href="https://news.sbs.co.kr/news/endPage.do?news_id=N100003">
  <meta itemprop="datePublished" content="2026-08-20T09:00:00+09:00">
  <meta itemprop="headline" content="세 번째 기사">
</span></li></ul></div>
"""


def _article(news_id: str, title: str, published_at: str) -> dict[str, str]:
    return {
        "title": title,
        "published_at": published_at,
        "news_id": news_id,
        "link": f"https://news.sbs.co.kr/news/endPage.do?news_id={news_id}",
    }


def test_parser_keeps_only_required_schema_metadata():
    rows = parse_sbs_page(PAGE_1)

    assert rows[0] == {
        "title": "첫 번째 기사",
        "published_at": "2026-08-20T13:20:00+09:00",
        "link": "https://news.sbs.co.kr/news/endPage.do?news_id=N100001",
        "news_id": "N100001",
    }
    assert set(rows[0]) == {"title", "published_at", "news_id", "link"}
    assert page_count(PAGE_1) == 2


def test_parser_requires_the_observed_latest_news_list():
    with pytest.raises(RuntimeError, match="latest-news list"):
        parse_sbs_page("<html><body>changed markup</body></html>")


def test_windows_and_crawl_cover_all_advertised_pages():
    calls: list[str] = []

    def fetcher(url: str) -> str:
        calls.append(url)
        return PAGE_1 if "pageIdx=1" in url else PAGE_2

    rows, pages = crawl_day(date(2026, 8, 20), fetcher=fetcher)

    assert window_dates(date(2026, 8, 20)) == {
        "current_start": date(2026, 7, 22),
        "current_end": date(2026, 8, 20),
        "previous_start": date(2026, 6, 22),
        "previous_end": date(2026, 7, 21),
    }
    assert pages == 2
    assert len(calls) == 2
    assert [row["news_id"] for row in rows] == ["N100003", "N100002", "N100001"]


def test_ranking_b_deduplicates_articles_and_keeps_fixed_formula():
    windows = window_dates(date(2026, 8, 20))
    rows = [
        _article(f"C{i}", "지원 후보", f"2026-08-{20 - i:02d}T12:00:00+09:00")
        for i in range(5)
    ]
    rows += [
        _article("P1", "지원 후보", "2026-07-01T12:00:00+09:00"),
        _article("C0", "중복 제목", "2026-08-20T12:00:00+09:00"),
    ]

    result, _ = rank_sbs_articles(rows, windows)

    assert [row["news_id"] for row in dedupe_articles(rows)].count("C0") == 1
    assert result[0]["candidate"] == "지원 후보"
    assert result[0]["current_article_df"] == 5
    assert result[0]["previous_article_df"] == 1
    assert result[0]["change_score"] == pytest.approx(
        log2(((5 + 0.5) / (5 + 1)) / ((1 + 0.5) / (1 + 1)))
    )


def test_surface_longer_phrase_preference_drops_embedded_short_term():
    windows = window_dates(date(2026, 8, 20))
    rows = [_article(f"C{i}", "김부장", f"2026-08-{20 - i:02d}T12:00:00+09:00") for i in range(5)]
    rows.append(_article("P0", "김부장", "2026-07-01T12:00:00+09:00"))
    result, _ = rank_sbs_articles(rows, windows)
    candidates = {row["candidate"] for row in result}
    assert "김부장" in candidates
    assert "부장" not in candidates
