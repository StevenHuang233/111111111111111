# Identity And Style Audit / 身份措辞与解说风格审计

EN: This report checks whether generated commentary uses supported identities and natural broadcast wording.

ZH: 本报告检查生成解说是否使用有依据的身份表达，以及是否接近自然人类解说。

## Summary / 摘要

- `segment_count`: 257
- `color_identity_segments`: 43
- `team_identity_segments`: 176
- `number_identity_segments`: 47
- `role_identity_segments`: 178
- `raw_visual_segments`: 44
- `wrong_entity_segments`: 9
- `unsupported_name_segments`: 13
- `color_identity_ratio`: 0.1673
- `raw_visual_ratio`: 0.1712

## Style Gate / 风格门禁

- `status`: fail
- `blockers`: wrong_entity_segments, unsupported_name_segments
- `warnings`: color_identity_segments, raw_visual_segments
- EN: Fail means the script contains unsupported identity facts. Warnings mean the style still sounds like raw visual description.
- ZH: fail 表示解说稿包含无依据身份事实；warning 表示文本仍偏向原始画面描述。

## Recommended Identity Distribution / 建议身份表达分布

| Identity Form | Target Share | EN Condition | ZH Condition |
| --- | --- | --- | --- |
| verified_name | 35-50% | Use only when roster/OCR/broadcast graphic or prior verified fact supports it. | 仅在名单、OCR、转播图表或已验证事实支持时使用。 |
| team_plus_role_or_number | 30-45% | Use when team and role/jersey number are visible but the name is not secure. | 球队与角色/号码可见但姓名不稳时使用。 |
| team_only | 15-25% | Use for flowing play when exact identity is not important. | 普通推进或身份不关键时使用球队主语。 |
| color_as_evidence | <5% | Use color only as evidence, contrast, or occasional rhetoric, not as the default subject. | 颜色只作证据、对比或少量修辞，不能作为默认主语。 |

## Repeated Starters / 重复开头

| Starter | Count | Example |
| --- | ---: | --- |
| And there it is | 10 | U029 |
| And here comes the | 7 | U011 |
| A shot from inside | 6 | U032 |
| Germany builds a dangerous | 6 | U034 |
| Inside the penalty area | 4 | U039 |
| A player in white | 4 | U052 |
| Germany takes a free | 4 | U090 |
| A close-up on the | 3 | U005 |
| Germany in the final | 3 | U030 |
| A German player in | 3 | U046 |
| A foul is called | 3 | U055 |
| Germany awarded a free | 3 | U056 |

## Wrong Entity / 错误实体

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U011 | other_relevant | `00:05:28-00:05:32` | And here comes the crowd reaction. A sea of blue and yellow, Colombian fans in their signature wide-brimmed hats, hands clasped in quiet tension. Then, a sharp cut to the other sid |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U084 | foul | `00:33:00-00:33:00` | A sharp challenge from behind catches the German player off guard — he goes down under contact from the Colombian defender. The referee immediately blows for the foul, and play sto |
| U089 | foul | `00:34:36-00:34:40` | There's a foul here — the Colombian player catches the German attacker with a late leg, sending him tumbling to the ground. The referee will need to decide whether that was careles |
| U118 | dangerous_attack | `00:43:04-00:43:08` | Colombia’s #12 drives down the right flank, cutting inside as German defenders converge — a tight moment in the box, no shot taken yet, but the pressure is building. / 哥伦比亚12号沿右路高速 |
| U191 | shot | `01:17:40-01:17:40` | Colombia's number 11 takes a powerful shot from outside the box — the ball rockets toward goal as the German keeper braces for impact. A moment of tension, but will it find the net |
| U248 | goal | `01:46:32-01:47:44` | In stoppage time, Colombia’s number 10 breaks away with pace, chased by a German defender. He drives forward, enters the penalty area, and fires a shot. The ball finds the back of  |
| U249 | foul | `01:46:36-01:46:36` | And there's the whistle! The German defender #22 makes contact with the Colombian attacker #10 near the sideline, causing a loss of balance. The assistant referee immediately raise |
| U252 | goal | `01:48:12-01:49:32` | In stoppage time, Germany takes a free kick from just outside the penalty area. The ball is struck with precision, curling over the defensive wall and into the top corner of the ne |

## Unsupported Name / 无依据姓名

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U011 | other_relevant | `00:05:28-00:05:32` | And here comes the crowd reaction. A sea of blue and yellow, Colombian fans in their signature wide-brimmed hats, hands clasped in quiet tension. Then, a sharp cut to the other sid |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U042 | goal | `00:17:12-00:18:12` | And here it is — Germany doubles their lead! A crisp, clinical finish from inside the box as the ball nestles into the back of the net. The keeper dives but can’t reach it — pure c |
| U084 | foul | `00:33:00-00:33:00` | A sharp challenge from behind catches the German player off guard — he goes down under contact from the Colombian defender. The referee immediately blows for the foul, and play sto |
| U089 | foul | `00:34:36-00:34:40` | There's a foul here — the Colombian player catches the German attacker with a late leg, sending him tumbling to the ground. The referee will need to decide whether that was careles |
| U118 | dangerous_attack | `00:43:04-00:43:08` | Colombia’s #12 drives down the right flank, cutting inside as German defenders converge — a tight moment in the box, no shot taken yet, but the pressure is building. / 哥伦比亚12号沿右路高速 |
| U130 | celebration_or_replay | `00:48:48-00:49:08` | Germany takes the lead! Späne finds the back of the net with a powerful strike, sending the home crowd into a frenzy. The replay shows his precise placement past the diving keeper, |
| U191 | shot | `01:17:40-01:17:40` | Colombia's number 11 takes a powerful shot from outside the box — the ball rockets toward goal as the German keeper braces for impact. A moment of tension, but will it find the net |
| U193 | goal | `01:18:08-01:18:52` | Germany scores! A fast break down the right flank sees Gnabry cut inside and strike a low shot that beats the goalkeeper and nestles into the bottom corner. The net ripples as the  |
| U225 | goal | `01:31:28-01:32:36` | Germany goes up 6-1! The ball finds the back of the net as the German players erupt in celebration. The crowd is on its feet, and the scoreboard confirms the goal. Nkunku and Kimmi |
| U244 | goal | `01:42:08-01:43:24` | And here comes the goal for Germany! Havetz with a sharp finish from inside the box, the ball finds the back of the net as the keeper is beaten. The crowd erupts — 7-1 now! Havertz |
| U248 | goal | `01:46:32-01:47:44` | In stoppage time, Colombia’s number 10 breaks away with pace, chased by a German defender. He drives forward, enters the penalty area, and fires a shot. The ball finds the back of  |
| U249 | foul | `01:46:36-01:46:36` | And there's the whistle! The German defender #22 makes contact with the Colombian attacker #10 near the sideline, causing a loss of balance. The assistant referee immediately raise |

## Color Identity Fallback / 颜色身份 fallback

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U017 | period_transition | `00:08:08-00:08:12` | The German national team gathers in a tight huddle on the pitch, signaling a period transition—either before kickoff or after halftime. Players in white jerseys with visible number |
| U023 | dangerous_attack | `00:09:28-00:09:28` | A white-shirted attacker drives into the penalty area, surrounded by blue-shirted defenders. The ball is played forward as pressure mounts near the goal line. / 白衣进攻球员突入禁区，被蓝衣防守队员包 |
| U030 | dangerous_attack | `00:11:48-00:11:48` | Germany in the final third, a white-jerseyed attacker drives forward with pace as defenders converge — this is where danger brews. The cross or shot is imminent, and the box is cro |
| U034 | dangerous_attack | `00:12:28-00:12:32` | Germany builds a dangerous attack in the final third. A German player in white drives forward with the ball, drawing defenders as teammates converge near the penalty area. The ball |
| U045 | dangerous_attack | `00:18:52-00:18:52` | A dangerous attack unfolds as the player in blue drives into the penalty area, drawing defenders in tight. The pressure builds as he attempts to create space, but the defense holds |
| U046 | foul | `00:19:04-00:19:04` | A German player in white goes down under the challenge from a Curaçao defender in blue. The referee is on the spot to assess whether contact was made. / 一名身穿白色球衣的德国球员在蓝衣库拉索防守球员的铲抢下 |
| U051 | dangerous_attack | `00:20:40-00:20:40` | White builds through the middle, and a runner in white finds space near the edge of the box. The attacker drives forward with the ball, pressing into the final third as a defender  |
| U052 | shot | `00:20:44-00:20:44` | A player in white takes a shot from inside the penalty area. The ball is struck towards the goal, and the goalkeeper is positioned to react, but the outcome is not yet determined.  |
| U053 | dangerous_attack | `00:20:48-00:20:48` | A white-jerseyed attacker breaks into the penalty area, but the goalkeeper is already down — defenders scramble to close out the chance. The ball’s gone, and the attack fizzles bef |
| U055 | foul | `00:21:12-00:21:24` | A foul is called near the center circle as a player in white goes down after contact with Locadia #9. The referee immediately intervenes, speaking to Locadia and gesturing for a fr |
| U058 | foul | `00:23:04-00:23:04` | Wintz in white makes a challenge with his arm out, making contact with the opponent as they go for the ball. The referee will likely blow for a foul there. / 身穿白色球衣的温茨在拼抢中伸臂拦截，与对手同 |
| U068 | dangerous_attack | `00:27:04-00:27:04` | Curaçao's attacker in blue drives forward into the penalty area, closely tracked by two German defenders. The pressure is high as he approaches the goal line with the ball, but the |
| U073 | dangerous_attack | `00:28:48-00:28:48` | Germany in the final third, a dangerous attack developing with pace. The player in white drives forward, supported by runners into the box. Pressure is building as they look to unl |
| U078 | shot | `00:29:48-00:29:48` | A blue-shirted attacker takes a shot from inside the penalty area, but the goalkeeper dives to make a save. / 一名身穿蓝色球衣的进攻球员在禁区附近起脚射门，但门将迅速倒地成功将球扑出。 |
| U088 | foul | `00:34:28-00:34:28` | A blue-shirted defender closes in on the attacker in white, and as the challenge comes in, the German player goes down cleanly under contact. The referee blows for a foul — a clear |
| U092 | foul | `00:36:24-00:36:24` | And there it is — a clean, sharp challenge from the Curacao defender in blue, catching the German attacker off balance just outside the box. The German player goes down cleanly und |
| U106 | corner | `00:38:24-00:38:28` | Corner kick for the team in white. The ball is placed at the corner flag as players from both teams position themselves in the penalty area. The referee oversees the setup, ensurin |
| U107 | shot | `00:38:32-00:38:32` | A player in blue takes a shot towards the goal, with the ball traveling towards the goal and the goalkeeper reacting to the shot. / 一名身穿蓝色球衣的球员起脚射门，皮球直飞球门，门将迅速做出反应。 |
| U109 | shot | `00:40:12-00:40:12` | Germany's player in white takes a shot from inside the penalty box, ball heading toward goal as goalkeeper prepares to react. / 德国队白衣球员在禁区起脚射门，皮球直逼球门，门将已做好扑救准备。 |
| U112 | shot | `00:41:28-00:41:28` | Inside the penalty area, the player in white takes a shot. The ball is in flight towards the goal, and the goalkeeper is reacting to the strike. / 禁区之内，白衣球员起脚射门。皮球飞向球门，门将正在做出反应。 |

## Raw Visual Wording / 原始画面式措辞

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U005 | other_relevant | `00:03:52-00:03:52` | A close-up on the jacket reveals the crest of the Federashon Futbol Kòrsou, marking the presence of the Curaçao national team in this broadcast segment. / 镜头特写这件夹克，上面印有库拉索足球联合会的队徽， |
| U007 | celebration_or_replay | `00:04:24-00:04:24` | The camera finds a group of fans in the stands, their faces alight with emotion as they stand for the national anthem. One woman places her hand over her heart, eyes closed in reve |
| U010 | period_transition | `00:04:48-00:05:24` | The players are lining up for the pre-match handshake ceremony, a moment of sportsmanship before the kickoff. Mascots and young ball boys accompany the teams as they walk onto the  |
| U011 | other_relevant | `00:05:28-00:05:32` | And here comes the crowd reaction. A sea of blue and yellow, Colombian fans in their signature wide-brimmed hats, hands clasped in quiet tension. Then, a sharp cut to the other sid |
| U013 | other_relevant | `00:06:28-00:06:44` | The match officials are introduced on screen with their names and nationalities displayed. Referees are shown in a huddle, likely discussing match protocols before kickoff. Close-u |
| U016 | other_relevant | `00:07:04-00:08:00` | The broadcast is now presenting the pre-match team lineups for both sides. Germany, under head coach Julian Nagelsmann, are set up in a 4-2-3-1 formation, with Jonathan Tah wearing |
| U017 | period_transition | `00:08:08-00:08:12` | The German national team gathers in a tight huddle on the pitch, signaling a period transition—either before kickoff or after halftime. Players in white jerseys with visible number |
| U021 | other_relevant | `00:08:48-00:08:52` | A moment of heavy emotion for Germany as Kimmich sinks to his knees, head bowed in clear frustration or exhaustion. The weight of the game is visible on his shoulders. Across the p |
| U028 | foul | `00:11:12-00:11:16` | A German player makes contact with a Curaçao player, causing the Curaçao player to fall to the ground. This is visible as a foul situation. / 一名德国球员与库拉索球员发生接触，导致库拉索球员倒地。这明显是一次犯规情况。 |
| U029 | foul | `00:11:28-00:11:28` | And there it is — a clear trip from behind by Germany’s No. 5 as the Curaçao attacker dives forward in pursuit of the ball. The contact is visible, the fall is abrupt, and the refe |
| U033 | other_relevant | `00:12:04-00:12:08` | Julian Nagelsmann is on the touchline, visibly animated as he directs his team. He points upward with one hand, then brings it to his lips in a focused gesture — likely signaling f |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U042 | goal | `00:17:12-00:18:12` | And here it is — Germany doubles their lead! A crisp, clinical finish from inside the box as the ball nestles into the back of the net. The keeper dives but can’t reach it — pure c |
| U061 | celebration_or_replay | `00:23:20-00:23:20` | Germany's Pavlović and his teammate react with visible frustration after a missed opportunity — hands on heads, bowed heads — as the scoreboard shows Germany leading 1-0 against Cu |
| U066 | other_relevant | `00:25:04-00:25:04` | A close-up on Curaçao's Locden, number 6, standing near the sideline. The camera focuses on him as he looks towards the pitch, possibly awaiting instructions or preparing for a sub |
| U075 | celebration_or_replay | `00:29:00-00:29:00` | Havertz reacts with visible frustration, hands on his head — a clear sign of a missed opportunity or setback in the match. The camera lingers on his back, capturing the weight of t |
| U076 | other_relevant | `00:29:04-00:29:08` | Manuel Neuer stands alert in goal, the broadcast noting his status as Germany’s oldest ever player at 40 years and 79 days — a quiet moment of legacy amid the match’s rhythm. / 门前的 |
| U090 | goal | `00:34:52-00:36:16` | Germany takes a free kick near the penalty area. The ball is struck with precision, curling past the defensive wall and into the net. The German players celebrate as the goal is co |
| U099 | celebration_or_replay | `00:37:00-00:37:00` | A close-up on the German player, number 16, shows a look of clear frustration. The scoreboard indicates the match is level at 1-1 against Curaçao, and this reaction follows a misse |
| U102 | celebration_or_replay | `00:37:48-00:37:48` | A close-up on the German player, Pavlovic, as he reacts to the play. The match remains tied at 1-1. / 镜头特写德国球员帕夫洛维奇，他正对刚才的攻防做出反应。目前比赛仍维持在1-1平局。 |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Block unsupported names and wrong teams before final packaging. | 最终打包前必须拦截无依据姓名和错误球队。 |
| Should | Add an identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric. | 增加身份选择级联：已验证姓名 -> 球队+号码/角色 -> 仅球队 -> 少量颜色修辞。 |
| Should | Use a style sampler so wording varies naturally inside the same broadcast style instead of repeating one template. | 使用风格采样器，让同一解说风格内部自然变化，而不是重复同一模板。 |
