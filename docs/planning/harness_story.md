# Harness Story / Harness 叙事

Last updated: 2026-07-04

## One-Sentence Claim / 一句话主张

EN: Our project is not a prompt wrapper. It is a video-to-commentary harness that turns match video into timestamped evidence, asks Intern-S2-Preview to write grounded commentary, verifies facts, and records the full process.

ZH: 我们的项目不是简单的 prompt 包装，而是一个“视频到解说稿”的 Harness：先把比赛视频转成带时间戳的证据，再让 Intern-S2-Preview 生成有依据的解说，最后核实事实并记录全过程。

## What Is A Harness / 什么是 Harness

EN: A harness is the engineering layer around a model that makes it reliable on real tasks. It provides task decomposition, tools, context management, verification, memory, safety boundaries, and iteration.

ZH: Harness 是模型外层的工程系统，让模型能稳定完成真实任务。它负责任务拆解、工具调用、上下文管理、结果核验、记忆、安全边界和迭代优化。

References / 参考材料:

- The Anatomy of an Agent Harness: <https://www.langchain.com/blog/the-anatomy-of-an-agent-harness>
- Harness design for long-running application development: <https://www.anthropic.com/engineering/harness-design-long-running-apps>
- 智能体 Harness 工程指南: <https://yeasy.gitbook.io/harness_engineering_guide>

## Our Target Agent / 我们的目标任务 Agent

EN: The target agent is the World Cup commentary harness. Its final product is a timestamped Chinese commentary script.

ZH: 目标任务 Agent 是世界杯视频解说 Harness。最终产出是带时间戳的中文解说稿。

Input / 输入:

- EN: Match video, extracted frames, optional metadata, and known facts.
- ZH: 比赛视频、抽帧、可选元数据和已知事实。

Output / 输出:

- EN: Timestamped event notes, commentary script, verification report, and trace.
- ZH: 带时间戳的事件笔记、解说稿、事实核验报告和运行轨迹。

## Harness Components / Harness 组成

| Component | EN | ZH |
| --- | --- | --- |
| Agent loop | Plan, call tools, observe results, revise, and finalize. | 规划、调用工具、观察结果、修订、最终输出。 |
| Tools | Video frame extraction, frame indexing, OCR/manual evidence, search, script export. | 视频抽帧、帧索引、OCR/人工证据、搜索、脚本导出。 |
| Context | Keep only relevant frames, event notes, and verified facts in the model context. | 只把相关帧、事件笔记和已核实事实放入模型上下文。 |
| Memory | Store lessons, style rules, event templates, and failure cases. | 记录经验、风格规则、事件模板和失败案例。 |
| Skills | Reusable procedures for kickoff, attack, defense, replay, foul, goal, and closing narration. | 开场、进攻、防守、回放、犯规、进球、收尾等可复用流程。 |
| Verification | Check timestamp consistency, score consistency, unsupported names, and unsupported facts. | 检查时间戳、比分、人名和事实是否有依据。 |
| Trace | Save what was seen, what was inferred, what Intern-S2 generated, and what was corrected. | 保存看到什么、推断什么、Intern-S2 生成什么、修正了什么。 |
| Safety | Keep large media and secrets outside Git; isolate local paths and API keys. | 大媒体和密钥不进 Git；隔离本地路径和 API Key。 |

## Current Built Evidence / 当前已实现证据

EN: The codebase now has a concrete long-running harness entry point: `run_full_bilingual_with_progress.py`. It turns a full frame manifest and a coarse manifest into coarse event detection, dense per-event manifests, per-event bilingual commentary, an aggregated bilingual commentary JSON, progress logs, cached API responses, and checkpoint reuse.

ZH: 当前代码库已经有一个长任务 Harness 入口：`run_full_bilingual_with_progress.py`。它把全量 frame manifest 和 coarse manifest 转换为粗粒度事件检测、事件级 dense manifest、逐事件双语解说、聚合双语解说 JSON、进度日志、API 响应缓存和 checkpoint 复用。

EN: This is useful for the pitch because it makes "harness" visible: the model is only one component; the surrounding system schedules stages, records progress, limits repeated calls, and can resume after interruption.

ZH: 这对路演很有用，因为它让“harness”可见：模型只是其中一个组件，外围系统负责任务阶段调度、进度记录、减少重复调用，并在中断后恢复。

## Why Intern-S2-Preview Matters / Intern-S2-Preview 的角色

EN: Intern-S2-Preview is the core reasoning and generation model in the final run. It should not be asked to magically understand a two-hour video directly. The harness prepares structured evidence and asks the model to reason and write from that evidence.

ZH: Intern-S2-Preview 是最终运行中的核心推理和生成模型。我们不应让它直接“凭空看懂两小时视频”，而是由 Harness 准备结构化证据，再让模型基于证据推理和写作。

## What We Can Honestly Claim / 我们可以诚实宣称什么

EN: We can claim a complete, traceable pipeline from match video to timestamped commentary. We should not claim perfect professional live commentary or fully automatic deep tactical analysis unless the evidence supports it.

ZH: 我们可以宣称完成了从比赛视频到带时间戳解说稿的完整可追踪流程。除非有证据支撑，不应宣称达到完美职业解说或完全自动深度战术分析。

## Differentiation / 区分度

EN:

- We separate video time from match clock.
- We ground commentary in frame evidence and known facts.
- We provide resumable long-running execution instead of a one-shot prompt.
- We record failures and costs as part of the harness.
- We treat our own coding-agent workflow as a parallel harness, learning from mistakes such as Git object bloat and large-file isolation.

ZH:

- 区分视频时间和比赛计时。
- 解说内容基于帧证据和已知事实。
- 提供可续跑的长任务执行，而不是一次性 prompt。
- 把失败、成本和修正过程作为 Harness 的一部分记录。
- 把协作 coding agent 工作流也视作一个并行 Harness，从 Git 大对象事故、大文件隔离等问题中沉淀方法。

