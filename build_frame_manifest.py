from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FRAME_RE = re.compile(r"(\d+)")


def frame_sort_key(path: Path) -> tuple[int, str]:
    match = FRAME_RE.search(path.stem)
    if match:
        return (int(match.group(1)), path.name)
    return (10**12, path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a frames_manifest.json from an extracted frame directory.")
    parser.add_argument("frames_dir", help="Directory containing extracted image frames.")
    parser.add_argument("--fps", type=float, default=4.0, help="Frame rate of the extracted frame sequence.")
    parser.add_argument("--video-id", default="video_frames", help="video_id written into the manifest.")
    parser.add_argument("--source-video", default="", help="Original source video name or path.")
    parser.add_argument("--output", default="", help="Output manifest path. Defaults to frames_dir/frames_manifest.json.")
    parser.add_argument("--start-index", type=int, default=0, help="Start from this sorted frame index.")
    parser.add_argument("--max-frames", type=int, default=0, help="Maximum number of frames to include. 0 means no limit.")
    parser.add_argument("--every-n", type=int, default=1, help="Keep every Nth frame from the sorted frame list.")
    args = parser.parse_args()

    if args.fps <= 0:
        raise ValueError("--fps must be positive.")
    if args.every_n <= 0:
        raise ValueError("--every-n must be positive.")

    frames_dir = Path(args.frames_dir).expanduser().resolve()
    if not frames_dir.exists():
        raise FileNotFoundError(frames_dir)

    images = sorted(
        [path for path in frames_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}],
        key=frame_sort_key,
    )
    selected = images[args.start_index :: args.every_n]
    if args.max_frames > 0:
        selected = selected[: args.max_frames]
    if not selected:
        raise ValueError("No frames selected.")

    manifest_path = Path(args.output).expanduser().resolve() if args.output else frames_dir / "frames_manifest.json"
    manifest = {
        "video_id": args.video_id,
        "source_video": args.source_video or frames_dir.name,
        "frames": [
            {
                "frame_id": path.stem,
                "path": path.name if path.parent == manifest_path.parent else str(path),
                "timestamp_sec": round(frame_sort_key(path)[0] / args.fps, 3),
            }
            for path in selected
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")
    print(f"Frames: {len(selected)}")
    print(f"Time range: {manifest['frames'][0]['timestamp_sec']}s - {manifest['frames'][-1]['timestamp_sec']}s")


if __name__ == "__main__":
    main()
