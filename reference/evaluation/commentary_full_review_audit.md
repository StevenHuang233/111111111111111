# Commentary Output Audit / 解说输出审计

EN: Evaluation-only report. Do not feed public facts into the target agent prompt.

ZH: 本报告仅用于验证。不要把公开事实注入目标 Agent 的 prompt。

## Summary / 摘要

- `segment_count`: 75
- `generated_goal_count`: 23
- `expected_goal_count_from_public_reference`: 8
- `asr_goal_candidate_count`: 9
- `critical_or_high_issue_count`: 12
- `style_issue_count`: 13
- `score_claim_count`: 23

## Expected Goal Sequence / 公开参考进球顺序

| # | Score | Minute | Team | Scorer | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Germany 1-0 Curacao | 6 | Germany | Nmecha | Second-line finish after a group move. |
| 2 | Germany 1-1 Curacao | 21 | Curacao | Livano Comenencia | Historic first World Cup goal for Curacao. |
| 3 | Germany 2-1 Curacao | 38 | Germany | Schlotterbeck | Header from a corner. |
| 4 | Germany 3-1 Curacao | 45+5 | Germany | Havertz | Penalty after Bazoer fouled Nmecha. |
| 5 | Germany 4-1 Curacao | 47 | Germany | Musiala | Run into space and low finish. |
| 6 | Germany 5-1 Curacao | 68 | Germany | Brown | Strong shot from the edge of the area. |
| 7 | Germany 6-1 Curacao | 78 | Germany | Undav | Finish into an open or exposed goalmouth. |
| 8 | Germany 7-1 Curacao | 88 | Germany | Havertz | Second Havertz goal; lob/quality finish. |

## Generated Goal Alignment / 生成 goal 事件对齐

| Event | Time | Score Claims | Nearest ASR | Distance | Excerpt |
| --- | --- | --- | --- | --- | --- |
| U005 | `00:14:08-00:15:28` | 1-0, 1-0, 14:08, 14:12, 14:24 | AG01 `00:14:03-00:16:36` | 5s | 德国队率先取得领先！第14分08秒，一名身穿白色球衣的德国球员进入禁区，受到防守队员的紧逼盯防。他在第14分12秒于禁区内射门，身穿橙色球衣的门将奋力扑救并触碰到皮球，但球反弹出来。到第14分24秒，皮球越过球门线，记分牌更新为1-0。23 |
| U008 | `00:17:12-00:18:12` | - | AG01 `00:14:03-00:16:36` | 36s | 德国队扩大了领先优势！一次精妙的进攻中，昆库带球向前，制造了犯规，随后球传到穆勒脚下，他射门越过扑救的门将。球网晃动确认进球，现场观众爆发出庆祝的欢呼。 |
| U020 | `00:30:48-00:31:20` | - | AG02 `00:29:31-00:30:38` | 10s | 一名身穿白色球衣的德国球员在禁区范围内射门，但身穿蓝色球衣的门将飞身扑救成功阻止了射门。球没有进入球门。 |
| U022 | `00:34:52-00:36:16` | - | AG02 `00:29:31-00:30:38` | 254s | 德国队在禁区前沿获得任意球。皮球快速开出并绕过人墙，德国15号球员高高跃起，力压防守队员头球攻门。皮球飞越了扑救的门将，直入网窝！德国队进球！进球球员将手放在胸前庆祝，而门将则面露失望。 |
| U033 | `00:45:16-00:46:36` | 2-1 | AG03 `00:45:19-00:46:26` | 3s | 德国队在禁区外获得任意球。皮球精准踢出，绕过人墙，飞入球门死角！德国队球员爆发庆祝，记分牌更新为2-1。看台上的球迷挥舞旗帜、欢呼雀跃，队友们纷纷冲上前互相祝贺这粒关键进球。 |
| U034 | `00:49:40-00:50:40` | 2-1 | AG03 `00:45:19-00:46:26` | 194s | 德国队在本场比赛中率先取得领先。一名球员带球进入禁区，射门越过门将，将球送入网窝。德国球员庆祝得分，记分牌更新为2-1。回放显示，进攻球员在中圈附近带球过掉防守队员，随后精准射门，使门将无能为力。随着进球被确认，观众席上爆发出热烈的欢呼声。 |
| U035 | `00:51:40-00:53:00` | - | AG04 `00:57:19-00:58:26` | 339s | 德国队在禁区外获得任意球。皮球精准地开出，绕过人墙，飞入球门死角。德国球员庆祝进球，皮球入网，德国队领先优势扩大。 |
| U039 | `00:55:48-00:56:48` | 2-1 | AG04 `00:57:19-00:58:26` | 91s | 德国队在禁区前沿射门，皮球越过飞身扑救的哥伦比亚门将，飞入球门。进球有效，德国队2-1领先。随后裁判准备开出任意球，德国队7号球员上前准备主罚。 |
| U040 | `00:57:00-00:58:20` | - | AG04 `00:57:19-00:58:26` | 19s | 德国队获得点球机会，球员7号主罚，助跑后大力射门，皮球直挂球门死角，门将虽奋力扑救但未能阻止入网！德国队3-1领先！ |
| U041 | `01:01:40-01:02:44` | 4-1 | AG06 `01:01:24-01:02:33` | 16s | 德国队进入对方半场，多名球员在禁区附近站位。穆西亚拉在禁区内射门，门将飞身扑救但未能阻止皮球入网。皮球越过球门线，穆西亚拉跑开庆祝。两名德国球员穆西亚拉和恩梅查拥抱庆祝。记分牌更新为4-1。德国球迷热情欢呼，挥舞围巾并举起手臂。德国球员在场 |
| U042 | `01:02:56-01:03:00` | - | AG06 `01:01:24-01:02:33` | 23s | 穆西亚拉为德国队破门，将领先优势扩大至四球，这是一场对库拉索的压倒性胜利。 |
| U043 | `01:06:04-01:06:16` | - | AG07 `01:06:26-01:07:34` | 22s | 德国队进球了！皮球入网，德国球员与队友庆祝。进球后，萨内和穆西亚拉向观众致意。 |
| U047 | `01:12:24-01:12:28` | 4-1 | AG07 `01:06:26-01:07:34` | 290s | 穆西亚拉为德国队破门，这是他在本届赛事中的第10个进球。比分更新为4-1，穆西亚拉在射门后稍作喘息。 |
| U048 | `01:14:52-01:15:00` | - | AG07 `01:06:26-01:07:34` | 438s | 德国队进球了！皮球入网，德国球员与队友庆祝，而门将仍倒在地上。 |
| U053 | `01:18:08-01:18:52` | 5-1 | AG08 `01:23:00-01:24:08` | 292s | 德国队发动快速进攻。前锋突入禁区，摆脱越位陷阱。他调整一步后，低射破门，皮球越过出击的门将，直挂球门死角。进球！网窝晃动，现场球迷欢呼沸腾。进球球员转身，手指指向天空庆祝。看台上一名德国球迷双手抱头，被这瞬间震撼。回放显示，前锋在禁区边缘接 |
| U056 | `01:21:32-01:22:04` | 4-1 | AG08 `01:23:00-01:24:08` | 88s | 库拉索队在禁区前沿获得任意球。球传入禁区，一名库拉索前锋迎球大力头球攻门。德国门将奋力扑救却未能触球——皮球飞入网窝！库拉索球员爆发庆祝，现场球迷欢呼雀跃。看台上球迷挥舞旗帜，一名球员高举手臂向看台致意。记分牌仍显示4-1，但此球已扭转比赛 |
| U057 | `01:23:16-01:24:24` | 5-1 | AG08 `01:23:00-01:24:08` | 16s | 德国队在禁区前沿射门。皮球入网，门将扑救徒劳无功。德国队进球了！18号球员与队友激情庆祝，现场观众欢呼雀跃。比分更新为5-1，德国队领先。 |
| U063 | `01:29:44-01:30:40` | - | AG08 `01:23:00-01:24:08` | 336s | 第75分钟，德国队身穿白色球衣的球员在禁区前沿射门。身穿绿色球衣的门将向右侧飞身扑救，但未能阻止皮球入网。现场观众爆发出欢呼声，球迷们鼓掌庆祝这一进球。慢镜头回放显示，尽管门将奋力扑救，皮球仍滚入网窝。随后画面切换到身穿橙色球衣的门将持球， |
| U064 | `01:31:28-01:32:36` | 6-1 | AG08 `01:23:00-01:24:08` | 440s | 德国队进球了！皮球入网，德国球员们爆发庆祝。记分牌更新为6-1，确认进球有效。看台上的球迷纷纷起立，疯狂欢呼，庆祝球队在比赛的这一关键时刻。 |
| U067 | `01:38:04-01:38:32` | 6-1, 6比1 | AG09 `01:48:54-01:50:01` | 650s | 德国队在对方半场持续组织进攻，球员进入禁区制造压力。球被转移到危险位置，随后有人从近距离射门。德国队26号球员维尔茨跟进庆祝，皮球入网，将德国队对库拉索的领先优势扩大至6比1。 |
| U071 | `01:42:08-01:43:24` | 7-1 | AG09 `01:48:54-01:50:01` | 406s | 进了！德国队再次得分！哈弗茨在禁区内射门得分，骗过了飞身扑救的门将。比分更新为7-1，德国球迷爆发庆祝。哈弗茨与队友维尔茨和施洛特贝克一起被队友包围，展现出欢乐的团队精神。球迷挥舞旗帜，疯狂欢呼，这是德国队在本场比赛中的统治性时刻。 |
| U073 | `01:46:32-01:47:44` | - | AG09 `01:48:54-01:50:01` | 142s | 伤停补时阶段，哥伦比亚10号球员带球高速突破，身后有一名德国后卫紧追不舍。他进入禁区并射门，皮球飞过了扑救的门将，直入网窝！哥伦比亚进球了！现场观众欢呼雀跃，球员们庆祝进球，看台上的球迷用手机记录下这一精彩瞬间。回放显示，进攻球员跑位巧妙， |
| U075 | `01:48:12-01:49:32` | - | AG09 `01:48:54-01:50:01` | 42s | 伤停补时阶段，德国队在禁区外获得任意球。皮球摆放妥当，德国球员起脚大力射门，皮球绕过人墙飞入球门死角。哥伦比亚门将奋力扑救但未能触球。进球有效，德国球员庆祝，观众对这一绝杀进球做出反应。 |

## Issues / 问题

| Severity | Category | Event | Time | Message |
| --- | --- | --- | --- | --- |
| medium | non_broadcast_style | U003 | `00:11:52-00:11:52` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U005 | `00:14:08-00:15:28` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| high | unsupported_named_fact | U005 | `00:14:08-00:15:28` | Named player 'Ibragimov' is unsupported by the evaluation reference. |
| high | unsupported_named_fact | U008 | `00:17:12-00:18:12` | Named player 'Nkunku' is unsupported by the evaluation reference. |
| high | unsupported_named_fact | U008 | `00:17:12-00:18:12` | Named player 'Müller' is unsupported by the evaluation reference. |
| medium | non_broadcast_style | U009 | `00:18:40-00:18:40` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U011 | `00:20:44-00:20:44` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U018 | `00:29:48-00:29:48` | Color/jersey descriptor '蓝队' should usually be team/player identity or avoided. |
| critical | goal_label_contradiction | U020 | `00:30:48-00:31:20` | Event is labeled goal but its text says no goal / no ball entry. |
| medium | non_broadcast_style | U020 | `00:30:48-00:31:20` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U027 | `00:38:32-00:38:32` | Color/jersey descriptor 'blue jersey' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U029 | `00:41:28-00:41:28` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U037 | `00:55:16-00:55:16` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| critical | wrong_team_or_entity | U039 | `00:55:48-00:56:48` | Mentions 'Colombia', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U039 | `00:55:48-00:56:48` | Mentions 'Colombian', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U039 | `00:55:48-00:56:48` | Mentions '哥伦比亚', which is not part of Germany vs Curacao. |
| medium | non_broadcast_style | U045 | `01:09:12-01:09:12` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U061 | `01:28:00-01:28:00` | Color/jersey descriptor 'blue jersey' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U063 | `01:29:44-01:30:40` | Color/jersey descriptor 'player in white' should usually be team/player identity or avoided. |
| medium | non_broadcast_style | U072 | `01:45:20-01:45:20` | Color/jersey descriptor '身穿白色球衣' should usually be team/player identity or avoided. |
| critical | wrong_team_or_entity | U073 | `01:46:32-01:47:44` | Mentions 'Colombia', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U073 | `01:46:32-01:47:44` | Mentions '哥伦比亚', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U075 | `01:48:12-01:49:32` | Mentions 'Colombia', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U075 | `01:48:12-01:49:32` | Mentions 'Colombian', which is not part of Germany vs Curacao. |
| critical | wrong_team_or_entity | U075 | `01:48:12-01:49:32` | Mentions '哥伦比亚', which is not part of Germany vs Curacao. |

## Recommendations / 改进建议

- Add a scoreboard/state verifier before accepting any goal label or score-changing commentary.
- Use ASR goal candidates only as weak retrieval windows, then verify with frame evidence.
- Force every generated goal to pass a monotonically increasing score-state check.
- Require unsupported player names to be backed by roster, jersey number OCR, or user metadata; otherwise say team/player role.
- Add a style linter that rejects repeated color-shirt descriptions in final broadcast text.
- Separate live goals, replays, halftime summaries, and historical mentions before commentary generation.
