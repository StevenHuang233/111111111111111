# Submission Checklist

This checklist is a placeholder until the official task is released.

## Required Materials

| Item | Owner | Status | Location | Notes |
| --- | --- | --- | --- | --- |
| Code zip | TBD | Not started | `submission/` | Must run from clean checkout. |
| Cover image | TBD | Not started | `submission/` | Public-safe image. |
| Project title | TBD | Not started | `submission/` | Short, memorable, aligned with value. |
| Short introduction | TBD | Not started | `submission/` | One paragraph. |
| Markdown documentation | TBD | Not started | `submission/` | Setup, usage, architecture, evaluation. |
| Demo video | TBD | Not started | `submission/` | Show input, process, verification, output. |
| Individual contribution PPT | TBD | Not started | `submission/` | Evidence-backed. |
| Pitch script | TBD | Not started | `submission/` | 10-15 minute version plus 30 second version. |
| Q&A notes | TBD | Not started | `submission/` | Risks, limitations, tradeoffs. |
| Intern-S2 feedback table | TBD | Not started | `submission/intern_s2_feedback_table.md` | Required model feedback questions. |

## Final Verification

- Fresh checkout can run the demo.
- No secrets or private notes are included.
- README and docs match the actual code.
- Video and screenshots match the final demo.
- Contribution evidence is traceable.
- Claims in the pitch have supporting traces, metrics, or examples.

## Evidence To Package / 建议打包证据

| Evidence | EN Use | 中文用途 |
| --- | --- | --- |
| `progress.log` and `progress.jsonl` | Show long-running harness progress, ETA, and stages. | 展示长任务 Harness 的进度、ETA 和阶段。 |
| `cache/<stage>/call_*.json` count, not full sensitive contents | Show resume and cost control without exposing keys or private payloads. | 展示续跑和成本控制，但不暴露 key 或私密 payload。 |
| `coarse/events.json` and dense event outputs | Show coarse-to-dense task decomposition. | 展示从粗扫到 dense 复查的任务拆解。 |
| `commentary_bilingual.json` | Final timestamped bilingual commentary result. | 最终带时间戳双语解说结果。 |
| A small interrupted-run demo | Prove checkpoint resume if time allows. | 如时间允许，用小任务证明 checkpoint 续跑。 |
