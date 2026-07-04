# Submission Checklist / 提交清单

This checklist records the required hackathon deliverables and the extra evidence we should package for the harness story.

本清单记录黑客松要求提交物，以及为了讲清楚 Harness 额外应打包的证据。

## Required Materials / 必交材料

| Item | Owner | Status | Location | Notes |
| --- | --- | --- | --- | --- |
| Code zip / 代码 zip | TBD | Not started / 未开始 | `submission/` | Must run from clean checkout; exclude videos, frames, `.env`, and large outputs. / 必须能从干净 checkout 运行；排除视频、抽帧、`.env` 和大输出。 |
| Cover image / 封面图 | TBD | Not started / 未开始 | `submission/` | Public-safe image showing the project concept. / 公开安全，表达项目概念。 |
| Project title / 作品标题 | TBD | Not started / 未开始 | `submission/` | Short, memorable, aligned with value. / 简短、有记忆点、贴合价值。 |
| Short introduction / 作品简介 | TBD | Not started / 未开始 | `submission/` | One paragraph for submission form. / 表单用一段简介。 |
| Markdown documentation / 说明文档 md | TBD | Not started / 未开始 | `submission/` | Setup, usage, architecture, evaluation, limitations. / 环境、用法、架构、评估、限制。 |
| Demo video / demo 视频 | TBD | Not started / 未开始 | `submission/` | Show input, process, progress/resume, verification, output. / 展示输入、流程、进度/续跑、核验和输出。 |
| Individual contribution PPT / 个人贡献 PPT | TBD | Not started / 未开始 | `submission/` | Evidence-backed: commits, docs, screenshots, runs. / 用 commit、文档、截图、运行记录支撑。 |
| Pitch script / 路演稿 | TBD | Not started / 未开始 | `submission/` | 10-15 minute version plus 30 second version. / 10-15 分钟版和 30 秒版。 |
| Q&A notes / 答辩 Q&A | TBD | Not started / 未开始 | `submission/` | Risks, limitations, tradeoffs, model weaknesses. / 风险、限制、取舍、模型不足。 |
| Intern-S2 feedback table / Intern-S2 反馈表 | TBD | Started / 已建模板 | `submission/intern_s2_feedback_table.md` | Required model feedback questions. / 必填模型反馈问题。 |

## Required Feedback Form / 必填反馈表

| No. | Question EN | 问题中文 | Where |
| --- | --- | --- | --- |
| 2 | During the hackathon, you used Intern-S2-Preview. In which scenarios did it perform well? | 在黑客松期间使用了 Intern S2 Preview，您觉得这个模型在哪些场景还不错？ | `submission/intern_s2_feedback_table.md` |
| 3 | What weaknesses and improvement directions did you observe for Intern-S2-Preview? | 您觉得 Intern S2 Preview 有哪些不足和提升空间？ | `submission/intern_s2_feedback_table.md` |
| 4 | Optional: would you like to leave your name and contact information for follow-up? | （选填）是否愿意留下您的姓名和联系方式，方便后续联络？ | `submission/intern_s2_feedback_table.md` |

## Final Verification / 最终核验

- Fresh checkout can run the demo. / 干净 checkout 能跑 demo。
- No secrets or private notes are included. / 不包含密钥或私密笔记。
- README and docs match the actual code. / README 和文档与代码一致。
- Video and screenshots match the final demo. / 视频和截图与最终 demo 一致。
- Contribution evidence is traceable. / 个人贡献证据可追溯。
- Claims in the pitch have supporting traces, metrics, or examples. / 路演主张有 trace、指标或样例支撑。

## Evidence To Package / 建议打包证据

| Evidence | EN Use | 中文用途 |
| --- | --- | --- |
| `progress.log` and `progress.jsonl` | Show long-running harness progress, ETA, and stages. | 展示长任务 Harness 的进度、ETA 和阶段。 |
| `cache/<stage>/call_*.json` count, not full sensitive contents | Show resume and cost control without exposing keys or private payloads. | 展示续跑和成本控制，但不暴露 key 或私密 payload。 |
| `coarse/events.json` and dense event outputs | Show coarse-to-dense task decomposition. | 展示从粗扫到 dense 复查的任务拆解。 |
| `commentary_bilingual.json` | Final timestamped bilingual commentary result. | 最终带时间戳双语解说结果。 |
| A small interrupted-run demo | Prove checkpoint resume if time allows. | 如时间允许，用小任务证明 checkpoint 续跑。 |
