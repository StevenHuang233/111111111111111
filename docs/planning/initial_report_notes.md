# Initial Report Notes / 初步汇报记录

Last updated: 2026-07-04

## Core Claim / 核心主张

EN: We built a World Cup video commentary harness around Intern-S2-Preview. The system decomposes long match video into frame evidence and event intervals, generates timestamped bilingual commentary, and records progress, cache, resume, concurrency, and verification evidence.

ZH: 我们围绕 Intern-S2-Preview 构建了一个世界杯视频解说 Harness。系统把长比赛视频拆成帧证据和事件区间，生成带时间戳的双语解说，并记录进度、缓存、续跑、并发和核验证据。

## Current Evidence / 当前证据

| Evidence | EN | ZH |
| --- | --- | --- |
| Preprocessing | 1080p 25fps source video was extracted to 26612 JPG frames at 4fps outside Git. | 1080p 25fps 原视频已按 4fps 抽取 26612 张 JPG，保存在 Git 外。 |
| Harness code | Repository includes frame manifest builder, event scanner, visual commentary, bilingual translation, tracing, and full-run runner. | 仓库包含 frame manifest 构建、事件扫描、视觉解说、双语翻译、trace 和全流程 runner。 |
| Long-run controls | Latest runner supports progress logs, JSONL records, cache, checkpoint resume, concurrency, request staggering, and retry/backoff. | 最新 runner 支持进度日志、JSONL 记录、缓存、checkpoint 续跑、并发、请求错峰和 retry/backoff。 |
| Audio reference | ASR reference package has 2323 timestamped subtitle segments for weak evaluation. | ASR 参考包包含 2323 条带时间戳字幕段，可作为弱评估信号。 |
| Safety | `.gitignore` and planning docs keep videos, frames, outputs, and secrets outside Git. | `.gitignore` 和规划文档要求视频、帧、输出和密钥不进 Git。 |
| Submission tracking | Required deliverables and Intern-S2 feedback questions are tracked in `submission_checklist.md` and `intern_s2_feedback_table.md`. | 必交材料和 Intern-S2 反馈问题已记录在 `submission_checklist.md` 和 `intern_s2_feedback_table.md`。 |

## Current Gaps / 当前缺口

| Gap | Needed Before Strong Claim | 中文 |
| --- | --- | --- |
| Local environment | Install dependencies and rerun no-API unit tests. | 安装依赖并重跑无 API 单测。 |
| Model smoke | Run a tiny Intern-S2 text/image smoke with real key. | 用真实 key 跑极小 Intern-S2 文本/图像 smoke。 |
| Resume proof | Interrupt and resume a small run with the same `--run-name`. | 用相同 `--run-name` 中断并恢复一个小任务。 |
| Concurrency proof | Run low-concurrency smoke and inspect ordering/rate-limit logs. | 跑低并发 smoke，检查顺序和限流日志。 |
| Fact verification | Manually verify one demo event against video time, match clock, and scoreboard. | 人工核对一个 demo 事件的视频时间、比赛计时和比分牌。 |
| Final materials | Cover, title, intro, README/package docs, demo video, contribution PPT, pitch/Q&A. | 封面、标题、简介、说明文档、demo 视频、贡献 PPT、路演/Q&A。 |

## 30-Second Draft / 30 秒稿草案

EN: Our project turns a long World Cup match video into timestamped commentary through an Agentic Harness rather than a one-shot prompt. It extracts frame evidence, builds coarse-to-dense event timelines, asks Intern-S2-Preview to generate grounded bilingual commentary, and records progress, cache, resume, concurrency, and verification logs so the output is inspectable and recoverable.

ZH: 我们的项目不是一次性 prompt，而是把世界杯长视频变成带时间戳解说的 Agentic Harness。它抽取帧证据，构建从粗扫到 dense 复查的事件时间线，再让 Intern-S2-Preview 基于证据生成双语解说，并记录进度、缓存、续跑、并发和核验日志，让结果可检查、可恢复。

## Do Not Overclaim / 不要过度宣称

EN:

- Do not claim perfect full-match professional commentary until a full run is verified.
- Do not claim reliable possession or tactical analytics unless metrics are computed.
- Do not invent player names or match facts not visible in video or provided metadata.

ZH:

- 全片运行验证前，不宣称完美职业级全场解说。
- 未计算指标前，不宣称可靠控球率或战术分析。
- 视频或元数据未支持的人名和比赛事实，不编造。
