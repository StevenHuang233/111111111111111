# Night Goal Reflection Report / Night 进球反思后处理报告

EN: This report is produced after full commentary generation. It rewrites unverified goal claims into replay, shot, or dangerous-attack commentary.

ZH: 本报告在完整解说生成之后产出，将未核验的进球宣称改写为回放、射门或危险进攻解说。

## Summary / 摘要

- `segments`: 235
- `verified_score_changes`: 8
- `goal_assertion_segments_before`: 57
- `primary_verified_goal_segments`: 8
- `rewritten_false_positive_segments`: 49
- `sanitized_non_goal_score_claim_segments`: 11
- `sanitized_forbidden_entity_segments`: 0
- `sanitized_prematch_action_segments`: 0
- `api_review_segments`: 0
- `remaining_goal_type_segments`: 8

## Verified Primary Goals / 保留的真实进球片段

| Event | Goal | Time | Score Change |
| --- | --- | --- | --- |
| U028 | G01 | `00:14:08-00:15:28` | 0-0 -> 1-0 |
| U068 | G02 | `00:30:32-00:31:20` | 1-0 -> 1-1 |
| U102 | G03 | `00:45:16-00:46:36` | 1-1 -> 2-1 |
| U134 | G04 | `00:57:00-00:58:20` | 2-1 -> 3-1 |
| U143 | G05 | `01:01:48-01:02:00` | 3-1 -> 4-1 |
| U190 | G06 | `01:25:12-01:25:24` | 4-1 -> 5-1 |
| U208 | G07 | `01:31:12-01:32:36` | 5-1 -> 6-1 |
| U220 | G08 | `01:42:00-01:43:24` | 6-1 -> 7-1 |

## Rewritten False Positives / 已改写误判进球

| Event | Time | Old Type | New Type | Reason | Expected Score | Excerpt |
| --- | --- | --- | --- | --- | --- | --- |
| U023 | `00:11:00-00:11:56` | celebration_or_replay | celebration_or_replay | not_near_verified_score_change | 0-0 | Germany builds a dangerous attack in the final third, with multiple players converging in the penalty area. A shot is taken from inside the box — the ball finds the back of the net as the Curacao keeper is beaten. The go |
| U030 | `00:15:44-00:15:56` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 1-0 | Germany take an early lead as Nmecha finds the back of the net in the 6th minute. The replay shows a well-worked move building up to the goal, with German attackers pressing forward and Curacao defenders struggling to co |
| U032 | `00:17:16-00:17:16` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 1-0 | Germany's No. 10, Müller, turns away from the pitch as the crowd erupts — a quiet moment after the opener. The scoreboard holds at 1-0, and this close-up captures the calm before the next phase. / Müller #10 walks off as |
| U034 | `00:17:28-00:17:28` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 23 drives forward with pace, taking a shot under pressure from Curacao's defender. The ball is struck cleanly toward goal — a moment of sharp attacking intent. / Germany's No. 23 takes a shot on goal. / 德国队 |
| U046 | `00:20:04-00:20:08` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 1-0 | Nmecha finds the net for Germany in the 6th minute, putting them ahead 1-0 against Curacao. The scoreboard confirms the goal as players regroup for the restart. / Nmecha scores for Germany at 6', making it 1-0. / 第6分钟，内梅 |
| U047 | `00:20:36-00:21:32` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany builds pressure in Curacao's penalty area, with multiple attackers converging near the edge of the 18-yard zone. A German player takes a shot from inside the box, and the ball finds its way past the diving goalke |
| U049 | `00:22:52-00:23:44` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany takes an early lead! Wirtz (No. 17) finds space on the edge of the box, cuts inside, and fires a low shot past the diving Curacao goalkeeper into the bottom corner. The net ripples as the ball crosses the line —  |
| U056 | `00:27:04-00:27:04` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 1-0 | Curacao's No. 2 drives forward into the final third, pressing Germany's defense with urgency. Germany's No. 10 and No. 5 close in to contain the threat as the goalkeeper remains alert near the goal line. / Curacao's No.  |
| U057 | `00:27:48-00:27:52` | dangerous_attack | shot | not_near_verified_score_change | 1-0 | Germany builds a dangerous attack in the final third. A German player makes a run towards the penalty area, supported by teammates, creating a promising offensive situation for Curacao to defend. The ball is moved into t |
| U058 | `00:27:56-00:27:56` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 14 takes a shot from inside the penalty area. The ball is struck towards the goal, but it does not result in a goal. / Germany's No. 14 takes a shot from inside the penalty area. / 德国队14号在禁区前沿起脚射门，皮球直挂球门，可惜 |
| U073 | `00:33:04-00:33:16` | goal | shot | not_near_verified_score_change | 1-1 | Curacao take a close-range shot from inside the box — the ball beats the diving German goalkeeper and finds the back of the net! The net ripples, the ball is clearly over the line, and German defenders sit on the ground  |
| U074 | `00:33:20-00:33:24` | period_transition | dangerous_attack | not_near_verified_score_change | 1-1 | The teams are resetting for the restart after the equalizer. The scoreboard confirms it's 1-1 as Germany and Curacao line up for the kickoff in this World Cup 2026 clash. / Teams resetting for restart after the equalizer |
| U077 | `00:34:52-00:36:12` | goal | celebration_or_replay | not_near_verified_score_change | 1-1 | Germany's No. 10 takes a free kick near the penalty area. The goalkeeper directs the wall as players position themselves. The ball is struck and flies into the net, equalizing the score at 1-1. Curacao players celebrate  |
| U085 | `00:37:24-00:38:36` | goal | shot | not_near_verified_score_change | 1-1 | Germany takes a corner kick. The ball is delivered into the penalty area, and a German player heads it towards goal. The Curacao goalkeeper dives but cannot reach the ball, and it goes into the net. Germany scores! / Ger |
| U093 | `00:41:24-00:41:24` | shot | shot | not_near_verified_score_change | 1-1 | Germany's No. 10 takes a shot from inside the penalty area. The ball is in mid-air heading towards the goal, and the goalkeeper is reacting to the shot. / Germany's No. 10 shoots from inside the box. / 德国队10号在禁区前沿起脚射门，皮球 |
| U097 | `00:42:52-00:43:08` | dangerous_attack | shot | not_near_verified_score_change | 1-1 | Curacao's No. 12 drives forward with the ball, cutting through Germany's midfield pressure. He enters the penalty area and unleashes a powerful shot from close range — the ball finds the back of the net! The German goalk |
| U111 | `00:49:40-00:50:36` | goal | shot | not_near_verified_score_change | 2-1 | Germany's No. 10 dribbles into the penalty area, drawing multiple defenders and creating a promising scoring opportunity. He takes a shot inside the box; the ball enters the net as the goalkeeper dives but fails to save  |
| U130 | `00:55:52-00:55:56` | penalty | dangerous_attack | not_near_verified_score_change | 2-1 | A penalty is awarded to Germany after a foul inside the box. German No. 13 goes down under contact from a Curacao defender near the goal line. The referee points to the spot as players regroup for the kick. / Penalty awa |
| U133 | `00:56:16-00:56:48` | free_kick | celebration_or_replay | duplicate_or_replay_near_verified_goal | 2-1 | Germany's No. 7, Wirtz, prepares to take a free kick just outside the penalty area. The referee ensures the defensive wall is set and the goalkeeper is in position. Wirtz places the ball carefully, takes a step back, and |
| U135 | `00:58:40-00:59:08` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 3-1 | Half-time at the World Cup in 2026, and Germany hold a commanding 3-1 lead over Curacao. The German players are seen walking off the pitch, with some donning training bibs as they head towards the tunnel. Goalkeeper Neue |
| U144 | `01:02:28-01:02:44` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany scores! A German player takes a shot that beats the diving Curacao goalkeeper and finds the back of the net. The net ripples as the ball crosses the line, confirming the goal. Immediate celebrations erupt on the  |
| U145 | `01:02:56-01:03:00` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany lead 4-1 at halftime, with Musiala adding a late goal just before the break. The scoreboard confirms the scoreline as players regroup for the second half. / Germany 4-1 Curacao at halftime. Musiala scores just be |
| U149 | `01:06:04-01:06:44` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany takes control in the attacking half, and it's Musiala who finds space inside the box. He fires a low shot from close range — the ball beats the keeper and nestles into the net! The crowd erupts as Musiala celebra |
| U150 | `01:07:36-01:07:44` | dangerous_attack | shot | not_near_verified_score_change | 4-1 | Germany builds a dangerous attack in the final third. The ball is worked into the penalty area, and with multiple German players making runs, they create pressure on the Curacao defense. A shot is fired from inside the b |
| U155 | `01:09:12-01:10:04` | celebration_or_replay | shot | not_near_verified_score_change | 4-1 | Germany's No. 17 takes a shot from outside the box, and the ball finds the back of the net! The scoreboard updates to 4-1 for Germany. Players celebrate as the crowd cheers. / Germany's No. 17 scores from outside the box |
| U160 | `01:12:24-01:12:32` | celebration_or_replay | shot | not_near_verified_score_change | 4-1 | Germany's No. 10, Jamal Musiala, finds the back of the net once more. The scoreboard confirms it: Germany leads 4-1. Musiala is shown on the ground, catching his breath after the strike. A graphic overlay highlights this |
| U164 | `01:14:52-01:15:00` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany's No. 16 finds space inside the box and fires a low shot that beats the diving Curacao goalkeeper — it’s in! The net ripples as the ball crosses the line, and Germany takes a commanding lead. Replays show the pre |
| U166 | `01:16:04-01:16:04` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 4-1 | Germany's No. 10 drives forward into the final third, drawing multiple Curacao defenders as he enters the penalty area. The German attacker looks to combine with a teammate in the box, creating a promising overload near  |
| U169 | `01:16:48-01:16:52` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | Germany takes a commanding 4-1 lead, and the home crowd erupts in celebration. Fans wave German flags and cheer wildly as the scoreboard confirms the score at 61:10. / Germany 4-1 Curacao – Crowd erupts in celebration. / |
| U170 | `01:16:56-01:16:56` | period_transition | dangerous_attack | not_near_verified_score_change | 4-1 | Germany take a corner kick at the right side of the field, with the score standing at 4-1 in their favor as they look to extend their lead. / Germany take a corner kick at the right side of the field, with the score stan |
| U174 | `01:17:40-01:17:40` | shot | shot | not_near_verified_score_change | 4-1 | Curacao's No. 11 unleashes a powerful shot from range, the ball hurtling toward Germany's goal as goalkeeper #1 in red braces for impact. The scoreboard remains 4-1 — this strike will be remembered for its ambition, not  |
| U175 | `01:17:44-01:17:44` | dangerous_attack | shot | not_near_verified_score_change | 4-1 | Curacao's No. 23 drives a shot into the penalty area, and the ball flies toward the goal as Germany's defenders scramble to react. The goalkeeper is on his feet, tracking the ball’s path — this is a dangerous moment in f |
| U176 | `01:18:08-01:18:40` | goal | celebration_or_replay | not_near_verified_score_change | 4-1 | Germany takes control in the final third — a crisp run into the box, and the ball finds the back of the net! The net ripples as the goalkeeper is beaten, and Sané immediately points skyward in celebration. The crowd erup |
| U184 | `01:21:32-01:22:04` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | Curacao take a free kick in a dangerous position. The ball is struck towards the goal and finds the back of the net! The Curacao fans and players erupt in celebration as the scoreboard updates to 4-1. / Curacao free kick |
| U185 | `01:23:16-01:24:12` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany's No. 18, Brown, finds space inside the box and fires a low shot that beats the diving Curacao goalkeeper. The ball nestles into the bottom corner as the net ripples — goal confirmed. Brown celebrates with teamma |
| U186 | `01:24:16-01:24:24` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany's No. 10 brings his hands to his head in celebration, joined by teammate No. 7 as the stadium erupts. The German fans are on their feet, waving flags and cheering loudly — pure elation following a crucial goal. / |
| U193 | `01:26:24-01:26:36` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany extend their lead! The scoreboard confirms 5-1 as the German players erupt in celebration. Tah (No. 4) is seen embracing teammates and staff, while Rügge (No. 7) pumps his fist with intensity. The crowd roars as  |
| U197 | `01:27:44-01:27:44` | dangerous_attack | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Germany's No. 10 threads a perfect through ball, splitting the Curacao defense as the runner surges into the penalty area. The ball is played with precision, and the German attacker finds space to threaten the goal — a m |
| U201 | `01:28:56-01:29:00` | dangerous_attack | shot | not_near_verified_score_change | 5-1 | Curacao counter-attack in full flow! A blue-shirted attacker breaks past the halfway line, driving forward with pace. Germany's defenders scramble to recover as the attack enters the final third. The ball is moved quickl |
| U205 | `01:29:44-01:30:32` | goal | celebration_or_replay | not_near_verified_score_change | 5-1 | Germany takes control in the attacking third. A German player receives the ball just outside the penalty area, under pressure from a Curacao defender. He drives forward, evades the challenge, and unleashes a powerful sho |
| U209 | `01:33:12-01:33:12` | dangerous_attack | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Germany's No. 10 drives into the box under pressure from a Curacao defender, forcing the goalkeeper to narrow the angle. The attacker holds his touch, scanning for a pass or shot as the defense closes in — a moment of co |
| U211 | `01:33:40-01:33:48` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 6-1 | Germany's No. 26, Deniz Undav, is seen in a moment of sportsmanship, smiling and interacting with a Curacao player. The scoreboard remains at 6-1, indicating this is a post-goal sequence. Undav's recent form is highlight |
| U214 | `01:35:48-01:36:56` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 6-1 | Germany takes a penalty kick in the 82nd minute. The ball is struck with precision and finds the back of the net as the Curacao goalkeeper is beaten. The German players erupt in celebration, with Kimmich (No. 6) and Anto |
| U218 | `01:38:04-01:38:24` | goal | shot | not_near_verified_score_change | 6-1 | Curacao's attacker in blue and yellow drives forward into Germany's half, drawing defenders as he approaches the penalty area. He takes a shot from inside the box — but it’s Germany who seize the moment. Wirtz, No. 19, f |
| U219 | `01:39:36-01:40:24` | goal | shot | not_near_verified_score_change | 6-1 | Germany takes the lead in this World Cup match against Curacao! The German player, wearing number 22, receives a pass near the penalty area and unleashes a powerful shot that beats the Curacao goalkeeper, who dives but f |
| U221 | `01:43:40-01:43:44` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 7-1 | Havertz adds a second goal for Germany in the 88th minute, extending their lead to 7-1. The scoreboard confirms his brace, including a penalty in first-half stoppage time. Germany players regroup as Curacao look to respo |
| U225 | `01:46:32-01:47:44` | goal | celebration_or_replay | not_near_verified_score_change | 7-1 | Curacao's No. 10 drives forward with the ball, challenged by Germany's No. 22 near the penalty area. The assistant referee raises his flag for a foul, and Germany's No. 22 prepares for the free kick restart. But moments  |
| U230 | `01:48:12-01:49:28` | goal | shot | not_near_verified_score_change | 7-1 | Germany wins a free kick just outside the penalty area. The player steps up, takes a run, and strikes it with precision. The ball curls past the wall and into the top corner of the net! The Curacao goalkeeper dives but c |
| U233 | `01:50:12-01:50:24` | period_transition | dangerous_attack | not_near_verified_score_change | 7-1 | Full time in this World Cup encounter, and Germany have sealed a commanding 7-1 victory over Curacao. The final whistle blows as players from both sides gather on the pitch, acknowledging the crowd and the result. The sc |

## Sanitized Non-Goal Score Claims / 已清洗非进球数字比分片段

| Event | Time | Type | Reason |
| --- | --- | --- | --- |
| U071 | `00:31:52-00:32:44` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U091 | `00:40:40-00:40:40` | save | non_goal_segment_should_not_repeat_numeric_score |
| U095 | `00:41:44-00:41:44` | save | non_goal_segment_should_not_repeat_numeric_score |
| U110 | `00:48:48-00:49:08` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U115 | `00:51:40-00:53:04` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U116 | `00:53:12-00:53:12` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U139 | `01:00:48-01:00:52` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U188 | `01:24:36-01:24:36` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U191 | `01:25:44-01:25:56` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U222 | `01:44:28-01:44:28` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U231 | `01:49:36-01:49:40` | period_transition | non_goal_segment_should_not_repeat_numeric_score |

## Other Safety Sanitizers / 其他安全清洗

- `forbidden_entity_sanitized`: 0
- `prematch_action_sanitized`: 0

## API Hook / API 接口

- `api_mode`: off
- `api_review_segments`: 0
EN: Use `--api-mode review --frame-root <frames>` to attach Intern-S2 visual reflection evidence to selected suspect segments.
ZH: 使用 `--api-mode review --frame-root <frames>` 可以让 Intern-S2 对选中的可疑片段追加视觉反思证据。
