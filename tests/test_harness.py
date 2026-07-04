from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

from PIL import Image

from harness import (
    CommentaryResult,
    CommentarySegment,
    CommentaryUnitConfig,
    EventCandidate,
    EventPhase,
    GoalVerificationConfig,
    ScanConfig,
    SubtitleLine,
    TraceRecorder,
    TranslationConfig,
    VisualCommentaryConfig,
    consolidate_goal_timeline,
    dump_bilingual_commentary_result,
    build_commentary_units,
    generate_commentary,
    verify_goal_events,
    run_bilingual_pipeline,
    load_event_types,
    load_manifest,
    load_style,
    run_pipeline,
    scan_events,
    translate_commentary_to_chinese,
)
from harness.manifest import FrameInfo
from harness.scanner import build_windows
from harness.time_utils import format_timestamp
from intern_client import InternClient
from run_full_bilingual_with_progress import build_dense_manifests


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("FakeClient ran out of responses.")
        content = self.responses.pop(0)
        return {"choices": [{"message": {"content": content}}]}


def write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), "green").save(path)


def write_manifest(root: Path, count: int = 5) -> Path:
    frames = []
    for index in range(count):
        frame_path = Path("frames") / f"f{index}.png"
        write_png(root / frame_path)
        frames.append({"frame_id": f"f{index}", "path": str(frame_path), "timestamp_sec": index * 2.0})

    manifest_path = root / "frames_manifest.json"
    manifest_path.write_text(
        json.dumps({"video_id": "demo", "source_video": "demo.mp4", "frames": frames}),
        encoding="utf-8",
    )
    return manifest_path


def write_manifest_with_timestamps(root: Path, timestamps: list[float]) -> Path:
    frames = []
    for index, timestamp in enumerate(timestamps):
        frame_path = Path("frames") / f"f{index}.png"
        write_png(root / frame_path)
        frames.append({"frame_id": f"f{index}", "path": str(frame_path), "timestamp_sec": timestamp})

    manifest_path = root / "frames_manifest.json"
    manifest_path.write_text(
        json.dumps({"video_id": "demo", "source_video": "demo.mp4", "frames": frames}),
        encoding="utf-8",
    )
    return manifest_path


class HarnessTests(unittest.TestCase):
    def test_builtin_and_custom_style_loading(self) -> None:
        style = load_style("short_passionate")
        self.assertEqual(style.style_id, "short_passionate")
        self.assertGreater(style.temperature, 0.0)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "custom_style.json"
            path.write_text(
                json.dumps(
                    {
                        "style_id": "custom",
                        "name": "Custom",
                        "description": "A custom test style.",
                        "prompt_injection": "Speak plainly.",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(load_style(str(path)).style_id, "custom")

            bad_path = Path(tmp) / "bad_style.json"
            bad_path.write_text(json.dumps({"style_id": "bad"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_style(str(bad_path))

    def test_manifest_relative_paths_and_timestamp_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = load_manifest(write_manifest(Path(tmp), count=2))
            self.assertEqual(manifest.video_id, "demo")
            self.assertTrue(manifest.frames[0].path.is_absolute())
            self.assertTrue(manifest.frames[0].path.exists())
            self.assertEqual(format_timestamp(65.25), "01:05.25")

    def test_event_type_descriptions_are_loaded_and_prompted(self) -> None:
        registry = load_event_types()
        reference = registry.prompt_reference()
        self.assertIn("goal", registry.event_types)
        self.assertIn("A live scoring action where the ball clearly enters the goal", reference)

        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=1)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""}
                    ]
                }
            )
            fake = FakeClient([response])
            scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=1, stride_frames=1),
                fake,
            )
            prompt_content = fake.calls[0]["messages"][0]["content"][0]["text"]
            self.assertIn("Event definitions and decision cues", prompt_content)
            self.assertIn("A live scoring action where the ball clearly enters the goal", prompt_content)

    def test_sliding_windows(self) -> None:
        frames = tuple(FrameInfo(f"f{i}", Path(f"f{i}.png"), float(i)) for i in range(10))
        self.assertEqual(build_windows(frames, window_size=6, stride=3), [(0, 6), (3, 9), (6, 10)])

    def test_scan_event_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=5)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "goal", "confidence": 0.9, "evidence": "ball in net"},
                        {"frame_id": "f2", "needs_commentary": True, "event_type": "goal", "confidence": 0.8, "evidence": "players celebrate"},
                        {"frame_id": "f3", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f4", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=5, stride_frames=5),
                FakeClient([response]),
            )

            self.assertEqual(len(result.events), 1)
            event = result.events[0]
            self.assertEqual(event.event_type, "goal")
            self.assertEqual(event.start_sec, 2.0)
            self.assertEqual(event.end_sec, 4.0)
            self.assertEqual(event.evidence_frames, ("f1", "f2"))
            self.assertEqual(event.phases[0].phase_type, "live_goal")

    def test_no_event_breaks_split_same_type_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=6)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "shot", "confidence": 0.8, "evidence": "player shoots"},
                        {"frame_id": "f2", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f3", "needs_commentary": True, "event_type": "shot", "confidence": 0.7, "evidence": "keeper reacts"},
                        {"frame_id": "f4", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f5", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=6, stride_frames=6, merge_gap_sec=4.0),
                FakeClient([response]),
            )
            self.assertEqual(len(result.events), 2)
            self.assertEqual([event.event_type for event in result.events], ["shot", "shot"])
            self.assertEqual(result.events[0].evidence_frames, ("f1",))
            self.assertEqual(result.events[1].evidence_frames, ("f3",))

    def test_scan_normalizes_frame_ids_with_timestamp_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=1)
            response = json.dumps(
                {
                    "frames": [
                        {
                            "frame_id": "f0, timestamp=00:00.00",
                            "needs_commentary": True,
                            "event_type": "shot",
                            "confidence": 0.8,
                            "evidence": "shot visible",
                        }
                    ]
                }
            )
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=1, stride_frames=1),
                FakeClient([response]),
            )
            self.assertEqual(result.events[0].evidence_frames, ("f0",))
            self.assertEqual(result.window_errors, ())

    def test_event_type_change_is_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=4)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": True, "event_type": "period_transition", "confidence": 0.8, "evidence": "ceremony"},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "other_relevant", "confidence": 0.9, "evidence": "crowd"},
                        {"frame_id": "f2", "needs_commentary": True, "event_type": "period_transition", "confidence": 0.85, "evidence": "lineup"},
                        {"frame_id": "f3", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=4, stride_frames=4, merge_gap_sec=8.0),
                FakeClient([response]),
            )

            self.assertEqual(len(result.events), 3)
            self.assertEqual([event.event_type for event in result.events], ["period_transition", "other_relevant", "period_transition"])
            self.assertEqual([(event.start_sec, event.end_sec) for event in result.events], [(0.0, 0.0), (2.0, 2.0), (4.0, 4.0)])

    def test_goal_replay_merge_creates_replay_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=7)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "goal", "confidence": 0.92, "evidence": "ball in net"},
                        {"frame_id": "f2", "needs_commentary": True, "event_type": "goal", "confidence": 0.9, "evidence": "players celebrate"},
                        {"frame_id": "f3", "needs_commentary": True, "event_type": "celebration_or_replay", "confidence": 0.83, "evidence": "slow motion replay angle"},
                        {"frame_id": "f4", "needs_commentary": True, "event_type": "celebration_or_replay", "confidence": 0.81, "evidence": "wide replay shows pass"},
                        {"frame_id": "f5", "needs_commentary": True, "event_type": "celebration_or_replay", "confidence": 0.8, "evidence": "replay continues"},
                        {"frame_id": "f6", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=7, stride_frames=7, goal_replay_merge_gap_sec=30.0),
                FakeClient([response]),
            )
            self.assertEqual(len(result.events), 1)
            event = result.events[0]
            self.assertEqual(event.event_type, "goal")
            self.assertEqual([phase.phase_type for phase in event.phases], ["live_goal", "replay"])
            self.assertIn("wide replay", event.evidence_summary)

    def test_commentary_units_merge_goal_with_mixed_replay_sequence(self) -> None:
        events = [
            EventCandidate("E001", "shot", 10.0, 10.0, ("f1",), 0.8, "shot starts", (EventPhase("shot", 10.0, 10.0, ("f1",), "shot starts"),)),
            EventCandidate("E002", "goal", 14.0, 18.0, ("f2", "f3"), 0.95, "ball in net", (EventPhase("live_goal", 14.0, 18.0, ("f2", "f3"), "ball in net"),)),
            EventCandidate("E003", "dangerous_attack", 26.0, 26.0, ("f4",), 0.75, "replay buildup", (EventPhase("dangerous_attack", 26.0, 26.0, ("f4",), "replay buildup"),)),
            EventCandidate("E004", "celebration_or_replay", 30.0, 34.0, ("f5",), 0.9, "slow replay", (EventPhase("celebration_or_replay", 30.0, 34.0, ("f5",), "slow replay"),)),
            EventCandidate("E005", "foul", 100.0, 100.0, ("f6",), 0.7, "late foul", (EventPhase("foul", 100.0, 100.0, ("f6",), "late foul"),)),
        ]

        units = build_commentary_units(events, CommentaryUnitConfig(goal_context_before_sec=8.0, goal_replay_after_sec=24.0))

        self.assertEqual(len(units), 2)
        self.assertEqual(units[0].event_type, "goal")
        self.assertEqual(units[0].start_sec, 10.0)
        self.assertEqual(units[0].end_sec, 34.0)
        self.assertEqual([phase.phase_type for phase in units[0].phases], ["buildup", "live_goal", "replay", "replay"])
        self.assertEqual(units[1].event_type, "foul")

    def test_commentary_units_mark_goal_celebration_phase(self) -> None:
        events = [
            EventCandidate("E001", "goal", 20.0, 20.0, ("f1",), 0.95, "ball in net", (EventPhase("live_goal", 20.0, 20.0, ("f1",), "ball in net"),)),
            EventCandidate(
                "E002",
                "celebration_or_replay",
                24.0,
                28.0,
                ("f2",),
                0.9,
                "players celebrating with arms raised and crowd cheering",
                (EventPhase("celebration_or_replay", 24.0, 28.0, ("f2",), "players celebrating with arms raised and crowd cheering"),),
            ),
        ]

        units = build_commentary_units(events, CommentaryUnitConfig(goal_replay_after_sec=20.0))

        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].event_type, "goal")
        self.assertEqual([phase.phase_type for phase in units[0].phases], ["live_goal", "celebration"])

    def test_goal_verifier_can_downgrade_false_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = load_manifest(write_manifest(Path(tmp), count=2))
            event = EventCandidate(
                "E001",
                "goal",
                0.0,
                2.0,
                ("f0", "f1"),
                0.9,
                "goalkeeper catches the ball; no goal scored",
                (
                    EventPhase("live_goal", 0.0, 0.0, ("f0",), "shot toward goal"),
                    EventPhase("replay", 2.0, 2.0, ("f1",), "goalkeeper catches the ball"),
                ),
            )
            response = json.dumps(
                {
                    "verdict": "not_goal",
                    "confidence": 0.92,
                    "corrected_event_type": "save",
                    "rationale": "The goalkeeper catches the ball and there is no scoring evidence.",
                    "phase_labels": [
                        {"phase_index": 0, "phase_type": "buildup", "reason": "shot setup"},
                        {"phase_index": 1, "phase_type": "replay", "reason": "save replay"},
                    ],
                    "warnings": ["downgraded false goal"],
                }
            )
            result = verify_goal_events([event], manifest, load_style("broadcast_professional"), FakeClient([response]))

            self.assertEqual(result.events[0].event_type, "save")
            self.assertEqual(result.records[0].verdict, "not_goal")
            self.assertIn("Goal verification verdict=not_goal", result.events[0].evidence_summary)

    def test_goal_timeline_consolidation_merges_duplicates_and_downgrades(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = load_manifest(write_manifest(Path(tmp), count=5))
            events = [
                EventCandidate(
                    "U001",
                    "goal",
                    0.0,
                    2.0,
                    ("f0", "f1"),
                    0.9,
                    "live finish and ball in net",
                    (EventPhase("live_goal", 0.0, 2.0, ("f0", "f1"), "live finish"),),
                ),
                EventCandidate(
                    "U002",
                    "goal",
                    4.0,
                    4.0,
                    ("f2",),
                    0.85,
                    "slow-motion replay of the same finish",
                    (EventPhase("replay", 4.0, 4.0, ("f2",), "replay angle"),),
                ),
                EventCandidate(
                    "U003",
                    "goal",
                    6.0,
                    8.0,
                    ("f3", "f4"),
                    0.8,
                    "goalkeeper saves the shot",
                    (EventPhase("live_goal", 6.0, 8.0, ("f3", "f4"), "keeper save"),),
                ),
            ]
            response = json.dumps(
                {
                    "actual_goal_event_ids": ["U001"],
                    "candidate_labels": [
                        {
                            "event_id": "U001",
                            "classification": "actual_goal",
                            "corrected_event_type": "goal",
                            "confidence": 0.95,
                            "merge_into_event_id": "",
                            "rationale": "The live scoring action is visible.",
                            "phase_labels": [{"phase_index": 0, "phase_type": "live_goal", "reason": "finish"}],
                            "warnings": [],
                        },
                        {
                            "event_id": "U002",
                            "classification": "duplicate_replay",
                            "corrected_event_type": "celebration_or_replay",
                            "confidence": 0.9,
                            "merge_into_event_id": "U001",
                            "rationale": "Replay of the earlier goal.",
                            "phase_labels": [{"phase_index": 0, "phase_type": "replay", "reason": "replay"}],
                            "warnings": [],
                        },
                        {
                            "event_id": "U003",
                            "classification": "shot_or_save",
                            "corrected_event_type": "save",
                            "confidence": 0.88,
                            "merge_into_event_id": "",
                            "rationale": "The goalkeeper saves it.",
                            "phase_labels": [],
                            "warnings": [],
                        },
                    ],
                    "warnings": [],
                }
            )

            result = consolidate_goal_timeline(
                events,
                manifest,
                load_style("broadcast_professional"),
                FakeClient([response]),
                config=GoalVerificationConfig(timeline_max_frames_per_goal=1),
            )

            self.assertEqual([event.event_id for event in result.events], ["U001", "U003"])
            self.assertEqual([event.event_type for event in result.events], ["goal", "save"])
            self.assertEqual(result.events[0].end_sec, 4.0)
            self.assertIn("Merged U002", result.events[0].evidence_summary)
            self.assertEqual(len(result.records), 3)
            self.assertEqual(result.input_event_ids, ("U001", "U002", "U003"))

    def test_goal_timeline_downgrades_weak_goal_without_followup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = load_manifest(write_manifest(Path(tmp), count=2))
            event = EventCandidate(
                "U010",
                "goal",
                0.0,
                2.0,
                ("f0", "f1"),
                0.7,
                "attacker shoots toward goal but the result is unclear",
                (EventPhase("live_goal", 0.0, 2.0, ("f0", "f1"), "shot toward goal"),),
            )
            response = json.dumps(
                {
                    "actual_goal_event_ids": ["U010"],
                    "candidate_labels": [
                        {
                            "event_id": "U010",
                            "classification": "actual_goal",
                            "corrected_event_type": "goal",
                            "confidence": 0.6,
                            "merge_into_event_id": "",
                            "rationale": "Possible goal but the ball crossing the line is not visible.",
                            "phase_labels": [{"phase_index": 0, "phase_type": "live_goal", "reason": "shot"}],
                            "warnings": [],
                        }
                    ],
                    "warnings": [],
                }
            )

            result = consolidate_goal_timeline(
                [event],
                manifest,
                load_style("broadcast_professional"),
                FakeClient([response]),
                config=GoalVerificationConfig(min_actual_goal_confidence_without_followup=0.82),
            )

            self.assertEqual(result.events[0].event_type, "shot")
            self.assertEqual(result.records[0].verdict, "shot_or_save")
            self.assertIn("no follow-up support", result.records[0].warnings[0])

    def test_illegal_event_type_repair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=1)
            bad = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": True, "event_type": "weird", "confidence": 0.9, "evidence": "bad type"}
                    ]
                }
            )
            fixed = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": True, "event_type": "shot", "confidence": 0.7, "evidence": "shot visible"}
                    ]
                }
            )
            fake = FakeClient([bad, fixed])
            result = scan_events(
                manifest_path,
                load_style("broadcast_professional"),
                ScanConfig(window_size_frames=1, stride_frames=1, repair_attempts=1),
                fake,
            )
            self.assertEqual(result.events[0].event_type, "shot")
            self.assertEqual(len(fake.calls), 2)
            self.assertEqual(result.window_errors, ())

    def test_generate_commentary_with_fake_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = load_manifest(write_manifest(Path(tmp), count=1))
            event = EventCandidate(
                "E001",
                "goal",
                0.0,
                2.0,
                ("f0",),
                0.9,
                "ball in net",
                (EventPhase("live_goal", 0.0, 2.0, ("f0",), "ball in net"),),
            )
            response = json.dumps(
                {
                    "commentary_text": "A decisive finish opens the scoring.",
                    "subtitle_lines": [{"start_sec": 0.0, "end_sec": 2.0, "text": "Decisive finish!"}],
                }
            )
            result = generate_commentary([event], manifest, load_style("broadcast_professional"), FakeClient([response]))
            self.assertEqual(result.segments[0].talk_start_sec, 0.0)
            self.assertEqual(result.segments[0].talk_end_sec, 2.0)
            self.assertIn("decisive", result.segments[0].commentary_text.lower())

    def test_translate_commentary_to_chinese_with_style_prompt(self) -> None:
        commentary = CommentaryResult(
            video_id="demo",
            style_id="broadcast_professional",
            segments=(
                CommentarySegment(
                    event_id="E001",
                    event_type="goal",
                    talk_start_sec=0.0,
                    talk_end_sec=4.0,
                    commentary_text="A decisive finish opens the scoring.",
                    subtitle_lines=(SubtitleLine(0.0, 4.0, "A decisive finish."),),
                ),
            ),
        )
        response = json.dumps(
            {
                "commentary_text": "一次决定性的终结打破僵局。",
                "subtitle_lines": [{"start_sec": 0.0, "end_sec": 4.0, "text": "决定性的终结。"}],
            },
            ensure_ascii=False,
        )
        fake = FakeClient([response])
        result = translate_commentary_to_chinese(
            commentary,
            load_style("broadcast_professional"),
            fake,
            config=TranslationConfig(max_tokens=512),
        )

        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language_code, "zh-CN")
        self.assertEqual(result.segments[0].english.commentary_text, "A decisive finish opens the scoring.")
        self.assertIn("打破僵局", result.segments[0].chinese.commentary_text)
        prompt = fake.calls[0]["messages"][0]["content"]
        self.assertIn("Meaning fidelity is the first priority", prompt)
        self.assertIn("Use a professional broadcast tone", prompt)
        self.assertIn("Translate as a polished Chinese football commentator would speak", prompt)
        self.assertIn("Use natural Mandarin sports-broadcast language", prompt)

    def test_dump_bilingual_commentary_result(self) -> None:
        commentary = CommentaryResult(
            video_id="demo",
            style_id="broadcast_professional",
            segments=(
                CommentarySegment(
                    event_id="E001",
                    event_type="shot",
                    talk_start_sec=0.0,
                    talk_end_sec=2.0,
                    commentary_text="The shot flashes wide.",
                    subtitle_lines=(),
                ),
            ),
        )
        fake = FakeClient([json.dumps({"commentary_text": "这脚射门偏出。", "subtitle_lines": []}, ensure_ascii=False)])
        result = translate_commentary_to_chinese(commentary, load_style("broadcast_professional"), fake)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bilingual.json"
            dump_bilingual_commentary_result(result, path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["segments"][0]["english"]["commentary_text"], "The shot flashes wide.")
            self.assertEqual(data["segments"][0]["chinese"]["commentary_text"], "这脚射门偏出。")

    def test_run_pipeline_with_fake_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=3)
            scan_response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "dangerous_attack", "confidence": 0.75, "evidence": "attack near box"},
                        {"frame_id": "f2", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            commentary_response = json.dumps({"commentary_text": "Pressure builds near the box.", "subtitle_lines": []})
            result = run_pipeline(
                manifest_path,
                "broadcast_professional",
                ScanConfig(window_size_frames=3, stride_frames=3),
                FakeClient([scan_response, commentary_response]),
                visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=2, max_frames_per_phase=2),
            )
            self.assertEqual(len(result.scan.events), 1)
            self.assertEqual(len(result.commentary.segments), 1)

    def test_run_bilingual_pipeline_with_fake_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=3)
            scan_response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "shot", "confidence": 0.75, "evidence": "shot toward goal"},
                        {"frame_id": "f2", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            commentary_response = json.dumps({"commentary_text": "A shot flashes toward goal.", "subtitle_lines": []})
            translation_response = json.dumps(
                {"commentary_text": "一脚射门直奔球门而去。", "subtitle_lines": []},
                ensure_ascii=False,
            )
            tracker = TraceRecorder()
            result = run_bilingual_pipeline(
                manifest_path,
                "broadcast_professional",
                ScanConfig(window_size_frames=3, stride_frames=3),
                FakeClient([scan_response, commentary_response, translation_response]),
                tracker,
                visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=2, max_frames_per_phase=2),
                translation_config=TranslationConfig(max_tokens=512),
            )

            self.assertEqual(len(result.scan.events), 1)
            self.assertEqual(len(result.bilingual_commentary.segments), 1)
            self.assertIn("射门", result.bilingual_commentary.segments[0].chinese.commentary_text)
            actions = [(step.step, step.action) for step in tracker.steps]
            self.assertIn(("generate_visual_commentary.event", "prepare_model_call"), actions)
            self.assertIn(("translate_commentary_to_chinese.segment", "prepare_model_call"), actions)

    def test_visual_commentary_receives_selected_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=3)
            scan_response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "shot", "confidence": 0.75, "evidence": "shot toward goal"},
                        {"frame_id": "f2", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            commentary_response = json.dumps({"commentary_text": "A shot flashes toward goal.", "subtitle_lines": []})
            fake = FakeClient([scan_response, commentary_response])
            run_pipeline(
                manifest_path,
                "broadcast_professional",
                ScanConfig(window_size_frames=3, stride_frames=3),
                fake,
                visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=2, max_frames_per_phase=2),
            )
            commentary_call = fake.calls[-1]
            content = commentary_call["messages"][0]["content"]
            self.assertIsInstance(content, list)
            self.assertTrue(any(part.get("type") == "image_url" for part in content if isinstance(part, dict)))
            self.assertIn("selected visual frames", content[0]["text"])

    def test_visual_commentary_samples_interval_context_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=5)
            scan_response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f2", "needs_commentary": True, "event_type": "shot", "confidence": 0.75, "evidence": "shot toward goal"},
                        {"frame_id": "f3", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f4", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            commentary_response = json.dumps({"commentary_text": "The shot is taken after a short buildup.", "subtitle_lines": []})
            fake = FakeClient([scan_response, commentary_response])
            run_pipeline(
                manifest_path,
                "broadcast_professional",
                ScanConfig(window_size_frames=5, stride_frames=5),
                fake,
                visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=4, max_frames_per_phase=3),
            )
            content = fake.calls[-1]["messages"][0]["content"]
            sent_text = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
            self.assertIn("frame_id=f1", sent_text)
            self.assertIn("frame_id=f2", sent_text)
            self.assertIn("frame_id=f3", sent_text)

    def test_visual_commentary_respects_sample_fps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest_with_timestamps(Path(tmp), [0.0, 1.0, 2.0, 3.0, 4.0])
            manifest = load_manifest(manifest_path)
            event = EventCandidate(
                event_id="E001",
                event_type="shot",
                start_sec=0.0,
                end_sec=4.0,
                evidence_frames=("f0", "f1", "f2", "f3", "f4"),
                confidence=0.8,
                evidence_summary="shot sequence",
            )
            fake = FakeClient([json.dumps({"commentary_text": "A shot sequence.", "subtitle_lines": []})])
            generate_commentary(
                [event],
                manifest,
                load_style("broadcast_professional"),
                fake,
                visual_config=VisualCommentaryConfig(
                    max_frames_per_event=10,
                    max_frames_per_phase=10,
                    context_frames_each_side=0,
                    sample_fps=0.5,
                ),
            )

            content = fake.calls[-1]["messages"][0]["content"]
            sent_text = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
            self.assertIn("frame_id=f0", sent_text)
            self.assertIn("frame_id=f2", sent_text)
            self.assertIn("frame_id=f4", sent_text)
            self.assertNotIn("frame_id=f1", sent_text)
            self.assertNotIn("frame_id=f3", sent_text)

    def test_dense_manifests_respect_sample_fps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = load_manifest(write_manifest_with_timestamps(root, [index * 0.25 for index in range(9)]))
            event = EventCandidate(
                event_id="E001",
                event_type="shot",
                start_sec=0.0,
                end_sec=2.0,
                evidence_frames=(),
                confidence=0.8,
                evidence_summary="shot",
            )
            paths = build_dense_manifests(manifest, [event], root / "dense", padding_sec=0.0, sample_fps=1.0, resume=False)
            data = json.loads(paths[0].read_text(encoding="utf-8"))
            self.assertEqual([frame["timestamp_sec"] for frame in data["frames"]], [0.0, 1.0, 2.0])
            self.assertEqual(data["event_source"]["sample_fps"], 1.0)

    def test_pipeline_trace_records_step_jumps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=3)
            scan_response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "dangerous_attack", "confidence": 0.75, "evidence": "attack near box"},
                        {"frame_id": "f2", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                    ]
                }
            )
            commentary_response = json.dumps({"commentary_text": "Pressure builds near the box.", "subtitle_lines": []})
            tracker = TraceRecorder()
            result = run_pipeline(
                manifest_path,
                "broadcast_professional",
                ScanConfig(window_size_frames=3, stride_frames=3),
                FakeClient([scan_response, commentary_response]),
                tracker,
                visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=2, max_frames_per_phase=2),
            )
            actions = [(step.step, step.action) for step in tracker.steps]
            self.assertIn(("run_pipeline", "load_style"), actions)
            self.assertIn(("scan_events", "build_windows"), actions)
            self.assertIn(("scan_events.window", "prepare_model_call"), actions)
            self.assertIn(("scan_events", "merge_event_candidates"), actions)
            self.assertIn(("generate_visual_commentary.event", "prepare_model_call"), actions)
            self.assertIs(result.trace, tracker)

    @unittest.skipUnless(
        os.getenv("INTERN_API_KEY") and os.getenv("RUN_REAL_API_TESTS") == "1",
        "Set INTERN_API_KEY and RUN_REAL_API_TESTS=1 to run real API smoke tests.",
    )
    def test_optional_real_api_text_smoke(self) -> None:
        client = InternClient()
        data = client.chat(
            [{"role": "user", "content": "Reply with exactly: ok"}],
            max_tokens=32,
            thinking_mode=False,
        )
        self.assertTrue(InternClient.text_from_response(data).strip())


if __name__ == "__main__":
    unittest.main()
