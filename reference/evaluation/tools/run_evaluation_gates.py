#!/usr/bin/env python
"""Run all final-output evaluation gates for the commentary harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_identity_style
import compare_goal_timeline
import evaluate_commentary_quality


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual.json"
DEFAULT_FACTS = REPO_ROOT / "reference" / "evaluation" / "germany_curacao_public_reference.json"
DEFAULT_MANUAL_REVIEW = REPO_ROOT / "reference" / "evaluation" / "goal_scoreboard_manual_review.md"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "final_evaluation_gates.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "final_evaluation_gates.md"


def gate_rank(status: str) -> int:
    return {"pass": 0, "pass_with_warnings": 1, "fail": 2}.get(status, 2)


def overall_status(statuses: list[str]) -> str:
    worst = max((gate_rank(status) for status in statuses), default=0)
    if worst >= 2:
        return "fail"
    if worst == 1:
        return "pass_with_warnings"
    return "pass"


def summarize_quality(report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    gate = report["quality_gate"]
    return {
        "status": gate["status"],
        "blockers": gate["blockers"],
        "warnings": gate["warnings"],
        "key_metrics": {
            "generated_goal_count": summary["generated_goal_count"],
            "verified_goal_count": summary["verified_goal_count"],
            "goal_overcount": summary["goal_overcount"],
            "score_claim_segments": summary["score_claim_segments"],
            "wrong_entity_segments": summary["wrong_entity_segments"],
            "style_color_identity_segments": summary["style_color_identity_segments"],
        },
    }


def summarize_alignment(report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    gate = report["alignment_gate"]
    return {
        "status": gate["status"],
        "blockers": gate["blockers"],
        "warnings": gate["warnings"],
        "key_metrics": {
            "verified_score_changes": summary["verified_score_changes"],
            "generated_goal_type_segments": summary["generated_goal_type_segments"],
            "generated_goal_assertion_segments": summary["generated_goal_assertion_segments"],
            "covered_verified_goals": summary["covered_verified_goals"],
            "missing_verified_goals": summary["missing_verified_goals"],
            "duplicate_verified_goal_groups": summary["duplicate_verified_goal_groups"],
            "extra_goal_assertions": summary["extra_goal_assertions"],
        },
    }


def summarize_style(report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    gate = report["style_gate"]
    return {
        "status": gate["status"],
        "blockers": gate["blockers"],
        "warnings": gate["warnings"],
        "key_metrics": {
            "color_identity_segments": summary["color_identity_segments"],
            "raw_visual_segments": summary["raw_visual_segments"],
            "wrong_entity_segments": summary["wrong_entity_segments"],
            "unsupported_name_segments": summary["unsupported_name_segments"],
            "color_identity_ratio": summary["color_identity_ratio"],
            "raw_visual_ratio": summary["raw_visual_ratio"],
        },
    }


def build_recommendations(report: dict[str, Any]) -> list[dict[str, str]]:
    recommendations: list[dict[str, str]] = []
    gates = report["gates"]
    if gates["goal_alignment"]["status"] == "fail":
        recommendations.append(
            {
                "priority": "Must",
                "area": "Goal precision",
                "en": "Enable goal verification plus score-state suppression before accepting final narration.",
                "zh": "接受最终解说前，必须启用进球验证与比分状态抑制，降低假进球。",
            }
        )
    if gates["identity_style"]["status"] == "fail":
        recommendations.append(
            {
                "priority": "Must",
                "area": "Fact safety",
                "en": "Block wrong teams and unsupported names, then rewrite identity wording through the verified-name cascade.",
                "zh": "拦截错误球队和无依据姓名，再通过已验证姓名级联重写身份措辞。",
            }
        )
    if gates["quality"]["status"] == "fail":
        recommendations.append(
            {
                "priority": "Must",
                "area": "Final output audit",
                "en": "Do not use this generated file directly for the demo video or route speech.",
                "zh": "不要把当前生成文件直接用于 demo 视频或路演解说稿。",
            }
        )
    if not recommendations:
        recommendations.append(
            {
                "priority": "Should",
                "area": "Manual review",
                "en": "Perform a short manual review of high-stakes events before packaging.",
                "zh": "打包前仍应对高风险事件做短人工复核。",
            }
        )
    return recommendations


def run_gates(
    input_path: str | Path = DEFAULT_INPUT,
    facts_path: str | Path = DEFAULT_FACTS,
    manual_review_path: str | Path = DEFAULT_MANUAL_REVIEW,
    refresh_reports: bool = True,
) -> dict[str, Any]:
    input_path = Path(input_path)
    facts_path = Path(facts_path)
    manual_review_path = Path(manual_review_path)

    quality_report = evaluate_commentary_quality.evaluate_commentary_quality(input_path, facts_path, manual_review_path)
    alignment_report = compare_goal_timeline.align_goal_timeline(input_path, manual_review_path)
    style_report = audit_identity_style.audit_identity_style(input_path, facts_path)

    if refresh_reports:
        quality_json = REPO_ROOT / "reference" / "evaluation" / "commentary_quality_eval.json"
        quality_md = REPO_ROOT / "reference" / "evaluation" / "commentary_quality_eval.md"
        alignment_json = REPO_ROOT / "reference" / "evaluation" / "goal_timeline_alignment.json"
        alignment_md = REPO_ROOT / "reference" / "evaluation" / "goal_timeline_alignment.md"
        style_json = REPO_ROOT / "reference" / "evaluation" / "identity_style_audit.json"
        style_md = REPO_ROOT / "reference" / "evaluation" / "identity_style_audit.md"
        quality_json.write_text(json.dumps(quality_report, ensure_ascii=False, indent=2), encoding="utf-8")
        evaluate_commentary_quality.write_markdown(quality_report, quality_md)
        alignment_json.write_text(json.dumps(alignment_report, ensure_ascii=False, indent=2), encoding="utf-8")
        compare_goal_timeline.write_markdown(alignment_report, alignment_md)
        style_json.write_text(json.dumps(style_report, ensure_ascii=False, indent=2), encoding="utf-8")
        audit_identity_style.write_markdown(style_report, style_md)

    gates = {
        "quality": summarize_quality(quality_report),
        "goal_alignment": summarize_alignment(alignment_report),
        "identity_style": summarize_style(style_report),
    }
    status = overall_status([gate["status"] for gate in gates.values()])
    try:
        input_label = str(input_path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        input_label = str(input_path)
    report = {
        "policy": "Evaluation-only. Do not inject public references, manual review, or gate outputs into target-agent prompt/runtime context.",
        "overall_status": status,
        "input": input_label,
        "gates": gates,
        "recommendations": [],
    }
    report["recommendations"] = build_recommendations(report)
    return report


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Final Evaluation Gates / 终稿评测门禁",
        "",
        "EN: This report aggregates quality, goal-timeline, and identity/style gates for the generated commentary.",
        "",
        "ZH: 本报告汇总生成解说的质量、进球时间线、身份与风格三类门禁。",
        "",
        f"- `overall_status`: {report['overall_status']}",
        f"- `input`: `{report['input']}`",
        "",
        "## Gates / 门禁",
        "",
        "| Gate | Status | Blockers | Warnings | Key Metrics |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, gate in report["gates"].items():
        metrics = ", ".join(f"{key}={value}" for key, value in gate["key_metrics"].items())
        blockers = ", ".join(gate["blockers"]) or "-"
        warnings = ", ".join(gate["warnings"]) or "-"
        lines.append(f"| {name} | {gate['status']} | {blockers} | {warnings} | {metrics} |")

    lines.extend(["", "## Recommendations / 建议", "", "| Priority | Area | EN | ZH |", "| --- | --- | --- | --- |"])
    for item in report["recommendations"]:
        lines.append(f"| {item['priority']} | {item['area']} | {item['en']} | {item['zh']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all final-output commentary evaluation gates.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    parser.add_argument("--manual-review", type=Path, default=DEFAULT_MANUAL_REVIEW)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--no-refresh-reports", action="store_true")
    parser.add_argument("--fail-on-any", action="store_true", help="Return exit code 2 when any gate fails.")
    args = parser.parse_args()

    report = run_gates(args.input, args.facts, args.manual_review, refresh_reports=not args.no_refresh_reports)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps({"overall_status": report["overall_status"], "gates": report["gates"]}, ensure_ascii=False, indent=2))
    if args.fail_on_any and report["overall_status"] == "fail":
        print("final_evaluation_gates_status=fail")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
