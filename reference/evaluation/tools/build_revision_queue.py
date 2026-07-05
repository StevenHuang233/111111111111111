#!/usr/bin/env python
"""Build a prioritized revision queue from evaluation gate reports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
EVAL_ROOT = REPO_ROOT / "reference" / "evaluation"
DEFAULT_QUALITY = EVAL_ROOT / "commentary_quality_eval.json"
DEFAULT_ALIGNMENT = EVAL_ROOT / "goal_timeline_alignment.json"
DEFAULT_STYLE = EVAL_ROOT / "identity_style_audit.json"
DEFAULT_JSON = EVAL_ROOT / "revision_queue.json"
DEFAULT_MD = EVAL_ROOT / "revision_queue.md"

PRIORITY_RANK = {"Must": 0, "Should": 1, "Could": 2, "Later": 3}


def parse_time_label(value: str) -> int:
    match = re.search(r"(\d{2}):(\d{2}):(\d{2})", value or "")
    if not match:
        return 0
    hours, minutes, seconds = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_key(row: dict[str, Any]) -> str:
    event_id = str(row.get("event_id", "")).strip()
    time = str(row.get("time", "")).strip()
    return event_id or time or "unknown"


def add_issue(
    queue: dict[str, dict[str, Any]],
    row: dict[str, Any],
    *,
    issue: str,
    priority: str,
    action: str,
    rationale: str,
    source: str,
    details: dict[str, Any] | None = None,
) -> None:
    key = row_key(row)
    item = queue.setdefault(
        key,
        {
            "event_id": str(row.get("event_id", "")),
            "event_type": str(row.get("event_type", "")),
            "time": str(row.get("time", "")),
            "time_sort": parse_time_label(str(row.get("time", ""))),
            "excerpt": str(row.get("excerpt", "")),
            "highest_priority": priority,
            "issues": [],
        },
    )
    if PRIORITY_RANK[priority] < PRIORITY_RANK[item["highest_priority"]]:
        item["highest_priority"] = priority
    if not item.get("excerpt") and row.get("excerpt"):
        item["excerpt"] = str(row.get("excerpt", ""))
    item["issues"].append(
        {
            "issue": issue,
            "priority": priority,
            "action": action,
            "rationale": rationale,
            "source": source,
            "details": details or {},
        }
    )


def add_goal_alignment_issues(queue: dict[str, dict[str, Any]], alignment: dict[str, Any]) -> None:
    for row in alignment.get("extra_goal_assertions", []):
        state = row.get("expected_score_state", {}) if isinstance(row, dict) else {}
        add_issue(
            queue,
            row,
            issue="extra_goal_assertion",
            priority="Must",
            action="Suppress score-changing wording, or rewrite as replay/history/pending verification.",
            rationale="Generated goal/score assertion does not align with a verified scoreboard transition.",
            source="goal_timeline_alignment",
            details={
                "score_should_be": state.get("score_should_be"),
                "previous_goal_id": state.get("previous_goal_id"),
                "next_goal_id": state.get("next_goal_id"),
                "next_goal_window": state.get("next_goal_window"),
            },
        )

    for goal in alignment.get("verified_goals", []):
        assigned = goal.get("assigned_generated_events", []) if isinstance(goal, dict) else []
        if len(assigned) <= 1:
            continue
        for row in assigned[1:]:
            add_issue(
                queue,
                row,
                issue="duplicate_goal_near_verified_change",
                priority="Should",
                action="Merge with the primary verified goal segment, or demote to replay/celebration context.",
                rationale=f"Multiple generated segments map to verified goal {goal.get('goal_id')} {goal.get('score_change')}.",
                source="goal_timeline_alignment",
                details={
                    "goal_id": goal.get("goal_id"),
                    "score_change": goal.get("score_change"),
                    "verified_window": goal.get("verified_window"),
                },
            )


def add_style_issues(queue: dict[str, dict[str, Any]], style: dict[str, Any]) -> None:
    buckets = style.get("buckets", {})
    for row in buckets.get("wrong_entity", []):
        add_issue(
            queue,
            row,
            issue="wrong_entity",
            priority="Must",
            action="Remove or replace the wrong team/entity with verified match metadata.",
            rationale="Wrong team/entity is a factual blocker for final narration.",
            source="identity_style_audit",
            details={"entity": row.get("entity")},
        )
    for row in buckets.get("unsupported_name", []):
        add_issue(
            queue,
            row,
            issue="unsupported_name",
            priority="Must",
            action="Remove the name unless roster/OCR/broadcast graphic evidence supports it; use team+role/number instead.",
            rationale="Unsupported names are unsafe factual assertions.",
            source="identity_style_audit",
            details={"name": row.get("name")},
        )
    for row in buckets.get("color_identity", []):
        add_issue(
            queue,
            row,
            issue="color_identity_fallback",
            priority="Should",
            action="Rewrite through identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric.",
            rationale="Repeated color-subject wording sounds like raw frame description rather than broadcast commentary.",
            source="identity_style_audit",
            details={"patterns": row.get("patterns", [])},
        )
    for row in buckets.get("raw_visual", []):
        add_issue(
            queue,
            row,
            issue="raw_visual_wording",
            priority="Should",
            action="Convert camera/frame description into playable commentary, or keep it only for shots where the broadcast camera itself is meaningful.",
            rationale="Final narration should not read like direct image-caption output.",
            source="identity_style_audit",
            details={"patterns": row.get("patterns", [])},
        )


def add_quality_issues(queue: dict[str, dict[str, Any]], quality: dict[str, Any]) -> None:
    flags = quality.get("flags", {})
    for row in flags.get("prematch_action", []):
        add_issue(
            queue,
            row,
            issue="prematch_action_misclassification",
            priority="Must",
            action="Reclassify as opening/officials/broadcast context; do not narrate as match action.",
            rationale="Before kickoff, ceremony and broadcast graphics must not become fouls, VAR incidents, or restarts.",
            source="commentary_quality_eval",
        )
    for row in flags.get("mixed_language", []):
        add_issue(
            queue,
            row,
            issue="mixed_language_chinese",
            priority="Could",
            action="Run Chinese polish pass to remove stray English tokens unless they are official names/acronyms.",
            rationale="Mixed-language fragments reduce final narration polish.",
            source="commentary_quality_eval",
            details={"tokens": row.get("tokens", [])},
        )


def build_revision_queue(
    quality_path: str | Path = DEFAULT_QUALITY,
    alignment_path: str | Path = DEFAULT_ALIGNMENT,
    style_path: str | Path = DEFAULT_STYLE,
) -> dict[str, Any]:
    queue: dict[str, dict[str, Any]] = {}
    quality = load_json(Path(quality_path))
    alignment = load_json(Path(alignment_path))
    style = load_json(Path(style_path))
    add_goal_alignment_issues(queue, alignment)
    add_style_issues(queue, style)
    add_quality_issues(queue, quality)

    items = sorted(
        queue.values(),
        key=lambda item: (PRIORITY_RANK[item["highest_priority"]], item["time_sort"], item["event_id"]),
    )
    for item in items:
        item["issues"].sort(key=lambda issue: (PRIORITY_RANK[issue["priority"]], issue["issue"]))
        item.pop("time_sort", None)

    counts_by_priority: dict[str, int] = {}
    counts_by_issue: dict[str, int] = {}
    for item in items:
        counts_by_priority[item["highest_priority"]] = counts_by_priority.get(item["highest_priority"], 0) + 1
        for issue in item["issues"]:
            counts_by_issue[issue["issue"]] = counts_by_issue.get(issue["issue"], 0) + 1

    return {
        "policy": "Evaluation-only revision queue. Do not inject public references or manual-review facts into target-agent hidden context.",
        "summary": {
            "revision_items": len(items),
            "counts_by_priority": counts_by_priority,
            "counts_by_issue": counts_by_issue,
        },
        "items": items,
        "workflow": [
            {
                "step": "1",
                "en": "Fix Must items first: wrong entities, unsupported names, extra goal assertions, and prematch action mistakes.",
                "zh": "先处理 Must：错误实体、无依据姓名、额外进球声明、赛前动作误判。",
            },
            {
                "step": "2",
                "en": "Run final evaluation gates again; do not polish style before factual blockers are gone.",
                "zh": "重新运行终稿门禁；事实阻塞项清零前，不优先做风格润色。",
            },
            {
                "step": "3",
                "en": "Then handle Should items: duplicate goals, color fallback, and raw visual wording.",
                "zh": "再处理 Should：重复进球、颜色 fallback、原始画面式措辞。",
            },
        ],
    }


def write_markdown(report: dict[str, Any], path: Path, limit: int) -> None:
    summary = report["summary"]
    lines = [
        "# Revision Queue / 修订队列",
        "",
        "EN: This queue converts evaluation failures into concrete rewrite or suppression actions.",
        "",
        "ZH: 本队列把评测失败项转成具体的重写或抑制动作。",
        "",
        "## Summary / 摘要",
        "",
        f"- `revision_items`: {summary['revision_items']}",
        f"- `counts_by_priority`: {summary['counts_by_priority']}",
        f"- `counts_by_issue`: {summary['counts_by_issue']}",
        "",
        "## Workflow / 处理流程",
        "",
        "| Step | EN | ZH |",
        "| --- | --- | --- |",
    ]
    for step in report["workflow"]:
        lines.append(f"| {step['step']} | {step['en']} | {step['zh']} |")

    lines.extend(
        [
            "",
            "## Queue / 队列",
            "",
            "| Priority | Event | Type | Time | Issues | First Action | Excerpt |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["items"][:limit]:
        issues = ", ".join(issue["issue"] for issue in item["issues"])
        first_action = item["issues"][0]["action"] if item["issues"] else "-"
        excerpt = str(item.get("excerpt", "")).replace("|", "/")
        lines.append(
            f"| {item['highest_priority']} | {item['event_id']} | {item['event_type']} | `{item['time']}` | "
            f"{issues} | {first_action} | {excerpt[:180]} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a prioritized revision queue from evaluation reports.")
    parser.add_argument("--quality", type=Path, default=DEFAULT_QUALITY)
    parser.add_argument("--alignment", type=Path, default=DEFAULT_ALIGNMENT)
    parser.add_argument("--style", type=Path, default=DEFAULT_STYLE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--md-limit", type=int, default=60)
    args = parser.parse_args()

    report = build_revision_queue(args.quality, args.alignment, args.style)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md, max(1, args.md_limit))
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
