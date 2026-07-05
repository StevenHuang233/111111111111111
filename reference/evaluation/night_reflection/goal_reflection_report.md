# Night Goal Reflection Report / Night 进球反思后处理报告

EN: This report is produced after full commentary generation. It rewrites unverified goal claims into replay, shot, or dangerous-attack commentary.

ZH: 本报告在完整解说生成之后产出，将未核验的进球宣称改写为回放、射门或危险进攻解说。

## Summary / 摘要

- `segments`: 235
- `verified_score_changes`: 8
- `goal_assertion_segments_before`: 61
- `primary_verified_goal_segments`: 8
- `rewritten_false_positive_segments`: 53
- `sanitized_non_goal_score_claim_segments`: 11
- `sanitized_forbidden_entity_segments`: 1
- `sanitized_prematch_action_segments`: 1
- `api_review_segments`: 0
- `remaining_goal_type_segments`: 8

## Verified Primary Goals / 保留的真实进球片段

| Event | Goal | Time | Score Change |
| --- | --- | --- | --- |
| U028 | G01 | `00:14:08-00:15:28` | 0-0 -> 1-0 |
| U061 | G02 | `00:28:56-00:28:56` | 1-0 -> 1-1 |
| U102 | G03 | `00:45:16-00:46:36` | 1-1 -> 2-1 |
| U134 | G04 | `00:57:00-00:58:20` | 2-1 -> 3-1 |
| U143 | G05 | `01:01:48-01:02:00` | 3-1 -> 4-1 |
| U188 | G06 | `01:24:36-01:24:36` | 4-1 -> 5-1 |
| U208 | G07 | `01:31:12-01:32:36` | 5-1 -> 6-1 |
| U220 | G08 | `01:42:00-01:43:24` | 6-1 -> 7-1 |

## Rewritten False Positives / 已改写误判进球

| Event | Time | Old Type | New Type | Reason | Expected Score | Excerpt |
| --- | --- | --- | --- | --- | --- | --- |
| U018 | `00:08:08-00:08:24` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 0-0 | Germany players in white kits huddle together in celebration on the pitch, with German flags visible in the background crowd. Close-up of Germany players continuing their team huddle/celebration, showing emotional intens |
| U023 | `00:11:00-00:11:56` | goal | celebration_or_replay | not_near_verified_score_change | 0-0 | Germany takes an early lead! The buildup starts with Germany's No. 5 driving forward, beating a diving Curacao defender. He enters the penalty area and fires a shot that finds the back of the net. The net ripples as the  |
| U026 | `00:12:28-00:12:32` | dangerous_attack | shot | not_near_verified_score_change | 0-0 | Germany builds a dangerous attack as the ball moves into Curacao's final third. A German player drives forward with pace, drawing multiple defenders toward the penalty area. The Curacao goalkeeper remains alert near the  |
| U030 | `00:15:44-00:15:56` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 1-0 | And there it is! Germany takes an early lead in this World Cup clash. Nmecha finds space inside the box, collects a pass, and fires a low shot that beats the diving Curacao goalkeeper. The scoreboard confirms it: Germany |
| U032 | `00:17:16-00:17:16` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 1-0 | Germany's No. 10, Müller, walks away from the play as the crowd reacts — a moment of quiet aftermath following the earlier goal. The scoreboard confirms Germany leads 1-0, and this close-up captures the calm after the st |
| U034 | `00:17:28-00:17:28` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 23 drives forward, takes a shot under pressure from Curacao's defender — the ball is struck toward goal, but whether it finds the net remains to be seen. / Germany No. 23 shoots under challenge / 德国队23号球员带球 |
| U040 | `00:18:52-00:18:52` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 1-0 | Germany's No. 10, Kai Havertz, finds space inside the box as he receives the ball under pressure from a Curacao defender. The German attacker is positioned centrally near the goal, creating a high-probability scoring opp |
| U046 | `00:20:04-00:20:08` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 1-0 | Germany take an early lead as Nmecha finds the net in the sixth minute. The scoreboard confirms the goal, and the stadium reacts to this decisive moment. / Germany 1-0 Curacao: Nmecha scores in the 6th minute. / 德国队率先取得领 |
| U047 | `00:20:36-00:21:32` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany takes an early lead! At 11:53, Germany's No. 23 receives the ball just outside the penalty area, drives forward past a Curacao defender, and fires a low shot that beats the diving goalkeeper into the bottom corne |
| U049 | `00:22:52-00:23:44` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany takes the lead! Wirtz (No. 17) finds the back of the net with a precise strike, beating the diving goalkeeper. The scoreboard updates to 1-0 as he collects the ball in celebration. Replays show the ball nestling  |
| U068 | `00:30:32-00:31:20` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 1-1 | Curacao strike first! The blue-and-yellow kit players are celebrating wildly as the ball finds the net. A Curacao attacker, wearing number 8, takes a powerful shot from inside the penalty area that beats the German goalk |
| U073 | `00:33:04-00:33:16` | goal | shot | not_near_verified_score_change | 1-1 | Curacao strike from close range! The ball finds the back of the net as Germany's defenders are caught out. Comenencia (No. 8) celebrates with his teammates, while German players sit on the ground in disappointment. / Cur |
| U074 | `00:33:20-00:33:24` | period_transition | dangerous_attack | not_near_verified_score_change | 1-1 | The teams are resetting on the pitch after the goal, with the scoreboard showing a 1-1 tie. Players from both Germany and Curacao are positioning themselves for the restart as the crowd settles back into anticipation. /  |
| U077 | `00:34:52-00:36:12` | goal | celebration_or_replay | not_near_verified_score_change | 1-1 | Germany's No. 17, Wirtz, takes the free kick near the penalty area. The ball is delivered into the box, and a German player rises to meet it with a powerful header. The ball flies past the diving goalkeeper and into the  |
| U085 | `00:37:24-00:38:36` | goal | shot | not_near_verified_score_change | 1-1 | Germany takes the lead! Germany's No. 17 dribbles forward, evades a Curacao defender, and delivers a precise cross into the penalty area. A German attacker meets it with a powerful shot that beats the diving Curacao goal |
| U087 | `00:40:12-00:40:12` | shot | shot | not_near_verified_score_change | 1-1 | Germany's No. 19 takes a shot from inside the penalty box. The ball is struck with intent towards the goal, and the goalkeeper reacts to the incoming threat. / Germany's No. 19 shoots from inside the box. / 德国队19号在禁区前沿起脚 |
| U090 | `00:40:36-00:40:36` | shot | shot | not_near_verified_score_change | 1-1 | Germany's No. 18 unleashes a powerful strike from distance, the ball rocketing toward the goal as Curacao's defenders scramble to react. / Germany's No. 18 shoots! / 德国队18号球员在禁区外大力轰门，皮球如炮弹般直挂球门，库拉索的防守球员纷纷回追试图补救。 / 德国队18号 |
| U111 | `00:49:40-00:50:36` | goal | shot | not_near_verified_score_change | 2-1 | Germany's No. 10, Möller, takes a shot inside the box. The ball enters the net as the goalkeeper dives but fails to save it. The net ripples, confirming the goal. Close-up shot of a Curacao player showing a disappointed  |
| U112 | `00:50:48-00:50:48` | shot | shot | not_near_verified_score_change | 2-1 | Germany's No. 8 drives a shot from inside the box, forcing a reaction from the Curacao goalkeeper. / Germany's No. 8 takes a shot on goal. / 德国队8号在禁区起脚射门，库拉索门将被迫做出反应。 / 德国队8号射门。 |
| U115 | `00:51:40-00:53:04` | goal | celebration_or_replay | not_near_verified_score_change | 2-1 | Germany takes a free kick near the penalty area. The German player strikes the ball, and it goes into the goal. The goalkeeper dives but cannot stop it. The German players celebrate as the ball crosses the goal line. / G |
| U131 | `00:56:08-00:56:08` | free_kick | dangerous_attack | not_near_verified_score_change | 2-1 | Germany's No. 10 steps up for a free kick just outside the penalty area. The defensive wall is set, the referee signals for play to resume, and the ball is struck with precision — curling over the wall and into the top c |
| U135 | `00:58:40-00:59:08` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 3-1 | Half-time at the World Cup 2026, and Germany hold a 3-1 lead over Curacao. The scoreboard confirms Havertz’s penalty, Schlotterbeck’s strike, and Nmecha’s early opener for Germany, while Comenencia pulled one back for Cu |
| U144 | `01:02:28-01:02:44` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany's No. 10 finds space inside the box and fires a low shot past the diving Curacao goalkeeper. The ball nestles into the back of the net as the net ripples—goal confirmed. The German coach erupts on the bench, and  |
| U145 | `01:02:56-01:03:00` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany take a commanding 4-1 lead into halftime, with Musiala adding a late flourish just before the break. The scoreboard confirms the scoreline as players begin to regroup for the second half. / Germany lead 4-1 at ha |
| U149 | `01:06:04-01:06:44` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany's No. 10, Jamal Musiala, finds space inside the box and fires a low shot from close range. The ball beats the diving Curacao goalkeeper and nestles into the bottom corner! Musiala celebrates with a hand-to-ear ge |
| U150 | `01:07:36-01:07:44` | dangerous_attack | shot | not_near_verified_score_change | 4-1 | Germany builds a dangerous attack as they move the ball into the final third. Players are entering the penalty area, creating pressure on the Curacao defense. A German player takes a shot from inside the penalty area, an |
| U155 | `01:09:12-01:10:04` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany in white shirts is attacking in the final third with multiple players entering the penalty area, creating a promising chance against Curacao's defense. A German player takes a shot on goal, the ball enters the ne |
| U160 | `01:12:24-01:12:32` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | Germany's No. 10, Jamal Musiala, finds the back of the net once more — his 10th goal for the national team. The scoreboard confirms Germany leads 4-1 as Musiala catches his breath, visibly spent but composed. A Curacao p |
| U164 | `01:14:52-01:15:00` | goal | shot | not_near_verified_score_change | 4-1 | Germany's No. 16 finds the back of the net with a sharp strike inside the box, beating the diving Curacao keeper. The net ripples as the ball crosses the line, and German players begin to reset while the Curacao keeper c |
| U169 | `01:16:48-01:16:52` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | Germany fans erupt in celebration as their team extends the lead to 4-1. The crowd is electric, waving flags and cheering wildly. / Germany fans celebrate wildly after extending their lead to 4-1. / 德国队球迷沸腾了！球队将比分扩大为4-1， |
| U171 | `01:17:00-01:17:08` | corner | dangerous_attack | not_near_verified_score_change | 4-1 | Germany wins a corner kick on the right flank. The ball is placed at the arc as players from both teams jostle for position inside the penalty area. The Curacao goalkeeper stands alert in his goal, ready to react to the  |
| U172 | `01:17:12-01:17:28` | free_kick | shot | not_near_verified_score_change | 4-1 | Germany win a free kick just outside the penalty area. The referee is ensuring the defensive wall is set as Germany's No. 17 steps up to take it. He strikes it with precision, curling it over the wall and into the top co |
| U174 | `01:17:40-01:17:40` | shot | shot | not_near_verified_score_change | 4-1 | Curacao's No. 11 finds space and unleashes a shot from range. The ball travels with intent toward the goal, but Germany's goalkeeper, No. 1, is alert and ready to react. A moment of threat, but the score remains 4-1 as t |
| U175 | `01:17:44-01:17:44` | dangerous_attack | shot | not_near_verified_score_change | 4-1 | Curacao's No. 8 sends a shot flying into the box, and the German defense scrambles to clear it as the ball hangs in the air near the goal line. / Curacao's No. 8 shoots into the box / 库拉索队8号一脚劲射直捣禁区，德国队后卫们仓促解围，皮球悬在球门线附近。 |
| U176 | `01:18:08-01:18:40` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany's No. 19, Sane, drives into the penalty area with pace and composure, beating the offside trap. He takes a touch to set himself, then fires a low shot across the keeper. The ball finds the back of the net — net r |
| U184 | `01:21:32-01:22:04` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Curacao takes a free kick just outside the penalty area. The ball is struck with precision, curling past the defensive wall and into the top corner of the net. The German goalkeeper dives but cannot reach it. The Curacao |
| U185 | `01:23:16-01:24:12` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany breaks through! Germany's No. 18 receives the ball inside the penalty area, takes a shot with his right foot, and the ball flies past the diving Curacao goalkeeper into the net. The goal is confirmed as the score |
| U193 | `01:26:24-01:26:36` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany extend their lead! The scoreboard reads 5-1 as the German players erupt in celebration. Tah (No. 4) is seen embracing teammates and staff, while Rügger (No. 7) pumps his fist in triumph. The crowd roars, with a y |
| U197 | `01:27:44-01:27:44` | dangerous_attack | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Germany's No. 10 threads a perfect through ball, splitting the Curacao defense as the runner surges into the box — a razor-thin chance that demands composure under pressure. / Germany's No. 10 threads a through ball — ru |
| U198 | `01:27:48-01:27:48` | shot | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Germany's No. 10 finds space inside the box and unleashes a powerful shot towards the goal. The Curacao goalkeeper reacts quickly, but it's too late as the ball nestles into the back of the net! / Germany scores! / 德国队10 |
| U199 | `01:28:00-01:28:00` | shot | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Curacao's No. 10 takes a shot from the left flank, driving it toward the goal as Germany's No. 17 reacts in defense. / Curacao No. 10 shoots / 库拉索队10号从左路起脚射门，皮球直逼球门，德国队17号迅速回防应对。 / 库拉索10号射门 |
| U202 | `01:29:04-01:29:04` | shot | shot | not_near_verified_score_change | 5-1 | Curacao's No. 11 fires a shot from inside the penalty area, but Germany's goalkeeper is alert and makes a clean catch to keep the scoreline intact. / Curacao's No. 11 shoots, but the German keeper catches it cleanly. / 库 |
| U205 | `01:29:44-01:30:32` | goal | celebration_or_replay | not_near_verified_score_change | 5-1 | Germany's No. 22 receives the ball inside the penalty area, closely marked by a Curacao defender. He takes a touch to set himself and fires a low shot toward the near post. The Curacao goalkeeper dives but cannot reach i |
| U211 | `01:33:40-01:33:48` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 6-1 | Germany's Deniz Undav (26) is shown in a post-goal moment, smiling and sharing a brief interaction with Curacao's No. 7. The scoreboard remains 6-1 as the camera highlights his recent form — 7 goals in his last 7 caps —  |
| U214 | `01:35:48-01:36:56` | goal | shot | not_near_verified_score_change | 6-1 | Germany awarded a penalty kick in the 81st minute. The German player steps up and takes the shot, sending the ball past the Curacao goalkeeper into the net. The goal is confirmed, and the German players celebrate their 7 |
| U218 | `01:38:04-01:38:24` | goal | dangerous_attack | not_near_verified_score_change | 6-1 | Germany's No. 19 Wirtz finds space in the box, takes a touch, and fires into the bottom corner — net rippling as the ball crosses the line. The scoreboard confirms it: 6-1 to Germany. Wirtz celebrates with teammates as t |
| U219 | `01:39:36-01:40:24` | goal | celebration_or_replay | not_near_verified_score_change | 6-1 | Germany takes control in the 85th minute! No. 22 finds space on the edge of the box, fires a low drive past the diving Curacao keeper — net ripples, scoreboard updates to 6-1. The German attacker celebrates with a mix of |
| U221 | `01:43:40-01:43:44` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 7-1 | Havertz adds a second goal for Germany in the 88th minute, extending their lead to 7-1 against Curacao. The scoreboard confirms his brace, including a penalty in the first half, as Germany maintains control late into the |
| U223 | `01:45:20-01:45:20` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 7-1 | Germany in the final third, a dangerous attack as a German player enters the penalty area and makes a move towards goal, creating a promising chance as defenders converge. / Germany in the final third, a dangerous attack |
| U225 | `01:46:32-01:47:44` | goal | celebration_or_replay | not_near_verified_score_change | 7-1 | Curacao's No. 10 drives forward, but Germany's No. 22 brings him down near the touchline. The assistant raises the flag for offside. Germany's No. 22 takes the free kick, and with a precise pass, he finds a teammate who  |
| U230 | `01:48:12-01:49:28` | goal | dangerous_attack | not_near_verified_score_change | 7-1 | Germany takes a free kick near the penalty area. The ball is struck with precision and sails into the net, leaving the Curacao goalkeeper with no chance. The German players celebrate as the goal is confirmed, adding to t |
| U231 | `01:49:36-01:49:40` | period_transition | dangerous_attack | not_near_verified_score_change | 7-1 | The final whistle blows at 95:10, +5 minutes added time, as Germany seal a commanding 7-1 victory over Curacao in their World Cup 2026 opener. Players from both sides begin to disperse across the pitch — some walking off |
| U233 | `01:50:12-01:50:24` | period_transition | dangerous_attack | not_near_verified_score_change | 7-1 | The final whistle blows in Houston as Germany secure a commanding 7-1 victory over Curacao in their FIFA World Cup 2026 opener. Havertz fires in two, including a penalty, while Schlotterbeck, Nmecha, Musiala, Brown, and  |

## Sanitized Non-Goal Score Claims / 已清洗非进球数字比分片段

| Event | Time | Type | Reason |
| --- | --- | --- | --- |
| U062 | `00:29:00-00:29:00` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U071 | `00:31:52-00:32:44` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U110 | `00:48:48-00:49:08` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U116 | `00:53:12-00:53:12` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U118 | `00:53:28-00:53:28` | other_relevant | non_goal_segment_should_not_repeat_numeric_score |
| U139 | `01:00:48-01:00:52` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U170 | `01:16:56-01:16:56` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U178 | `01:19:08-01:19:56` | substitution | non_goal_segment_should_not_repeat_numeric_score |
| U191 | `01:25:44-01:25:56` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U215 | `01:36:20-01:36:52` | substitution | non_goal_segment_should_not_repeat_numeric_score |
| U222 | `01:44:28-01:44:28` | period_transition | non_goal_segment_should_not_repeat_numeric_score |

## Other Safety Sanitizers / 其他安全清洗

- `forbidden_entity_sanitized`: 1
- `prematch_action_sanitized`: 1

## API Hook / API 接口

- `api_mode`: off
- `api_review_segments`: 0
EN: Use `--api-mode review --frame-root <frames>` to attach Intern-S2 visual reflection evidence to selected suspect segments.
ZH: 使用 `--api-mode review --frame-root <frames>` 可以让 Intern-S2 对选中的可疑片段追加视觉反思证据。
