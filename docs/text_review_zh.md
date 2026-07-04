# 非代码文本与配置参数审阅稿（中文）

本文用于人工审核当前世界杯视频解说 Harness 中会影响模型行为、用户配置和输出结构的非代码文本。当前运行时配置源主要来自 `configs/styles.json`、`configs/event_types.json`、`harness/scanner.py`、`harness/commentary.py`。

## 1. 审核范围

- 风格配置文本：风格名称、描述、prompt 注入文本、生成超参数。
- 事件类型文本：事件 ID、英文名称、英文判定描述、正例线索、反例线索。
- 扫描阶段 Prompt：低帧率图片窗口识别事件时发送给模型的说明。
- 修复阶段 Prompt：模型输出非法 JSON 或非法事件类型时的修复说明。
- 精细解说 Prompt：针对已识别事件生成解说片段时发送给模型的说明。
- 人工配置参数：manifest 格式、滑块参数、风格参数、事件类型参数、输出字段。

## 2. 风格配置（待审核）

### broadcast_professional：专业电视解说风

- 当前用途：稳定、准确、有电视转播感的通用解说。
- 当前参数：`temperature=0.35`，`top_p=0.9`，`max_tokens=1200`，`thinking_mode=false`。
- 当前英文 prompt 注入：

```text
Use a professional broadcast tone. Be accurate, concise, and smooth. Mention visible evidence and match context without exaggeration. Keep emotion controlled except for decisive moments.
```

- 中文审核含义：使用专业转播语气，准确、简洁、流畅。提及可见证据和比赛上下文，不夸张；除决定性时刻外控制情绪。

### short_passionate：激情短视频风

- 当前用途：适合短视频、高光片段和社交媒体传播。
- 当前参数：`temperature=0.65`，`top_p=0.95`，`max_tokens=900`，`thinking_mode=false`。
- 当前英文 prompt 注入：

```text
Use a high-energy short-video tone. Sentences should be punchy, vivid, and rhythmic. Highlight dramatic moments quickly. Do not invent facts; make the visible action feel exciting.
```

- 中文审核含义：使用高能短视频语气，句子有冲击力、画面感和节奏感。快速突出戏剧性时刻。不编造事实，让可见动作更有激情。

### tactical_analysis：战术复盘分析风

- 当前用途：适合赛后分析、技战术复盘、较理性的讲解。
- 当前参数：`temperature=0.25`，`top_p=0.85`，`max_tokens=1400`，`thinking_mode=false`。
- 当前英文 prompt 注入：

```text
Use a tactical analyst tone. Focus on spacing, transitions, defensive shape, passing lanes, pressure, and decision-making. Keep emotion secondary to explanation.
```

- 中文审核含义：使用战术分析师语气。重点关注空间、攻防转换、防守阵型、传球线路、压迫和决策质量。情绪表达服从解释。

## 3. 事件类型与英文判定描述（待审核）

所有事件类型均配置在 `configs/event_types.json`。模型扫描时只能输出这些 `id`，否则会触发修复或失败记录。

### goal

- 中文名称：进球
- 英文描述：The ball appears to cross the goal line, the scoreboard changes, or players clearly celebrate a scored goal.
- 正例线索：球在网内或门线后；门将被击败；球员冲出庆祝；比分牌增加；进球回放。
- 反例线索：结果未明的普通射门；差点进球；扑救后没有明确庆祝。

### shot

- 中文名称：射门
- 英文描述：A player attempts to score by striking, heading, or redirecting the ball toward goal, but the frame does not prove it became a goal.
- 正例线索：射门身体姿态；球飞向球门；头球攻门；防守球员或门将对射门作出反应。
- 反例线索：普通传球或传中；已经确认进球；远离球门的普通控球。

### save

- 中文名称：扑救/关键封堵
- 英文描述：The goalkeeper or a defender prevents a likely goal or blocks a clear shot near the goal.
- 正例线索：门将飞身或伸展扑救；球在球门附近被挡出；门线解围；门将触球后形成二点球。
- 反例线索：无压力的常规接球；射偏且无人触碰；已经进球。

### dangerous_attack

- 中文名称：危险进攻
- 英文描述：An attacking team is in or near the final third with a promising chance, but no specific shot, goal, set piece, or foul is clearly shown.
- 正例线索：快速反击；进攻球员进入禁区；禁区附近人数优势；直塞打身后；向密集区域传中。
- 反例线索：中场慢速组织；死球重开；已经是明确射门或进球。

### corner

- 中文名称：角球
- 英文描述：A corner kick is being taken, prepared, or replayed.
- 正例线索：球放在角旗区；大量球员在禁区等待角球；角旗在重开画面中可见。
- 反例线索：靠近角旗的运动战传中；界外球；边路任意球。

### free_kick

- 中文名称：任意球
- 英文描述：A free kick restart is being prepared or taken outside the penalty spot context.
- 正例线索：犯规后球静止；人墙；裁判管理重开；主罚球员站在球前。
- 反例线索：角球；点球；运动战传球。

### penalty

- 中文名称：点球
- 英文描述：A penalty kick is awarded, prepared, taken, saved, or scored.
- 正例线索：球在点球点；单个主罚者面对门将；其他球员在禁区外；裁判点球手势。
- 反例线索：禁区外任意球；运动战射门；角球。

### foul

- 中文名称：犯规
- 英文描述：Illegal physical contact, a trip, push, handball, or another stoppage-causing infringement is visible or strongly indicated.
- 正例线索：接触后球员倒地；裁判鸣哨或手势；球员抗议；铲到对手。
- 反例线索：正常身体对抗；球员自己滑倒；只看到出牌但没有犯规上下文。

### card

- 中文名称：黄牌/红牌
- 英文描述：The referee shows or is clearly about to show a yellow or red card.
- 正例线索：黄牌可见；红牌可见；裁判高举牌；球员纪律处罚反应。
- 反例线索：没有出牌的普通犯规；换人牌；比分图形。

### substitution

- 中文名称：换人
- 英文描述：A player substitution is happening or clearly displayed.
- 正例线索：换人牌；球员在边线进出场；转播换人图形；教练迎接下场球员。
- 反例线索：治疗但没有换人；只是热身。

### var_review

- 中文名称：VAR 审核
- 英文描述：A VAR review, referee monitor check, or broadcast VAR decision sequence is visible.
- 正例线索：VAR 图形；裁判看场边屏幕；审核完成或判罚图形；球员等待审核。
- 反例线索：没有 VAR 上下文的普通回放；普通裁判讨论。

### celebration_or_replay

- 中文名称：庆祝或回放
- 英文描述：A celebration, emotional reaction, or replay of an important moment is shown when the exact live event type is not clear.
- 正例线索：球员集体庆祝；观众庆祝；慢动作回放角度；情绪特写。
- 反例线索：能明确分类的实时进攻；与比赛无关的普通观众镜头。

### period_transition

- 中文名称：比赛阶段切换
- 英文描述：Kickoff, halftime, full-time, restart after halftime, or another major match-period transition is shown.
- 正例线索：球员准备开球；裁判开始或结束半场；半场或终场图形；球队进出场。
- 反例线索：犯规后的普通重开；随机中场控球。

### other_relevant

- 中文名称：其他重要事件
- 英文描述：A clearly commentary-worthy football moment that does not fit any other configured event type.
- 正例线索：伤病治疗；重要战术指令；特殊转播图形；重要观众席或替补席反应。
- 反例线索：普通控球；画面不清；信息量低的场景。

### no_event

- 中文名称：无重要事件
- 英文描述：No commentary-worthy football event is visible in the frame.
- 正例线索：普通推进；静态中场控球；画面不清或信息量低；无明显动作的转播镜头。
- 反例线索：明确进球；明确射门；明确定位球；可见出牌或换人。

## 4. 扫描阶段 Prompt（中文审核版）

该 Prompt 用于低帧率滑块扫描。真实运行时使用英文，下面是中文审核含义：

```text
你是一个足球视频事件扫描器。

风格上下文仅用于判断哪些内容更值得解说：
{style.prompt_injection}

允许的 event_type 值：
{allowed_types}

事件定义和判定线索：
{event_reference}

对每一帧，判断它是否包含需要解说的时刻。
event_type 必须严格等于允许值之一。没有重要内容时使用 no_event。

帧时间前缀：
{prefixes}

只返回 JSON，格式如下：
{
  "frames": [
    {
      "frame_id": "same frame_id",
      "needs_commentary": true,
      "event_type": "goal",
      "confidence": 0.0,
      "evidence": "short visual evidence"
    }
  ]
}
```

## 5. 修复阶段 Prompt（中文审核版）

该 Prompt 用于模型返回非法 JSON、未知事件类型、未知 frame_id 时的一次修复。

```text
把这个足球事件扫描结果修复为合法 JSON。
错误：{error}
允许的 event_type 值：{event_types}
事件定义和判定线索：
{event_reference}
必需的 frame_id：{frame_ids}

错误响应：
{bad_text}

只返回同样 schema 的 JSON：
{"frames":[{"frame_id":"...","needs_commentary":false,"event_type":"no_event","confidence":0.0,"evidence":"..."}]}
```

## 6. 精细解说生成 Prompt（中文审核版）

该 Prompt 用于根据已识别事件生成对应解说文本。

```text
你正在为一个已检测到的足球事件生成解说。

严格使用这个风格：
{style.prompt_injection}

解说必须适配从 {start_time} 到 {end_time} 的时间区间。
不要编造事件证据中不存在的球员名、球队名、比分或事实。

事件数据：
{event_json}

只返回 JSON：
{
  "commentary_text": "spoken commentary text",
  "subtitle_lines": [
    {"start_sec": 0.0, "end_sec": 2.0, "text": "subtitle text"}
  ]
}
```

## 7. 需要重点审核的配置参数

### 环境变量

| 参数 | 默认值 | 用途 | 是否建议改 |
|---|---|---|---|
| `INTERN_API_KEY` | 无 | Intern-S2-Preview API Key | 必填 |
| `INTERN_BASE_URL` | `https://chat.intern-ai.org.cn/api/v1` | API base URL | 一般不改 |
| `INTERN_MODEL` | `intern-s2-preview` | 模型名 | 一般不改 |

### 风格参数

| 参数 | 当前含义 | 审核建议 |
|---|---|---|
| `style_id` | 风格唯一 ID | 保持英文小写加下划线 |
| `description` | 风格说明 | 给人看，可中英文都维护 |
| `prompt_injection` | 实际注入模型的风格控制文本 | 重点审核 |
| `temperature` | 创造性/随机性 | 短视频可高，战术分析应低 |
| `top_p` | 采样范围 | 通常 0.85 到 0.95 |
| `max_tokens` | 单次输出上限 | 解说越长越高 |
| `thinking_mode` | 是否开启深度思考 | 当前默认关闭，避免输出思考过程 |

### 扫描参数

| 参数 | 默认值 | 作用 | 调参建议 |
|---|---:|---|---|
| `window_size_frames` | 6 | 每次让模型读取多少帧 | 越大越省调用，但边界更粗 |
| `stride_frames` | 3 | 滑块每次移动多少帧 | 越小越稳，但调用更多 |
| `repair_attempts` | 1 | 非法输出后修复次数 | 通常 1 次够用 |
| `event_types_path` | `None` | 自定义事件类型配置路径 | 有自定义分类时填写 |
| `merge_gap_sec` | 4.0 | 同类型事件候选的最大合并间隔 | 解决滑块切分导致的同一事件断裂 |
| `goal_replay_merge_gap_sec` | 30.0 | 进球与后续庆祝/回放的最大合并间隔 | 用于生成“进球 + 回放”的复合事件 |

### Manifest 字段

| 字段 | 类型 | 用途 |
|---|---|---|
| `video_id` | string | 视频唯一标识 |
| `source_video` | string | 原视频文件名或来源 |
| `frames[].frame_id` | string | 帧唯一 ID |
| `frames[].path` | string | 帧图路径，相对路径按 manifest 所在目录解析 |
| `frames[].timestamp_sec` | number | 帧对应视频秒数 |

### 输出字段

| 输出 | 关键字段 | 用途 |
|---|---|---|
| `events.json` | `event_id/event_type/start_sec/end_sec/evidence_frames/confidence/evidence_summary/phases` | 事件证据链 |
| `commentary.json` | `event_id/talk_start_sec/talk_end_sec/commentary_text/subtitle_lines` | 解说与字幕候选 |

### 复合事件 phases

`goal` 事件现在可能包含多个阶段：

```json
{
  "event_type": "goal",
  "phases": [
    {"phase_type": "live_goal", "start_sec": 80.0, "end_sec": 92.0},
    {"phase_type": "replay", "start_sec": 96.0, "end_sec": 116.0}
  ]
}
```

精细解说生成时，如果发现 `goal` 同时包含 `live_goal` 和 `replay`，会要求模型先描述实时进球，再利用回放阶段补充射门线路、传球、跑位、防守和门将反应等可见细节。

## 8. 建议你审核时重点看

- 事件类型是否够用：是否要加 `offside`、`injury`、`kickoff`、`goal_kick`、`throw_in`。
- `goal` 与 `celebration_or_replay` 是否会混：如果你希望庆祝全部归到进球后处理，需要调整描述。
- `shot` 与 `dangerous_attack` 的边界是否符合你的预期。
- 三种风格是否满足展示需求：是否要加“央视正式风”“B站二创风”“詹俊式激情风”等自定义风格。
- 扫描默认 `6/3` 是否适合你准备的切帧间隔。如果帧间隔是 2 秒，默认窗口覆盖约 12 秒，每步约 6 秒。
