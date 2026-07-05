# Commentary Quality Evaluation / 解说质量评测

EN: This report evaluates generated commentary quality. It is an evaluation artifact, not target-agent hidden context.

ZH: 本报告用于评估生成解说质量，是评测产物，不是目标 Agent 的隐藏上下文。

## Metrics / 指标

- `segment_count`: 257
- `event_type_counts`: {'period_transition': 23, 'other_relevant': 23, 'celebration_or_replay': 25, 'var_review': 3, 'dangerous_attack': 45, 'foul': 42, 'shot': 29, 'save': 19, 'goal': 21, 'substitution': 12, 'free_kick': 8, 'corner': 6, 'card': 1}
- `generated_goal_count`: 21
- `verified_goal_count`: 8
- `goal_overcount`: 13
- `score_claim_segments`: 37
- `wrong_entity_segments`: 9
- `style_color_identity_segments`: 44
- `prematch_action_segments`: 1
- `unsupported_name_segments`: 10
- `mixed_language_segments`: 5
- `replay_goal_risk_segments`: 10

## Quality Gate / 质量门禁

- `status`: fail
- `blockers`: wrong_entity_segments, goal_overcount, score_claim_segments
- `warnings`: style_color_identity_segments, mixed_language_segments, prematch_action_segments
- EN: Fail means the output should not be used as the final demo script without review.
- ZH: fail 表示该输出不应未经复核直接作为最终 demo 解说稿。

## Opening Context / 开场阶段

- `opening_segment_count`: 22
- `background_terms_found`: anthem, child, children, lineup, mascot, official, referee, 入场, 列队, 吉祥物, 国歌, 球童, 裁判
- `has_basic_opening_context`: True
- `needs_official_child_mascot_distinction`: False

## Human Review Notes / 人工补充观察

| Area | EN | ZH |
| --- | --- | --- |
| Opening background | Opening and entrance shots should introduce the match, teams, and visible ceremony context when evidence is available. | 入场和开场画面应在证据充分时适当介绍比赛、球队和可见仪式背景。 |
| Role distinction | Distinguish mascots, player escorts, referees, assistant referees, fourth officials, and VAR-room officials instead of collapsing them into one role. | 区分吉祥物、球童、主裁、边裁、第四官员和视频助理裁判，不能混成一个角色。 |
| Broadcast graphics as knowledge | Lineup, referee, shirt number, kit color, and goalkeeper color graphics can enrich background facts, but must remain uncertain when substitutions or unclear shots break the mapping. | 球员列表、裁判信息、号码、队服颜色和门将颜色可作为背景知识，但替补和模糊画面会破坏对应关系，必须保留不确定性。 |
| Phase awareness | Before kickoff, entrance, lineup, anthem, ceremony, and broadcast graphics are context phases, not fouls, restarts, or repeated kickoffs. | 开球前的入场、列队、国歌、仪式和转播图表属于背景阶段，不应识别为犯规、任意球或重复开球。 |
| Commentary conversion | Raw visual descriptions are not always playable commentary; color/position observations should be converted into natural broadcast wording. | 原始画面描述不一定能直接当解说词；颜色、位置等观察应转换为自然的解说表达。 |
| Fact verification | Names, teams, scores, referees, and event results must be organized as facts with evidence status instead of being asserted from weak visual guesses. | 姓名、球队、比分、裁判和事件结果应整理为带证据状态的事实，而不是从弱视觉猜测中直接断言。 |

## Issue Samples / 问题样例

### Wrong entity / 错误球队或实体

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

### Prematch action misclassification / 开球前动作误判

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U014 | var_review | `00:06:48-00:06:52` | The VAR team is now reviewing the incident. Referee Hamza El Fario and assistant Nicolas Gallo are closely examining the footage in the Hisense VAR room, with multiple screens disp |

### Color-based identity wording / 颜色式身份描述

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

### Replay-goal risk / 回放误判进球风险

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U042 | goal | `00:17:12-00:18:12` | And here it is — Germany doubles their lead! A crisp, clinical finish from inside the box as the ball nestles into the back of the net. The keeper dives but can’t reach it — pure c |
| U081 | goal | `00:30:48-00:32:44` | And there it is! The ball finds the back of the net from a tight angle inside the box. The German attacker has beaten the diving goalkeeper with a precise strike into the bottom co |
| U090 | goal | `00:34:52-00:36:16` | Germany takes a free kick near the penalty area. The ball is struck with precision, curling past the defensive wall and into the net. The German players celebrate as the goal is co |
| U158 | goal | `01:01:40-01:02:44` | Germany breaks through! Musiala, the number 10, receives the ball inside the penalty area, takes a touch to set himself, and fires a low shot that beats the diving goalkeeper. The  |
| U193 | goal | `01:18:08-01:18:52` | Germany scores! A fast break down the right flank sees Gnabry cut inside and strike a low shot that beats the goalkeeper and nestles into the bottom corner. The net ripples as the  |
| U202 | goal | `01:21:32-01:22:04` | Curaçao takes a free kick near the penalty area. The ball is played into the box, and a Curaçao player makes a run towards the goal. He receives the ball and takes a shot from insi |
| U225 | goal | `01:31:28-01:32:36` | Germany goes up 6-1! The ball finds the back of the net as the German players erupt in celebration. The crowd is on its feet, and the scoreboard confirms the goal. Nkunku and Kimmi |

### Unsupported named fact / 无依据人名

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U011 | other_relevant | `00:05:28-00:05:32` | And here comes the crowd reaction. A sea of blue and yellow, Colombian fans in their signature wide-brimmed hats, hands clasped in quiet tension. Then, a sharp cut to the other sid |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U042 | goal | `00:17:12-00:18:12` | And here it is — Germany doubles their lead! A crisp, clinical finish from inside the box as the ball nestles into the back of the net. The keeper dives but can’t reach it — pure c |
| U084 | foul | `00:33:00-00:33:00` | A sharp challenge from behind catches the German player off guard — he goes down under contact from the Colombian defender. The referee immediately blows for the foul, and play sto |
| U089 | foul | `00:34:36-00:34:40` | There's a foul here — the Colombian player catches the German attacker with a late leg, sending him tumbling to the ground. The referee will need to decide whether that was careles |
| U118 | dangerous_attack | `00:43:04-00:43:08` | Colombia’s #12 drives down the right flank, cutting inside as German defenders converge — a tight moment in the box, no shot taken yet, but the pressure is building. / 哥伦比亚12号沿右路高速 |
| U191 | shot | `01:17:40-01:17:40` | Colombia's number 11 takes a powerful shot from outside the box — the ball rockets toward goal as the German keeper braces for impact. A moment of tension, but will it find the net |
| U225 | goal | `01:31:28-01:32:36` | Germany goes up 6-1! The ball finds the back of the net as the German players erupt in celebration. The crowd is on its feet, and the scoreboard confirms the goal. Nkunku and Kimmi |

### Mixed-language Chinese / 中文夹杂英文

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U039 | shot | `00:15:52-00:15:52` | Inside the penalty area, the attacker rises and directs a header toward goal — the keeper is already in motion to react. That’s a genuine attempt from close range, forcing the defe |
| U088 | foul | `00:34:28-00:34:28` | A blue-shirted defender closes in on the attacker in white, and as the challenge comes in, the German player goes down cleanly under contact. The referee blows for a foul — a clear |
| U158 | goal | `01:01:40-01:02:44` | Germany breaks through! Musiala, the number 10, receives the ball inside the penalty area, takes a touch to set himself, and fires a low shot that beats the diving goalkeeper. The  |
| U183 | foul | `01:16:20-01:16:20` | Nmecha makes contact, the blue player goes down — a moment of physical challenge that halts play. The referee will need to assess whether it was fair or foul. / Nmecha 与对方球员发生身体接触， |
| U211 | celebration_or_replay | `01:26:24-01:26:36` | Germany extend their lead to 5-1, and the players are celebrating on the pitch. Tah and Raum are seen embracing, while Rüdiger runs back towards midfield. The crowd is in full swin |

### Score claim / 比分声明

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U033 | other_relevant | `00:12:04-00:12:08` | Julian Nagelsmann is on the touchline, visibly animated as he directs his team. He points upward with one hand, then brings it to his lips in a focused gesture — likely signaling f |
| U036 | goal | `00:14:08-00:15:28` | Germany takes the lead! A shot from inside the box finds the back of the net after a scramble in the penalty area. The goalkeeper dives but can't reach it as the ball rolls past hi |
| U054 | celebration_or_replay | `00:21:00-00:21:00` | And there it is — a moment of pure precision. The German striker connects cleanly on the volley, sending the ball past the keeper and into the net. The crowd erupts as the scoreboa |
| U061 | celebration_or_replay | `00:23:20-00:23:20` | Germany's Pavlović and his teammate react with visible frustration after a missed opportunity — hands on heads, bowed heads — as the scoreboard shows Germany leading 1-0 against Cu |
| U075 | celebration_or_replay | `00:29:00-00:29:00` | Havertz reacts with visible frustration, hands on his head — a clear sign of a missed opportunity or setback in the match. The camera lingers on his back, capturing the weight of t |
| U081 | goal | `00:30:48-00:32:44` | And there it is! The ball finds the back of the net from a tight angle inside the box. The German attacker has beaten the diving goalkeeper with a precise strike into the bottom co |
| U099 | celebration_or_replay | `00:37:00-00:37:00` | A close-up on the German player, number 16, shows a look of clear frustration. The scoreboard indicates the match is level at 1-1 against Curaçao, and this reaction follows a misse |
| U124 | goal | `00:45:16-00:46:36` | Germany takes a free kick just outside the penalty area. The ball is struck with precision, curling past the defensive wall and into the top corner of the net. The goalkeeper dives |

## Recommendations / 建设性建议

| Priority | Area | EN | ZH |
| --- | --- | --- | --- |
| Must | Output audit gate | Reject or manually review any final output with wrong teams, excessive goal count, or unverified score-changing claims. | 最终输出若出现错误球队、进球数明显过多、未经验证的比分变化，应拒绝或转人工复核。 |
| Must | Goal score-state verifier | A goal claim must be supported by live scoring evidence plus a previous/post scoreboard state, or remain pending/uncertain. | 进球宣称必须有现场进球证据和前后比分牌状态支撑，否则保持 pending/uncertain。 |
| Must | Wrong-entity guard | Hard-block team names outside Germany and Curacao for this match unless they appear in explicit broadcast metadata. | 本场应硬性禁止德国、库拉索以外的球队名，除非它们出现在明确转播元数据中。 |
| Should | Identity wording | Use team, role, jersey number, or verified name; avoid default color-shirt subjects. | 优先使用球队、角色、号码或已验证姓名，不要默认用球衣颜色当主语。 |
| Should | Opening phase classifier | Before kickoff, classify entrance, lineup, anthem, officials, mascots/children, and broadcast graphics as context, not fouls or restarts. | 开球前应识别入场、列队、国歌、裁判、球童/吉祥物和转播图表为背景，不应误判为犯规或重复开球。 |
| Could | Final Chinese polish | Run a lightweight Chinese linter to remove mixed English fragments and template-like wording. | 增加轻量中文润色检查，去除英文残留和模板化表达。 |
| Could | Fact registry | Store extracted facts with source, confidence, validity window, and evidence frame IDs so later commentary can cite or avoid them. | 将抽取事实按来源、置信度、有效时间段和证据帧记录，便于后续解说引用或规避。 |
