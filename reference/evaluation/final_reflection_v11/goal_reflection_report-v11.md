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
- `sanitized_forbidden_entity_segments`: 0
- `sanitized_prematch_action_segments`: 1
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
| U018 | `00:08:08-00:08:24` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 0-0 | Germany players in white kits huddle together in celebration on the pitch, with German flags visible in the background crowd. Close-up of Germany players continuing their team huddle/celebration, showing emotional intens |
| U030 | `00:15:44-00:15:56` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 1-0 | The replay shows the moment Nmecha broke through Curacao's defense. With precise control, he dribbled past the midfield line and into the penalty area, evading retreating defenders. As he approached the goal, he unleashe |
| U032 | `00:17:16-00:17:16` | celebration_or_replay | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany's No. 10, Müller, turns away as the crowd reacts — a moment of quiet aftermath after the goal. The scoreboard holds at 1-0, and the replay angle suggests this is part of the post-goal sequence, not a new event. / |
| U034 | `00:17:28-00:17:28` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 23 drives forward with the ball, challenged closely by a Curacao defender. He unleashes a powerful shot toward goal — the ball is struck cleanly, but whether it finds the back of the net remains to be seen. |
| U040 | `00:18:52-00:18:52` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 1-0 | Germany's No. 10, Kai Havertz, finds himself in a prime position inside the penalty area. He receives the ball under pressure from a Curacao defender, creating a high-probability scoring opportunity as he is positioned c |
| U045 | `00:19:48-00:19:48` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 19, Sane, finds space in the box and unleashes a powerful shot on goal. The ball is struck cleanly with his right foot, heading toward the far post as two Curacao defenders close in. The keeper reacts insta |
| U046 | `00:20:04-00:20:08` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 1-0 | Germany takes an early lead in this World Cup clash as Nmecha finds the back of the net in the 6th minute. The scoreboard confirms the goal, and the players are now resetting for the next phase of play. / Germany leads 1 |
| U047 | `00:20:36-00:21:32` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany builds pressure in Curacao's half, with multiple attackers entering the penalty area. A German player takes a shot from inside the box, and the ball finds the back of the net as the goalkeeper dives in vain. The  |
| U049 | `00:22:52-00:23:44` | goal | celebration_or_replay | not_near_verified_score_change | 1-0 | Germany takes an early lead in this World Cup clash against Curacao. The breakthrough comes from a well-timed run by Germany's No. 17, Wirtz, who finds space inside the box and fires a precise shot past the diving Curaca |
| U052 | `00:24:20-00:24:20` | shot | shot | not_near_verified_score_change | 1-0 | Germany's No. 23 takes a shot from inside the penalty area, sending the ball toward goal as Curacao's goalkeeper reacts to the threat. / Germany's No. 23 shoots from inside the box / 德国队23号在禁区前沿起脚射门，皮球直挂球门，库拉索门将迅速做出反应。 / |
| U056 | `00:27:04-00:27:04` | dangerous_attack | shot | not_near_verified_score_change | 1-0 | Curacao's No. 2 makes a daring run into the penalty area, closely tracked by Germany's defenders. The goalkeeper is alert, ready to react as the pressure mounts near the goal. / Curacao's No. 2 takes a shot at Germany's  |
| U073 | `00:33:04-00:33:16` | goal | shot | not_near_verified_score_change | 1-1 | Curacao strike from close range! The ball finds the back of the net as German defenders and the goalkeeper are left on the ground in disbelief. Comenencia, wearing number 8, leads the celebration with his teammates, incl |
| U074 | `00:33:20-00:33:24` | period_transition | dangerous_attack | not_near_verified_score_change | 1-1 | The teams are resetting on the pitch after the goal, with the scoreboard showing a 1-1 tie. Players from both Germany and Curacao are positioning themselves for the restart, while the crowd settles back into anticipation |
| U077 | `00:34:52-00:36:12` | goal | celebration_or_replay | not_near_verified_score_change | 1-1 | Germany's No. 17 takes a corner kick, delivering the ball into the penalty area. A German player heads the ball powerfully towards the goal, beating the goalkeeper and sending it into the net. The crowd erupts as the goa |
| U080 | `00:36:28-00:36:28` | free_kick | dangerous_attack | not_near_verified_score_change | 1-1 | Germany awarded a free-kick just outside the box as the referee points decisively towards goal. Players from both sides are positioning themselves for the restart. / Germany awarded a free-kick just outside the box / 德国队 |
| U082 | `00:36:44-00:36:44` | free_kick | shot | not_near_verified_score_change | 1-1 | Germany's No. 17 steps up to take a free kick just outside the penalty area as the referee signals for play to resume. The Curacao defensive line forms a compact wall, and the goalkeeper is alert in position. The stadium |
| U083 | `00:36:52-00:36:52` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 1-1 | Germany's No. 10 drives into the box, drawing multiple defenders before slipping a pass to a teammate on the edge of the area — one-touch, sharp, and dangerous. The crowd leans forward as the ball is played across goal,  |
| U085 | `00:37:24-00:38:36` | goal | celebration_or_replay | not_near_verified_score_change | 1-1 | Germany's No. 17, Wirtz, drives forward with the ball, evading a Curacao defender in midfield. He enters the penalty area, drawing multiple defenders, and delivers a precise pass to a teammate. The ball is struck powerfu |
| U093 | `00:41:24-00:41:24` | shot | shot | not_near_verified_score_change | 1-1 | Germany's No. 10 finds space inside the box and unleashes a powerful shot from close range. The ball rockets toward goal, forcing the Curacao goalkeeper into a sharp reaction. It’s a moment of real pressure — will it fin |
| U097 | `00:42:52-00:43:08` | goal | shot | not_near_verified_score_change | 1-1 | Curacao's No. 12 drives forward with the ball, cutting inside from the right flank as German defenders converge. He finds space just outside the box and unleashes a low, driven shot that beats the German keeper and nestl |
| U110 | `00:48:48-00:49:08` | celebration_or_replay | celebration_or_replay | not_near_verified_score_change | 2-1 | Germany takes the lead! Sané (No. 10) finds the back of the net, putting Germany ahead 2-1 against Curacao. The crowd erupts as fans wave flags and cheer wildly. Replays show the precise strike from inside the box, leavi |
| U111 | `00:49:40-00:50:36` | goal | celebration_or_replay | not_near_verified_score_change | 2-1 | Germany takes the lead! A German player drives into the box, draws defenders, and fires a shot that finds the back of the net as the goalkeeper dives in vain. The net ripples — goal confirmed. Möller celebrates with a fo |
| U116 | `00:53:12-00:53:12` | celebration_or_replay | celebration_or_replay | not_near_verified_score_change | 2-1 | Curacao's No. 12 raises his arms in celebration as the crowd erupts behind him. The scoreboard confirms Germany leads 2-1 at 45:02, suggesting this is a replay or post-goal reaction sequence. A German player in No. 17 pa |
| U119 | `00:53:44-00:53:44` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 2-1 | Germany in the final third, building pressure with multiple attackers entering the penalty area. The ball is moving toward goal as Curacao's defense reacts to contain the threat. / Germany's dangerous attack in the final |
| U124 | `00:55:08-00:55:08` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 2-1 | Germany moves into the final third with multiple players in the penalty area, creating a promising attacking opportunity. / Germany advances into the final third with multiple players in the penalty area. / 德国队带球进入前场，禁区内 |
| U144 | `01:02:28-01:02:44` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany takes the lead! Germany's No. 10 finds space on the edge of the box, drives forward, and fires a low shot that beats the diving Curacao goalkeeper and nestles into the bottom corner. The net ripples as the ball c |
| U145 | `01:02:56-01:03:00` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany take a commanding 4-1 lead into halftime after Musiala's late strike just before the break. The scoreboard confirms the scoreline as players begin to regroup for the second half. / Germany lead 4-1 at halftime th |
| U149 | `01:06:04-01:06:44` | goal | shot | not_near_verified_score_change | 4-1 | Germany scores! Musiala finds the net with a powerful close-range strike. The ball rockets past the diving goalkeeper and into the back of the net. Musiala celebrates with a hand-to-ear gesture, acknowledging the crowd a |
| U150 | `01:07:36-01:07:44` | dangerous_attack | shot | not_near_verified_score_change | 4-1 | Germany builds a dangerous attack in the final third. The ball is worked into the penalty area, where multiple German players converge to pressure Curacao's defense. A shot is fired from inside the box — the ball heads t |
| U155 | `01:09:12-01:10:04` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | Germany's No. 17 is celebrating after the goal, and the crowd is cheering. The scoreboard shows Germany leading 4-1 against Curacao. / Germany's No. 17 celebrates as the scoreboard shows Germany 4-1 Curacao. / 德国队的17号球员正 |
| U160 | `01:12:24-01:12:32` | celebration_or_replay | shot | not_near_verified_score_change | 4-1 | Germany's No. 10, Jamal Musiala, finds the back of the net once again. The scoreboard confirms it: Germany leads 4-1. Musiala catches his breath after the strike, visibly exhausted but composed. A graphic overlay highlig |
| U164 | `01:14:52-01:15:00` | goal | shot | not_near_verified_score_change | 4-1 | Germany's No. 16 finds space inside the box and fires a low shot that beats the diving Curacao goalkeeper into the bottom corner. The net ripples, and the goal is confirmed as the keeper retrieves the ball while German p |
| U169 | `01:16:48-01:16:52` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 4-1 | The German fans are absolutely electric in the stands, waving flags and cheering as the scoreboard confirms Germany's 4-1 lead at the 61-minute mark. The energy is palpable as supporters celebrate what appears to be a re |
| U175 | `01:17:44-01:17:44` | dangerous_attack | dangerous_attack | not_near_verified_score_change | 4-1 | Curacao's No. 23 delivers a dangerous cross into the box, and the ball is met by a teammate in the air. Germany's defenders scramble to clear as the ball hovers near the goal line, but it's not enough to find the back of |
| U176 | `01:18:08-01:18:40` | goal | shot | not_near_verified_score_change | 4-1 | Germany take the lead! Sané finds the back of the net with a powerful strike. The German striker beats the goalkeeper to the ball, sending it into the corner of the net. The crowd erupts in celebration as Sané points sky |
| U184 | `01:21:32-01:22:04` | celebration_or_replay | celebration_or_replay | not_near_verified_score_change | 4-1 | Curacao's No. 7 takes the free kick, and the ball finds the back of the net! The scoreboard updates to 4-1 as Curacao fans erupt in celebration. The replay shows the strike beating the German goalkeeper, and the sideline |
| U185 | `01:23:16-01:24:12` | goal | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany breaks through! Germany's No. 18 takes a shot from inside the area, and the ball finds the back of the net past the diving Curacao goalkeeper. The net ripples as the goal is confirmed, and German players immediat |
| U188 | `01:24:36-01:24:36` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | And we are back in action for the second half. The teams have lined up, Germany looking to build from the back as Curacao set their defensive shape. A level 1-1 scoreline on the screen sets the stage for a renewed battle |
| U191 | `01:25:44-01:25:56` | period_transition | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany hold a commanding 5-1 lead as the match enters the 71st minute. The stadium buzzes with anticipation as players regroup for the next phase of play. / Germany lead 5-1 at the 71st minute mark. / 比赛进入第71分钟，德国队以5-1的 |
| U193 | `01:26:24-01:26:36` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 4-1 | Germany's Tah (No. 4) and Rügger (No. 7) celebrate with teammates and staff as the scoreboard confirms their 5-1 lead. The crowd roars in support, with fans waving 'Deutschland' scarves and flags. / Germany celebrates a  |
| U199 | `01:28:00-01:28:00` | shot | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Curacao's No. 10 takes a shot from the left flank, driving it toward the goal as Germany's No. 17 reacts in close coverage. / Curacao No. 10 shoots / 库拉索队10号从左侧起脚射门，皮球直逼球门，德国队17号在近距离内迅速做出反应。 / 库拉索10号射门 |
| U202 | `01:29:04-01:29:04` | shot | shot | not_near_verified_score_change | 5-1 | Curacao's No. 11 fires a shot from inside the box, the ball hurtling toward goal as Germany's goalkeeper tracks its flight. The outcome hangs in the balance for a split second. / Curacao's No. 11 shoots from inside the a |
| U205 | `01:29:44-01:30:32` | goal | shot | not_near_verified_score_change | 5-1 | Germany takes control in the attacking third, with a German player advancing into Curacao's half under pressure from a defender. The ball is delivered into the penalty area, and as the German attacker meets it, he fires  |
| U209 | `01:33:12-01:33:12` | dangerous_attack | celebration_or_replay | duplicate_or_replay_near_verified_goal | 5-1 | Germany in the final third, a dangerous attack unfolding. The German attacker drives into the penalty area, closely marked by a Curacao defender, as the goalkeeper positions himself near the goal line for an imminent opp |
| U211 | `01:33:40-01:33:48` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 6-1 | Deniz Undav (26) is shown in close-up, smiling and exchanging a moment with a Curacao player — a gesture of sportsmanship following the goal. The scoreboard remains 6-1 as Germany continues to build momentum. Undav’s rec |
| U214 | `01:35:48-01:36:56` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 6-1 | Germany takes a penalty in the 82nd minute. The ball finds the back of the net as the Curacao goalkeeper is beaten. The German players celebrate the goal, with Kimmich (No. 6) and Anton embracing. The scoreboard shows Ge |
| U218 | `01:38:04-01:38:24` | goal | shot | not_near_verified_score_change | 6-1 | Curacao's attacker drives forward, drawing defenders into the box. He unleashes a shot from inside the penalty area — but it’s Germany who respond with precision. Wirtz, No. 19, finds space, finishes clinically, and send |
| U219 | `01:39:36-01:40:24` | goal | shot | not_near_verified_score_change | 6-1 | Germany's No. 22 finds space on the edge of the box, drives forward past Curacao's No. 10, and unleashes a low shot that beats the diving keeper and nestles into the net. The net ripples as the ball crosses the line — go |
| U221 | `01:43:40-01:43:44` | celebration_or_replay | celebration_or_replay | duplicate_or_replay_near_verified_goal | 7-1 | Germany extend their lead in the 88th minute as Havertz finds the net once more, sealing a dominant performance against Curacao. The scoreboard reflects Germany's commanding 7-1 advantage, with Havertz contributing twice |
| U225 | `01:46:32-01:47:44` | goal | celebration_or_replay | not_near_verified_score_change | 7-1 | Curacao's No. 10 drives forward into the German half, closely tracked by Germany's No. 22. The pressure builds as the Curacao attacker cuts inside, drawing defenders. A shot is fired — the ball finds the back of the net! |
| U230 | `01:48:12-01:49:28` | goal | shot | not_near_verified_score_change | 7-1 | Germany wins the penalty kick. The German player takes the shot and scores a goal. The Curacao goalkeeper dives but fails to save it. The German players celebrate the goal. / Germany wins the penalty kick. The German pla |
| U233 | `01:50:12-01:50:24` | period_transition | dangerous_attack | not_near_verified_score_change | 7-1 | The final whistle blows in this World Cup 2026 encounter, and Germany secures a commanding 7-1 victory over Curacao. The scoreboard confirms the result as players begin to disperse from the pitch under the stadium lights |
| U234 | `01:50:28-01:50:36` | celebration_or_replay | dangerous_attack | not_near_verified_score_change | 7-1 | The final whistle blows and the players begin their post-match rituals. Curacao's No. 8, Comenencia, is seen shaking hands with a German opponent before turning to acknowledge the crowd with a clap. The scene shows mutua |

## Sanitized Non-Goal Score Claims / 已清洗非进球数字比分片段

| Event | Time | Type | Reason |
| --- | --- | --- | --- |
| U023 | `00:11:00-00:11:56` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U062 | `00:29:00-00:29:00` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U115 | `00:51:40-00:53:04` | celebration_or_replay | non_goal_segment_should_not_repeat_numeric_score |
| U135 | `00:58:40-00:59:08` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U139 | `01:00:48-01:00:52` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U151 | `01:07:48-01:07:48` | save | non_goal_segment_should_not_repeat_numeric_score |
| U170 | `01:16:56-01:16:56` | period_transition | non_goal_segment_should_not_repeat_numeric_score |
| U174 | `01:17:40-01:17:40` | shot | non_goal_segment_should_not_repeat_numeric_score |
| U195 | `01:27:04-01:27:08` | substitution | non_goal_segment_should_not_repeat_numeric_score |
| U215 | `01:36:20-01:36:52` | substitution | non_goal_segment_should_not_repeat_numeric_score |
| U222 | `01:44:28-01:44:28` | period_transition | non_goal_segment_should_not_repeat_numeric_score |

## Other Safety Sanitizers / 其他安全清洗

- `forbidden_entity_sanitized`: 0
- `prematch_action_sanitized`: 1

## API Hook / API 接口

- `api_mode`: off
- `api_review_segments`: 0
EN: Use `--api-mode review --frame-root <frames>` to attach Intern-S2 visual reflection evidence to selected suspect segments.
ZH: 使用 `--api-mode review --frame-root <frames>` 可以让 Intern-S2 对选中的可疑片段追加视觉反思证据。
