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


GOAL_VERIFICATION_VERSION = 4

ALLOWED_VERDICTS = {"confirmed_goal", "not_goal", "uncertain"}
ALLOWED_TIMELINE_CLASSIFICATIONS = {
    "actual_goal",
    "duplicate_replay",
    "celebration_only",
    "scoreboard_graphic",
    "shot_or_save",
    "uncertain",
}
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
    timeline_max_frames_per_goal: int = 4
    context_frames_each_side: int = 1
    temperature: float = 0.1
    top_p: float = 0.8
    max_tokens: int = 1400
    thinking_mode: bool = False
    downgrade_not_goal: bool = True
    downgrade_uncertain: bool = False
    merge_duplicate_goals: bool = True
    downgrade_weak_goal_without_followup: bool = True
    min_actual_goal_confidence_without_followup: float = 0.82


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


def consolidate_goal_timeline(
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
    input_event_ids = tuple(event.event_id for event in events)
    goal_events = [event for event in events if event.event_type == "goal"]
    trace.record(
        "consolidate_goal_timeline",
        "start",
        {
            "video_id": manifest.video_id,
            "event_count": len(events),
            "goal_candidate_count": len(goal_events),
            "goal_verification_version": GOAL_VERIFICATION_VERSION,
        },
    )
    if not goal_events:
        trace.record("consolidate_goal_timeline", "finish", {"actual_goals": 0, "records": 0})
        return GoalVerificationResult(events=tuple(events), records=(), config=verify_config, input_event_ids=input_event_ids)

    selected_frames = {
        event.event_id: _select_timeline_frames(event, manifest.frames, verify_config)
        for event in goal_events
    }
    trace.record(
        "consolidate_goal_timeline",
        "prepare_model_call",
        {
            "goal_candidate_count": len(goal_events),
            "selected_frame_ids": {
                event_id: [frame.frame_id for frame in frames]
                for event_id, frames in selected_frames.items()
            },
        },
    )
    messages = _build_goal_timeline_messages(goal_events, manifest, style, selected_frames, verify_config)
    if should_record_model_io(trace):
        trace.record(
            "consolidate_goal_timeline",
            "model_call_input",
            {
                "prompt": clip_text(str(messages[0]["content"][0].get("text", "")), tracker_text_limit(trace)),
                "frames": {
                    event_id: [
                        {
                            "frame_id": frame.frame_id,
                            "timestamp_sec": frame.timestamp_sec,
                            "timestamp": format_timestamp(frame.timestamp_sec),
                            "path": str(frame.path),
                        }
                        for frame in frames
                    ]
                    for event_id, frames in selected_frames.items()
                },
                "image_payload_policy": "Image inputs are sent as data URIs to the API, but trace records local paths instead of base64 payloads.",
            },
        )
    data = active_client.chat(
        messages,
        temperature=verify_config.temperature,
        top_p=verify_config.top_p,
        max_tokens=verify_config.max_tokens,
        thinking_mode=verify_config.thinking_mode,
    )
    text = data["choices"][0]["message"].get("content") or ""
    if should_record_model_io(trace):
        trace.record(
            "consolidate_goal_timeline",
            "model_call_output",
            {"content": clip_text(text, tracker_text_limit(trace))},
        )

    payload = _parse_goal_timeline_response(text, goal_events, verify_config)
    refined, records = _apply_goal_timeline_consolidation(events, payload, verify_config)
    actual_goals = sum(1 for event in refined if event.event_type == "goal")
    trace.record(
        "consolidate_goal_timeline",
        "parsed_model_response",
        {"records": len(records), "actual_goals": actual_goals},
    )
    trace.record("consolidate_goal_timeline", "finish", {"actual_goals": actual_goals, "records": len(records)})
    return GoalVerificationResult(
        events=tuple(refined),
        records=tuple(records),
        config=verify_config,
        input_event_ids=input_event_ids,
    )


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


def _build_goal_timeline_messages(
    goal_events: list[EventCandidate],
    manifest: FramesManifest,
    style: StyleProfile,
    frames_by_event: dict[str, tuple[FrameInfo, ...]],
    config: GoalVerificationConfig,
) -> list[dict[str, Any]]:
    candidates = []
    for index, event in enumerate(goal_events):
        selected_frames = frames_by_event.get(event.event_id, ())
        candidates.append(
            {
                "candidate_index": index,
                "event_id": event.event_id,
                "time_range": {
                    "start_sec": event.start_sec,
                    "end_sec": event.end_sec,
                    "start_label": format_timestamp(event.start_sec),
                    "end_label": format_timestamp(event.end_sec),
                },
                "confidence": event.confidence,
                "evidence_frames": list(event.evidence_frames),
                "evidence_summary": event.evidence_summary,
                "support_signals": _goal_support_signals(event),
                "phases": [
                    {
                        "phase_index": phase_index,
                        "phase_type": phase.phase_type,
                        "start_sec": phase.start_sec,
                        "end_sec": phase.end_sec,
                        "start_label": format_timestamp(phase.start_sec),
                        "end_label": format_timestamp(phase.end_sec),
                        "evidence_frames": list(phase.evidence_frames),
                        "evidence_summary": phase.evidence_summary,
                    }
                    for phase_index, phase in enumerate(event.phases)
                ],
                "selected_frames": [
                    {
                        "frame_id": frame.frame_id,
                        "timestamp_sec": frame.timestamp_sec,
                        "timestamp": format_timestamp(frame.timestamp_sec),
                    }
                    for frame in selected_frames
                ],
            }
        )

    prompt = f"""
You are consolidating a football match timeline before commentary generation.

The coarse scanner produced multiple event_type=goal candidates, but that label is only a candidate label. It can include live goals, shots, saves, replays, celebrations, and scoreboard graphics.

Your task:
- Classify every candidate independently but with full timeline awareness.
- Use actual_goal only for the candidate that contains the first live scoring action of one real scored goal.
- Use duplicate_replay for replay angles, ball-already-in-net shots, repeated finish views, or later goal packages of the same real goal.
- Use celebration_only for players/crowd/bench celebrating without the live scoring action.
- Use scoreboard_graphic for score bugs, score updates, or broadcast graphics without the live scoring action.
- Use shot_or_save when the candidate is really a shot, save, block, or near miss instead of a scored goal.
- Use uncertain only when evidence is genuinely ambiguous.
- If a duplicate/replay/celebration/scoreboard candidate belongs to a real goal, set merge_into_event_id to the actual_goal event_id.
- Do not use any known or assumed total goal count. Do not force the timeline to contain a fixed number of goals.
- Do not count the same scoring sequence twice. Prefer the earliest candidate with live scoring evidence as actual_goal, and mark later replay/celebration material as duplicate context.
- Follow-up support means a later replay, celebration, scoreboard confirmation, or VAR/decision context that supports the live scoring moment. Lack of follow-up support is not proof by itself, but it should lower confidence.
- If a candidate has neither clear live scoring evidence nor follow-up support, do not keep it as actual_goal; classify it as shot_or_save or uncertain.
- If visual evidence directly contradicts a goal, such as a save, miss, keeper catch, block, or ball never crossing the line, downgrade it even if the original event_type is goal.
- Do not invent teams, players, scores, or facts.

Corrected event type rules:
- actual_goal -> corrected_event_type must be goal.
- duplicate_replay, celebration_only, scoreboard_graphic -> usually celebration_or_replay.
- shot_or_save -> choose shot, save, dangerous_attack, penalty, free_kick, or other_relevant based on evidence.
- uncertain -> choose other_relevant unless the evidence strongly suggests a more specific non-goal type.

Style context, only for salience, not for wording:
{style.prompt_injection}

Goal candidates:
{to_pretty_json({"video_id": manifest.video_id, "source_video": manifest.source_video, "candidates": candidates})}

Return JSON only:
{{
  "actual_goal_event_ids": ["U001"],
  "candidate_labels": [
    {{
      "event_id": "U001",
      "classification": "actual_goal",
      "corrected_event_type": "goal",
      "confidence": 0.0,
      "merge_into_event_id": "",
      "rationale": "short visual/timeline reason",
      "phase_labels": [
        {{"phase_index": 0, "phase_type": "live_goal", "reason": "short reason"}}
      ],
      "warnings": []
    }}
  ],
  "warnings": []
}}
""".strip()
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for event in goal_events:
        content.append(
            {
                "type": "text",
                "text": f"Candidate {event.event_id} ({format_timestamp(event.start_sec)}-{format_timestamp(event.end_sec)}) selected frames:",
            }
        )
        for frame in frames_by_event.get(event.event_id, ()):
            content.append({"type": "text", "text": f"[event_id={event.event_id}, frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]"})
            content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame.path))}})
    return [{"role": "user", "content": content}]


def _parse_goal_timeline_response(
    text: str,
    goal_events: list[EventCandidate],
    config: GoalVerificationConfig,
) -> dict[str, Any]:
    payload = extract_json_object(text)
    goal_by_id = {event.event_id: event for event in goal_events}
    goal_ids = set(goal_by_id)
    raw_labels = payload.get("candidate_labels", [])
    if not isinstance(raw_labels, list):
        raw_labels = []

    raw_actual_ids = payload.get("actual_goal_event_ids", [])
    actual_ids = {
        str(event_id).strip()
        for event_id in raw_actual_ids
        if str(event_id).strip() in goal_ids
    } if isinstance(raw_actual_ids, list) else set()

    labels: dict[str, dict[str, Any]] = {}
    for raw in raw_labels:
        if not isinstance(raw, dict):
            continue
        event_id = str(raw.get("event_id", "")).strip()
        if event_id not in goal_ids:
            continue
        classification = str(raw.get("classification", "")).strip()
        if classification not in ALLOWED_TIMELINE_CLASSIFICATIONS:
            classification = "actual_goal" if event_id in actual_ids else "uncertain"

        corrected_event_type = str(raw.get("corrected_event_type", "")).strip()
        if classification == "actual_goal":
            corrected_event_type = "goal"
        elif corrected_event_type not in ALLOWED_CORRECTED_TYPES or corrected_event_type == "goal":
            corrected_event_type = _default_corrected_type_for_classification(classification)

        merge_into_event_id = str(raw.get("merge_into_event_id", "")).strip()
        if merge_into_event_id not in goal_ids or merge_into_event_id == event_id:
            merge_into_event_id = ""

        phase_labels = raw.get("phase_labels", [])
        if not isinstance(phase_labels, list):
            phase_labels = []
        warnings = raw.get("warnings", [])
        if not isinstance(warnings, list):
            warnings = []
        labels[event_id] = {
            "event_id": event_id,
            "classification": classification,
            "corrected_event_type": corrected_event_type,
            "confidence": _clamp_float(raw.get("confidence", 0.0)),
            "merge_into_event_id": merge_into_event_id,
            "rationale": str(raw.get("rationale", "")).strip(),
            "phase_labels": phase_labels,
            "warnings": [str(item) for item in warnings if isinstance(item, str)],
        }

    for event_id in actual_ids:
        labels.setdefault(
            event_id,
            {
                "event_id": event_id,
                "classification": "actual_goal",
                "corrected_event_type": "goal",
                "confidence": 0.0,
                "merge_into_event_id": "",
                "rationale": "Listed in actual_goal_event_ids.",
                "phase_labels": [],
                "warnings": [],
            },
        )

    for event in goal_events:
        labels.setdefault(
            event.event_id,
            {
                "event_id": event.event_id,
                "classification": "uncertain",
                "corrected_event_type": "other_relevant",
                "confidence": 0.0,
                "merge_into_event_id": "",
                "rationale": "Missing model label for this goal candidate.",
                "phase_labels": [],
                "warnings": ["missing model label"],
            },
        )

    labels = _apply_weak_goal_without_followup_policy(labels, goal_by_id, config)

    valid_actual_ids = {
        event_id
        for event_id, row in labels.items()
        if row["classification"] == "actual_goal"
    }
    for row in labels.values():
        if row["classification"] in {"duplicate_replay", "celebration_only", "scoreboard_graphic"}:
            merge_id = str(row.get("merge_into_event_id", ""))
            if merge_id not in valid_actual_ids:
                row["merge_into_event_id"] = _nearest_actual_goal_id(goal_by_id[row["event_id"]], goal_by_id, valid_actual_ids)

    warnings = payload.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    return {
        "actual_goal_event_ids": sorted(valid_actual_ids, key=lambda event_id: goal_by_id[event_id].start_sec),
        "candidate_labels": list(labels.values()),
        "warnings": [str(item) for item in warnings if isinstance(item, str)],
    }


def _apply_weak_goal_without_followup_policy(
    labels: dict[str, dict[str, Any]],
    goal_by_id: dict[str, EventCandidate],
    config: GoalVerificationConfig,
) -> dict[str, dict[str, Any]]:
    if not config.downgrade_weak_goal_without_followup:
        return labels

    followup_target_ids = {
        str(row.get("merge_into_event_id", ""))
        for row in labels.values()
        if row.get("classification") in {"duplicate_replay", "celebration_only", "scoreboard_graphic"}
        and str(row.get("merge_into_event_id", "")) in goal_by_id
    }
    updated = dict(labels)
    threshold = max(0.0, min(1.0, config.min_actual_goal_confidence_without_followup))
    for event_id, row in labels.items():
        if row.get("classification") != "actual_goal" or event_id not in goal_by_id:
            continue
        event = goal_by_id[event_id]
        support = _goal_support_signals(event)
        has_followup_support = bool(support["has_followup_support"]) or event_id in followup_target_ids
        has_strong_live_evidence = bool(support["has_strong_live_goal_evidence"]) or _row_has_strong_goal_evidence(row)
        confidence = _clamp_float(row.get("confidence", 0.0))
        if has_followup_support:
            continue

        replacement = dict(row)
        warnings = list(replacement.get("warnings", [])) if isinstance(replacement.get("warnings", []), list) else []
        if not has_strong_live_evidence or confidence < threshold:
            replacement["classification"] = "shot_or_save"
            replacement["corrected_event_type"] = "shot"
            replacement["merge_into_event_id"] = ""
            warnings.append("downgraded actual_goal because it has no follow-up support and weak live scoring evidence")
            rationale = str(replacement.get("rationale", "")).strip()
            extra = (
                "Downgraded by weak-goal follow-up policy: no replay/celebration/scoreboard/VAR support "
                "and insufficient clear live scoring evidence."
            )
            replacement["rationale"] = f"{rationale} {extra}".strip()
        else:
            warnings.append("actual_goal_without_followup_support")
        replacement["warnings"] = list(dict.fromkeys(str(item) for item in warnings if str(item)))
        updated[event_id] = replacement
    return updated


def _apply_goal_timeline_consolidation(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    payload: dict[str, Any],
    config: GoalVerificationConfig,
) -> tuple[list[EventCandidate], list[GoalVerificationRecord]]:
    labels = {
        str(row.get("event_id", "")): row
        for row in payload.get("candidate_labels", [])
        if isinstance(row, dict)
    }
    actual_ids = {
        str(row.get("event_id", ""))
        for row in labels.values()
        if row.get("classification") == "actual_goal"
    }
    refined_by_id: dict[str, EventCandidate] = {}
    merge_sources: dict[str, list[tuple[EventCandidate, dict[str, Any]]]] = {}
    records: list[GoalVerificationRecord] = []

    for event in events:
        if event.event_type != "goal":
            refined_by_id[event.event_id] = event
            continue

        row = labels.get(event.event_id) or {
            "classification": "uncertain",
            "corrected_event_type": "other_relevant",
            "confidence": 0.0,
            "merge_into_event_id": "",
            "rationale": "Missing timeline label.",
            "phase_labels": [],
            "warnings": ["missing timeline label"],
        }
        classification = str(row.get("classification", "uncertain"))
        corrected_type = str(row.get("corrected_event_type", _default_corrected_type_for_classification(classification)))
        merge_into_event_id = str(row.get("merge_into_event_id", ""))
        should_merge = (
            config.merge_duplicate_goals
            and classification in {"duplicate_replay", "celebration_only", "scoreboard_graphic"}
            and merge_into_event_id in actual_ids
        )

        if should_merge:
            merge_sources.setdefault(merge_into_event_id, []).append((event, row))
            refined_event_type = "merged_into_goal"
        else:
            refined_event = _event_with_timeline_label(event, row)
            refined_by_id[event.event_id] = refined_event
            refined_event_type = refined_event.event_type

        records.append(
            GoalVerificationRecord(
                event_id=event.event_id,
                original_event_type=event.event_type,
                refined_event_type=refined_event_type,
                verdict=classification,
                confidence=_clamp_float(row.get("confidence", 0.0)),
                rationale=str(row.get("rationale", "")),
                corrected_event_type=corrected_type,
                warnings=tuple(str(item) for item in row.get("warnings", []) if isinstance(item, str)),
            )
        )

    for target_id, sources in merge_sources.items():
        if target_id not in refined_by_id:
            for source_event, row in sources:
                refined_by_id[source_event.event_id] = _event_with_timeline_label(source_event, row)
            continue
        merged = refined_by_id[target_id]
        for source_event, row in sorted(sources, key=lambda item: item[0].start_sec):
            merged = _merge_duplicate_goal_candidate(merged, source_event, row)
        refined_by_id[target_id] = merged

    refined = [event for event in refined_by_id.values()]
    refined.sort(key=lambda event: (event.start_sec, event.end_sec, event.event_id))
    records.sort(key=lambda record: record.event_id)
    return refined, records


def _event_with_timeline_label(event: EventCandidate, row: dict[str, Any]) -> EventCandidate:
    classification = str(row.get("classification", "uncertain"))
    corrected_type = str(row.get("corrected_event_type", _default_corrected_type_for_classification(classification)))
    if classification == "actual_goal":
        refined_type = "goal"
    elif classification == "uncertain" and not corrected_type:
        refined_type = "other_relevant"
    else:
        refined_type = corrected_type if corrected_type in ALLOWED_CORRECTED_TYPES else _default_corrected_type_for_classification(classification)

    phase_map = _phase_label_map(row.get("phase_labels", []))
    phases: list[EventPhase] = []
    source_phases = event.phases or (
        EventPhase(event.event_type, event.start_sec, event.end_sec, event.evidence_frames, event.evidence_summary),
    )
    for index, phase in enumerate(source_phases):
        phase_type = phase_map.get(index, phase.phase_type)
        if refined_type != "goal":
            phase_type = _non_goal_phase_type(refined_type, phase_type)
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

    note = _timeline_note(row)
    return EventCandidate(
        event_id=event.event_id,
        event_type=refined_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=max(event.confidence, _clamp_float(row.get("confidence", 0.0))),
        evidence_summary="; ".join(part for part in [event.evidence_summary, note] if part),
        phases=tuple(phases),
    )


def _merge_duplicate_goal_candidate(
    target: EventCandidate,
    duplicate: EventCandidate,
    row: dict[str, Any],
) -> EventCandidate:
    classification = str(row.get("classification", "duplicate_replay"))
    duplicate_phase_type = _goal_phase_type_for_timeline_classification(classification)
    duplicate_phases: list[EventPhase] = []
    source_phases = duplicate.phases or (
        EventPhase(duplicate.event_type, duplicate.start_sec, duplicate.end_sec, duplicate.evidence_frames, duplicate.evidence_summary),
    )
    for phase in source_phases:
        duplicate_phases.append(
            EventPhase(
                phase_type=duplicate_phase_type,
                start_sec=phase.start_sec,
                end_sec=phase.end_sec,
                evidence_frames=phase.evidence_frames,
                evidence_summary=phase.evidence_summary,
            )
        )

    merge_note = (
        f"Merged {duplicate.event_id} into {target.event_id}: "
        f"{_timeline_note(row)}"
    )
    return EventCandidate(
        event_id=target.event_id,
        event_type="goal",
        start_sec=min(target.start_sec, duplicate.start_sec),
        end_sec=max(target.end_sec, duplicate.end_sec),
        evidence_frames=_unique_strings(target.evidence_frames + duplicate.evidence_frames),
        confidence=max(target.confidence, duplicate.confidence, _clamp_float(row.get("confidence", 0.0))),
        evidence_summary="; ".join(part for part in [target.evidence_summary, duplicate.evidence_summary, merge_note] if part),
        phases=tuple(_keep_single_live_goal(list(target.phases) + duplicate_phases)),
    )


def _nearest_actual_goal_id(
    event: EventCandidate,
    goal_by_id: dict[str, EventCandidate],
    actual_ids: set[str],
) -> str:
    if not actual_ids:
        return ""
    previous = [
        goal_by_id[event_id]
        for event_id in actual_ids
        if goal_by_id[event_id].end_sec <= event.start_sec
    ]
    if previous:
        return max(previous, key=lambda item: item.end_sec).event_id
    nearest = min(
        (goal_by_id[event_id] for event_id in actual_ids),
        key=lambda item: abs(item.start_sec - event.start_sec),
    )
    return nearest.event_id


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


def _select_timeline_frames(
    event: EventCandidate,
    manifest_frames: tuple[FrameInfo, ...],
    config: GoalVerificationConfig,
) -> tuple[FrameInfo, ...]:
    timeline_config = GoalVerificationConfig(
        sample_fps=config.sample_fps,
        max_frames_per_goal=max(1, config.timeline_max_frames_per_goal),
        max_frames_per_phase=max(1, min(config.max_frames_per_phase, config.timeline_max_frames_per_goal)),
        timeline_max_frames_per_goal=config.timeline_max_frames_per_goal,
        context_frames_each_side=config.context_frames_each_side,
        temperature=config.temperature,
        top_p=config.top_p,
        max_tokens=config.max_tokens,
        thinking_mode=config.thinking_mode,
        downgrade_not_goal=config.downgrade_not_goal,
        downgrade_uncertain=config.downgrade_uncertain,
        merge_duplicate_goals=config.merge_duplicate_goals,
        downgrade_weak_goal_without_followup=config.downgrade_weak_goal_without_followup,
        min_actual_goal_confidence_without_followup=config.min_actual_goal_confidence_without_followup,
    )
    return _select_verification_frames(event, manifest_frames, timeline_config)


def _phase_label_map(raw_labels: Any) -> dict[int, str]:
    phase_map: dict[int, str] = {}
    if not isinstance(raw_labels, list):
        return phase_map
    for row in raw_labels:
        if not isinstance(row, dict):
            continue
        try:
            index = int(row.get("phase_index"))
        except Exception:
            continue
        phase_type = str(row.get("phase_type", "")).strip()
        if phase_type in GOAL_PHASE_TYPES:
            phase_map[index] = phase_type
    return phase_map


def _non_goal_phase_type(refined_type: str, phase_type: str) -> str:
    if phase_type in {"replay", "celebration", "var_review"}:
        return "celebration_or_replay" if refined_type not in {"var_review"} else "var_review"
    if phase_type in {"live_goal", "goal", "buildup"}:
        return refined_type
    return phase_type if phase_type in ALLOWED_CORRECTED_TYPES else refined_type


def _goal_phase_type_for_timeline_classification(classification: str) -> str:
    if classification == "celebration_only":
        return "celebration"
    if classification == "scoreboard_graphic":
        return "replay"
    return "replay"


def _default_corrected_type_for_classification(classification: str) -> str:
    if classification == "actual_goal":
        return "goal"
    if classification in {"duplicate_replay", "celebration_only", "scoreboard_graphic"}:
        return "celebration_or_replay"
    if classification == "shot_or_save":
        return "shot"
    return "other_relevant"


def _timeline_note(row: dict[str, Any]) -> str:
    merge_text = f", merge_into={row.get('merge_into_event_id')}" if row.get("merge_into_event_id") else ""
    return (
        f"Goal timeline classification={row.get('classification')}, "
        f"corrected_event_type={row.get('corrected_event_type')}, "
        f"confidence={_clamp_float(row.get('confidence', 0.0)):.2f}{merge_text}, "
        f"rationale={row.get('rationale', '')}"
    )


def _unique_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


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
        "timeline_max_frames_per_goal": config.timeline_max_frames_per_goal,
        "context_frames_each_side": config.context_frames_each_side,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "max_tokens": config.max_tokens,
        "thinking_mode": config.thinking_mode,
        "downgrade_not_goal": config.downgrade_not_goal,
        "downgrade_uncertain": config.downgrade_uncertain,
        "merge_duplicate_goals": config.merge_duplicate_goals,
        "downgrade_weak_goal_without_followup": config.downgrade_weak_goal_without_followup,
        "min_actual_goal_confidence_without_followup": config.min_actual_goal_confidence_without_followup,
    }


def _clamp_float(value: Any) -> float:
    try:
        number = float(value)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, number))
