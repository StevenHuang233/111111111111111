from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

from PIL import Image

from harness import (
    EventCandidate,
    EventPhase,
    ScanConfig,
    TraceRecorder,
    VisualCommentaryConfig,
    generate_commentary,
    load_event_types,
    load_manifest,
    load_style,
    run_pipeline,
    scan_events,
)
from harness.manifest import FrameInfo
from harness.scanner import build_windows
from harness.time_utils import format_timestamp
from intern_client import InternClient


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
        self.assertIn("The ball appears to cross the goal line", reference)

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
            self.assertIn("The ball appears to cross the goal line", prompt_content)

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
            self.assertEqual(event.start_sec, 0.0)
            self.assertEqual(event.end_sec, 6.0)
            self.assertEqual(event.evidence_frames, ("f1", "f2"))
            self.assertEqual(event.phases[0].phase_type, "live_goal")

    def test_time_range_merge_for_split_same_type_events(self) -> None:
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
            self.assertEqual(len(result.events), 1)
            self.assertEqual(result.events[0].event_type, "shot")
            self.assertEqual(result.events[0].evidence_frames, ("f1", "f3"))
            self.assertEqual(len(result.events[0].phases), 2)

    def test_goal_replay_merge_creates_replay_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = write_manifest(Path(tmp), count=7)
            response = json.dumps(
                {
                    "frames": [
                        {"frame_id": "f0", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f1", "needs_commentary": True, "event_type": "goal", "confidence": 0.92, "evidence": "ball in net"},
                        {"frame_id": "f2", "needs_commentary": True, "event_type": "goal", "confidence": 0.9, "evidence": "players celebrate"},
                        {"frame_id": "f3", "needs_commentary": False, "event_type": "no_event", "confidence": 0.0, "evidence": ""},
                        {"frame_id": "f4", "needs_commentary": True, "event_type": "celebration_or_replay", "confidence": 0.83, "evidence": "slow motion replay angle"},
                        {"frame_id": "f5", "needs_commentary": True, "event_type": "celebration_or_replay", "confidence": 0.81, "evidence": "wide replay shows pass"},
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
