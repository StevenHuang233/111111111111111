from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from harness import (
    BilingualCommentaryResult,
    BilingualCommentarySegment,
    EventCandidate,
    EventPhase,
    LocalizedCommentary,
    ScanConfig,
    SubtitleLine,
    TraceRecorder,
    TranslationConfig,
    VisualCommentaryConfig,
    dump_bilingual_commentary_result,
    dump_scan_result,
    generate_bilingual_commentary,
    load_manifest,
    load_style,
    scan_events,
)
from harness.scanner import build_windows
from intern_client import InternClient


class ProgressLogger:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.text_path = run_dir / "progress.log"
        self.jsonl_path = run_dir / "progress.jsonl"
        self.start = time.perf_counter()

    def record(self, action: str, **detail: Any) -> None:
        payload = {
            "elapsed_sec": round(time.perf_counter() - self.start, 3),
            "action": action,
            **detail,
        }
        line = json.dumps(payload, ensure_ascii=False)
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        text = self._format_line(payload)
        with self.text_path.open("a", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print(text, flush=True)

    @staticmethod
    def _format_line(payload: dict[str, Any]) -> str:
        elapsed = payload.get("elapsed_sec", 0)
        action = payload.get("action", "")
        stage = payload.get("stage")
        current = payload.get("current")
        total = payload.get("total")
        extra = payload.get("extra", "")
        if stage and current is not None and total:
            percent = (float(current) / float(total)) * 100.0
            return f"[{elapsed:>8.1f}s] {action} {stage} {current}/{total} ({percent:5.1f}%) {extra}".rstrip()
        if stage:
            return f"[{elapsed:>8.1f}s] {action} {stage} {extra}".rstrip()
        return f"[{elapsed:>8.1f}s] {action} {extra}".rstrip()


class ProgressClient:
    def __init__(self, client: InternClient, logger: ProgressLogger, cache_root: Path, resume: bool = True) -> None:
        self.client = client
        self.logger = logger
        self.cache_root = cache_root
        self.resume = resume
        self.stage = "api"
        self.stage_started = time.perf_counter()
        self.stage_cache_dir = cache_root / "api"
        self.total: int | None = None
        self.count = 0
        self.live_durations: list[float] = []

    def set_stage(self, stage: str, total: int | None = None, extra: str = "") -> None:
        self.stage = stage
        self.total = total
        self.count = 0
        self.live_durations = []
        self.stage_started = time.perf_counter()
        self.stage_cache_dir = self.cache_root / sanitize_filename(stage)
        self.stage_cache_dir.mkdir(parents=True, exist_ok=True)
        cached = len(list(self.stage_cache_dir.glob("call_*.json"))) if self.resume else 0
        cache_note = f" cached_calls={cached}" if cached else ""
        self.logger.record("stage_start", stage=stage, total=total, extra=extra)
        if cache_note:
            self.logger.record("stage_cache_ready", stage=stage, total=total, extra=cache_note.strip())

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        index = self.count + 1
        cache_path = self.stage_cache_dir / f"call_{index:06d}.json"
        if self.resume and cache_path.exists():
            result = json.loads(cache_path.read_text(encoding="utf-8"))
            self.count = index
            self.logger.record(
                "api_call_cached",
                stage=self.stage,
                current=self.count,
                total=self.total,
                extra=self._progress_extra("cached"),
            )
            return result

        started = time.perf_counter()
        try:
            result = self.client.chat(messages, **kwargs)
        except Exception as exc:
            self.logger.record(
                "api_call_error",
                stage=self.stage,
                current=index,
                total=self.total,
                extra=str(exc),
            )
            raise
        self.count = index
        elapsed = time.perf_counter() - started
        self.live_durations.append(elapsed)
        tmp_path = cache_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(cache_path)
        self.logger.record(
            "api_call_done",
            stage=self.stage,
            current=self.count,
            total=self.total,
            extra=self._progress_extra(f"call_elapsed={elapsed:.2f}s"),
        )
        return result

    def _progress_extra(self, prefix: str) -> str:
        if not self.total or self.count <= 0:
            return prefix
        avg_api = sum(self.live_durations) / len(self.live_durations) if self.live_durations else None
        elapsed = time.perf_counter() - self.stage_started
        avg_wall = elapsed / max(1, self.count)
        remaining = max(0, self.total - self.count)
        eta = avg_api * remaining if avg_api is not None else avg_wall * remaining
        avg_text = f"avg_api={avg_api:.2f}s" if avg_api is not None else f"avg_wall={avg_wall:.2f}s"
        return f"{prefix} {avg_text} eta={format_duration(eta)}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full coarse+dense bilingual commentary pipeline with progress logs.")
    parser.add_argument("--full-manifest", default=r"C:\Users\hjj\Desktop\frames_4fps_q3\frames_manifest.json")
    parser.add_argument("--coarse-manifest", default=r"C:\Users\hjj\Desktop\frames_4fps_q3\frames_manifest_coarse_4s.json")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--run-name", default="")
    parser.add_argument("--style", default="broadcast_professional")
    parser.add_argument("--coarse-window", type=int, default=6)
    parser.add_argument("--coarse-stride", type=int, default=6)
    parser.add_argument("--dense-window", type=int, default=8)
    parser.add_argument("--dense-stride", type=int, default=8)
    parser.add_argument("--coarse-merge-gap-sec", type=float, default=8.0)
    parser.add_argument("--dense-merge-gap-sec", type=float, default=2.0)
    parser.add_argument("--goal-replay-merge-gap-sec", type=float, default=40.0)
    parser.add_argument("--dense-padding-sec", type=float, default=2.0)
    parser.add_argument("--max-frames-per-event", type=int, default=12)
    parser.add_argument("--max-frames-per-phase", type=int, default=4)
    parser.add_argument("--trace-max-text-chars", type=int, default=30000)
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Disable checkpoint reuse for this run.")
    parser.set_defaults(resume=True)
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    run_name = args.run_name or "full_latest_bilingual_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST_FULL_RUN.txt").write_text(str(run_dir), encoding="utf-8")

    logger = ProgressLogger(run_dir)
    logger.record("run_start", extra=f"{run_dir} resume={args.resume}")
    write_run_config(args, run_dir)

    style = load_style(args.style)
    full_manifest = load_manifest(args.full_manifest)
    coarse_manifest = load_manifest(args.coarse_manifest)
    client = ProgressClient(InternClient(), logger, run_dir / "cache", resume=args.resume)

    coarse_config = ScanConfig(
        window_size_frames=args.coarse_window,
        stride_frames=args.coarse_stride,
        merge_gap_sec=args.coarse_merge_gap_sec,
        goal_replay_merge_gap_sec=args.goal_replay_merge_gap_sec,
    )
    coarse_windows = build_windows(coarse_manifest.frames, coarse_config.window_size_frames, coarse_config.stride_frames)
    coarse_dir = run_dir / "coarse"
    coarse_dir.mkdir(parents=True, exist_ok=True)
    coarse_events_path = coarse_dir / "events.json"
    if args.resume and coarse_events_path.exists():
        coarse_events = load_event_candidates(coarse_events_path)
        logger.record("checkpoint_hit", stage="coarse_scan", extra=f"events={len(coarse_events)}")
    else:
        client.set_stage(
            "coarse_scan",
            len(coarse_windows),
            extra=f"frames={len(coarse_manifest.frames)} window={args.coarse_window} stride={args.coarse_stride}",
        )
        coarse_tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
        coarse = scan_events(args.coarse_manifest, style, coarse_config, client, coarse_tracker)
        dump_scan_result(coarse, coarse_events_path)
        coarse_tracker.dump(coarse_dir / "trace.json")
        write_summary(coarse_dir / "summary.txt", coarse)
        coarse_events = list(coarse.events)
        logger.record("coarse_scan_finished", extra=f"events={len(coarse.events)} window_errors={len(coarse.window_errors)}")

    dense_manifest_dir = run_dir / "dense_manifests"
    dense_manifest_dir.mkdir(parents=True, exist_ok=True)
    dense_manifest_paths = build_dense_manifests(
        full_manifest=full_manifest,
        coarse_events=coarse_events,
        output_dir=dense_manifest_dir,
        padding_sec=args.dense_padding_sec,
        resume=args.resume,
    )
    logger.record("dense_manifests_built", extra=f"count={len(dense_manifest_paths)}")

    dense_config = ScanConfig(
        window_size_frames=args.dense_window,
        stride_frames=args.dense_stride,
        merge_gap_sec=args.dense_merge_gap_sec,
        goal_replay_merge_gap_sec=args.goal_replay_merge_gap_sec,
    )
    visual_config = VisualCommentaryConfig(
        max_frames_per_event=args.max_frames_per_event,
        max_frames_per_phase=args.max_frames_per_phase,
    )
    translation_config = TranslationConfig()

    all_segments = []
    dense_root = run_dir / "dense"
    commentary_root = run_dir / "commentary"
    dense_root.mkdir(parents=True, exist_ok=True)
    commentary_root.mkdir(parents=True, exist_ok=True)

    for manifest_index, manifest_path in enumerate(dense_manifest_paths, start=1):
        dense_manifest = load_manifest(manifest_path)
        event_label = manifest_path.stem.replace("_dense_manifest", "")
        dense_windows = build_windows(dense_manifest.frames, dense_config.window_size_frames, dense_config.stride_frames)
        client.set_stage(
            f"dense_scan:{event_label}",
            len(dense_windows),
            extra=f"event_manifest={manifest_index}/{len(dense_manifest_paths)} frames={len(dense_manifest.frames)}",
        )
        event_dense_dir = dense_root / event_label
        event_dense_dir.mkdir(parents=True, exist_ok=True)
        dense_events_path = event_dense_dir / "events.json"
        if args.resume and dense_events_path.exists():
            dense_events = load_event_candidates(dense_events_path)
            logger.record("checkpoint_hit", stage=f"dense_scan:{event_label}", extra=f"events={len(dense_events)}")
        else:
            dense_tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
            dense = scan_events(manifest_path, style, dense_config, client, dense_tracker)
            dump_scan_result(dense, dense_events_path)
            dense_tracker.dump(event_dense_dir / "trace.json")
            write_summary(event_dense_dir / "summary.txt", dense)
            dense_events = list(dense.events)
            logger.record(
                "dense_scan_finished",
                stage=f"dense_scan:{event_label}",
                extra=f"events={len(dense.events)} window_errors={len(dense.window_errors)}",
            )

        if not dense_events:
            continue

        event_commentary_dir = commentary_root / event_label
        event_commentary_dir.mkdir(parents=True, exist_ok=True)
        bilingual_path = event_commentary_dir / "commentary_bilingual.json"
        if args.resume and bilingual_path.exists():
            bilingual = load_bilingual_result(bilingual_path)
            logger.record(
                "checkpoint_hit",
                stage=f"bilingual_generation:{event_label}",
                extra=f"segments={len(bilingual.segments)}",
            )
        else:
            client.set_stage(
                f"bilingual_generation:{event_label}",
                len(dense_events) * 2,
                extra=f"events={len(dense_events)}",
            )
            bilingual_tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
            bilingual = generate_bilingual_commentary(
                dense_events,
                dense_manifest,
                style,
                client,
                bilingual_tracker,
                visual_config,
                translation_config,
            )
            dump_bilingual_commentary_result(bilingual, bilingual_path)
            bilingual_tracker.dump(event_commentary_dir / "trace.json")
            logger.record(
                "bilingual_generation_finished",
                stage=f"bilingual_generation:{event_label}",
                extra=f"segments={len(bilingual.segments)}",
            )
        all_segments.extend(bilingual.segments)

    aggregate = BilingualCommentaryResult(
        video_id=full_manifest.video_id,
        style_id=style.style_id,
        source_language="en",
        target_language=translation_config.target_language,
        target_language_code=translation_config.target_language_code,
        segments=tuple(all_segments),
    )
    dump_bilingual_commentary_result(aggregate, run_dir / "commentary_bilingual.json")
    logger.record("run_finished", extra=f"segments={len(all_segments)} output={run_dir / 'commentary_bilingual.json'}")


def build_dense_manifests(
    full_manifest: Any,
    coarse_events: Any,
    output_dir: Path,
    padding_sec: float,
    resume: bool,
) -> list[Path]:
    paths: list[Path] = []
    for event in coarse_events:
        start_sec = max(0.0, event.start_sec - padding_sec)
        end_sec = event.end_sec + padding_sec
        selected = [frame for frame in full_manifest.frames if start_sec <= frame.timestamp_sec <= end_sec]
        if not selected:
            continue

        safe_type = sanitize_filename(event.event_type)
        output = output_dir / f"{event.event_id}_{safe_type}_dense_manifest.json"
        if resume and output.exists():
            paths.append(output)
            continue
        manifest = {
            "video_id": f"{full_manifest.video_id}_{event.event_id}_dense",
            "source_video": full_manifest.source_video,
            "frames": [
                {
                    "frame_id": frame.frame_id,
                    "path": str(frame.path),
                    "timestamp_sec": frame.timestamp_sec,
                }
                for frame in selected
            ],
            "event_source": {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "coarse_start_sec": event.start_sec,
                "coarse_end_sec": event.end_sec,
                "padding_sec": padding_sec,
            },
        }
        output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        paths.append(output)
    return paths


def write_run_config(args: argparse.Namespace, run_dir: Path) -> None:
    data = {key: value for key, value in vars(args).items() if "key" not in key.lower()}
    (run_dir / "run_config.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(path: Path, scan_result: Any) -> None:
    lines = [
        f"video_id={scan_result.manifest.video_id}",
        f"frames={len(scan_result.manifest.frames)}",
        f"observations={len(scan_result.observations)}",
        f"events={len(scan_result.events)}",
        f"window_errors={len(scan_result.window_errors)}",
    ]
    for event in scan_result.events:
        lines.append(
            f"{event.event_id} {event.event_type} {event.start_sec:.2f}-{event.end_sec:.2f} "
            f"frames={len(event.evidence_frames)} conf={event.confidence:.2f} "
            f"phases={','.join(phase.phase_type for phase in event.phases)}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def sanitize_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "event"


def load_event_candidates(path: Path) -> list[EventCandidate]:
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data.get("events", [])
    if not isinstance(events, list):
        raise ValueError(f"{path} must contain an events list.")

    candidates: list[EventCandidate] = []
    for item in events:
        if not isinstance(item, dict):
            continue
        phases = tuple(
            EventPhase(
                phase_type=str(phase.get("phase_type", "")),
                start_sec=float(phase.get("start_sec", 0.0)),
                end_sec=float(phase.get("end_sec", 0.0)),
                evidence_frames=tuple(str(value) for value in phase.get("evidence_frames", [])),
                evidence_summary=str(phase.get("evidence_summary", "")),
            )
            for phase in item.get("phases", [])
            if isinstance(phase, dict)
        )
        candidates.append(
            EventCandidate(
                event_id=str(item.get("event_id", "")),
                event_type=str(item.get("event_type", "")),
                start_sec=float(item.get("start_sec", 0.0)),
                end_sec=float(item.get("end_sec", 0.0)),
                evidence_frames=tuple(str(value) for value in item.get("evidence_frames", [])),
                confidence=float(item.get("confidence", 0.0)),
                evidence_summary=str(item.get("evidence_summary", "")),
                phases=phases,
            )
        )
    return candidates


def load_bilingual_result(path: Path) -> BilingualCommentaryResult:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments: list[BilingualCommentarySegment] = []
    for item in data.get("segments", []):
        if not isinstance(item, dict):
            continue
        segments.append(
            BilingualCommentarySegment(
                event_id=str(item.get("event_id", "")),
                event_type=str(item.get("event_type", "")),
                talk_start_sec=float(item.get("talk_start_sec", 0.0)),
                talk_end_sec=float(item.get("talk_end_sec", 0.0)),
                english=load_localized_commentary(item.get("english", {})),
                chinese=load_localized_commentary(item.get("chinese", {})),
            )
        )
    return BilingualCommentaryResult(
        video_id=str(data.get("video_id", "")),
        style_id=str(data.get("style_id", "")),
        source_language=str(data.get("source_language", "en")),
        target_language=str(data.get("target_language", "Simplified Chinese")),
        target_language_code=str(data.get("target_language_code", "zh-CN")),
        segments=tuple(segments),
    )


def load_localized_commentary(data: Any) -> LocalizedCommentary:
    if not isinstance(data, dict):
        return LocalizedCommentary(commentary_text="", subtitle_lines=())
    return LocalizedCommentary(
        commentary_text=str(data.get("commentary_text", "")),
        subtitle_lines=tuple(
            SubtitleLine(
                start_sec=float(row.get("start_sec", 0.0)),
                end_sec=float(row.get("end_sec", 0.0)),
                text=str(row.get("text", "")),
            )
            for row in data.get("subtitle_lines", [])
            if isinstance(row, dict)
        ),
    )


def format_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


if __name__ == "__main__":
    main()
