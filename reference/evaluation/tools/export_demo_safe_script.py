#!/usr/bin/env python
"""Export a demo-safe commentary candidate from revision annotations.

The exporter is conservative and non-generative. It does not correct facts or
rewrite text. It only separates segments that are blocked from final-demo use.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ANNOTATIONS = REPO_ROOT / "reference" / "evaluation" / "commentary_revision_annotations.json"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "demo_safe_commentary_candidate.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "demo_safe_commentary_candidate.md"


def display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stamp(seconds: Any) -> str:
    total = max(0, int(round(float(seconds))))
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def segment_text(segment: dict[str, Any], language: str) -> str:
    value = segment.get(language, {})
    if isinstance(value, dict):
        return str(value.get("commentary_text", "")).strip()
    return ""


def compact_segment(segment: dict[str, Any]) -> dict[str, Any]:
    review = segment.get("review", {})
    return {
        "event_id": segment.get("event_id"),
        "event_type": segment.get("event_type"),
        "time_range": f"{stamp(segment.get('talk_start_sec', 0.0))}-{stamp(segment.get('talk_end_sec', 0.0))}",
        "review_status": review.get("status"),
        "review_priority": review.get("priority"),
        "issues": review.get("issues", []),
        "suggested_treatment": review.get("policy", {}).get("suggested_treatment"),
        "zh": segment_text(segment, "chinese"),
        "en": segment_text(segment, "english"),
    }


def build_candidate(annotations_path: Path, *, clear_only: bool) -> dict[str, Any]:
    annotations = load_json(annotations_path)
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for segment in annotations.get("segments", []):
        if not isinstance(segment, dict):
            continue
        status = segment.get("review", {}).get("status", "clear")
        if status == "blocker" or (clear_only and status != "clear"):
            excluded.append(compact_segment(segment))
        else:
            included.append(compact_segment(segment))

    summary = {
        "source_annotations": display_path(annotations_path),
        "mode": "clear_only" if clear_only else "exclude_blockers",
        "included_segments": len(included),
        "excluded_segments": len(excluded),
        "included_status_counts": count_by(included, "review_status"),
        "excluded_status_counts": count_by(excluded, "review_status"),
        "policy": "Non-generative demo candidate. Excluded segments need suppression, rewrite, or manual acceptance before final packaging.",
    }
    return {
        "summary": summary,
        "included_segments": included,
        "excluded_segments": excluded,
    }


def count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key, "unknown"))
        counts[value] = counts.get(value, 0) + 1
    return counts


def safe_cell(value: Any, limit: int = 180) -> str:
    text = str(value or "").replace("|", "/").replace("\n", " ").strip()
    return text[:limit]


def write_markdown(candidate: dict[str, Any], path: Path, *, limit: int) -> None:
    summary = candidate["summary"]
    lines = [
        "# Demo-Safe Commentary Candidate / Demo 安全候选稿",
        "",
        "EN: This file is a non-generative export from revision annotations. It excludes blocker segments by default.",
        "",
        "ZH: 本文件从修订标注中非生成式导出，默认剔除阻塞片段。",
        "",
        "## Summary / 摘要",
        "",
        f"- `mode`: {summary['mode']}",
        f"- `included_segments`: {summary['included_segments']}",
        f"- `excluded_segments`: {summary['excluded_segments']}",
        f"- `included_status_counts`: {summary['included_status_counts']}",
        f"- `excluded_status_counts`: {summary['excluded_status_counts']}",
        "",
        "EN: Warning segments are not fatal, but still need quick human review for style and factual safety.",
        "",
        "ZH: Warning 片段不是阻塞项，但仍需要人工快速检查风格和事实安全。",
        "",
        "## Excluded Blockers / 已剔除阻塞片段",
        "",
        "| Event | Type | Time | Issues | Treatment | Excerpt |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for segment in candidate["excluded_segments"][:limit]:
        lines.append(
            f"| {segment['event_id']} | {segment['event_type']} | `{segment['time_range']}` | "
            f"{', '.join(segment['issues'])} | {segment['suggested_treatment']} | {safe_cell(segment['zh'])} |"
        )
    if not candidate["excluded_segments"]:
        lines.append("| - | - | - | - | - | - |")

    lines.extend(
        [
            "",
            "## Included Candidate Preview / 候选保留片段预览",
            "",
            "| Event | Type | Time | Status | Excerpt |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for segment in candidate["included_segments"][:limit]:
        lines.append(
            f"| {segment['event_id']} | {segment['event_type']} | `{segment['time_range']}` | "
            f"{segment['review_status']} | {safe_cell(segment['zh'])} |"
        )
    if not candidate["included_segments"]:
        lines.append("| - | - | - | - | - |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a demo-safe commentary candidate.")
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--clear-only", action="store_true", help="Exclude warning and polish segments too.")
    parser.add_argument("--md-limit", type=int, default=80)
    args = parser.parse_args()

    candidate = build_candidate(args.annotations, clear_only=args.clear_only)
    args.output_json.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(candidate, args.output_md, limit=max(1, args.md_limit))
    print(json.dumps(candidate["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
