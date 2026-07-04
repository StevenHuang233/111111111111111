# Token Governance

This document separates assistant collaboration cost from project runtime cost.

## Assistant Collaboration Cost

Assistant collaboration cost is the token and time cost from using coding or writing assistants while building the project.

Rules:

- Put stable instructions in files, especially `AGENTS.md`, instead of repeating them in prompts.
- Send only deltas when plans change.
- Ask the assistant to inspect directory structure before reading full files.
- Prefer targeted file reads over loading entire folders.
- Summarize long meeting notes and task interpretations before implementation.
- Keep decisions in `docs/decision_log.md` so future prompts can reference a stable source.

Metrics:

- Number of assistant turns.
- Estimated tokens per major task.
- Rework caused by unclear prompts.
- Files read or rewritten unnecessarily.

## Project Runtime Cost

Project runtime cost is the cost of the final harness while solving its target task.

Rules:

- Use deterministic scripts before model calls when possible.
- Set token budgets and maximum iteration counts for each task.
- Truncate or summarize long tool outputs before sending them back to the model.
- Store large artifacts on disk and pass references plus summaries.
- Cache stable intermediate results.
- Track failures, retries, and stop reasons.

Metrics:

- Input tokens, output tokens, and total tokens.
- Wall-clock time.
- Tool calls.
- Retry count.
- Success rate.
- Unit cost per successful task.

## Current Runtime Controls

EN:

- Use sparse coarse manifests before dense event manifests.
- Use the resumable runner cache at `outputs/<run-name>/cache/<stage>/call_*.json` to avoid paying again for completed model calls.
- Use `progress.log` and `progress.jsonl` to estimate remaining time and detect stalls.
- Prefer sequential execution until API rate limits, cache consistency, and output ordering are tested.
- Keep smoke tests tiny; use full-video runs only after schema and fact checks pass.

ZH:

- 先用稀疏 coarse manifest，再对事件区间生成 dense manifest。
- 使用 `outputs/<run-name>/cache/<stage>/call_*.json` 的可续跑缓存，避免已完成模型调用重复付费。
- 用 `progress.log` 和 `progress.jsonl` 估计剩余时间并发现卡住的阶段。
- 在 API 限流、缓存一致性和输出顺序验证前，优先采用顺序执行。
- smoke 测试保持很小；等结构和事实核验通过后再跑全片。

## Review Question

Every optimization should answer: what quality changed, what cost changed, and whether the tradeoff is worth it.

