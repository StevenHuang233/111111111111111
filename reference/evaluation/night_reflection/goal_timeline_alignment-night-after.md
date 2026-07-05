# Goal Timeline Alignment / 进球时间线对齐

EN: This report aligns generated goal/score assertions with manually verified scoreboard changes.

ZH: 本报告将生成的进球/比分声明与人工核验的比分牌变化进行对齐。

## Summary / 摘要

- `verified_score_changes`: 8
- `generated_goal_type_segments`: 8
- `generated_goal_assertion_segments`: 8
- `covered_verified_goals`: 8
- `missing_verified_goals`: 0
- `duplicate_verified_goal_groups`: 0
- `extra_goal_assertions`: 0
- `alignment_before_sec`: 45.0
- `alignment_after_sec`: 90.0

## Alignment Gate / 对齐门禁

- `status`: pass
- `blockers`: -
- `warnings`: -
- EN: Fail means goal/score assertions are not aligned with verified scoreboard changes.
- ZH: fail 表示进球/比分声明没有与已核验比分牌变化对齐。

## Verified Score Changes / 已核验比分变化覆盖情况

| Goal | Score Change | Window | Status | Assigned Generated Events |
| --- | --- | --- | --- | --- |
| G01 | 0-0 -> 1-0 | `00:14:03-00:14:41` | covered | U028 `00:14:08-00:15:28` |
| G02 | 1-0 -> 1-1 | `00:29:31-00:30:04` | covered | U061 `00:28:56-00:28:56` |
| G03 | 1-1 -> 2-1 | `00:45:35-00:45:52` | covered | U102 `00:45:16-00:46:36` |
| G04 | 2-1 -> 3-1 | `00:57:19-00:57:35` | covered | U134 `00:57:00-00:58:20` |
| G05 | 3-1 -> 4-1 | `01:01:41-01:01:58` | covered | U143 `01:01:48-01:02:00` |
| G06 | 4-1 -> 5-1 | `01:23:34-01:26:40` | covered | U188 `01:24:36-01:24:36` |
| G07 | 5-1 -> 6-1 | `01:31:30-01:33:20` | covered | U208 `01:31:12-01:32:36` |
| G08 | 6-1 -> 7-1 | `01:42:20-01:42:30` | covered | U220 `01:42:00-01:43:24` |

## Extra Goal Assertions / 额外进球声明

| Event | Type | Time | Expected Score State | Next Verified Goal | Excerpt |
| --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | - |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Only allow a final score-changing goal claim when it is aligned with a verified scoreboard state transition or passes a live-goal verifier. | 只有当进球宣称能对齐已核验比分牌变化，或通过现场进球验证器时，才允许改变最终比分状态。 |
| Must | Treat unaligned goal assertions as replay, historical mention, possible disallowed goal, or manual-review pending instead of incrementing score. | 未对齐的进球宣称应视为回放、历史提及、可能被吹或待人工复核，不应直接推进比分。 |
| Should | Use this report after every full run to decide whether to rerun goal verification, narrow frames around false positives, or rewrite final commentary. | 每次全量运行后使用本报告判断是否重跑进球验证、收窄假阳性片段，或重写最终解说。 |
