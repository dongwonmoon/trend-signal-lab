#!/usr/bin/env python3
"""Run the fixed E001 title-only YouTube keyword baselines."""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

from kiwipiepy import Kiwi

from trend_signal_lab.dataset import (
    ALLOWED_CATEGORY_IDS,
    CURRENT_END,
    CURRENT_START,
    PREVIOUS_END,
    PREVIOUS_START,
    Snapshot,
    load_snapshots,
)

CURRENT_RANKING = "current_share"
CHANGE_RANKING = "change_score"
SMOOTHING = 0.5
MIN_SUPPORT = 5
MAX_NGRAM = 3

# Fixed before the first full-data run. Changes require a new experiment.
ELIGIBLE_TAGS = frozenset({"NNG", "NNP", "NNB", "SL", "SH"})
STOPWORDS = frozenset(
    {
        "공개",
        "공식",
        "뉴스",
        "다시",
        "라이브",
        "방송",
        "영상",
        "예고편",
        "오늘",
        "원본",
        "유튜브",
        "직캠",
        "추천",
        "채널",
        "콘텐츠",
        "티저",
        "풀영상",
        "프로필",
        "화제",
        "youtube",
        "shorts",
        "쇼츠",
    }
)
URL_FRAGMENT = re.compile(r"(?:https?|www|\.com|\.kr|\.net|\.org)", re.IGNORECASE)


def normalize_title(title: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", title).split())


def _normalized_form(form: str) -> str:
    return unicodedata.normalize("NFKC", form).casefold()


def _eligible(form: str, tag: str) -> bool:
    normalized = _normalized_form(form)
    return (
        tag in ELIGIBLE_TAGS
        and len(normalized) > 1
        and normalized not in STOPWORDS
        and URL_FRAGMENT.search(normalized) is None
    )


def extract_candidates(title: str, kiwi: Kiwi | None = None) -> set[str]:
    """Return unique 1-3 grams from consecutive eligible Kiwi tokens."""

    analyzer = kiwi or Kiwi()
    candidates: set[str] = set()
    run: list[str] = []

    def flush() -> None:
        for start in range(len(run)):
            for width in range(1, min(MAX_NGRAM, len(run) - start) + 1):
                candidates.add(" ".join(run[start : start + width]))
        run.clear()

    for token in analyzer.tokenize(normalize_title(title)):
        if _eligible(token.form, token.tag):
            run.append(_normalized_form(token.form))
        else:
            flush()
    flush()
    return candidates


def _phrase_preference(
    supports: Mapping[str, Mapping[str, set]],
) -> dict[str, dict[str, set]]:
    """Drop a shorter term only when a longer term has identical support."""

    terms = sorted(supports, key=lambda term: (-len(term.split()), term))
    retained: dict[str, dict[str, set]] = {}
    for term in terms:
        support = supports[term]
        if any(
            len(longer.split()) > len(term.split())
            and f" {term} " in f" {longer} "
            and supports[longer]["current"] == support["current"]
            and supports[longer]["previous"] == support["previous"]
            for longer in supports
        ):
            continue
        retained[term] = {key: set(value) for key, value in support.items()}
    return retained


def collect_supports(snapshots: Sequence[Snapshot], kiwi: Kiwi | None = None) -> dict[str, dict[str, set]]:
    analyzer = kiwi or Kiwi()
    supports: dict[str, dict[str, set]] = defaultdict(
        lambda: {"current": set(), "previous": set(), "videos": set(), "evidence": []}
    )
    for snapshot in snapshots:
        key = (snapshot.video_id, snapshot.trending_date.isoformat())
        period = "current" if CURRENT_START <= snapshot.trending_date <= CURRENT_END else "previous"
        for candidate in extract_candidates(snapshot.title, analyzer):
            entry = supports[candidate]
            entry[period].add(key)
            entry["videos"].add(snapshot.video_id)
            entry["evidence"].append(snapshot)
    preferred = _phrase_preference(supports)
    for term in preferred:
        preferred[term]["evidence"] = sorted(
            preferred[term]["evidence"],
            key=lambda item: (
                not (CURRENT_START <= item.trending_date <= CURRENT_END),
                item.trending_date,
                item.video_id,
                item.title,
            ),
        )[:3]
    return preferred


def rank_candidates(
    supports: Mapping[str, Mapping[str, set]],
    *,
    current_total: int,
    previous_total: int,
    mode: str,
    min_support: int = MIN_SUPPORT,
) -> list[dict]:
    """Rank support sets using one of the two preregistered baseline scores."""

    if mode not in {CURRENT_RANKING, CHANGE_RANKING}:
        raise ValueError(f"unknown ranking mode: {mode}")
    rows: list[dict] = []
    for candidate, support in supports.items():
        current_df = len(support["current"])
        if current_df < min_support:
            continue
        previous_df = len(support["previous"])
        current_share = current_df / current_total if current_total else 0.0
        previous_share = previous_df / previous_total if previous_total else 0.0
        change_score = math.log2(
            ((current_df + SMOOTHING) / (current_total + 1))
            / ((previous_df + SMOOTHING) / (previous_total + 1))
        )
        rows.append(
            {
                "candidate": candidate,
                "current_snapshot_df": current_df,
                "current_share": current_share,
                "previous_snapshot_df": previous_df,
                "previous_share": previous_share,
                "change_score": change_score,
                "video_count": len(support["videos"]),
                "evidence": [
                    {
                        "title": item.title,
                        "date": item.trending_date.isoformat(),
                        "video_id": item.video_id,
                    }
                    for item in support.get("evidence", [])[:3]
                ],
            }
        )
    rows.sort(
        key=lambda row: (
            -row[mode],
            -row["current_snapshot_df"],
            -len(row["candidate"].split()),
            row["candidate"],
        )
    )
    for rank, row in enumerate(rows[:20], start=1):
        row["rank"] = rank
    return rows[:20]


def render_result_json(result: Mapping) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result: Mapping) -> str:
    params = result["parameters"]
    lines = [
        "# E001 YouTube trend keyword baseline",
        "",
        "Generated from the fixed historical input; usefulness labels remain pending human review.",
        "",
        "## Parameters",
        "",
        f"- Current window: `{params['current_start']}` to `{params['current_end']}`",
        f"- Previous window: `{params['previous_start']}` to `{params['previous_end']}`",
        f"- Categories: `{', '.join(map(str, params['category_ids']))}`",
        f"- Minimum current support: `{params['min_support']}` snapshots",
        f"- Eligible tags: `{', '.join(params['eligible_tags'])}`",
        "",
        f"## Ranking A — current snapshot share ({result['counts']['current_snapshots']} snapshots)",
        "",
    ]
    lines.extend(_ranking_table(result["rankings"][CURRENT_RANKING]))
    lines.extend(
        [
            "",
            f"## Ranking B — smoothed log2 change ({result['counts']['previous_snapshots']} previous snapshots)",
            "",
        ]
    )
    lines.extend(_ranking_table(result["rankings"][CHANGE_RANKING]))
    lines.extend(
        [
            "",
            "## Anchor",
            "",
            f"- Variants: `{', '.join(result['anchor']['variants'])}`",
            f"- Present in either top 20: **{result['anchor']['present']}**",
            "",
            "## Source",
            "",
            f"- Dataset: `{result['source_manifest'].get('dataset_slug', 'unknown')}` version `{result['source_manifest'].get('dataset_version', 'unknown')}`",
            f"- SHA-256: `{result['source_manifest'].get('sha256', 'unknown')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _ranking_table(rows: Sequence[Mapping]) -> list[str]:
    lines = [
        "| rank | candidate | current df/share | previous df/share | change | videos | evidence |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        evidence = "<br>".join(
            f"{item['date']} {item['video_id']}: {item['title']}" for item in row["evidence"]
        )
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["rank"]),
                    _markdown_cell(row["candidate"]),
                    f"{row['current_snapshot_df']} / {row['current_share']:.6f}",
                    f"{row['previous_snapshot_df']} / {row['previous_share']:.6f}",
                    f"{row['change_score']:.6f}",
                    str(row["video_count"]),
                    _markdown_cell(evidence),
                )
            )
            + " |"
        )
    return lines


def run_experiment(input_path: str | Path, output_dir: str | Path) -> dict:
    source = Path(input_path)
    snapshots = load_snapshots(source)
    current = [item for item in snapshots if CURRENT_START <= item.trending_date <= CURRENT_END]
    previous = [item for item in snapshots if PREVIOUS_START <= item.trending_date <= PREVIOUS_END]
    supports = collect_supports(snapshots)
    manifest_path = source.with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    rankings = {
        CURRENT_RANKING: rank_candidates(
            supports,
            current_total=len(current),
            previous_total=len(previous),
            mode=CURRENT_RANKING,
        ),
        CHANGE_RANKING: rank_candidates(
            supports,
            current_total=len(current),
            previous_total=len(previous),
            mode=CHANGE_RANKING,
        ),
    }
    anchor_variants = ("오징어 게임", "오징어게임", "squid game")
    top_candidates = {row["candidate"] for rows in rankings.values() for row in rows}
    result = {
        "experiment": "E001",
        "source_manifest": manifest,
        "parameters": {
            "current_start": CURRENT_START.isoformat(),
            "current_end": CURRENT_END.isoformat(),
            "previous_start": PREVIOUS_START.isoformat(),
            "previous_end": PREVIOUS_END.isoformat(),
            "category_ids": sorted(ALLOWED_CATEGORY_IDS),
            "eligible_tags": sorted(ELIGIBLE_TAGS),
            "stopwords": sorted(STOPWORDS),
            "max_ngram": MAX_NGRAM,
            "smoothing": SMOOTHING,
            "min_support": MIN_SUPPORT,
        },
        "counts": {
            "snapshots": len(snapshots),
            "current_snapshots": len(current),
            "previous_snapshots": len(previous),
            "unique_videos": len({item.video_id for item in snapshots}),
            "candidate_count": len(supports),
        },
        "rankings": rankings,
        "anchor": {
            "variants": list(anchor_variants),
            "present": any(variant in top_candidates for variant in anchor_variants),
            "matched_candidates": sorted(top_candidates.intersection(anchor_variants)),
        },
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(render_result_json(result), encoding="utf-8")
    (destination / "results.md").write_text(render_markdown(result), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/e001"))
    args = parser.parse_args()
    result = run_experiment(args.input, args.output_dir)
    print(
        f"wrote {args.output_dir / 'results.json'} and {args.output_dir / 'results.md'}; "
        f"anchor_present={result['anchor']['present']}"
    )


if __name__ == "__main__":
    main()
