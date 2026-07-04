from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intern_client import InternClient

from .bilingual import BilingualCommentaryResult, TranslationConfig, generate_bilingual_commentary
from .commentary import CommentaryResult, VisualCommentaryConfig, generate_visual_commentary
from .match_context import MatchContext, load_match_context
from .manifest import FramesManifest, load_manifest
from .scanner import ScanConfig, ScanResult, scan_events
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


@dataclass(frozen=True)
class BilingualPipelineResult:
    manifest: FramesManifest
    style: StyleProfile
    match_context: MatchContext | None
    scan: ScanResult
    bilingual_commentary: BilingualCommentaryResult
    trace: StepTracker | None = None


def run_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
    tracker: StepTracker | None = None,
    visual_commentary_config: VisualCommentaryConfig | None = None,
    match_context_id_or_path: str | None = None,
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
    commentary = generate_visual_commentary(
        scan.events,
        manifest,
        style,
        active_client,
        trace,
        visual_commentary_config,
        match_context,
    )
    trace.record("run_pipeline", "finish", {"segment_count": len(commentary.segments)})
    return PipelineResult(manifest=manifest, style=style, match_context=match_context, scan=scan, commentary=commentary, trace=tracker)


def run_bilingual_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
    tracker: StepTracker | None = None,
    visual_commentary_config: VisualCommentaryConfig | None = None,
    translation_config: TranslationConfig | None = None,
    match_context_id_or_path: str | None = None,
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
    bilingual = generate_bilingual_commentary(
        scan.events,
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
    )
