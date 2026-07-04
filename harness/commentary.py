from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient

from .json_utils import extract_json_object, to_pretty_json
from .manifest import FramesManifest
from .scanner import EventCandidate
from .styles import StyleProfile
from .time_utils import format_timestamp
from .tracing import NullTracker, StepTracker


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class SubtitleLine:
    start_sec: float
    end_sec: float
    text: str


@dataclass(frozen=True)
class CommentarySegment:
    event_id: str
    event_type: str
    talk_start_sec: float
    talk_end_sec: float
    commentary_text: str
    subtitle_lines: tuple[SubtitleLine, ...] = ()


@dataclass(frozen=True)
class CommentaryResult:
    video_id: str
    style_id: str
    segments: tuple[CommentarySegment, ...]


def generate_commentary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
) -> CommentaryResult:
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "generate_commentary",
        "start",
        {"video_id": manifest.video_id, "style_id": style.style_id, "event_count": len(events)},
    )
    segments: list[CommentarySegment] = []
    for event in events:
        trace.record(
            "generate_commentary.event",
            "prepare_model_call",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "time_range": [event.start_sec, event.end_sec],
                "phase_types": [phase.phase_type for phase in event.phases],
            },
        )
        data = active_client.chat(
            _build_commentary_messages(event, manifest, style),
            temperature=style.temperature,
            top_p=style.top_p,
            max_tokens=style.max_tokens,
            thinking_mode=style.thinking_mode,
        )
        text = data["choices"][0]["message"].get("content") or ""
        segments.append(_parse_commentary_response(text, event))
        trace.record("generate_commentary.event", "parsed_model_response", {"event_id": event.event_id})

    trace.record("generate_commentary", "finish", {"segment_count": len(segments)})
    return CommentaryResult(video_id=manifest.video_id, style_id=style.style_id, segments=tuple(segments))


def _build_commentary_messages(
    event: EventCandidate,
    manifest: FramesManifest,
    style: StyleProfile,
) -> list[dict[str, str]]:
    event_json = {
        "video_id": manifest.video_id,
        "source_video": manifest.source_video,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "time_range": {
            "start_sec": event.start_sec,
            "end_sec": event.end_sec,
            "start_label": format_timestamp(event.start_sec),
            "end_label": format_timestamp(event.end_sec),
        },
        "evidence_frames": list(event.evidence_frames),
        "confidence": event.confidence,
        "evidence_summary": event.evidence_summary,
        "phases": [
            {
                "phase_type": phase.phase_type,
                "start_sec": phase.start_sec,
                "end_sec": phase.end_sec,
                "start_label": format_timestamp(phase.start_sec),
                "end_label": format_timestamp(phase.end_sec),
                "evidence_frames": list(phase.evidence_frames),
                "evidence_summary": phase.evidence_summary,
            }
            for phase in event.phases
        ],
    }
    phase_instruction = ""
    if event.event_type == "goal" and any(phase.phase_type == "replay" for phase in event.phases):
        phase_instruction = (
            "This goal event includes both the live goal phase and a replay phase. "
            "Generate dual commentary: first describe the live goal moment, then use the replay phase to add details such as shooting route, passing, positioning, defensive issues, or goalkeeper reaction when visible."
        )
    prompt = f"""
You are generating football commentary for one detected event.

Use this style exactly:
{style.prompt_injection}

The narration must fit from {format_timestamp(event.start_sec)} to {format_timestamp(event.end_sec)}.
Do not invent player names, teams, scores, or facts that are not present in the event evidence.
{phase_instruction}

Event data:
{to_pretty_json(event_json)}

Return JSON only:
{{
  "commentary_text": "spoken commentary text",
  "subtitle_lines": [
    {{"start_sec": {event.start_sec}, "end_sec": {event.end_sec}, "text": "subtitle text"}}
  ]
}}
""".strip()
    return [{"role": "user", "content": prompt}]


def _parse_commentary_response(text: str, event: EventCandidate) -> CommentarySegment:
    try:
        payload = extract_json_object(text)
        commentary_text = str(payload.get("commentary_text", "")).strip() or text.strip()
        subtitle_rows = payload.get("subtitle_lines", [])
        subtitles: list[SubtitleLine] = []
        if isinstance(subtitle_rows, list):
            for row in subtitle_rows:
                if not isinstance(row, dict):
                    continue
                subtitles.append(
                    SubtitleLine(
                        start_sec=float(row.get("start_sec", event.start_sec)),
                        end_sec=float(row.get("end_sec", event.end_sec)),
                        text=str(row.get("text", "")).strip(),
                    )
                )
    except Exception:
        commentary_text = text.strip()
        subtitles = []

    return CommentarySegment(
        event_id=event.event_id,
        event_type=event.event_type,
        talk_start_sec=event.start_sec,
        talk_end_sec=event.end_sec,
        commentary_text=commentary_text,
        subtitle_lines=tuple(subtitles),
    )


def commentary_result_to_dict(result: CommentaryResult) -> dict[str, Any]:
    return {
        "video_id": result.video_id,
        "style_id": result.style_id,
        "segments": [
            {
                "event_id": segment.event_id,
                "event_type": segment.event_type,
                "talk_start_sec": segment.talk_start_sec,
                "talk_end_sec": segment.talk_end_sec,
                "commentary_text": segment.commentary_text,
                "subtitle_lines": [
                    {
                        "start_sec": subtitle.start_sec,
                        "end_sec": subtitle.end_sec,
                        "text": subtitle.text,
                    }
                    for subtitle in segment.subtitle_lines
                ],
            }
            for segment in result.segments
        ],
    }


def dump_commentary_result(result: CommentaryResult, path: str | Path) -> None:
    Path(path).write_text(to_pretty_json(commentary_result_to_dict(result)), encoding="utf-8")
