# Final Reflection And SRT Package / 最终反思与 SRT 打包

EN: This directory stores evaluation reports for the final reflected commentary package.

ZH: 本目录存放最终 reflected 解说包的评测报告。

## One-Shot Command / 一键命令

EN: The command below composes the latest night/final outputs without merging branches. It reads the unreflected final commentary, runs goal reflection, evaluates the result, exports SRT subtitles, and writes a manifest.

ZH: 以下命令不需要合并分支，只通过路径组合 night/final 最新输出。它读取未反思终稿，运行进球反思，评测结果，导出 SRT 字幕，并写出清单。

```powershell
python scripts/run_final_reflection_package.py `
  --input outputs/commentary_bilingual-final-unreflected.json `
  --events outputs/events-night.json `
  --reflected-output outputs/commentary_bilingual-final-reflected.json `
  --report-dir reference/evaluation/final_reflection `
  --srt-output-dir outputs/srt/final_reflected
```

## Outputs / 输出

| Path | EN | ZH |
| --- | --- | --- |
| `outputs/commentary_bilingual-final-reflected.json` | Final reflected commentary JSON. | 最终 reflected 解说 JSON。 |
| `outputs/srt/final_reflected/` | SRT exports for subtitle and full commentary text. | subtitle 与完整解说词两类 SRT 导出。 |
| `final_evaluation_gates-final-after.md` | Aggregate acceptance report. | 汇总验收报告。 |
| `goal_reflection_report-final.md` | Reflection changes and kept true goals. | 反思修改和保留真实进球报告。 |
| `final_reflection_package_manifest.md` | Package manifest with SRT file counts. | 打包清单，含 SRT 文件条数。 |

## Current Acceptance / 当前验收

EN: The latest reflected output passes goal alignment and has no blocker-level factual/entity failures. Remaining warnings are style-level.

ZH: 最新 reflected 输出通过进球对齐，没有 blocker 级事实/实体错误。剩余警告属于表达风格层面。
