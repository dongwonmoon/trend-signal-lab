import json
from datetime import date

import pytest

from scripts import build_wikimedia_page as page
from scripts.collect_wikimedia import API_PROJECT, SOURCE, endpoint_url


def stored(day, articles):
    return {
        "source": SOURCE, "project": API_PROJECT,
        "snapshot_date": day.isoformat(), "time_zone": "UTC",
        "collected_at": "2026-08-31T01:00:00Z",
        "request_url": endpoint_url(day), "articles": articles,
    }


def test_daily_selection_projection_and_validation(tmp_path):
    day = date(2026, 8, 29)
    rows = [
        {"article": name, "views": 100, "rank": 1}
        for name in ["위키백과:대문", "특수:검색", "파일:그림.svg"]
    ] + [
        {"article": "나_주제", "views": 20, "rank": 4},
        {"article": "가:주제", "views": 20, "rank": 4},
    ] + [
        {"article": f"항목{i:02}", "views": 1, "rank": i + 6}
        for i in range(25)
    ]
    target = tmp_path / "2026-08-29.json"
    payload = stored(day, rows)
    target.write_text(json.dumps(payload), encoding="utf-8")
    # The current UTC day is ineligible; its contents must not be read.
    (tmp_path / "2026-08-30.json").write_text("invalid", encoding="utf-8")
    selected = page.select_snapshot(tmp_path, None, today=date(2026, 8, 30))
    assert selected == target
    result = page.build_result(page.load_snapshot(selected))
    assert result["snapshot_date"] == "2026-08-29"
    assert result["ranking"] == "daily_views"
    assert len(result["items"]) == 20
    assert result["items"][0] == {
        "rank": 1, "source_rank": 4, "page": "가:주제", "views": 20,
    }
    assert result["items"][1]["page"] == "나_주제"
    assert [r["rank"] for r in result["items"]] == list(range(1, 21))
    payload["source"] = "another_source"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        page.load_snapshot(selected)
    with pytest.raises(ValueError):
        page.select_snapshot(tmp_path, date(2026, 8, 30), today=date(2026, 8, 30))
    with pytest.raises(FileNotFoundError):
        page.select_snapshot(tmp_path, date(2026, 8, 28), today=date(2026, 8, 30))


def test_invalid_snapshot_does_not_replace_accepted_json(tmp_path):
    root, out = tmp_path / "raw", tmp_path / "out"
    root.mkdir()
    out.mkdir()
    (root / "2026-08-29.json").write_text("{}", encoding="utf-8")
    accepted = out / "results.json"
    accepted.write_text("accepted", encoding="utf-8")
    assert page.main(["--data-root", str(root), "--date", "2026-08-29",
                      "--output-dir", str(out)]) != 0
    assert accepted.read_text(encoding="utf-8") == "accepted"


def test_page_escapes_source_text_and_handles_empty_results():
    result = page.build_result(stored(date(2026, 8, 29), [
        {"article": "<script>_&_주제", "views": 20, "rank": 1},
    ]))
    html = page.render_html(result)
    for label in ["인기 키워드", "한국어 위키백과 조회수 기준", "2026-08-29", "UTC"]:
        assert label in html
    assert "<script>" not in html
    assert "&lt;script&gt; &amp; 주제" in html
    assert "<th" in html
    assert result["items"][0]["page"] == "<script>_&_주제"
    result["items"] = []
    assert "표시할 항목이 없습니다" in page.render_html(result)


def test_build_is_repeatable_and_failure_preserves_page(tmp_path, monkeypatch):
    root, out = tmp_path / "raw", tmp_path / "out"
    root.mkdir()
    raw = root / "2026-08-29.json"
    raw.write_text(json.dumps(stored(date(2026, 8, 29), [
        {"article": "가_주제", "views": 20, "rank": 1},
    ])), encoding="utf-8")
    args = ["--data-root", str(root), "--date", "2026-08-29", "--output-dir", str(out)]
    assert page.main(args) == 0
    files = [out / "results.json", out / "index.html"]
    accepted = [p.read_bytes() for p in files]
    assert page.main(args) == 0
    assert [p.read_bytes() for p in files] == accepted
    real_replace = page.os.replace

    def reject_html(source, destination):
        if destination == files[1]:
            raise OSError("simulated publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(page.os, "replace", reject_html)
    assert page.main(args) != 0
    assert files[1].read_bytes() == accepted[1]
    assert sorted(p.name for p in out.iterdir()) == ["index.html", "results.json"]
    raw.write_text("invalid", encoding="utf-8")
    assert page.main(args) != 0
    assert [p.read_bytes() for p in files] == accepted
