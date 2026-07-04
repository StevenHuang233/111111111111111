# Track Decision Matrix

Last updated: 2026-07-04

This matrix compares the two visible team directions from the briefing photos.

Scores use 1-5 where 5 is strongest. These are preliminary and should be updated after official details, API behavior, and data access are confirmed.

| Criterion | Weight | World Cup Commentary | Academic Review | Notes |
| --- | ---: | ---: | ---: | --- |
| Technical capability | 30% | 5 | 4 | World Cup shows multimodal orchestration; academic review shows grounded RAG and verification. |
| Social value | 20% | 3 | 5 | Academic review has clearer research productivity value; World Cup can frame accessibility and media productivity. |
| Tool integration | 15% | 5 | 5 | World Cup integrates video/audio/OCR/CV/LLM; review integrates Sciverse/MinerU/RAG/citation checks. |
| Expression and logic | 15% | 5 | 4 | World Cup is easier to demo live and easier for broad judges to understand. |
| Background/contribution evidence | 30% | 4 | 4 | Both can show PRs, traces, docs, and evaluation artifacts. |
| Roadshow popularity bonus | Bonus | 5 | 3 | World Cup likely has stronger public-vote appeal. |
| 24h feasibility | Risk | 3 | 4 | Academic review is safer; World Cup needs tighter MVP. |
| Data/legal safety | Risk | 3 | 4 | World Cup video rights need care; paper access and licenses still need attention. |

## Current Decision

Preliminary preference: World Cup video commentary harness.

Reason:

- Better roadshow and demo appeal.
- More obvious agentic harness story.
- Differentiates from likely science-RAG competitors.

Conditions that should trigger switching to academic review:

- Intern-S2 or available tools cannot support reliable video-evidence workflow.
- No usable public-safe soccer clips are available.
- Official evaluation strongly favors Sciverse/MinerU scientific-data integration.
- Team lacks enough time to implement even a scoped video pipeline.

## Feishu Editing Status

Current Codex environment has no Feishu/Lark Docs connector or authenticated browser automation tool exposed. I can prepare Markdown content locally, but I cannot directly modify the Feishu document from this environment unless one of the following becomes available:

- A Feishu/Lark connector with document edit permission.
- A Feishu OpenAPI app token and document API permission.
- An authenticated browser environment that allows editing the shared document.
- The document is exported to Markdown/Docx, edited locally, then re-imported manually.

Do not commit the shared-document password or any access token to this repository.

