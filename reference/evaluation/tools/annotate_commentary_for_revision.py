#!/usr/bin/env python
"""Annotate generated commentary with revision actions.

This is intentionally non-destructive: it does not rewrite commentary text or
invent corrected facts. It attaches review metadata so a human or a later
revision agent can decide what to suppress, verify, or rewrite.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual.json"
DEFAULT_QUEUE = REPO_ROOT / "reference" / "evaluation" / "revision_queue.json"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "commentary_revision_annotations.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "commentary_revision_annotations.md"
PRIORITY_RANK = {"Must": 0, "Should": 1, "Could": 2, "Later": 3}


def display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def queue_by_event(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in queue.get("items", []):
        if not isinstance(item, dict):
            continue
        event_id = str(item.get("event_id", "")).strip()
        if event_id:
            result[event_id] = item
    return result


def issue_names(item: dict[str, Any]) -> list[str]:
    return [str(issue.get("issue", "")) for issue in item.get("issues", []) if isinstance(issue, dict)]


def actions(item: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for issue in item.get("issues", []):
        if not isinstance(issue, dict):
            continue
        action = str(issue.get("action", "")).strip()
        if action and action not in values:
            values.append(action)
    return values


def review_status(priority: str) -> str:
    if priority == "Must":
        return "blocker"
    if priority == "Should":
        return "warning"
    if priority == "Could":
        return "polish"
    return "clear"


def recommended_policy(names: list[str], priority: str) -> dict[str, Any]:
    policy = {
        "use_in_final_demo": priority not in {"Must"},
        "requires_manual_review": priority == "Must",
        "score_change_allowed": "extra_goal_assertion" not in names,
        "fact_claim_allowed": not ({"wrong_entity", "unsupported_name"} & set(names)),
        "style_rewrite_needed": bool({"color_identity_fallback", "raw_visual_wording", "mixed_language_chinese"} & set(names)),
        "suggested_treatment": "keep",
    }
    if "extra_goal_assertion" in names:
        policy["suggested_treatment"] = "suppress_score_change_or_rewrite_as_replay_history_pending"
    elif {"wrong_entity", "unsupported_name"} & set(names):
        policy["suggested_treatment"] = "remove_unsafe_fact_or_replace_with_verified_team_role_number"
    elif "prematch_action_misclassification" in names:
        policy["suggested_treatment"] = "rewrite_as_opening_officials_broadcast_context"
    elif policy["style_rewrite_needed"]:
        policy["suggested_treatment"] = "rewrite_for_broadcast_style"
    return policy


def annotate_commentary(
    input_path: str | Path = DEFAULT_INPUT,
    queue_path: str | Path = DEFAULT_QUEUE,
) -> dict[str, Any]:
    commentary = load_json(Path(input_path))
    queue = load_json(Path(queue_path))
    by_event = queue_by_event(queue)

    annotated_segments: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    policy_counts: dict[str, int] = {
        "not_for_final_demo": 0,
        "score_change_not_allowed": 0,
        "unsafe_fact_claim": 0,
        "style_rewrite_needed": 0,
    }
    for segment in commentary.get("segments", []):
        if not isinstance(segment, dict):
            continue
        event_id = str(segment.get("event_id", ""))
        queue_item = by_event.get(event_id)
        if queue_item:
            priority = str(queue_item.get("highest_priority", "Later"))
            names = issue_names(queue_item)
            policy = recommended_policy(names, priority)
            review = {
                "status": review_status(priority),
                "priority": priority,
                "issues": names,
                "actions": actions(queue_item),
                "policy": policy,
            }
        else:
            review = {
                "status": "clear",
                "priority": "Later",
                "issues": [],
                "actions": [],
                "policy": recommended_policy([], "Later"),
            }
        status_counts[review["status"]] = status_counts.get(review["status"], 0) + 1
        if not review["policy"]["use_in_final_demo"]:
            policy_counts["not_for_final_demo"] += 1
        if not review["policy"]["score_change_allowed"]:
            policy_counts["score_change_not_allowed"] += 1
        if not review["policy"]["fact_claim_allowed"]:
            policy_counts["unsafe_fact_claim"] += 1
        if review["policy"]["style_rewrite_needed"]:
            policy_counts["style_rewrite_needed"] += 1

        copy = dict(segment)
        copy["review"] = review
        annotated_segments.append(copy)

    payload = {
        "policy": "Evaluation-only revision annotation. Do not inject public references or manual-review facts into target-agent hidden context.",
        "source_commentary": display_path(input_path),
        "source_revision_queue": display_path(queue_path),
        "summary": {
            "segments": len(annotated_segments),
            "status_counts": status_counts,
            "policy_counts": policy_counts,
        },
        "segments": annotated_segments,
    }
    return payload


def segment_text(segment: dict[str, Any]) -> str:
    chinese = segment.get("chinese", {})
    english = segment.get("english", {})
    zh = chinese.get("commentary_text", "") if isinstance(chinese, dict) else ""
    en = english.get("commentary_text", "") if isinstance(english, dict) else ""
    return (zh or en or "").replace("|", "/")[:180]


def stamp(seconds: Any) -> str:
    total = max(0, int(round(float(seconds))))
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def write_markdown(payload: dict[str, Any], path: Path, limit: int) -> None:
    summary = payload["summary"]
    lines = [
        "# Commentary Revision Annotations / 解说修订标注",
        "",
        "EN: This file marks which generated segments are blocked, warning-only, or clear for final use.",
        "",
        "ZH: 本文件标注生成解说中哪些片段属于阻塞、仅警告或可保留。",
        "",
        "## Summary / 摘要",
        "",
        f"- `segments`: {summary['segments']}",
        f"- `status_counts`: {summary['status_counts']}",
        f"- `policy_counts`: {summary['policy_counts']}",
        "",
        "## Blockers / 阻塞片段",
        "",
        "| Event | Type | Time | Issues | Suggested Treatment | Excerpt |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    rows = [segment for segment in payload["segments"] if segment.get("review", {}).get("status") == "blocker"]
    for segment in rows[:limit]:
        review = segment["review"]
        time_range = f"{stamp(segment.get('talk_start_sec', 0.0))}-{stamp(segment.get('talk_end_sec', 0.0))}"
        lines.append(
            f"| {segment.get('event_id')} | {segment.get('event_type')} | "
            f"`{time_range}` | "
            f"{', '.join(review['issues'])} | {review['policy']['suggested_treatment']} | {segment_text(segment)} |"
        )
    if not rows:
        lines.append("| - | - | - | - | - | - |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotate commentary segments with revision-queue metadata.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--md-limit", type=int, default=80)
    args = parser.parse_args()

    payload = annotate_commentary(args.input, args.queue)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload, args.output_md, max(1, args.md_limit))
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
