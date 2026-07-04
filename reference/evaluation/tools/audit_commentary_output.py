#!/usr/bin/env python
"""Audit generated commentary against weak references and public match facts.

This tool is intentionally evaluation-only. It should not feed public facts into
the target visual commentary agent. Its job is to expose factual conflicts,
over-detected goals, missing key-event coverage, and non-human commentary style
so the harness can add verifiers and revision loops.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMMENTARY = REPO_ROOT / "outputs" / "commentary_bilingual_full_review.md"
DEFAULT_FACTS = REPO_ROOT / "reference" / "evaluation" / "germany_curacao_public_reference.json"
DEFAULT_ASR = REPO_ROOT / "reference" / "audio_asr" / "germany_curacao" / "goal_candidate_windows.json"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "commentary_full_review_audit.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "commentary_full_review_audit.md"


@dataclass
class Segment:
    index: int
    event_id: str
    event_type: str
    start_sec: int
    end_sec: int
    english: str
    chinese: str


def parse_time_to_sec(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(float(seconds))
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
    raise ValueError(f"Unsupported timestamp: {value}")


def stamp(seconds: int) -> str:
    minutes, sec = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def parse_markdown_table(path: Path) -> list[Segment]:
    segments: list[Segment] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("|---") or line.startswith("| # "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 6 or not cells[0].isdigit():
            continue
        start_text, end_text = cells[3].split("-", 1)
        segments.append(
            Segment(
                index=int(cells[0]),
                event_id=cells[1],
                event_type=cells[2],
                start_sec=parse_time_to_sec(start_text),
                end_sec=parse_time_to_sec(end_text),
                english=cells[4],
                chinese=cells[5],
            )
        )
    return segments


def text_of(segment: Segment) -> str:
    return f"{segment.english}\n{segment.chinese}"


def extract_score_claims(text: str) -> list[str]:
    claims: list[str] = []
    claims.extend(re.findall(r"\b\d+\s*-\s*\d+\b", text))
    claims.extend(re.findall(r"\d+\s*比\s*\d+", text))
    claims.extend(re.findall(r"\d+\s*[:：]\s*\d+", text))
    return [claim.replace(" ", "") for claim in claims]


def nearest_asr_window(segment: Segment, windows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not windows:
        return None
    midpoint = (segment.start_sec + segment.end_sec) // 2
    return min(windows, key=lambda item: min(abs(midpoint - item["start_sec"]), abs(midpoint - item["end_sec"])))


def audit(segments: list[Segment], facts: dict[str, Any], asr_windows: list[dict[str, Any]]) -> dict[str, Any]:
    goal_segments = [segment for segment in segments if segment.event_type == "goal"]
    wrong_entities = facts.get("forbidden_wrong_entities_for_this_match", [])
    style_flags = facts.get("style_red_flags", [])
    known_names = set(facts.get("known_participant_names", []))

    issues: list[dict[str, Any]] = []
    for segment in segments:
        text = text_of(segment)
        lowered = text.lower()

        if segment.event_type == "goal" and re.search(r"does not enter|no goal|没有进入|没有进球|阻止了射门", text, re.I):
            issues.append(
                {
                    "severity": "critical",
                    "category": "goal_label_contradiction",
                    "event_id": segment.event_id,
                    "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                    "message": "Event is labeled goal but its text says no goal / no ball entry.",
                }
            )

        for entity in wrong_entities:
            if entity.lower() in lowered:
                issues.append(
                    {
                        "severity": "critical",
                        "category": "wrong_team_or_entity",
                        "event_id": segment.event_id,
                        "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                        "message": f"Mentions '{entity}', which is not part of Germany vs Curacao.",
                    }
                )

        for flag in style_flags:
            if flag.lower() in lowered:
                issues.append(
                    {
                        "severity": "medium",
                        "category": "non_broadcast_style",
                        "event_id": segment.event_id,
                        "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                        "message": f"Color/jersey descriptor '{flag}' should usually be team/player identity or avoided.",
                    }
                )
                break

        # Obvious invented names visible in current output.
        for name in re.findall(r"\b[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+(?:\s+[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+)?\b", segment.english):
            if name in {"Germany", "German", "Curaçao", "Curacao", "VAR", "Goal"}:
                continue
            if name not in known_names and name.lower() not in lowered[:0]:
                if name in {"Ibragimov", "Nkunku", "Müller"}:
                    issues.append(
                        {
                            "severity": "high",
                            "category": "unsupported_named_fact",
                            "event_id": segment.event_id,
                            "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                            "message": f"Named player '{name}' is unsupported by the evaluation reference.",
                        }
                    )

    score_claims = []
    for segment in segments:
        for claim in extract_score_claims(text_of(segment)):
            score_claims.append(
                {
                    "event_id": segment.event_id,
                    "event_type": segment.event_type,
                    "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                    "claim": claim,
                }
            )

    expected_goals = facts["known_goal_sequence"]
    goal_alignment: list[dict[str, Any]] = []
    for goal in goal_segments:
        nearest = nearest_asr_window(goal, asr_windows)
        distance = None
        if nearest:
            distance = min(abs(goal.start_sec - nearest["start_sec"]), abs(goal.start_sec - nearest["end_sec"]))
        goal_alignment.append(
            {
                "event_id": goal.event_id,
                "time": f"{stamp(goal.start_sec)}-{stamp(goal.end_sec)}",
                "score_claims": extract_score_claims(text_of(goal)),
                "nearest_asr_candidate": nearest["candidate_id"] if nearest else None,
                "nearest_asr_time": f"{nearest['start_time']}-{nearest['end_time']}" if nearest else None,
                "distance_to_asr_sec": distance,
                "text_excerpt": goal.chinese[:120],
            }
        )

    critical_or_high = [item for item in issues if item["severity"] in {"critical", "high"}]
    return {
        "summary": {
            "segment_count": len(segments),
            "generated_goal_count": len(goal_segments),
            "expected_goal_count_from_public_reference": len(expected_goals),
            "asr_goal_candidate_count": len(asr_windows),
            "critical_or_high_issue_count": len(critical_or_high),
            "style_issue_count": len([item for item in issues if item["category"] == "non_broadcast_style"]),
            "score_claim_count": len(score_claims),
        },
        "expected_goal_sequence": expected_goals,
        "score_claims": score_claims,
        "goal_alignment": goal_alignment,
        "issues": issues,
        "recommendations": [
            "Add a scoreboard/state verifier before accepting any goal label or score-changing commentary.",
            "Use ASR goal candidates only as weak retrieval windows, then verify with frame evidence.",
            "Force every generated goal to pass a monotonically increasing score-state check.",
            "Require unsupported player names to be backed by roster, jersey number OCR, or user metadata; otherwise say team/player role.",
            "Add a style linter that rejects repeated color-shirt descriptions in final broadcast text.",
            "Separate live goals, replays, halftime summaries, and historical mentions before commentary generation.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Commentary Output Audit / 解说输出审计",
        "",
        "EN: Evaluation-only report. Do not feed public facts into the target agent prompt.",
        "",
        "ZH: 本报告仅用于验证。不要把公开事实注入目标 Agent 的 prompt。",
        "",
        "## Summary / 摘要",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Expected Goal Sequence / 公开参考进球顺序",
            "",
            "| # | Score | Minute | Team | Scorer | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for goal in report["expected_goal_sequence"]:
        lines.append(
            f"| {goal['order']} | {goal['score_after']} | {goal['minute']} | "
            f"{goal['team']} | {goal['scorer']} | {goal['notes']} |"
        )

    lines.extend(
        [
            "",
            "## Generated Goal Alignment / 生成 goal 事件对齐",
            "",
            "| Event | Time | Score Claims | Nearest ASR | Distance | Excerpt |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["goal_alignment"]:
        claims = ", ".join(item["score_claims"]) if item["score_claims"] else "-"
        excerpt = item["text_excerpt"].replace("|", "/")
        lines.append(
            f"| {item['event_id']} | `{item['time']}` | {claims} | "
            f"{item['nearest_asr_candidate']} `{item['nearest_asr_time']}` | "
            f"{item['distance_to_asr_sec']}s | {excerpt} |"
        )

    lines.extend(
        [
            "",
            "## Issues / 问题",
            "",
            "| Severity | Category | Event | Time | Message |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for issue in report["issues"]:
        lines.append(
            f"| {issue['severity']} | {issue['category']} | {issue['event_id']} | "
            f"`{issue['time']}` | {issue['message']} |"
        )

    lines.extend(["", "## Recommendations / 改进建议", ""])
    for item in report["recommendations"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit generated commentary output.")
    parser.add_argument("--commentary", type=Path, default=DEFAULT_COMMENTARY)
    parser.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    parser.add_argument("--asr", type=Path, default=DEFAULT_ASR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()

    segments = parse_markdown_table(args.commentary)
    facts = json.loads(args.facts.read_text(encoding="utf-8"))
    asr_windows = json.loads(args.asr.read_text(encoding="utf-8"))
    report = audit(segments, facts, asr_windows)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
