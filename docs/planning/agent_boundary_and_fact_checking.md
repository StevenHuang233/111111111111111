# Agent Boundary And Fact Checking / Agent 边界与事实核实

Last updated: 2026-07-04

## Two Agents / 两类 Agent

| Type | EN | ZH |
| --- | --- | --- |
| Collaboration coding agent | Helps the team write docs, code, plans, scripts, and retrospectives. Examples: Codex, GPT, Claude. | 帮团队写文档、代码、计划、脚本和复盘的协作型 coding agent，例如 Codex、GPT、Claude。 |
| Target task agent | The submitted World Cup commentary harness that uses Intern-S2-Preview as the core model. | 最终提交的世界杯解说 Harness，核心模型调用必须是 Intern-S2-Preview。 |

## Shared Lessons / 可复用经验

EN: Problems found in collaboration can become design requirements for the target harness.

ZH: 协作过程中遇到的问题，可以反向转化为目标 Harness 的设计要求。

| Collaboration Issue | Target Harness Requirement |
| --- | --- |
| Git object database grew unexpectedly. / Git object 异常膨胀。 | Large media must stay outside Git; add ignore rules and size guards. / 大媒体必须在 Git 外；加入 ignore 和 size guard。 |
| Assistant can over-assume facts. / AI 容易过度假设事实。 | Unsupported facts must be flagged and verified. / 无依据事实必须标记和核验。 |
| Long context wastes tokens. / 长上下文浪费 token。 | Use progressive disclosure and summaries. / 使用渐进披露和摘要。 |
| Paths and local resources differ by machine. / 路径和本地资源因机器不同而变化。 | Use `.env` configuration and manifests. / 使用 `.env` 配置和 manifest。 |

## Fact Policy / 事实策略

EN: If a fact is missing, the agent must search, ask, or mark it unknown. It must not invent details.

ZH: 缺事实时，Agent 必须搜索、询问或标注未知，不能无中生有。

Allowed sources / 可用事实来源:

- EN: Visible scoreboard, extracted frames, official task statement, user-provided notes, reliable public search, or manually verified annotations.
- ZH: 画面比分牌、抽帧、官方题面、用户提供信息、可靠公开搜索、人工核验标注。

Unsupported claims to block / 必须阻止的无依据说法:

- EN: Player names not visible or provided.
- ZH: 未在画面或资料中出现的人名。
- EN: Tactical statistics such as possession unless measured or sourced.
- ZH: 未测量或无来源的控球率等战术统计。
- EN: Referee decisions or foul causes not visible in evidence.
- ZH: 证据中看不出的判罚原因或犯规细节。

## Time Policy / 时间策略

EN: Use two time systems.

ZH: 使用两套时间系统。

| Time Type | EN | ZH |
| --- | --- | --- |
| Video time | Starts at 00:00:00 of the MP4 file. Frame index maps to this time. | 从 MP4 文件 00:00:00 开始。帧编号映射到这个时间。 |
| Match clock | The clock shown on the broadcast scoreboard, such as 47:17 +4. | 转播比分牌上的比赛计时，例如 47:17 +4。 |

Mapping rule / 映射规则:

- EN: `video_seconds = frame_id / extracted_fps`. For current extraction, `video_seconds = frame_id / 4`.
- ZH: `视频秒数 = 帧号 / 抽帧帧率`。当前抽帧为 4fps，所以 `视频秒数 = 帧号 / 4`。

## Commentary Scene Types / 解说场景类型

The harness should distinguish these scene types before writing:

Harness 在生成解说前应区分以下场景：

- Kickoff and opening atmosphere / 开场与现场氛围
- Normal possession / 常规控球
- Attacking build-up / 进攻推进
- Defensive block / 防守站位
- Shot or save / 射门或扑救
- Goal / 进球
- Replay / 回放
- Referee decision / 判罚
- Foul or injury / 犯规或受伤
- Player close-up / 人物特写
- Substitution or stoppage / 换人或比赛中断
- Tempo shift / 比赛节奏变化
- Closing summary / 阶段总结或收尾

Advanced claims such as possession rate, tempo, or tactical dominance must be measured, estimated with evidence, or marked as qualitative.

控球率、节奏、战术压制等进阶判断必须有测量、证据化估计，或明确标注为定性判断。

