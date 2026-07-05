from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intern_client import InternClient

from .commentary import (
    CommentaryResult,
    CommentarySegment,
    SubtitleLine,
    VisualCommentaryConfig,
    generate_visual_commentary,
)
from .json_utils import extract_json_object, to_pretty_json
from .match_context import MatchContext, match_context_block
from .manifest import FramesManifest
from .scanner import EventCandidate
from .styles import StyleProfile, style_instruction_block
from .tracing import NullTracker, StepTracker, clip_text, should_record_model_io, tracker_text_limit


class ChatClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class TranslationConfig:
    target_language: str = "Simplified Chinese"
    target_language_code: str = "zh-CN"
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 1600
    thinking_mode: bool = False


@dataclass(frozen=True)
class LocalizedCommentary:
    commentary_text: str
    subtitle_lines: tuple[SubtitleLine, ...] = ()


@dataclass(frozen=True)
class BilingualCommentarySegment:
    event_id: str
    event_type: str
    talk_start_sec: float
    talk_end_sec: float
    english: LocalizedCommentary
    chinese: LocalizedCommentary


@dataclass(frozen=True)
class BilingualCommentaryResult:
    video_id: str
    style_id: str
    source_language: str
    target_language: str
    target_language_code: str
    segments: tuple[BilingualCommentarySegment, ...]


def generate_bilingual_commentary(
    events: list[EventCandidate] | tuple[EventCandidate, ...],
    manifest: FramesManifest,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    visual_config: VisualCommentaryConfig | None = None,
    translation_config: TranslationConfig | None = None,
    match_context: MatchContext | None = None,
) -> BilingualCommentaryResult:
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "generate_bilingual_commentary",
        "start",
        {
            "video_id": manifest.video_id,
            "style_id": style.style_id,
            "event_count": len(events),
            "match_context_id": match_context.context_id if match_context else None,
        },
    )
    english = generate_visual_commentary(events, manifest, style, active_client, trace, visual_config, match_context)
    trace.record(
        "generate_bilingual_commentary",
        "english_generated",
        {"segment_count": len(english.segments)},
    )
    bilingual = translate_commentary_to_chinese(english, style, active_client, trace, translation_config, match_context)
    trace.record(
        "generate_bilingual_commentary",
        "finish",
        {"segment_count": len(bilingual.segments), "target_language_code": bilingual.target_language_code},
    )
    return bilingual


def translate_commentary_to_chinese(
    commentary: CommentaryResult,
    style: StyleProfile,
    client: ChatClient | None = None,
    tracker: StepTracker | None = None,
    config: TranslationConfig | None = None,
    match_context: MatchContext | None = None,
) -> BilingualCommentaryResult:
    translation_config = config or TranslationConfig()
    active_client = client or InternClient()
    trace = tracker or NullTracker()
    trace.record(
        "translate_commentary_to_chinese",
        "start",
        {
            "video_id": commentary.video_id,
            "style_id": style.style_id,
            "segment_count": len(commentary.segments),
            "target_language_code": translation_config.target_language_code,
            "match_context_id": match_context.context_id if match_context else None,
        },
    )

    bilingual_segments: list[BilingualCommentarySegment] = []
    for segment in commentary.segments:
        trace.record(
            "translate_commentary_to_chinese.segment",
            "prepare_model_call",
            {
                "event_id": segment.event_id,
                "event_type": segment.event_type,
                "time_range": [segment.talk_start_sec, segment.talk_end_sec],
                "subtitle_count": len(segment.subtitle_lines),
            },
        )
        messages = _build_translation_messages(segment, style, translation_config, match_context)
        if should_record_model_io(trace):
            trace.record(
                "translate_commentary_to_chinese.segment",
                "model_call_input",
                {
                    "event_id": segment.event_id,
                    "prompt": clip_text(str(messages[0].get("content", "")), tracker_text_limit(trace)),
                },
            )
        data = active_client.chat(
            messages,
            temperature=translation_config.temperature,
            top_p=translation_config.top_p,
            max_tokens=translation_config.max_tokens,
            thinking_mode=translation_config.thinking_mode,
        )
        text = data["choices"][0]["message"].get("content") or ""
        if should_record_model_io(trace):
            trace.record(
                "translate_commentary_to_chinese.segment",
                "model_call_output",
                {"event_id": segment.event_id, "content": clip_text(text, tracker_text_limit(trace))},
            )
        chinese = _parse_translation_response(text, segment)
        bilingual_segments.append(
            BilingualCommentarySegment(
                event_id=segment.event_id,
                event_type=segment.event_type,
                talk_start_sec=segment.talk_start_sec,
                talk_end_sec=segment.talk_end_sec,
                english=LocalizedCommentary(
                    commentary_text=segment.commentary_text,
                    subtitle_lines=segment.subtitle_lines,
                ),
                chinese=chinese,
            )
        )
        trace.record("translate_commentary_to_chinese.segment", "parsed_model_response", {"event_id": segment.event_id})

    trace.record("translate_commentary_to_chinese", "finish", {"segment_count": len(bilingual_segments)})
    return BilingualCommentaryResult(
        video_id=commentary.video_id,
        style_id=commentary.style_id,
        source_language="en",
        target_language=translation_config.target_language,
        target_language_code=translation_config.target_language_code,
        segments=tuple(bilingual_segments),
    )


def _build_translation_messages(
    segment: CommentarySegment,
    style: StyleProfile,
    config: TranslationConfig,
    match_context: MatchContext | None = None,
) -> list[dict[str, str]]:
    source = {
        "event_id": segment.event_id,
        "event_type": segment.event_type,
        "talk_start_sec": segment.talk_start_sec,
        "talk_end_sec": segment.talk_end_sec,
        "commentary_text": segment.commentary_text,
        "subtitle_lines": [
            {
                "start_sec": subtitle.start_sec,
                "end_sec": subtitle.end_sec,
                "text": subtitle.text,
            }
            for subtitle in segment.subtitle_lines
        ],
    }
    prompt = f"""
You are translating football commentary from English into {config.target_language}.

Meaning fidelity is the first priority. Preserve the exact factual meaning, timing, numbers, names, teams, score references, and uncertainty.
Apply this commentary style strongly after preserving meaning:
{style_instruction_block(style, "chinese_translation")}

Match context for factual disambiguation:
{match_context_block(match_context)}

Translation rules:
- Do not add facts, player names, team names, scores, or tactical details that are not in the English source.
- Use the match context to preserve team identity and avoid wrong team substitutions; for this video, do not translate Curacao/Curaçao as Colombia or Paraguay.
- The returned commentary_text and subtitle_lines must be written in {config.target_language}; do not copy the English source into the translated fields.
- Translate an in-match "penalty kick" as "点球" or "主罚点球"; do not call it "点球大战" unless the source explicitly says penalty shootout.
- Keep the same event_id, event_type, talk_start_sec, talk_end_sec, and subtitle timing.
- Translate as a polished Chinese football commentator would speak, not as a literal subtitle translator.
- Preserve factual meaning, but you may reshape sentence order, rhythm, connectives, and exclamatory cadence to fit the selected style.
- Avoid flat phrases like "a player takes a shot" when the source allows a more vivid but still faithful Chinese rendering.
- Do not leave stray English words in Chinese text except standard football/broadcast terms such as VAR.
- If style and meaning conflict, choose meaning, then recover style through rhythm and wording.
- Return JSON only.

English source:
{to_pretty_json(source)}

Return JSON only:
{{
  "commentary_text": "Chinese spoken commentary text",
  "subtitle_lines": [
    {{"start_sec": {segment.talk_start_sec}, "end_sec": {segment.talk_end_sec}, "text": "Chinese subtitle text"}}
  ]
}}
""".strip()
    return [{"role": "user", "content": prompt}]


def _parse_translation_response(text: str, source: CommentarySegment) -> LocalizedCommentary:
    try:
        payload = extract_json_object(text)
        commentary_text = _first_text_value(payload, ("commentary_text", "commentation_text", "commentary", "text")) or text.strip()
        subtitle_rows = payload.get("subtitle_lines", [])
        subtitles: list[SubtitleLine] = []
        if isinstance(subtitle_rows, list):
            for row in subtitle_rows:
                if not isinstance(row, dict):
                    continue
                subtitles.append(
                    SubtitleLine(
                        start_sec=float(row.get("start_sec", source.talk_start_sec)),
                        end_sec=float(row.get("end_sec", source.talk_end_sec)),
                        text=str(row.get("text", "")).strip(),
                    )
                )
    except Exception:
        commentary_text = text.strip()
        subtitles = ()
    return LocalizedCommentary(commentary_text=commentary_text, subtitle_lines=tuple(subtitles))


def _first_text_value(payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for value in payload.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def bilingual_commentary_result_to_dict(result: BilingualCommentaryResult) -> dict[str, Any]:
    return {
        "video_id": result.video_id,
        "style_id": result.style_id,
        "source_language": result.source_language,
        "target_language": result.target_language,
        "target_language_code": result.target_language_code,
        "segments": [
            {
                "event_id": segment.event_id,
                "event_type": segment.event_type,
                "talk_start_sec": segment.talk_start_sec,
                "talk_end_sec": segment.talk_end_sec,
                "english": _localized_to_dict(segment.english),
                "chinese": _localized_to_dict(segment.chinese),
            }
            for segment in result.segments
        ],
    }


def _localized_to_dict(commentary: LocalizedCommentary) -> dict[str, Any]:
    return {
        "commentary_text": commentary.commentary_text,
        "subtitle_lines": [
            {
                "start_sec": subtitle.start_sec,
                "end_sec": subtitle.end_sec,
                "text": subtitle.text,
            }
            for subtitle in commentary.subtitle_lines
        ],
    }


def dump_bilingual_commentary_result(result: BilingualCommentaryResult, path: str | Path) -> None:
    Path(path).write_text(to_pretty_json(bilingual_commentary_result_to_dict(result)), encoding="utf-8")
