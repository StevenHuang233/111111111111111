from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EVENT_TYPE_IDS = [
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
    "no_event",
]
DEFAULT_EVENT_TYPES = DEFAULT_EVENT_TYPE_IDS

EVENT_TYPES_PATH = Path(__file__).resolve().parent.parent / "configs" / "event_types.json"


@dataclass(frozen=True)
class EventTypeDefinition:
    event_id: str
    name: str
    description: str
    positive_cues: tuple[str, ...] = ()
    negative_cues: tuple[str, ...] = ()

    @classmethod
    def from_config(cls, item: str | dict) -> "EventTypeDefinition":
        if isinstance(item, str):
            return cls(event_id=item, name=item, description=f"Classify as {item} when the frame clearly matches this event.")
        if not isinstance(item, dict):
            raise ValueError("Each event type must be a string or an object.")

        event_id = str(item.get("id", "")).strip()
        if not event_id:
            raise ValueError("Event type object missing required field 'id'.")

        positive = item.get("positive_cues", [])
        negative = item.get("negative_cues", [])
        if not isinstance(positive, list) or not all(isinstance(cue, str) for cue in positive):
            raise ValueError(f"positive_cues for '{event_id}' must be a string list.")
        if not isinstance(negative, list) or not all(isinstance(cue, str) for cue in negative):
            raise ValueError(f"negative_cues for '{event_id}' must be a string list.")

        return cls(
            event_id=event_id,
            name=str(item.get("name", event_id)),
            description=str(item.get("description", f"Classify as {event_id} when this event is clearly visible.")),
            positive_cues=tuple(positive),
            negative_cues=tuple(negative),
        )


@dataclass(frozen=True)
class EventTypeRegistry:
    definitions: tuple[EventTypeDefinition, ...]
    no_event_type: str = "no_event"

    def __post_init__(self) -> None:
        if self.no_event_type not in self.event_types:
            raise ValueError(f"Event types must include '{self.no_event_type}'.")
        if len(set(self.event_types)) != len(self.event_types):
            raise ValueError("Event types must be unique.")

    @property
    def event_types(self) -> tuple[str, ...]:
        return tuple(definition.event_id for definition in self.definitions)

    @property
    def allowed(self) -> set[str]:
        return set(self.event_types)

    def validate(self, event_type: str) -> str:
        if event_type not in self.allowed:
            raise ValueError(f"Unsupported event_type '{event_type}'.")
        return event_type

    def prompt_reference(self) -> str:
        lines: list[str] = []
        for definition in self.definitions:
            lines.append(f"- {definition.event_id} ({definition.name}): {definition.description}")
            if definition.positive_cues:
                lines.append(f"  Positive cues: {'; '.join(definition.positive_cues)}")
            if definition.negative_cues:
                lines.append(f"  Negative cues: {'; '.join(definition.negative_cues)}")
        return "\n".join(lines)


def load_event_types(path: str | None = None) -> EventTypeRegistry:
    config_path = Path(path).expanduser() if path else EVENT_TYPES_PATH
    if config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        event_types = data.get("event_types") if isinstance(data, dict) else data
        if not isinstance(event_types, list):
            raise ValueError("Event type config must be a list or an object with an 'event_types' list.")
        return EventTypeRegistry(tuple(EventTypeDefinition.from_config(item) for item in event_types))
    return EventTypeRegistry(tuple(EventTypeDefinition.from_config(item) for item in DEFAULT_EVENT_TYPE_IDS))
