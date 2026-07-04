# Judging And Execution Plan / 评审标准与执行计划

Last updated: 2026-07-04

## Current Situation / 当前情况

EN: Less than 15 hours remain. Humans leave around 22:00 and resume around 09:00 the next day. The priority is a complete runnable flow, complete submission materials, and a clear harness story.

ZH: 剩余时间不到 15 小时。人约 22:00 离开，第二天 09:00 恢复工作。优先级是完整可运行流程、完整提交材料和讲得清楚的 Harness 叙事。

## Implementation Evidence / 当前实现证据

| Item | EN Status | 中文状态 |
| --- | --- | --- |
| Frame preprocessing | 4fps extraction has produced 26612 JPG frames from the 1080p 25fps source video, stored outside Git. | 已从 1080p 25fps 原视频按 4fps 抽取 26612 张 JPG，存放在 Git 外。 |
| Smoke manifest path | README documents `build_frame_manifest.py --max-frames 30` for quick smoke tests. | README 已写明用 `build_frame_manifest.py --max-frames 30` 做快速 smoke。 |
| Full-run orchestration | `run_full_bilingual_with_progress.py` provides coarse scan, dense event manifests, per-event bilingual commentary, and final aggregation. | `run_full_bilingual_with_progress.py` 提供粗扫、事件级 dense manifest、逐事件双语解说和最终聚合。 |
| Resume and progress | The runner writes `progress.log`, `progress.jsonl`, cached API calls, stage outputs, and reuses checkpoints by default. | runner 写出 `progress.log`、`progress.jsonl`、API 调用缓存和阶段产物，并默认复用 checkpoint。 |
| Concurrency | Not claimed yet. Sequential resumable execution is safer until rate limits, cache consistency, and output ordering are tested. | 暂不宣称并发。先以顺序可续跑为稳妥路线，等限流、缓存一致性和输出顺序验证后再加。 |

## Immediate Verification Targets / 近期验证目标

EN:

- Run local unit tests: `python -m unittest discover -s tests -v`.
- Build a 30-frame smoke manifest from the extracted frames.
- Run the smallest Intern-S2 real API smoke when the key is ready.
- Interrupt and rerun a small job with the same `--run-name` to prove checkpoint resume.
- Compare video timestamp, visible match clock, scoreboard, and generated text for at least one demo window.

ZH:

- 运行本地单测：`python -m unittest discover -s tests -v`。
- 从抽帧目录生成 30 帧 smoke manifest。
- API key 准备好后跑最小 Intern-S2 真实 smoke。
- 对小任务中断后用相同 `--run-name` 重跑，证明 checkpoint 续跑。
- 至少对一个 demo 窗口核对视频时间、画面比赛计时、比分牌和生成解说。

## Judging Requirements / 题目要求整理

| Requirement | EN Action | 中文行动 |
| --- | --- | --- |
| Runnable harness prototype | Provide source code and run instructions. | 提供可运行原型、源码和运行说明。 |
| Intern-S2-Preview final core model | Expose API Base URL and Key through config. | 通过配置暴露 API Base URL 和 Key。 |
| Complete selected-task output | Produce timestamped World Cup commentary script and supporting event notes. | 产出带时间戳的世界杯解说稿和事件笔记。 |
| Semantic plagiarism check | Keep implementation original and document our design. | 代码保持原创，并说明我们的设计。 |
| Intern-S2 capability feedback | Fill the required feedback table. | 填写 Intern-S2 能力反馈表。 |
| Presentation | Explain harness design, implementation, result, analysis, and team contribution. | 汇报 Harness 设计、实现、结果、分析和分工。 |
| Bonus demo | Show input-to-output flow or recorded fast-forward. | 展示从输入到输出的流程，长任务可录屏快进。 |
| Bonus mechanisms | Skills, memory, sandbox, trace, evaluation, cost control. | Skills、Memory、Sandbox、Trace、评估、成本控制。 |

## Scoring-Oriented Priorities / 面向评分的优先级

| Priority | EN | ZH |
| --- | --- | --- |
| P0 | Do not lose basic requirements: runnable flow, config, output, docs, presentation. | 不能丢基础要求：可运行、可配置、有产出、有文档、能汇报。 |
| P1 | Make harness design explicit: tools, loop, trace, verification, memory/skills story. | 把 Harness 设计讲清楚：工具、循环、轨迹、核验、记忆/技能。 |
| P2 | Improve demo appeal: video frames, timestamps, scoreboard evidence, energetic commentary. | 提升 Demo 表现：帧画面、时间戳、比分牌证据、激情解说。 |
| P3 | Add advanced analysis: tempo, possession, richer scene types, better verification. | 加进阶分析：节奏、控球、更多场景类型、更好核验。 |

## Phase Plan / 阶段计划

### Phase 1: Stabilize Inputs / 阶段一：稳定输入

EN:

- Keep original video and extracted frames outside Git.
- Record frame extraction facts: 4fps, 26612 frames, output path.
- Define video time vs match clock mapping.

ZH:

- 原视频和抽帧全部放在 Git 外。
- 记录抽帧事实：4fps、26612 帧、输出路径。
- 明确视频时间和比赛计时的映射。

Exit criteria / 完成标准:

- EN: Frame directory exists and can be sampled.
- ZH: 抽帧目录存在，并能抽样查看。

### Phase 2: Build Minimum Evidence / 阶段二：建立最小证据链

EN:

- Select representative frames or windows.
- Identify visible scoreboard changes and key scene categories.
- Record evidence in a simple timeline.

ZH:

- 选择代表性帧或时间窗口。
- 识别比分牌变化和关键场景类型。
- 用简单时间线记录证据。

Exit criteria / 完成标准:

- EN: A small evidence timeline exists for demo windows.
- ZH: 至少有一份可用于 Demo 的小型证据时间线。

### Phase 3: Generate Commentary / 阶段三：生成解说稿

EN:

- Use Intern-S2-Preview as the core final model.
- Generate timestamped commentary from evidence, not from unsupported guesses.
- Keep output structured for subtitles or dubbing.
- Prefer the existing resumable full-run runner for integrated demos after smoke tests pass.

ZH:

- 最终核心模型使用 Intern-S2-Preview。
- 基于证据生成带时间戳解说，不凭空猜。
- 输出结构适合字幕或配音。
- smoke 通过后，优先用已有可续跑全流程 runner 做集成 demo。

Exit criteria / 完成标准:

- EN: A timestamped script exists and can be shown.
- ZH: 有一份可展示的带时间戳解说稿。

### Phase 4: Verify And Revise / 阶段四：核验与修订

EN:

- Check score, time, event type, unsupported names, and unsupported facts.
- Keep a correction log.
- Verify that resume logs and cached calls match the actual produced commentary.

ZH:

- 检查比分、时间、事件类型、无依据人名和无依据事实。
- 保留修订记录。
- 核对续跑日志、缓存调用和最终解说是否一致。

Exit criteria / 完成标准:

- EN: The demo output has a verification note.
- ZH: Demo 输出附带核验说明。

### Phase 5: Submit And Present / 阶段五：提交与展示

EN:

- Package code, docs, title, intro, demo video, contribution slides, and Intern-S2 feedback.
- Prepare 30-second and 10-15 minute stories.
- Use progress logs, traces, and checkpoint resume as concrete harness evidence.

ZH:

- 整理代码、文档、标题、简介、Demo 视频、贡献 PPT 和 Intern-S2 反馈。
- 准备 30 秒版本和 10-15 分钟版本。
- 用进度日志、trace 和 checkpoint 续跑作为 Harness 的具体证据。

Exit criteria / 完成标准:

- EN: A teammate can run or explain the whole flow from docs.
- ZH: 队友能根据文档运行或讲清楚整个流程。

