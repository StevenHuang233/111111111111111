from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient, image_source_to_url

from .json_utils import extract_json_object, to_pretty_json
from .manifest import FrameInfo, FramesManifest
from .scanner import EventCandidate
from .styles import StyleProfile
from .time_utils import format_timestamp
from .tracing import NullTracker, StepTracker, clip_text, should_record_model_io, tracker_text_limit


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


@dataclass(frozen=True)
class VisualCommentaryConfig:
    max_frames_per_event: int = 12
    max_frames_per_phase: int = 4


def generate_commentary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    visual_config: VisualCommentaryConfig | None = None,
) -> CommentaryResult:
    return generate_visual_commentary(events, manifest, style, client, tracker, visual_config)


def generate_commentary_from_summary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
) -> CommentaryResult:
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "generate_commentary_from_summary",
        "start",
        {"video_id": manifest.video_id, "style_id": style.style_id, "event_count": len(events)},
    )
    segments: list[CommentarySegment] = []
    for event in events:
        trace.record(
            "generate_commentary_from_summary.event",
            "prepare_model_call",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "time_range": [event.start_sec, event.end_sec],
                "phase_types": [phase.phase_type for phase in event.phases],
            },
        )
        messages = _build_commentary_messages(event, manifest, style)
        if should_record_model_io(trace):
            trace.record(
                "generate_commentary_from_summary.event",
                "model_call_input",
                {
                    "event_id": event.event_id,
                    "prompt": clip_text(str(messages[0].get("content", "")), tracker_text_limit(trace)),
                },
            )
        data = active_client.chat(
            messages,
            temperature=style.temperature,
            top_p=style.top_p,
            max_tokens=style.max_tokens,
            thinking_mode=style.thinking_mode,
        )
        text = data["choices"][0]["message"].get("content") or ""
        if should_record_model_io(trace):
            trace.record(
                "generate_commentary_from_summary.event",
                "model_call_output",
                {"event_id": event.event_id, "content": clip_text(text, tracker_text_limit(trace))},
            )
        segments.append(_parse_commentary_response(text, event))
        trace.record("generate_commentary_from_summary.event", "parsed_model_response", {"event_id": event.event_id})

    trace.record("generate_commentary_from_summary", "finish", {"segment_count": len(segments)})
    return CommentaryResult(video_id=manifest.video_id, style_id=style.style_id, segments=tuple(segments))


def generate_visual_commentary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    config: VisualCommentaryConfig | None = None,
) -> CommentaryResult:
    visual_config = config or VisualCommentaryConfig()
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "generate_visual_commentary",
        "start",
        {
            "video_id": manifest.video_id,
            "style_id": style.style_id,
            "event_count": len(events),
            "max_frames_per_event": visual_config.max_frames_per_event,
            "max_frames_per_phase": visual_config.max_frames_per_phase,
        },
    )

    segments: list[CommentarySegment] = []
    for event in events:
        selected_frames = _select_visual_frames(event, manifest.frames, visual_config)
        trace.record(
            "generate_visual_commentary.event",
            "prepare_model_call",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "time_range": [event.start_sec, event.end_sec],
                "phase_types": [phase.phase_type for phase in event.phases],
                "selected_frame_ids": [frame.frame_id for frame in selected_frames],
            },
        )
        messages = _build_visual_commentary_messages(event, manifest, style, selected_frames)
        if should_record_model_io(trace):
            trace.record(
                "generate_visual_commentary.event",
                "model_call_input",
                {
                    "event_id": event.event_id,
                    "prompt": clip_text(str(messages[0]["content"][0].get("text", "")), tracker_text_limit(trace)),
                    "frames": [
                        {
                            "frame_id": frame.frame_id,
                            "timestamp_sec": frame.timestamp_sec,
                            "timestamp": format_timestamp(frame.timestamp_sec),
                            "path": str(frame.path),
                        }
                        for frame in selected_frames
                    ],
                    "image_payload_policy": "Image inputs are sent as data URIs to the API, but trace records local paths instead of base64 payloads.",
                },
            )
        data = active_client.chat(
            messages,
            temperature=style.temperature,
            top_p=style.top_p,
            max_tokens=style.max_tokens,
            thinking_mode=style.thinking_mode,
        )
        text = data["choices"][0]["message"].get("content") or ""
        if should_record_model_io(trace):
            trace.record(
                "generate_visual_commentary.event",
                "model_call_output",
                {"event_id": event.event_id, "content": clip_text(text, tracker_text_limit(trace))},
            )
        segments.append(_parse_commentary_response(text, event))
        trace.record("generate_visual_commentary.event", "parsed_model_response", {"event_id": event.event_id})

    trace.record("generate_visual_commentary", "finish", {"segment_count": len(segments)})
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
Fact and style rules:
- Evidence overrides the event label. If event_type says "goal" but the evidence shows a save, miss, replay, or unclear outcome, do not claim a goal.
- Only claim a goal or score change when the evidence contains a scoreboard increment, ball over the line/in the net, or immediate unambiguous live celebration after a finish.
- Do not invent player names, teams, scores, cards, referees, venues, or tactical facts that are not present in the event evidence.
- Mention player names only if they are visible in the evidence or supplied by structured metadata. Otherwise use team, role, or jersey number when visible.
- Avoid repetitive kit-color phrases such as "player in white" or "green goalkeeper"; use team/role wording instead. Kit color is only a rare fallback when identity is otherwise impossible.
- Never introduce a country, club, or team name that is absent from the event data or source video.
- If score, scorer, or match clock is uncertain, say the visual evidence is unclear instead of guessing.
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


def _build_visual_commentary_messages(
    event: EventCandidate,
    manifest: FramesManifest,
    style: StyleProfile,
    frames: tuple[FrameInfo, ...],
) -> list[dict[str, Any]]:
    event_json = _event_to_prompt_dict(event, manifest)
    phase_instruction = ""
    if event.event_type == "goal" and any(phase.phase_type == "replay" for phase in event.phases):
        phase_instruction = (
            "This goal event includes both the live goal phase and a replay phase. "
            "Generate dual commentary: first describe the live goal moment, then use the replay frames to add details such as shooting route, passing, positioning, defensive issues, or goalkeeper reaction when visible."
        )
    frame_listing = "\n".join(
        f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]" for frame in frames
    )
    prompt = f"""
You are generating football commentary for one detected event using both structured event data and selected visual frames.

Use this style exactly:
{style.prompt_injection}

The narration must fit from {format_timestamp(event.start_sec)} to {format_timestamp(event.end_sec)}.
Use the provided frames to enrich visual details, but do not invent player names, teams, scores, or facts that are not present in the event data or visible frames.
Treat selected frames as representative samples from the event and phase intervals, not as a complete video clip.
Fact and style rules:
- Evidence overrides the event label. If event_type says "goal" but the selected frames show a save, miss, replay, or unclear outcome, do not claim a goal.
- Only claim a goal or score change when the frames or event evidence show a scoreboard increment, ball over the line/in the net, or immediate unambiguous live celebration after a finish.
- Mention player names only if a shirt number/name graphic, scoreboard graphic, event data, or user metadata supports that name. Otherwise use team, role, or jersey number when visible.
- Avoid repetitive kit-color phrases such as "player in white" or "green goalkeeper"; use team/role wording instead. Kit color is only a rare fallback when identity is otherwise impossible.
- Never introduce a country, club, or team name that is absent from the event data, source video, or visible broadcast graphics.
- If score, scorer, or match clock is uncertain, say the visual evidence is unclear instead of guessing.
{phase_instruction}

Selected frame prefixes:
{frame_listing}

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
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for frame in frames:
        content.append({"type": "text", "text": f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]"})
        content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame.path))}})
    return [{"role": "user", "content": content}]


def _event_to_prompt_dict(event: EventCandidate, manifest: FramesManifest) -> dict[str, Any]:
    return {
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


def _select_visual_frames(
    event: EventCandidate,
    manifest_frames: tuple[FrameInfo, ...],
    config: VisualCommentaryConfig,
) -> tuple[FrameInfo, ...]:
    frame_by_id = {frame.frame_id: frame for frame in manifest_frames}
    selected_frames: list[FrameInfo] = []
    for phase in event.phases:
        phase_frames = _frames_in_time_range(manifest_frames, phase.start_sec, phase.end_sec)
        selected_frames.extend(
            _select_related_frame_sample(
                phase_frames,
                phase.evidence_frames,
                config.max_frames_per_phase,
                frame_by_id,
            )
        )

    selected_frames = _unique_frames(selected_frames)
    remaining_budget = max(0, config.max_frames_per_event - len(selected_frames))
    if remaining_budget:
        event_frames = _frames_in_time_range(manifest_frames, event.start_sec, event.end_sec)
        selected_frames.extend(
            _select_related_frame_sample(
                event_frames,
                event.evidence_frames,
                remaining_budget,
                frame_by_id,
            )
        )

    return tuple(_unique_frames(selected_frames)[: config.max_frames_per_event])


def _frames_in_time_range(frames: tuple[FrameInfo, ...], start_sec: float, end_sec: float) -> tuple[FrameInfo, ...]:
    return tuple(frame for frame in frames if start_sec <= frame.timestamp_sec <= end_sec)


def _select_related_frame_sample(
    interval_frames: tuple[FrameInfo, ...],
    evidence_frame_ids: tuple[str, ...],
    limit: int,
    frame_by_id: dict[str, FrameInfo],
) -> list[FrameInfo]:
    if limit <= 0:
        return []

    evidence_frames = tuple(frame_by_id[frame_id] for frame_id in evidence_frame_ids if frame_id in frame_by_id)
    selected = list(_sample_frames(evidence_frames, min(limit, len(evidence_frames))))
    remaining = limit - len(_unique_frames(selected))
    if remaining > 0:
        selected.extend(_sample_frames(interval_frames, remaining))
    return _unique_frames(selected)[:limit]


def _sample_frames(frames: tuple[FrameInfo, ...], limit: int) -> tuple[FrameInfo, ...]:
    if limit <= 0 or not frames:
        return ()
    if len(frames) <= limit:
        return frames
    if limit == 1:
        return (frames[len(frames) // 2],)

    positions = [round(index * (len(frames) - 1) / (limit - 1)) for index in range(limit)]
    return tuple(frames[position] for position in dict.fromkeys(positions))


def _unique_frames(frames: list[FrameInfo]) -> list[FrameInfo]:
    by_id: dict[str, FrameInfo] = {}
    for frame in frames:
        by_id.setdefault(frame.frame_id, frame)
    return sorted(by_id.values(), key=lambda frame: frame.timestamp_sec)


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
