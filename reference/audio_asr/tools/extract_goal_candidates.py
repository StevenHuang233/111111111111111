#!/usr/bin/env python
"""Extract weak goal-candidate windows from ASR subtitle segments.

This is not a gold-event detector. It is a cheap cross-check signal for the
visual harness: prioritize these windows, then verify them from frames and the
scoreboard before making any factual claim.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "germany_curacao" / "audio_reference.segments.json"
DEFAULT_JSON = Path(__file__).resolve().parents[1] / "germany_curacao" / "goal_candidate_windows.json"
DEFAULT_MD = Path(__file__).resolve().parents[1] / "germany_curacao" / "goal_candidate_windows.md"

STRONG_PATTERNS = [
    "球进了",
    "进球了",
    "破门",
    "先开纪录",
    "扳回",
    "扩大比分",
    "改写比分",
    "再下一城",
]

WEAK_PATTERNS = [
    "进球",
    "打进",
    "比分",
    "领先",
    "扳平",
    "射门",
    "得分",
]

NEGATIVE_HINTS = [
    "第九次出场",
    "打进的第",
    "生涯",
    "此前",
    "历史",
    "身价",
]


def seconds_to_stamp(seconds: int) -> str:
    minutes, sec = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def score_segment(text: str) -> tuple[int, list[str]]:
    hits: list[str] = []
    score = 0
    for pattern in STRONG_PATTERNS:
        if pattern in text:
            score += 4
            hits.append(pattern)
    for pattern in WEAK_PATTERNS:
        if pattern in text:
            score += 1
            hits.append(pattern)
    if re.search(r"\d+\s*[:比-]\s*\d+", text):
        score += 2
        hits.append("score_like")
    for hint in NEGATIVE_HINTS:
        if hint in text:
            score -= 2
            hits.append(f"negative:{hint}")
    return score, hits


def load_segments(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_windows(
    segments: list[dict[str, Any]],
    *,
    pre_sec: int,
    post_sec: int,
    merge_gap_sec: int,
    min_score: int,
) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    for segment in segments:
        text = str(segment.get("text", ""))
        score, hits = score_segment(text)
        if score >= min_score:
            start_sec = int(segment["start_ms"] // 1000)
            end_sec = int(segment["end_ms"] // 1000)
            seeds.append(
                {
                    "start_sec": max(0, start_sec - pre_sec),
                    "end_sec": end_sec + post_sec,
                    "seed_start_sec": start_sec,
                    "seed_end_sec": end_sec,
                    "score": score,
                    "hits": hits,
                    "texts": [text],
                    "segment_indices": [segment.get("index")],
                }
            )

    seeds.sort(key=lambda item: (item["start_sec"], item["end_sec"]))
    windows: list[dict[str, Any]] = []
    for seed in seeds:
        if not windows or seed["start_sec"] > windows[-1]["end_sec"] + merge_gap_sec:
            windows.append(seed)
            continue
        current = windows[-1]
        current["end_sec"] = max(current["end_sec"], seed["end_sec"])
        current["score"] += seed["score"]
        current["hits"].extend(seed["hits"])
        current["texts"].extend(seed["texts"])
        current["segment_indices"].extend(seed["segment_indices"])

    for index, window in enumerate(windows, 1):
        window["candidate_id"] = f"AG{index:02d}"
        window["start_time"] = seconds_to_stamp(window["start_sec"])
        window["end_time"] = seconds_to_stamp(window["end_sec"])
        window["frame_start_4fps"] = window["start_sec"] * 4
        window["frame_end_4fps"] = window["end_sec"] * 4
        window["hits"] = sorted(set(window["hits"]))
        window["note"] = "Weak ASR-derived candidate; verify with frames and scoreboard."
    return windows


def write_markdown(windows: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Goal Candidate Windows / 进球候选窗口",
        "",
        "EN: These windows are derived from ASR keywords and must be verified from video frames.",
        "",
        "ZH: 这些窗口来自 ASR 关键词，必须再用视频帧核验。",
        "",
        "| ID | Window | 4fps Frames | Score | Evidence Text |",
        "| --- | --- | --- | --- | --- |",
    ]
    for window in windows:
        text = "<br>".join(window["texts"][:4]).replace("|", "/")
        if len(window["texts"]) > 4:
            text += "<br>..."
        lines.append(
            f"| {window['candidate_id']} | `{window['start_time']}-{window['end_time']}` | "
            f"`{window['frame_start_4fps']}-{window['frame_end_4fps']}` | "
            f"{window['score']} | {text} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract weak goal-candidate windows from ASR segments.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--pre-sec", type=int, default=20)
    parser.add_argument("--post-sec", type=int, default=45)
    parser.add_argument("--merge-gap-sec", type=int, default=45)
    parser.add_argument("--min-score", type=int, default=3)
    args = parser.parse_args()

    segments = load_segments(args.input)
    windows = build_windows(
        segments,
        pre_sec=args.pre_sec,
        post_sec=args.post_sec,
        merge_gap_sec=args.merge_gap_sec,
        min_score=args.min_score,
    )
    args.output_json.write_text(json.dumps(windows, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(windows, args.output_md)
    print(f"Wrote {len(windows)} candidates to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
