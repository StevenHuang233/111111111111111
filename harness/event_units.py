from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .json_utils import to_pretty_json
from .manifest import FramesManifest
from .scanner import EventCandidate, EventPhase


DEFAULT_GOAL_RELATED_TYPES = (
    "goal",
    "shot",
    "save",
    "dangerous_attack",
    "corner",
    "free_kick",
    "penalty",
    "var_review",
    "celebration_or_replay",
    "other_relevant",
)


@dataclass(frozen=True)
class CommentaryUnitConfig:
    enabled: bool = True
    goal_context_before_sec: float = 20.0
    goal_replay_after_sec: float = 48.0
    goal_related_types: tuple[str, ...] = DEFAULT_GOAL_RELATED_TYPES
    include_event_types: tuple[str, ...] = ()
    exclude_event_types: tuple[str, ...] = ()
    min_confidence: float = 0.0


def build_commentary_units(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    config: CommentaryUnitConfig | None = None,
) -> list[EventCandidate]:
    unit_config = config or CommentaryUnitConfig()
    ordered = sorted(events, key=lambda event: (event.start_sec, event.end_sec, event.event_id))
    if not unit_config.enabled:
        return _renumber_units([event for event in ordered if _keep_event(event, unit_config)])

    consumed: set[int] = set()
    units: list[EventCandidate] = []

    for index, event in enumerate(ordered):
        if index in consumed or event.event_type != "goal" or not _type_allowed("goal", unit_config):
            continue
        included_indexes = _goal_cluster_indexes(index, ordered, consumed, unit_config)
        consumed.update(included_indexes)
        included = [ordered[item] for item in sorted(included_indexes)]
        units.append(_build_goal_unit(included))

    for index, event in enumerate(ordered):
        if index in consumed:
            continue
        if _keep_event(event, unit_config):
            units.append(event)

    return _renumber_units(units)


def commentary_units_to_dict(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest | None = None,
    config: CommentaryUnitConfig | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "events": [_event_to_dict(event) for event in events],
    }
    if manifest is not None:
        payload["video_id"] = manifest.video_id
        payload["source_video"] = manifest.source_video
    if config is not None:
        payload["config"] = {
            "enabled": config.enabled,
            "goal_context_before_sec": config.goal_context_before_sec,
            "goal_replay_after_sec": config.goal_replay_after_sec,
            "goal_related_types": list(config.goal_related_types),
            "include_event_types": list(config.include_event_types),
            "exclude_event_types": list(config.exclude_event_types),
            "min_confidence": config.min_confidence,
        }
    return payload


def dump_commentary_units(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest | None,
    path: str | Path,
    config: CommentaryUnitConfig | None = None,
) -> None:
    Path(path).write_text(to_pretty_json(commentary_units_to_dict(events, manifest, config)), encoding="utf-8")


def _goal_cluster_indexes(
    seed_index: int,
    events: list[EventCandidate],
    consumed: set[int],
    config: CommentaryUnitConfig,
) -> set[int]:
    related_types = set(config.goal_related_types)
    excluded_types = set(config.exclude_event_types)
    seed = events[seed_index]
    context_start = seed.start_sec - max(0.0, config.goal_context_before_sec)
    forward_end = seed.end_sec + max(0.0, config.goal_replay_after_sec)
    included = {seed_index}

    for index in range(seed_index - 1, -1, -1):
        event = events[index]
        if event.end_sec < context_start:
            break
        if index in consumed or event.event_type not in related_types or event.event_type in excluded_types:
            continue
        if event.start_sec <= seed.start_sec:
            included.add(index)

    for index in range(seed_index + 1, len(events)):
        event = events[index]
        if event.start_sec > forward_end:
            break
        if index in consumed or event.event_type not in related_types or event.event_type in excluded_types:
            continue
        included.add(index)

    return included


def _build_goal_unit(events: list[EventCandidate]) -> EventCandidate:
    ordered = sorted(events, key=lambda event: (event.start_sec, event.end_sec, event.event_id))
    first_goal = next((event for event in ordered if event.event_type == "goal"), ordered[0])
    phases: list[EventPhase] = []
    evidence_frames: list[str] = []
    summaries: list[str] = []
    confidence = 0.0

    for event in ordered:
        confidence = max(confidence, event.confidence)
        evidence_frames.extend(event.evidence_frames)
        if event.evidence_summary:
            summaries.append(event.evidence_summary)
        source_phases = event.phases or (
            EventPhase(event.event_type, event.start_sec, event.end_sec, event.evidence_frames, event.evidence_summary),
        )
        for phase in source_phases:
            phases.append(
                EventPhase(
                    phase_type=_goal_phase_type(event, phase, first_goal),
                    start_sec=phase.start_sec,
                    end_sec=phase.end_sec,
                    evidence_frames=phase.evidence_frames,
                    evidence_summary=phase.evidence_summary,
                )
            )

    return EventCandidate(
        event_id=ordered[0].event_id,
        event_type="goal",
        start_sec=min(event.start_sec for event in ordered),
        end_sec=max(event.end_sec for event in ordered),
        evidence_frames=_unique_tuple(tuple(evidence_frames)),
        confidence=confidence,
        evidence_summary="; ".join(dict.fromkeys(summary for summary in summaries if summary)),
        phases=tuple(phases),
    )


def _goal_phase_type(event: EventCandidate, phase: EventPhase, first_goal: EventCandidate) -> str:
    if event.event_type == "goal":
        if event.start_sec <= first_goal.end_sec and phase.start_sec <= first_goal.end_sec:
            return "live_goal"
        return "replay"
    if event.event_type == "var_review":
        return "var_review"
    if event.end_sec <= first_goal.start_sec:
        return "buildup"
    if event.event_type == "celebration_or_replay":
        return _classify_replay_or_celebration(phase.evidence_summary or event.evidence_summary)
    if event.event_type in {"shot", "save", "dangerous_attack", "corner", "free_kick", "penalty", "other_relevant"}:
        return "replay"
    return phase.phase_type


def _classify_replay_or_celebration(text: str) -> str:
    lowered = text.lower()
    replay_markers = (
        "replay",
        "slow motion",
        "slow-motion",
        "angle",
        "close-up of the finish",
        "behind the goal",
        "broadcast replay",
        "replayed",
    )
    celebration_markers = (
        "celebrat",
        "crowd cheering",
        "crowd celebration",
        "players embracing",
        "arms raised",
        "coach",
        "reaction",
        "emotional",
    )
    if any(marker in lowered for marker in replay_markers):
        return "replay"
    if any(marker in lowered for marker in celebration_markers):
        return "celebration"
    return "celebration"


def _keep_event(event: EventCandidate, config: CommentaryUnitConfig) -> bool:
    return (
        _type_allowed(event.event_type, config)
        and event.confidence >= max(0.0, config.min_confidence)
    )


def _type_allowed(event_type: str, config: CommentaryUnitConfig) -> bool:
    include = set(config.include_event_types)
    exclude = set(config.exclude_event_types)
    if include and event_type not in include:
        return False
    return event_type not in exclude


def _overlaps(left_start: float, left_end: float, right_start: float, right_end: float) -> bool:
    return left_start <= right_end and right_start <= left_end


def _renumber_units(events: list[EventCandidate]) -> list[EventCandidate]:
    return [_renumber_event(event, index + 1) for index, event in enumerate(sorted(events, key=lambda item: item.start_sec))]


def _renumber_event(event: EventCandidate, number: int) -> EventCandidate:
    return EventCandidate(
        event_id=f"U{number:03d}",
        event_type=event.event_type,
        start_sec=event.start_sec,
        end_sec=event.end_sec,
        evidence_frames=event.evidence_frames,
        confidence=event.confidence,
        evidence_summary=event.evidence_summary,
        phases=event.phases,
    )


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


def _unique_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
