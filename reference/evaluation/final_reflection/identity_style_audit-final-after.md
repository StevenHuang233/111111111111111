# Identity And Style Audit / 身份措辞与解说风格审计

EN: This report checks whether generated commentary uses supported identities and natural broadcast wording.

ZH: 本报告检查生成解说是否使用有依据的身份表达，以及是否接近自然人类解说。

## Summary / 摘要

- `segment_count`: 235
- `color_identity_segments`: 4
- `team_identity_segments`: 220
- `number_identity_segments`: 104
- `role_identity_segments`: 187
- `raw_visual_segments`: 42
- `wrong_entity_segments`: 0
- `unsupported_name_segments`: 0
- `color_identity_ratio`: 0.017
- `raw_visual_ratio`: 0.1787

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
| The broadcast brings us | 21 | U023 |
| Germany find a pocket | 16 | U034 |
| Germany's No. 10 drives | 13 | U020 |
| Germany keep the pressure | 10 | U032 |
| A Curacao player goes | 7 | U072 |
| The game moves through | 6 | U071 |
| Germany make a change | 4 | U029 |
| A German player goes | 4 | U088 |
| Germany builds a dangerous | 4 | U092 |
| The stage is set | 3 | U004 |
| Curacao's goalkeeper makes a | 3 | U035 |
| Germany's No. 19 drives | 3 | U044 |

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
| U001 | period_transition | `00:00:04-00:01:04` | The pre-match ceremony is underway at the FIFA World Cup 2026, as Germany and Curacao make their grand entrance onto the pitch. Referees in bright yellow kits lead the procession,  |
| U038 | dangerous_attack | `00:18:36-00:18:36` | Germany pushes forward with pace, a white-shirted attacker surges into the final third, drawing defenders and creating space. The buildup is sharp, the movement fluid — Curacao’s b |
| U138 | period_transition | `01:00:12-01:00:36` | The second half is underway. Germany and Curacao line up at the center circle for the kickoff after halftime. The referee signals as players settle into position — Germany in white |
| U208 | goal | `01:31:12-01:32:36` | Germany in possession near Curacao's penalty area with multiple attackers advancing into the final third; German player dribbling toward Curacao box, drawing defenders; attacking b |

## Raw Visual Wording / 原始画面式措辞

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U002 | celebration_or_replay | `00:01:12-00:01:12` | The German fans are on their feet, waving flags in unison as the stadium erupts in celebration — a powerful visual echo of Germany’s dominance in this World Cup encounter. / 德国队球迷全 |
| U008 | period_transition | `00:04:28-00:04:28` | A sweeping view of the stadium as Germany and Curacao line up for the pre-match ceremony. The pitch is adorned with giant national flags — Germany’s black-red-gold on the left, Cur |
| U009 | celebration_or_replay | `00:04:32-00:04:32` | A close-up on a Curacao player, eyes closed and mouth open in a moment of deep focus or reflection before the match begins. / 镜头给到库拉索队一名球员的特写，他双眼紧闭，嘴巴微张，似乎在赛前进行着深度的专注与调整。 |
| U016 | other_relevant | `00:06:28-00:06:36` | The match officials are walking onto the pitch, ready to take control of the game. The referee and his assistants are seen in discussion, likely finalizing their pre-match briefing |
| U018 | celebration_or_replay | `00:08:08-00:08:24` | Germany players in white kits gather in a tight huddle, celebrating with visible emotion and unity — Sané (No. 19) among them, arms locked as teammates close in. The crowd behind t |
| U023 | celebration_or_replay | `00:11:00-00:11:56` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U030 | celebration_or_replay | `00:15:44-00:15:56` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U047 | celebration_or_replay | `00:20:36-00:21:32` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U049 | celebration_or_replay | `00:22:52-00:23:44` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U063 | other_relevant | `00:29:08-00:29:08` | Germany's No. 1, Manuel Neuer, stands on the pitch as a broadcast graphic reminds us he is Germany's oldest ever player at 40 years and 79 days. / 德国队门将诺伊尔站在场上，屏幕上的数据显示，他已成为德国队历史上年 |
| U068 | goal | `00:30:32-00:31:20` | Curacao strike first! The blue and yellow team breaks through Germany's defense with a precise shot from inside the penalty area. The ball finds the bottom corner of the net as the |
| U071 | period_transition | `00:31:52-00:32:44` | The game moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U077 | celebration_or_replay | `00:34:52-00:36:12` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U096 | celebration_or_replay | `00:41:48-00:41:52` | Curacao's No. 7 takes a shot from close range, but Germany's goalkeeper makes a spectacular diving save to his right, pushing the ball away just in time. The German players react w |
| U102 | goal | `00:45:16-00:46:36` | Germany takes a free kick near the edge of the penalty area. The ball is struck with precision, flying past the defensive wall and into the net. The net ripples as the ball crosses |
| U133 | celebration_or_replay | `00:56:16-00:56:48` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U134 | goal | `00:57:00-00:58:20` | Germany's No. 7, Havertz, steps up to take the penalty kick. He approaches the ball with composure, the Curacao goalkeeper ready in goal. Havertz strikes it cleanly — the ball find |
| U135 | celebration_or_replay | `00:58:40-00:59:08` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |
| U139 | period_transition | `01:00:48-01:00:52` | The game moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U144 | celebration_or_replay | `01:02:28-01:02:44` | The broadcast brings us back to that attacking sequence. Germany worked the ball into a dangerous area, and the replay angle lets us focus on the movement, the defensive recovery,  |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Block unsupported names and wrong teams before final packaging. | 最终打包前必须拦截无依据姓名和错误球队。 |
| Should | Add an identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric. | 增加身份选择级联：已验证姓名 -> 球队+号码/角色 -> 仅球队 -> 少量颜色修辞。 |
| Should | Use a style sampler so wording varies naturally inside the same broadcast style instead of repeating one template. | 使用风格采样器，让同一解说风格内部自然变化，而不是重复同一模板。 |
