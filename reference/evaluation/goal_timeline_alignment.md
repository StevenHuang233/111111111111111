# Goal Timeline Alignment / 进球时间线对齐

EN: This report aligns generated goal/score assertions with manually verified scoreboard changes.

ZH: 本报告将生成的进球/比分声明与人工核验的比分牌变化进行对齐。

## Summary / 摘要

- `verified_score_changes`: 8
- `generated_goal_type_segments`: 21
- `generated_goal_assertion_segments`: 37
- `covered_verified_goals`: 8
- `missing_verified_goals`: 0
- `duplicate_verified_goal_groups`: 5
- `extra_goal_assertions`: 21
- `alignment_before_sec`: 45.0
- `alignment_after_sec`: 90.0

## Alignment Gate / 对齐门禁

- `status`: fail
- `blockers`: extra_goal_assertions
- `warnings`: duplicate_verified_goal_groups
- EN: Fail means goal/score assertions are not aligned with verified scoreboard changes.
- ZH: fail 表示进球/比分声明没有与已核验比分牌变化对齐。

## Verified Score Changes / 已核验比分变化覆盖情况

| Goal | Score Change | Window | Status | Assigned Generated Events |
| --- | --- | --- | --- | --- |
| G01 | 0-0 -> 1-0 | `00:14:03-00:14:41` | covered | U036 `00:14:08-00:15:28` |
| G02 | 1-0 -> 1-1 | `00:29:31-00:30:04` | covered_with_duplicates | U080 `00:29:56-00:30:20`, U081 `00:30:48-00:32:44` |
| G03 | 1-1 -> 2-1 | `00:45:35-00:45:52` | covered | U124 `00:45:16-00:46:36` |
| G04 | 2-1 -> 3-1 | `00:57:19-00:57:35` | covered_with_duplicates | U147 `00:55:48-00:56:48`, U149 `00:57:00-00:58:20`, U150 `00:58:40-00:59:08` |
| G05 | 3-1 -> 4-1 | `01:01:41-01:01:58` | covered_with_duplicates | U156 `01:00:36-01:01:08`, U158 `01:01:40-01:02:44`, U159 `01:02:56-01:03:00` |
| G06 | 4-1 -> 5-1 | `01:23:34-01:26:40` | covered_with_duplicates | U203 `01:23:16-01:24:24`, U211 `01:26:24-01:26:36`, U215 `01:27:40-01:27:44` |
| G07 | 5-1 -> 6-1 | `01:31:30-01:33:20` | covered_with_duplicates | U225 `01:31:28-01:32:36`, U226 `01:33:40-01:33:48` |
| G08 | 6-1 -> 7-1 | `01:42:20-01:42:30` | covered | U244 `01:42:08-01:43:24` |

## Extra Goal Assertions / 额外进球声明

| Event | Type | Time | Expected Score State | Next Verified Goal | Excerpt |
| --- | --- | --- | --- | --- | --- |
| U042 | goal | `00:17:12-00:18:12` | 1-0 | G02 00:29:31-00:30:04 | And here it is — Germany doubles their lead! A crisp, clinical finish from inside the box as the ball nestles into the back of the net. The keeper dives but can’t reach it — pure c |
| U054 | celebration_or_replay | `00:21:00-00:21:00` | 1-0 | G02 00:29:31-00:30:04 | And there it is — a moment of pure precision. The German striker connects cleanly on the volley, sending the ball past the keeper and into the net. The crowd erupts as the scoreboa |
| U062 | dangerous_attack | `00:23:32-00:23:32` | 1-0 | G02 00:29:31-00:30:04 | Germany's #15 raises his arm in appeal as he advances — the team is pushing forward with intent, pressing into the final third. The momentum suggests a dangerous attack unfolding,  |
| U090 | goal | `00:34:52-00:36:16` | 1-1 | G03 00:45:35-00:45:52 | Germany takes a free kick near the penalty area. The ball is struck with precision, curling past the defensive wall and into the net. The German players celebrate as the goal is co |
| U119 | dangerous_attack | `00:43:16-00:43:16` | 1-1 | G03 00:45:35-00:45:52 | Germany builds a dangerous attack in the final third, with multiple players entering the penalty area and a cross delivered into a crowded box. The chance looks promising as the ba |
| U131 | goal | `00:49:40-00:50:40` | 2-1 | G04 00:57:19-00:57:35 | Germany takes a commanding lead! The attacking move builds with precision as the ball is moved into the final third. A player drives forward, evading defenders, and delivers a deci |
| U135 | goal | `00:51:40-00:53:00` | 2-1 | G04 00:57:19-00:57:35 | Germany takes a free kick near the penalty area. The German player strikes the ball, and it goes into the net! The goalkeeper dives but cannot reach it. The German players celebrat |
| U136 | celebration_or_replay | `00:53:12-00:53:20` | 2-1 | G04 00:57:19-00:57:35 | Curacao's player in blue and yellow celebrates as the crowd erupts. The scoreboard shows Germany leading 2-1 at 45:02, but the home fans are visibly energized. Close-ups reveal emo |
| U162 | goal | `01:06:04-01:06:16` | 4-1 | G06 01:23:34-01:26:40 | And there it is! Germany scores! The ball finds the back of the net as the goalkeeper is beaten. Sané and Musiala are seen celebrating in the moments following the goal. / 球进了！德国队破 |
| U176 | celebration_or_replay | `01:12:24-01:12:28` | 4-1 | G06 01:23:34-01:26:40 | And there it is, Musiala with his 10th goal for Germany. The scoreboard confirms the 4-1 lead as Musiala catches his breath, bending over in exhaustion after the strike. / 进了！穆西亚拉为 |
| U180 | goal | `01:14:52-01:15:00` | 4-1 | G06 01:23:34-01:26:40 | And there it is! A goal for Germany! The ball finds the back of the net as the goalkeeper is beaten on the dive. The German player who scored turns away with a focused look, and hi |
| U186 | celebration_or_replay | `01:16:40-01:16:52` | 4-1 | G06 01:23:34-01:26:40 | The German fans are absolutely losing it in the stands! Look at that sea of white and black-red-gold, everyone on their feet, arms raised, flags waving — pure electric atmosphere a |
| U187 | free_kick | `01:16:56-01:17:08` | 4-1 | G06 01:23:34-01:26:40 | Germany awarded a free kick just outside the penalty area. The referee ensures the defensive wall is set, and the taker steps up to take control of the situation. With the scorelin |
| U193 | goal | `01:18:08-01:18:52` | 4-1 | G06 01:23:34-01:26:40 | Germany scores! A fast break down the right flank sees Gnabry cut inside and strike a low shot that beats the goalkeeper and nestles into the bottom corner. The net ripples as the  |
| U200 | foul | `01:21:12-01:21:16` | 4-1 | G06 01:23:34-01:26:40 | Curaçao's Bacuna goes up for a header, but he's caught off balance by Undav's challenge. The German defender makes contact with his back, sending Bacuna crashing to the turf. The r |
| U201 | other_relevant | `01:21:20-01:21:20` | 4-1 | G06 01:23:34-01:26:40 | Leandro Bacuna, wearing the number 10 for Curaçao, is shown on the field with a graphic indicating his 73rd cap for the national team. He stands next to an opponent in a Germany je |
| U202 | goal | `01:21:32-01:22:04` | 4-1 | G06 01:23:34-01:26:40 | Curaçao takes a free kick near the penalty area. The ball is played into the box, and a Curaçao player makes a run towards the goal. He receives the ball and takes a shot from insi |
| U222 | goal | `01:29:44-01:30:40` | 5-1 | G07 01:31:30-01:33:20 | Germany extends their lead! The attacker in white takes a shot from inside the box, the goalkeeper in green dives but can't reach it, and the ball finds the back of the net. The cr |
| U238 | goal | `01:38:04-01:38:32` | 6-1 | G08 01:42:20-01:42:30 | Germany's #26, Wirtz, finds space in the box and fires a low shot past the keeper! The net ripples as the ball crosses the line. Confirmed: Germany extend their lead to 6-1. Wirtz  |
| U248 | goal | `01:46:32-01:47:44` | 7-1 | -  | In stoppage time, Colombia’s number 10 breaks away with pace, chased by a German defender. He drives forward, enters the penalty area, and fires a shot. The ball finds the back of  |
| U252 | goal | `01:48:12-01:49:32` | 7-1 | -  | In stoppage time, Germany takes a free kick from just outside the penalty area. The ball is struck with precision, curling over the defensive wall and into the top corner of the ne |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Only allow a final score-changing goal claim when it is aligned with a verified scoreboard state transition or passes a live-goal verifier. | 只有当进球宣称能对齐已核验比分牌变化，或通过现场进球验证器时，才允许改变最终比分状态。 |
| Must | Treat unaligned goal assertions as replay, historical mention, possible disallowed goal, or manual-review pending instead of incrementing score. | 未对齐的进球宣称应视为回放、历史提及、可能被吹或待人工复核，不应直接推进比分。 |
| Should | Use this report after every full run to decide whether to rerun goal verification, narrow frames around false positives, or rewrite final commentary. | 每次全量运行后使用本报告判断是否重跑进球验证、收窄假阳性片段，或重写最终解说。 |
