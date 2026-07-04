from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient, image_source_to_url

from .event_types import EventTypeDefinition, load_event_types
from .json_utils import extract_json_object, to_pretty_json
from .match_context import MatchContext, match_context_block
from .manifest import FrameInfo, FramesManifest
from .scanner import EventCandidate
from .styles import StyleProfile, style_instruction_block
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
    context_frames_each_side: int = 1
    sample_fps: float | None = 0.5


def generate_commentary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    visual_config: VisualCommentaryConfig | None = None,
    match_context: MatchContext | None = None,
) -> CommentaryResult:
    return generate_visual_commentary(events, manifest, style, client, tracker, visual_config, match_context)


def generate_commentary_from_summary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    match_context: MatchContext | None = None,
) -> CommentaryResult:
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "generate_commentary_from_summary",
        "start",
        {
            "video_id": manifest.video_id,
            "style_id": style.style_id,
            "event_count": len(events),
            "match_context_id": match_context.context_id if match_context else None,
        },
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
        messages = _build_commentary_messages(event, manifest, style, match_context)
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
    match_context: MatchContext | None = None,
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
            "context_frames_each_side": visual_config.context_frames_each_side,
            "sample_fps": visual_config.sample_fps,
            "match_context_id": match_context.context_id if match_context else None,
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
        messages = _build_visual_commentary_messages(event, manifest, style, selected_frames, match_context)
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
    match_context: MatchContext | None = None,
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
    if event.event_type == "goal" and any(phase.phase_type in {"replay", "celebration", "var_review"} for phase in event.phases):
        phase_instruction = (
            "This goal event may be a goal sequence package with buildup, live_goal, replay, celebration, and var_review phases. "
            "Generate sequence-aware commentary: call the live_goal first, then use replay phases for tactical or technical details, "
            "celebration phases for emotional reaction, and var_review phases only if the evidence clearly supports review context."
        )
    prompt = f"""
You are generating football commentary for one detected event.

Use this style exactly:
{style_instruction_block(style, "english_generation")}

Match context for factual disambiguation:
{match_context_block(match_context)}

Event type reference for this candidate:
{_event_type_reference_block(event.event_type)}

The narration must fit from {format_timestamp(event.start_sec)} to {format_timestamp(event.end_sec)}.
Write all returned commentary_text and subtitle_lines in English only.
Do not invent player names, teams, scores, or facts that are not present in the event evidence.
If an exact name, team, or score is uncertain, describe it visually instead of guessing.
Treat event_type as a pipeline candidate label, not as proof. For event_type=goal, call it as a goal only when the event evidence, selected frames, or a goal verification note clearly supports an actual scored goal. If the evidence contradicts the label, describe the visible action conservatively instead of forcing a goal call.
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
    match_context: MatchContext | None = None,
) -> list[dict[str, Any]]:
    event_json = _event_to_prompt_dict(event, manifest)
    phase_instruction = ""
    if event.event_type == "goal" and any(phase.phase_type in {"replay", "celebration", "var_review"} for phase in event.phases):
        phase_instruction = (
            "This goal event may be a goal sequence package with buildup, live_goal, replay, celebration, and var_review phases. "
            "Generate sequence-aware commentary: call the live_goal first, then use replay frames for tactical or technical details, "
            "celebration frames for emotional reaction, and var_review frames only if the evidence clearly supports review context."
        )
    frame_listing = "\n".join(
        f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]" for frame in frames
    )
    prompt = f"""
You are generating football commentary for one detected event using both structured event data and selected visual frames.

Use this style exactly:
{style_instruction_block(style, "english_generation")}

Match context for factual disambiguation:
{match_context_block(match_context)}

Event type reference for this candidate:
{_event_type_reference_block(event.event_type)}

The narration must fit from {format_timestamp(event.start_sec)} to {format_timestamp(event.end_sec)}.
Write all returned commentary_text and subtitle_lines in English only.
Use the provided frames to enrich visual details, but do not invent player names, teams, scores, or facts that are not present in the event data or visible frames.
If an exact name, team, or score is uncertain, describe it visually instead of guessing.
Treat event_type as a pipeline candidate label, not as proof. For event_type=goal, call it as a goal only when the event evidence, selected frames, or a goal verification note clearly supports an actual scored goal. If the evidence contradicts the label, describe the visible action conservatively instead of forcing a goal call.
Treat selected frames as representative samples from the event and phase intervals, not as a complete video clip.
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


def _event_type_reference_block(event_type: str) -> str:
    try:
        registry = load_event_types()
        definition = next((item for item in registry.definitions if item.event_id == event_type), None)
    except Exception:
        definition = None
    if definition is None:
        return (
            f"- event_type: {event_type}\n"
            "- description: No configured definition was found. Use the visible frames and event evidence conservatively."
        )
    return _format_event_type_definition(definition)


def _format_event_type_definition(definition: EventTypeDefinition) -> str:
    lines = [
        f"- event_type: {definition.event_id} ({definition.name})",
        f"- description: {definition.description}",
    ]
    if definition.positive_cues:
        lines.append(f"- positive cues: {'; '.join(definition.positive_cues)}")
    if definition.negative_cues:
        lines.append(f"- negative cues: {'; '.join(definition.negative_cues)}")
    lines.append("- usage: Use these cues to interpret the candidate label, but let the event evidence and visible frames decide the final wording.")
    return "\n".join(lines)


def _select_visual_frames(
    event: EventCandidate,
    manifest_frames: tuple[FrameInfo, ...],
    config: VisualCommentaryConfig,
) -> tuple[FrameInfo, ...]:
    frame_by_id = {frame.frame_id: frame for frame in manifest_frames}
    selected_frames: list[FrameInfo] = []
    for phase in event.phases:
        phase_frames = _frames_in_time_range_with_context(
            manifest_frames,
            phase.start_sec,
            phase.end_sec,
            config.context_frames_each_side,
        )
        phase_frames = _sample_frames_by_fps(phase_frames, config.sample_fps)
        selected_frames.extend(
            _select_related_frame_sample(
                phase_frames,
                phase.evidence_frames,
                config.max_frames_per_phase,
                frame_by_id,
                config.sample_fps,
            )
        )

    selected_frames = _unique_frames(selected_frames)
    remaining_budget = max(0, config.max_frames_per_event - len(selected_frames))
    if remaining_budget:
        event_frames = _frames_in_time_range_with_context(
            manifest_frames,
            event.start_sec,
            event.end_sec,
            config.context_frames_each_side,
        )
        event_frames = _sample_frames_by_fps(event_frames, config.sample_fps)
        selected_frames.extend(
            _select_related_frame_sample(
                event_frames,
                event.evidence_frames,
                remaining_budget,
                frame_by_id,
                config.sample_fps,
            )
        )

    return tuple(_unique_frames(selected_frames)[: config.max_frames_per_event])


def _frames_in_time_range(frames: tuple[FrameInfo, ...], start_sec: float, end_sec: float) -> tuple[FrameInfo, ...]:
    return tuple(frame for frame in frames if start_sec <= frame.timestamp_sec <= end_sec)


def _frames_in_time_range_with_context(
    frames: tuple[FrameInfo, ...],
    start_sec: float,
    end_sec: float,
    context_each_side: int,
) -> tuple[FrameInfo, ...]:
    in_range_indexes = [index for index, frame in enumerate(frames) if start_sec <= frame.timestamp_sec <= end_sec]
    if not in_range_indexes:
        return ()

    context = max(0, context_each_side)
    start_index = max(0, in_range_indexes[0] - context)
    end_index = min(len(frames) - 1, in_range_indexes[-1] + context)
    return frames[start_index : end_index + 1]


def _select_related_frame_sample(
    interval_frames: tuple[FrameInfo, ...],
    evidence_frame_ids: tuple[str, ...],
    limit: int,
    frame_by_id: dict[str, FrameInfo],
    sample_fps: float | None,
) -> list[FrameInfo]:
    if limit <= 0:
        return []

    evidence_frames = tuple(frame_by_id[frame_id] for frame_id in evidence_frame_ids if frame_id in frame_by_id)
    evidence_frames = _sample_frames_by_fps(evidence_frames, sample_fps)
    selected = list(_sample_frames(evidence_frames, min(limit, len(evidence_frames))))
    remaining = limit - len(_unique_frames(selected))
    if remaining > 0:
        selected.extend(_sample_frames(interval_frames, remaining))
    return _unique_frames(selected)[:limit]


def _sample_frames_by_fps(frames: tuple[FrameInfo, ...], sample_fps: float | None) -> tuple[FrameInfo, ...]:
    if not frames or sample_fps is None or sample_fps <= 0:
        return frames

    min_interval_sec = 1.0 / sample_fps
    selected: list[FrameInfo] = []
    last_timestamp: float | None = None
    for frame in sorted(frames, key=lambda item: item.timestamp_sec):
        if last_timestamp is None or frame.timestamp_sec >= last_timestamp + min_interval_sec - 1e-6:
            selected.append(frame)
            last_timestamp = frame.timestamp_sec
    return tuple(selected)


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
        commentary_text = _first_text_value(payload, ("commentary_text", "commentation_text", "commentary", "text")) or text.strip()
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


def _first_text_value(payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for value in payload.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


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
