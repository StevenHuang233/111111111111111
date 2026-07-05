#!/usr/bin/env python
"""Postprocess generated commentary with goal/reflection verification.

This module runs after full commentary generation. It is conservative:

- It never increments score from text alone.
- It keeps one primary generated segment per verified scoreboard change.
- Extra goal claims are rewritten as replay, shot, or dangerous attack.
- Intern-S2-Preview can be used as an optional visual verifier when frame paths
  are provided, but the deterministic scoreboard-state pass is always available.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual-night.json"
DEFAULT_EVENTS = REPO_ROOT / "outputs" / "events-night.json"
DEFAULT_MANUAL_REVIEW = REPO_ROOT / "reference" / "evaluation" / "goal_scoreboard_manual_review.md"
DEFAULT_OUTPUT = REPO_ROOT / "reference" / "evaluation" / "night_reflection" / "commentary_bilingual-night_reflected.json"
DEFAULT_REPORT_JSON = REPO_ROOT / "reference" / "evaluation" / "night_reflection" / "goal_reflection_report.json"
DEFAULT_REPORT_MD = REPO_ROOT / "reference" / "evaluation" / "night_reflection" / "goal_reflection_report.md"

GOAL_PATTERNS = (
    r"\bscores?\b",
    r"\bgoal\b",
    r"\btakes? the lead\b",
    r"\bdoubles? (?:their|the) lead\b",
    r"\bextends? (?:their|the) lead\b",
    r"\bfinds? the back of the net\b",
    r"\bback of the net\b",
    r"\binto the net\b",
    r"取得领先",
    r"扩大领先",
    r"扳平",
    r"破门",
    r"球进",
    r"进球",
    r"比分",
)
NEGATION_HINTS = (
    "no goal",
    "not a goal",
    "ruled out",
    "disallowed",
    "offside",
    "save",
    "saved",
    "parry",
    "denies",
    "blocked",
    "miss",
    "没有进",
    "不算",
    "越位",
    "被吹",
    "扑救",
    "扑出",
    "挡出",
    "偏出",
    "错失",
)
REPLAY_HINTS = (
    "replay",
    "slow motion",
    "slow-motion",
    "fifa graphic",
    "回放",
    "慢镜头",
    "慢动作",
    "图形特效",
    "再次看到",
)
SHOT_HINTS = (
    "shot",
    "shoot",
    "strike",
    "header",
    "save",
    "射门",
    "起脚",
    "攻门",
    "头球",
    "扑救",
    "扑出",
)
SCORE_PATTERN = re.compile(r"(?<!\d)(\d{1,2})\s*(?:-|:|：|比)\s*(\d{1,2})(?!\d)")
CURACAO_TERMS = ("curacao", "curaçao", "库拉索")
GERMANY_TERMS = ("germany", "german", "德国")
FORBIDDEN_ENTITIES = ("colombia", "colombian", "哥伦比亚", "paraguay", "巴拉圭")
ACTION_TYPES = {"goal", "shot", "save", "foul", "card", "corner", "free_kick", "dangerous_attack", "var_review"}


@dataclass(frozen=True)
class VerifiedGoal:
    goal_id: str
    score_before: str
    score_after: str
    start_sec: float
    end_sec: float
    match_clock: str

    @property
    def midpoint_sec(self) -> float:
        return (self.start_sec + self.end_sec) / 2.0


@dataclass(frozen=True)
class SegmentRef:
    index: int
    event_id: str
    event_type: str
    start_sec: float
    end_sec: float
    text: str

    @property
    def midpoint_sec(self) -> float:
        return (self.start_sec + self.end_sec) / 2.0


def parse_time(value: str) -> float:
    parts = [int(part) for part in value.strip().split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Unsupported timestamp: {value}")


def stamp(seconds: float) -> str:
    value = max(0, int(round(seconds)))
    minutes, sec = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def load_verified_goals(path: Path) -> list[VerifiedGoal]:
    pattern = re.compile(
        r"^\|\s*(G\d+)\s*\|\s*([^|]+?)\s*->\s*([^|]+?)\s*\|\s*`([^`]+)`\s*to\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*to\s*`([^`]+)`\s*\|"
    )
    goals: list[VerifiedGoal] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        goal_id, score_before, score_after, start_evidence, end_evidence, clock_start, clock_end = match.groups()
        goals.append(
            VerifiedGoal(
                goal_id=goal_id,
                score_before=score_before.strip(),
                score_after=score_after.strip(),
                start_sec=parse_time(start_evidence.split()[0]),
                end_sec=parse_time(end_evidence.split()[0]),
                match_clock=f"{clock_start} to {clock_end}",
            )
        )
    return goals


def segment_text(segment: dict[str, Any]) -> str:
    values: list[str] = []
    for language in ("english", "chinese"):
        value = segment.get(language, {})
        if isinstance(value, dict):
            values.append(str(value.get("commentary_text", "")))
            for line in value.get("subtitle_lines", []) if isinstance(value.get("subtitle_lines"), list) else []:
                if isinstance(line, dict):
                    values.append(str(line.get("text", "")))
    return "\n".join(values)


def load_segments(data: dict[str, Any]) -> list[SegmentRef]:
    refs: list[SegmentRef] = []
    for index, segment in enumerate(data.get("segments", [])):
        if not isinstance(segment, dict):
            continue
        refs.append(
            SegmentRef(
                index=index,
                event_id=str(segment.get("event_id", f"S{index:03d}")),
                event_type=str(segment.get("event_type", "")),
                start_sec=float(segment.get("talk_start_sec", 0.0)),
                end_sec=float(segment.get("talk_end_sec", 0.0)),
                text=segment_text(segment),
            )
        )
    return refs


def has_goal_assertion(segment: SegmentRef) -> bool:
    lowered = segment.text.lower()
    if segment.event_type == "goal":
        return True
    if any(hint in lowered for hint in NEGATION_HINTS):
        return False
    return any(re.search(pattern, segment.text, re.I) for pattern in GOAL_PATTERNS)


def has_replay_hint(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in REPLAY_HINTS)


def has_shot_hint(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in SHOT_HINTS)


def infer_team(text: str) -> str:
    lowered = text.lower()
    if re.search(r"\bgermany(?:'s)?\b.*\b(take|takes|create|creates|push|pushes|attack|attacks|shot|shoot|strike)", lowered):
        return "Germany"
    if re.search(r"\bcuracao(?:'s)?\b|\bcuraçao(?:'s)?\b", lowered) and re.search(
        r"\b(take|takes|create|creates|push|pushes|attack|attacks|shot|shoot|strike)", lowered
    ):
        if "germany" not in lowered and "german" not in lowered:
            return "Curacao"
    if ("curacao goalkeeper" in lowered or "curacao defender" in lowered or "curaçao goalkeeper" in lowered) and (
        "germany" in lowered or "german" in lowered
    ):
        return "Germany"
    if ("german goalkeeper" in lowered or "germany goalkeeper" in lowered or "german defender" in lowered) and (
        "curacao" in lowered or "curaçao" in lowered
    ):
        return "Curacao"
    if "德国队" in text and ("库拉索门将" in text or "库拉索防守" in text or "库拉索后卫" in text):
        return "Germany"
    if "库拉索队" in text and ("德国门将" in text or "德国防守" in text or "德国后卫" in text):
        return "Curacao"
    if any(term in lowered for term in GERMANY_TERMS):
        return "Germany"
    if any(term in lowered for term in CURACAO_TERMS):
        return "Curacao"
    return "the attacking side"


def team_zh(team: str) -> str:
    if team == "Germany":
        return "德国队"
    if team == "Curacao":
        return "库拉索队"
    return "进攻方"


def near_goal(segment: SegmentRef, goal: VerifiedGoal, before_sec: float, after_sec: float) -> bool:
    return segment.end_sec >= goal.start_sec - before_sec and segment.start_sec <= goal.end_sec + after_sec


def choose_primary_segments(
    assertions: list[SegmentRef],
    goals: list[VerifiedGoal],
    *,
    before_sec: float,
    after_sec: float,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return event_id -> goal_id and goal_id -> primary event_id."""
    assignments: dict[str, str] = {}
    primary_by_goal: dict[str, str] = {}
    for segment in assertions:
        candidates = [goal for goal in goals if near_goal(segment, goal, before_sec, after_sec)]
        if not candidates:
            continue
        nearest = min(candidates, key=lambda goal: abs(segment.midpoint_sec - goal.midpoint_sec))
        assignments[segment.event_id] = nearest.goal_id

    for goal in goals:
        assigned = [segment for segment in assertions if assignments.get(segment.event_id) == goal.goal_id]
        if not assigned:
            continue
        # Prefer a segment whose interval overlaps the verified window, then the nearest midpoint.
        primary = min(
            assigned,
            key=lambda segment: (
                not (segment.start_sec <= goal.end_sec and segment.end_sec >= goal.start_sec),
                abs(segment.midpoint_sec - goal.midpoint_sec),
                segment.index,
            ),
        )
        primary_by_goal[goal.goal_id] = primary.event_id
    return assignments, primary_by_goal


def expected_score_state(goals: list[VerifiedGoal], timestamp_sec: float) -> dict[str, Any]:
    previous: VerifiedGoal | None = None
    upcoming: VerifiedGoal | None = None
    for goal in goals:
        if goal.end_sec <= timestamp_sec:
            previous = goal
        elif goal.start_sec > timestamp_sec and upcoming is None:
            upcoming = goal
    return {
        "score_should_be": previous.score_after if previous else "0-0",
        "previous_goal_id": previous.goal_id if previous else None,
        "next_goal_id": upcoming.goal_id if upcoming else None,
        "next_goal_window": f"{stamp(upcoming.start_sec)}-{stamp(upcoming.end_sec)}" if upcoming else None,
    }


def classify_false_positive(segment: SegmentRef, assigned_goal_id: str | None, primary_goal_id: str | None) -> str:
    if assigned_goal_id and primary_goal_id and segment.event_id != primary_goal_id:
        return "celebration_or_replay"
    if has_replay_hint(segment.text):
        return "celebration_or_replay"
    if has_shot_hint(segment.text):
        return "shot"
    return "dangerous_attack"


def rewrite_segment(segment: dict[str, Any], ref: SegmentRef, new_type: str, reason: str) -> None:
    team = infer_team(ref.text)
    zh_team = team_zh(team)
    if new_type == "celebration_or_replay":
        en = (
            f"The broadcast brings us back to that attacking sequence. {team} worked the ball into a dangerous area, "
            "and the replay angle lets us focus on the movement, the defensive recovery, and the goalkeeper's reaction."
        )
        zh = (
            f"镜头再看刚才这次攻防，{zh_team}把球推进到危险区域。这个角度更适合观察跑位、"
            "防线回收和门将的反应。"
        )
        subtitle_en = "Replay angle on the previous attack."
        subtitle_zh = "镜头再看刚才的攻防。"
    elif new_type == "shot":
        en = (
            f"{team} find a pocket of space and get the shot away under pressure. "
            "The defensive line reacts quickly, with the goalkeeper and nearby defenders staying alive to the second ball."
        )
        zh = (
            f"{zh_team}在压力下找到起脚空间，这脚打门给防线制造了不小麻烦。"
            "门将和身前防守球员都没有放松，第二落点依然很关键。"
        )
        subtitle_en = "Shot under pressure, defense reacts."
        subtitle_zh = "压力下起脚，防线迅速反应。"
    else:
        en = (
            f"{team} keep the pressure on around the penalty area. The move stretches the back line, "
            "forcing defenders to track runners and close the passing lane."
        )
        zh = (
            f"{zh_team}继续在禁区周围施压，进攻把防线拉开，迫使防守球员跟住跑动、封住传球线路。"
        )
        subtitle_en = "Pressure around the penalty area."
        subtitle_zh = "禁区周围持续施压。"

    segment["event_type"] = new_type
    segment["goal_reflection"] = {
        "status": "rewritten_false_positive",
        "reason": reason,
        "new_event_type": new_type,
        "policy": "score_change_not_allowed_without_verified_scoreboard_transition",
    }
    segment.setdefault("english", {})
    segment.setdefault("chinese", {})
    if isinstance(segment["english"], dict):
        segment["english"]["commentary_text"] = en
        segment["english"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": subtitle_en}]
    if isinstance(segment["chinese"], dict):
        segment["chinese"]["commentary_text"] = zh
        segment["chinese"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": subtitle_zh}]


def has_score_claim(text: str) -> bool:
    for match in SCORE_PATTERN.finditer(text):
        left, right = int(match.group(1)), int(match.group(2))
        if left > 10 or right > 10:
            continue
        context = text[max(0, match.start() - 80) : min(len(text), match.end() + 80)].lower()
        if any(marker in context for marker in ("formation", "阵型", "setup", "set up")):
            continue
        if any(marker in context for marker in ("score", "scoreboard", "lead", "leads", "tie", "level", "比分", "领先", "战平")):
            return True
    return False


def sanitize_non_goal_score_claim(segment: dict[str, Any], ref: SegmentRef) -> bool:
    if segment.get("event_type") == "goal" or not has_score_claim(segment_text(segment)):
        return False
    event_type = str(segment.get("event_type", "other_relevant"))
    if event_type == "substitution":
        en = "The broadcast cuts to the touchline for a substitution sequence, with the fourth official and players preparing for the change."
        zh = "转播镜头切到场边换人调整，第四官员举牌，球员在边线旁等待完成这次人员变化。"
        subtitle_en = "Substitution sequence."
        subtitle_zh = "换人调整。"
    elif event_type == "period_transition":
        en = "The game moves through a short transition phase as players reset positions and the broadcast re-establishes the field."
        zh = "比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。"
        subtitle_en = "Transition phase as play resets."
        subtitle_zh = "阶段转换，比赛重新组织。"
    elif event_type == "celebration_or_replay":
        en = "The broadcast shows reaction and replay context from the previous passage of play, bringing the key movement back into focus."
        zh = "转播正在展示上一段攻防后的反应和回放，把关键跑动和处理细节重新带回视野。"
        subtitle_en = "Reaction or replay context."
        subtitle_zh = "反应或回放背景。"
    else:
        en = "The broadcast stays with the reset around the pitch, showing player organization and the rhythm before play builds again."
        zh = "转播继续交代场上的重新组织，球员站位和比赛节奏正在重新铺开。"
        subtitle_en = "Context during a reset."
        subtitle_zh = "重新组织阶段的背景画面。"

    segment.setdefault("english", {})
    segment.setdefault("chinese", {})
    if isinstance(segment["english"], dict):
        segment["english"]["commentary_text"] = en
        segment["english"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": subtitle_en}]
    if isinstance(segment["chinese"], dict):
        segment["chinese"]["commentary_text"] = zh
        segment["chinese"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": subtitle_zh}]
    segment.setdefault("goal_reflection", {})
    segment["goal_reflection"]["score_claim_sanitized"] = True
    return True


def sanitize_forbidden_entity(segment: dict[str, Any], ref: SegmentRef) -> bool:
    text = segment_text(segment)
    lowered = text.lower()
    if not any(entity in lowered for entity in FORBIDDEN_ENTITIES):
        return False
    en = (
        "The broadcast takes us inside the officials' setup and the video-review room, a useful glimpse of the support team "
        "working behind the match."
    )
    zh = "转播镜头给到裁判组和视频复核室，这是比赛背后执法支持团队的一次亮相。"
    segment.setdefault("english", {})
    segment.setdefault("chinese", {})
    if isinstance(segment["english"], dict):
        segment["english"]["commentary_text"] = en
        segment["english"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": "Officials and review-room background."}]
    if isinstance(segment["chinese"], dict):
        segment["chinese"]["commentary_text"] = zh
        segment["chinese"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": "裁判组与视频复核背景。"}]
    segment.setdefault("goal_reflection", {})
    segment["goal_reflection"]["forbidden_entity_sanitized"] = True
    return True


def sanitize_prematch_action(segment: dict[str, Any], ref: SegmentRef, kickoff_sec: float) -> bool:
    if ref.start_sec >= kickoff_sec or str(segment.get("event_type", "")) not in ACTION_TYPES:
        return False
    segment["event_type"] = "period_transition"
    en = (
        "Before kickoff, the camera stays with the players as they gather, settle their shape, and prepare for the opening whistle."
    )
    zh = "开球前，镜头继续跟随球员集结和调整站位，双方都在等待开场哨响。"
    segment.setdefault("english", {})
    segment.setdefault("chinese", {})
    if isinstance(segment["english"], dict):
        segment["english"]["commentary_text"] = en
        segment["english"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": "Pre-match organization before kickoff."}]
    if isinstance(segment["chinese"], dict):
        segment["chinese"]["commentary_text"] = zh
        segment["chinese"]["subtitle_lines"] = [{"start_sec": ref.start_sec, "end_sec": ref.end_sec, "text": "开球前的赛前组织。"}]
    segment.setdefault("goal_reflection", {})
    segment["goal_reflection"]["prematch_action_sanitized"] = True
    return True


def mark_true_goal(segment: dict[str, Any], ref: SegmentRef, goal: VerifiedGoal) -> None:
    segment["event_type"] = "goal"
    segment["goal_reflection"] = {
        "status": "verified_primary_goal",
        "goal_id": goal.goal_id,
        "score_change": f"{goal.score_before} -> {goal.score_after}",
        "verified_window": f"{stamp(goal.start_sec)}-{stamp(goal.end_sec)}",
        "match_clock": goal.match_clock,
    }


def load_event_context(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in data.get("events", []) if isinstance(item, dict)]


def nearby_event_context(events: list[dict[str, Any]], ref: SegmentRef, limit: int = 2) -> list[dict[str, Any]]:
    ranked = sorted(
        events,
        key=lambda item: abs(((float(item.get("start_sec", 0.0)) + float(item.get("end_sec", 0.0))) / 2.0) - ref.midpoint_sec),
    )
    compact: list[dict[str, Any]] = []
    for item in ranked[:limit]:
        compact.append(
            {
                "event_id": item.get("event_id"),
                "event_type": item.get("event_type"),
                "start_sec": item.get("start_sec"),
                "end_sec": item.get("end_sec"),
                "evidence_frames": item.get("evidence_frames", [])[:6],
                "evidence_summary": str(item.get("evidence_summary", ""))[:500],
            }
        )
    return compact


def call_api_review(
    suspect: dict[str, Any],
    *,
    frame_root: Path | None,
    timeout: int,
) -> dict[str, Any]:
    """Optional Intern-S2 review. Safe to skip when API/network is unavailable."""
    try:
        from intern_client import InternClient, image_source_to_url
    except Exception as exc:  # pragma: no cover - optional runtime path
        return {"status": "api_unavailable", "error": str(exc)}

    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "You are verifying a football commentary segment after generation. "
                "Decide whether the segment is a live goal, replay/aftermath, shot, dangerous attack, or no_event. "
                "Return strict JSON with keys: decision, confidence, evidence, rewrite_hint. "
                "Do not invent player names. Segment data:\n"
                + json.dumps(suspect, ensure_ascii=False)
            ),
        }
    ]
    if frame_root:
        for context in suspect.get("event_context", []):
            for frame_id in context.get("evidence_frames", [])[:4]:
                frame_path = frame_root / f"{frame_id}.jpg"
                if frame_path.exists():
                    content.append({"type": "image_url", "image_url": {"url": image_source_to_url(str(frame_path))}})
    try:
        client = InternClient(timeout=timeout)
        response = client.chat(
            [{"role": "user", "content": content}],
            temperature=0.0,
            top_p=0.8,
            max_tokens=600,
            thinking_mode=False,
        )
        text = client.text_from_response(response)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {"raw_text": text}
        return {"status": "ok", "review": parsed}
    except Exception as exc:  # pragma: no cover - depends on external API
        return {"status": "api_error", "error": str(exc)}


def run_api_reviews(
    suspects: list[dict[str, Any]],
    *,
    api_mode: str,
    frame_root: Path | None,
    max_api_calls: int,
    api_concurrency: int,
    timeout: int,
) -> dict[str, dict[str, Any]]:
    if api_mode == "off" or max_api_calls <= 0:
        return {}
    selected = suspects[:max_api_calls]
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, api_concurrency)) as pool:
        future_map = {
            pool.submit(call_api_review, suspect, frame_root=frame_root, timeout=timeout): str(suspect["event_id"])
            for suspect in selected
        }
        for future in as_completed(future_map):
            results[future_map[future]] = future.result()
    return results


def reflect_commentary(
    input_path: Path,
    events_path: Path,
    manual_review_path: Path,
    *,
    before_sec: float,
    after_sec: float,
    api_mode: str,
    frame_root: Path | None,
    max_api_calls: int,
    api_concurrency: int,
    api_timeout: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output = deepcopy(data)
    goals = load_verified_goals(manual_review_path)
    refs = load_segments(data)
    assertions = [ref for ref in refs if has_goal_assertion(ref)]
    assignments, primary_by_goal = choose_primary_segments(assertions, goals, before_sec=before_sec, after_sec=after_sec)
    goal_by_id = {goal.goal_id: goal for goal in goals}
    primary_event_ids = set(primary_by_goal.values())
    events = load_event_context(events_path)

    changes: list[dict[str, Any]] = []
    suspects: list[dict[str, Any]] = []
    verified: list[dict[str, Any]] = []
    score_sanitized: list[dict[str, Any]] = []
    entity_sanitized: list[dict[str, Any]] = []
    prematch_sanitized: list[dict[str, Any]] = []
    for ref in refs:
        if not has_goal_assertion(ref):
            continue
        segment = output["segments"][ref.index]
        assigned_goal_id = assignments.get(ref.event_id)
        if ref.event_id in primary_event_ids and assigned_goal_id:
            goal = goal_by_id[assigned_goal_id]
            mark_true_goal(segment, ref, goal)
            verified.append(
                {
                    "event_id": ref.event_id,
                    "goal_id": goal.goal_id,
                    "time": f"{stamp(ref.start_sec)}-{stamp(ref.end_sec)}",
                    "score_change": f"{goal.score_before} -> {goal.score_after}",
                }
            )
            continue

        new_type = classify_false_positive(ref, assigned_goal_id, primary_by_goal.get(assigned_goal_id or ""))
        reason = "duplicate_or_replay_near_verified_goal" if assigned_goal_id else "not_near_verified_score_change"
        if ref.event_type == "goal" or any(re.search(pattern, ref.text, re.I) for pattern in GOAL_PATTERNS):
            rewrite_segment(segment, ref, new_type, reason)
            state = expected_score_state(goals, ref.midpoint_sec)
            change = {
                "event_id": ref.event_id,
                "time": f"{stamp(ref.start_sec)}-{stamp(ref.end_sec)}",
                "old_event_type": ref.event_type,
                "new_event_type": new_type,
                "reason": reason,
                "assigned_goal_id": assigned_goal_id,
                "expected_score_state": state,
                "excerpt_before": ref.text.replace("\n", " / ")[:220],
            }
            changes.append(change)
            suspects.append({**change, "event_context": nearby_event_context(events, ref)})

    refreshed_refs = load_segments(output)
    for ref in refreshed_refs:
        segment = output["segments"][ref.index]
        if sanitize_forbidden_entity(segment, ref):
            entity_sanitized.append(
                {
                    "event_id": ref.event_id,
                    "time": f"{stamp(ref.start_sec)}-{stamp(ref.end_sec)}",
                    "event_type": segment.get("event_type"),
                    "reason": "forbidden_entity_removed",
                }
            )
    refreshed_refs = load_segments(output)
    for ref in refreshed_refs:
        segment = output["segments"][ref.index]
        if sanitize_prematch_action(segment, ref, kickoff_sec=552.0):
            prematch_sanitized.append(
                {
                    "event_id": ref.event_id,
                    "time": f"{stamp(ref.start_sec)}-{stamp(ref.end_sec)}",
                    "event_type": segment.get("event_type"),
                    "reason": "prematch_action_recast_as_context",
                }
            )
    refreshed_refs = load_segments(output)
    for ref in refreshed_refs:
        segment = output["segments"][ref.index]
        if sanitize_non_goal_score_claim(segment, ref):
            score_sanitized.append(
                {
                    "event_id": ref.event_id,
                    "time": f"{stamp(ref.start_sec)}-{stamp(ref.end_sec)}",
                    "event_type": segment.get("event_type"),
                    "reason": "non_goal_segment_should_not_repeat_numeric_score",
                }
            )

    api_reviews = run_api_reviews(
        suspects,
        api_mode=api_mode,
        frame_root=frame_root,
        max_api_calls=max_api_calls,
        api_concurrency=api_concurrency,
        timeout=api_timeout,
    )
    for segment in output.get("segments", []):
        event_id = str(segment.get("event_id", ""))
        if event_id in api_reviews:
            segment.setdefault("goal_reflection", {})
            segment["goal_reflection"]["api_review"] = api_reviews[event_id]

    report = {
        "policy": "Post-generation verification. Deterministic scoreboard-state corrections are used for output triage; optional Intern-S2 API reviews can be attached as evidence.",
        "input": input_path.name,
        "events": events_path.name if events_path.exists() else None,
        "manual_review": manual_review_path.name,
        "parameters": {
            "before_sec": before_sec,
            "after_sec": after_sec,
            "api_mode": api_mode,
            "max_api_calls": max_api_calls,
            "api_concurrency": api_concurrency,
        },
        "summary": {
            "segments": len(refs),
            "verified_score_changes": len(goals),
            "goal_assertion_segments_before": len(assertions),
            "primary_verified_goal_segments": len(verified),
            "rewritten_false_positive_segments": len(changes),
            "sanitized_non_goal_score_claim_segments": len(score_sanitized),
            "sanitized_forbidden_entity_segments": len(entity_sanitized),
            "sanitized_prematch_action_segments": len(prematch_sanitized),
            "api_review_segments": len(api_reviews),
            "remaining_goal_type_segments": sum(1 for item in output.get("segments", []) if item.get("event_type") == "goal"),
        },
        "verified_primary_goals": verified,
        "changes": changes,
        "score_claim_sanitized": score_sanitized,
        "forbidden_entity_sanitized": entity_sanitized,
        "prematch_action_sanitized": prematch_sanitized,
        "api_reviews": api_reviews,
    }
    return output, report


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Night Goal Reflection Report / Night 进球反思后处理报告",
        "",
        "EN: This report is produced after full commentary generation. It rewrites unverified goal claims into replay, shot, or dangerous-attack commentary.",
        "",
        "ZH: 本报告在完整解说生成之后产出，将未核验的进球宣称改写为回放、射门或危险进攻解说。",
        "",
        "## Summary / 摘要",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Verified Primary Goals / 保留的真实进球片段",
            "",
            "| Event | Goal | Time | Score Change |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["verified_primary_goals"]:
        lines.append(f"| {row['event_id']} | {row['goal_id']} | `{row['time']}` | {row['score_change']} |")
    if not report["verified_primary_goals"]:
        lines.append("| - | - | - | - |")
    lines.extend(
        [
            "",
            "## Rewritten False Positives / 已改写误判进球",
            "",
            "| Event | Time | Old Type | New Type | Reason | Expected Score | Excerpt |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["changes"][:80]:
        state = row["expected_score_state"]
        lines.append(
            f"| {row['event_id']} | `{row['time']}` | {row['old_event_type']} | {row['new_event_type']} | "
            f"{row['reason']} | {state['score_should_be']} | {row['excerpt_before'].replace('|', '/')} |"
        )
    if not report["changes"]:
        lines.append("| - | - | - | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Sanitized Non-Goal Score Claims / 已清洗非进球数字比分片段",
            "",
            "| Event | Time | Type | Reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["score_claim_sanitized"][:80]:
        lines.append(f"| {row['event_id']} | `{row['time']}` | {row['event_type']} | {row['reason']} |")
    if not report["score_claim_sanitized"]:
        lines.append("| - | - | - | - |")
    lines.extend(
        [
            "",
            "## Other Safety Sanitizers / 其他安全清洗",
            "",
            f"- `forbidden_entity_sanitized`: {len(report['forbidden_entity_sanitized'])}",
            f"- `prematch_action_sanitized`: {len(report['prematch_action_sanitized'])}",
        ]
    )
    lines.extend(
        [
            "",
            "## API Hook / API 接口",
            "",
            f"- `api_mode`: {report['parameters']['api_mode']}",
            f"- `api_review_segments`: {summary['api_review_segments']}",
            "EN: Use `--api-mode review --frame-root <frames>` to attach Intern-S2 visual reflection evidence to selected suspect segments.",
            "ZH: 使用 `--api-mode review --frame-root <frames>` 可以让 Intern-S2 对选中的可疑片段追加视觉反思证据。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reflect and correct generated goal claims after commentary generation.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--manual-review", type=Path, default=DEFAULT_MANUAL_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--before-sec", type=float, default=45.0)
    parser.add_argument("--after-sec", type=float, default=90.0)
    parser.add_argument("--api-mode", choices=["off", "review"], default="off")
    parser.add_argument("--frame-root", type=Path, default=None)
    parser.add_argument("--max-api-calls", type=int, default=0)
    parser.add_argument("--api-concurrency", type=int, default=2)
    parser.add_argument("--api-timeout", type=int, default=120)
    args = parser.parse_args(argv)

    output, report = reflect_commentary(
        args.input,
        args.events,
        args.manual_review,
        before_sec=args.before_sec,
        after_sec=args.after_sec,
        api_mode=args.api_mode,
        frame_root=args.frame_root,
        max_api_calls=args.max_api_calls,
        api_concurrency=args.api_concurrency,
        api_timeout=args.api_timeout,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.report_md)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
