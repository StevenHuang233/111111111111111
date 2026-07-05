# Identity And Style Audit / 身份措辞与解说风格审计

EN: This report checks whether generated commentary uses supported identities and natural broadcast wording.

ZH: 本报告检查生成解说是否使用有依据的身份表达，以及是否接近自然人类解说。

## Summary / 摘要

- `segment_count`: 235
- `color_identity_segments`: 5
- `team_identity_segments`: 218
- `number_identity_segments`: 98
- `role_identity_segments`: 129
- `raw_visual_segments`: 21
- `wrong_entity_segments`: 0
- `unsupported_name_segments`: 0
- `color_identity_ratio`: 0.0213
- `raw_visual_ratio`: 0.0894

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
| Curacao create a shooting | 13 | U026 |
| Germany's No. 10 drives | 9 | U020 |
| Curacao push forward and | 8 | U040 |
| A Curacao player goes | 7 | U055 |
| Germany push forward and | 5 | U032 |
| The match moves through | 5 | U071 |
| Germany's No. 10 takes | 4 | U039 |
| Germany builds a dangerous | 4 | U098 |
| The stage is set | 3 | U003 |
| A German player goes | 3 | U027 |
| Germany make a change | 3 | U029 |
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
| U001 | period_transition | `00:00:04-00:01:04` | The referees lead the way onto the pitch, followed by the teams in their pre-match warm-up gear. Germany's players, identifiable by their white jackets and black shorts, walk along |
| U003 | period_transition | `00:01:16-00:01:32` | The stage is set for the 2026 World Cup as Germany and Curacao line up for the pre-match ceremony. Players from both teams form a circle around the center pitch, flags waving under |
| U024 | foul | `00:11:12-00:11:16` | A German player in white shirt makes contact with a Curacao player in blue/yellow shirt, causing the Curacao player to fall. The ball is loose nearby, indicating a stoppage likely  |
| U138 | period_transition | `01:00:12-01:00:36` | The second half gets underway at the Astrodome in Houston. Germany kick off, with their players in white shirts and black shorts taking control of the center circle. Curacao, in th |
| U227 | foul | `01:46:48-01:46:48` | Late in stoppage time, a German defender in white makes contact with a Curacao player in blue and yellow as he attempts to advance, causing the Curacao player to go down under the  |

## Raw Visual Wording / 原始画面式措辞

| Event | Type | Time | Excerpt |
| --- | --- | --- | --- |
| U003 | period_transition | `00:01:16-00:01:32` | The stage is set for the 2026 World Cup as Germany and Curacao line up for the pre-match ceremony. Players from both teams form a circle around the center pitch, flags waving under |
| U009 | celebration_or_replay | `00:04:32-00:04:32` | A close-up on a Curacao player, eyes closed and mouth open in a moment of intense emotion or concentration, likely during the national anthem before the match. / 镜头给到库拉索队一名球员的特写，他双 |
| U013 | other_relevant | `00:05:28-00:05:32` | The atmosphere in the stadium is electric as we see passionate fans from both teams. Curacao supporters, donned in their vibrant blue and yellow jerseys with distinctive cowboy hat |
| U017 | var_show | `00:06:40-00:06:52` | The broadcast shows match-official and video-review context. Treat this as background information only, and avoid naming countries or people unless the graphic is independently ver |
| U024 | foul | `00:11:12-00:11:16` | A German player in white shirt makes contact with a Curacao player in blue/yellow shirt, causing the Curacao player to fall. The ball is loose nearby, indicating a stoppage likely  |
| U028 | goal | `00:14:08-00:15:28` | Germany takes an early lead! Nmecha, wearing number 23, finds the back of the net with a powerful shot from inside the penalty area. The German fans erupt in celebration as the sco |
| U054 | other_relevant | `00:25:52-00:25:56` | Germany's No. 10, Leroy Sané, is seen in close-up, focused and composed as the match continues. The referee is actively communicating via his earpiece, likely coordinating with the |
| U071 | period_transition | `00:31:52-00:32:44` | The match moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U096 | celebration_or_replay | `00:41:48-00:41:52` | Curacao's attacker in blue and yellow takes a shot, but Germany's goalkeeper makes a spectacular save, leaping high to palm the ball away. The German players on the pitch react wit |
| U103 | foul | `00:45:24-00:45:24` | At the 45:24 mark, Curacao's No. 5 Floranus is shown in a heated exchange with a German player, prompting the referee to step in and separate them with arms outstretched. The close |
| U118 | other_relevant | `00:53:28-00:53:28` | This is contextual broadcast footage around a stoppage or reset, so the commentary should stay on visible organization and rhythm. / 这是停顿或重新组织阶段的转播背景，解说应聚焦可见的站位、节奏和场上组织。 |
| U139 | period_transition | `01:00:48-01:00:52` | The match moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U170 | period_transition | `01:16:56-01:16:56` | The match moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U178 | substitution | `01:19:08-01:19:56` | The broadcast cuts to a substitution sequence, with the fourth official and players preparing for the change. / 转播画面切到换人调整，第四官员举牌，双方球员准备完成这次人员变化。 |
| U189 | period_transition | `01:24:44-01:25:08` | The hydration break is underway in this World Cup clash between Germany and Curacao. Players from both sides are seen heading towards the sidelines to rehydrate, with German player |
| U191 | period_transition | `01:25:44-01:25:56` | The match moves through a short transition phase as players reset positions and the broadcast re-establishes the field. / 比赛进入短暂的阶段转换，球员重新站位，转播镜头重新交代场上形势。 |
| U195 | substitution | `01:27:04-01:27:08` | Germany make their second double substitution of the match. Nmecha comes on for Tah, and Brown replaces Raum. The graphic confirms the changes as Germany look to add fresh legs in  |
| U208 | goal | `01:31:12-01:32:36` | Germany takes control near Curacao's penalty area, building pressure with quick passes and overlapping runs. A shot from outside the box is saved by the Curacao goalkeeper, but Ger |
| U215 | substitution | `01:36:20-01:36:52` | The broadcast cuts to a substitution sequence, with the fourth official and players preparing for the change. / 转播画面切到换人调整，第四官员举牌，双方球员准备完成这次人员变化。 |
| U220 | goal | `01:42:00-01:43:24` | Germany takes control in the final third as No. 7, Havertz, drives forward with the ball. He cuts inside past a sliding Curacao defender and unleashes a low shot from just outside  |

## Recommendations / 建议

| Priority | EN | ZH |
| --- | --- | --- |
| Must | Block unsupported names and wrong teams before final packaging. | 最终打包前必须拦截无依据姓名和错误球队。 |
| Should | Add an identity cascade: verified name -> team+number/role -> team-only -> rare color rhetoric. | 增加身份选择级联：已验证姓名 -> 球队+号码/角色 -> 仅球队 -> 少量颜色修辞。 |
| Should | Use a style sampler so wording varies naturally inside the same broadcast style instead of repeating one template. | 使用风格采样器，让同一解说风格内部自然变化，而不是重复同一模板。 |
