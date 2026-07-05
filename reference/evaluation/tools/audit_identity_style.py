#!/usr/bin/env python
"""Audit identity wording and broadcast style in generated commentary.

Evaluation-only. This script checks whether final commentary sounds like a
human broadcast script rather than raw visual descriptions. It may use
evaluation references, but those references must not be injected into the
target visual commentary agent as hidden context.
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
DEFAULT_JSON = REPO_ROOT / "reference" / "evaluation" / "identity_style_audit.json"
DEFAULT_MD = REPO_ROOT / "reference" / "evaluation" / "identity_style_audit.md"

COLOR_IDENTITY_PATTERNS = (
    r"\bplayer in white\b",
    r"\bplayer in blue\b",
    r"\bplayer in (?:the )?(?:green|orange|yellow|black) jersey\b",
    r"\bwhite-shirted\b",
    r"\bblue-shirted\b",
    r"\bwhite-jerseyed\b",
    r"\bblue-jerseyed\b",
    r"\bwhite jersey\b",
    r"\bblue jersey\b",
    r"\bgreen goalkeeper\b",
    r"\borange goalkeeper\b",
    r"\bteam in blue\b",
    r"\bteam in white\b",
    r"\bblue team\b",
    r"\bwhite team\b",
    r"身穿白色",
    r"身穿蓝色",
    r"身穿绿色",
    r"身穿橙色",
    r"白衣球员",
    r"蓝衣球员",
    r"蓝衣",
    r"白衣",
    r"绿衣门将",
    r"橙衣门将",
    r"蓝队",
    r"白队",
)
TEAM_IDENTITY_PATTERNS = (
    r"\bGermany\b",
    r"\bGerman\b",
    r"\bCura(?:ç|c)ao\b",
    r"德国",
    r"库拉索",
)
JERSEY_NUMBER_PATTERNS = (
    r"\bnumber\s+\d{1,2}\b",
    r"#\d{1,2}\b",
    r"\d{1,2}号",
)
ROLE_PATTERNS = (
    r"\bgoalkeeper\b",
    r"\bdefender\b",
    r"\battacker\b",
    r"\bmidfielder\b",
    r"\breferee\b",
    r"\bassistant referee\b",
    r"\bofficial\b",
    r"门将",
    r"后卫",
    r"进攻球员",
    r"防守球员",
    r"裁判",
    r"边裁",
    r"球童",
    r"吉祥物",
)
RAW_VISUAL_PATTERNS = (
    r"\bwe see\b",
    r"\bthe camera (?:shows|cuts|lingers)\b",
    r"\bis shown\b",
    r"\bvisible\b",
    r"\bin the frame\b",
    r"\bclose-up\b",
    r"镜头",
    r"画面",
    r"特写",
    r"可以看到",
    r"显示",
)
ALLOWED_GENERIC_NAMES = {
    "Germany",
    "German",
    "Curaçao",
    "Curacao",
    "FIFA",
    "VAR",
    "World Cup",
    "Goal",
    "The",
    "And",
    "In",
    "At",
}


@dataclass(frozen=True)
class Segment:
    event_id: str
    event_type: str
    start_sec: float
    end_sec: float
    english: str
    chinese: str

    @property
    def text(self) -> str:
        return f"{self.english}\n{self.chinese}".strip()


def stamp(seconds: float) -> str:
    value = max(0, int(round(seconds)))
    minutes, sec = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def excerpt(text: str, limit: int = 180) -> str:
    return text.replace("\n", " / ").replace("|", "/")[:limit]


def load_segments(path: Path) -> list[Segment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments: list[Segment] = []
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


def pattern_hits(text: str, patterns: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, re.I):
            hits.append(pattern)
    return hits


def named_entities(text: str) -> list[str]:
    names = []
    for match in re.finditer(r"\b[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+(?:\s+[A-Z][A-Za-zÀ-ÿćovićşçãéüöäß]+)?\b", text):
        name = match.group(0)
        if name not in ALLOWED_GENERIC_NAMES:
            names.append(name)
    return names


def classify_segments(segments: list[Segment], facts: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    known_names = {str(item) for item in facts.get("known_participant_names", [])}
    forbidden_entities = [str(item).lower() for item in facts.get("forbidden_wrong_entities_for_this_match", [])]
    buckets: dict[str, list[dict[str, Any]]] = {
        "color_identity": [],
        "team_identity": [],
        "number_identity": [],
        "role_identity": [],
        "raw_visual": [],
        "unsupported_name": [],
        "wrong_entity": [],
    }
    for segment in segments:
        text = segment.text
        lowered = text.lower()
        row = {
            "event_id": segment.event_id,
            "event_type": segment.event_type,
            "time": f"{stamp(segment.start_sec)}-{stamp(segment.end_sec)}",
            "excerpt": excerpt(text),
        }

        color_hits = pattern_hits(text, COLOR_IDENTITY_PATTERNS)
        if color_hits:
            buckets["color_identity"].append({**row, "patterns": color_hits})
        if pattern_hits(text, TEAM_IDENTITY_PATTERNS):
            buckets["team_identity"].append(row)
        if pattern_hits(text, JERSEY_NUMBER_PATTERNS):
            buckets["number_identity"].append(row)
        if pattern_hits(text, ROLE_PATTERNS):
            buckets["role_identity"].append(row)
        raw_hits = pattern_hits(text, RAW_VISUAL_PATTERNS)
        if raw_hits:
            buckets["raw_visual"].append({**row, "patterns": raw_hits})

        for entity in forbidden_entities:
            if entity and entity in lowered:
                buckets["wrong_entity"].append({**row, "entity": entity})
                break

        for name in named_entities(segment.english):
            if name not in known_names and name in {"Ibragimov", "Nkunku", "Müller", "Colombia", "Colombian", "Späne", "Havetz", "Gnabry"}:
                buckets["unsupported_name"].append({**row, "name": name})
                break
    return buckets


def repeated_starters(segments: list[Segment]) -> list[dict[str, Any]]:
    starts = Counter()
    examples: dict[str, str] = {}
    for segment in segments:
        text = re.sub(r"\s+", " ", segment.english.strip())
        if not text:
            continue
        starter = " ".join(text.split()[:4]).strip(".,!—-")
        if len(starter) < 8:
            continue
        starts[starter] += 1
        examples.setdefault(starter, segment.event_id)
    return [
        {"starter": starter, "count": count, "example_event_id": examples[starter]}
        for starter, count in starts.most_common(12)
        if count >= 2
    ]


def style_gate(summary: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if summary["wrong_entity_segments"] > 0:
        blockers.append("wrong_entity_segments")
    if summary["unsupported_name_segments"] > 0:
        blockers.append("unsupported_name_segments")
    if summary["color_identity_segments"] > max(12, summary["segment_count"] * 0.08):
        warnings.append("color_identity_segments")
    if summary["raw_visual_segments"] > max(12, summary["segment_count"] * 0.08):
        warnings.append("raw_visual_segments")
    return {
        "status": "fail" if blockers else "pass_with_warnings" if warnings else "pass",
        "blockers": blockers,
        "warnings": warnings,
        "en": "Fail means the script contains unsupported identity facts. Warnings mean the style still sounds like raw visual description.",
        "zh": "fail 表示解说稿包含无依据身份事实；warning 表示文本仍偏向原始画面描述。",
    }


def recommended_identity_distribution() -> list[dict[str, Any]]:
    return [
        {
            "identity_form": "verified_name",
            "target_share": "35-50%",
            "condition_en": "Use only when roster/OCR/broadcast graphic or prior verified fact supports it.",
            "condition_zh": "仅在名单、OCR、转播图表或已验证事实支持时使用。",
        },
        {
            "identity_form": "team_plus_role_or_number",
            "target_share": "30-45%",
            "condition_en": "Use when team and role/jersey number are visible but the name is not secure.",
            "condition_zh": "球队与角色/号码可见但姓名不稳时使用。",
        },
        {
            "identity_form": "team_only",
            "target_share": "15-25%",
            "condition_en": "Use for flowing play when exact identity is not important.",
            "condition_zh": "普通推进或身份不关键时使用球队主语。",
        },
        {
            "identity_form": "color_as_evidence",
            "target_share": "<5%",
            "condition_en": "Use color only as evidence, contrast, or occasional rhetoric, not as the default subject.",
            "condition_zh": "颜色只作证据、对比或少量修辞，不能作为默认主语。",
        },
    ]


def audit_identity_style(
    input_path: str | Path = DEFAULT_INPUT,
    facts_path: str | Path = DEFAULT_FACTS,
) -> dict[str, Any]:
    segments = load_segments(Path(input_path))
    facts = json.loads(Path(facts_path).read_text(encoding="utf-8"))
    buckets = classify_segments(segments, facts)
    summary = {
        "segment_count": len(segments),
        "color_identity_segments": len(buckets["color_identity"]),
        "team_identity_segments": len(buckets["team_identity"]),
        "number_identity_segments": len(buckets["number_identity"]),
        "role_identity_segments": len(buckets["role_identity"]),
        "raw_visual_segments": len(buckets["raw_visual"]),
        "wrong_entity_segments": len(buckets["wrong_entity"]),
        "unsupported_name_segments": len(buckets["unsupported_name"]),
        "color_identity_ratio": round(len(buckets["color_identity"]) / max(1, len(segments)), 4),
        "raw_visual_ratio": round(len(buckets["raw_visual"]) / max(1, len(segments)), 4),
    }
    return {
        "policy": "Evaluation-only. Do not inject this report into target-agent prompt/runtime context.",
        "summary": summary,
        "style_gate": style_gate(summary),
        "recommended_identity_distribution": recommended_identity_distribution(),
        "repeated_starters": repeated_starters(segments),
        "buckets": buckets,
        "recommendations": [
            {
                "priority": "Must",
                "en": "Block unsupported names and wrong teams before final packaging.",
                "zh": "最终打包前必须拦截无依据姓名和错误球队。",
            },
            {
                "priority": "Should",
                "en": "Add an identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric.",
                "zh": "增加身份选择级联：已验证姓名 -> 球队+号码/角色 -> 仅球队 -> 少量颜色修辞。",
            },
            {
                "priority": "Should",
                "en": "Use a style sampler so wording varies naturally inside the same broadcast style instead of repeating one template.",
                "zh": "使用风格采样器，让同一解说风格内部自然变化，而不是重复同一模板。",
            },
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Identity And Style Audit / 身份措辞与解说风格审计",
        "",
        "EN: This report checks whether generated commentary uses supported identities and natural broadcast wording.",
        "",
        "ZH: 本报告检查生成解说是否使用有依据的身份表达，以及是否接近自然人类解说。",
        "",
        "## Summary / 摘要",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")

    gate = report["style_gate"]
    lines.extend(
        [
            "",
            "## Style Gate / 风格门禁",
            "",
            f"- `status`: {gate['status']}",
            f"- `blockers`: {', '.join(gate['blockers']) or '-'}",
            f"- `warnings`: {', '.join(gate['warnings']) or '-'}",
            f"- EN: {gate['en']}",
            f"- ZH: {gate['zh']}",
            "",
            "## Recommended Identity Distribution / 建议身份表达分布",
            "",
            "| Identity Form | Target Share | EN Condition | ZH Condition |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["recommended_identity_distribution"]:
        lines.append(
            f"| {row['identity_form']} | {row['target_share']} | {row['condition_en']} | {row['condition_zh']} |"
        )

    lines.extend(["", "## Repeated Starters / 重复开头", "", "| Starter | Count | Example |", "| --- | ---: | --- |"])
    for row in report["repeated_starters"]:
        lines.append(f"| {row['starter']} | {row['count']} | {row['example_event_id']} |")
    if not report["repeated_starters"]:
        lines.append("| - | - | - |")

    sections = [
        ("wrong_entity", "Wrong Entity / 错误实体"),
        ("unsupported_name", "Unsupported Name / 无依据姓名"),
        ("color_identity", "Color Identity Fallback / 颜色身份 fallback"),
        ("raw_visual", "Raw Visual Wording / 原始画面式措辞"),
    ]
    for key, title in sections:
        lines.extend(["", f"## {title}", "", "| Event | Type | Time | Excerpt |", "| --- | --- | --- | --- |"])
        for row in report["buckets"][key][:20]:
            lines.append(f"| {row['event_id']} | {row['event_type']} | `{row['time']}` | {row['excerpt']} |")
        if not report["buckets"][key]:
            lines.append("| - | - | - | - |")

    lines.extend(["", "## Recommendations / 建议", "", "| Priority | EN | ZH |", "| --- | --- | --- |"])
    for item in report["recommendations"]:
        lines.append(f"| {item['priority']} | {item['en']} | {item['zh']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit identity wording and broadcast style.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--fail-on-style",
        action="store_true",
        help="Return exit code 2 when unsupported identity facts are found.",
    )
    args = parser.parse_args()

    report = audit_identity_style(args.input, args.facts)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if args.fail_on_style and report["style_gate"]["status"] == "fail":
        print("style_gate_status=fail")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
