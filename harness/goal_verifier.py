from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient, image_source_to_url

from .json_utils import extract_json_object, to_pretty_json
from .manifest import FrameInfo, FramesManifest
from .replay_markers import FIFA_REPLAY_BUMPER_EVIDENCE, detect_fifa_replay_bumper
from .scanner import EventCandidate, EventPhase
from .styles import StyleProfile
from .time_utils import format_timestamp
from .tracing import NullTracker, StepTracker, clip_text, should_record_model_io, tracker_text_limit


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...


GOAL_VERIFICATION_VERSION = 10

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
    "var_show",
    "var_review",
    "celebration_or_replay",
    "period_transition",
    "other_relevant",
}
GOAL_PHASE_TYPES = {"buildup", "live_goal", "replay", "celebration", "var_review"}
GOAL_FOLLOWUP_PHASE_TYPES = {"replay", "celebration", "var_review"}
NON_GOAL_PRIMARY_TYPES = {
    "shot",
    "save",
    "dangerous_attack",
    "corner",
    "free_kick",
    "penalty",
    "foul",
    "card",
    "substitution",
    "var_show",
    "var_review",
    "other_relevant",
}
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
    sample_fps: float | None = 2.0
    window_sec: float = 3.0
    stride_sec: float = 3.0
    max_frames_per_goal: int | None = None
    max_frames_per_phase: int | None = None
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


@dataclass(frozen=True)
class GoalVerificationWindow:
    window_index: int
    start_sec: float
    end_sec: float
    frames: tuple[FrameInfo, ...]
    fifa_replay_frame_ids: tuple[str, ...] = ()


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
        result_events, record = verify_goal_event(event, manifest, style, active_client, trace, verify_config)
        refined.extend(result_events)
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
) -> tuple[tuple[EventCandidate, ...], GoalVerificationRecord]:
    trace = tracker or NullTracker()
    verify_config = config or GoalVerificationConfig()
    windows = _build_verification_windows(event, manifest.frames, verify_config)
    trace.record(
        "verify_goal_event",
        "prepare_model_call",
        {
            "event_id": event.event_id,
            "time_range": [event.start_sec, event.end_sec],
            "phase_types": [phase.phase_type for phase in event.phases],
            "sample_fps": verify_config.sample_fps,
            "window_sec": verify_config.window_sec,
            "stride_sec": verify_config.stride_sec,
            "window_count": len(windows),
            "fifa_replay_marker_frames": list(
                dict.fromkeys(frame_id for window in windows for frame_id in window.fifa_replay_frame_ids)
            ),
        },
    )
    window_payloads: list[dict[str, Any]] = []
    for window in windows:
        messages = _build_goal_verification_window_messages(event, manifest, style, window)
        trace.record(
            "verify_goal_event.window",
            "prepare_model_call",
            {
                "event_id": event.event_id,
                "window_index": window.window_index,
                "time_range": [window.start_sec, window.end_sec],
                "selected_frame_ids": [frame.frame_id for frame in window.frames],
                "fifa_replay_marker_frames": list(window.fifa_replay_frame_ids),
            },
        )
        if should_record_model_io(trace):
            trace.record(
                "verify_goal_event.window",
                "model_call_input",
                {
                    "event_id": event.event_id,
                    "window_index": window.window_index,
                    "prompt": clip_text(str(messages[0]["content"][0].get("text", "")), tracker_text_limit(trace)),
                    "frames": [
                        {
                            "frame_id": frame.frame_id,
                            "timestamp_sec": frame.timestamp_sec,
                            "timestamp": format_timestamp(frame.timestamp_sec),
                            "path": str(frame.path),
                        }
                        for frame in window.frames
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
                "verify_goal_event.window",
                "model_call_output",
                {
                    "event_id": event.event_id,
                    "window_index": window.window_index,
                    "content": clip_text(text, tracker_text_limit(trace)),
                },
            )
        parsed = _parse_goal_window_response(text)
        parsed["window_index"] = window.window_index
        parsed["start_sec"] = window.start_sec
        parsed["end_sec"] = window.end_sec
        parsed["frame_ids"] = [frame.frame_id for frame in window.frames]
        parsed["fifa_replay_frame_ids"] = list(window.fifa_replay_frame_ids)
        if window.fifa_replay_frame_ids:
            parsed["contains_fifa_replay_bumper"] = True
        window_payloads.append(parsed)

    payload = _aggregate_goal_window_payload(event, windows, window_payloads)
    payload = _apply_single_goal_followup_policy(event, payload, verify_config)
    refined_events = _apply_goal_verification(event, payload, verify_config)
    refined_type_summary = _refined_type_summary(refined_events)
    record = GoalVerificationRecord(
        event_id=event.event_id,
        original_event_type=event.event_type,
        refined_event_type=refined_type_summary,
        verdict=str(payload["verdict"]),
        confidence=float(payload["confidence"]),
        rationale=str(payload.get("rationale", "")),
        corrected_event_type=str(payload.get("corrected_event_type", refined_events[0].event_type if refined_events else event.event_type)),
        warnings=tuple(str(item) for item in payload.get("warnings", []) if isinstance(item, str)),
    )
    trace.record(
        "verify_goal_event",
        "parsed_model_response",
        {
            "event_id": event.event_id,
            "verdict": record.verdict,
            "refined_event_type": record.refined_event_type,
            "refined_event_count": len(refined_events),
            "refined_event_ids": [item.event_id for item in refined_events],
            "confidence": record.confidence,
            "window_count": len(windows),
            "fifa_replay_marker_frames": list(
                dict.fromkeys(frame_id for window in windows for frame_id in window.fifa_replay_frame_ids)
            ),
        },
    )
    return refined_events, record


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


def _build_goal_verification_window_messages(
    event: EventCandidate,
    manifest: FramesManifest,
    style: StyleProfile,
    window: GoalVerificationWindow,
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
    frames = window.frames
    frame_listing = "\n".join(
        f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]" for frame in frames
    )
    fifa_marker_text = (
        "Local FIFA replay bumper detector matched these frames: "
        + ", ".join(window.fifa_replay_frame_ids)
        + f". Treat matched frames as replay packaging, not live scoring action. {FIFA_REPLAY_BUMPER_EVIDENCE}"
        if window.fifa_replay_frame_ids
        else "Local FIFA replay bumper detector did not match any frame in this window."
    )
    prompt = f"""
You are verifying one sliding visual window inside a football goal candidate before commentary generation.

The coarse scanner already grouped the full package as event_type=goal, but it can confuse live goals, saves, replays, celebrations, scoreboard shots, and FIFA replay bumpers.
Your task is to classify only this 3-second window using the structured evidence and selected visual frames.

Decision rules:
- Use window_verdict=live_goal only when this window contains clear live or immediate scoring evidence: ball crossing the line, ball in net immediately after the finish, net rippling from the shot, or live scoring action plus unmistakable immediate reaction.
- Do not use live_goal for scoreboard graphics alone, celebration-only shots, ball-already-in-net shots, or replays of an earlier goal.
- Use window_verdict=replay_or_celebration for replay bumpers, slow-motion replays, post-goal reaction, scoreboard-only confirmation, or celebration-only shots.
- Use window_verdict=not_goal when the best evidence says it is a save, blocked shot, ordinary shot, near miss, restart, or unrelated attack without proof of live scoring.
- Use uncertain only when visual evidence is genuinely ambiguous.
- If this window is not a live goal, choose corrected_event_type from: shot, save, dangerous_attack, corner, free_kick, penalty, var_show, var_review, celebration_or_replay, other_relevant.
- If this window is a live goal, set corrected_event_type to goal and contains_live_scoring_action to true.
- If a local FIFA replay bumper marker is present, classify those matched frames as replay_or_celebration unless unmistakable live scoring action is visible elsewhere in the same window.
- Do not invent names, teams, scores, or facts.

Style context, only for salience, not for wording:
{style.prompt_injection}

Window:
- window_index: {window.window_index}
- start_sec: {window.start_sec}
- end_sec: {window.end_sec}
- start_label: {format_timestamp(window.start_sec)}
- end_label: {format_timestamp(window.end_sec)}
- sample_fps: approximately 2 fps

FIFA replay marker precheck:
{fifa_marker_text}

Selected frame prefixes for this window:
{frame_listing}

Goal package data:
{to_pretty_json(event_json)}

Return JSON only:
{{
  "window_verdict": "live_goal",
  "confidence": 0.0,
  "corrected_event_type": "goal",
  "contains_live_scoring_action": false,
  "contains_fifa_replay_bumper": false,
  "rationale": "short reason grounded in visual evidence",
  "warnings": []
}}
""".strip()
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for frame in frames:
        content.append({"type": "text", "text": f"[frame_id={frame.frame_id}, timestamp={format_timestamp(frame.timestamp_sec)}]"})
        content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame.path))}})
    return [{"role": "user", "content": content}]


def _parse_goal_window_response(text: str) -> dict[str, Any]:
    payload = extract_json_object(text)
    verdict = str(payload.get("window_verdict", payload.get("verdict", "uncertain"))).strip()
    verdict_aliases = {
        "confirmed_goal": "live_goal",
        "goal": "live_goal",
        "replay": "replay_or_celebration",
        "celebration": "replay_or_celebration",
        "celebration_or_replay": "replay_or_celebration",
    }
    verdict = verdict_aliases.get(verdict, verdict)
    if verdict not in {"live_goal", "not_goal", "replay_or_celebration", "uncertain"}:
        verdict = "uncertain"

    corrected_event_type = str(payload.get("corrected_event_type", "goal" if verdict == "live_goal" else "other_relevant")).strip()
    if corrected_event_type not in ALLOWED_CORRECTED_TYPES:
        corrected_event_type = "goal" if verdict == "live_goal" else "other_relevant"
    if verdict == "live_goal":
        corrected_event_type = "goal"
    elif verdict == "replay_or_celebration" and corrected_event_type == "goal":
        corrected_event_type = "celebration_or_replay"

    warnings = payload.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    return {
        "window_verdict": verdict,
        "confidence": _clamp_float(payload.get("confidence", 0.0)),
        "corrected_event_type": corrected_event_type,
        "contains_live_scoring_action": bool(payload.get("contains_live_scoring_action", verdict == "live_goal")),
        "contains_fifa_replay_bumper": bool(payload.get("contains_fifa_replay_bumper", False)),
        "rationale": str(payload.get("rationale", "")).strip(),
        "warnings": [str(item) for item in warnings if str(item)],
    }


def _aggregate_goal_window_payload(
    event: EventCandidate,
    windows: tuple[GoalVerificationWindow, ...],
    window_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    fifa_frame_ids = tuple(
        dict.fromkeys(frame_id for window in windows for frame_id in window.fifa_replay_frame_ids)
    )
    live_rows = [
        row
        for row in window_payloads
        if (
            row.get("window_verdict") == "live_goal"
            or bool(row.get("contains_live_scoring_action"))
            or row.get("corrected_event_type") == "goal"
        )
        and not (row.get("contains_fifa_replay_bumper") and not row.get("contains_live_scoring_action"))
    ]

    if live_rows:
        best = max(live_rows, key=lambda row: float(row.get("confidence", 0.0)))
        verdict = "confirmed_goal"
        corrected_type = "goal"
        confidence = _clamp_float(best.get("confidence", 0.0))
        rationale = _join_window_rationales(
            "At least one 3-second verification window contains live scoring evidence.",
            window_payloads,
        )
    else:
        all_uncertain = bool(window_payloads) and all(row.get("window_verdict") == "uncertain" for row in window_payloads)
        verdict = "uncertain" if all_uncertain and not fifa_frame_ids else "not_goal"
        corrected_type = _choose_downgrade_type(window_payloads, bool(fifa_frame_ids))
        confidence = max((_clamp_float(row.get("confidence", 0.0)) for row in window_payloads), default=0.0)
        rationale = _join_window_rationales(
            "No 3-second verification window contains clear live scoring evidence.",
            window_payloads,
        )

    warnings = _aggregate_window_warnings(window_payloads)
    if fifa_frame_ids:
        warnings.append("fifa_replay_bumper_detected:" + ",".join(fifa_frame_ids))

    return {
        "verdict": verdict,
        "confidence": confidence,
        "corrected_event_type": corrected_type,
        "rationale": rationale,
        "phase_labels": _phase_labels_from_windows(event, windows, live_rows[:1], fifa_frame_ids),
        "warnings": list(dict.fromkeys(warnings)),
    }


def _choose_downgrade_type(window_payloads: list[dict[str, Any]], has_fifa_replay_marker: bool) -> str:
    if has_fifa_replay_marker:
        return "celebration_or_replay"
    candidates = [
        row
        for row in window_payloads
        if row.get("corrected_event_type") in ALLOWED_CORRECTED_TYPES and row.get("corrected_event_type") != "goal"
    ]
    if not candidates:
        return "other_relevant"
    best = max(candidates, key=lambda row: float(row.get("confidence", 0.0)))
    return str(best.get("corrected_event_type") or "other_relevant")


def _join_window_rationales(prefix: str, window_payloads: list[dict[str, Any]]) -> str:
    snippets: list[str] = []
    for row in window_payloads:
        rationale = str(row.get("rationale", "")).strip()
        if not rationale:
            continue
        snippets.append(
            f"window {row.get('window_index')} {row.get('window_verdict')} "
            f"{row.get('corrected_event_type')}: {rationale}"
        )
    if not snippets:
        return prefix
    return prefix + " " + " | ".join(snippets[:8])


def _aggregate_window_warnings(window_payloads: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for row in window_payloads:
        for warning in row.get("warnings", []):
            text = str(warning).strip()
            if text:
                warnings.append(f"window {row.get('window_index')}: {text}")
    return warnings


def _phase_labels_from_windows(
    event: EventCandidate,
    windows: tuple[GoalVerificationWindow, ...],
    live_rows: list[dict[str, Any]],
    fifa_frame_ids: tuple[str, ...],
) -> list[dict[str, Any]]:
    live_row = live_rows[0] if live_rows else None
    live_start = float(live_row.get("start_sec", 0.0)) if live_row else None
    live_end = float(live_row.get("end_sec", live_start or 0.0)) if live_row else None
    fifa_windows = [window for window in windows if window.fifa_replay_frame_ids]

    labels: list[dict[str, Any]] = []
    used_live = False
    for index, phase in enumerate(event.phases):
        phase_type = phase.phase_type if phase.phase_type in GOAL_PHASE_TYPES else "buildup"
        reason = "Preserved original phase label."
        if _phase_has_fifa_marker(phase, fifa_frame_ids, fifa_windows):
            phase_type = "replay"
            reason = "Local FIFA replay bumper detector matched this phase/window."
        elif live_start is not None and live_end is not None and _ranges_overlap(
            phase.start_sec,
            phase.end_sec,
            live_start,
            live_end,
        ):
            if used_live:
                phase_type = "replay"
                reason = "Additional live-looking phase after first live goal window is treated as replay."
            else:
                phase_type = "live_goal"
                reason = "This phase overlaps the first window with live scoring evidence."
                used_live = True
        elif live_start is not None and phase.end_sec < live_start:
            phase_type = "buildup"
            reason = "This phase occurs before the verified live goal window."
        elif live_start is not None and phase.start_sec > (live_end or live_start):
            phase_type = "celebration" if phase.phase_type == "celebration" else "replay"
            reason = "This phase occurs after the verified live goal window."
        labels.append({"phase_index": index, "phase_type": phase_type, "reason": reason})
    if live_row and labels and not any(label.get("phase_type") == "live_goal" for label in labels):
        fallback_index = _nearest_phase_index(event.phases, live_start or event.start_sec, live_end or live_start or event.end_sec)
        labels[fallback_index] = {
            "phase_index": fallback_index,
            "phase_type": "live_goal",
            "reason": "Fallback live_goal label assigned to the phase nearest the verified live scoring window.",
        }
    return labels


def _nearest_phase_index(phases: tuple[EventPhase, ...], start_sec: float, end_sec: float) -> int:
    target_midpoint = (start_sec + end_sec) / 2.0
    best_index = 0
    best_score = float("inf")
    for index, phase in enumerate(phases):
        overlap = max(0.0, min(phase.end_sec, end_sec) - max(phase.start_sec, start_sec))
        midpoint = (phase.start_sec + phase.end_sec) / 2.0
        score = abs(midpoint - target_midpoint) - overlap
        if score < best_score:
            best_score = score
            best_index = index
    return best_index


def _phase_has_fifa_marker(
    phase: EventPhase,
    fifa_frame_ids: tuple[str, ...],
    fifa_windows: list[GoalVerificationWindow],
) -> bool:
    if any(frame_id in fifa_frame_ids for frame_id in phase.evidence_frames):
        return True
    return any(_ranges_overlap(phase.start_sec, phase.end_sec, window.start_sec, window.end_sec) for window in fifa_windows)


def _ranges_overlap(left_start: float, left_end: float, right_start: float, right_end: float) -> bool:
    return left_start <= right_end and right_start <= left_end


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
) -> tuple[EventCandidate, ...]:
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
        if refined_type != "goal" and (phase_type == "live_goal" or phase.phase_type == "live_goal"):
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
    confidence = max(event.confidence, float(payload["confidence"]))
    if refined_type != "goal":
        return _split_downgraded_goal_package(
            event,
            refined_type,
            tuple(phases),
            confidence,
            evidence_summary,
        )

    return (
        EventCandidate(
            event_id=event.event_id,
            event_type=refined_type,
            start_sec=event.start_sec,
            end_sec=event.end_sec,
            evidence_frames=event.evidence_frames,
            confidence=confidence,
            evidence_summary=evidence_summary,
            phases=tuple(phases),
        ),
    )


def _split_downgraded_goal_package(
    event: EventCandidate,
    refined_type: str,
    phases: tuple[EventPhase, ...],
    confidence: float,
    evidence_summary: str,
) -> tuple[EventCandidate, ...]:
    if refined_type == "celebration_or_replay":
        replay_phases = tuple(_as_replay_phase(phase) for phase in phases) or (
            EventPhase("replay", event.start_sec, event.end_sec, event.evidence_frames, event.evidence_summary),
        )
        return (
            _event_from_phases(
                event.event_id,
                "celebration_or_replay",
                replay_phases,
                confidence,
                evidence_summary,
            ),
        )

    primary_phases = tuple(phase for phase in phases if phase.phase_type not in GOAL_FOLLOWUP_PHASE_TYPES)
    if not primary_phases:
        primary_phases = (
            EventPhase(refined_type, event.start_sec, event.end_sec, event.evidence_frames, event.evidence_summary),
        )
    primary_phases = _ensure_primary_phase_type(primary_phases, refined_type)
    split_events = [
        _event_from_phases(
            event.event_id,
            refined_type,
            primary_phases,
            confidence,
            evidence_summary,
        )
    ]

    followup_phases = tuple(phase for phase in phases if phase.phase_type in GOAL_FOLLOWUP_PHASE_TYPES)
    if followup_phases:
        followup_summary = "; ".join(
            part
            for part in [
                "Split from downgraded goal package as replay/celebration follow-up.",
                evidence_summary,
            ]
            if part
        )
        split_events.append(
            _event_from_phases(
                f"{event.event_id}_replay_01",
                "celebration_or_replay",
                followup_phases,
                confidence,
                followup_summary,
            )
        )
    return tuple(split_events)


def _ensure_primary_phase_type(phases: tuple[EventPhase, ...], refined_type: str) -> tuple[EventPhase, ...]:
    if any(phase.phase_type == refined_type for phase in phases):
        return phases
    if refined_type not in NON_GOAL_PRIMARY_TYPES:
        return phases
    updated = list(phases)
    target_index = next(
        (index for index, phase in enumerate(updated) if phase.phase_type == "live_goal"),
        len(updated) - 1,
    )
    phase = updated[target_index]
    updated[target_index] = EventPhase(
        phase_type=refined_type,
        start_sec=phase.start_sec,
        end_sec=phase.end_sec,
        evidence_frames=phase.evidence_frames,
        evidence_summary=phase.evidence_summary,
    )
    return tuple(updated)


def _as_replay_phase(phase: EventPhase) -> EventPhase:
    phase_type = phase.phase_type if phase.phase_type in GOAL_FOLLOWUP_PHASE_TYPES else "replay"
    return EventPhase(
        phase_type=phase_type,
        start_sec=phase.start_sec,
        end_sec=phase.end_sec,
        evidence_frames=phase.evidence_frames,
        evidence_summary=phase.evidence_summary,
    )


def _event_from_phases(
    event_id: str,
    event_type: str,
    phases: tuple[EventPhase, ...],
    confidence: float,
    evidence_summary: str,
) -> EventCandidate:
    start_sec = min(phase.start_sec for phase in phases)
    end_sec = max(phase.end_sec for phase in phases)
    evidence_frames = tuple(
        dict.fromkeys(frame_id for phase in phases for frame_id in phase.evidence_frames)
    )
    return EventCandidate(
        event_id=event_id,
        event_type=event_type,
        start_sec=start_sec,
        end_sec=end_sec,
        evidence_frames=evidence_frames,
        confidence=confidence,
        evidence_summary=evidence_summary,
        phases=phases,
    )


def _refined_type_summary(events: tuple[EventCandidate, ...]) -> str:
    if len(events) == 1:
        return events[0].event_type
    return "split:" + ",".join(event.event_type for event in events)


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


def estimate_goal_verification_calls(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest_frames: tuple[FrameInfo, ...],
    config: GoalVerificationConfig | None = None,
) -> int:
    verify_config = config or GoalVerificationConfig()
    return sum(
        len(_build_verification_windows(event, manifest_frames, verify_config))
        for event in events
        if event.event_type == "goal"
    )


def _build_verification_windows(
    event: EventCandidate,
    manifest_frames: tuple[FrameInfo, ...],
    config: GoalVerificationConfig,
) -> tuple[GoalVerificationWindow, ...]:
    window_sec = max(0.25, float(config.window_sec))
    stride_sec = max(0.25, float(config.stride_sec))
    start_sec = min(event.start_sec, event.end_sec)
    end_sec = max(event.start_sec, event.end_sec)
    windows: list[GoalVerificationWindow] = []
    current = start_sec
    index = 1
    while current <= end_sec + 1e-6:
        window_end = min(end_sec, current + window_sec)
        include_end = window_end >= end_sec - 1e-6
        interval_frames = _frames_in_time_window(manifest_frames, current, window_end, include_end)
        sampled_frames = _sample_frames_by_fps(interval_frames, config.sample_fps)
        if sampled_frames:
            fifa_frame_ids = tuple(
                frame.frame_id for frame in sampled_frames if detect_fifa_replay_bumper(frame.path)
            )
            windows.append(
                GoalVerificationWindow(
                    window_index=index,
                    start_sec=current,
                    end_sec=window_end,
                    frames=sampled_frames,
                    fifa_replay_frame_ids=fifa_frame_ids,
                )
            )
            index += 1
        if include_end:
            break
        current += stride_sec
    return tuple(windows)


def _frames_in_time_window(
    frames: tuple[FrameInfo, ...],
    start_sec: float,
    end_sec: float,
    include_end: bool,
) -> tuple[FrameInfo, ...]:
    if include_end:
        return tuple(frame for frame in frames if start_sec <= frame.timestamp_sec <= end_sec)
    return tuple(frame for frame in frames if start_sec <= frame.timestamp_sec < end_sec)


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
        "window_sec": config.window_sec,
        "stride_sec": config.stride_sec,
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
