from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dense per-event manifests from coarse events and a full manifest.")
    parser.add_argument("--full-manifest", required=True, help="Full-density frames_manifest.json.")
    parser.add_argument("--events", required=True, help="Coarse events.json produced by dump_scan_result().")
    parser.add_argument("--output-dir", required=True, help="Directory for per-event detailed manifests.")
    parser.add_argument("--padding-sec", type=float, default=0.0, help="Extra seconds before/after each event interval.")
    parser.add_argument("--sample-fps", type=float, default=1.0, help="Output sampling rate for detailed manifests. Use <=0 to keep every frame.")
    args = parser.parse_args()

    full_manifest = load_manifest(args.full_manifest)
    events_data = json.loads(Path(args.events).read_text(encoding="utf-8"))
    events = events_data.get("events", [])
    if not isinstance(events, list):
        raise ValueError("events file must contain an 'events' list.")

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = str(event.get("event_id", f"E{written + 1:03d}"))
        event_type = str(event.get("event_type", "event"))
        start_sec = max(0.0, float(event.get("start_sec", 0.0)) - args.padding_sec)
        end_sec = float(event.get("end_sec", start_sec)) + args.padding_sec
        interval_frames = [frame for frame in full_manifest.frames if start_sec <= frame.timestamp_sec <= end_sec]
        selected = sample_frames_by_fps(interval_frames, args.sample_fps)
        if not selected:
            continue

        manifest = {
            "video_id": f"{full_manifest.video_id}_{event_id}_dense",
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
                "event_id": event_id,
                "event_type": event_type,
                "coarse_start_sec": event.get("start_sec"),
                "coarse_end_sec": event.get("end_sec"),
                "padding_sec": args.padding_sec,
                "sample_fps": args.sample_fps,
                "input_frame_count": len(interval_frames),
                "sampled_frame_count": len(selected),
            },
        }
        output = out_dir / f"{event_id}_{event_type}_dense_manifest.json"
        output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {output} ({len(selected)} frames, {start_sec}s - {end_sec}s)")
        written += 1

    print(f"Detailed manifests written: {written}")


def sample_frames_by_fps(frames, sample_fps: float):
    if not frames or sample_fps <= 0:
        return list(frames)

    min_interval_sec = 1.0 / sample_fps
    selected = []
    last_timestamp = None
    for frame in sorted(frames, key=lambda item: item.timestamp_sec):
        if last_timestamp is None or frame.timestamp_sec >= last_timestamp + min_interval_sec - 1e-6:
            selected.append(frame)
            last_timestamp = frame.timestamp_sec
    return selected


if __name__ == "__main__":
    main()
