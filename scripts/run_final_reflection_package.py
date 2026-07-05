#!/usr/bin/env python
"""One-shot final reflection, evaluation, and SRT packaging.

This script intentionally composes existing tools by path. It does not require
merging a night branch; provide the latest night/final JSON outputs as inputs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual-final-unreflected.json"
DEFAULT_EVENTS = REPO_ROOT / "outputs" / "events-night.json"
DEFAULT_REFLECTED = REPO_ROOT / "outputs" / "commentary_bilingual-final-reflected.json"
DEFAULT_REPORT_DIR = REPO_ROOT / "reference" / "evaluation" / "final_reflection"
DEFAULT_SRT_DIR = REPO_ROOT / "outputs" / "srt" / "final_reflected"
DEFAULT_MANUAL_REVIEW = REPO_ROOT / "reference" / "evaluation" / "goal_scoreboard_manual_review.md"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def run_command(args: list[str]) -> None:
    print("+ " + subprocess.list2cmdline(args), flush=True)
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def srt_stats(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    entries = sum(1 for block in text.split("\n\n") if block.strip())
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "entries": entries,
    }


def write_manifest(
    *,
    path_json: Path,
    path_md: Path,
    input_path: Path,
    reflected_path: Path,
    events_path: Path,
    report_dir: Path,
    srt_dir: Path,
    srt_files: list[Path],
) -> None:
    final_gate = load_json(report_dir / "final_evaluation_gates-final-after.json")
    reflection = load_json(report_dir / "goal_reflection_report-final.json")
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input": rel(input_path),
        "events": rel(events_path),
        "reflected_output": rel(reflected_path),
        "report_dir": rel(report_dir),
        "srt_dir": rel(srt_dir),
        "reflection_summary": reflection.get("summary", {}),
        "final_gate": {
            "overall_status": final_gate.get("overall_status"),
            "gates": final_gate.get("gates", {}),
        },
        "srt_files": [srt_stats(path) for path in srt_files],
    }
    path_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Final Reflection Package Manifest / 最终反思打包清单",
        "",
        "EN: This file records the one-shot reflected commentary, evaluation reports, and SRT exports.",
        "",
        "ZH: 本文件记录一键生成的反思后解说、评测报告和 SRT 字幕导出。",
        "",
        "## Inputs / 输入",
        "",
        f"- `input`: `{manifest['input']}`",
        f"- `events`: `{manifest['events']}`",
        f"- `reflected_output`: `{manifest['reflected_output']}`",
        "",
        "## Gate Summary / 门禁摘要",
        "",
        f"- `overall_status`: {manifest['final_gate']['overall_status']}",
        f"- `primary_verified_goal_segments`: {manifest['reflection_summary'].get('primary_verified_goal_segments')}",
        f"- `rewritten_false_positive_segments`: {manifest['reflection_summary'].get('rewritten_false_positive_segments')}",
        f"- `remaining_goal_type_segments`: {manifest['reflection_summary'].get('remaining_goal_type_segments')}",
        "",
        "## SRT Files / SRT 文件",
        "",
        "| File | Entries | Bytes |",
        "| --- | --- | --- |",
    ]
    for item in manifest["srt_files"]:
        lines.append(f"| `{item['path']}` | {item['entries']} | {item['bytes']} |")
    path_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run final reflection, evaluation gates, and SRT export in one command.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--manual-review", type=Path, default=DEFAULT_MANUAL_REVIEW)
    parser.add_argument("--reflected-output", type=Path, default=DEFAULT_REFLECTED)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--srt-output-dir", type=Path, default=DEFAULT_SRT_DIR)
    parser.add_argument("--languages", default="all")
    parser.add_argument("--text-source", default="both", choices=("subtitle", "commentary", "both"))
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    report_dir = args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "reference" / "evaluation" / "tools" / "postprocess_goal_reflection.py"),
            "--input",
            str(args.input),
            "--events",
            str(args.events),
            "--manual-review",
            str(args.manual_review),
            "--output",
            str(args.reflected_output),
            "--report-json",
            str(report_dir / "goal_reflection_report-final.json"),
            "--report-md",
            str(report_dir / "goal_reflection_report-final.md"),
        ]
    )
    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "reference" / "evaluation" / "tools" / "evaluate_commentary_quality.py"),
            "--input",
            str(args.reflected_output),
            "--output-json",
            str(report_dir / "commentary_quality_eval-final-after.json"),
            "--output-md",
            str(report_dir / "commentary_quality_eval-final-after.md"),
        ]
    )
    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "reference" / "evaluation" / "tools" / "compare_goal_timeline.py"),
            "--input",
            str(args.reflected_output),
            "--output-json",
            str(report_dir / "goal_timeline_alignment-final-after.json"),
            "--output-md",
            str(report_dir / "goal_timeline_alignment-final-after.md"),
        ]
    )
    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "reference" / "evaluation" / "tools" / "audit_identity_style.py"),
            "--input",
            str(args.reflected_output),
            "--output-json",
            str(report_dir / "identity_style_audit-final-after.json"),
            "--output-md",
            str(report_dir / "identity_style_audit-final-after.md"),
        ]
    )
    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "reference" / "evaluation" / "tools" / "run_evaluation_gates.py"),
            "--input",
            str(args.reflected_output),
            "--output-json",
            str(report_dir / "final_evaluation_gates-final-after.json"),
            "--output-md",
            str(report_dir / "final_evaluation_gates-final-after.md"),
        ]
    )
    run_command(
        [
            args.python,
            "-B",
            str(REPO_ROOT / "scripts" / "export_commentary_srt.py"),
            "--input",
            str(args.reflected_output),
            "--output-dir",
            str(args.srt_output_dir),
            "--text-source",
            args.text_source,
            "--languages",
            args.languages,
        ]
    )
    srt_files = sorted(args.srt_output_dir.glob("*.srt"))
    write_manifest(
        path_json=report_dir / "final_reflection_package_manifest.json",
        path_md=report_dir / "final_reflection_package_manifest.md",
        input_path=args.input,
        reflected_path=args.reflected_output,
        events_path=args.events,
        report_dir=report_dir,
        srt_dir=args.srt_output_dir,
        srt_files=srt_files,
    )
    print(f"manifest={rel(report_dir / 'final_reflection_package_manifest.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
