# Decision Log / 决策日志

Last updated: 2026-07-04

## Format / 格式

| Date | Decision | Background | Alternatives | Tradeoff | Follow-up |
| --- | --- | --- | --- | --- | --- |

## Entries / 记录

| Date | Decision | Background | Alternatives | Tradeoff | Follow-up |
| --- | --- | --- | --- | --- | --- |
| 2026-07-04 | Keep `main` untouched; use `team/worldcup-commentary` for our work. / 不碰 `main`，我们的内容放 `team/worldcup-commentary`。 | Teammates continue updating `main`; user explicitly said not to touch it. / 队友会持续更新 `main`，用户明确要求不要动。 | Work directly on `main`; create a fork. / 直接在 `main` 工作；另建 fork。 | Branch work preserves teammate flow and reduces accidental overwrite risk. / 分支工作能保留队友节奏，降低误覆盖风险。 | Fetch/rebase from `origin/main`; push only team branch. / 从 `origin/main` 拉取并 rebase，只推送团队分支。 |
| 2026-07-04 | Use `public/demo-placeholder` as a neutral public-safe branch. / 使用 `public/demo-placeholder` 作为中性公开安全分支。 | User wants a simple branch unrelated to the harness, without contest material. / 用户希望有一个简单、与 Harness 无关、不含赛题材料的分支。 | Put placeholder on `main`; expose real work publicly. / 把占位内容放 `main`；直接公开真实工作。 | Neutral branch avoids early exposure while not hiding judged content improperly. / 中性分支避免过早暴露，同时不用于违规隐藏评审内容。 | Keep it minimal and do not merge into `main` unless the team decides. / 保持极简，除非团队决定，否则不并入 `main`。 |
| 2026-07-04 | Treat `run_full_bilingual_with_progress.py` as current long-running harness evidence. / 将 `run_full_bilingual_with_progress.py` 作为当前长任务 Harness 证据。 | Latest `origin/main` added progress, cache, checkpoint resume, coarse-to-dense stages, and bilingual aggregation. / 最新 `origin/main` 增加了进度、缓存、checkpoint 续跑、粗扫到 dense 阶段和双语聚合。 | Keep only small MVP script; rewrite orchestration. / 只保留小 MVP 脚本；重写调度。 | Reusing the runner saves time, but claims must be validated by smoke and interrupted-run tests. / 复用 runner 节省时间，但宣称前必须通过 smoke 和中断续跑验证。 | Run unit tests, smoke manifest, real API smoke, and resume demo. / 运行单测、smoke manifest、真实 API smoke 和续跑 demo。 |
| 2026-07-04 | Treat concurrency as implemented but not yet validated. / 将并发视为已实现但尚未验证。 | Latest `origin/main` added `--concurrency`, `ThreadPoolExecutor`, request staggering, and retry/backoff for rate limits. / 最新 `origin/main` 增加了 `--concurrency`、`ThreadPoolExecutor`、请求错峰和限流 retry/backoff。 | Claim concurrency fully reliable now; disable it and stay sequential. / 立即宣称并发完全可靠；关闭并发只走顺序。 | The implementation is valuable for tool integration and efficiency, but under pitch pressure it needs small-run proof before strong claims. / 该实现对工具整合和效率有价值，但路演前强宣称需要小规模运行证据。 | Run low-concurrency smoke, inspect `progress.jsonl`, then scale cautiously. / 跑低并发 smoke，检查 `progress.jsonl`，再谨慎提高。 |
