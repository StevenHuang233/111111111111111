#!/usr/bin/env python
"""Export bilingual commentary JSON to SRT subtitle files."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "outputs" / "commentary_bilingual.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "srt"
LANGUAGES = ("zh", "en", "bilingual")
TEXT_SOURCES = ("subtitle", "commentary", "both")


@dataclass(frozen=True)
class SrtEntry:
    start_sec: float
    end_sec: float
    text: str
    event_id: str


def normalize_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    return text


def srt_timestamp(seconds: float) -> str:
    milliseconds_total = max(0, int(round(seconds * 1000)))
    seconds_total, milliseconds = divmod(milliseconds_total, 1000)
    minutes_total, sec = divmod(seconds_total, 60)
    hours, minutes = divmod(minutes_total, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{milliseconds:03d}"


def wrap_srt_text(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return text
    lines: list[str] = []
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        wrapped = textwrap.wrap(
            raw_line,
            width=max_chars,
            break_long_words=True,
            replace_whitespace=False,
        )
        lines.extend(wrapped or [raw_line])
    return "\n".join(lines)


def load_segments(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = data.get("segments", [])
    if not isinstance(segments, list):
        raise ValueError(f"{path} must contain a list at key 'segments'.")
    return [item for item in segments if isinstance(item, dict)]


def language_payload(segment: dict[str, Any], language: str) -> dict[str, Any]:
    key = "chinese" if language == "zh" else "english"
    payload = segment.get(key, {})
    return payload if isinstance(payload, dict) else {}


def segment_time(segment: dict[str, Any]) -> tuple[float, float]:
    start = float(segment.get("talk_start_sec", 0.0))
    end = float(segment.get("talk_end_sec", start))
    return start, end


def entries_for_language(
    segments: list[dict[str, Any]],
    language: str,
    text_source: str,
    min_duration_sec: float,
) -> list[SrtEntry]:
    entries: list[SrtEntry] = []
    for segment in segments:
        event_id = str(segment.get("event_id", ""))
        start, end = segment_time(segment)
        payload = language_payload(segment, language)
        if text_source == "subtitle":
            subtitle_lines = payload.get("subtitle_lines", [])
            if isinstance(subtitle_lines, list) and subtitle_lines:
                for line in subtitle_lines:
                    if not isinstance(line, dict):
                        continue
                    text = normalize_text(str(line.get("text", "")))
                    if not text:
                        continue
                    line_start = float(line.get("start_sec", start))
                    line_end = float(line.get("end_sec", line_start))
                    entries.append(SrtEntry(line_start, max(line_end, line_start + min_duration_sec), text, event_id))
                continue

        text = normalize_text(str(payload.get("commentary_text", "")))
        if text:
            entries.append(SrtEntry(start, max(end, start + min_duration_sec), text, event_id))
    return sorted(entries, key=lambda item: (item.start_sec, item.end_sec, item.event_id))


def entries_for_bilingual(
    segments: list[dict[str, Any]],
    text_source: str,
    min_duration_sec: float,
) -> list[SrtEntry]:
    zh_entries = entries_for_language(segments, "zh", text_source, min_duration_sec)
    en_entries = entries_for_language(segments, "en", text_source, min_duration_sec)
    if len(zh_entries) == len(en_entries):
        entries: list[SrtEntry] = []
        for zh, en in zip(zh_entries, en_entries):
            start = min(zh.start_sec, en.start_sec)
            end = max(zh.end_sec, en.end_sec, start + min_duration_sec)
            entries.append(SrtEntry(start, end, f"{zh.text}\n{en.text}", zh.event_id or en.event_id))
        return entries

    by_event_en = {entry.event_id: entry for entry in en_entries}
    entries = []
    for zh in zh_entries:
        en = by_event_en.get(zh.event_id)
        if en is None:
            entries.append(zh)
            continue
        start = min(zh.start_sec, en.start_sec)
        end = max(zh.end_sec, en.end_sec, start + min_duration_sec)
        entries.append(SrtEntry(start, end, f"{zh.text}\n{en.text}", zh.event_id))
    return sorted(entries, key=lambda item: (item.start_sec, item.end_sec, item.event_id))


def write_srt(entries: list[SrtEntry], path: Path, max_chars_per_line: int) -> None:
    lines: list[str] = []
    for index, entry in enumerate(entries, start=1):
        lines.append(str(index))
        lines.append(f"{srt_timestamp(entry.start_sec)} --> {srt_timestamp(entry.end_sec)}")
        lines.append(wrap_srt_text(entry.text, max_chars_per_line))
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def export_srt(
    input_path: Path,
    output_dir: Path,
    languages: tuple[str, ...],
    text_source: str,
    min_duration_sec: float,
    max_chars_per_line: int,
) -> list[Path]:
    segments = load_segments(input_path)
    sources = ("subtitle", "commentary") if text_source == "both" else (text_source,)
    written: list[Path] = []
    for source in sources:
        for language in languages:
            if language == "bilingual":
                entries = entries_for_bilingual(segments, source, min_duration_sec)
            else:
                entries = entries_for_language(segments, language, source, min_duration_sec)
            output_path = output_dir / f"{input_path.stem}.{source}.{language}.srt"
            write_srt(entries, output_path, max_chars_per_line)
            written.append(output_path)
    return written


def parse_languages(value: str) -> tuple[str, ...]:
    if value.strip().lower() == "all":
        return LANGUAGES
    parts = tuple(part.strip().lower() for part in value.split(",") if part.strip())
    invalid = [part for part in parts if part not in LANGUAGES]
    if invalid:
        raise ValueError(f"Unsupported language(s): {', '.join(invalid)}. Use one of: {', '.join(LANGUAGES)}")
    return parts or LANGUAGES


def main() -> int:
    parser = argparse.ArgumentParser(description="Export commentary_bilingual.json to SRT files.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--languages", default="all", help="Comma-separated: zh,en,bilingual, or all.")
    parser.add_argument("--text-source", choices=TEXT_SOURCES, default="both")
    parser.add_argument("--min-duration-sec", type=float, default=1.2)
    parser.add_argument("--max-chars-per-line", type=int, default=42)
    args = parser.parse_args()

    written = export_srt(
        input_path=args.input,
        output_dir=args.output_dir,
        languages=parse_languages(args.languages),
        text_source=args.text_source,
        min_duration_sec=max(0.1, args.min_duration_sec),
        max_chars_per_line=args.max_chars_per_line,
    )
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
