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
    dump_commentary_result,
    dump_scan_result,
    run_pipeline,
)

tracker = TraceRecorder()
result = run_pipeline(
    manifest_path="frames_manifest.json",
    style_id_or_path="broadcast_professional",
    scan_config=ScanConfig(window_size_frames=6, stride_frames=3),
    tracker=tracker,
)

dump_scan_result(result.scan, "outputs/events.json")
dump_commentary_result(result.commentary, "outputs/commentary.json")
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
- `generate_commentary.event -> prepare_model_call`

Each step includes an index, elapsed seconds, action name, and structured details such as frame IDs, window ranges, event counts, phase types, and merge counts.

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

`generate_commentary()` reads:

- event type
- event start/end seconds
- evidence frame IDs
- evidence summary
- selected style profile

It returns segments with:

- `talk_start_sec`
- `talk_end_sec`
- `commentary_text`
- optional `subtitle_lines`

By default, the speaking interval equals the detected event interval.

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
