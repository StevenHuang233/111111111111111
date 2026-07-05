# V11 Final Reflection Evaluation / V11 最终反思验收记录

EN: This folder records the acceptance loop for `commentary_bilingual-final-V11-unreflected.json`: evaluate before reflection, apply goal/reflection post-processing, evaluate again, then export SRT files.

中文：本目录记录 `commentary_bilingual-final-V11-unreflected.json` 的验收闭环：反思前检测、进球反思修正、反思后复检、导出 SRT。

## Inputs And Outputs / 输入与输出

- Input commentary / 输入解说：`outputs/commentary_bilingual-final-V11-unreflected.json`
- Event reference / 事件参考：`outputs/events-night.json`
- Manual verified scoreboard reference / 人工核验比分参考：`reference/evaluation/goal_scoreboard_manual_review.md`
- Reflected commentary / 反思后解说：`outputs/commentary_bilingual-final-V11-reflected.json`
- SRT output directory / SRT 输出目录：`outputs/srt/final_V11_reflected/`

`outputs/` is ignored by Git. The committed files in this directory are acceptance reports and reproducibility records, not the large runtime outputs.

中文：`outputs/` 默认被 Git 忽略。本目录提交的是验收报告和复现记录，不是大体量运行产物。

## Commands / 复现命令

Run from the repository root:

```powershell
$PY = "E:/conda/envs/ailab-hackathon/python.exe"

& $PY -B reference/evaluation/tools/evaluate_commentary_quality.py `
  --input outputs/commentary_bilingual-final-V11-unreflected.json `
  --output-json reference/evaluation/final_reflection_v11/commentary_quality_eval-v11-before.json `
  --output-md reference/evaluation/final_reflection_v11/commentary_quality_eval-v11-before.md

& $PY -B reference/evaluation/tools/compare_goal_timeline.py `
  --input outputs/commentary_bilingual-final-V11-unreflected.json `
  --output-json reference/evaluation/final_reflection_v11/goal_timeline_alignment-v11-before.json `
  --output-md reference/evaluation/final_reflection_v11/goal_timeline_alignment-v11-before.md

& $PY -B reference/evaluation/tools/audit_identity_style.py `
  --input outputs/commentary_bilingual-final-V11-unreflected.json `
  --output-json reference/evaluation/final_reflection_v11/identity_style_audit-v11-before.json `
  --output-md reference/evaluation/final_reflection_v11/identity_style_audit-v11-before.md

& $PY -B reference/evaluation/tools/run_evaluation_gates.py `
  --input outputs/commentary_bilingual-final-V11-unreflected.json `
  --output-json reference/evaluation/final_reflection_v11/final_evaluation_gates-v11-before.json `
  --output-md reference/evaluation/final_reflection_v11/final_evaluation_gates-v11-before.md

& $PY -B reference/evaluation/tools/postprocess_goal_reflection.py `
  --input outputs/commentary_bilingual-final-V11-unreflected.json `
  --events outputs/events-night.json `
  --manual-review reference/evaluation/goal_scoreboard_manual_review.md `
  --output outputs/commentary_bilingual-final-V11-reflected.json `
  --report-json reference/evaluation/final_reflection_v11/goal_reflection_report-v11.json `
  --report-md reference/evaluation/final_reflection_v11/goal_reflection_report-v11.md

& $PY -B reference/evaluation/tools/evaluate_commentary_quality.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-json reference/evaluation/final_reflection_v11/commentary_quality_eval-v11-after.json `
  --output-md reference/evaluation/final_reflection_v11/commentary_quality_eval-v11-after.md

& $PY -B reference/evaluation/tools/compare_goal_timeline.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-json reference/evaluation/final_reflection_v11/goal_timeline_alignment-v11-after.json `
  --output-md reference/evaluation/final_reflection_v11/goal_timeline_alignment-v11-after.md

& $PY -B reference/evaluation/tools/audit_identity_style.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-json reference/evaluation/final_reflection_v11/identity_style_audit-v11-after.json `
  --output-md reference/evaluation/final_reflection_v11/identity_style_audit-v11-after.md

& $PY -B reference/evaluation/tools/run_evaluation_gates.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-json reference/evaluation/final_reflection_v11/final_evaluation_gates-v11-after.json `
  --output-md reference/evaluation/final_reflection_v11/final_evaluation_gates-v11-after.md

& $PY -B scripts/export_commentary_srt.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-dir outputs/srt/final_V11_reflected `
  --text-source both `
  --languages all
```

## Result Summary / 结果摘要

| Metric / 指标 | Before / 反思前 | After / 反思后 |
| --- | ---: | ---: |
| Overall gate / 总门禁 | fail | pass_with_warnings |
| Generated goal type segments / 生成 goal 类型段 | 23 | 8 |
| Verified goals / 已核验真实进球 | 8 | 8 |
| Goal overcount / 进球过计数 | 15 | 0 |
| Goal assertion segments / 进球断言段 | 43 | 8 |
| Extra goal assertions / 额外进球断言 | 30 | 0 |
| Duplicate verified goal groups / 重复进球组 | 4 | 0 |
| Missing verified goals / 漏掉真实进球 | 0 | 0 |
| Unsupported name segments / 未支撑姓名段 | 1 | 0 |
| Mixed language segments / 混杂语言段 | 2 | 0 |
| Raw visual segments / 原始画面描述段 | 44 | 43 |

The reflection module rewrote `53` false-positive goal-related segments and kept `8` primary verified goal segments.

中文：反思模块改写了 `53` 个假阳性进球相关片段，并保留 `8` 个主要已核验进球片段。

## SRT Files / SRT 文件

- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.subtitle.zh.srt`
- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.subtitle.en.srt`
- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.subtitle.bilingual.srt`
- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.commentary.zh.srt`
- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.commentary.en.srt`
- `outputs/srt/final_V11_reflected/commentary_bilingual-final-V11-reflected.commentary.bilingual.srt`

## Remaining Risk / 剩余风险

- EN: The final gate still has a warning for raw visual wording. It is not a factual blocker, but some lines may still sound like visual notes rather than polished broadcast commentary.
- 中文：最终门禁仍提示部分原始画面描述。这不是事实阻塞问题，但个别语句可能仍像画面笔记，不够像最终播报解说。
- EN: Score verification currently depends on the manually reviewed scoreboard timeline plus event text. If judges require full automation, the next improvement is OCR/vision-based scoreboard change detection.
- 中文：比分核验目前依赖人工核验比分时间线与事件文本。如果评审要求更强自动化，下一步应补 OCR/视觉比分变化检测。
