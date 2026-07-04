# Goal Scoreboard Manual Review / 进球比分牌人工核验

Last updated: 2026-07-05

EN: This review uses extracted 4fps frames and local contact sheets only. It is evaluation evidence, not hidden target-agent context.

ZH: 本核验只使用本地 4fps 抽帧和本地拼图。它是评估证据，不是目标 Agent 的隐藏上下文。

## Verified Score Changes / 已核验比分变化

| ID | Score Change | Evidence Window | Match Clock Evidence | Status |
| --- | --- | --- | --- | --- |
| G01 | 0-0 -> 1-0 | `00:14:03 frame_003372.jpg` to `00:14:41 frame_003524.jpg` | `04:56` to `05:34` | confirmed scoreboard change |
| G02 | 1-0 -> 1-1 | `00:29:31 frame_007084.jpg` to `00:30:04 frame_007216.jpg` | `20:24` to `20:57` | confirmed scoreboard change |
| G03 | 1-1 -> 2-1 | `00:45:35 frame_010940.jpg` to `00:45:52 frame_011008.jpg` | `37:25` to `37:42` | confirmed scoreboard change |
| G04 | 2-1 -> 3-1 | `00:57:19 frame_013756.jpg` to `00:57:35 frame_013820.jpg` | `49:09` to `49:25` | confirmed scoreboard change |
| G05 | 3-1 -> 4-1 | `01:01:41 frame_014804.jpg` to `01:01:58 frame_014872.jpg` | `46:03` to `46:20` | confirmed scoreboard change |
| G06 | 4-1 -> 5-1 | `01:23:34 frame_020056.jpg` to `01:26:40 frame_020800.jpg` | `67:56` to `72:14` | confirmed score, coarse timing because scoreboard disappears during replay/animation |
| G07 | 5-1 -> 6-1 | `01:31:30 frame_021960.jpg` to `01:33:20 frame_022400.jpg` | `77:04` to `78:54` | confirmed score, coarse timing |
| G08 | 6-1 -> 7-1 | `01:42:20 frame_024560.jpg` to `01:42:30 frame_024600.jpg` | `87:44` to `88:04` | confirmed scoreboard change |

## ASR Candidate Review / ASR 候选复核

| Candidate | Visual Review | Harness Meaning |
| --- | --- | --- |
| AG01 | overlaps G01 | useful weak signal |
| AG02 | overlaps G02 | useful weak signal |
| AG03 | overlaps G03 | useful weak signal |
| AG04 | overlaps G04 | useful weak signal |
| AG05 | halftime/summary context, no live score change | should not increment score |
| AG06 | overlaps G05 | useful weak signal |
| AG07 | score remains 4-1 across probes; likely stat/replay context | should not increment score |
| AG08 | overlaps G06 but coarse probes miss the final scoreboard update | useful but needs extended window |
| AG09 | score already 7-1; historical/final-stage discussion | should not increment score |

## Harness Implications / Harness 启示

EN:

- ASR goal cues are useful but not complete. They over-trigger on summaries and miss later live score changes.
- The harness needs an independent scoreboard sweep, not only ASR-derived goal windows.
- A final goal claim should pass a score-state check: previous score, post-event score, live/replay/summary classification, and contradiction check.
- When scoreboard disappears during replay/VAR/animation, keep the event in `pending_verification` until a later post-event scoreboard frame is found.

ZH:

- ASR 的进球线索有帮助，但不完整：它会被总结/历史提及误触发，也会漏掉后段现场比分变化。
- Harness 需要独立的比分牌 sweep，不能只依赖 ASR 候选窗口。
- 最终进球宣称必须通过比分状态检查：前一比分、后一比分、现场/回放/总结分类，以及文本矛盾检查。
- 当回放、VAR、进球动画导致比分牌消失时，应先标为 `pending_verification`，直到找到后续比分牌帧。
