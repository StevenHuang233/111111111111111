# Commentary Quality Evaluation / 解说质量评测

EN: This report evaluates generated commentary quality. It is an evaluation artifact, not target-agent hidden context.

ZH: 本报告用于评估生成解说质量，是评测产物，不是目标 Agent 的隐藏上下文。

## Metrics / 指标

- `segment_count`: 235
- `event_type_counts`: {'period_transition': 26, 'celebration_or_replay': 23, 'other_relevant': 8, 'var_show': 1, 'dangerous_attack': 43, 'foul': 50, 'goal': 28, 'substitution': 8, 'shot': 22, 'save': 11, 'free_kick': 8, 'corner': 4, 'var_review': 2, 'penalty': 1}
- `generated_goal_count`: 28
- `verified_goal_count`: 8
- `goal_overcount`: 20
- `score_claim_segments`: 39
- `wrong_entity_segments`: 1
- `style_color_identity_segments`: 9
- `prematch_action_segments`: 0
- `unsupported_name_segments`: 2
- `mixed_language_segments`: 3
- `replay_goal_risk_segments`: 14

## Quality Gate / 质量门禁

- `status`: fail
- `blockers`: wrong_entity_segments, goal_overcount, score_claim_segments
- `warnings`: mixed_language_segments
- EN: Fail means the output should not be used as the final demo script without review.
- ZH: fail 表示该输出不应未经复核直接作为最终 demo 解说稿。

## Opening Context / 开场阶段

- `opening_segment_count`: 19
- `background_terms_found`: anthem, mascot, official, referee, 入场, 列队, 吉祥物, 国歌, 裁判
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
| U017 | var_show | `00:06:40-00:06:52` | We're taken to the VAR room for a broadcast segment showcasing the Video Assistant Referee team. The FIFA VAR Room graphic appears, identifying VAR Referee Hamza El Fario from Moro |

### Prematch action misclassification / 开球前动作误判

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| - | - | - | - |

### Color-based identity wording / 颜色式身份描述

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U001 | period_transition | `00:00:04-00:01:04` | The referees lead the way onto the pitch, followed by the teams in their pre-match warm-up gear. Germany's players, identifiable by their white jackets and black shorts, walk along |
| U003 | period_transition | `00:01:16-00:01:32` | The stage is set for the 2026 World Cup as Germany and Curacao line up for the pre-match ceremony. Players from both teams form a circle around the center pitch, flags waving under |
| U018 | celebration_or_replay | `00:08:08-00:08:24` | Germany players in white kits huddle together in celebration on the pitch, with German flags visible in the background crowd. Close-up of Germany players continuing their team hudd |
| U024 | foul | `00:11:12-00:11:16` | A German player in white shirt makes contact with a Curacao player in blue/yellow shirt, causing the Curacao player to fall. The ball is loose nearby, indicating a stoppage likely  |
| U138 | period_transition | `01:00:12-01:00:36` | The second half gets underway at the Astrodome in Houston. Germany kick off, with their players in white shirts and black shorts taking control of the center circle. Curacao, in th |
| U155 | goal | `01:09:12-01:10:04` | Germany in white shirts is attacking in the final third with multiple players entering the penalty area, creating a promising chance against Curacao's defense. A German player take |
| U160 | celebration_or_replay | `01:12:24-01:12:32` | Germany's No. 10, Jamal Musiala, finds the back of the net once more — his 10th goal for the national team. The scoreboard confirms Germany leads 4-1 as Musiala catches his breath, |
| U170 | period_transition | `01:16:56-01:16:56` | Germany leads 4-1 as the teams regroup for a set-piece at 61:18. Players from both sides position themselves near the penalty area, with Germany in white and Curacao in blue/yellow |

### Replay-goal risk / 回放误判进球风险

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U023 | goal | `00:11:00-00:11:56` | Germany takes an early lead! The buildup starts with Germany's No. 5 driving forward, beating a diving Curacao defender. He enters the penalty area and fires a shot that finds the  |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha, wearing number 23, finds the back of the net with a powerful shot from inside the penalty area. The German fans erupt in celebration as the sco |
| U047 | goal | `00:20:36-00:21:32` | Germany takes an early lead! At 11:53, Germany's No. 23 receives the ball just outside the penalty area, drives forward past a Curacao defender, and fires a low shot that beats the |
| U049 | goal | `00:22:52-00:23:44` | Germany takes the lead! Wirtz (No. 17) finds the back of the net with a precise strike, beating the diving goalkeeper. The scoreboard updates to 1-0 as he collects the ball in cele |
| U077 | goal | `00:34:52-00:36:12` | Germany's No. 17, Wirtz, takes the free kick near the penalty area. The ball is delivered into the box, and a German player rises to meet it with a powerful header. The ball flies  |
| U149 | goal | `01:06:04-01:06:44` | Germany's No. 10, Jamal Musiala, finds space inside the box and fires a low shot from close range. The ball beats the diving Curacao goalkeeper and nestles into the bottom corner!  |
| U155 | goal | `01:09:12-01:10:04` | Germany in white shirts is attacking in the final third with multiple players entering the penalty area, creating a promising chance against Curacao's defense. A German player take |
| U176 | goal | `01:18:08-01:18:40` | Germany's No. 19, Sane, drives into the penalty area with pace and composure, beating the offside trap. He takes a touch to set himself, then fires a low shot across the keeper. Th |

### Unsupported named fact / 无依据人名

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U017 | var_show | `00:06:40-00:06:52` | We're taken to the VAR room for a broadcast segment showcasing the Video Assistant Referee team. The FIFA VAR Room graphic appears, identifying VAR Referee Hamza El Fario from Moro |
| U032 | celebration_or_replay | `00:17:16-00:17:16` | Germany's No. 10, Müller, walks away from the play as the crowd reacts — a moment of quiet aftermath following the earlier goal. The scoreboard confirms Germany leads 1-0, and this |

### Mixed-language Chinese / 中文夹杂英文

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U071 | period_transition | `00:31:52-00:32:44` | Germany and Curacao are at a hydration break during the first half of their World Cup 2026 match. The scoreboard shows a 1-1 tie as players from both teams regroup near the sidelin |
| U085 | goal | `00:37:24-00:38:36` | Germany takes the lead! Germany's No. 17 dribbles forward, evades a Curacao defender, and delivers a precise cross into the penalty area. A German attacker meets it with a powerful |
| U193 | celebration_or_replay | `01:26:24-01:26:36` | Germany extend their lead! The scoreboard reads 5-1 as the German players erupt in celebration. Tah (No. 4) is seen embracing teammates and staff, while Rügger (No. 7) pumps his fi |

### Score claim / 比分声明

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha, wearing number 23, finds the back of the net with a powerful shot from inside the penalty area. The German fans erupt in celebration as the sco |
| U030 | goal | `00:15:44-00:15:56` | And there it is! Germany takes an early lead in this World Cup clash. Nmecha finds space inside the box, collects a pass, and fires a low shot that beats the diving Curacao goalkee |
| U032 | celebration_or_replay | `00:17:16-00:17:16` | Germany's No. 10, Müller, walks away from the play as the crowd reacts — a moment of quiet aftermath following the earlier goal. The scoreboard confirms Germany leads 1-0, and this |
| U049 | goal | `00:22:52-00:23:44` | Germany takes the lead! Wirtz (No. 17) finds the back of the net with a precise strike, beating the diving goalkeeper. The scoreboard updates to 1-0 as he collects the ball in cele |
| U062 | celebration_or_replay | `00:29:00-00:29:00` | Germany's No. 8, Havertz, reacts with visible frustration after a missed opportunity — hand on head, turning away from play. The scoreboard shows Germany leading 1-0 at 19:53, but  |
| U068 | goal | `00:30:32-00:31:20` | Curacao strike first! The blue-and-yellow kit players are celebrating wildly as the ball finds the net. A Curacao attacker, wearing number 8, takes a powerful shot from inside the  |
| U071 | period_transition | `00:31:52-00:32:44` | Germany and Curacao are at a hydration break during the first half of their World Cup 2026 match. The scoreboard shows a 1-1 tie as players from both teams regroup near the sidelin |
| U074 | period_transition | `00:33:20-00:33:24` | The teams are resetting on the pitch after the goal, with the scoreboard showing a 1-1 tie. Players from both Germany and Curacao are positioning themselves for the restart as the  |

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
