from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .json_utils import to_pretty_json


class StepTracker(Protocol):
    def record(self, step: str, action: str, detail: dict[str, Any] | None = None) -> None:
        ...


@dataclass(frozen=True)
class TraceStep:
    index: int
    elapsed_sec: float
    step: str
    action: str
    detail: dict[str, Any] = field(default_factory=dict)


class TraceRecorder:
    def __init__(self, record_model_io: bool = True, max_text_chars: int = 20000) -> None:
        self._start = time.perf_counter()
        self._steps: list[TraceStep] = []
        self.record_model_io = record_model_io
        self.max_text_chars = max_text_chars

    @property
    def steps(self) -> tuple[TraceStep, ...]:
        return tuple(self._steps)

    def record(self, step: str, action: str, detail: dict[str, Any] | None = None) -> None:
        self._steps.append(
            TraceStep(
                index=len(self._steps) + 1,
                elapsed_sec=round(time.perf_counter() - self._start, 6),
                step=step,
                action=action,
                detail=detail or {},
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": [
                {
                    "index": step.index,
                    "elapsed_sec": step.elapsed_sec,
                    "step": step.step,
                    "action": step.action,
                    "detail": step.detail,
                }
                for step in self._steps
            ]
        }

    def dump(self, path: str | Path) -> None:
        Path(path).write_text(to_pretty_json(self.to_dict()), encoding="utf-8")


class NullTracker:
    record_model_io = False
    max_text_chars = 0

    def record(self, step: str, action: str, detail: dict[str, Any] | None = None) -> None:
        return None


def should_record_model_io(tracker: StepTracker) -> bool:
    return bool(getattr(tracker, "record_model_io", False))


def clip_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"


def tracker_text_limit(tracker: StepTracker) -> int:
    return int(getattr(tracker, "max_text_chars", 20000))
