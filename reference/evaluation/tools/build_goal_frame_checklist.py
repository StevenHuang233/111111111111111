#!/usr/bin/env python
"""Build frame-level checklists for ASR-derived goal candidates.

The checklist is a bridge between weak audio cues and visual verification. It
does not decide whether a goal happened. It tells the harness or a human which
4fps frames to inspect first and how to narrow the scoreboard-change point.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANDIDATES = REPO_ROOT / "reference" / "audio_asr" / "germany_curacao" / "goal_candidate_windows.json"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "goal_frame_checklist.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "goal_frame_checklist.md"


def stamp(seconds: int) -> str:
    minutes, sec = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def frame_name(frame_id: int) -> str:
    return f"frame_{frame_id:06d}.jpg"


def frame_probe(second: int, fps: int) -> dict[str, Any]:
    frame_id = max(0, second * fps)
    return {"video_sec": second, "video_time": stamp(second), "frame_id": frame_id, "frame_name": frame_name(frame_id)}


def unique_probes(seconds: list[int], fps: int) -> list[dict[str, Any]]:
    seen: set[int] = set()
    probes: list[dict[str, Any]] = []
    for second in seconds:
        if second in seen:
            continue
        seen.add(second)
        probes.append(frame_probe(second, fps))
    return probes


def build_checklist(candidates: list[dict[str, Any]], fps: int) -> list[dict[str, Any]]:
    checklist: list[dict[str, Any]] = []
    for candidate in candidates:
        start = int(candidate["start_sec"])
        end = int(candidate["end_sec"])
        seed = int(candidate.get("seed_start_sec", (start + end) // 2))
        coarse_seconds = [start, start + (end - start) // 4, (start + end) // 2, start + 3 * (end - start) // 4, end]
        dense_seconds = list(range(max(start, seed - 12), min(end, seed + 12) + 1, 2))
        item = {
            "candidate_id": candidate["candidate_id"],
            "candidate_time": f"{candidate['start_time']}-{candidate['end_time']}",
            "asr_hits": candidate.get("hits", []),
            "asr_texts": candidate.get("texts", []),
            "coarse_scoreboard_probes": unique_probes(coarse_seconds, fps),
            "dense_action_probes": unique_probes(dense_seconds, fps),
            "bisection_protocol": [
                "Compare scoreboard at first and last coarse probes.",
                "If score changes, bisect the interval by checking midpoint frames until the interval is <= 4 seconds.",
                "Confirm with at least one frame showing ball/net/celebration and one frame showing scoreboard after the event.",
                "If no score change but ASR says goal, classify as replay/summary/historical mention or disallowed/unclear pending manual review.",
            ],
            "status": "unverified",
        }
        checklist.append(item)
    return checklist


def write_markdown(checklist: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Goal Frame Checklist / 进球帧核验清单",
        "",
        "EN: These frame probes are for verification only. They do not prove a goal by themselves.",
        "",
        "ZH: 这些帧探针只用于核验，本身不证明进球。",
        "",
        "| ID | Candidate Time | Coarse Frames | Dense Action Frames | ASR Text |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in checklist:
        coarse = "<br>".join(f"`{probe['video_time']} {probe['frame_name']}`" for probe in item["coarse_scoreboard_probes"])
        dense = "<br>".join(f"`{probe['video_time']} {probe['frame_name']}`" for probe in item["dense_action_probes"][:8])
        if len(item["dense_action_probes"]) > 8:
            dense += "<br>..."
        text = "<br>".join(str(text).replace("|", "/") for text in item["asr_texts"][:3])
        lines.append(f"| {item['candidate_id']} | `{item['candidate_time']}` | {coarse} | {dense} | {text} |")
    lines.extend(
        [
            "",
            "## Bisection Protocol / 二分核验流程",
            "",
            "1. Compare scoreboard at the first and last coarse probes.",
            "2. If score changes, check midpoint frames and shrink the interval until it is no longer than 4 seconds.",
            "3. Confirm with one frame showing the ball/net/celebration and one frame showing the post-event scoreboard.",
            "4. If no score change but ASR says goal, classify as replay, summary, historical mention, disallowed goal, or unclear.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build frame-level verification checklist for goal candidates.")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--fps", type=int, default=4)
    args = parser.parse_args()

    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    checklist = build_checklist(candidates, args.fps)
    args.output_json.write_text(json.dumps(checklist, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(checklist, args.output_md)
    print(f"Wrote {len(checklist)} frame-check candidates to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
