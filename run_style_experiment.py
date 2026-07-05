from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from harness import (
    EventCandidate,
    EventPhase,
    TraceRecorder,
    TranslationConfig,
    VisualCommentaryConfig,
    dump_bilingual_commentary_result,
    generate_bilingual_commentary,
    load_manifest,
    load_match_context,
    load_style,
)
from intern_client import InternClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run small bilingual style experiments from an existing events JSON.")
    parser.add_argument("--full-manifest", default=r"C:\Users\hjj\Desktop\frames_4fps_q3\frames_manifest.json")
    parser.add_argument(
        "--events-json",
        default=r"outputs\coarse_new_boundary_20260704_223738\goal_validation\refined_events.json",
    )
    parser.add_argument("--output-dir", default=r"outputs\nightwork_style_experiment")
    parser.add_argument("--styles", default="storytelling_witty,elite_broadcast_replay")
    parser.add_argument("--event-ids", default="U036,U149,U225")
    parser.add_argument("--match-context", default="germany_curacao_world_cup_2026")
    parser.add_argument("--commentary-sample-fps", type=float, default=0.5)
    parser.add_argument("--max-frames-per-event", type=int, default=10)
    parser.add_argument("--max-frames-per-phase", type=int, default=3)
    parser.add_argument("--trace-max-text-chars", type=int, default=20000)
    args = parser.parse_args()

    manifest = load_manifest(args.full_manifest)
    events = load_events(args.events_json)
    wanted_ids = [item.strip() for item in args.event_ids.split(",") if item.strip()]
    selected_events = [event for event in events if event.event_id in wanted_ids]
    missing = sorted(set(wanted_ids) - {event.event_id for event in selected_events})
    if missing:
        raise SystemExit(f"Missing event ids in events JSON: {', '.join(missing)}")

    context = load_match_context(args.match_context)
    style_ids = [item.strip() for item in args.styles.split(",") if item.strip()]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    client = InternClient()
    visual_config = VisualCommentaryConfig(
        max_frames_per_event=args.max_frames_per_event,
        max_frames_per_phase=args.max_frames_per_phase,
        sample_fps=args.commentary_sample_fps,
    )

    summary_rows: list[dict[str, Any]] = []
    for style_id in style_ids:
        style = load_style(style_id)
        style_dir = output_dir / style.style_id
        style_dir.mkdir(parents=True, exist_ok=True)
        tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
        result = generate_bilingual_commentary(
            selected_events,
            manifest,
            style,
            client=client,
            tracker=tracker,
            visual_config=visual_config,
            translation_config=TranslationConfig(),
            match_context=context,
        )
        dump_bilingual_commentary_result(result, style_dir / "commentary_bilingual.json")
        tracker.dump(style_dir / "trace.json")
        for segment in result.segments:
            summary_rows.append(
                {
                    "style_id": style.style_id,
                    "event_id": segment.event_id,
                    "event_type": segment.event_type,
                    "talk_start_sec": segment.talk_start_sec,
                    "talk_end_sec": segment.talk_end_sec,
                    "english": segment.english.commentary_text,
                    "chinese": segment.chinese.commentary_text,
                }
            )

    (output_dir / "summary.json").write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(output_dir / "summary.md", summary_rows)
    print(f"Wrote style experiment outputs to {output_dir.resolve()}")


def load_events(path: str | Path) -> list[EventCandidate]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("events", payload)
    if not isinstance(rows, list):
        raise ValueError("events JSON must be a list or an object with an 'events' list.")
    return [_event_from_dict(row) for row in rows if isinstance(row, dict)]


def _event_from_dict(row: dict[str, Any]) -> EventCandidate:
    phases = tuple(_phase_from_dict(phase) for phase in row.get("phases", []) if isinstance(phase, dict))
    return EventCandidate(
        event_id=str(row["event_id"]),
        event_type=str(row["event_type"]),
        start_sec=float(row["start_sec"]),
        end_sec=float(row["end_sec"]),
        evidence_frames=tuple(str(item) for item in row.get("evidence_frames", [])),
        confidence=float(row.get("confidence", 0.0)),
        evidence_summary=str(row.get("evidence_summary", "")),
        phases=phases,
    )


def _phase_from_dict(row: dict[str, Any]) -> EventPhase:
    return EventPhase(
        phase_type=str(row.get("phase_type", "other_relevant")),
        start_sec=float(row.get("start_sec", 0.0)),
        end_sec=float(row.get("end_sec", 0.0)),
        evidence_frames=tuple(str(item) for item in row.get("evidence_frames", [])),
        evidence_summary=str(row.get("evidence_summary", "")),
    )


def write_markdown_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Nightwork Style Experiment",
        "",
        "| Style | Event | Time | English | Chinese |",
        "|---|---|---:|---|---|",
    ]
    for row in rows:
        english = str(row["english"]).replace("|", "\\|").replace("\n", " ")
        chinese = str(row["chinese"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {row['style_id']} | {row['event_id']} | "
            f"{float(row['talk_start_sec']):.1f}-{float(row['talk_end_sec']):.1f}s | "
            f"{english} | {chinese} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
