# Goal Timeline Alignment / 进球时间线对齐

EN: This report aligns generated goal/score assertions with manually verified scoreboard changes.

ZH: 本报告将生成的进球/比分声明与人工核验的比分牌变化进行对齐。

## Summary / 摘要

- `verified_score_changes`: 8
- `generated_goal_type_segments`: 23
- `generated_goal_assertion_segments`: 43
- `covered_verified_goals`: 8
- `missing_verified_goals`: 0
- `duplicate_verified_goal_groups`: 4
- `extra_goal_assertions`: 30
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
| G01 | 0-0 -> 1-0 | `00:14:03-00:14:41` | covered_with_duplicates | U028 `00:14:08-00:15:28`, U030 `00:15:44-00:15:56` |
| G02 | 1-0 -> 1-1 | `00:29:31-00:30:04` | covered | U068 `00:30:32-00:31:20` |
| G03 | 1-1 -> 2-1 | `00:45:35-00:45:52` | covered | U102 `00:45:16-00:46:36` |
| G04 | 2-1 -> 3-1 | `00:57:19-00:57:35` | covered | U134 `00:57:00-00:58:20` |
| G05 | 3-1 -> 4-1 | `01:01:41-01:01:58` | covered_with_duplicates | U143 `01:01:48-01:02:00`, U144 `01:02:28-01:02:44`, U145 `01:02:56-01:03:00` |
| G06 | 4-1 -> 5-1 | `01:23:34-01:26:40` | covered | U185 `01:23:16-01:24:12` |
| G07 | 5-1 -> 6-1 | `01:31:30-01:33:20` | covered_with_duplicates | U208 `01:31:12-01:32:36`, U211 `01:33:40-01:33:48` |
| G08 | 6-1 -> 7-1 | `01:42:20-01:42:30` | covered_with_duplicates | U220 `01:42:00-01:43:24`, U221 `01:43:40-01:43:44` |

## Extra Goal Assertions / 额外进球声明

| Event | Type | Time | Expected Score State | Next Verified Goal | Excerpt |
| --- | --- | --- | --- | --- | --- |
| U018 | celebration_or_replay | `00:08:08-00:08:24` | 0-0 | G01 00:14:03-00:14:41 | Germany players in white kits huddle together in celebration on the pitch, with German flags visible in the background crowd. Close-up of Germany players continuing their team hudd |
| U032 | celebration_or_replay | `00:17:16-00:17:16` | 1-0 | G02 00:29:31-00:30:04 | Germany's No. 10, Müller, turns away as the crowd reacts — a moment of quiet aftermath after the goal. The scoreboard holds at 1-0, and the replay angle suggests this is part of th |
| U034 | shot | `00:17:28-00:17:28` | 1-0 | G02 00:29:31-00:30:04 | Germany's No. 23 drives forward with the ball, challenged closely by a Curacao defender. He unleashes a powerful shot toward goal — the ball is struck cleanly, but whether it finds |
| U046 | celebration_or_replay | `00:20:04-00:20:08` | 1-0 | G02 00:29:31-00:30:04 | Germany takes an early lead in this World Cup clash as Nmecha finds the back of the net in the 6th minute. The scoreboard confirms the goal, and the players are now resetting for t |
| U047 | goal | `00:20:36-00:21:32` | 1-0 | G02 00:29:31-00:30:04 | Germany builds pressure in Curacao's half, with multiple attackers entering the penalty area. A German player takes a shot from inside the box, and the ball finds the back of the n |
| U049 | goal | `00:22:52-00:23:44` | 1-0 | G02 00:29:31-00:30:04 | Germany takes an early lead in this World Cup clash against Curacao. The breakthrough comes from a well-timed run by Germany's No. 17, Wirtz, who finds space inside the box and fir |
| U073 | goal | `00:33:04-00:33:16` | 1-1 | G03 00:45:35-00:45:52 | Curacao strike from close range! The ball finds the back of the net as German defenders and the goalkeeper are left on the ground in disbelief. Comenencia, wearing number 8, leads  |
| U074 | period_transition | `00:33:20-00:33:24` | 1-1 | G03 00:45:35-00:45:52 | The teams are resetting on the pitch after the goal, with the scoreboard showing a 1-1 tie. Players from both Germany and Curacao are positioning themselves for the restart, while  |
| U077 | goal | `00:34:52-00:36:12` | 1-1 | G03 00:45:35-00:45:52 | Germany's No. 17 takes a corner kick, delivering the ball into the penalty area. A German player heads the ball powerfully towards the goal, beating the goalkeeper and sending it i |
| U082 | free_kick | `00:36:44-00:36:44` | 1-1 | G03 00:45:35-00:45:52 | Germany's No. 17 steps up to take a free kick just outside the penalty area as the referee signals for play to resume. The Curacao defensive line forms a compact wall, and the goal |
| U085 | goal | `00:37:24-00:38:36` | 1-1 | G03 00:45:35-00:45:52 | Germany's No. 17, Wirtz, drives forward with the ball, evading a Curacao defender in midfield. He enters the penalty area, drawing multiple defenders, and delivers a precise pass t |
| U093 | shot | `00:41:24-00:41:24` | 1-1 | G03 00:45:35-00:45:52 | Germany's No. 10 finds space inside the box and unleashes a powerful shot from close range. The ball rockets toward goal, forcing the Curacao goalkeeper into a sharp reaction. It’s |
| U097 | goal | `00:42:52-00:43:08` | 1-1 | G03 00:45:35-00:45:52 | Curacao's No. 12 drives forward with the ball, cutting inside from the right flank as German defenders converge. He finds space just outside the box and unleashes a low, driven sho |
| U110 | celebration_or_replay | `00:48:48-00:49:08` | 2-1 | G04 00:57:19-00:57:35 | Germany takes the lead! Sané (No. 10) finds the back of the net, putting Germany ahead 2-1 against Curacao. The crowd erupts as fans wave flags and cheer wildly. Replays show the p |
| U111 | goal | `00:49:40-00:50:36` | 2-1 | G04 00:57:19-00:57:35 | Germany takes the lead! A German player drives into the box, draws defenders, and fires a shot that finds the back of the net as the goalkeeper dives in vain. The net ripples — goa |
| U116 | celebration_or_replay | `00:53:12-00:53:12` | 2-1 | G04 00:57:19-00:57:35 | Curacao's No. 12 raises his arms in celebration as the crowd erupts behind him. The scoreboard confirms Germany leads 2-1 at 45:02, suggesting this is a replay or post-goal reactio |
| U124 | dangerous_attack | `00:55:08-00:55:08` | 2-1 | G04 00:57:19-00:57:35 | Germany moves into the final third with multiple players in the penalty area, creating a promising attacking opportunity. / 德国队带球进入前场，禁区内外多名球员接应，攻势一触即发。 |
| U149 | goal | `01:06:04-01:06:44` | 4-1 | G06 01:23:34-01:26:40 | Germany scores! Musiala finds the net with a powerful close-range strike. The ball rockets past the diving goalkeeper and into the back of the net. Musiala celebrates with a hand-t |
| U155 | celebration_or_replay | `01:09:12-01:10:04` | 4-1 | G06 01:23:34-01:26:40 | Germany's No. 17 is celebrating after the goal, and the crowd is cheering. The scoreboard shows Germany leading 4-1 against Curacao. / 德国队的17号球员正在庆祝进球，现场球迷欢呼雀跃。记分牌显示，德国队以4-1领先库拉索队。 |
| U160 | celebration_or_replay | `01:12:24-01:12:32` | 4-1 | G06 01:23:34-01:26:40 | Germany's No. 10, Jamal Musiala, finds the back of the net once again. The scoreboard confirms it: Germany leads 4-1. Musiala catches his breath after the strike, visibly exhausted |
| U164 | goal | `01:14:52-01:15:00` | 4-1 | G06 01:23:34-01:26:40 | Germany's No. 16 finds space inside the box and fires a low shot that beats the diving Curacao goalkeeper into the bottom corner. The net ripples, and the goal is confirmed as the  |
| U169 | celebration_or_replay | `01:16:48-01:16:52` | 4-1 | G06 01:23:34-01:26:40 | The German fans are absolutely electric in the stands, waving flags and cheering as the scoreboard confirms Germany's 4-1 lead at the 61-minute mark. The energy is palpable as supp |
| U176 | goal | `01:18:08-01:18:40` | 4-1 | G06 01:23:34-01:26:40 | Germany take the lead! Sané finds the back of the net with a powerful strike. The German striker beats the goalkeeper to the ball, sending it into the corner of the net. The crowd  |
| U184 | celebration_or_replay | `01:21:32-01:22:04` | 4-1 | G06 01:23:34-01:26:40 | Curacao's No. 7 takes the free kick, and the ball finds the back of the net! The scoreboard updates to 4-1 as Curacao fans erupt in celebration. The replay shows the strike beating |
| U205 | goal | `01:29:44-01:30:32` | 5-1 | G07 01:31:30-01:33:20 | Germany takes control in the attacking third, with a German player advancing into Curacao's half under pressure from a defender. The ball is delivered into the penalty area, and as |
| U214 | celebration_or_replay | `01:35:48-01:36:56` | 6-1 | G08 01:42:20-01:42:30 | Germany takes a penalty in the 82nd minute. The ball finds the back of the net as the Curacao goalkeeper is beaten. The German players celebrate the goal, with Kimmich (No. 6) and  |
| U218 | goal | `01:38:04-01:38:24` | 6-1 | G08 01:42:20-01:42:30 | Curacao's attacker drives forward, drawing defenders into the box. He unleashes a shot from inside the penalty area — but it’s Germany who respond with precision. Wirtz, No. 19, fi |
| U219 | goal | `01:39:36-01:40:24` | 6-1 | G08 01:42:20-01:42:30 | Germany's No. 22 finds space on the edge of the box, drives forward past Curacao's No. 10, and unleashes a low shot that beats the diving keeper and nestles into the net. The net r |
| U225 | goal | `01:46:32-01:47:44` | 7-1 | -  | Curacao's No. 10 drives forward into the German half, closely tracked by Germany's No. 22. The pressure builds as the Curacao attacker cuts inside, drawing defenders. A shot is fir |
| U230 | goal | `01:48:12-01:49:28` | 7-1 | -  | Germany wins the penalty kick. The German player takes the shot and scores a goal. The Curacao goalkeeper dives but fails to save it. The German players celebrate the goal. / 德国队获得 |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Only allow a final score-changing goal claim when it is aligned with a verified scoreboard state transition or passes a live-goal verifier. | 只有当进球宣称能对齐已核验比分牌变化，或通过现场进球验证器时，才允许改变最终比分状态。 |
| Must | Treat unaligned goal assertions as replay, historical mention, possible disallowed goal, or manual-review pending instead of incrementing score. | 未对齐的进球宣称应视为回放、历史提及、可能被吹或待人工复核，不应直接推进比分。 |
| Should | Use this report after every full run to decide whether to rerun goal verification, narrow frames around false positives, or rewrite final commentary. | 每次全量运行后使用本报告判断是否重跑进球验证、收窄假阳性片段，或重写最终解说。 |
