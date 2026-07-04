from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intern_client import InternClient

from .commentary import CommentaryResult, generate_commentary
from .manifest import FramesManifest, load_manifest
from .scanner import ScanConfig, ScanResult, scan_events
from .styles import StyleProfile, load_style


@dataclass(frozen=True)
class PipelineResult:
    manifest: FramesManifest
    style: StyleProfile
    scan: ScanResult
    commentary: CommentaryResult


def run_pipeline(
    manifest_path: str | Path,
    style_id_or_path: str = "broadcast_professional",
    scan_config: ScanConfig | None = None,
    client: Any | None = None,
) -> PipelineResult:
    active_client = client or InternClient()
    style = load_style(style_id_or_path)
    manifest = load_manifest(manifest_path)
    scan = scan_events(manifest_path, style, scan_config, active_client)
    commentary = generate_commentary(scan.events, manifest, style, active_client)
    return PipelineResult(manifest=manifest, style=style, scan=scan, commentary=commentary)
