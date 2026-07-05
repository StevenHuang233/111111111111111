# Identity And Style Audit / 身份措辞与解说风格审计

EN: This report checks whether generated commentary uses supported identities and natural broadcast wording.

ZH: 本报告检查生成解说是否使用有依据的身份表达，以及是否接近自然人类解说。

## Summary / 摘要

- `segment_count`: 235
- `color_identity_segments`: 2
- `team_identity_segments`: 215
- `number_identity_segments`: 99
- `role_identity_segments`: 186
- `raw_visual_segments`: 43
- `wrong_entity_segments`: 0
- `unsupported_name_segments`: 0
- `color_identity_ratio`: 0.0085
- `raw_visual_ratio`: 0.183

## Style Gate / 风格门禁

- `status`: pass_with_warnings
- `blockers`: -
- `warnings`: raw_visual_segments
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
| The broadcast brings us | 21 | U030 |
| Germany find a pocket | 16 | U034 |
| Germany keep the pressure | 13 | U040 |
| Germany's No. 10 drives | 12 | U020 |
| A Curacao player goes | 7 | U055 |
| Germany make a change | 5 | U029 |
| Germany's No. 19 drives | 4 | U044 |
| Germany builds a dangerous | 4 | U057 |
| Germany's No. 19 takes | 4 | U061 |
| The game moves through | 4 | U135 |
| The broadcast shows reaction | 3 | U023 |
| A German player goes | 3 | U088 |

## Wrong Entity / 错误实体

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| - | - | - | - |

## Unsupported Name / 无依据姓名

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| - | - | - | - |

## Color Identity Fallback / 颜色身份 fallback

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U201 | dangerous_attack | `01:28:56-01:29:00` | Curacao counter-attack! The blue-shirted player breaks through Germany's midfield, driving forward with pace. He enters the final third, drawing defenders, and delivers a dangerous |
| U227 | foul | `01:46:48-01:46:48` | Late in stoppage time, a German player in white makes contact with a Curacao player in blue and yellow, sending him to the ground. The referee is watching closely to determine if i |

## Raw Visual Wording / 原始画面式措辞

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U004 | period_transition | `00:01:40-00:02:24` | The pre-match ceremony unfolds in grand fashion as Germany and Curacao take their places on the pitch. Players from both teams, clad in their respective warm-up gear, walk onto the |
| U005 | period_transition | `00:02:40-00:02:52` | The stage is set for the 2026 World Cup clash between Germany and Curacao. Both teams line up on the pitch as the national flags are unfurled across the field, creating a powerful  |
| U008 | period_transition | `00:04:28-00:04:28` | A sweeping view of the stadium as Germany and Curacao line up for the pre-match ceremony. The pitch is adorned with massive national flags — Germany’s black-red-gold on the left, C |
| U009 | celebration_or_replay | `00:04:32-00:04:32` | A close-up on a Curacao player, eyes closed and mouth open in what appears to be a moment of deep concentration or emotion during the national anthem. The intensity is palpable as  |
| U013 | other_relevant | `00:05:28-00:05:32` | The atmosphere in the stadium is electric as we see Curacao fans in their vibrant blue and yellow jerseys, some wearing distinctive blue cowboy hats, watching the match with intens |
| U017 | var_show | `00:06:40-00:06:52` | We're being taken to the VAR room as the officials review a potential incident. The FIFA VAR ROOM graphic is on screen, showing VAR referee Hamza El Fario, Assistant VAR Nicolas Ga |
| U018 | period_transition | `00:08:08-00:08:24` | Before kickoff, the camera stays with the players as they gather, settle their shape, and prepare for the opening whistle. / 开球前，镜头继续跟随球员集结和调整站位，双方都在等待开场哨响。 |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha (No. 23) finds space in the box and fires a shot that beats the Curacao goalkeeper. The ball nestles into the back of the net, and the scoreboar |
| U030 | celebration_or_replay | `00:15:44-00:15:56` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U032 | celebration_or_replay | `00:17:16-00:17:16` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U047 | celebration_or_replay | `00:20:36-00:21:32` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U049 | celebration_or_replay | `00:22:52-00:23:44` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U058 | shot | `00:27:56-00:27:56` | Germany's No. 14 takes a shot from inside the penalty area. The ball is struck towards the goal, but the frame does not confirm if it results in a goal or a save. / 德国队14号在禁区前沿起脚射门 |
| U063 | other_relevant | `00:29:08-00:29:08` | Germany's No. 1, Manuel Neuer, stands on the pitch as a broadcast graphic notes he is Germany's oldest ever player at 40 years and 79 days. / 德国队门将，1号诺伊尔，正站在场上。转播画面显示，他已成为德国队历史上最年长 |
| U071 | period_transition | `00:31:52-00:32:44` | A hydration break has been called as the match clock reads 22:41. The players are dispersing from the pitch and heading towards the sidelines. Germany's squad is seen huddled toget |
| U077 | celebration_or_replay | `00:34:52-00:36:12` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U085 | celebration_or_replay | `00:37:24-00:38:36` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U096 | celebration_or_replay | `00:41:48-00:41:52` | A dramatic moment unfolds as Curacao's No. 7 takes a shot, but Germany's goalkeeper leaps high to make a stunning save, denying the opportunity. The German players react with visib |
| U102 | goal | `00:45:16-00:46:36` | Germany takes a free kick just outside the penalty area. The ball is struck with precision, curling past the defensive wall and into the top corner of the net! The net ripples as t |
| U110 | celebration_or_replay | `00:48:48-00:49:08` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Block unsupported names and wrong teams before final packaging. | 最终打包前必须拦截无依据姓名和错误球队。 |
| Should | Add an identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric. | 增加身份选择级联：已验证姓名 -> 球队+号码/角色 -> 仅球队 -> 少量颜色修辞。 |
| Should | Use a style sampler so wording varies naturally inside the same broadcast style instead of repeating one template. | 使用风格采样器，让同一解说风格内部自然变化，而不是重复同一模板。 |
