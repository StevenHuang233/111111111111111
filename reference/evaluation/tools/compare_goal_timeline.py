#!/usr/bin/env python
"""Align generated goal claims with manually verified scoreboard changes.

Evaluation-only. This tool may use manual review evidence and public facts, but
the target commentary agent must not receive these references as hidden context.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual.json"
DEFAULT_MANUAL_REVIEW = REPO_ROOT / "reference" / "evaluation" / "goal_scoreboard_manual_review.md"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "goal_timeline_alignment.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "goal_timeline_alignment.md"

TEXTUAL_GOAL_PATTERNS = (
    r"\bscores?\b",
    r"\btakes? the lead\b",
    r"\bdoubles? (?:their|the) lead\b",
    r"\bextends? (?:their|the) lead\b",
    r"\bgoes? up\b",
    r"\bequali[sz]es?\b",
    r"\bfinds? the back of the net\b",
    r"\bback of the net\b",
    r"\binto the net\b",
    r"\bgoal is confirmed\b",
    r"取得领先",
    r"扩大领先",
    r"扳平",
    r"破门",
    r"球进",
    r"进球",
)
NEGATION_HINTS = (
    "no goal",
    "not a goal",
    "does not count",
    "ruled out",
    "offside",
    "disallowed",
    "missed opportunity",
    "save",
    "saves",
    "parry",
    "parries",
    "deny",
    "denies",
    "clear",
    "clears",
    "blocked",
    "miss",
    "misses",
    "没有进",
    "不算",
    "越位",
    "被吹",
    "错失",
    "扑救",
    "扑出",
    "挡出",
    "解围",
    "阻止",
)


@dataclass(frozen=True)
class VerifiedGoal:
    goal_id: str
    score_before: str
    score_after: str
    start_sec: float
    end_sec: float
    evidence_window: str
    match_clock: str
    status: str


@dataclass(frozen=True)
class GeneratedSegment:
    event_id: str
    event_type: str
    start_sec: float
    end_sec: float
    english: str
    chinese: str

    @property
    def midpoint_sec(self) -> float:
        return (self.start_sec + self.end_sec) / 2.0

    @property
    def text(self) -> str:
        return f"{self.english}\n{self.chinese}".strip()


def parse_time(value: str) -> float:
    parts = [int(part) for part in value.strip().split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Unsupported timestamp: {value}")


def stamp(seconds: float) -> str:
    value = max(0, int(round(seconds)))
    minutes, sec = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def excerpt(text: str, limit: int = 180) -> str:
    return text.replace("\n", " / ").replace("|", "/")[:limit]


def load_verified_goals(path: Path) -> list[VerifiedGoal]:
    goals: list[VerifiedGoal] = []
    pattern = re.compile(
        r"^\|\s*(G\d+)\s*\|\s*([^|]+?)\s*->\s*([^|]+?)\s*\|\s*`([^`]+)`\s*to\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*to\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        goal_id, score_before, score_after, start_evidence, end_evidence, clock_start, clock_end, status = match.groups()
        video_start = start_evidence.split()[0]
        video_end = end_evidence.split()[0]
        goals.append(
            VerifiedGoal(
                goal_id=goal_id,
                score_before=score_before.strip(),
                score_after=score_after.strip(),
                start_sec=parse_time(video_start),
                end_sec=parse_time(video_end),
                evidence_window=f"{start_evidence} to {end_evidence}",
                match_clock=f"{clock_start} to {clock_end}",
                status=status.strip(),
            )
        )
    return goals


def load_segments(path: Path) -> list[GeneratedSegment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments: list[GeneratedSegment] = []
    for item in data.get("segments", []):
        if not isinstance(item, dict):
            continue
        english = item.get("english", {})
        chinese = item.get("chinese", {})
        segments.append(
            GeneratedSegment(
                event_id=str(item.get("event_id", "")),
                event_type=str(item.get("event_type", "")),
                start_sec=float(item.get("talk_start_sec", 0.0)),
                end_sec=float(item.get("talk_end_sec", 0.0)),
                english=str(english.get("commentary_text", "")) if isinstance(english, dict) else "",
                chinese=str(chinese.get("commentary_text", "")) if isinstance(chinese, dict) else "",
            )
        )
    return segments


def has_goal_assertion(segment: GeneratedSegment) -> bool:
    text = segment.text
    lowered = text.lower()
    if segment.event_type == "goal":
        return True
    if any(hint in lowered for hint in NEGATION_HINTS):
        return False
    return any(re.search(pattern, text, re.I) for pattern in TEXTUAL_GOAL_PATTERNS)


def alignment_gate(summary: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if summary["missing_verified_goals"] > 0:
        blockers.append("missing_verified_goals")
    if summary["extra_goal_assertions"] > 0:
        blockers.append("extra_goal_assertions")
    if summary["duplicate_verified_goal_groups"] > 0:
        warnings.append("duplicate_verified_goal_groups")
    return {
        "status": "fail" if blockers else "pass_with_warnings" if warnings else "pass",
        "blockers": blockers,
        "warnings": warnings,
        "en": "Fail means goal/score assertions are not aligned with verified scoreboard changes.",
        "zh": "fail 表示进球/比分声明没有与已核验比分牌变化对齐。",
    }


def overlaps_or_near(segment: GeneratedSegment, goal: VerifiedGoal, before_sec: float, after_sec: float) -> bool:
    return segment.end_sec >= goal.start_sec - before_sec and segment.start_sec <= goal.end_sec + after_sec


def expected_score_state(goals: list[VerifiedGoal], timestamp_sec: float) -> dict[str, Any]:
    previous: VerifiedGoal | None = None
    upcoming: VerifiedGoal | None = None
    for goal in goals:
        if goal.end_sec <= timestamp_sec:
            previous = goal
        elif goal.start_sec > timestamp_sec and upcoming is None:
            upcoming = goal
    return {
        "score_should_be": previous.score_after if previous else "0-0",
        "previous_goal_id": previous.goal_id if previous else None,
        "next_goal_id": upcoming.goal_id if upcoming else None,
        "next_goal_window": f"{stamp(upcoming.start_sec)}-{stamp(upcoming.end_sec)}" if upcoming else None,
    }


def align_goal_timeline(
    input_path: str | Path = DEFAULT_INPUT,
    manual_review_path: str | Path = DEFAULT_MANUAL_REVIEW,
    before_sec: float = 45.0,
    after_sec: float = 90.0,
) -> dict[str, Any]:
    goals = load_verified_goals(Path(manual_review_path))
    segments = load_segments(Path(input_path))
    assertions = [segment for segment in segments if has_goal_assertion(segment)]
    goal_type_segments = [segment for segment in segments if segment.event_type == "goal"]

    assigned: dict[str, list[GeneratedSegment]] = {goal.goal_id: [] for goal in goals}
    assigned_event_ids: set[str] = set()
    for segment in assertions:
        candidate_goals = [goal for goal in goals if overlaps_or_near(segment, goal, before_sec, after_sec)]
        if not candidate_goals:
            continue
        nearest = min(candidate_goals, key=lambda goal: abs(segment.midpoint_sec - ((goal.start_sec + goal.end_sec) / 2.0)))
        assigned[nearest.goal_id].append(segment)
        assigned_event_ids.add(segment.event_id)

    verified_rows = []
    missing_goal_ids: list[str] = []
    duplicate_goal_ids: list[str] = []
    for goal in goals:
        rows = sorted(assigned[goal.goal_id], key=lambda item: (item.start_sec, item.event_id))
        if not rows:
            status = "missing_generated_goal_claim"
            missing_goal_ids.append(goal.goal_id)
        elif len(rows) == 1:
            status = "covered"
        else:
            status = "covered_with_duplicates"
            duplicate_goal_ids.append(goal.goal_id)
        verified_rows.append(
            {
                "goal_id": goal.goal_id,
                "score_change": f"{goal.score_before} -> {goal.score_after}",
                "verified_window": f"{stamp(goal.start_sec)}-{stamp(goal.end_sec)}",
                "match_clock": goal.match_clock,
                "status": status,
                "assigned_generated_events": [
                    {
                        "event_id": segment.event_id,
                        "event_type": segment.event_type,
                        "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                        "excerpt": excerpt(segment.text),
                    }
                    for segment in rows
                ],
            }
        )

    extra_rows = []
    for segment in assertions:
        if segment.event_id in assigned_event_ids:
            continue
        state = expected_score_state(goals, segment.midpoint_sec)
        extra_rows.append(
            {
                "event_id": segment.event_id,
                "event_type": segment.event_type,
                "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
                "expected_score_state": state,
                "reason": "goal_or_score_assertion_not_near_verified_score_change",
                "excerpt": excerpt(segment.text),
            }
        )

    summary = {
        "verified_score_changes": len(goals),
        "generated_goal_type_segments": len(goal_type_segments),
        "generated_goal_assertion_segments": len(assertions),
        "covered_verified_goals": sum(1 for row in verified_rows if row["status"] != "missing_generated_goal_claim"),
        "missing_verified_goals": len(missing_goal_ids),
        "duplicate_verified_goal_groups": len(duplicate_goal_ids),
        "extra_goal_assertions": len(extra_rows),
        "alignment_before_sec": before_sec,
        "alignment_after_sec": after_sec,
    }
    return {
        "policy": "Evaluation-only. Do not inject this report into target-agent prompt/runtime context.",
        "summary": summary,
        "alignment_gate": alignment_gate(summary),
        "verified_goals": verified_rows,
        "extra_goal_assertions": extra_rows,
        "missing_goal_ids": missing_goal_ids,
        "duplicate_goal_ids": duplicate_goal_ids,
        "recommendations": [
            {
                "priority": "Must",
                "en": "Only allow a final score-changing goal claim when it is aligned with a verified scoreboard state transition or passes a live-goal verifier.",
                "zh": "只有当进球宣称能对齐已核验比分牌变化，或通过现场进球验证器时，才允许改变最终比分状态。",
            },
            {
                "priority": "Must",
                "en": "Treat unaligned goal assertions as replay, historical mention, possible disallowed goal, or manual-review pending instead of incrementing score.",
                "zh": "未对齐的进球宣称应视为回放、历史提及、可能被吹或待人工复核，不应直接推进比分。",
            },
            {
                "priority": "Should",
                "en": "Use this report after every full run to decide whether to rerun goal verification, narrow frames around false positives, or rewrite final commentary.",
                "zh": "每次全量运行后使用本报告判断是否重跑进球验证、收窄假阳性片段，或重写最终解说。",
            },
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Goal Timeline Alignment / 进球时间线对齐",
        "",
        "EN: This report aligns generated goal/score assertions with manually verified scoreboard changes.",
        "",
        "ZH: 本报告将生成的进球/比分声明与人工核验的比分牌变化进行对齐。",
        "",
        "## Summary / 摘要",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    gate = report["alignment_gate"]
    lines.extend(
        [
            "",
            "## Alignment Gate / 对齐门禁",
            "",
            f"- `status`: {gate['status']}",
            f"- `blockers`: {', '.join(gate['blockers']) or '-'}",
            f"- `warnings`: {', '.join(gate['warnings']) or '-'}",
            f"- EN: {gate['en']}",
            f"- ZH: {gate['zh']}",
        ]
    )

    lines.extend(
        [
            "",
            "## Verified Score Changes / 已核验比分变化覆盖情况",
            "",
            "| Goal | Score Change | Window | Status | Assigned Generated Events |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["verified_goals"]:
        assigned = ", ".join(
            f"{item['event_id']} `{item['time']}`" for item in row["assigned_generated_events"]
        )
        lines.append(
            f"| {row['goal_id']} | {row['score_change']} | `{row['verified_window']}` | {row['status']} | {assigned or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Extra Goal Assertions / 额外进球声明",
            "",
            "| Event | Type | Time | Expected Score State | Next Verified Goal | Excerpt |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["extra_goal_assertions"][:30]:
        state = row["expected_score_state"]
        lines.append(
            f"| {row['event_id']} | {row['event_type']} | `{row['time']}` | "
            f"{state['score_should_be']} | {state['next_goal_id'] or '-'} {state['next_goal_window'] or ''} | {row['excerpt']} |"
        )
    if not report["extra_goal_assertions"]:
        lines.append("| - | - | - | - | - | - |")

    lines.extend(["", "## Recommendations / 建议", "", "| Priority | EN | ZH |", "| --- | --- | --- |"])
    for item in report["recommendations"]:
        lines.append(f"| {item['priority']} | {item['en']} | {item['zh']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare generated goal timeline with verified scoreboard changes.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--manual-review", type=Path, default=DEFAULT_MANUAL_REVIEW)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--before-sec", type=float, default=45.0)
    parser.add_argument("--after-sec", type=float, default=90.0)
    parser.add_argument(
        "--fail-on-alignment",
        action="store_true",
        help="Return exit code 2 when missing or extra goal assertions are found.",
    )
    args = parser.parse_args()

    report = align_goal_timeline(args.input, args.manual_review, args.before_sec, args.after_sec)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if args.fail_on_alignment and report["alignment_gate"]["status"] == "fail":
        print("alignment_gate_status=fail")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
