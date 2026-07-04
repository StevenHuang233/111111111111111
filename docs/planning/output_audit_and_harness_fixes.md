# Output Audit And Harness Fixes / 输出审计与 Harness 修正

Last updated: 2026-07-05

## Scope / 范围

EN: This note summarizes the audit of `outputs/commentary_bilingual_full_review.md`. Public match facts and ASR transcript data are used only for evaluation. They must not be injected into the target visual commentary agent as hidden context.

ZH: 本文总结对 `outputs/commentary_bilingual_full_review.md` 的审计。公开比赛事实和 ASR 字幕只用于验证，不能作为隐藏上下文注入目标视觉解说 Agent。

## Evidence / 证据

| Source | Path / URL | Use |
| --- | --- | --- |
| Generated output / 生成输出 | `outputs/commentary_bilingual_full_review.md` | Current model result under audit. / 当前被审计的模型结果。 |
| ASR weak signal / ASR 弱信号 | `reference/audio_asr/germany_curacao/` | Original commentary transcript and candidate event windows. / 原解说字幕和候选事件窗口。 |
| Public fact reference / 公开事实参考 | `reference/evaluation/germany_curacao_public_reference.json` | Evaluation-only final score and goal order. / 仅用于验证的比分和进球顺序。 |
| Audit report / 审计报告 | `reference/evaluation/commentary_full_review_audit.md` | Detected conflicts and style issues. / 检出的冲突和风格问题。 |
| Frame checklist / 帧核验清单 | `reference/evaluation/goal_frame_checklist.md` | 4fps probes and bisection plan for goal candidates. / 进球候选的 4fps 帧探针和二分核验计划。 |

## Main Findings / 主要发现

| Finding | Impact | Harness Fix |
| --- | --- | --- |
| Generated `goal` count is 23, while public reference has 8 goals and ASR weak candidates have 9 windows. / 生成 `goal` 数为 23，公开参考为 8 球，ASR 弱候选为 9 个窗口。 | Severe over-detection and replay/summary confusion. / 严重多报，且把回放/总结混为现场进球。 | Add live-goal verifier and score-state machine before final commentary. / 最终解说前加入现场进球验证器和比分状态机。 |
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

## Immediate Development Tasks / 立刻可做任务

| Priority | Task | Acceptance |
| --- | --- | --- |
| Must | Run `reference/evaluation/tools/audit_commentary_output.py` after every full review output. | Audit report exists and critical issues are listed. |
| Must | Add scoreboard cross-check for all `goal` events and score claims. | A goal cannot advance final score unless scoreboard evidence or high-confidence event evidence supports it. |
| Must | Separate live goal, replay, halftime summary, historical mention, and possible disallowed goal. | Replay/summary no longer increments score. |
| Should | Build small visual verification windows from ASR goal candidates. | Each candidate has frame range and verification status. |
| Should | Add style rewrite pass for color-shirt fallback. | Final Chinese text uses team/player/role wording where possible. |
| Could | Add player roster/OCR metadata. | Names are upgraded only when supported. |

## Prompt Changes Already Made / 已做 Prompt 修正

EN: `harness/commentary.py`, `configs/styles.json`, and `configs/event_types.json` now discourage unsupported names, wrong teams, score guessing, goal claims without clear evidence, and repeated kit-color descriptions.

ZH: 已修改 `harness/commentary.py`、`configs/styles.json` 和 `configs/event_types.json`，限制无依据人名、错误球队、猜比分、无明确证据的进球宣称，以及重复球衣颜色描述。
