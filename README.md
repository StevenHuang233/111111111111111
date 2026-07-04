# Intern-S2-Preview football commentary harness

Minimal Python setup for testing Intern-S2-Preview text/image calls and building a highly decoupled football video commentary harness.

## Setup

```powershell
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Put your API key in `.env` or set `INTERN_API_KEY` in the shell.

## Text test

```powershell
python test_text.py
```

## Image test

Generate and test a local sample image:

```powershell
python test_image.py
```

Use a local frame or screenshot:

```powershell
python test_image.py --image "C:\\path\\to\\frame.jpg" --prompt "Describe the football scene and list visible evidence."
```

## Harness API

The first harness version is a Python API, not a CLI. It consumes a frame manifest that you prepare from already-cut frames.

For text and configuration review, see:

- Chinese: `docs/text_review_zh.md`
- English: `docs/text_review_en.md`

```python
from harness import (
    ScanConfig,
    TraceRecorder,
    TranslationConfig,
    VisualCommentaryConfig,
    dump_bilingual_commentary_result,
    dump_commentary_result,
    dump_scan_result,
    run_bilingual_pipeline,
    run_pipeline,
)

tracker = TraceRecorder()
result = run_pipeline(
    manifest_path="frames_manifest.json",
    style_id_or_path="broadcast_professional",
    scan_config=ScanConfig(window_size_frames=6, stride_frames=3),
    tracker=tracker,
    visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=12, max_frames_per_phase=4),
)

dump_scan_result(result.scan, "outputs/events.json")
dump_commentary_result(result.commentary, "outputs/commentary.json")
tracker.dump("outputs/trace.json")
```

For bilingual English/Chinese output, use the separate bilingual pipeline:

```python
tracker = TraceRecorder()
result = run_bilingual_pipeline(
    manifest_path="frames_manifest.json",
    style_id_or_path="broadcast_professional",
    scan_config=ScanConfig(window_size_frames=6, stride_frames=3),
    tracker=tracker,
    visual_commentary_config=VisualCommentaryConfig(max_frames_per_event=12, max_frames_per_phase=4),
    translation_config=TranslationConfig(),
)

dump_scan_result(result.scan, "outputs/events.json")
dump_bilingual_commentary_result(result.bilingual_commentary, "outputs/commentary_bilingual.json")
tracker.dump("outputs/trace.json")
```

You can also call the modules separately:

```python
from intern_client import InternClient
from harness import generate_commentary, load_manifest, load_style, scan_events

client = InternClient()
style = load_style("short_passionate")
manifest = load_manifest("frames_manifest.json")
scan = scan_events(manifest.manifest_path, style, client=client)
commentary = generate_commentary(scan.events, manifest, style, client=client)
```

## Step tracing

Use `TraceRecorder` when you want to inspect how the harness jumps through the pipeline:

```python
from harness import TraceRecorder, run_pipeline

tracker = TraceRecorder()
result = run_pipeline("frames_manifest.json", tracker=tracker)
tracker.dump("outputs/trace.json")
```

The trace records high-level and module-level steps such as:

- `run_pipeline -> load_style`
- `run_pipeline -> load_manifest`
- `scan_events -> build_windows`
- `scan_events.window -> prepare_model_call`
- `scan_events.window -> parsed_model_response`
- `scan_events -> aggregate_frame_observations`
- `scan_events -> merge_event_candidates`
- `generate_visual_commentary.event -> prepare_model_call`

Each step includes an index, elapsed seconds, action name, and structured details such as frame IDs, window ranges, event counts, phase types, and merge counts.

When `TraceRecorder(record_model_io=True)` is used, each model call also records:

- `model_call_input`: prompt text, frame IDs, timestamps, and local image paths.
- `model_call_output`: raw model text response.

Image base64 payloads are not written to trace files. The trace records local image paths instead, so the log stays reviewable.

## Frame manifest

Use `frames_manifest.json` as the boundary between your frame extraction step and this harness:

```json
{
  "video_id": "germany_curacao_group_e_round_1",
  "source_video": "Germany_vs_Curacao.mp4",
  "frames": [
    {"frame_id": "f000001", "path": "frames/f000001.jpg", "timestamp_sec": 0.0},
    {"frame_id": "f000002", "path": "frames/f000002.jpg", "timestamp_sec": 2.0}
  ]
}
```

Relative frame paths are resolved relative to the manifest file. Each frame is sent to the model with a text prefix like `[frame_id=f000001, timestamp=00:00.00]`.

You can build a manifest from a frame directory:

```powershell
python build_frame_manifest.py "C:\path\to\frames" --fps 4 --video-id "demo_video"
```

For a quick smoke test, create a smaller manifest:

```powershell
python build_frame_manifest.py "C:\path\to\frames" --fps 4 --every-n 4 --max-frames 30 --output "C:\path\to\frames\frames_manifest_smoke.json"
```

For coarse scanning on 4fps frames, use one frame every 4 seconds:

```powershell
python build_frame_manifest.py "C:\path\to\frames" --fps 4 --every-n 16 --output "C:\path\to\frames\frames_manifest_coarse_4s.json"
```

After coarse scanning, build dense per-event manifests from the full manifest:

```powershell
python build_event_interval_manifests.py `
  --full-manifest "C:\path\to\frames\frames_manifest.json" `
  --events "outputs\coarse\events.json" `
  --output-dir "outputs\dense_event_manifests" `
  --padding-sec 2
```

Those detailed manifests use every frame in the selected event interval.

## Style control

Built-in styles live in `configs/styles.json`:

- `broadcast_professional`: calm professional broadcast style.
- `short_passionate`: high-energy short-video style.
- `tactical_analysis`: tactical review style.

To create your own style, copy one JSON object from `configs/styles.json` into a new file and change:

- `style_id`
- `description`
- `prompt_injection`
- `temperature`
- `top_p`
- `max_tokens`
- `thinking_mode`

Then pass that file path to `load_style()` or `run_pipeline(..., style_id_or_path="my_style.json")`.

## Low-frame-rate scanning

The scanner uses a sliding window over frame images:

- `window_size_frames`: how many frames the model reads in one call. Larger windows reduce calls but make event boundaries rougher.
- `stride_frames`: how far the window moves each step. Smaller strides are more stable but cost more API calls.

Default:

```python
ScanConfig(window_size_frames=6, stride_frames=3)
```

For rough early exploration, use larger values such as `8/4` or `10/5`. For important clips, use smaller values such as `4/2`.

The scanner marks each frame as either commentary-worthy or `no_event`. Event intervals are expanded from the first needed frame back to the previous non-needed frame, and from the last needed frame forward to the next non-needed frame.

After frame-level aggregation, the scanner also performs event-level merging:

- Same event types are merged when their time ranges overlap or are close enough.
- A `goal` followed by nearby `celebration_or_replay` is merged into one goal event.
- Merged events keep `phases`, so a goal can contain both `live_goal` and `replay` phases for dual commentary.

Relevant merge parameters:

```python
ScanConfig(
    merge_gap_sec=4.0,
    goal_replay_merge_gap_sec=30.0,
)
```

## Event types

Allowed event types live in `configs/event_types.json`. Each event now has an English decision description so the visual classifier has clearer boundaries:

```json
{
  "id": "goal",
  "name": "Goal",
  "description": "The ball appears to cross the goal line, the scoreboard changes, or players clearly celebrate a scored goal.",
  "positive_cues": ["ball inside or behind the net", "scoreboard increment"],
  "negative_cues": ["ordinary shot before the result is known", "near miss"]
}
```

The model must return one of these values. If it returns an illegal type, the scanner performs one JSON repair request. If repair fails, that window is recorded in `window_errors`.

When adding event types, update `configs/event_types.json` and keep `no_event`. Use English descriptions and cue lists because they are injected into the model prompt. The downstream merger and commentary generator do not need code changes for ordinary type additions.

## Commentary generation

The default pipeline and `generate_commentary()` now use visual commentary generation. It reads:

- event type
- event start/end seconds
- evidence frame IDs
- evidence summary
- selected keyframes from the event interval and each phase interval
- selected style profile

It returns segments with:

- `talk_start_sec`
- `talk_end_sec`
- `commentary_text`
- optional `subtitle_lines`

By default, the speaking interval equals the detected event interval.

`generate_visual_commentary()` sends structured event data plus selected visual frames to the model. It does not send every frame in a long event; it samples representative frames from each phase interval and the overall event interval, while prioritizing evidence frames. Tune this with:

```python
VisualCommentaryConfig(
    max_frames_per_event=12,
    max_frames_per_phase=4,
)
```

The previous summary-only behavior is still available as `generate_commentary_from_summary()`.

## Bilingual commentary

The bilingual module keeps English generation and Chinese translation decoupled:

- `generate_bilingual_commentary()` first generates English commentary with visual frames, then translates each segment into Chinese.
- `translate_commentary_to_chinese()` translates an existing `CommentaryResult`, so you can reuse an existing `commentary.json` without rerunning visual generation.
- `run_bilingual_pipeline()` runs scan, English visual generation, and Chinese translation in one call.

The translation prompt injects the selected style, but meaning fidelity has priority. It preserves event IDs, event types, timing, names, teams, scores, numbers, and uncertainty from the English source.

Translation tuning:

```python
TranslationConfig(
    target_language="Simplified Chinese",
    target_language_code="zh-CN",
    temperature=0.2,
    top_p=0.9,
    max_tokens=1600,
    thinking_mode=False,
)
```

The bilingual output nests both languages under each segment:

```json
{
  "event_id": "E001",
  "event_type": "goal",
  "english": {"commentary_text": "...", "subtitle_lines": []},
  "chinese": {"commentary_text": "...", "subtitle_lines": []}
}
```

## Full run with progress and resume

For a full-video run with live progress, ETA, and checkpoint resume:

```powershell
$env:INTERN_API_KEY="your_key"
python run_full_bilingual_with_progress.py --run-name "full_latest_bilingual" --concurrency 16
```

The runner writes:

- `progress.log`: human-readable progress with current step, count, average call time, and ETA.
- `progress.jsonl`: machine-readable progress records.
- `cache/<stage>/call_000001.json`: cached model responses for breakpoint resume.
- `coarse/events.json`: full-video coarse scan result.
- `dense/<event>/events.json`: dense scan result for each coarse event interval.
- `commentary/<event>/commentary_bilingual.json`: per-event bilingual commentary.
- `commentary_bilingual.json`: aggregated bilingual commentary.

Resume is enabled by default. If the process is interrupted, run the same command with the same `--run-name`; completed stages and cached model calls are reused. Use `--no-resume` only when you want to ignore checkpoints.

`--concurrency` controls independent model calls. Coarse scan windows and dense scan windows run concurrently. For bilingual generation, English must be generated before the matching Chinese translation for the same event, but different events can run concurrently.

The runner also staggers request starts and retries rate-limit errors by default. Tune this with `--request-stagger-sec`, `--max-retries`, `--retry-base-sec`, and `--retry-max-sec` if the API reports requests are too frequent.

## Tests

Run local tests without a real API key:

```powershell
python -m unittest discover -s tests -v
```

Optional real API smoke test:

```powershell
$env:INTERN_API_KEY="your_key"
$env:RUN_REAL_API_TESTS="1"
python -m unittest discover -s tests -v
```
