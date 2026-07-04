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

## Runtime Modes

| Mode | EN Purpose | 中文目的 |
| --- | --- | --- |
| Smoke | Use a tiny manifest, for example 30 frames, to verify imports, config, API connectivity, output schema, and trace writing. | 用很小的 manifest，例如 30 帧，验证导入、配置、API 连通性、输出结构和 trace 写入。 |
| Coarse scan | Use sparse frames to find candidate events at lower cost. | 用稀疏帧低成本发现候选事件。 |
| Dense event pass | Revisit only candidate event intervals with denser frames. | 只对候选事件区间使用更密集帧复查。 |
| Full bilingual run | Use `run_full_bilingual_with_progress.py` to run coarse scan, dense passes, bilingual commentary, aggregation, progress logging, resume, concurrency, request staggering, and retry/backoff. | 用 `run_full_bilingual_with_progress.py` 串起粗扫、dense 复查、双语解说、聚合、进度记录、续跑、并发、请求错峰和 retry/backoff。 |

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

Current extension:

> The repository now contains a full-match-style resumable runner. It should be treated as an integration path after smoke tests pass, not as a reason to skip small verified demos.

中文补充：

> 当前仓库已经有接近全片运行的可续跑 runner。它应作为 smoke 通过后的集成路径，而不是跳过小规模可验证 demo 的理由。

Latest update:

> The full runner now supports concurrency with request staggering and retry/backoff. It improves throughput, but the pitch should still show at least one small verified run before claiming reliability.

最新更新：

> 全流程 runner 现在支持并发、请求错峰和 retry/backoff。它提升吞吐，但路演前仍应至少展示一个小规模验证通过的运行，再宣称可靠性。

## Risks

| Risk | Mitigation |
| --- | --- |
| 7GB video too large for local disk and memory | Use external or D drive storage, generate compressed proxy, avoid DaVinci cache on C drive, process in chunks. |
| Frame extraction creates too many files | Extract sparse FPS first, then targeted dense frames near candidate events. |
| Intern-S2 has limited direct video capability | Convert video into structured visual evidence and event timelines before model calls. |
| Commentary hallucination | Require named facts to come from metadata or detected evidence; run verifier before final output. |
| Copyright or privacy | Do not commit original video or extracted frames; use local ignored folders. |
| Resume appears implemented but unverified locally | Prove it with a small interrupted run before using it as a pitch claim. |
| 可续跑看起来已实现但本机未验证 | 先用小任务中断重跑验证，再在路演中宣称。 |
| Concurrent run may hit API limits or produce hard-to-debug ordering issues | Start with low concurrency, keep request staggering, inspect logs, and verify output ordering. |
| 并发运行可能触发 API 限流或输出顺序问题 | 从低并发开始，保留请求错峰，检查日志并核对输出顺序。 |

