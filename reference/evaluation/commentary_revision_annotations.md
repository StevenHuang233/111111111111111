# Commentary Revision Annotations / 解说修订标注

EN: This file marks which generated segments are blocked, warning-only, or clear for final use.

ZH: 本文件标注生成解说中哪些片段属于阻塞、仅警告或可保留。

## Summary / 摘要

- `segments`: 257
- `status_counts`: {'clear': 149, 'warning': 75, 'blocker': 32, 'polish': 1}
- `policy_counts`: {'not_for_final_demo': 32, 'score_change_not_allowed': 21, 'unsafe_fact_claim': 14, 'style_rewrite_needed': 85}

## Blockers / 阻塞片段

| Event | Type | Time | Issues | Suggested Treatment | Excerpt |
| --- | --- | --- | --- | --- | --- |
| U011 | other_relevant | `00:05:28-00:05:32` | unsupported_name, wrong_entity, raw_visual_wording | remove_unsafe_fact_or_replace_with_verified_team_role_number | 看台上传来了热烈的回应。一片蓝黄海洋，哥伦比亚球迷戴着他们标志性的宽边帽，双手合十，屏息凝神。镜头一转，来到球场另一端——德国球迷顶着他们标志性的红黄假发，声浪高涨，为球队呐喊助威。两种截然不同的文化，却共同点燃了这炽热的赛场氛围。 |
| U014 | var_review | `00:06:48-00:06:52` | prematch_action_misclassification | rewrite_as_opening_officials_broadcast_context | VAR团队正在回看这次犯规。主裁判哈姆扎·埃尔法里奥和助理裁判尼古拉斯·加洛在海信VAR室内仔细查看录像，多个屏幕同步播放着不同角度的回放。辅助VAR肖恩·埃文斯也参与其中协助判断。裁判组目前暂停比赛，正在等待最终决定。 |
| U036 | goal | `00:14:08-00:15:28` | unsupported_name, wrong_entity, raw_visual_wording | remove_unsafe_fact_or_replace_with_verified_team_role_number | 德国队领先了！禁区内的混战中，一脚射门直挂球门死角。门将虽然奋力扑救，但未能触碰到皮球，球滚入网窝。德国球员和球迷立刻爆发庆祝——23号球员身处庆祝中心，与队友帕夫洛维奇（5号）紧紧相拥。记分牌确认：德国 1-0 哥伦比亚。回放显示，最初的射门被门将扑出，但反弹球恰到好处地送到了射门者脚下。纯粹的冷静把握机会。 |
| U042 | goal | `00:17:12-00:18:12` | extra_goal_assertion, unsupported_name, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 看哪——德国队将比分扩大为两球领先！穆勒在禁区内的处理干净利落，皮球稳稳滚入网窝。门将奋力扑救却鞭长莫及，这完全是高压下的冷静把握。穆勒转身面露满意之色，现场观众瞬间沸腾。慢动作回放显示，恩昆库的犀利跑位扯开了防线，为穆勒创造了射门空间。这是一粒教科书般的进球。 |
| U054 | celebration_or_replay | `00:21:00-00:21:00` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 就是这一瞬间——纯粹的精准。德国前锋迎球凌空抽射，皮球越过门将，直入网窝。现场沸腾了，记分牌确认：德国队1-0领先。高压之下的教科书式破门。 |
| U062 | dangerous_attack | `00:23:32-00:23:32` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 德国15号在推进中举手示意——球队攻势如潮，正全力压入对方半场。攻势渐起，危险进攻一触即发，但尚未有射门或进球确认。 |
| U084 | foul | `00:33:00-00:33:00` | unsupported_name, wrong_entity | remove_unsafe_fact_or_replace_with_verified_team_role_number | 德国球员被身后铲倒，毫无防备——哥伦比亚防守队员这一脚直接将他放倒。裁判立即吹罚犯规，比赛暂停，倒地的球员正在接受队医处理。 |
| U089 | foul | `00:34:36-00:34:40` | unsupported_name, wrong_entity | remove_unsafe_fact_or_replace_with_verified_team_role_number | 这里犯规了——哥伦比亚球员在身后对德国进攻球员进行了一次铲球，导致他摔倒在地。裁判需要判断这次接触是草率还是鲁莽。 |
| U090 | goal | `00:34:52-00:36:16` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队在禁区附近获得任意球。皮球精准踢出，绕过人墙直挂球门死角。德国队球员随即庆祝进球，裁判确认有效。慢动作回放显示皮球飞越了扑救的门将，直入网窝。现场观众的反应可谓喜忧参半。 |
| U118 | dangerous_attack | `00:43:04-00:43:08` | unsupported_name, wrong_entity | remove_unsafe_fact_or_replace_with_verified_team_role_number | 哥伦比亚12号沿右路高速插上，面对德国后卫的合围选择内切——禁区内的关键一瞬，虽然尚未射门，但攻势一触即发。 |
| U119 | dangerous_attack | `00:43:16-00:43:16` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队在对方禁区前沿发起了一次危险的进攻，多名球员进入禁区，传中球送入拥挤的禁区内。皮球进入禁区时，这次机会看起来很有希望，但此刻结果仍难预料。 |
| U130 | celebration_or_replay | `00:48:48-00:49:08` | unsupported_name, raw_visual_wording | remove_unsafe_fact_or_replace_with_verified_team_role_number | 德国队领先！施潘内一记劲射破门，皮球直挂死角，主场球迷瞬间沸腾。回放显示他精准地晃过了飞身扑救的门将，为德国队锁定关键一球。记分牌更新为2-1，球迷们在庆祝声中欢呼雀跃。 |
| U131 | goal | `00:49:40-00:50:40` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队取得领先！进攻配合行云流水，皮球精准推进至前场。一名球员带球突破防线，送出致命一击，皮球直挂球门死角。门将奋力扑救却鞭长莫及，皮球越过门线。德国球员随即展开庆祝，现场球迷欢呼雀跃。记分牌显示，德国队以2-1领先。 |
| U135 | goal | `00:51:40-00:53:00` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队在禁区附近获得任意球。德国球员起脚射门，皮球直挂球门死角！门将奋力扑救却鞭长莫及。皮球越过门线，德国队球员纷纷庆祝进球，现场球迷也爆发出热烈的欢呼声。 |
| U136 | celebration_or_replay | `00:53:12-00:53:20` | extra_goal_assertion, color_identity_fallback, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 身穿蓝黄球衣的库拉索球员庆祝进球，现场球迷瞬间沸腾。记分牌显示，比赛第45分02秒时德国队以2-1领先，但主场球迷显然士气高涨。特写镜头捕捉到球迷们的激动反应，有人挥舞旗帜，有人笑容满面，气氛热烈，充分展现了这一刻的激情与活力。 |
| U162 | goal | `01:06:04-01:06:16` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 球进了！德国队破门得分！皮球直挂死角，门将鞭长莫及。萨内和穆西亚拉在进球后立刻展开了庆祝。 |
| U176 | celebration_or_replay | `01:12:24-01:12:28` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 进了！穆西亚拉为德国队打入第10粒进球。记分牌显示4-1领先，穆西亚拉气喘吁吁，弯腰喘息，显然已经筋疲力尽。 |
| U180 | goal | `01:14:52-01:15:00` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 进了！德国队进球了！皮球入网，门将扑救不及。进球的德国球员转身面露专注神情，队友们随即开始庆祝，比分牌更新为4-1。 |
| U186 | celebration_or_replay | `01:16:40-01:16:52` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 德国球迷在看台上彻底沸腾了！看那一片黑白红金的海洋，所有人起立，挥舞手臂，旗帜飘扬——这绝对是关键进球后点燃的狂热氛围。能量极具感染力，整座球场都在庆祝中震颤。你能从每个角落感受到释放的喜悦，他们为球队4-1的领先优势欢呼雀跃。 |
| U187 | free_kick | `01:16:56-01:17:08` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队在禁区前沿获得了一个任意球。裁判确认人墙站好，主罚球员上前掌控局面。此时比分4-1，德国队又获得了一次扩大领先优势的机会。 |
| U191 | shot | `01:17:40-01:17:40` | unsupported_name, wrong_entity | remove_unsafe_fact_or_replace_with_verified_team_role_number | 哥伦比亚11号禁区外大力抽射——皮球如炮弹般直挂球门，德国门将严阵以待。这一瞬间剑拔弩张，皮球能否应声入网？ |
| U193 | goal | `01:18:08-01:18:52` | extra_goal_assertion, unsupported_name | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队进球了！快速反击沿右路推进，格纳布里内切，一脚低射越过门将，皮球滚入球门死角。网窝随之颤动，皮球越过门线，德国球员立刻高举手臂庆祝。现场球迷沸腾，全体起立，有人难以置信地捂着头，有人狂喜。回放展现了这粒进球的精准度以及促成这次进攻的速度。 |
| U200 | foul | `01:21:12-01:21:16` | extra_goal_assertion | suppress_score_change_or_rewrite_as_replay_history_pending | 库拉索队的巴库纳准备头球攻门，但被翁达夫的防守动作干扰失去重心。这名德国后卫从背后与巴库纳发生接触，导致后者重重摔倒在地。裁判毫无疑问会判罚库拉索队获得一个任意球，这次铲抢确实太过鲁莽。 |
| U201 | other_relevant | `01:21:20-01:21:20` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 库拉索队10号球员利安德罗·巴库纳，此刻身披战袍，屏幕上的数据显示他已为国家队出场第73次。比赛进行到65分42秒，场上比分仍是德国4-1领先库拉索，巴库纳正与一名身穿德国队服的对手并肩而立。 |
| U202 | goal | `01:21:32-01:22:04` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 库拉索在禁区附近获得任意球。球传入禁区，一名库拉索球员插上射门。他在禁区内起脚，德国门将奋力扑救，但球从他身边入网。库拉索球员庆祝进球，现场球迷欢呼雀跃，挥舞旗帜、高举双臂。记分牌更新显示最新比分。回放显示进攻球员带球突入禁区，防守队员迅速逼近。 |
| U222 | goal | `01:29:44-01:30:40` | extra_goal_assertion, color_identity_fallback | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队扩大了领先优势！白衣进攻球员在禁区起脚射门，绿衣门将奋力扑救却未能触球，皮球应声入网。随着进球被确认，现场观众瞬间沸腾。 |
| U225 | goal | `01:31:28-01:32:36` | unsupported_name, raw_visual_wording | remove_unsafe_fact_or_replace_with_verified_team_role_number | 德国队6-1领先！皮球入网，德国球员瞬间爆发庆祝。全场起立，记分牌确认进球。恩昆库与基米希拥抱，共享此刻喜悦。回放显示禁区内的精彩射门，骗过飞身扑救的门将。看台球迷狂喜，挥舞旗帜欢呼。这一球进一步巩固了德国队的场上优势。 |
| U238 | goal | `01:38:04-01:38:32` | extra_goal_assertion, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 德国队26号维尔茨在禁区内找到空当，一脚低射破门！皮球入网，网窝随之颤动。确认无误：德国队将比分扩大为6-1。维尔茨在球门附近庆祝，现场观众沸腾。慢镜头回放显示，这脚射门来自球门后方——一记冷静的终结，彻底锁定胜局。 |
| U244 | goal | `01:42:08-01:43:24` | unsupported_name | remove_unsafe_fact_or_replace_with_verified_team_role_number | 德国队进球了！哈弗茨在禁区内的这脚射门非常犀利，皮球直挂死角，门将鞭长莫及。现场球迷瞬间沸腾——比分变成7-1！哈弗茨与维尔茨、格雷茨卡拥抱庆祝，德国球迷挥舞旗帜，欢呼声震耳欲聋。这是一次教科书般的终结，进一步拉大了领先优势。 |
| U248 | goal | `01:46:32-01:47:44` | extra_goal_assertion, unsupported_name, wrong_entity, raw_visual_wording | suppress_score_change_or_rewrite_as_replay_history_pending | 伤停补时阶段，哥伦比亚10号球员带球高速突破，身后有一名德国后卫紧追不舍。他加速突入禁区，果断起脚射门。皮球直挂球门死角——网窝剧烈晃动，门将鞭长莫及，现场球迷瞬间沸腾。进球有效！哥伦比亚在比赛最后时刻取得领先。球员们在球门线附近庆祝看台上的球迷情绪激动，一位女球迷甚至举起手机记录下这历史性的一刻，画面中还叠加了FIFA的图形特效。虽然记分牌可能略有延迟，但 |
| U249 | foul | `01:46:36-01:46:36` | unsupported_name, wrong_entity | remove_unsafe_fact_or_replace_with_verified_team_role_number | 哨声响起！德国22号防守球员在边路与哥伦比亚10号进攻球员发生身体接触，导致对方失去平衡。助理裁判立即举旗，这应该是一次犯规。 |
| U252 | goal | `01:48:12-01:49:32` | extra_goal_assertion, wrong_entity | suppress_score_change_or_rewrite_as_replay_history_pending | 伤停补时阶段，德国队在禁区前沿获得任意球。皮球精准踢出，绕过人墙，直挂球门死角。哥伦比亚门将奋力扑救，但未能触碰到皮球，球已入网。现场观众沸腾庆祝，德国队将比分扩大为8-1。 |
