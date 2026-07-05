# Commentary Quality Evaluation / 解说质量评测

EN: This report evaluates generated commentary quality. It is an evaluation artifact, not target-agent hidden context.

ZH: 本报告用于评估生成解说质量，是评测产物，不是目标 Agent 的隐藏上下文。

## Metrics / 指标

- `segment_count`: 235
- `event_type_counts`: {'period_transition': 21, 'celebration_or_replay': 35, 'other_relevant': 8, 'var_show': 1, 'dangerous_attack': 46, 'foul': 50, 'goal': 8, 'substitution': 8, 'shot': 34, 'save': 11, 'free_kick': 7, 'corner': 4, 'var_review': 2}
- `generated_goal_count`: 8
- `verified_goal_count`: 8
- `goal_overcount`: 0
- `score_claim_segments`: 5
- `wrong_entity_segments`: 0
- `style_color_identity_segments`: 6
- `prematch_action_segments`: 0
- `unsupported_name_segments`: 0
- `mixed_language_segments`: 2
- `replay_goal_risk_segments`: 5

## Quality Gate / 质量门禁

- `status`: pass_with_warnings
- `blockers`: -
- `warnings`: mixed_language_segments
- EN: Fail means the output should not be used as the final demo script without review.
- ZH: fail 表示该输出不应未经复核直接作为最终 demo 解说稿。

## Opening Context / 开场阶段

- `opening_segment_count`: 19
- `background_terms_found`: anthem, mascot, official, referee, 入场, 列队, 吉祥物, 国歌, 球童, 裁判
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
| - | - | - | - |

### Prematch action misclassification / 开球前动作误判

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| - | - | - | - |

### Color-based identity wording / 颜色式身份描述

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U001 | period_transition | `00:00:04-00:01:04` | The pre-match ceremony is underway at the FIFA World Cup 2026, as Germany and Curacao make their grand entrance onto the pitch. Referees in bright yellow kits lead the procession,  |
| U013 | other_relevant | `00:05:28-00:05:32` | The atmosphere in the stadium is electric, with fans from both teams showing their support. Curacao fans, donning blue jerseys and cowboy hats, watch intently, while German fans, s |
| U018 | celebration_or_replay | `00:08:08-00:08:24` | Germany players in white kits gather in a tight huddle, celebrating with visible emotion and unity — Sané (No. 19) among them, arms locked as teammates close in. The crowd behind t |
| U038 | dangerous_attack | `00:18:36-00:18:36` | Germany pushes forward with pace, a white-shirted attacker surges into the final third, drawing defenders and creating space. The buildup is sharp, the movement fluid — Curacao’s b |
| U138 | period_transition | `01:00:12-01:00:36` | The second half is underway. Germany and Curacao line up at the center circle for the kickoff after halftime. The referee signals as players settle into position — Germany in white |
| U208 | goal | `01:31:12-01:32:36` | Germany in possession near Curacao's penalty area with multiple attackers advancing into the final third; German player dribbling toward Curacao box, drawing defenders; attacking b |

### Replay-goal risk / 回放误判进球风险

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha (No. 23) finds the back of the net with a powerful strike from inside the box, beating the Curacao goalkeeper. The German fans erupt in celebrat |
| U102 | goal | `00:45:16-00:46:36` | Germany takes a free kick near the edge of the penalty area. The ball is struck with precision, flying past the defensive wall and into the net. The net ripples as the ball crosses |
| U134 | goal | `00:57:00-00:58:20` | Germany's No. 7, Havertz, steps up to take the penalty kick. He approaches the ball with composure, the Curacao goalkeeper ready in goal. Havertz strikes it cleanly — the ball find |
| U208 | goal | `01:31:12-01:32:36` | Germany in possession near Curacao's penalty area with multiple attackers advancing into the final third; German player dribbling toward Curacao box, drawing defenders; attacking b |
| U220 | goal | `01:42:00-01:43:24` | Germany's No. 7 drives forward into the Curacao penalty area, drawing a defender before unleashing a low shot from close range. The ball beats the diving Curacao goalkeeper and nes |

### Unsupported named fact / 无依据人名

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| - | - | - | - |

### Mixed-language Chinese / 中文夹杂英文

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U134 | goal | `00:57:00-00:58:20` | Germany's No. 7, Havertz, steps up to take the penalty kick. He approaches the ball with composure, the Curacao goalkeeper ready in goal. Havertz strikes it cleanly — the ball find |
| U189 | period_transition | `01:24:44-01:25:08` | Germany and Curacao take a hydration break as the match pauses. Players head to the sidelines for refreshments while the crowd waits. The 'HYDRATION BREAK' graphic confirms the sto |

### Score claim / 比分声明

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha (No. 23) finds the back of the net with a powerful strike from inside the box, beating the Curacao goalkeeper. The German fans erupt in celebrat |
| U068 | goal | `00:30:32-00:31:20` | Curacao strike first! The blue and yellow team breaks through Germany's defense with a precise shot from inside the penalty area. The ball finds the bottom corner of the net as the |
| U143 | goal | `01:01:48-01:02:00` | Germany scores! Musiala finds the back of the net and the stadium erupts. The No. 10 sprints forward, arms outstretched, as Nmecha rushes to embrace him. Schlotterbeck, Kimmich, an |
| U208 | goal | `01:31:12-01:32:36` | Germany in possession near Curacao's penalty area with multiple attackers advancing into the final third; German player dribbling toward Curacao box, drawing defenders; attacking b |
| U220 | goal | `01:42:00-01:43:24` | Germany's No. 7 drives forward into the Curacao penalty area, drawing a defender before unleashing a low shot from close range. The ball beats the diving Curacao goalkeeper and nes |

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
