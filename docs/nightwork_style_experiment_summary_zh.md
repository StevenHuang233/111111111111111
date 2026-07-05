# Nightwork API 风格实验摘要

实验目的：验证新增 `MatchContext` 和两种新风格是否能在真实 Intern-S2-Preview API 调用中生效。

实验输入：

- 事件来源：`outputs/coarse_new_boundary_20260704_223738/goal_validation/refined_events.json`
- 视频帧来源：`C:/Users/hjj/Desktop/frames_4fps_q3/frames_manifest.json`
- 比赛上下文：`germany_curacao_world_cup_2026`
- 风格：`storytelling_witty`、`elite_broadcast_replay`
- 事件：`U036`、`U149`、`U225`

实验输出保存在本机：

```text
outputs/nightwork_style_experiment/summary.md
outputs/nightwork_style_experiment/summary.json
outputs/nightwork_style_experiment/storytelling_witty/commentary_bilingual.json
outputs/nightwork_style_experiment/elite_broadcast_replay/commentary_bilingual.json
```

质量检查：

- 未出现 `Colombia`、`Paraguay`、`哥伦比亚`、`巴拉圭`。
- 未出现把比赛中点球误译为“点球大战”的情况。
- 英文生成未混入中文。
- 中文翻译未大段复制英文。

## 样例节选

### storytelling_witty / U036

英文：

> Germany takes control in the final third, with a player in white advancing into the penalty area closely marked by defenders. He takes a shot from inside the box, and the goalkeeper in orange dives to make a save. The rebound falls to another German player who fires it into the net, beating the diving keeper.

中文：

> 德国队掌控了前场，一名白衣球员带球突入禁区，被防守队员紧紧盯防。他在禁区起脚射门，穿橙色球衣的门将奋力扑救。皮球反弹到另一名德国球员脚下，他果断补射破门，皮球越过倒地的门将入网。

### storytelling_witty / U149

英文：

> Germany take a penalty — Havertz steps up, the keeper dives, and it’s in! The net ripples, the scoreboard flips to 3-1, and the German players are already piling on the celebration.

中文：

> 德国队获得点球！哈弗茨主罚，门将飞身扑救，球进了！网窝颤动，记分牌变成3-1，德国队的球员们已经蜂拥而至庆祝。

### elite_broadcast_replay / U149

英文：

> Germany takes a penalty. The ball is struck with precision into the bottom corner. The goalkeeper dives but cannot reach it. Goal for Germany! The scoreboard updates to 3-1 as the German players celebrate their lead. In the replay, we can see the technique of the shot—perfect placement and power.

中文：

> 德国队获得点球！皮球精准地打入球门死角。门将奋力扑救，但未能触及皮球。德国队进球！比分更新为3-1，德国球员们庆祝他们的领先优势。在回放中，我们可以看到这脚射门的技术——完美的位置与力量。

## 风格观察

`storytelling_witty` 更强调现场故事、人群反应和有节奏的表达，适合演示和集锦。

`elite_broadcast_replay` 更像正式国际转播，会先给出直播结论，再补充回放中的技术细节，适合进球和关键攻防。

