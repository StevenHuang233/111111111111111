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

## Review Question

Every optimization should answer: what quality changed, what cost changed, and whether the tradeoff is worth it.

