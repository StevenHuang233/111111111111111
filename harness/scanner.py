from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Protocol

from intern_client import InternClient, image_source_to_url

from .event_types import EventTypeRegistry, load_event_types
from .json_utils import extract_json_object, to_pretty_json
from .match_context import MatchContext, match_context_block
from .manifest import FrameInfo, FramesManifest, load_manifest
from .styles import StyleProfile
from .time_utils import format_timestamp
from .tracing import NullTracker, StepTracker, clip_text, should_record_model_io, tracker_text_limit


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...


SCAN_ALGORITHM_VERSION = 3
DERIVED_SCAN_EVENT_TYPES = {"var_show"}


@dataclass(frozen=True)
class ScanConfig:
    window_size_frames: int = 6
    stride_frames: int = 3
    repair_attempts: int = 1
    event_types_path: str | None = None
    merge_gap_sec: float = 4.0
    goal_replay_merge_gap_sec: float = 30.0
    first_var_review_as_var_show: bool = True


@dataclass(frozen=True)
class EventPhase:
    phase_type: str
    start_sec: float
    end_sec: float
    evidence_frames: tuple[str, ...]
    evidence_summary: str


@dataclass(frozen=True)
class FrameObservation:
    frame_id: str
    timestamp_sec: float
    needs_commentary: bool
    event_type: str
    confidence: float
    evidence: str
    source_window: int


@dataclass(frozen=True)
class EventCandidate:
    event_id: str
    event_type: str
    start_sec: float
    end_sec: float
    evidence_frames: tuple[str, ...]
    confidence: float
    evidence_summary: str
    phases: tuple[EventPhase, ...] = ()


@dataclass(frozen=True)
class ScanResult:
    manifest: FramesManifest
    observations: tuple[FrameObservation, ...]
    events: tuple[EventCandidate, ...]
    window_errors: tuple[str, ...] = field(default_factory=tuple)


def build_windows(items: list[FrameInfo] | tuple[FrameInfo, ...], window_size: int, stride: int) -> list[tuple[int, int]]:
    if window_size <= 0:
        raise ValueError("window_size must be positive.")
    if stride <= 0:
        raise ValueError("stride must be positive.")
    if not items:
        return []

    windows: list[tuple[int, int]] = []
    start = 0
    while start < len(items):
        end = min(start + window_size, len(items))
        windows.append((start, end))
        if end == len(items):
            break
        start += stride
    return windows


def scan_events(
    manifest_path: str | Path,
    style: StyleProfile,
    config: ScanConfig | None = None,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    match_context: MatchContext | None = None,
) -> ScanResult:
    trace = tracker or NullTracker()
    scan_config = config or ScanConfig()
    trace.record(
        "scan_events",
        "start",
        {
            "manifest_path": str(manifest_path),
            "style_id": style.style_id,
            "window_size_frames": scan_config.window_size_frames,
            "stride_frames": scan_config.stride_frames,
            "merge_gap_sec": scan_config.merge_gap_sec,
            "goal_replay_merge_gap_sec": scan_config.goal_replay_merge_gap_sec,
            "first_var_review_as_var_show": scan_config.first_var_review_as_var_show,
            "scan_algorithm_version": SCAN_ALGORITHM_VERSION,
            "match_context_id": match_context.context_id if match_context else None,
        },
    )
    registry = load_event_types(scan_config.event_types_path)
    manifest = load_manifest(manifest_path)
    active_client = client or InternClient()

    raw_observations: list[FrameObservation] = []
    window_errors: list[str] = []
    windows = build_windows(manifest.frames, scan_config.window_size_frames, scan_config.stride_frames)
    trace.record(
        "scan_events",
        "build_windows",
        {
            "frame_count": len(manifest.frames),
            "window_count": len(windows),
            "windows": [{"start": start, "end": end} for start, end in windows],
        },
    )

    for window_index, (start, end) in enumerate(windows):
        frames = manifest.frames[start:end]
        trace.record(
            "scan_events.window",
            "prepare_model_call",
            {
                "window_index": window_index,
                "frame_ids": [frame.frame_id for frame in frames],
                "time_range": [frames[0].timestamp_sec, frames[-1].timestamp_sec] if frames else [],
            },
        )
        messages = _build_scan_messages(frames, style, registry, match_context)
        if should_record_model_io(trace):
            trace.record(
                "scan_events.window",
                "model_call_input",
                _scan_model_input_detail(messages, frames, window_index, trace),
            )
        data = active_client.chat(
            messages,
            temperature=style.temperature,
            top_p=style.top_p,
            max_tokens=style.max_tokens,
            thinking_mode=style.thinking_mode,
        )
        text = _response_text(data)
        if should_record_model_io(trace):
            trace.record(
                "scan_events.window",
                "model_call_output",
                {
                    "window_index": window_index,
                    "content": clip_text(text, tracker_text_limit(trace)),
                },
            )
        try:
            parsed = _parse_scan_response(text, frames, registry, window_index)
            raw_observations.extend(parsed)
            trace.record(
                "scan_events.window",
                "parsed_model_response",
                {
                    "window_index": window_index,
                    "observation_count": len(parsed),
                    "positive_count": sum(1 for item in parsed if item.needs_commentary),
                },
            )
        except Exception as exc:
            trace.record("scan_events.window", "parse_failed_try_repair", {"window_index": window_index, "error": str(exc)})
            repaired = _try_repair_scan_response(
                active_client, text, str(exc), frames, registry, window_index, scan_config.repair_attempts, trace
            )
            if repaired is None:
                window_errors.append(f"window={window_index}: {exc}")
                trace.record("scan_events.window", "repair_failed", {"window_index": window_index, "error": str(exc)})
            else:
                raw_observations.extend(repaired)
                trace.record(
                    "scan_events.window",
                    "repair_succeeded",
                    {
                        "window_index": window_index,
                        "observation_count": len(repaired),
                        "positive_count": sum(1 for item in repaired if item.needs_commentary),
                    },
                )

    observations = _aggregate_observations(manifest, raw_observations, registry)
    trace.record(
        "scan_events",
        "aggregate_frame_observations",
        {
            "raw_observation_count": len(raw_observations),
            "frame_observation_count": len(observations),
            "positive_frame_count": sum(1 for item in observations if item.needs_commentary),
        },
    )
    initial_events = _build_event_candidates(manifest, observations, registry)
    events = _merge_event_candidates(initial_events, scan_config, registry, observations)
    var_show_event_id = None
    if scan_config.first_var_review_as_var_show:
        events, var_show_event_id = _apply_first_var_review_as_var_show(events, registry)
    trace.record(
        "scan_events",
        "merge_event_candidates",
        {
            "initial_event_count": len(initial_events),
            "merged_event_count": len(events),
            "first_var_review_as_var_show": scan_config.first_var_review_as_var_show,
            "var_show_event_id": var_show_event_id,
        },
    )
    trace.record("scan_events", "finish", {"window_errors": len(window_errors), "event_count": len(events)})
    return ScanResult(
        manifest=manifest,
        observations=tuple(observations),
        events=tuple(events),
        window_errors=tuple(window_errors),
    )


def _build_scan_messages(
    frames: Iterable[FrameInfo],
    style: StyleProfile,
    registry: EventTypeRegistry,
    match_context: MatchContext | None = None,
) -> list[dict[str, Any]]:
    frame_list = list(frames)
    allowed_types = ", ".join(_scan_event_types(registry))
    event_reference = _scan_prompt_reference(registry)
    prefixes = "\n".join(_frame_prefix(frame) for frame in frame_list)
    prompt = f"""
You are a football video event scanner.

Style context for salience only:
{style.prompt_injection}

Match context for team and kit disambiguation:
{match_context_block(match_context)}

Allowed event_type values:
{allowed_types}

Event definitions and decision cues:
{event_reference}

For each frame, decide whether it contains a moment that needs commentary.
The event_type must be exactly one allowed value. Use no_event when nothing important is visible.

Frame time prefixes:
{prefixes}

Return JSON only with this schema:
{{
  "frames": [
    {{
      "frame_id": "same frame_id",
      "needs_commentary": true,
      "event_type": "goal",
      "confidence": 0.0,
      "evidence": "short visual evidence"
    }}
  ]
}}
""".strip()
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for frame in frame_list:
        content.append({"type": "text", "text": _frame_prefix(frame)})
        content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame.path))}})
    return [{"role": "user", "content": content}]


def _scan_model_input_detail(
    messages: list[dict[str, Any]],
    frames: tuple[FrameInfo, ...],
    window_index: int,
    tracker: StepTracker,
) -> dict[str, Any]:
    prompt = ""
    content = messages[0].get("content", []) if messages else []
    if isinstance(content, list) and content and isinstance(content[0], dict):
        prompt = str(content[0].get("text", ""))
    return {
        "window_index": window_index,
        "prompt": clip_text(prompt, tracker_text_limit(tracker)),
        "frames": [
            {
                "frame_id": frame.frame_id,
                "timestamp_sec": frame.timestamp_sec,
                "timestamp": format_timestamp(frame.timestamp_sec),
                "path": str(frame.path),
            }
            for frame in frames
        ],
        "image_payload_policy": "Image inputs are sent as data URIs to the API, but trace records local paths instead of base64 payloads.",
    }


def _frame_prefix(frame: FrameInfo) -> str:
    return f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]"


def _response_text(data: dict[str, Any]) -> str:
    return data["choices"][0]["message"].get("content") or ""


def _scan_event_types(registry: EventTypeRegistry) -> tuple[str, ...]:
    return tuple(event_type for event_type in registry.event_types if event_type not in DERIVED_SCAN_EVENT_TYPES)


def _scan_prompt_reference(registry: EventTypeRegistry) -> str:
    lines: list[str] = []
    for definition in registry.definitions:
        if definition.event_id in DERIVED_SCAN_EVENT_TYPES:
            continue
        lines.append(f"- {definition.event_id} ({definition.name}): {definition.description}")
        if definition.positive_cues:
            lines.append(f"  Positive cues: {'; '.join(definition.positive_cues)}")
        if definition.negative_cues:
            lines.append(f"  Negative cues: {'; '.join(definition.negative_cues)}")
    return "\n".join(lines)


def _normalize_scan_event_type(raw_event_type: str, registry: EventTypeRegistry) -> str:
    event_type = raw_event_type.strip()
    if event_type in DERIVED_SCAN_EVENT_TYPES:
        return "var_review" if "var_review" in registry.allowed else registry.no_event_type
    return event_type


def _parse_scan_response(
    text: str,
    frames: tuple[FrameInfo, ...],
    registry: EventTypeRegistry,
    window_index: int,
) -> list[FrameObservation]:
    payload = extract_json_object(text)
    rows = payload.get("frames")
    if not isinstance(rows, list):
        raise ValueError("Scan response must contain a 'frames' list.")

    frame_by_id = {frame.frame_id: frame for frame in frames}
    observations: list[FrameObservation] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each frame result must be an object.")
        raw_frame_id = str(row.get("frame_id", ""))
        frame_id = _normalize_frame_id(raw_frame_id, frame_by_id)
        if frame_id is None:
            raise ValueError(f"Unknown frame_id '{raw_frame_id}'.")

        event_type = registry.validate(_normalize_scan_event_type(str(row.get("event_type", registry.no_event_type)), registry))
        needs_commentary = bool(row.get("needs_commentary", False)) and event_type != registry.no_event_type
        confidence = max(0.0, min(1.0, float(row.get("confidence", 0.0))))
        evidence = str(row.get("evidence", "")).strip()
        frame = frame_by_id[frame_id]
        observations.append(
            FrameObservation(
                frame_id=frame_id,
                timestamp_sec=frame.timestamp_sec,
                needs_commentary=needs_commentary,
                event_type=event_type if needs_commentary else registry.no_event_type,
                confidence=confidence,
                evidence=evidence,
                source_window=window_index,
            )
        )

    return observations


def _normalize_frame_id(raw_frame_id: str, frame_by_id: dict[str, FrameInfo]) -> str | None:
    cleaned = raw_frame_id.strip()
    if cleaned in frame_by_id:
        return cleaned

    for separator in (",", " ", "\n", "\t"):
        prefix = cleaned.split(separator, 1)[0].strip()
        if prefix in frame_by_id:
            return prefix

    for frame_id in sorted(frame_by_id, key=len, reverse=True):
        if not cleaned.startswith(frame_id):
            continue
        suffix = cleaned[len(frame_id) :].strip()
        if not suffix or suffix.startswith((",", "[", "(", "-", "|")) or "timestamp" in suffix.lower():
            return frame_id
    return None


def _try_repair_scan_response(
    client: ChatClient,
    bad_text: str,
    error: str,
    frames: tuple[FrameInfo, ...],
    registry: EventTypeRegistry,
    window_index: int,
    attempts: int,
    tracker: StepTracker,
) -> list[FrameObservation] | None:
    if attempts <= 0:
        return None

    repair_prompt = f"""
Fix this football event scan response into valid JSON.
Error: {error}
Allowed event_type values: {", ".join(_scan_event_types(registry))}
Event definitions and decision cues:
{_scan_prompt_reference(registry)}
Required frame_ids: {", ".join(frame.frame_id for frame in frames)}

Bad response:
{bad_text}

Return JSON only with the same schema:
{{"frames":[{{"frame_id":"...","needs_commentary":false,"event_type":"no_event","confidence":0.0,"evidence":"..."}}]}}
""".strip()
    if should_record_model_io(tracker):
        tracker.record(
            "scan_events.window.repair",
            "model_call_input",
            {
                "window_index": window_index,
                "prompt": clip_text(repair_prompt, tracker_text_limit(tracker)),
            },
        )
    data = client.chat([{"role": "user", "content": repair_prompt}], temperature=0.0, top_p=1.0, max_tokens=1024)
    if should_record_model_io(tracker):
        tracker.record(
            "scan_events.window.repair",
            "model_call_output",
            {
                "window_index": window_index,
                "content": clip_text(_response_text(data), tracker_text_limit(tracker)),
            },
        )
    try:
        return _parse_scan_response(_response_text(data), frames, registry, window_index)
    except Exception:
        return None


def _aggregate_observations(
    manifest: FramesManifest,
    observations: list[FrameObservation],
    registry: EventTypeRegistry,
) -> list[FrameObservation]:
    by_frame: dict[str, list[FrameObservation]] = {}
    for observation in observations:
        by_frame.setdefault(observation.frame_id, []).append(observation)

    aggregated: list[FrameObservation] = []
    for frame in manifest.frames:
        candidates = by_frame.get(frame.frame_id, [])
        positive = [item for item in candidates if item.needs_commentary]
        if not positive:
            aggregated.append(
                FrameObservation(
                    frame_id=frame.frame_id,
                    timestamp_sec=frame.timestamp_sec,
                    needs_commentary=False,
                    event_type=registry.no_event_type,
                    confidence=0.0,
                    evidence="",
                    source_window=-1,
                )
            )
            continue

        best = max(positive, key=lambda item: item.confidence)
        evidence = "; ".join(dict.fromkeys(item.evidence for item in positive if item.evidence))
        aggregated.append(
            FrameObservation(
                frame_id=frame.frame_id,
                timestamp_sec=frame.timestamp_sec,
                needs_commentary=True,
                event_type=best.event_type,
                confidence=best.confidence,
                evidence=evidence,
                source_window=best.source_window,
            )
        )
    return aggregated


def _build_event_candidates(
    manifest: FramesManifest,
    observations: list[FrameObservation],
    registry: EventTypeRegistry,
) -> list[EventCandidate]:
    events: list[EventCandidate] = []
    index = 0
    while index < len(observations):
        current = observations[index]
        if not current.needs_commentary:
            index += 1
            continue

        event_type = current.event_type
        start = index
        end = index
        while (
            end + 1 < len(observations)
            and observations[end + 1].needs_commentary
            and observations[end + 1].event_type == event_type
        ):
            end += 1

        start_sec = manifest.frames[start].timestamp_sec
        end_sec = manifest.frames[end].timestamp_sec
        run = observations[start : end + 1]
        confidence = max(item.confidence for item in run)
        evidence_summary = "; ".join(dict.fromkeys(item.evidence for item in run if item.evidence))
        events.append(
            _candidate_with_default_phase(
            EventCandidate(
                event_id=f"E{len(events) + 1:03d}",
                event_type=registry.validate(event_type),
                start_sec=start_sec,
                end_sec=end_sec,
                evidence_frames=tuple(item.frame_id for item in run),
                confidence=confidence,
                evidence_summary=evidence_summary,
            )
            )
        )
        index = end + 1

    return events


def _candidate_with_default_phase(event: EventCandidate) -> EventCandidate:
    if event.phases:
        return event
    phase_type = "live_goal" if event.event_type == "goal" else event.event_type
    return EventCandidate(
        event_id=event.event_id,
        event_type=event.event_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=event.confidence,
        evidence_summary=event.evidence_summary,
        phases=(
            EventPhase(
                phase_type=phase_type,
                start_sec=event.start_sec,
                end_sec=event.end_sec,
                evidence_frames=event.evidence_frames,
                evidence_summary=event.evidence_summary,
            ),
        ),
    )


def _merge_event_candidates(
    candidates: list[EventCandidate],
    config: ScanConfig,
    registry: EventTypeRegistry,
    observations: list[FrameObservation] | None = None,
) -> list[EventCandidate]:
    if not candidates:
        return []

    ordered = sorted((_candidate_with_default_phase(candidate) for candidate in candidates), key=lambda item: item.start_sec)
    merged: list[EventCandidate] = []

    for candidate in ordered:
        if not merged:
            merged.append(candidate)
            continue

        previous = merged[-1]
        if _should_merge_events(previous, candidate, config, observations):
            merged[-1] = _merge_two_events(previous, candidate, registry)
        else:
            merged.append(candidate)

    return [_renumber_event(event, index + 1) for index, event in enumerate(merged)]


def _apply_first_var_review_as_var_show(
    events: list[EventCandidate],
    registry: EventTypeRegistry,
) -> tuple[list[EventCandidate], str | None]:
    if "var_show" not in registry.allowed or "var_review" not in registry.allowed:
        return list(events), None

    adjusted: list[EventCandidate] = []
    relabeled_event_id: str | None = None
    for event in events:
        if relabeled_event_id is None and event.event_type == "var_review":
            adjusted.append(_relabel_event_and_matching_phases(event, "var_show", "var_review"))
            relabeled_event_id = event.event_id
            continue
        adjusted.append(event)
    return adjusted, relabeled_event_id


def _relabel_event_and_matching_phases(
    event: EventCandidate,
    event_type: str,
    phase_type_to_replace: str,
) -> EventCandidate:
    return EventCandidate(
        event_id=event.event_id,
        event_type=event_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=event.confidence,
        evidence_summary=event.evidence_summary,
        phases=tuple(
            EventPhase(
                phase_type=event_type if phase.phase_type == phase_type_to_replace else phase.phase_type,
                start_sec=phase.start_sec,
                end_sec=phase.end_sec,
                evidence_frames=phase.evidence_frames,
                evidence_summary=phase.evidence_summary,
            )
            for phase in event.phases
        ),
    )


def _should_merge_events(
    left: EventCandidate,
    right: EventCandidate,
    config: ScanConfig,
    observations: list[FrameObservation] | None = None,
) -> bool:
    gap = right.start_sec - left.end_sec
    overlaps_or_close = gap <= config.merge_gap_sec
    has_no_event_barrier = _has_between_observation_barrier(left, right, observations, block_event_type_change=False)
    has_type_barrier = _has_between_observation_barrier(left, right, observations, block_event_type_change=True)

    if left.event_type == right.event_type and overlaps_or_close and not has_type_barrier:
        return True

    if (
        left.event_type == "goal"
        and right.event_type == "celebration_or_replay"
        and gap <= config.goal_replay_merge_gap_sec
        and not has_no_event_barrier
    ):
        return True

    if (
        left.event_type == "celebration_or_replay"
        and right.event_type == "goal"
        and gap <= config.goal_replay_merge_gap_sec
        and not has_no_event_barrier
    ):
        return True

    return False


def _has_between_observation_barrier(
    left: EventCandidate,
    right: EventCandidate,
    observations: list[FrameObservation] | None,
    *,
    block_event_type_change: bool,
) -> bool:
    if not observations:
        return False

    lower = min(left.end_sec, right.start_sec)
    upper = max(left.end_sec, right.start_sec)
    if lower == upper:
        return False

    for observation in observations:
        if not (lower < observation.timestamp_sec < upper):
            continue
        if not observation.needs_commentary:
            return True
        if block_event_type_change and observation.event_type not in {left.event_type, right.event_type}:
            return True
    return False


def _merge_two_events(left: EventCandidate, right: EventCandidate, registry: EventTypeRegistry) -> EventCandidate:
    event_type = _merged_event_type(left, right)
    phases = _normalize_phases(event_type, left.phases + right.phases)
    evidence_frames = _unique_tuple(left.evidence_frames + right.evidence_frames)
    evidence_summary = "; ".join(dict.fromkeys(part for part in [left.evidence_summary, right.evidence_summary] if part))
    return EventCandidate(
        event_id=left.event_id,
        event_type=registry.validate(event_type),
        start_sec=min(left.start_sec, right.start_sec),
        end_sec=max(left.end_sec, right.end_sec),
        evidence_frames=evidence_frames,
        confidence=max(left.confidence, right.confidence),
        evidence_summary=evidence_summary,
        phases=phases,
    )


def _merged_event_type(left: EventCandidate, right: EventCandidate) -> str:
    if left.event_type == "goal" or right.event_type == "goal":
        return "goal"
    return left.event_type


def _normalize_phases(event_type: str, phases: tuple[EventPhase, ...]) -> tuple[EventPhase, ...]:
    normalized: list[EventPhase] = []
    for phase in phases:
        phase_type = phase.phase_type
        if event_type == "goal" and phase.phase_type == "celebration_or_replay":
            phase_type = "replay"
        if event_type == "goal" and phase.phase_type == "goal":
            phase_type = "live_goal"
        normalized.append(
            EventPhase(
                phase_type=phase_type,
                start_sec=phase.start_sec,
                end_sec=phase.end_sec,
                evidence_frames=phase.evidence_frames,
                evidence_summary=phase.evidence_summary,
            )
        )
    return tuple(normalized)


def _renumber_event(event: EventCandidate, number: int) -> EventCandidate:
    return EventCandidate(
        event_id=f"E{number:03d}",
        event_type=event.event_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=event.confidence,
        evidence_summary=event.evidence_summary,
        phases=event.phases,
    )


def _unique_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def scan_result_to_dict(result: ScanResult) -> dict[str, Any]:
    return {
        "video_id": result.manifest.video_id,
        "source_video": result.manifest.source_video,
        "events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "start_sec": event.start_sec,
                "end_sec": event.end_sec,
                "evidence_frames": list(event.evidence_frames),
                "confidence": event.confidence,
                "evidence_summary": event.evidence_summary,
                "phases": [
                    {
                        "phase_type": phase.phase_type,
                        "start_sec": phase.start_sec,
                        "end_sec": phase.end_sec,
                        "evidence_frames": list(phase.evidence_frames),
                        "evidence_summary": phase.evidence_summary,
                    }
                    for phase in event.phases
                ],
            }
            for event in result.events
        ],
        "observations": [
            {
                "frame_id": observation.frame_id,
                "timestamp_sec": observation.timestamp_sec,
                "needs_commentary": observation.needs_commentary,
                "event_type": observation.event_type,
                "confidence": observation.confidence,
                "evidence": observation.evidence,
                "source_window": observation.source_window,
            }
            for observation in result.observations
        ],
        "window_errors": list(result.window_errors),
    }


def dump_scan_result(result: ScanResult, path: str | Path) -> None:
    Path(path).write_text(to_pretty_json(scan_result_to_dict(result)), encoding="utf-8")
