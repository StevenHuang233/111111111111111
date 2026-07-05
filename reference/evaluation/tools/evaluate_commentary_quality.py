#!/usr/bin/env python
"""Evaluate football commentary output quality.

This is an evaluation-only tool. It is safe to use public references here, but
those references must not be injected into the target visual commentary agent as
hidden context.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual.json"
DEFAULT_FACTS = REPO_ROOT / "reference" / "evaluation" / "germany_curacao_public_reference.json"
DEFAULT_MANUAL_REVIEW = REPO_ROOT / "reference" / "evaluation" / "goal_scoreboard_manual_review.md"
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "commentary_quality_eval.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "commentary_quality_eval.md"

ACTION_TYPES = {"goal", "shot", "save", "foul", "card", "corner", "free_kick", "dangerous_attack", "var_review"}
GOAL_TYPES = {"goal"}
REPLAY_MARKERS = ("replay", "slow motion", "slow-motion", "回放", "慢镜头", "FIFA")
COLOR_STYLE_PATTERNS = (
    r"\bplayer in white\b",
    r"\bplayer in blue\b",
    r"\bwhite-shirted\b",
    r"\bblue-shirted\b",
    r"\bwhite jersey\b",
    r"\bblue jersey\b",
    r"\bgreen goalkeeper\b",
    r"身穿白色",
    r"身穿蓝色",
    r"白衣球员",
    r"蓝衣",
    r"绿衣门将",
)
OPENING_BACKGROUND_TERMS = (
    "lineup",
    "mascot",
    "child",
    "children",
    "referee",
    "official",
    "anthem",
    "入场",
    "列队",
    "球童",
    "吉祥物",
    "裁判",
    "国歌",
)
HUMAN_REVIEW_NOTES = [
    {
        "area": "Opening background",
        "en": "Opening and entrance shots should introduce the match, teams, and visible ceremony context when evidence is available.",
        "zh": "入场和开场画面应在证据充分时适当介绍比赛、球队和可见仪式背景。",
    },
    {
        "area": "Role distinction",
        "en": "Distinguish mascots, player escorts, referees, assistant referees, fourth officials, and VAR-room officials instead of collapsing them into one role.",
        "zh": "区分吉祥物、球童、主裁、边裁、第四官员和视频助理裁判，不能混成一个角色。",
    },
    {
        "area": "Broadcast graphics as knowledge",
        "en": "Lineup, referee, shirt number, kit color, and goalkeeper color graphics can enrich background facts, but must remain uncertain when substitutions or unclear shots break the mapping.",
        "zh": "球员列表、裁判信息、号码、队服颜色和门将颜色可作为背景知识，但替补和模糊画面会破坏对应关系，必须保留不确定性。",
    },
    {
        "area": "Phase awareness",
        "en": "Before kickoff, entrance, lineup, anthem, ceremony, and broadcast graphics are context phases, not fouls, restarts, or repeated kickoffs.",
        "zh": "开球前的入场、列队、国歌、仪式和转播图表属于背景阶段，不应识别为犯规、任意球或重复开球。",
    },
    {
        "area": "Commentary conversion",
        "en": "Raw visual descriptions are not always playable commentary; color/position observations should be converted into natural broadcast wording.",
        "zh": "原始画面描述不一定能直接当解说词；颜色、位置等观察应转换为自然的解说表达。",
    },
    {
        "area": "Fact verification",
        "en": "Names, teams, scores, referees, and event results must be organized as facts with evidence status instead of being asserted from weak visual guesses.",
        "zh": "姓名、球队、比分、裁判和事件结果应整理为带证据状态的事实，而不是从弱视觉猜测中直接断言。",
    },
]
LOWERCASE_ENGLISH_TOKEN = re.compile(r"\b[a-z]{4,}\b")
SCORE_PATTERN = re.compile(r"(?<!\d)(\d{1,2})\s*(?:-|:|：|比)\s*(\d{1,2})(?!\d)")


@dataclass(frozen=True)
class Segment:
    event_id: str
    event_type: str
    start_sec: float
    end_sec: float
    english: str
    chinese: str


def load_segments(path: Path) -> list[Segment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = []
    for item in data.get("segments", []):
        if not isinstance(item, dict):
            continue
        english = item.get("english", {})
        chinese = item.get("chinese", {})
        segments.append(
            Segment(
                event_id=str(item.get("event_id", "")),
                event_type=str(item.get("event_type", "")),
                start_sec=float(item.get("talk_start_sec", 0.0)),
                end_sec=float(item.get("talk_end_sec", 0.0)),
                english=str(english.get("commentary_text", "")) if isinstance(english, dict) else "",
                chinese=str(chinese.get("commentary_text", "")) if isinstance(chinese, dict) else "",
            )
        )
    return segments


def load_verified_goal_count(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| G") and "->" in line:
            count += 1
    return count


def text_of(segment: Segment) -> str:
    return f"{segment.english}\n{segment.chinese}".strip()


def stamp(seconds: float) -> str:
    value = max(0, int(round(seconds)))
    minutes, sec = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def excerpt(text: str, limit: int = 180) -> str:
    return text.replace("\n", " / ").replace("|", "/")[:limit]


def score_claims(text: str) -> list[str]:
    claims: list[str] = []
    lowered = text.lower()
    for match in SCORE_PATTERN.finditer(text):
        left, right = int(match.group(1)), int(match.group(2))
        if left > 10 or right > 10:
            continue
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 80)
        context = text[start:end].lower()
        if any(marker in context for marker in ("formation", "阵型", "setup", "set up")):
            continue
        if any(marker in context for marker in ("score", "scoreboard", "lead", "leads", "makes it", "updates", "比分", "领先", "扩大")):
            claims.append(match.group(0).replace(" ", ""))
    return claims


def find_flags(segments: list[Segment], facts: dict[str, Any], kickoff_sec: float) -> dict[str, list[dict[str, Any]]]:
    wrong_entities = [str(item).lower() for item in facts.get("forbidden_wrong_entities_for_this_match", [])]
    known_names = set(str(item) for item in facts.get("known_participant_names", []))
    style_red_flags = [str(item).lower() for item in facts.get("style_red_flags", [])]
    flags: dict[str, list[dict[str, Any]]] = {
        "goal_overcount": [],
        "score_claim": [],
        "wrong_entity": [],
        "style_color_identity": [],
        "prematch_action": [],
        "unsupported_name": [],
        "mixed_language": [],
        "replay_goal_risk": [],
    }

    for segment in segments:
        text = text_of(segment)
        lowered = text.lower()
        row = {
            "event_id": segment.event_id,
            "event_type": segment.event_type,
            "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
            "excerpt": excerpt(text),
        }

        claims = score_claims(text)
        if claims:
            flags["score_claim"].append({**row, "claims": claims})

        for entity in wrong_entities:
            if entity and entity in lowered:
                flags["wrong_entity"].append({**row, "entity": entity})
                break

        if any(re.search(pattern, text, re.I) for pattern in COLOR_STYLE_PATTERNS) or any(
            marker and marker in lowered for marker in style_red_flags
        ):
            flags["style_color_identity"].append(row)

        if segment.start_sec < kickoff_sec and segment.event_type in ACTION_TYPES:
            flags["prematch_action"].append(row)

        if segment.event_type == "goal" and any(marker.lower() in lowered for marker in REPLAY_MARKERS):
            flags["replay_goal_risk"].append(row)

        for name in re.findall(r"\b[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+(?:\s+[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+)?\b", segment.english):
            if name in {"Germany", "German", "Curaçao", "Curacao", "FIFA", "VAR", "World Cup", "Goal"}:
                continue
            if name not in known_names and name in {"Ibragimov", "Nkunku", "Müller", "Colombia", "Colombian"}:
                flags["unsupported_name"].append({**row, "name": name})
                break

        chinese_lower = segment.chinese.lower()
        latin_tokens = [
            token
            for token in LOWERCASE_ENGLISH_TOKEN.findall(chinese_lower)
            if token not in {"fifa", "var", "curacao", "havertz", "wirtz", "sane", "musiala", "gnabry"}
        ]
        if latin_tokens:
            flags["mixed_language"].append({**row, "tokens": sorted(set(latin_tokens))[:5]})

    return flags


def opening_background_score(segments: list[Segment], kickoff_sec: float) -> dict[str, Any]:
    opening_segments = [segment for segment in segments if segment.start_sec < kickoff_sec]
    text = "\n".join(text_of(segment) for segment in opening_segments)
    hits = sorted({term for term in OPENING_BACKGROUND_TERMS if term.lower() in text.lower()})
    return {
        "opening_segment_count": len(opening_segments),
        "background_terms_found": hits,
        "has_basic_opening_context": bool({"lineup", "入场", "列队"} & set(hits)) or len(hits) >= 3,
        "needs_official_child_mascot_distinction": not ({"referee", "official", "裁判"} & set(hits)),
    }


def build_report(
    segments: list[Segment],
    facts: dict[str, Any],
    verified_goal_count: int,
    kickoff_sec: float,
) -> dict[str, Any]:
    counts = Counter(segment.event_type for segment in segments)
    flags = find_flags(segments, facts, kickoff_sec)
    goal_count = counts.get("goal", 0)
    goal_overcount = max(0, goal_count - verified_goal_count) if verified_goal_count else 0
    summary = {
        "segment_count": len(segments),
        "event_type_counts": dict(counts),
        "generated_goal_count": goal_count,
        "verified_goal_count": verified_goal_count,
        "goal_overcount": goal_overcount,
        "score_claim_segments": len(flags["score_claim"]),
        "wrong_entity_segments": len(flags["wrong_entity"]),
        "style_color_identity_segments": len(flags["style_color_identity"]),
        "prematch_action_segments": len(flags["prematch_action"]),
        "unsupported_name_segments": len(flags["unsupported_name"]),
        "mixed_language_segments": len(flags["mixed_language"]),
        "replay_goal_risk_segments": len(flags["replay_goal_risk"]),
    }
    return {
        "policy": "Evaluation-only. Public facts and manual reviews must not be injected as hidden target-agent context.",
        "summary": summary,
        "quality_gate": quality_gate(summary),
        "opening_background": opening_background_score(segments, kickoff_sec),
        "flags": flags,
        "human_review_notes": HUMAN_REVIEW_NOTES,
        "recommendations": recommendations(summary),
    }


def quality_gate(summary: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if summary["wrong_entity_segments"] > 0:
        blockers.append("wrong_entity_segments")
    if summary["goal_overcount"] > 0:
        blockers.append("goal_overcount")
    if summary["score_claim_segments"] > summary["verified_goal_count"] + 6:
        blockers.append("score_claim_segments")
    if summary["style_color_identity_segments"] > 20:
        warnings.append("style_color_identity_segments")
    if summary["mixed_language_segments"] > 0:
        warnings.append("mixed_language_segments")
    if summary["prematch_action_segments"] > 0:
        warnings.append("prematch_action_segments")
    return {
        "status": "fail" if blockers else "pass_with_warnings" if warnings else "pass",
        "blockers": blockers,
        "warnings": warnings,
        "en": "Fail means the output should not be used as the final demo script without review.",
        "zh": "fail 表示该输出不应未经复核直接作为最终 demo 解说稿。",
    }


def recommendations(summary: dict[str, Any]) -> list[dict[str, str]]:
    items = [
        {
            "priority": "Must",
            "area": "Output audit gate",
            "en": "Reject or manually review any final output with wrong teams, excessive goal count, or unverified score-changing claims.",
            "zh": "最终输出若出现错误球队、进球数明显过多、未经验证的比分变化，应拒绝或转人工复核。",
        },
        {
            "priority": "Must",
            "area": "Goal score-state verifier",
            "en": "A goal claim must be supported by live scoring evidence plus a previous/post scoreboard state, or remain pending/uncertain.",
            "zh": "进球宣称必须有现场进球证据和前后比分牌状态支撑，否则保持 pending/uncertain。",
        },
        {
            "priority": "Must",
            "area": "Wrong-entity guard",
            "en": "Hard-block team names outside Germany and Curacao for this match unless they appear in explicit broadcast metadata.",
            "zh": "本场应硬性禁止德国、库拉索以外的球队名，除非它们出现在明确转播元数据中。",
        },
        {
            "priority": "Should",
            "area": "Identity wording",
            "en": "Use team, role, jersey number, or verified name; avoid default color-shirt subjects.",
            "zh": "优先使用球队、角色、号码或已验证姓名，不要默认用球衣颜色当主语。",
        },
        {
            "priority": "Should",
            "area": "Opening phase classifier",
            "en": "Before kickoff, classify entrance, lineup, anthem, officials, mascots/children, and broadcast graphics as context, not fouls or restarts.",
            "zh": "开球前应识别入场、列队、国歌、裁判、球童/吉祥物和转播图表为背景，不应误判为犯规或重复开球。",
        },
        {
            "priority": "Could",
            "area": "Final Chinese polish",
            "en": "Run a lightweight Chinese linter to remove mixed English fragments and template-like wording.",
            "zh": "增加轻量中文润色检查，去除英文残留和模板化表达。",
        },
        {
            "priority": "Could",
            "area": "Fact registry",
            "en": "Store extracted facts with source, confidence, validity window, and evidence frame IDs so later commentary can cite or avoid them.",
            "zh": "将抽取事实按来源、置信度、有效时间段和证据帧记录，便于后续解说引用或规避。",
        },
    ]
    return items


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Commentary Quality Evaluation / 解说质量评测",
        "",
        "EN: This report evaluates generated commentary quality. It is an evaluation artifact, not target-agent hidden context.",
        "",
        "ZH: 本报告用于评估生成解说质量，是评测产物，不是目标 Agent 的隐藏上下文。",
        "",
        "## Metrics / 指标",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    gate = report["quality_gate"]
    lines.extend(
        [
            "",
            "## Quality Gate / 质量门禁",
            "",
            f"- `status`: {gate['status']}",
            f"- `blockers`: {', '.join(gate['blockers']) or '-'}",
            f"- `warnings`: {', '.join(gate['warnings']) or '-'}",
            f"- EN: {gate['en']}",
            f"- ZH: {gate['zh']}",
        ]
    )
    opening = report["opening_background"]
    lines.extend(
        [
            "",
            "## Opening Context / 开场阶段",
            "",
            f"- `opening_segment_count`: {opening['opening_segment_count']}",
            f"- `background_terms_found`: {', '.join(opening['background_terms_found']) or '-'}",
            f"- `has_basic_opening_context`: {opening['has_basic_opening_context']}",
            f"- `needs_official_child_mascot_distinction`: {opening['needs_official_child_mascot_distinction']}",
            "",
            "## Human Review Notes / 人工补充观察",
            "",
            "| Area | EN | ZH |",
            "| --- | --- | --- |",
        ]
    )
    for note in report["human_review_notes"]:
        lines.append(f"| {note['area']} | {note['en']} | {note['zh']} |")
    lines.extend(
        [
            "",
            "## Issue Samples / 问题样例",
            "",
        ]
    )
    sample_sections = [
        ("wrong_entity", "Wrong entity / 错误球队或实体"),
        ("prematch_action", "Prematch action misclassification / 开球前动作误判"),
        ("style_color_identity", "Color-based identity wording / 颜色式身份描述"),
        ("replay_goal_risk", "Replay-goal risk / 回放误判进球风险"),
        ("unsupported_name", "Unsupported named fact / 无依据人名"),
        ("mixed_language", "Mixed-language Chinese / 中文夹杂英文"),
        ("score_claim", "Score claim / 比分声明"),
    ]
    for key, title in sample_sections:
        rows = report["flags"].get(key, [])
        lines.extend([f"### {title}", "", "| Event | Type | Time | Excerpt |", "| --- | --- | --- | --- |"])
        for row in rows[:8]:
            lines.append(f"| {row['event_id']} | {row['event_type']} | `{row['time']}` | {row['excerpt']} |")
        if not rows:
            lines.append("| - | - | - | - |")
        lines.append("")

    lines.extend(["## Recommendations / 建设性建议", "", "| Priority | Area | EN | ZH |", "| --- | --- | --- | --- |"])
    for item in report["recommendations"]:
        lines.append(f"| {item['priority']} | {item['area']} | {item['en']} | {item['zh']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate_commentary_quality(
    input_path: str | Path = DEFAULT_INPUT,
    facts_path: str | Path = DEFAULT_FACTS,
    manual_review_path: str | Path = DEFAULT_MANUAL_REVIEW,
    kickoff_sec: float = 552.0,
) -> dict[str, Any]:
    """Python API for tests or external reviewers."""
    segments = load_segments(Path(input_path))
    facts = json.loads(Path(facts_path).read_text(encoding="utf-8"))
    verified_goal_count = load_verified_goal_count(Path(manual_review_path))
    return build_report(segments, facts, verified_goal_count, kickoff_sec)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate generated football commentary quality.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    parser.add_argument("--manual-review", type=Path, default=DEFAULT_MANUAL_REVIEW)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--kickoff-sec", type=float, default=552.0)
    args = parser.parse_args()

    report = evaluate_commentary_quality(args.input, args.facts, args.manual_review, args.kickoff_sec)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
