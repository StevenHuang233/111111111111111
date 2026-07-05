# Quality Acceptance Standards / 质量验收标准

EN: This document records what the quality gates check, where the code lives, and which parts are rule-based versus API-assisted.

ZH: 本文记录质量门禁检查什么、代码在哪里，以及哪些部分是规则型、哪些部分可调用 API 辅助。

## Source / 来源

EN: The current gates are project-defined engineering gates written by the team, not an official competition scoring script. They are based on video-derived scoreboard review, public/evaluation-only facts, and conservative text checks.

ZH: 当前门禁是团队自定义工程验收门禁，不是官方比赛评分脚本。标准来自视频比分牌人工核验、仅用于评测的公开事实，以及保守文本检查。

## Scripts / 脚本

| Script | Purpose / 用途 | Standard / 标准 |
| --- | --- | --- |
| `tools/evaluate_commentary_quality.py` | General final-output quality gate. / 通用终稿质量门禁。 | Goal count, score claims, wrong entities, unsupported names, pre-kickoff action errors, mixed language, color-identity wording. / 进球数、比分声明、错误实体、无依据姓名、开球前动作误判、中英混杂、颜色式身份描述。 |
| `tools/compare_goal_timeline.py` | Goal/score timeline alignment. / 进球与比分时间线对齐。 | Every verified score change must be covered; no extra goal assertions; no duplicate goal groups. / 每个已核验比分变化都要覆盖；不能有额外进球断言；不能重复。 |
| `tools/audit_identity_style.py` | Identity and broadcast style gate. / 身份与解说风格门禁。 | Wrong team/entity and unsupported names must be zero; color/raw visual wording should stay low. / 错误球队/实体和无依据姓名必须为 0；颜色式、原始画面式描述应尽量低。 |
| `tools/run_evaluation_gates.py` | Aggregated acceptance runner. / 汇总验收入口。 | Aggregates the three gates above. / 汇总上述三类门禁。 |
| `tools/postprocess_goal_reflection.py` | Post-generation goal reflection and correction. / 生成后进球反思与修正。 | Keep only one primary segment per verified score change; rewrite false goal claims as replay, shot, or dangerous attack; optionally attach Intern-S2 API visual review. / 每个已核验比分变化只保留一个主进球片段；将误判进球改写为回放、射门或危险进攻；可选追加 Intern-S2 API 视觉复核。 |

## Current Night Result / 当前 Night 结果

Input / 输入:

- `outputs/commentary_bilingual-night.json`
- `outputs/events-night.json`

Postprocessed output / 后处理输出:

- `reference/evaluation/night_reflection/commentary_bilingual-night_reflected.json`

Latest aggregate result / 最新汇总结果:

- `reference/evaluation/night_reflection/final_evaluation_gates-night-after.md`
- overall status: `pass_with_warnings`

Key metrics after reflection / 反思后关键指标:

- verified score changes / 已核验比分变化: `8`
- generated goal type segments / 生成 goal 类型片段: `8`
- generated goal assertion segments / 生成进球断言片段: `8`
- covered verified goals / 覆盖真实进球: `8`
- missing verified goals / 漏掉真实进球: `0`
- extra goal assertions / 额外进球断言: `0`
- wrong entity segments / 错误实体: `0`
- unsupported name segments / 无依据姓名: `0`
- remaining warning / 剩余警告: raw visual wording `21`

## API-Assisted Reflection / API 辅助反思

EN: The deterministic run does not require API calls. To use Intern-S2-Preview as a verifier on suspicious segments, pass `--api-mode review`, `--frame-root`, and a bounded `--max-api-calls`.

ZH: 确定性运行不需要 API。若要让 Intern-S2-Preview 对可疑片段做视觉复核，传入 `--api-mode review`、`--frame-root` 和受控的 `--max-api-calls`。

```powershell
python reference/evaluation/tools/postprocess_goal_reflection.py `
  --input outputs/commentary_bilingual-night.json `
  --events outputs/events-night.json `
  --output reference/evaluation/night_reflection/commentary_bilingual-night_reflected.json `
  --report-json reference/evaluation/night_reflection/goal_reflection_report.json `
  --report-md reference/evaluation/night_reflection/goal_reflection_report.md `
  --api-mode review `
  --frame-root E:\worldcup_data\frames_4fps_q3 `
  --max-api-calls 8 `
  --api-concurrency 2
```

EN: The API path is intentionally bounded for cost control. If API/network fails, the deterministic scoreboard-state pass still produces a usable correction.

ZH: API 路径有调用上限，用于控制成本。如果 API 或网络失败，确定性的比分状态后处理仍能产出可用修正版。
