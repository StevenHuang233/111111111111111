from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient, image_source_to_url

from .json_utils import extract_json_object, to_pretty_json
from .manifest import FrameInfo, FramesManifest
from .scanner import EventCandidate, EventPhase
from .styles import StyleProfile
from .time_utils import format_timestamp
from .tracing import NullTracker, StepTracker, clip_text, should_record_model_io, tracker_text_limit


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...


GOAL_VERIFICATION_VERSION = 6

ALLOWED_VERDICTS = {"confirmed_goal", "not_goal", "uncertain"}
ALLOWED_CORRECTED_TYPES = {
    "goal",
    "shot",
    "save",
    "dangerous_attack",
    "corner",
    "free_kick",
    "penalty",
    "foul",
    "card",
    "substitution",
    "var_review",
    "celebration_or_replay",
    "period_transition",
    "other_relevant",
}
GOAL_PHASE_TYPES = {"buildup", "live_goal", "replay", "celebration", "var_review"}
GOAL_FOLLOWUP_PHASE_TYPES = {"replay", "celebration", "var_review"}
GOAL_FOLLOWUP_MARKERS = (
    "replay",
    "slow motion",
    "slow-motion",
    "celebrat",
    "scoreboard",
    "score bug",
    "score graphic",
    "graphic",
    "var",
    "decision",
    "crowd cheering",
    "players embracing",
    "arms raised",
    "reaction",
)
STRONG_LIVE_GOAL_MARKERS = (
    "ball in net",
    "ball inside the net",
    "inside the net",
    "behind the net",
    "crossing the goal line",
    "crosses the goal line",
    "crossed the goal line",
    "over the line",
    "net rippling",
    "net ripples",
    "finish into the net",
    "goalkeeper beaten",
)


@dataclass(frozen=True)
class GoalVerificationConfig:
    sample_fps: float | None = 0.5
    max_frames_per_goal: int = 18
    max_frames_per_phase: int = 4
    context_frames_each_side: int = 1
    temperature: float = 0.1
    top_p: float = 0.8
    max_tokens: int = 1400
    thinking_mode: bool = False
    downgrade_not_goal: bool = True
    downgrade_uncertain: bool = False
    downgrade_weak_goal_without_followup: bool = True
    min_confirmed_goal_confidence_without_followup: float = 0.82


@dataclass(frozen=True)
class GoalVerificationRecord:
    event_id: str
    original_event_type: str
    refined_event_type: str
    verdict: str
    confidence: float
    rationale: str
    corrected_event_type: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class GoalVerificationResult:
    events: tuple[EventCandidate, ...]
    records: tuple[GoalVerificationRecord, ...]
    config: GoalVerificationConfig
    input_event_ids: tuple[str, ...] = ()


def verify_goal_events(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    config: GoalVerificationConfig | None = None,
) -> GoalVerificationResult:
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    verify_config = config or GoalVerificationConfig()
    trace.record(
        "verify_goal_events",
        "start",
        {
            "video_id": manifest.video_id,
            "event_count": len(events),
            "goal_count": sum(1 for event in events if event.event_type == "goal"),
            "goal_verification_version": GOAL_VERIFICATION_VERSION,
        },
    )

    refined: list[EventCandidate] = []
    records: list[GoalVerificationRecord] = []
    for event in events:
        if event.event_type != "goal":
            refined.append(event)
            continue
        result_event, record = verify_goal_event(event, manifest, style, active_client, trace, verify_config)
        refined.append(result_event)
        records.append(record)

    trace.record("verify_goal_events", "finish", {"verified_goals": len(records)})
    return GoalVerificationResult(
        events=tuple(refined),
        records=tuple(records),
        config=verify_config,
        input_event_ids=tuple(event.event_id for event in events),
    )


def verify_goal_event(
    event: EventCandidate,
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient,
    tracker: StepTracker | None = None,
    config: GoalVerificationConfig | None = None,
) -> tuple[EventCandidate, GoalVerificationRecord]:
    trace = tracker or NullTracker()
    verify_config = config or GoalVerificationConfig()
    selected_frames = _select_verification_frames(event, manifest.frames, verify_config)
    trace.record(
        "verify_goal_event",
        "prepare_model_call",
        {
            "event_id": event.event_id,
            "time_range": [event.start_sec, event.end_sec],
            "phase_types": [phase.phase_type for phase in event.phases],
            "selected_frame_ids": [frame.frame_id for frame in selected_frames],
        },
    )
    messages = _build_goal_verification_messages(event, manifest, style, selected_frames)
    if should_record_model_io(trace):
        trace.record(
            "verify_goal_event",
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
    data = client.chat(
        messages,
        temperature=verify_config.temperature,
        top_p=verify_config.top_p,
        max_tokens=verify_config.max_tokens,
        thinking_mode=verify_config.thinking_mode,
    )
    text = data["choices"][0]["message"].get("content") or ""
    if should_record_model_io(trace):
        trace.record(
            "verify_goal_event",
            "model_call_output",
            {"event_id": event.event_id, "content": clip_text(text, tracker_text_limit(trace))},
        )
    payload = _parse_goal_verification_response(text)
    payload = _apply_single_goal_followup_policy(event, payload, verify_config)
    refined = _apply_goal_verification(event, payload, verify_config)
    record = GoalVerificationRecord(
        event_id=event.event_id,
        original_event_type=event.event_type,
        refined_event_type=refined.event_type,
        verdict=str(payload["verdict"]),
        confidence=float(payload["confidence"]),
        rationale=str(payload.get("rationale", "")),
        corrected_event_type=str(payload.get("corrected_event_type", refined.event_type)),
        warnings=tuple(str(item) for item in payload.get("warnings", []) if isinstance(item, str)),
    )
    trace.record(
        "verify_goal_event",
        "parsed_model_response",
        {
            "event_id": event.event_id,
            "verdict": record.verdict,
            "refined_event_type": record.refined_event_type,
            "confidence": record.confidence,
        },
    )
    return refined, record


def goal_verification_result_to_dict(
    result: GoalVerificationResult,
    manifest: FramesManifest | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "goal_verification_version": GOAL_VERIFICATION_VERSION,
        "config": _config_to_dict(result.config),
        "input_event_ids": list(result.input_event_ids),
        "events": [_event_to_dict(event) for event in result.events],
        "records": [
            {
                "event_id": record.event_id,
                "original_event_type": record.original_event_type,
                "refined_event_type": record.refined_event_type,
                "verdict": record.verdict,
                "confidence": record.confidence,
                "rationale": record.rationale,
                "corrected_event_type": record.corrected_event_type,
                "warnings": list(record.warnings),
            }
            for record in result.records
        ],
    }
    if manifest is not None:
        payload["video_id"] = manifest.video_id
        payload["source_video"] = manifest.source_video
    return payload


def dump_goal_verification_result(
    result: GoalVerificationResult,
    manifest: FramesManifest | None,
    path: str | Path,
) -> None:
    Path(path).write_text(to_pretty_json(goal_verification_result_to_dict(result, manifest)), encoding="utf-8")


def _build_goal_verification_messages(
    event: EventCandidate,
    manifest: FramesManifest,
    style: StyleProfile,
    frames: tuple[FrameInfo, ...],
) -> list[dict[str, Any]]:
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
        "evidence_summary": event.evidence_summary,
        "phases": [
            {
                "phase_index": index,
                "phase_type": phase.phase_type,
                "start_sec": phase.start_sec,
                "end_sec": phase.end_sec,
                "start_label": format_timestamp(phase.start_sec),
                "end_label": format_timestamp(phase.end_sec),
                "evidence_frames": list(phase.evidence_frames),
                "evidence_summary": phase.evidence_summary,
            }
            for index, phase in enumerate(event.phases)
        ],
    }
    frame_listing = "\n".join(
        f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]" for frame in frames
    )
    prompt = f"""
You are verifying a football goal sequence package before commentary generation.

The coarse scanner already grouped this as event_type=goal, but it can confuse live goals, saves, replays, celebrations, and scoreboard shots.
Your task is to correct the event label and phase labels using the structured evidence and selected visual frames.

Decision rules:
- Use confirmed_goal only when the sequence contains clear live or immediate scoring evidence: ball crossing the line, ball in net immediately after the finish, net rippling from the shot, or the live scoring action plus unmistakable immediate reaction.
- Do not use confirmed_goal for scoreboard graphics alone, celebration-only shots, ball-already-in-net shots, or replays of an earlier goal unless the same candidate also contains the live scoring action.
- Use not_goal when the best evidence says it is a save, blocked shot, ordinary shot, near miss, restart, duplicate replay, scoreboard-only moment, or celebration-only moment without proof of the live scoring action.
- Use uncertain only when visual evidence is genuinely ambiguous.
- If the event is not a goal, choose corrected_event_type from: shot, save, dangerous_attack, free_kick, penalty, var_review, celebration_or_replay, other_relevant.
- If confirmed_goal, keep corrected_event_type as goal.
- Relabel each existing phase by phase_index. Use only: buildup, live_goal, replay, celebration, var_review.
- Mark at most one compact segment as live_goal: the first moment where the actual scoring action is visible. Later ball-in-net or scoreboard shots should be replay unless they are the first live scoring moment.
- Do not invent names, teams, scores, or facts.

Style context, only for salience, not for wording:
{style.prompt_injection}

Selected frame prefixes:
{frame_listing}

Goal package data:
{to_pretty_json(event_json)}

Return JSON only:
{{
  "verdict": "confirmed_goal",
  "confidence": 0.0,
  "corrected_event_type": "goal",
  "rationale": "short reason grounded in visual evidence",
  "phase_labels": [
    {{"phase_index": 0, "phase_type": "buildup", "reason": "short reason"}}
  ],
  "warnings": []
}}
""".strip()
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for frame in frames:
        content.append({"type": "text", "text": f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]"})
        content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame.path))}})
    return [{"role": "user", "content": content}]


def _goal_support_signals(event: EventCandidate) -> dict[str, Any]:
    phases = event.phases or (
        EventPhase(event.event_type, event.start_sec, event.end_sec, event.evidence_frames, event.evidence_summary),
    )
    phase_types = [phase.phase_type for phase in phases]
    summaries = [event.evidence_summary, *(phase.evidence_summary for phase in phases)]
    has_followup_phase = any(phase.phase_type in GOAL_FOLLOWUP_PHASE_TYPES for phase in phases)
    has_followup_marker = any(_contains_marker(text, GOAL_FOLLOWUP_MARKERS) for text in summaries)
    has_strong_live_goal_evidence = any(_contains_marker(text, STRONG_LIVE_GOAL_MARKERS) for text in summaries)
    return {
        "has_followup_support": bool(has_followup_phase or has_followup_marker),
        "has_followup_phase": bool(has_followup_phase),
        "has_followup_marker": bool(has_followup_marker),
        "has_live_goal_phase": any(phase_type == "live_goal" for phase_type in phase_types),
        "has_strong_live_goal_evidence": bool(has_strong_live_goal_evidence),
        "phase_types": phase_types,
    }


def _row_has_strong_goal_evidence(row: dict[str, Any]) -> bool:
    texts = [
        str(row.get("rationale", "")),
        " ".join(str(item) for item in row.get("warnings", []) if isinstance(item, str)),
    ]
    return any(_contains_marker(text, STRONG_LIVE_GOAL_MARKERS) for text in texts)


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _parse_goal_verification_response(text: str) -> dict[str, Any]:
    payload = extract_json_object(text)
    verdict = str(payload.get("verdict", "uncertain")).strip()
    if verdict not in ALLOWED_VERDICTS:
        verdict = "uncertain"
    corrected_event_type = str(payload.get("corrected_event_type", "goal")).strip()
    if corrected_event_type not in ALLOWED_CORRECTED_TYPES:
        corrected_event_type = "goal" if verdict == "confirmed_goal" else "other_relevant"
    confidence = _clamp_float(payload.get("confidence", 0.0))
    phase_labels = payload.get("phase_labels", [])
    if not isinstance(phase_labels, list):
        phase_labels = []
    warnings = payload.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    return {
        "verdict": verdict,
        "confidence": confidence,
        "corrected_event_type": corrected_event_type,
        "rationale": str(payload.get("rationale", "")).strip(),
        "phase_labels": phase_labels,
        "warnings": warnings,
    }


def _apply_single_goal_followup_policy(
    event: EventCandidate,
    payload: dict[str, Any],
    config: GoalVerificationConfig,
) -> dict[str, Any]:
    if not config.downgrade_weak_goal_without_followup or payload.get("verdict") != "confirmed_goal":
        return payload

    support = _goal_support_signals(event)
    has_followup_support = bool(support["has_followup_support"])
    has_strong_live_evidence = bool(support["has_strong_live_goal_evidence"]) or _row_has_strong_goal_evidence(payload)
    confidence = _clamp_float(payload.get("confidence", 0.0))
    threshold = max(0.0, min(1.0, config.min_confirmed_goal_confidence_without_followup))
    if has_followup_support:
        return payload

    updated = dict(payload)
    warnings = list(updated.get("warnings", [])) if isinstance(updated.get("warnings", []), list) else []
    if not has_strong_live_evidence or confidence < threshold:
        updated["verdict"] = "not_goal"
        updated["corrected_event_type"] = "shot"
        warnings.append("downgraded confirmed_goal because the goal package has no follow-up support and weak live scoring evidence")
        rationale = str(updated.get("rationale", "")).strip()
        extra = (
            "Downgraded by single-goal follow-up policy: no replay/celebration/scoreboard/VAR support "
            "and insufficient clear live scoring evidence."
        )
        updated["rationale"] = f"{rationale} {extra}".strip()
    else:
        warnings.append("confirmed_goal_without_followup_support")
    updated["warnings"] = list(dict.fromkeys(str(item) for item in warnings if str(item)))
    return updated


def _apply_goal_verification(
    event: EventCandidate,
    payload: dict[str, Any],
    config: GoalVerificationConfig,
) -> EventCandidate:
    verdict = str(payload["verdict"])
    corrected_type = str(payload["corrected_event_type"])
    if verdict == "confirmed_goal":
        refined_type = "goal"
    elif verdict == "not_goal" and config.downgrade_not_goal:
        refined_type = corrected_type if corrected_type != "goal" else "other_relevant"
    elif verdict == "uncertain" and config.downgrade_uncertain:
        refined_type = corrected_type if corrected_type != "goal" else "other_relevant"
    else:
        refined_type = "goal"

    phase_map: dict[int, str] = {}
    for row in payload.get("phase_labels", []):
        if not isinstance(row, dict):
            continue
        try:
            index = int(row.get("phase_index"))
        except Exception:
            continue
        phase_type = str(row.get("phase_type", "")).strip()
        if phase_type in GOAL_PHASE_TYPES:
            phase_map[index] = phase_type

    phases: list[EventPhase] = []
    for index, phase in enumerate(event.phases):
        phase_type = phase_map.get(index, phase.phase_type)
        if refined_type != "goal" and phase_type == "live_goal":
            phase_type = refined_type
        phases.append(
            EventPhase(
                phase_type=phase_type,
                start_sec=phase.start_sec,
                end_sec=phase.end_sec,
                evidence_frames=phase.evidence_frames,
                evidence_summary=phase.evidence_summary,
            )
        )
    if refined_type == "goal":
        phases = _keep_single_live_goal(phases)

    verification_note = (
        f"Goal verification verdict={verdict}, corrected_event_type={corrected_type}, "
        f"confidence={float(payload['confidence']):.2f}, rationale={payload.get('rationale', '')}"
    )
    evidence_summary = "; ".join(part for part in [event.evidence_summary, verification_note] if part)
    return EventCandidate(
        event_id=event.event_id,
        event_type=refined_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=max(event.confidence, float(payload["confidence"])),
        evidence_summary=evidence_summary,
        phases=tuple(phases),
    )


def _keep_single_live_goal(phases: list[EventPhase]) -> list[EventPhase]:
    seen_live = False
    normalized: list[EventPhase] = []
    for phase in phases:
        phase_type = phase.phase_type
        if phase_type == "live_goal":
            if seen_live:
                phase_type = "replay"
            else:
                seen_live = True
        normalized.append(
            EventPhase(
                phase_type=phase_type,
                start_sec=phase.start_sec,
                end_sec=phase.end_sec,
                evidence_frames=phase.evidence_frames,
                evidence_summary=phase.evidence_summary,
            )
        )
    return normalized


def _select_verification_frames(
    event: EventCandidate,
    manifest_frames: tuple[FrameInfo, ...],
    config: GoalVerificationConfig,
) -> tuple[FrameInfo, ...]:
    frame_by_id = {frame.frame_id: frame for frame in manifest_frames}
    selected: list[FrameInfo] = []
    for phase in event.phases:
        phase_frames = _frames_in_time_range_with_context(
            manifest_frames,
            phase.start_sec,
            phase.end_sec,
            config.context_frames_each_side,
        )
        phase_frames = _sample_frames_by_fps(phase_frames, config.sample_fps)
        evidence_frames = tuple(frame_by_id[frame_id] for frame_id in phase.evidence_frames if frame_id in frame_by_id)
        phase_selected = _sample_frames(_unique_frames(list(evidence_frames)), min(config.max_frames_per_phase, len(evidence_frames)))
        remaining = config.max_frames_per_phase - len(phase_selected)
        if remaining > 0:
            phase_selected.extend(_sample_frames(phase_frames, remaining))
        selected.extend(phase_selected)

    selected = _unique_frames(selected)
    if len(selected) < config.max_frames_per_goal:
        event_frames = _frames_in_time_range_with_context(
            manifest_frames,
            event.start_sec,
            event.end_sec,
            config.context_frames_each_side,
        )
        event_frames = _sample_frames_by_fps(event_frames, config.sample_fps)
        selected.extend(_sample_frames(event_frames, config.max_frames_per_goal - len(selected)))

    return tuple(_unique_frames(selected)[: config.max_frames_per_goal])


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


def _sample_frames(frames: tuple[FrameInfo, ...] | list[FrameInfo], limit: int) -> list[FrameInfo]:
    frame_tuple = tuple(frames)
    if limit <= 0 or not frame_tuple:
        return []
    if len(frame_tuple) <= limit:
        return list(frame_tuple)
    if limit == 1:
        return [frame_tuple[len(frame_tuple) // 2]]
    positions = [round(index * (len(frame_tuple) - 1) / (limit - 1)) for index in range(limit)]
    return [frame_tuple[position] for position in dict.fromkeys(positions)]


def _unique_frames(frames: list[FrameInfo]) -> list[FrameInfo]:
    by_id: dict[str, FrameInfo] = {}
    for frame in frames:
        by_id.setdefault(frame.frame_id, frame)
    return sorted(by_id.values(), key=lambda frame: frame.timestamp_sec)


def _event_to_dict(event: EventCandidate) -> dict[str, Any]:
    return {
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


def _config_to_dict(config: GoalVerificationConfig) -> dict[str, Any]:
    return {
        "sample_fps": config.sample_fps,
        "max_frames_per_goal": config.max_frames_per_goal,
        "max_frames_per_phase": config.max_frames_per_phase,
        "context_frames_each_side": config.context_frames_each_side,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "max_tokens": config.max_tokens,
        "thinking_mode": config.thinking_mode,
        "downgrade_not_goal": config.downgrade_not_goal,
        "downgrade_uncertain": config.downgrade_uncertain,
        "downgrade_weak_goal_without_followup": config.downgrade_weak_goal_without_followup,
        "min_confirmed_goal_confidence_without_followup": config.min_confirmed_goal_confidence_without_followup,
    }


def _clamp_float(value: Any) -> float:
    try:
        number = float(value)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, number))
