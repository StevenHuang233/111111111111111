# Docs Index / 文档索引

Last updated: 2026-07-04

## Read First / 优先阅读

| File | EN | ZH |
| --- | --- | --- |
| [harness_story.md](harness_story.md) | Core story: what harness means and what we built. | 核心叙事：Harness 是什么，我们做了什么。 |
| [judging_and_execution_plan.md](judging_and_execution_plan.md) | Requirements, priorities, and phased plan. | 题目要求、优先级和分阶段计划。 |
| [harness_completion_framework.md](harness_completion_framework.md) | Layered design and validation gates for a complete harness. | 完整 Harness 的分层设计和验收关卡。 |
| [initial_report_notes.md](initial_report_notes.md) | Current presentation claims, evidence, and gaps. | 当前汇报主张、证据和缺口。 |
| [agent_boundary_and_fact_checking.md](agent_boundary_and_fact_checking.md) | Distinguishes coding agent and target agent; defines fact policy. | 区分协作 coding agent 和目标任务 agent；定义事实策略。 |
| [task_spec_worldcup.md](task_spec_worldcup.md) | World Cup task input, output, constraints, risks. | 世界杯任务输入、输出、约束和风险。 |
| [video_preprocessing_guide.md](video_preprocessing_guide.md) | Frame extraction facts and next data steps. | 抽帧事实和下一步数据处理。 |
| [audio_reference_notes.md](audio_reference_notes.md) | Audio ASR reference package and evaluation policy. | 音频 ASR 参考包和评估口径。 |
| [output_audit_and_harness_fixes.md](output_audit_and_harness_fixes.md) | Current output audit and targeted harness fixes. | 当前输出审计和针对性 Harness 修正。 |

## Current Implementation Snapshot / 当前实现快照

EN: The shared repository now contains a full-video bilingual runner, `run_full_bilingual_with_progress.py`. It supports coarse scanning, dense per-event manifests, per-event bilingual commentary, progress logs, cached model calls, same-run checkpoint resume, concurrent independent model calls, request staggering, and rate-limit retries. Treat this as implementation evidence, but still verify it with smoke tests before claiming full robustness.

ZH: 协作仓库当前已经包含全片双语运行入口 `run_full_bilingual_with_progress.py`。它支持粗扫、按事件生成 dense manifest、逐事件双语解说、进度日志、模型调用缓存、同名运行 checkpoint 续跑、独立模型调用并发、请求错峰和限流重试。它可以作为实现证据，但在汇报中宣称“完整稳定”前仍需要 smoke test 验证。

## Collaboration / 协作

| File | EN | ZH |
| --- | --- | --- |
| [repo_branch_strategy.md](repo_branch_strategy.md) | Remote branch and public-safe branch strategy. | 远程分支和公开安全分支策略。 |
| [overnight_tasks.md](overnight_tasks.md) | What cloud agents can do overnight. | 夜间云端 agent 适合做什么。 |
| [decision_log.md](decision_log.md) | Important decisions and tradeoffs. | 关键决策和取舍。 |
| [lessons.md](lessons.md) | Issues, failures, lessons, reusable practices. | 问题、失败、经验和可复用做法。 |

## Research / 调研

| File | EN | ZH |
| --- | --- | --- |
| [problem_interpretation.md](problem_interpretation.md) | Briefing interpretation and visible slide details. | 老师介绍和照片内容解读。 |
| [official_problem_statement.md](official_problem_statement.md) | Problem statement notes. | 题目要求整理。 |
| [research_world_cup_commentary.md](research_world_cup_commentary.md) | World Cup commentary direction research. | 世界杯解说方向调研。 |
| [research_literature_review.md](research_literature_review.md) | Academic review fallback direction research. | 论文综述备选方向调研。 |
| [track_decision_matrix.md](track_decision_matrix.md) | Direction comparison. | 方向选择对比。 |

## Submission / 提交

| File | EN | ZH |
| --- | --- | --- |
| [submission_checklist.md](submission_checklist.md) | Final delivery checklist. | 最终提交清单。 |
| [pitch_pack.md](pitch_pack.md) | Pitch structure and Q&A prompts. | 路演结构和答辩问题。 |
| [token_governance.md](token_governance.md) | Cost separation and token rules. | 成本区分和 token 规则。 |

## Rule / 规则

EN: If a fact is not in the video evidence, official statement, reliable search result, or user-provided notes, do not invent it. Search, ask, or mark it unknown.

ZH: 如果事实不在视频证据、官方题面、可靠搜索或用户提供信息中，不要编造。去搜索、询问，或标注未知。

