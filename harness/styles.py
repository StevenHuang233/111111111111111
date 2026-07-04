from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STYLES_PATH = Path(__file__).resolve().parent.parent / "configs" / "styles.json"


@dataclass(frozen=True)
class StyleProfile:
    style_id: str
    name: str
    description: str
    prompt_injection: str
    temperature: float = 0.3
    top_p: float = 0.95
    max_tokens: int = 1024
    thinking_mode: bool = False
    extra: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StyleProfile":
        required = ["style_id", "name", "description", "prompt_injection"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Style profile missing required fields: {', '.join(missing)}")

        return cls(
            style_id=str(data["style_id"]),
            name=str(data["name"]),
            description=str(data["description"]),
            prompt_injection=str(data["prompt_injection"]),
            temperature=float(data.get("temperature", 0.3)),
            top_p=float(data.get("top_p", 0.95)),
            max_tokens=int(data.get("max_tokens", 1024)),
            thinking_mode=bool(data.get("thinking_mode", False)),
            extra=data.get("extra") if isinstance(data.get("extra"), dict) else None,
        )


def _load_styles_file(path: Path) -> dict[str, StyleProfile]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("styles") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("Style config must be a list or an object with a 'styles' list.")

    profiles = [StyleProfile.from_dict(item) for item in items]
    return {profile.style_id: profile for profile in profiles}


def load_style(style_id_or_path: str = "broadcast_professional") -> StyleProfile:
    path = Path(style_id_or_path).expanduser()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "styles" in data:
            styles = _load_styles_file(path)
            if len(styles) != 1:
                raise ValueError("Path-based load_style expects exactly one style or a single style object.")
            return next(iter(styles.values()))
        if not isinstance(data, dict):
            raise ValueError("Custom style file must contain one JSON object.")
        return StyleProfile.from_dict(data)

    styles = _load_styles_file(STYLES_PATH)
    if style_id_or_path not in styles:
        available = ", ".join(sorted(styles))
        raise KeyError(f"Unknown style '{style_id_or_path}'. Available styles: {available}")
    return styles[style_id_or_path]
