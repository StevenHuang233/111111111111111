from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MATCH_CONTEXTS_PATH = Path(__file__).resolve().parent.parent / "configs" / "match_contexts.json"


@dataclass(frozen=True)
class TeamContext:
    name: str
    short_name: str = ""
    aliases: tuple[str, ...] = ()
    kit: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TeamContext":
        if "name" not in data:
            raise ValueError("Team context missing required field: name")
        aliases = data.get("aliases", ())
        if not isinstance(aliases, list):
            aliases = ()
        return cls(
            name=str(data["name"]),
            short_name=str(data.get("short_name", "")),
            aliases=tuple(str(item) for item in aliases),
            kit=str(data.get("kit", "")),
        )


@dataclass(frozen=True)
class MatchContext:
    context_id: str
    match_title: str
    competition: str = ""
    description: str = ""
    home_team: TeamContext | None = None
    away_team: TeamContext | None = None
    final_score: str = ""
    prompt_injection: str = ""
    notes: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchContext":
        required = ["context_id", "match_title"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Match context missing required fields: {', '.join(missing)}")

        notes = data.get("notes", ())
        if not isinstance(notes, list):
            notes = ()
        home = data.get("home_team")
        away = data.get("away_team")
        return cls(
            context_id=str(data["context_id"]),
            match_title=str(data["match_title"]),
            competition=str(data.get("competition", "")),
            description=str(data.get("description", "")),
            home_team=TeamContext.from_dict(home) if isinstance(home, dict) else None,
            away_team=TeamContext.from_dict(away) if isinstance(away, dict) else None,
            final_score=str(data.get("final_score", "")),
            prompt_injection=str(data.get("prompt_injection", "")),
            notes=tuple(str(item) for item in notes),
            metadata=data.get("metadata") if isinstance(data.get("metadata"), dict) else None,
        )

    @property
    def team_names(self) -> tuple[str, ...]:
        names: list[str] = []
        for team in (self.home_team, self.away_team):
            if team is None:
                continue
            names.append(team.name)
            if team.short_name:
                names.append(team.short_name)
            names.extend(team.aliases)
        return tuple(dict.fromkeys(name for name in names if name))


def _load_contexts_file(path: Path) -> dict[str, MatchContext]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("contexts") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("Match context config must be a list or an object with a 'contexts' list.")
    contexts = [MatchContext.from_dict(item) for item in items]
    return {context.context_id: context for context in contexts}


def load_match_context(context_id_or_path: str | None = None) -> MatchContext | None:
    if context_id_or_path is None or str(context_id_or_path).strip() in {"", "none", "None"}:
        return None

    path = Path(str(context_id_or_path)).expanduser()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "contexts" in data:
            contexts = _load_contexts_file(path)
            if len(contexts) != 1:
                raise ValueError("Path-based load_match_context expects exactly one context or a single context object.")
            return next(iter(contexts.values()))
        if not isinstance(data, dict):
            raise ValueError("Custom match context file must contain one JSON object.")
        return MatchContext.from_dict(data)

    contexts = _load_contexts_file(MATCH_CONTEXTS_PATH)
    if str(context_id_or_path) not in contexts:
        available = ", ".join(sorted(contexts))
        raise KeyError(f"Unknown match context '{context_id_or_path}'. Available contexts: {available}")
    return contexts[str(context_id_or_path)]


def match_context_block(context: MatchContext | None) -> str:
    if context is None:
        return "No match context was provided. Use only visible evidence and event data for teams, scores, and names."

    lines = [
        f"Match context: {context.match_title} ({context.context_id})",
    ]
    if context.competition:
        lines.append(f"Competition: {context.competition}")
    if context.description:
        lines.append(f"Description: {context.description}")
    for label, team in (("Home/Team A", context.home_team), ("Away/Team B", context.away_team)):
        if team is None:
            continue
        aliases = f"; aliases: {', '.join(team.aliases)}" if team.aliases else ""
        short_name = f"; short name: {team.short_name}" if team.short_name else ""
        kit = f"; kit: {team.kit}" if team.kit else ""
        lines.append(f"{label}: {team.name}{short_name}{aliases}{kit}")
    if context.final_score:
        lines.append(f"Known final score metadata: {context.final_score}")
    if context.prompt_injection:
        lines.append(f"Context instruction: {context.prompt_injection}")
    if context.notes:
        lines.append("Context notes:")
        lines.extend(f"- {note}" for note in context.notes)
    lines.append(
        "Use this context only to disambiguate teams, kits, competition, and known names. "
        "Do not let context override visible frame evidence for whether a goal, foul, card, or save actually happened."
    )
    return "\n".join(lines)
