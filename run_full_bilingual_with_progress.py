from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from harness import (
    BilingualCommentaryResult,
    BilingualCommentarySegment,
    CommentaryUnitConfig,
    EventCandidate,
    EventPhase,
    GOAL_VERIFICATION_VERSION,
    GoalVerificationConfig,
    GoalVerificationResult,
    LocalizedCommentary,
    ScanConfig,
    SubtitleLine,
    TraceRecorder,
    TranslationConfig,
    VisualCommentaryConfig,
    dump_bilingual_commentary_result,
    dump_commentary_units,
    dump_goal_verification_result,
    dump_scan_result,
    build_commentary_units,
    generate_visual_commentary,
    load_match_context,
    load_manifest,
    load_style,
    translate_commentary_to_chinese,
    estimate_goal_verification_calls,
    verify_goal_event,
)
from harness.match_context import MatchContext
from harness.event_types import load_event_types
from harness.scanner import (
    FrameObservation,
    ScanResult,
    SCAN_ALGORITHM_VERSION,
    _apply_first_var_review_as_var_show,
    _aggregate_observations,
    _build_event_candidates,
    _build_scan_messages,
    _merge_event_candidates,
    _parse_scan_response,
    _response_text,
    _scan_model_input_detail,
    _scan_event_types,
    _scan_prompt_reference,
    build_windows,
)
from harness.tracing import clip_text, should_record_model_io, tracker_text_limit
from intern_client import InternClient


EVENT_CACHE_VERSION = 11


class ProgressLogger:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.text_path = run_dir / "progress.log"
        self.jsonl_path = run_dir / "progress.jsonl"
        self.start = time.perf_counter()
        self.lock = Lock()

    def record(self, action: str, **detail: Any) -> None:
        payload = {
            "elapsed_sec": round(time.perf_counter() - self.start, 3),
            "action": action,
            **detail,
        }
        with self.lock:
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
    def __init__(
        self,
        client: InternClient,
        logger: ProgressLogger,
        cache_root: Path,
        resume: bool = True,
        max_retries: int = 8,
        retry_base_sec: float = 10.0,
        retry_max_sec: float = 120.0,
        request_stagger_sec: float = 2.0,
    ) -> None:
        self.client = client
        self.logger = logger
        self.cache_root = cache_root
        self.resume = resume
        self.max_retries = max_retries
        self.retry_base_sec = retry_base_sec
        self.retry_max_sec = retry_max_sec
        self.request_stagger_sec = request_stagger_sec
        self.stage = "api"
        self.stage_started = time.perf_counter()
        self.stage_cache_dir = cache_root / "api"
        self.total: int | None = None
        self.count = 0
        self.assigned = 0
        self.workers = 1
        self.live_durations: list[float] = []
        self.lock = Lock()
        self.next_request_start = 0.0
        self.cooldown_until = 0.0

    def set_stage(self, stage: str, total: int | None = None, extra: str = "", workers: int = 1) -> None:
        self.stage = stage
        self.total = total
        self.count = 0
        self.assigned = 0
        self.workers = max(1, workers)
        self.live_durations = []
        self.stage_started = time.perf_counter()
        self.stage_cache_dir = self.cache_root / sanitize_filename(stage)
        self.stage_cache_dir.mkdir(parents=True, exist_ok=True)
        cached = len(list(self.stage_cache_dir.glob("*.json"))) if self.resume else 0
        cache_note = f" cached_calls={cached}" if cached else ""
        concurrency_note = f" concurrency={self.workers}"
        self.logger.record("stage_start", stage=stage, total=total, extra=(extra + concurrency_note).strip())
        if cache_note:
            self.logger.record("stage_cache_ready", stage=stage, total=total, extra=cache_note.strip())

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        with self.lock:
            self.assigned += 1
            index = self.assigned
        return self.chat_with_key(f"call_{index:06d}", messages, **kwargs)

    def chat_with_key(
        self,
        key: str,
        messages: list[dict[str, Any]],
        legacy_key: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        cache_path = self.stage_cache_dir / f"{sanitize_filename(key)}.json"
        legacy_path = self.stage_cache_dir / f"{sanitize_filename(legacy_key)}.json" if legacy_key else None
        if self.resume and cache_path.exists():
            result = json.loads(cache_path.read_text(encoding="utf-8"))
            current = self._mark_done(None)
            self.logger.record("api_call_cached", stage=self.stage, current=current, total=self.total, extra=self._progress_extra("cached"))
            return result
        if self.resume and legacy_path and legacy_path.exists():
            result = json.loads(legacy_path.read_text(encoding="utf-8"))
            cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            current = self._mark_done(None)
            self.logger.record(
                "api_call_cached",
                stage=self.stage,
                current=current,
                total=self.total,
                extra=self._progress_extra(f"cached legacy={legacy_path.name}"),
            )
            return result

        started = time.perf_counter()
        result = self._chat_with_retry(key, messages, **kwargs)
        elapsed = time.perf_counter() - started
        tmp_path = cache_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(cache_path)
        current = self._mark_done(elapsed)
        self.logger.record(
            "api_call_done",
            stage=self.stage,
            current=current,
            total=self.total,
            extra=self._progress_extra(f"call_elapsed={elapsed:.2f}s"),
        )
        return result

    def _chat_with_retry(self, key: str, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        attempt = 0
        while True:
            self._wait_for_request_slot()
            try:
                return self.client.chat(messages, **kwargs)
            except Exception as exc:
                retryable = is_retryable_rate_limit(exc)
                with self.lock:
                    current = self.count + 1
                if not retryable or attempt >= self.max_retries:
                    self.logger.record(
                        "api_call_error",
                        stage=self.stage,
                        current=current,
                        total=self.total,
                        extra=f"key={key} attempts={attempt + 1} {exc}",
                    )
                    raise
                delay = min(self.retry_max_sec, self.retry_base_sec * (2 ** attempt))
                delay += random.uniform(0.0, min(self.retry_base_sec, 5.0))
                self._set_global_cooldown(delay)
                self.logger.record(
                    "api_call_retry",
                    stage=self.stage,
                    current=current,
                    total=self.total,
                    extra=f"key={key} attempt={attempt + 1}/{self.max_retries} global_wait={delay:.1f}s {exc}",
                )
                time.sleep(delay)
                attempt += 1

    def _wait_for_request_slot(self) -> None:
        if self.request_stagger_sec <= 0:
            with self.lock:
                wait = max(0.0, self.cooldown_until - time.perf_counter())
            if wait > 0:
                time.sleep(wait)
            return
        with self.lock:
            now = time.perf_counter()
            next_allowed = max(self.next_request_start, self.cooldown_until)
            wait = max(0.0, next_allowed - now)
            self.next_request_start = max(now, next_allowed) + self.request_stagger_sec
        if wait > 0:
            time.sleep(wait)

    def _set_global_cooldown(self, delay: float) -> None:
        with self.lock:
            self.cooldown_until = max(self.cooldown_until, time.perf_counter() + delay)

    def _mark_done(self, elapsed: float | None) -> int:
        with self.lock:
            self.count += 1
            if elapsed is not None:
                self.live_durations.append(elapsed)
            return self.count

    def _progress_extra(self, prefix: str) -> str:
        with self.lock:
            count = self.count
            durations = list(self.live_durations)
            workers = self.workers
            total = self.total
        if not total or count <= 0:
            return prefix
        avg_api = sum(durations) / len(durations) if durations else None
        elapsed = time.perf_counter() - self.stage_started
        avg_wall = elapsed / max(1, count)
        remaining = max(0, total - count)
        eta = (avg_api * remaining / workers) if avg_api is not None else (avg_wall * remaining / workers)
        avg_text = f"avg_api={avg_api:.2f}s" if avg_api is not None else f"avg_wall={avg_wall:.2f}s"
        return f"{prefix} {avg_text} workers={workers} eta={format_duration(eta)}"


@dataclass(frozen=True)
class WindowResult:
    window_index: int
    frame_ids: list[str]
    time_range: list[float]
    model_input: dict[str, Any]
    model_output: str
    observations: tuple[FrameObservation, ...]
    parse_error: str = ""
    repair_input: str = ""
    repair_output: str = ""
    repaired: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the coarse-first bilingual commentary pipeline with progress logs.")
    parser.add_argument("--full-manifest", default=r"C:\Users\hjj\Desktop\frames_4fps_q3\frames_manifest.json")
    parser.add_argument("--coarse-manifest", default=r"C:\Users\hjj\Desktop\frames_4fps_q3\frames_manifest_coarse_4s.json")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--run-name", default="")
    parser.add_argument("--style", default="broadcast_professional")
    parser.add_argument("--match-context", default="", help="Match context id or JSON path for team names, kits, score metadata, and prompt guardrails.")
    parser.add_argument("--coarse-window", type=int, default=6)
    parser.add_argument("--coarse-stride", type=int, default=6)
    parser.add_argument("--dense-window", type=int, default=8)
    parser.add_argument("--dense-stride", type=int, default=8)
    parser.add_argument("--dense-sample-fps", type=float, default=1.0)
    parser.add_argument("--commentary-sample-fps", type=float, default=2.0)
    parser.add_argument("--coarse-merge-gap-sec", type=float, default=8.0)
    parser.add_argument("--dense-merge-gap-sec", type=float, default=2.0)
    parser.add_argument("--goal-replay-merge-gap-sec", type=float, default=40.0)
    parser.add_argument("--disable-commentary-units", action="store_true", help="Generate from raw scan events without the post-scan commentary unit packager.")
    parser.add_argument("--goal-unit-before-sec", type=float, default=20.0)
    parser.add_argument("--goal-unit-after-sec", type=float, default=48.0)
    parser.add_argument("--generation-event-types", default="", help="Comma-separated event types to keep for generation. Empty keeps all non-excluded types.")
    parser.add_argument("--exclude-generation-event-types", default="", help="Comma-separated event types to skip during generation.")
    parser.add_argument("--min-generation-confidence", type=float, default=0.0)
    parser.add_argument("--max-generation-events", type=int, default=0, help="Limit generation to the first N commentary units for smoke tests. 0 means no limit.")
    parser.add_argument("--verify-goals-with-model", action="store_true", help="Use a visual model pass to confirm or downgrade goal commentary units before generation.")
    parser.add_argument("--goal-verify-sample-fps", type=float, default=2.0)
    parser.add_argument("--goal-verify-window-sec", type=float, default=3.0)
    parser.add_argument("--goal-verify-stride-sec", type=float, default=3.0)
    parser.add_argument("--goal-verify-max-frames", type=int, default=0, help="Deprecated; goal verification now scans all sampled frames in sliding windows.")
    parser.add_argument("--goal-verify-max-frames-per-phase", type=int, default=0, help="Deprecated; goal verification now scans all sampled frames in sliding windows.")
    parser.add_argument("--goal-verify-context-frames", type=int, default=0, help="Deprecated for sliding-window goal verification.")
    parser.add_argument("--goal-verify-downgrade-uncertain", action="store_true")
    parser.add_argument("--disable-weak-goal-followup-downgrade", action="store_true", help="Do not downgrade weak confirmed_goal candidates when they lack replay/celebration/scoreboard follow-up support.")
    parser.add_argument("--weak-goal-followup-min-confidence", type=float, default=0.82, help="Minimum model confidence to keep a confirmed_goal candidate without follow-up support when live scoring evidence is otherwise strong.")
    parser.add_argument("--dense-padding-sec", type=float, default=2.0)
    parser.add_argument("--max-frames-per-event", type=int, default=0, help="Generation frame cap per event. 0 means no cap.")
    parser.add_argument("--max-frames-per-phase", type=int, default=0, help="Generation frame cap per phase. 0 means no cap.")
    parser.add_argument("--context-frames-each-side", type=int, default=1)
    parser.add_argument(
        "--coarse-only-generation",
        action="store_true",
        dest="coarse_only_generation",
        help="Generate bilingual commentary directly from coarse-derived events. This is the default.",
    )
    parser.add_argument(
        "--dense-generation",
        action="store_false",
        dest="coarse_only_generation",
        help="Run the legacy dense per-event scan layer before bilingual generation.",
    )
    parser.add_argument("--stop-after-coarse", action="store_true", help="Stop after writing coarse/events.json, useful for auditing scan quality before generation.")
    parser.add_argument("--trace-max-text-chars", type=int, default=30000)
    parser.add_argument("--concurrency", type=int, default=16, help="Maximum concurrent model calls for independent work.")
    parser.add_argument("--request-stagger-sec", type=float, default=2.0, help="Minimum spacing between new API request starts.")
    parser.add_argument("--max-retries", type=int, default=8, help="Retries per API call for retryable rate-limit errors.")
    parser.add_argument("--retry-base-sec", type=float, default=10.0, help="Initial retry delay for rate-limit backoff.")
    parser.add_argument("--retry-max-sec", type=float, default=120.0, help="Maximum retry delay for rate-limit backoff.")
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Disable checkpoint reuse for this run.")
    parser.set_defaults(resume=True, coarse_only_generation=True)
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
    match_context = load_match_context(args.match_context)
    full_manifest = load_manifest(args.full_manifest)
    coarse_manifest = load_manifest(args.coarse_manifest)
    client: ProgressClient | None = None

    def get_client() -> ProgressClient:
        nonlocal client
        if client is None:
            client = ProgressClient(
                InternClient(),
                logger,
                run_dir / "cache",
                resume=args.resume,
                max_retries=args.max_retries,
                retry_base_sec=args.retry_base_sec,
                retry_max_sec=args.retry_max_sec,
                request_stagger_sec=args.request_stagger_sec,
            )
        return client

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
    if args.resume and coarse_events_path.exists() and scan_checkpoint_valid(
        coarse_dir / "trace.json",
        len(coarse_manifest.frames),
        coarse_config,
        match_context,
    ):
        coarse_events = load_event_candidates(coarse_events_path)
        logger.record("checkpoint_hit", stage="coarse_scan", extra=f"events={len(coarse_events)}")
    else:
        active_client = get_client()
        active_client.set_stage(
            "coarse_scan",
            len(coarse_windows),
            extra=f"frames={len(coarse_manifest.frames)} window={args.coarse_window} stride={args.coarse_stride}",
            workers=args.concurrency,
        )
        coarse_tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
        coarse = scan_events_parallel(
            args.coarse_manifest,
            style,
            coarse_config,
            active_client,
            coarse_tracker,
            args.concurrency,
            match_context,
        )
        dump_scan_result(coarse, coarse_events_path)
        coarse_tracker.dump(coarse_dir / "trace.json")
        write_summary(coarse_dir / "summary.txt", coarse)
        coarse_events = list(coarse.events)
        logger.record("coarse_scan_finished", extra=f"events={len(coarse.events)} window_errors={len(coarse.window_errors)}")

    unit_config = CommentaryUnitConfig(
        enabled=not args.disable_commentary_units,
        goal_context_before_sec=args.goal_unit_before_sec,
        goal_replay_after_sec=args.goal_unit_after_sec,
        include_event_types=parse_event_type_csv(args.generation_event_types),
        exclude_event_types=parse_event_type_csv(args.exclude_generation_event_types),
        min_confidence=args.min_generation_confidence,
    )
    commentary_events = build_commentary_units(coarse_events, unit_config)
    units_dir = run_dir / "commentary_units"
    units_dir.mkdir(parents=True, exist_ok=True)
    dump_commentary_units(commentary_events, full_manifest, units_dir / "events.json", unit_config)
    write_event_candidates_summary(units_dir / "summary.txt", commentary_events, header=f"raw_events={len(coarse_events)}")
    logger.record(
        "commentary_units_built",
        extra=f"raw_events={len(coarse_events)} units={len(commentary_events)} output={units_dir / 'events.json'}",
    )
    generation_events = commentary_events
    if args.max_generation_events > 0:
        generation_events = commentary_events[: args.max_generation_events]
        dump_commentary_units(generation_events, full_manifest, units_dir / "events_selected.json", unit_config)
        write_event_candidates_summary(
            units_dir / "summary_selected.txt",
            generation_events,
            header=f"raw_events={len(coarse_events)} units={len(commentary_events)} selected={len(generation_events)}",
        )
        logger.record(
            "generation_events_limited",
            extra=f"selected={len(generation_events)} total_units={len(commentary_events)} output={units_dir / 'events_selected.json'}",
        )

    if args.stop_after_coarse:
        logger.record(
            "run_finished",
            extra=f"mode=stop_after_coarse raw_events={len(coarse_events)} units={len(commentary_events)} output={coarse_events_path}",
        )
        return

    if args.verify_goals_with_model:
        goal_verify_config = GoalVerificationConfig(
            sample_fps=args.goal_verify_sample_fps,
            window_sec=args.goal_verify_window_sec,
            stride_sec=args.goal_verify_stride_sec,
            max_frames_per_goal=None,
            max_frames_per_phase=None,
            context_frames_each_side=args.goal_verify_context_frames,
            downgrade_uncertain=args.goal_verify_downgrade_uncertain,
            downgrade_weak_goal_without_followup=not args.disable_weak_goal_followup_downgrade,
            min_confirmed_goal_confidence_without_followup=args.weak_goal_followup_min_confidence,
        )
        goal_validation_dir = run_dir / "goal_validation"
        goal_validation_dir.mkdir(parents=True, exist_ok=True)
        refined_events_path = goal_validation_dir / "refined_events.json"
        expected_ids = [event.event_id for event in generation_events]
        if args.resume and refined_events_path.exists() and goal_validation_checkpoint_valid(
            refined_events_path,
            goal_verify_config,
            expected_ids,
        ):
            generation_events = load_event_candidates(refined_events_path)
            logger.record("checkpoint_hit", stage="goal_verification", extra=f"events={len(generation_events)}")
        else:
            goal_count = sum(1 for event in generation_events if event.event_type == "goal")
            if goal_count:
                goal_window_count = estimate_goal_verification_calls(generation_events, full_manifest.frames, goal_verify_config)
                active_client = get_client()
                active_client.set_stage(
                    "goal_verification",
                    goal_window_count,
                    extra=(
                        f"goal_candidates={goal_count} events={len(generation_events)} "
                        f"mode=sliding_window sample_fps={args.goal_verify_sample_fps} "
                        f"window_sec={args.goal_verify_window_sec} stride_sec={args.goal_verify_stride_sec}"
                    ),
                    workers=min(args.concurrency, goal_count),
                )
                verification = verify_goals_parallel(
                    generation_events,
                    full_manifest,
                    style,
                    active_client,
                    goal_verify_config,
                    args.concurrency,
                    goal_validation_dir,
                    args.trace_max_text_chars,
                )
                dump_goal_verification_result(verification, full_manifest, refined_events_path)
                generation_events = list(verification.events)
                write_event_candidates_summary(
                    goal_validation_dir / "summary.txt",
                    generation_events,
                    header=f"input_events={len(expected_ids)} verified_goals={len(verification.records)}",
                )
                write_goal_verification_report(goal_validation_dir / "flagged_goals.md", verification)
                logger.record(
                    "goal_verification_finished",
                    extra=f"records={len(verification.records)} remaining_goal_events={sum(1 for event in generation_events if event.event_type == 'goal')} output={refined_events_path}",
                )
            else:
                dump_goal_verification_result(
                    GoalVerificationResult(
                        events=tuple(generation_events),
                        records=(),
                        config=goal_verify_config,
                        input_event_ids=tuple(event.event_id for event in generation_events),
                    ),
                    full_manifest,
                    refined_events_path,
                )
                logger.record("goal_verification_skipped", extra="goals=0")

    visual_config = VisualCommentaryConfig(
        max_frames_per_event=args.max_frames_per_event if args.max_frames_per_event > 0 else None,
        max_frames_per_phase=args.max_frames_per_phase if args.max_frames_per_phase > 0 else None,
        context_frames_each_side=args.context_frames_each_side,
        sample_fps=args.commentary_sample_fps,
    )
    translation_config = TranslationConfig()

    all_segments = []
    commentary_root = run_dir / "commentary"
    commentary_root.mkdir(parents=True, exist_ok=True)

    if args.coarse_only_generation:
        commentary_stage_label = f"coarse_events_verified_v{EVENT_CACHE_VERSION}" if args.verify_goals_with_model else "coarse_events"
        event_commentary_dir = commentary_root / commentary_stage_label
        event_commentary_dir.mkdir(parents=True, exist_ok=True)
        bilingual_path = event_commentary_dir / "commentary_bilingual.json"
        if args.resume and bilingual_path.exists() and bilingual_checkpoint_valid(
            event_commentary_dir / "trace.json",
            visual_config,
            [event.event_id for event in generation_events],
            style.style_id,
            match_context,
        ):
            bilingual = load_bilingual_result(bilingual_path)
            logger.record("checkpoint_hit", stage=f"bilingual_generation:{commentary_stage_label}", extra=f"segments={len(bilingual.segments)}")
        else:
            active_client = get_client()
            active_client.set_stage(
                f"bilingual_generation:{commentary_stage_label}",
                len(generation_events) * 2,
                extra=f"events={len(generation_events)} source=commentary_units",
                workers=min(args.concurrency, max(1, len(generation_events))),
            )
            bilingual = generate_bilingual_parallel(
                generation_events,
                full_manifest,
                style,
                active_client,
                visual_config,
                translation_config,
                args.concurrency,
                event_commentary_dir,
                args.trace_max_text_chars,
                match_context,
            )
            dump_bilingual_commentary_result(bilingual, bilingual_path)
            logger.record(
                "bilingual_generation_finished",
                stage=f"bilingual_generation:{commentary_stage_label}",
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
        logger.record("run_finished", extra=f"segments={len(all_segments)} output={run_dir / 'commentary_bilingual.json'} mode=coarse_only_generation")
        return

    dense_manifest_dir = run_dir / "dense_manifests"
    dense_manifest_dir.mkdir(parents=True, exist_ok=True)
    dense_manifest_paths = build_dense_manifests(
        full_manifest=full_manifest,
        coarse_events=generation_events,
        output_dir=dense_manifest_dir,
        padding_sec=args.dense_padding_sec,
        sample_fps=args.dense_sample_fps,
        resume=args.resume,
    )
    logger.record("dense_manifests_built", extra=f"count={len(dense_manifest_paths)} sample_fps={args.dense_sample_fps}")

    dense_config = ScanConfig(
        window_size_frames=args.dense_window,
        stride_frames=args.dense_stride,
        merge_gap_sec=args.dense_merge_gap_sec,
        goal_replay_merge_gap_sec=args.goal_replay_merge_gap_sec,
        first_var_review_as_var_show=False,
    )

    dense_root = run_dir / "dense"
    dense_root.mkdir(parents=True, exist_ok=True)

    for manifest_index, manifest_path in enumerate(dense_manifest_paths, start=1):
        dense_manifest = load_manifest(manifest_path)
        event_label = manifest_path.stem.replace("_dense_manifest", "")
        dense_windows = build_windows(dense_manifest.frames, dense_config.window_size_frames, dense_config.stride_frames)
        active_client = get_client()
        active_client.set_stage(
            f"dense_scan:{event_label}",
            len(dense_windows),
            extra=f"event_manifest={manifest_index}/{len(dense_manifest_paths)} frames={len(dense_manifest.frames)}",
            workers=args.concurrency,
        )
        event_dense_dir = dense_root / event_label
        event_dense_dir.mkdir(parents=True, exist_ok=True)
        dense_events_path = event_dense_dir / "events.json"
        if args.resume and dense_events_path.exists() and scan_checkpoint_valid(
            event_dense_dir / "trace.json",
            len(dense_manifest.frames),
            dense_config,
            match_context,
        ):
            dense_events = load_event_candidates(dense_events_path)
            logger.record("checkpoint_hit", stage=f"dense_scan:{event_label}", extra=f"events={len(dense_events)}")
        else:
            dense_tracker = TraceRecorder(record_model_io=True, max_text_chars=args.trace_max_text_chars)
            dense = scan_events_parallel(
                manifest_path,
                style,
                dense_config,
                active_client,
                dense_tracker,
                args.concurrency,
                match_context,
            )
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
        if args.resume and bilingual_path.exists() and bilingual_checkpoint_valid(
            event_commentary_dir / "trace.json",
            visual_config,
            [event.event_id for event in dense_events],
            style.style_id,
            match_context,
        ):
            bilingual = load_bilingual_result(bilingual_path)
            logger.record(
                "checkpoint_hit",
                stage=f"bilingual_generation:{event_label}",
                extra=f"segments={len(bilingual.segments)}",
            )
        else:
            active_client = get_client()
            active_client.set_stage(
                f"bilingual_generation:{event_label}",
                len(dense_events) * 2,
                extra=f"events={len(dense_events)}",
                workers=min(args.concurrency, max(1, len(dense_events))),
            )
            bilingual = generate_bilingual_parallel(
                dense_events,
                dense_manifest,
                style,
                active_client,
                visual_config,
                translation_config,
                args.concurrency,
                event_commentary_dir,
                args.trace_max_text_chars,
                match_context,
            )
            dump_bilingual_commentary_result(bilingual, bilingual_path)
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


def scan_events_parallel(
    manifest_path: str | Path,
    style: Any,
    config: ScanConfig,
    client: ProgressClient,
    tracker: TraceRecorder,
    concurrency: int,
    match_context: MatchContext | None = None,
) -> ScanResult:
    trace = tracker
    trace.record(
        "scan_events_parallel",
        "start",
        {
            "manifest_path": str(manifest_path),
            "style_id": style.style_id,
            "window_size_frames": config.window_size_frames,
            "stride_frames": config.stride_frames,
            "merge_gap_sec": config.merge_gap_sec,
            "goal_replay_merge_gap_sec": config.goal_replay_merge_gap_sec,
            "first_var_review_as_var_show": config.first_var_review_as_var_show,
            "concurrency": concurrency,
            "scan_algorithm_version": SCAN_ALGORITHM_VERSION,
            "match_context_id": match_context.context_id if match_context else None,
        },
    )
    registry = load_event_types(config.event_types_path)
    manifest = load_manifest(manifest_path)
    windows = build_windows(manifest.frames, config.window_size_frames, config.stride_frames)
    trace.record(
        "scan_events_parallel",
        "build_windows",
        {
            "frame_count": len(manifest.frames),
            "window_count": len(windows),
            "windows": [{"start": start, "end": end} for start, end in windows],
        },
    )

    def run_window(window_index: int, start: int, end: int) -> WindowResult:
        frames = manifest.frames[start:end]
        messages = _build_scan_messages(frames, style, registry, match_context)
        model_input = _scan_model_input_detail(messages, frames, window_index, trace)
        data = client.chat_with_key(
            f"window_{window_index:06d}_{window_fingerprint(frames)}",
            messages,
            temperature=style.temperature,
            top_p=style.top_p,
            max_tokens=style.max_tokens,
            thinking_mode=style.thinking_mode,
        )
        text = _response_text(data)
        try:
            parsed = tuple(_parse_scan_response(text, frames, registry, window_index))
            return WindowResult(
                window_index=window_index,
                frame_ids=[frame.frame_id for frame in frames],
                time_range=[frames[0].timestamp_sec, frames[-1].timestamp_sec] if frames else [],
                model_input=model_input,
                model_output=text,
                observations=parsed,
            )
        except Exception as exc:
            repair_input, repair_output, repaired = repair_scan_window(
                client,
                text,
                str(exc),
                frames,
                registry,
                window_index,
                config.repair_attempts,
            )
            if repaired is not None:
                return WindowResult(
                    window_index=window_index,
                    frame_ids=[frame.frame_id for frame in frames],
                    time_range=[frames[0].timestamp_sec, frames[-1].timestamp_sec] if frames else [],
                    model_input=model_input,
                    model_output=text,
                    observations=tuple(repaired),
                    parse_error=str(exc),
                    repair_input=repair_input,
                    repair_output=repair_output,
                    repaired=True,
                )
            return WindowResult(
                window_index=window_index,
                frame_ids=[frame.frame_id for frame in frames],
                time_range=[frames[0].timestamp_sec, frames[-1].timestamp_sec] if frames else [],
                model_input=model_input,
                model_output=text,
                observations=(),
                parse_error=str(exc),
                repair_input=repair_input,
                repair_output=repair_output,
                repaired=False,
            )

    results: list[WindowResult] = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
        futures = [executor.submit(run_window, index, start, end) for index, (start, end) in enumerate(windows)]
        for future in as_completed(futures):
            results.append(future.result())

    raw_observations: list[FrameObservation] = []
    window_errors: list[str] = []
    for result in sorted(results, key=lambda item: item.window_index):
        trace.record(
            "scan_events_parallel.window",
            "prepare_model_call",
            {
                "window_index": result.window_index,
                "frame_ids": result.frame_ids,
                "time_range": result.time_range,
            },
        )
        if should_record_model_io(trace):
            trace.record("scan_events_parallel.window", "model_call_input", result.model_input)
            trace.record(
                "scan_events_parallel.window",
                "model_call_output",
                {
                    "window_index": result.window_index,
                    "content": clip_text(result.model_output, tracker_text_limit(trace)),
                },
            )
        if result.parse_error:
            trace.record(
                "scan_events_parallel.window",
                "parse_failed_try_repair",
                {"window_index": result.window_index, "error": result.parse_error},
            )
            if should_record_model_io(trace) and result.repair_input:
                trace.record(
                    "scan_events_parallel.window.repair",
                    "model_call_input",
                    {
                        "window_index": result.window_index,
                        "prompt": clip_text(result.repair_input, tracker_text_limit(trace)),
                    },
                )
                trace.record(
                    "scan_events_parallel.window.repair",
                    "model_call_output",
                    {
                        "window_index": result.window_index,
                        "content": clip_text(result.repair_output, tracker_text_limit(trace)),
                    },
                )
            if not result.repaired:
                window_errors.append(f"window={result.window_index}: {result.parse_error}")
                trace.record(
                    "scan_events_parallel.window",
                    "repair_failed",
                    {"window_index": result.window_index, "error": result.parse_error},
                )
                continue
            trace.record(
                "scan_events_parallel.window",
                "repair_succeeded",
                {
                    "window_index": result.window_index,
                    "observation_count": len(result.observations),
                    "positive_count": sum(1 for item in result.observations if item.needs_commentary),
                },
            )
        else:
            trace.record(
                "scan_events_parallel.window",
                "parsed_model_response",
                {
                    "window_index": result.window_index,
                    "observation_count": len(result.observations),
                    "positive_count": sum(1 for item in result.observations if item.needs_commentary),
                },
            )
        raw_observations.extend(result.observations)

    observations = _aggregate_observations(manifest, raw_observations, registry)
    trace.record(
        "scan_events_parallel",
        "aggregate_frame_observations",
        {
            "raw_observation_count": len(raw_observations),
            "frame_observation_count": len(observations),
            "positive_frame_count": sum(1 for item in observations if item.needs_commentary),
        },
    )
    initial_events = _build_event_candidates(manifest, observations, registry)
    events = _merge_event_candidates(initial_events, config, registry, observations)
    var_show_event_id = None
    if config.first_var_review_as_var_show:
        events, var_show_event_id = _apply_first_var_review_as_var_show(events, registry)
    trace.record(
        "scan_events_parallel",
        "merge_event_candidates",
        {
            "initial_event_count": len(initial_events),
            "merged_event_count": len(events),
            "first_var_review_as_var_show": config.first_var_review_as_var_show,
            "var_show_event_id": var_show_event_id,
        },
    )
    trace.record("scan_events_parallel", "finish", {"window_errors": len(window_errors), "event_count": len(events)})
    return ScanResult(
        manifest=manifest,
        observations=tuple(observations),
        events=tuple(events),
        window_errors=tuple(window_errors),
    )


def repair_scan_window(
    client: ProgressClient,
    bad_text: str,
    error: str,
    frames: Any,
    registry: Any,
    window_index: int,
    attempts: int,
) -> tuple[str, str, list[FrameObservation] | None]:
    if attempts <= 0:
        return "", "", None

    repair_prompt = f"""
Fix this football event scan response into valid JSON.
Error: {error}
Allowed event_type values: {", ".join(_scan_event_types(registry))}
Event definitions and decision cues:
{_scan_prompt_reference(registry)}
Required frame_ids: {", ".join(frame.frame_id for frame in frames)}

Bad response:
{bad_text}

Return JSON only with the same schema:
{{"frames":[{{"frame_id":"...","needs_commentary":false,"event_type":"no_event","confidence":0.0,"evidence":"..."}}]}}
""".strip()
    repair_output = ""
    for attempt in range(1, attempts + 1):
        data = client.chat_with_key(
            f"repair_window_{window_index:06d}_attempt_{attempt}",
            [{"role": "user", "content": repair_prompt}],
            temperature=0.0,
            top_p=1.0,
            max_tokens=1024,
        )
        repair_output = _response_text(data)
        try:
            return repair_prompt, repair_output, _parse_scan_response(repair_output, frames, registry, window_index)
        except Exception:
            continue
    return repair_prompt, repair_output, None


class FixedKeyClient:
    def __init__(self, client: ProgressClient, key_prefix: str) -> None:
        self.client = client
        self.key_prefix = key_prefix
        self.count = 0
        self.lock = Lock()

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        with self.lock:
            self.count += 1
            count = self.count
        return self.client.chat_with_key(f"{self.key_prefix}_{count:02d}", messages, **kwargs)


def generate_bilingual_parallel(
    events: list[EventCandidate],
    manifest: Any,
    style: Any,
    client: ProgressClient,
    visual_config: VisualCommentaryConfig,
    translation_config: TranslationConfig,
    concurrency: int,
    trace_dir: Path,
    trace_max_text_chars: int,
    match_context: MatchContext | None = None,
) -> BilingualCommentaryResult:
    trace_dir.mkdir(parents=True, exist_ok=True)

    def run_event(event: EventCandidate) -> tuple[BilingualCommentarySegment, dict[str, Any]]:
        tracker = TraceRecorder(record_model_io=True, max_text_chars=trace_max_text_chars)
        english = generate_visual_commentary(
            [event],
            manifest,
            style,
            FixedKeyClient(client, f"event_{event.event_id}_{style_context_fingerprint(style, match_context)}_{event_fingerprint(event)}_english"),
            tracker,
            visual_config,
            match_context,
        )
        bilingual = translate_commentary_to_chinese(
            english,
            style,
            FixedKeyClient(client, f"event_{event.event_id}_{style_context_fingerprint(style, match_context)}_{event_fingerprint(event)}_chinese"),
            tracker,
            translation_config,
            match_context,
        )
        return bilingual.segments[0], tracker.to_dict()

    segments: list[BilingualCommentarySegment] = []
    traces: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(concurrency, len(events)))) as executor:
        futures = {executor.submit(run_event, event): event.event_id for event in events}
        for future in as_completed(futures):
            event_id = futures[future]
            segment, trace = future.result()
            segments.append(segment)
            traces[event_id] = trace
            (trace_dir / f"trace_{sanitize_filename(event_id)}.json").write_text(
                json.dumps(trace, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    segments.sort(key=lambda item: (item.talk_start_sec, item.event_id))
    (trace_dir / "trace.json").write_text(json.dumps({"events": traces}, ensure_ascii=False, indent=2), encoding="utf-8")
    return BilingualCommentaryResult(
        video_id=manifest.video_id,
        style_id=style.style_id,
        source_language="en",
        target_language=translation_config.target_language,
        target_language_code=translation_config.target_language_code,
        segments=tuple(segments),
    )


def verify_goals_parallel(
    events: list[EventCandidate],
    manifest: Any,
    style: Any,
    client: ProgressClient,
    config: GoalVerificationConfig,
    concurrency: int,
    trace_dir: Path,
    trace_max_text_chars: int,
) -> GoalVerificationResult:
    trace_dir.mkdir(parents=True, exist_ok=True)
    refined_by_id: dict[str, tuple[EventCandidate, ...]] = {event.event_id: (event,) for event in events}
    records = []
    traces: dict[str, Any] = {}
    goal_events = [event for event in events if event.event_type == "goal"]

    def run_event(event: EventCandidate) -> tuple[tuple[EventCandidate, ...], Any, dict[str, Any]]:
        tracker = TraceRecorder(record_model_io=True, max_text_chars=trace_max_text_chars)
        refined, record = verify_goal_event(
            event,
            manifest,
            style,
            FixedKeyClient(client, f"goal_verify_{event.event_id}_{event_fingerprint(event)}"),
            tracker,
            config,
        )
        return refined, record, tracker.to_dict()

    with ThreadPoolExecutor(max_workers=max(1, min(concurrency, len(goal_events)))) as executor:
        futures = {executor.submit(run_event, event): event.event_id for event in goal_events}
        for future in as_completed(futures):
            event_id = futures[future]
            refined, record, trace = future.result()
            refined_by_id[event_id] = refined
            records.append(record)
            traces[event_id] = trace
            (trace_dir / f"trace_{sanitize_filename(event_id)}.json").write_text(
                json.dumps(trace, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    ordered = [item for event in events for item in refined_by_id[event.event_id]]
    records.sort(key=lambda item: item.event_id)
    (trace_dir / "trace.json").write_text(json.dumps({"events": traces}, ensure_ascii=False, indent=2), encoding="utf-8")
    return GoalVerificationResult(
        events=tuple(ordered),
        records=tuple(records),
        config=config,
        input_event_ids=tuple(event.event_id for event in events),
    )


def build_dense_manifests(
    full_manifest: Any,
    coarse_events: Any,
    output_dir: Path,
    padding_sec: float,
    sample_fps: float | None,
    resume: bool,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for event in coarse_events:
        start_sec = max(0.0, event.start_sec - padding_sec)
        end_sec = event.end_sec + padding_sec
        interval_frames = [frame for frame in full_manifest.frames if start_sec <= frame.timestamp_sec <= end_sec]
        selected = sample_frames_by_fps(interval_frames, sample_fps)
        if not selected:
            continue

        safe_type = sanitize_filename(event.event_type)
        output = output_dir / f"{event.event_id}_{safe_type}_dense_manifest.json"
        if resume and output.exists() and dense_manifest_matches_sampling(output, sample_fps, padding_sec):
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
                "sample_fps": sample_fps,
                "input_frame_count": len(interval_frames),
                "sampled_frame_count": len(selected),
            },
        }
        output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        paths.append(output)
    return paths


def sample_frames_by_fps(frames: list[Any], sample_fps: float | None) -> list[Any]:
    if not frames or sample_fps is None or sample_fps <= 0:
        return list(frames)

    min_interval_sec = 1.0 / sample_fps
    selected: list[Any] = []
    last_timestamp: float | None = None
    for frame in sorted(frames, key=lambda item: item.timestamp_sec):
        if last_timestamp is None or frame.timestamp_sec >= last_timestamp + min_interval_sec - 1e-6:
            selected.append(frame)
            last_timestamp = frame.timestamp_sec
    return selected


def dense_manifest_matches_sampling(path: Path, sample_fps: float | None, padding_sec: float) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    event_source = payload.get("event_source", {})
    return event_source.get("sample_fps") == sample_fps and event_source.get("padding_sec") == padding_sec


def window_fingerprint(frames: Any) -> str:
    digest = hashlib.sha1()
    for frame in frames:
        digest.update(str(frame.frame_id).encode("utf-8"))
        digest.update(b"\0")
        digest.update(f"{float(frame.timestamp_sec):.6f}".encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def scan_checkpoint_valid(
    trace_path: Path,
    frame_count: int,
    config: ScanConfig,
    match_context: MatchContext | None = None,
) -> bool:
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    start_detail = _first_trace_detail(payload, action="start")
    windows_detail = _first_trace_detail(payload, action="build_windows")
    if not start_detail or not windows_detail:
        return False

    return (
        start_detail.get("scan_algorithm_version") == SCAN_ALGORITHM_VERSION
        and start_detail.get("window_size_frames") == config.window_size_frames
        and start_detail.get("stride_frames") == config.stride_frames
        and start_detail.get("merge_gap_sec") == config.merge_gap_sec
        and start_detail.get("goal_replay_merge_gap_sec") == config.goal_replay_merge_gap_sec
        and start_detail.get("first_var_review_as_var_show") == config.first_var_review_as_var_show
        and start_detail.get("match_context_id") == (match_context.context_id if match_context else None)
        and windows_detail.get("frame_count") == frame_count
    )


def bilingual_checkpoint_valid(
    trace_path: Path,
    visual_config: VisualCommentaryConfig,
    expected_event_ids: list[str] | None = None,
    expected_style_id: str | None = None,
    match_context: MatchContext | None = None,
) -> bool:
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    event_traces = payload.get("events", {})
    if not isinstance(event_traces, dict) or not event_traces:
        return False
    if expected_event_ids is not None and set(event_traces) != set(expected_event_ids):
        return False

    for event_trace in event_traces.values():
        detail = _first_trace_detail(event_trace, step="generate_visual_commentary", action="start")
        if not detail:
            return False
        if expected_style_id is not None and detail.get("style_id") != expected_style_id:
            return False
        if detail.get("match_context_id") != (match_context.context_id if match_context else None):
            return False
        if detail.get("max_frames_per_event") != visual_config.max_frames_per_event:
            return False
        if detail.get("max_frames_per_phase") != visual_config.max_frames_per_phase:
            return False
        if detail.get("context_frames_each_side") != visual_config.context_frames_each_side:
            return False
        if detail.get("sample_fps") != visual_config.sample_fps:
            return False
        if detail.get("contact_sheet_threshold") != visual_config.contact_sheet_threshold:
            return False
        if detail.get("contact_sheet_frames_per_image") != visual_config.contact_sheet_frames_per_image:
            return False
    return True


def goal_validation_checkpoint_valid(
    path: Path,
    config: GoalVerificationConfig,
    expected_event_ids: list[str],
) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    if payload.get("goal_verification_version") != GOAL_VERIFICATION_VERSION:
        return False
    if payload.get("config") != goal_verify_config_to_dict(config):
        return False
    input_event_ids = payload.get("input_event_ids")
    if isinstance(input_event_ids, list):
        return [str(event_id) for event_id in input_event_ids] == expected_event_ids
    events = payload.get("events", [])
    if not isinstance(events, list):
        return False
    event_ids = [str(event.get("event_id", "")) for event in events if isinstance(event, dict)]
    return event_ids == expected_event_ids


def _first_trace_detail(payload: dict[str, Any], action: str, step: str | None = None) -> dict[str, Any] | None:
    for row in payload.get("steps", []):
        if step is not None and row.get("step") != step:
            continue
        if row.get("action") == action:
            detail = row.get("detail")
            return detail if isinstance(detail, dict) else None
    return None


def write_run_config(args: argparse.Namespace, run_dir: Path) -> None:
    data = {key: value for key, value in vars(args).items() if "key" not in key.lower()}
    (run_dir / "run_config.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_event_type_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


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


def write_event_candidates_summary(path: Path, events: list[EventCandidate], header: str = "") -> None:
    lines = [header] if header else []
    lines.append(f"events={len(events)}")
    for event in events:
        lines.append(
            f"{event.event_id} {event.event_type} {event.start_sec:.2f}-{event.end_sec:.2f} "
            f"frames={len(event.evidence_frames)} conf={event.confidence:.2f} "
            f"phases={','.join(phase.phase_type for phase in event.phases)}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_goal_verification_report(path: Path, result: GoalVerificationResult) -> None:
    remaining_goal_events = sum(1 for event in result.events if event.event_type == "goal")
    merged_records = sum(1 for record in result.records if record.refined_event_type == "merged_into_goal")
    lines = [
        "# Goal Verification Report",
        "",
        f"- candidate_records={len(result.records)}",
        f"- remaining_goal_events={remaining_goal_events}",
        f"- merged_duplicate_records={merged_records}",
        "",
        "| Event | Verdict | Refined Type | Confidence | Warnings | Rationale |",
        "|---|---|---|---:|---|---|",
    ]
    for record in result.records:
        warnings = ", ".join(record.warnings)
        rationale = record.rationale.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {record.event_id} | {record.verdict} | {record.refined_event_type} | "
            f"{record.confidence:.2f} | {warnings} | {rationale} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def sanitize_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "event"


def event_fingerprint(event: EventCandidate) -> str:
    payload = {
        "event_cache_version": EVENT_CACHE_VERSION,
        "event_type": event.event_type,
        "start_sec": event.start_sec,
        "end_sec": event.end_sec,
        "evidence_frames": list(event.evidence_frames),
        "phases": [
            {
                "phase_type": phase.phase_type,
                "start_sec": phase.start_sec,
                "end_sec": phase.end_sec,
                "evidence_frames": list(phase.evidence_frames),
            }
            for phase in event.phases
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def style_context_fingerprint(style: Any, match_context: MatchContext | None) -> str:
    payload = {
        "style_id": getattr(style, "style_id", ""),
        "style_name": getattr(style, "name", ""),
        "match_context_id": match_context.context_id if match_context else None,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def events_fingerprint(events: list[EventCandidate]) -> str:
    digest = hashlib.sha1()
    digest.update(str(EVENT_CACHE_VERSION).encode("ascii"))
    digest.update(b"\0")
    for event in events:
        digest.update(event_fingerprint(event).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()[:12]


def goal_verify_config_to_dict(config: GoalVerificationConfig) -> dict[str, Any]:
    return {
        "sample_fps": config.sample_fps,
        "window_sec": config.window_sec,
        "stride_sec": config.stride_sec,
        "max_frames_per_goal": config.max_frames_per_goal,
        "max_frames_per_phase": config.max_frames_per_phase,
        "context_frames_each_side": config.context_frames_each_side,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "max_tokens": config.max_tokens,
        "thinking_mode": config.thinking_mode,
        "downgrade_not_goal": config.downgrade_not_goal,
        "downgrade_uncertain": config.downgrade_uncertain,
        "downgrade_weak_goal_without_followup": config.downgrade_weak_goal_without_followup,
        "min_confirmed_goal_confidence_without_followup": config.min_confirmed_goal_confidence_without_followup,
    }


def is_retryable_rate_limit(exc: Exception) -> bool:
    text = str(exc).lower()
    retryable_markers = [
        "-20048",
        "too frequent",
        "rate limit",
        "rate_limit",
        "429",
        "请求过于频繁",
    ]
    return any(marker in text for marker in retryable_markers)


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
