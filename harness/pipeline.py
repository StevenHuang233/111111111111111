from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intern_client import InternClient

from .commentary import CommentaryResult, generate_commentary
from .manifest import FramesManifest, load_manifest
from .scanner import ScanConfig, ScanResult, scan_events
from .styles import StyleProfile, load_style
from .tracing import NullTracker, StepTracker


@dataclass(frozen=True)
class PipelineResult:
    manifest: FramesManifest
    style: StyleProfile
    scan: ScanResult
    commentary: CommentaryResult
    trace: StepTracker | None = None


def run_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
    tracker: StepTracker | None = None,
) -> PipelineResult:
    trace = tracker or NullTracker()
    trace.record("run_pipeline", "start", {"manifest_path": str(manifest_path), "style_id_or_path": style_id_or_path})
    active_client = client or InternClient()
    trace.record("run_pipeline", "client_ready", {"client_type": type(active_client).__name__})
    style = load_style(style_id_or_path)
    trace.record("run_pipeline", "load_style", {"style_id": style.style_id})
    manifest = load_manifest(manifest_path)
    trace.record("run_pipeline", "load_manifest", {"video_id": manifest.video_id, "frame_count": len(manifest.frames)})
    scan = scan_events(manifest_path, style, scan_config, active_client, trace)
    trace.record("run_pipeline", "scan_complete", {"event_count": len(scan.events)})
    commentary = generate_commentary(scan.events, manifest, style, active_client, trace)
    trace.record("run_pipeline", "finish", {"segment_count": len(commentary.segments)})
    return PipelineResult(manifest=manifest, style=style, scan=scan, commentary=commentary, trace=tracker)
