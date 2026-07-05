# Nightwork 优化说明

本分支只做增量优化，不替换原有主流程。核心新增点是：

- 比赛关键信息注入：用 `MatchContext` 独立配置比赛双方、球衣颜色、队名别名和事实约束。
- 两种新增解说风格：`storytelling_witty` 与 `elite_broadcast_replay`。
- 风格实验脚本：不重跑粗扫，直接读取已有事件 JSON，快速比较不同风格的输出。
- 调参 preset：把常用参数集中写到 `configs/pipeline_presets.json`，便于审核和复用。

## 比赛关键信息注入

配置文件：

```text
configs/match_contexts.json
```

当前内置：

```text
germany_curacao_world_cup_2026
```

这个 context 会告诉模型：

- 比赛双方是 Germany 与 Curacao。
- 蓝黄球衣球队是 Curacao，不是 Colombia 或 Paraguay。
- 中文输出用“德国队”和“库拉索队”。
- 最终比分 metadata 是 Germany 7-1 Curacao，但只能作为一致性背景，不能替代画面证据。

使用方式：

```powershell
python run_full_bilingual_with_progress.py `
  --run-name "nightwork_context_full" `
  --match-context germany_curacao_world_cup_2026 `
  --coarse-only-generation `
  --verify-goals-with-model
```

如果不传 `--match-context`，所有旧逻辑保持原样。

## 新增风格

新增风格仍然在：

```text
configs/styles.json
```

### storytelling_witty

故事化、有人味、有一点轻幽默，适合黑客松演示或短片解说。但它不是短视频夸张风，要求幽默不能牺牲事实准确性。

### elite_broadcast_replay

高阶国际转播风，重点是“直播调用 + 回放解释”。适合进球、扑救、VAR、定位球等需要利用回放补充技术细节的场景。

## 快速风格实验

不用重新粗扫，直接读取已有事件结果：

```powershell
$env:INTERN_API_KEY="your_key"

python run_style_experiment.py `
  --events-json "outputs\coarse_new_boundary_20260704_223738\goal_validation\refined_events.json" `
  --event-ids U036,U149,U225 `
  --styles storytelling_witty,elite_broadcast_replay `
  --match-context germany_curacao_world_cup_2026 `
  --output-dir "outputs\nightwork_style_experiment"
```

输出：

```text
outputs/nightwork_style_experiment/storytelling_witty/commentary_bilingual.json
outputs/nightwork_style_experiment/elite_broadcast_replay/commentary_bilingual.json
outputs/nightwork_style_experiment/summary.md
outputs/nightwork_style_experiment/summary.json
```

## 便捷调参

常用参数集中在：

```text
configs/pipeline_presets.json
```

建议先审核这些字段：

- `style`
- `match_context`
- `event_ids`
- `commentary_sample_fps`
- `max_frames_per_event`
- `max_frames_per_phase`
- `concurrency`
- `request_stagger_sec`

当前脚本没有强制读取 preset 文件，preset 是审核和复用用的“参数清单”。如果要把 preset 变成自动执行入口，后续可以加一个 `--preset` 参数，不影响现有命令行。

## 回退方式

本分支新增功能都是可选项：

- 不传 `--match-context`，上下文注入关闭。
- 不使用新 style id，仍然使用原来的三种风格。
- 不运行 `run_style_experiment.py`，主流程不受影响。
- `main` 分支不包含这些 nightwork 增量，必要时可以直接切回 `main`。

