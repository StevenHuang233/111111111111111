#!/usr/bin/env python
"""Generate timestamped audio subtitles for the World Cup harness reference.

This script is intentionally dependency-light. It follows the same Bcut/Bijian
ASR protocol used by VideoCaptioner, but only relies on Python stdlib plus
ffmpeg so it can run in the bare ailab-hackathon Python 3.11 environment.

The Bcut/Bijian ASR path uploads extracted audio chunks to a third-party cloud
service. Use it only when the media owner allows that upload.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = (
    PROJECT_ROOT.parent
    / "hackathon"
    / "vedio"
    / "德国_库拉索.mp4"
)
DEFAULT_FFMPEG = Path(r"D:\software\tools\Doxent\platform\win\ffmpeg.exe")
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "work-dir" / "worldcup_caption_reference"

Bcut_API_BASE = "https://member.bilibili.com/x/bcut/rubick-interface"
Bcut_REQ_UPLOAD = Bcut_API_BASE + "/resource/create"
Bcut_COMMIT_UPLOAD = Bcut_API_BASE + "/resource/create/complete"
Bcut_CREATE_TASK = Bcut_API_BASE + "/task"
Bcut_QUERY_RESULT = Bcut_API_BASE + "/task/result"

JSON_HEADERS = {
    "User-Agent": "Bilibili/1.0.0 (https://www.bilibili.com)",
    "Content-Type": "application/json",
}


@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: str
    chunk_index: int


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)


def run_process(args: list[str], *, allow_error: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not allow_error and proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + subprocess.list2cmdline(args)
            + "\n\nSTDOUT:\n"
            + proc.stdout
            + "\n\nSTDERR:\n"
            + proc.stderr
        )
    return proc


def probe_duration_seconds(ffmpeg: Path, video: Path) -> float:
    proc = run_process([str(ffmpeg), "-hide_banner", "-i", str(video)], allow_error=True)
    text = proc.stderr + "\n" + proc.stdout
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not match:
        raise RuntimeError("Could not parse video duration from ffmpeg output.")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def extract_audio(ffmpeg: Path, video: Path, output_audio: Path) -> None:
    if output_audio.exists() and output_audio.stat().st_size > 0:
        log(f"Full audio already exists: {output_audio}")
        return
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    log(f"Extracting full audio -> {output_audio}")
    run_process(
        [
            str(ffmpeg),
            "-hide_banner",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "64k",
            str(output_audio),
        ]
    )


def extract_chunks(
    ffmpeg: Path,
    video: Path,
    chunk_dir: Path,
    duration_seconds: float,
    chunk_seconds: int,
) -> list[tuple[Path, int]]:
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunks: list[tuple[Path, int]] = []
    count = math.ceil(duration_seconds / chunk_seconds)
    for idx in range(count):
        start = idx * chunk_seconds
        remaining = max(0.0, duration_seconds - start)
        length = min(chunk_seconds, remaining)
        chunk_path = chunk_dir / f"chunk_{idx:03d}_{start:06d}s.mp3"
        chunks.append((chunk_path, int(start * 1000)))
        if chunk_path.exists() and chunk_path.stat().st_size > 0:
            continue
        log(f"Extracting chunk {idx + 1}/{count}: {start:.1f}s + {length:.1f}s")
        run_process(
            [
                str(ffmpeg),
                "-hide_banner",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-t",
                f"{length:.3f}",
                "-i",
                str(video),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-b:a",
                "64k",
                str(chunk_path),
            ]
        )
    return chunks


def http_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=JSON_HEADERS, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def http_put_bytes(url: str, body: bytes, timeout: int = 120) -> str:
    request = urllib.request.Request(url, data=body, headers=JSON_HEADERS, method="PUT")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()
        return response.headers.get("Etag", "")


def bcut_transcribe(audio_path: Path, *, poll_seconds: int, max_poll: int) -> dict[str, Any]:
    audio_bytes = audio_path.read_bytes()
    create_resp = http_json(
        Bcut_REQ_UPLOAD,
        method="POST",
        payload={
            "type": 2,
            "name": "audio.mp3",
            "size": len(audio_bytes),
            "ResourceFileType": "mp3",
            "model_id": "8",
        },
    )
    upload_data = create_resp["data"]

    per_size = int(upload_data["per_size"])
    etags: list[str] = []
    for clip, upload_url in enumerate(upload_data["upload_urls"]):
        start = clip * per_size
        end = min((clip + 1) * per_size, len(audio_bytes))
        etag = http_put_bytes(upload_url, audio_bytes[start:end])
        if etag:
            etags.append(etag)

    commit_resp = http_json(
        Bcut_COMMIT_UPLOAD,
        method="POST",
        payload={
            "InBossKey": upload_data["in_boss_key"],
            "ResourceId": upload_data["resource_id"],
            "Etags": ",".join(etags),
            "UploadId": upload_data["upload_id"],
            "model_id": "8",
        },
    )
    download_url = commit_resp["data"]["download_url"]

    task_resp = http_json(
        Bcut_CREATE_TASK,
        method="POST",
        payload={"resource": download_url, "model_id": "8"},
    )
    task_id = task_resp["data"]["task_id"]

    last_state = None
    for _ in range(max_poll):
        result_resp = http_json(
            Bcut_QUERY_RESULT,
            params={"model_id": 7, "task_id": task_id},
            timeout=60,
        )
        result_data = result_resp["data"]
        last_state = result_data.get("state")
        if last_state == 4:
            return json.loads(result_data["result"])
        time.sleep(poll_seconds)

    raise TimeoutError(f"Bcut ASR timed out for {audio_path.name}; last state={last_state}")


def load_or_transcribe_chunk(
    chunk_path: Path,
    raw_dir: Path,
    idx: int,
    *,
    poll_seconds: int,
    max_poll: int,
    retries: int,
) -> dict[str, Any]:
    raw_path = raw_dir / f"{chunk_path.stem}.bcut.raw.json"
    if raw_path.exists() and raw_path.stat().st_size > 0:
        return json.loads(raw_path.read_text(encoding="utf-8"))

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            log(f"Transcribing chunk {idx}: {chunk_path.name} (attempt {attempt}/{retries})")
            result = bcut_transcribe(chunk_path, poll_seconds=poll_seconds, max_poll=max_poll)
            raw_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        except Exception as exc:
            last_error = exc
            log(f"Chunk {idx} failed: {exc}")
            time.sleep(min(30, 5 * attempt))
    raise RuntimeError(f"Failed to transcribe {chunk_path.name}: {last_error}")


def segments_from_bcut(raw: dict[str, Any], *, offset_ms: int, chunk_index: int) -> list[Segment]:
    segments: list[Segment] = []
    for utterance in raw.get("utterances", []):
        text = str(utterance.get("transcript", "")).strip()
        if not text:
            continue
        start = int(utterance["start_time"]) + offset_ms
        end = int(utterance["end_time"]) + offset_ms
        if end <= start:
            end = start + 500
        segments.append(Segment(start_ms=start, end_ms=end, text=text, chunk_index=chunk_index))
    return segments


def ms_to_srt(ms: int) -> str:
    total_seconds, milliseconds = divmod(max(0, int(ms)), 1000)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def ms_to_hhmmss(ms: int) -> str:
    total_seconds = max(0, int(round(ms / 1000)))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def write_srt(segments: list[Segment], path: Path) -> None:
    lines: list[str] = []
    for idx, seg in enumerate(segments, 1):
        lines.append(str(idx))
        lines.append(f"{ms_to_srt(seg.start_ms)} --> {ms_to_srt(seg.end_ms)}")
        lines.append(seg.text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_segments_json(segments: list[Segment], path: Path) -> None:
    payload = [
        {
            "index": idx,
            "video_time_start": ms_to_hhmmss(seg.start_ms),
            "video_time_end": ms_to_hhmmss(seg.end_ms),
            "start_ms": seg.start_ms,
            "end_ms": seg.end_ms,
            "text": seg.text,
            "source": "audio_asr_bcut",
            "chunk_index": seg.chunk_index,
            "reference_policy": "audio transcript is a reference signal, not a complete visual gold answer",
        }
        for idx, seg in enumerate(segments, 1)
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_timeline(segments: list[Segment], path: Path) -> None:
    lines = [
        "# Audio ASR Timeline / 音频识别时间线",
        "",
        "中文：此时间线来自音频 ASR，用于辅助评判抽帧视觉 agent，不是完整标准答案。",
        "",
    ]
    for seg in segments:
        lines.append(f"- `{ms_to_hhmmss(seg.start_ms)}-{ms_to_hhmmss(seg.end_ms)}` {seg.text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_eval_guide(path: Path, subtitle_name: str, segments_name: str) -> None:
    content = f"""# LLM Judge Rubric / 大模型分级评判指南

Reference files / 参考文件:

- `{subtitle_name}`
- `{segments_name}`

Audio ASR is a reference signal, not the sole gold answer.

中文：音频字幕是参考信号，不是唯一标准答案。目标 agent 是通过抽帧图片识别关键事件并生成解说，所以评判必须区分：

- visual-evident facts / 画面可见事实
- audio-only hints / 只有音轨中出现的信息
- unsupported hallucinations / agent 自己虚构的信息

## Suggested Dimensions / 建议维度

Score each from 0 to 5:

1. visual_event_grounding / 画面事件扎根度
2. audio_reference_consistency / 音频参考一致性
3. timestamp_usefulness / 时间戳可用性
4. commentary_quality / 中文解说质量
5. factual_safety / 事实安全
6. harness_improvement_signal / 对 harness 改进的帮助

## Failure Categories / 失败类别

- missed_key_event
- timestamp_drift
- hallucinated_entity
- weak_scene_type
- style_too_flat
- audio_only_gap
- verifier_gap
"""
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build timestamped audio subtitles via VideoCaptioner-style Bcut ASR.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--ffmpeg", type=Path, default=DEFAULT_FFMPEG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--chunk-seconds", type=int, default=600)
    parser.add_argument("--poll-seconds", type=int, default=2)
    parser.add_argument("--max-poll", type=int, default=500)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--allow-upload", action="store_true", help="Required to upload audio chunks to Bcut ASR.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.video.exists():
        raise FileNotFoundError(f"Input video not found: {args.video}")
    if not args.ffmpeg.exists():
        raise FileNotFoundError(f"ffmpeg not found: {args.ffmpeg}")

    run_dir = args.run_dir or args.output_root / f"{args.video.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    audio_dir = run_dir / "audio"
    chunks_dir = run_dir / "chunks"
    raw_dir = run_dir / "raw_asr"
    raw_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration_seconds(args.ffmpeg, args.video)
    log(f"Video duration: {duration:.2f}s")

    full_audio = audio_dir / f"{args.video.stem}.audio_16k_mono_64k.mp3"
    extract_audio(args.ffmpeg, args.video, full_audio)
    chunks = extract_chunks(args.ffmpeg, args.video, chunks_dir, duration, args.chunk_seconds)

    manifest = {
        "input_video": str(args.video),
        "ffmpeg": str(args.ffmpeg),
        "duration_seconds": duration,
        "chunk_seconds": args.chunk_seconds,
        "full_audio": str(full_audio),
        "bcut_upload_allowed": bool(args.allow_upload),
        "chunks": [
            {"index": idx, "path": str(path), "offset_ms": offset_ms}
            for idx, (path, offset_ms) in enumerate(chunks)
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.extract_only:
        log(f"Extract-only complete: {run_dir}")
        return 0
    if not args.allow_upload:
        log("ASR skipped. Rerun with --allow-upload after confirming third-party audio upload is permitted.")
        return 2

    all_segments: list[Segment] = []
    for idx, (chunk_path, offset_ms) in enumerate(chunks):
        raw = load_or_transcribe_chunk(
            chunk_path,
            raw_dir,
            idx,
            poll_seconds=args.poll_seconds,
            max_poll=args.max_poll,
            retries=args.retries,
        )
        all_segments.extend(segments_from_bcut(raw, offset_ms=offset_ms, chunk_index=idx))

    all_segments.sort(key=lambda seg: (seg.start_ms, seg.end_ms))
    srt_path = run_dir / f"{args.video.stem}.audio_reference.srt"
    json_path = run_dir / f"{args.video.stem}.audio_reference.segments.json"
    timeline_path = run_dir / f"{args.video.stem}.audio_reference.timeline.md"
    rubric_path = run_dir / "llm_judge_rubric.md"
    write_srt(all_segments, srt_path)
    write_segments_json(all_segments, json_path)
    write_timeline(all_segments, timeline_path)
    write_eval_guide(rubric_path, srt_path.name, json_path.name)

    log(f"Done: {run_dir}")
    log(f"SRT: {srt_path}")
    log(f"Segments JSON: {json_path}")
    log(f"Rubric: {rubric_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
