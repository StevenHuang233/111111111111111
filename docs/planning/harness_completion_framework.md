# Harness Completion Framework / Harness 完成框架

Last updated: 2026-07-04

EN: This file is the working contract for turning scattered development into a complete hackathon harness. It does not force teammates to change their short-time coding style; it records what each part must eventually satisfy.

ZH: 本文件是把零散开发收束成完整黑客松 Harness 的工作契约。它不强行改变队友在时间紧张下“想到哪里写哪里”的方式，而是记录每个部件最终必须满足什么。

## Applicability / 适用边界

EN: General Agentic Harness ideas such as long-term memory, autonomous tool search, or large skill libraries are useful references, but not all are necessary for this World Cup commentary task. Our task needs stronger emphasis on video evidence, timestamp alignment, retry/resume, cost control, and fact verification.

ZH: 通用 Agentic Harness 中的长期记忆、自主工具搜索、大型技能库等思想可以借鉴，但并非全部适用于世界杯解说任务。我们的重点更应放在视频证据、时间戳对齐、retry/续跑、成本控制和事实核验。

## Layered Components / 分层部件

| Layer | Required Output | Validation Gate | Pitch Evidence |
| --- | --- | --- | --- |
| Data boundary / 数据边界 | Video path, frame directory, manifests, ignored large files. / 视频路径、抽帧目录、manifest、大文件忽略规则。 | No video/frame/secrets in Git; manifest paths resolve locally. / Git 中没有视频/帧/密钥；manifest 路径本机可解析。 | `.gitignore`, `.env.example`, manifest sample. |
| Preprocessing / 预处理 | 4fps frames, smoke manifest, coarse manifest, optional dense event manifests. / 4fps 帧、smoke manifest、coarse manifest、可选 dense manifest。 | Sample frames readable; frame ID maps to video time as `frame_id / 4`. / 能读取样例帧；`frame_id / 4` 映射视频时间。 | Frame count, sample image, preprocessing notes. |
| Evidence extraction / 证据抽取 | Event candidates with timestamps, event types, confidence, evidence frames. / 带时间、类型、置信度、证据帧的事件候选。 | At least one demo window manually checked against visible scoreboard/match clock. / 至少一个 demo 窗口与比分牌/比赛计时人工核对。 | `events.json`, annotated screenshots. |
| Commentary generation / 解说生成 | Timestamped English/Chinese segments. / 带时间戳中英解说片段。 | No unsupported names, scores, or tactical facts; uncertainty preserved. / 无无依据人名、比分或战术事实；不确定性被保留。 | `commentary_bilingual.json`, demo clip. |
| Audio reference / 音频参考 | ASR subtitle reference and weak evaluation signal. / ASR 字幕参考和弱评估信号。 | Compare key event windows without treating ASR as gold answer. / 对比关键事件窗口，但不把 ASR 当唯一标准答案。 | `reference/audio_asr/germany_curacao/`. |
| Orchestration / 调度 | Coarse-to-dense pipeline, progress logs, checkpoints, cache, concurrency knobs. / 粗扫到 dense 流程、进度日志、checkpoint、缓存、并发参数。 | Small smoke run completes; interrupted small run resumes; concurrent small run logs cleanly. / 小 smoke 跑通；小任务中断可续跑；小并发日志干净。 | `progress.log`, `progress.jsonl`, cache counts. |
| Verification / 核验 | Fact check report and correction notes. / 事实核验报告和修正记录。 | Every strong pitch claim points to video evidence, trace, test, or metric. / 每个强主张对应视频证据、trace、测试或指标。 | `eval_report.md`, Q&A notes. |
| Delivery / 交付 | Code zip, docs, cover, title, intro, demo video, contribution PPT, pitch/Q&A. / 代码 zip、文档、封面、标题、简介、demo 视频、贡献 PPT、路演/Q&A。 | Fresh checkout demo works; submission checklist complete. / 干净 checkout demo 可运行；提交清单完成。 | `submission/` package. |

## Must/Should/Could/Later / 优先级

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Runnable smoke path, timestamped commentary output, trace/progress, no secrets/large files in Git, submission materials. | 可运行 smoke 路径、带时间戳解说输出、trace/进度、Git 中无密钥/大文件、提交材料。 |
| Should | Resume proof, small concurrent proof, basic fact verification, bilingual docs, contribution evidence. | 续跑证明、小并发证明、基础事实核验、双语文档、贡献证据。 |
| Could | Better event taxonomy, subtitle export, cover image polish, demo narration polish. | 更细事件类型、字幕导出、封面图优化、demo 旁白优化。 |
| Later | Deep tactical analytics, full possession estimates, automatic player identification, broad skill library. | 深度战术分析、完整控球估计、自动球员识别、大型技能库。 |

## Validation Gates / 验证关卡

| Gate | Minimum Check | Pass Evidence |
| --- | --- | --- |
| G0 Repo hygiene / 仓库卫生 | No staged file over 50MB; `.env` ignored. / 无超过 50MB 的 staged 文件；`.env` 被忽略。 | Large-file scan output. |
| G1 Environment / 环境 | `pip install -r requirements.txt`; no-API unit tests import repo tests. / 安装依赖；无 API 单测能导入仓库测试。 | Test output or blocker note. |
| G2 Data / 数据 | Smoke manifest from extracted frames exists. / 从抽帧生成 smoke manifest。 | Manifest path and frame count. |
| G3 Model smoke / 模型 smoke | Intern-S2 text/image call succeeds on a tiny sample. / Intern-S2 在极小样本上文本/图像调用成功。 | Smoke output and trace. |
| G4 Pipeline / 流程 | Small pipeline produces events and commentary. / 小流程产出事件和解说。 | `events.json`, `commentary_bilingual.json`. |
| G5 Resume / 续跑 | Same `--run-name` reuses completed outputs/cache after interruption. / 中断后同名运行复用产物/缓存。 | `checkpoint_hit` or `api_call_cached` logs. |
| G6 Concurrency / 并发 | Low-concurrency run completes without rate-limit failure or ordering bugs. / 低并发运行无严重限流失败或顺序错误。 | `progress.jsonl`, final ordered output. |
| G7 Fact check / 事实核验 | Demo window facts match video evidence or are marked unknown. / demo 窗口事实匹配视频证据，或标记未知。 | Verification note. |
| G8 Submission / 提交 | Required package complete and README matches commands. / 必交包完整，README 与命令一致。 | Submission checklist. |

## Tomorrow Constraint / 明天约束

EN: Before tomorrow's pitch, assume only about 6 effective hours remain. After reserving time for slides, video, and rehearsal, development should be treated as finishing work: fix blockers, run validation gates, package evidence, and avoid large rewrites.

ZH: 明天路演前按只有约 6 个有效小时估算。扣除 PPT、视频和排练后，开发应视为收尾：修 blocker、跑验证关卡、打包证据，避免大改。
