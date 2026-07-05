# Output Audit And Harness Fixes / 输出审计与 Harness 修正

Last updated: 2026-07-05

## Scope / 范围

EN: This note summarizes the audit of generated commentary outputs, especially the current `outputs/commentary_bilingual.json`. Public match facts and ASR transcript data are used only for evaluation. They must not be injected into the target visual commentary agent as hidden context.

ZH: 本文总结对生成解说结果的审计，重点是当前 `outputs/commentary_bilingual.json`。公开比赛事实和 ASR 字幕只用于验证，不能作为隐藏上下文注入目标视觉解说 Agent。

## Evidence / 证据

| Source | Path / URL | Use |
| --- | --- | --- |
| Generated output / 生成输出 | `outputs/commentary_bilingual_full_review.md` | Current model result under audit. / 当前被审计的模型结果。 |
| Latest bilingual output / 最新双语输出 | `outputs/commentary_bilingual.json` | Current structured output with 257 segments. / 当前结构化输出，共 257 段。 |
| ASR weak signal / ASR 弱信号 | `reference/audio_asr/germany_curacao/` | Original commentary transcript and candidate event windows. / 原解说字幕和候选事件窗口。 |
| Public fact reference / 公开事实参考 | `reference/evaluation/germany_curacao_public_reference.json` | Evaluation-only final score and goal order. / 仅用于验证的比分和进球顺序。 |
| Audit report / 审计报告 | `reference/evaluation/commentary_full_review_audit.md` | Detected conflicts and style issues. / 检出的冲突和风格问题。 |
| Quality gate / 质量门禁 | `reference/evaluation/commentary_quality_eval.md` | Latest metrics, issue samples, and final-output gate status. / 最新指标、问题样例和终稿门禁状态。 |
| Manual scoreboard review / 人工比分牌核验 | `reference/evaluation/goal_scoreboard_manual_review.md` | 4fps visual evidence for score changes. / 基于 4fps 抽帧的比分变化证据。 |
| Frame checklist / 帧核验清单 | `reference/evaluation/goal_frame_checklist.md` | 4fps probes and bisection plan for goal candidates. / 进球候选的 4fps 帧探针和二分核验计划。 |
| Local contact sheets / 本地帧拼图 | `outputs/goal_frame_contact_sheets/` | Ignored PNG sheets generated from extracted frames for manual scoreboard checks. / 从抽帧生成、被 Git 忽略的 PNG 拼图，用于人工核验比分牌。 |

## Main Findings / 主要发现

| Finding | Impact | Harness Fix |
| --- | --- | --- |
| Current generated `goal` count is 21, while manual scoreboard review confirms 8 score changes. / 当前生成 `goal` 数为 21，人工比分牌核验确认 8 次比分变化。 | Severe over-detection and replay/summary confusion. / 严重多报，且把回放/总结混为现场进球。 | Add or enable live-goal verifier and score-state machine before final commentary. / 最终解说前加入或启用现场进球验证器和比分状态机。 |
| Quality gate status is `fail`: wrong entities, goal overcount, and excessive score claims are blockers. / 质量门禁为 `fail`：错误实体、进球过计数和比分声明过多是阻塞项。 | Current output cannot be used directly as final demo narration. / 当前输出不能直接作为最终 demo 解说稿。 | Run `evaluate_commentary_quality.py --fail-on-gate` before final packaging. / 最终打包前运行 `evaluate_commentary_quality.py --fail-on-gate`。 |
| ASR candidates cover several early score changes but miss late live goals and over-trigger on summary/stat text. / ASR 候选覆盖若干早期比分变化，但漏掉后段现场进球，并被总结/统计文本误触发。 | ASR-only event discovery is incomplete. / 只靠 ASR 发现事件不完整。 | Add independent scoreboard sweep over frames and use ASR only as a weak signal. / 增加独立比分牌 sweep，ASR 仅作为弱信号。 |
| Some events are labeled `goal` but the text says the ball did not enter. / 有些事件标签是 `goal`，文本却说球没有进。 | Internal contradiction; unacceptable final output. / 内部自相矛盾，最终输出不可接受。 | Add event-label/text contradiction check. / 加事件标签与文本矛盾检查。 |
| Wrong teams appear, especially Colombia/Colombian/哥伦比亚. / 出现错误球队，尤其是 Colombia/Colombian/哥伦比亚。 | Factual hallucination. / 事实幻觉。 | Restrict team names to video/event metadata and visible graphics. / 队名只能来自视频、事件元数据或可见图形。 |
| Unsupported player names appear, such as Ibragimov, Nkunku, Müller. / 出现无依据球员名，如 Ibragimov、Nkunku、Müller。 | Misleading factual detail. / 误导性事实细节。 | Names require roster/OCR/metadata support; otherwise use team role or number. / 人名必须有名单、OCR 或元数据支撑，否则用球队角色或号码。 |
| Repeated color-shirt descriptions appear. / 反复出现球衣颜色描述。 | Not natural broadcast style. / 不像自然人类解说。 | Style linter rejects repeated color-descriptor fallback. / 风格检查器拒绝重复颜色 fallback。 |

## Required Harness Loop / 必需 Harness 闭环

```text
event candidates
  -> live/replay/summary classifier
  -> scoreboard and score-state verifier
  -> named-fact verifier
  -> style linter
  -> revision prompt or reject-to-manual-review
  -> final commentary
```

## Relation To Latest Main / 与最新主干进展的关系

EN: The locally available `origin/main@94d5933` already adds a model-based `goal_verifier` and commentary-unit packaging. That is the right direction for reducing false live goals before generation. The remaining gap is a final-output gate: even after model-side verification, the generated script must still be checked for score conflicts, wrong entities, unsupported names, pre-kickoff action mistakes, and unnatural color-based wording.

ZH: 本地可见的 `origin/main@94d5933` 已经加入基于模型的 `goal_verifier` 和 commentary unit 打包，这是在生成前减少假进球的正确方向。仍然缺少的是终稿门禁：即使模型侧做了进球验证，最终解说稿仍要检查比分冲突、错误实体、无依据人名、开球前动作误判和不自然的颜色式措辞。

## Immediate Development Tasks / 立刻可做任务

| Priority | Task | Acceptance |
| --- | --- | --- |
| Must | Run `reference/evaluation/tools/audit_commentary_output.py` after every full review output. | Audit report exists and critical issues are listed. |
| Must | Run `reference/evaluation/tools/evaluate_commentary_quality.py --fail-on-gate` before final packaging. | Exit code is 0, or all blockers are explicitly reviewed and accepted. |
| Must | Add scoreboard cross-check for all `goal` events and score claims. | A goal cannot advance final score unless scoreboard evidence or high-confidence event evidence supports it. |
| Must | Add independent scoreboard sweep beyond ASR goal windows. | Late score changes are found even when ASR does not mention a clean live goal. |
| Must | Separate live goal, replay, halftime summary, historical mention, and possible disallowed goal. | Replay/summary no longer increments score. |
| Should | Build small visual verification windows from ASR goal candidates. | Each candidate has frame range and verification status. |
| Should | Generate local contact sheets for candidate frames. | Reviewers can inspect scoreboard/action frames without opening the full video. |
| Should | Add style rewrite pass for color-shirt fallback. | Final Chinese text uses team/player/role wording where possible. |
| Could | Add player roster/OCR metadata. | Names are upgraded only when supported. |

## Prompt Changes Already Made / 已做 Prompt 修正

EN: `harness/commentary.py`, `configs/styles.json`, and `configs/event_types.json` now discourage unsupported names, wrong teams, score guessing, goal claims without clear evidence, and repeated kit-color descriptions.

ZH: 已修改 `harness/commentary.py`、`configs/styles.json` 和 `configs/event_types.json`，限制无依据人名、错误球队、猜比分、无明确证据的进球宣称，以及重复球衣颜色描述。
