from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FrameInfo:
    frame_id: str
    path: Path
    timestamp_sec: float


@dataclass(frozen=True)
class FramesManifest:
    video_id: str
    source_video: str
    frames: tuple[FrameInfo, ...]
    manifest_path: Path

    @property
    def base_dir(self) -> Path:
        return self.manifest_path.parent


def _require(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ValueError(f"Manifest missing required field '{key}'.")
    return data[key]


def load_manifest(path: str | Path) -> FramesManifest:
    manifest_path = Path(path).expanduser().resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object.")

    frames_data = _require(data, "frames")
    if not isinstance(frames_data, list) or not frames_data:
        raise ValueError("Manifest 'frames' must be a non-empty list.")

    base_dir = manifest_path.parent
    frames: list[FrameInfo] = []
    for index, item in enumerate(frames_data):
        if not isinstance(item, dict):
            raise ValueError(f"Frame entry at index {index} must be an object.")

        frame_id = str(_require(item, "frame_id"))
        raw_path = Path(str(_require(item, "path"))).expanduser()
        frame_path = raw_path if raw_path.is_absolute() else (base_dir / raw_path).resolve()
        timestamp_sec = float(_require(item, "timestamp_sec"))
        frames.append(FrameInfo(frame_id=frame_id, path=frame_path, timestamp_sec=timestamp_sec))

    return FramesManifest(
        video_id=str(_require(data, "video_id")),
        source_video=str(_require(data, "source_video")),
        frames=tuple(frames),
        manifest_path=manifest_path,
    )
