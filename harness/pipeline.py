from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intern_client import InternClient

from .bilingual import BilingualCommentaryResult, TranslationConfig, generate_bilingual_commentary
from .commentary import CommentaryResult, VisualCommentaryConfig, generate_visual_commentary
from .event_units import CommentaryUnitConfig, build_commentary_units
from .goal_verifier import GoalVerificationConfig, GoalVerificationResult, verify_goal_events
from .match_context import MatchContext, load_match_context
from .manifest import FramesManifest, load_manifest
from .scanner import EventCandidate, ScanConfig, ScanResult, scan_events
from .styles import StyleProfile, load_style
from .tracing import NullTracker, StepTracker


@dataclass(frozen=True)
class PipelineResult:
    manifest: FramesManifest
    style: StyleProfile
    match_context: MatchContext | None
    scan: ScanResult
    commentary: CommentaryResult
    trace: StepTracker | None = None
    generation_events: tuple[EventCandidate, ...] = ()
    goal_verification: GoalVerificationResult | None = None


@dataclass(frozen=True)
class BilingualPipelineResult:
    manifest: FramesManifest
    style: StyleProfile
    match_context: MatchContext | None
    scan: ScanResult
    bilingual_commentary: BilingualCommentaryResult
    trace: StepTracker | None = None
    generation_events: tuple[EventCandidate, ...] = ()
    goal_verification: GoalVerificationResult | None = None


def prepare_generation_events(
    scan: ScanResult,
    manifest: FramesManifest,
    style: StyleProfile,
    client: Any | None = None,
    tracker: StepTracker | None = None,
    commentary_unit_config: CommentaryUnitConfig | None = None,
    verify_goals_with_model: bool = False,
    goal_verification_config: GoalVerificationConfig | None = None,
) -> tuple[tuple[EventCandidate, ...], GoalVerificationResult | None]:
    trace = tracker or NullTracker()
    unit_config = commentary_unit_config or CommentaryUnitConfig()
    trace.record(
        "prepare_generation_events",
        "start",
        {
            "raw_event_count": len(scan.events),
            "commentary_units_enabled": unit_config.enabled,
            "verify_goals_with_model": verify_goals_with_model,
        },
    )

    generation_events = tuple(build_commentary_units(scan.events, unit_config))
    trace.record(
        "prepare_generation_events",
        "coarse_events_merged",
        {
            "raw_event_count": len(scan.events),
            "generation_event_count": len(generation_events),
            "goal_count": sum(1 for event in generation_events if event.event_type == "goal"),
        },
    )

    verification: GoalVerificationResult | None = None
    if verify_goals_with_model:
        active_client = client or InternClient()
        verification = verify_goal_events(
            generation_events,
            manifest,
            style,
            active_client,
            trace,
            goal_verification_config,
        )
        generation_events = tuple(verification.events)
        trace.record(
            "prepare_generation_events",
            "goal_scan_complete",
            {
                "verified_goals": len(verification.records),
                "generation_event_count": len(generation_events),
                "remaining_goal_count": sum(1 for event in generation_events if event.event_type == "goal"),
            },
        )
    else:
        trace.record("prepare_generation_events", "goal_scan_skipped", {"generation_event_count": len(generation_events)})

    trace.record("prepare_generation_events", "finish", {"generation_event_count": len(generation_events)})
    return generation_events, verification


def run_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
    tracker: StepTracker | None = None,
    visual_commentary_config: VisualCommentaryConfig | None = None,
    match_context_id_or_path: str | None = None,
    commentary_unit_config: CommentaryUnitConfig | None = None,
    verify_goals_with_model: bool = False,
    goal_verification_config: GoalVerificationConfig | None = None,
) -> PipelineResult:
    trace = tracker or NullTracker()
    trace.record("run_pipeline", "start", {"manifest_path": str(manifest_path), "style_id_or_path": style_id_or_path})
    active_client = client or InternClient()
    trace.record("run_pipeline", "client_ready", {"client_type": type(active_client).__name__})
    style = load_style(style_id_or_path)
    trace.record("run_pipeline", "load_style", {"style_id": style.style_id})
    match_context = load_match_context(match_context_id_or_path)
    trace.record(
        "run_pipeline",
        "load_match_context",
        {"match_context_id": match_context.context_id if match_context else None},
    )
    manifest = load_manifest(manifest_path)
    trace.record("run_pipeline", "load_manifest", {"video_id": manifest.video_id, "frame_count": len(manifest.frames)})
    scan = scan_events(manifest_path, style, scan_config, active_client, trace, match_context)
    trace.record("run_pipeline", "scan_complete", {"event_count": len(scan.events)})
    generation_events, goal_verification = prepare_generation_events(
        scan,
        manifest,
        style,
        active_client,
        trace,
        commentary_unit_config,
        verify_goals_with_model,
        goal_verification_config,
    )
    trace.record(
        "run_pipeline",
        "generation_events_ready",
        {
            "raw_event_count": len(scan.events),
            "generation_event_count": len(generation_events),
            "goal_verified": goal_verification is not None,
        },
    )
    commentary = generate_visual_commentary(
        generation_events,
        manifest,
        style,
        active_client,
        trace,
        visual_commentary_config,
        match_context,
    )
    trace.record("run_pipeline", "finish", {"segment_count": len(commentary.segments)})
    return PipelineResult(
        manifest=manifest,
        style=style,
        match_context=match_context,
        scan=scan,
        commentary=commentary,
        trace=tracker,
        generation_events=tuple(generation_events),
        goal_verification=goal_verification,
    )


def run_bilingual_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
    tracker: StepTracker | None = None,
    visual_commentary_config: VisualCommentaryConfig | None = None,
    translation_config: TranslationConfig | None = None,
    match_context_id_or_path: str | None = None,
    commentary_unit_config: CommentaryUnitConfig | None = None,
    verify_goals_with_model: bool = False,
    goal_verification_config: GoalVerificationConfig | None = None,
) -> BilingualPipelineResult:
    trace = tracker or NullTracker()
    trace.record(
        "run_bilingual_pipeline",
        "start",
        {"manifest_path": str(manifest_path), "style_id_or_path": style_id_or_path},
    )
    active_client = client or InternClient()
    trace.record("run_bilingual_pipeline", "client_ready", {"client_type": type(active_client).__name__})
    style = load_style(style_id_or_path)
    trace.record("run_bilingual_pipeline", "load_style", {"style_id": style.style_id})
    match_context = load_match_context(match_context_id_or_path)
    trace.record(
        "run_bilingual_pipeline",
        "load_match_context",
        {"match_context_id": match_context.context_id if match_context else None},
    )
    manifest = load_manifest(manifest_path)
    trace.record(
        "run_bilingual_pipeline",
        "load_manifest",
        {"video_id": manifest.video_id, "frame_count": len(manifest.frames)},
    )
    scan = scan_events(manifest_path, style, scan_config, active_client, trace, match_context)
    trace.record("run_bilingual_pipeline", "scan_complete", {"event_count": len(scan.events)})
    generation_events, goal_verification = prepare_generation_events(
        scan,
        manifest,
        style,
        active_client,
        trace,
        commentary_unit_config,
        verify_goals_with_model,
        goal_verification_config,
    )
    trace.record(
        "run_bilingual_pipeline",
        "generation_events_ready",
        {
            "raw_event_count": len(scan.events),
            "generation_event_count": len(generation_events),
            "goal_verified": goal_verification is not None,
        },
    )
    bilingual = generate_bilingual_commentary(
        generation_events,
        manifest,
        style,
        active_client,
        trace,
        visual_commentary_config,
        translation_config,
        match_context,
    )
    trace.record("run_bilingual_pipeline", "finish", {"segment_count": len(bilingual.segments)})
    return BilingualPipelineResult(
        manifest=manifest,
        style=style,
        match_context=match_context,
        scan=scan,
        bilingual_commentary=bilingual,
        trace=tracker,
        generation_events=tuple(generation_events),
        goal_verification=goal_verification,
    )
