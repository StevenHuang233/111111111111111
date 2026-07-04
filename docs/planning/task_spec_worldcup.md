# Task Spec: World Cup Video Commentary Harness

Last updated: 2026-07-04

## Objective

Build a runnable Agentic Harness for the World Cup video commentary direction.

Target match from the official statement:

> 2026 Canada/Mexico/USA World Cup Group E first-round match: Germany defeats Curacao 7:1.

The harness should process match video materials and generate accurate, continuous, energetic Chinese commentary text. It may additionally output structured content for dubbing, subtitles, and highlight narration.

## Hard Constraints

- Final task run, live demo, and judging-test core LLM calls must use Intern-S2-Preview.
- Development may use other tools or models, but final code must be switchable to Intern-S2-Preview.
- API Base URL and API Key must be configurable through standard settings such as environment variables.
- Do not commit video download credentials, API keys, or the original large video.
- Do not rely on third-party commercial model APIs in the final judged run.

## Input

Minimum:

- One match video or clipped segment.

Recommended practical input for MVP:

- A compressed proxy video.
- Extracted key frames or low-FPS frame sequence.
- Optional manually supplied match metadata, such as teams, score context, known player names, and clip time range.

Local resource layout:

- Original 7GB video: `source/raw/` or external disk, ignored by Git.
- Compressed proxy: `source/compressed/`, ignored by Git.
- Extracted frames: `source/frames/`, ignored by Git.
- Audio track if needed: `source/audio/`, ignored by Git.

## Output

Minimum required output:

- Key event list with timestamps.
- Chinese energetic commentary script.
- Trace showing how the harness moved from input to output.

Recommended structured output:

- `events.json`: event timeline with timestamp, event type, confidence, evidence, and notes.
- `commentary.md`: continuous Chinese commentary script.
- `segments.json`: clip-level narration blocks for dubbing/highlight editing.
- `subtitles.srt`: optional subtitle track.
- `eval_report.md`: event and commentary quality checks.
- `trace.jsonl`: model calls, tool calls, token cost, runtime, failures, and revisions.

## Proposed Pipeline

```text
video
  -> compression/proxy generation
  -> frame extraction
  -> visual evidence extraction
  -> event timeline construction
  -> Intern-S2 commentary planning
  -> Intern-S2 style-controlled script generation
  -> factual/style verification
  -> final commentary package
```

## Evaluation

Quality:

- Event recall on known goals, shots, cards, fouls, substitutions, and other key moments.
- Timestamp accuracy.
- Factual consistency between commentary and event timeline.
- Commentary fluency, excitement, rhythm, and现场感.
- Human review score for usefulness as dubbing/subtitle/highlight narration material.

Project runtime cost:

- Intern-S2 input/output tokens.
- Number of model calls.
- Video processing time.
- Tool calls.
- Failure and retry count.

Assistant collaboration cost:

- Token/time cost used by coding assistants during implementation.
- Rework caused by unclear requirements.

## Current MVP Scope

Do not attempt full professional broadcast commentary for the entire match on the first pass.

MVP target:

> Given a short clip or selected match segment, extract representative frames, build a timestamped event timeline, use Intern-S2-Preview to generate a grounded energetic Chinese commentary script, verify unsupported claims, and export script plus trace.

Full-match support should be implemented as batching over clips only after the MVP is stable.

## Risks

| Risk | Mitigation |
| --- | --- |
| 7GB video too large for local disk and memory | Use external or D drive storage, generate compressed proxy, avoid DaVinci cache on C drive, process in chunks. |
| Frame extraction creates too many files | Extract sparse FPS first, then targeted dense frames near candidate events. |
| Intern-S2 has limited direct video capability | Convert video into structured visual evidence and event timelines before model calls. |
| Commentary hallucination | Require named facts to come from metadata or detected evidence; run verifier before final output. |
| Copyright or privacy | Do not commit original video or extracted frames; use local ignored folders. |

