# Evaluation References / 验证参考资料

This directory is for evaluating the target harness. It is not target-agent context.

本目录用于评估目标 Harness，不是目标 Agent 的上下文。

## Rule / 规则

EN: Public match facts, ASR transcripts, and audit reports can guide verification and harness improvement. They must not be silently injected into the visual commentary generation prompt because the judged task should still rely on Intern-S2-Preview plus the provided video/frame evidence.

ZH: 公开比赛事实、ASR 字幕和审计报告可以指导验证和 Harness 改进，但不能悄悄注入视觉解说生成 prompt，因为验收任务仍应基于 Intern-S2-Preview 和给定视频/帧证据。

## Files / 文件

| File | EN | ZH |
| --- | --- | --- |
| `germany_curacao_public_reference.json` | Evaluation-only public facts and expected goal sequence. | 仅用于验证的公开事实和预期进球顺序。 |
| `goal_scoreboard_manual_review.md` | Manual 4fps scoreboard review for live score changes. | 基于 4fps 抽帧的现场比分变化人工核验。 |
| `goal_timeline_alignment.md` | Aligns generated goal claims with verified scoreboard changes. | 将生成进球声明与已核验比分变化对齐。 |
| `identity_style_audit.md` | Audits supported identity wording and natural broadcast style. | 审计身份措辞依据和自然解说风格。 |
| `commentary_quality_eval.md` | Latest quality metrics, issue samples, and improvement suggestions for `outputs/commentary_bilingual.json`. | 对 `outputs/commentary_bilingual.json` 的最新质量指标、问题样例和改进建议。 |
| `final_evaluation_gates.md` | Aggregates quality, goal alignment, and identity/style gates. | 汇总质量、进球对齐、身份与风格三类门禁。 |
| `revision_queue.md` | Prioritized rewrite/suppression queue built from gate failures. | 从门禁失败项生成的重写/抑制优先级队列。 |
| `commentary_revision_annotations.md` | Final-output segments annotated with blocker/warning/clear status and safe-use policy. | 给终稿片段标注阻塞、警告、可保留状态和安全使用策略。 |
| `tools/audit_commentary_output.py` | Script that audits generated commentary against public facts and ASR weak signals. | 将生成解说与公开事实、ASR 弱信号对比的脚本。 |
| `tools/run_evaluation_gates.py` | One-command final evaluation gate runner. | 一条命令运行全部终稿评测门禁。 |
| `tools/build_revision_queue.py` | Converts gate reports into concrete segment-level fix actions. | 将门禁报告转换成具体片段级修订动作。 |
| `tools/annotate_commentary_for_revision.py` | Merges the revision queue back into commentary JSON for human/agent correction. | 将修订队列合并回解说 JSON，供人工或修订 Agent 使用。 |
| `tools/evaluate_commentary_quality.py` | General quality evaluator for bilingual commentary JSON. | 面向双语解说 JSON 的通用质量评测脚本。 |
| `tools/compare_goal_timeline.py` | Goal/score assertion alignment gate. | 进球/比分声明时间线对齐门禁。 |
| `tools/audit_identity_style.py` | Identity support and broadcast-style wording gate. | 身份依据与解说风格措辞门禁。 |
| `tools/build_goal_frame_checklist.py` | Converts ASR goal candidates into 4fps frame probes and bisection protocol. | 将 ASR 进球候选转成 4fps 帧探针和二分核验流程。 |
| `tools/build_frame_contact_sheets.py` | Builds local ignored PNG contact sheets from extracted frames. | 从本地抽帧生成被 Git 忽略的 PNG 拼图，方便人工核验。 |

## Teacher-Testable Entry / 老师可测试入口

Run all final-output gates / 运行全部终稿门禁：

```powershell
python reference/evaluation/tools/run_evaluation_gates.py `
  --input outputs/commentary_bilingual.json `
  --output-json reference/evaluation/final_evaluation_gates.json `
  --output-md reference/evaluation/final_evaluation_gates.md `
  --fail-on-any
```

EN: Exit code `2` means at least one final-output gate failed.

ZH: 退出码 `2` 表示至少一个终稿门禁未通过。

Build the actionable revision queue / 生成可执行修订队列：

```powershell
python reference/evaluation/tools/build_revision_queue.py `
  --output-json reference/evaluation/revision_queue.json `
  --output-md reference/evaluation/revision_queue.md
```

EN: Fix `Must` items first, then rerun `run_evaluation_gates.py --fail-on-any`.

ZH: 先处理 `Must` 项，再重新运行 `run_evaluation_gates.py --fail-on-any`。

Annotate the generated commentary with safe-use policies / 给生成解说标注安全使用策略：

```powershell
python reference/evaluation/tools/annotate_commentary_for_revision.py `
  --input outputs/commentary_bilingual.json `
  --queue reference/evaluation/revision_queue.json `
  --output-json reference/evaluation/commentary_revision_annotations.json `
  --output-md reference/evaluation/commentary_revision_annotations.md
```

EN: `blocker` segments must be suppressed, rewritten, or manually accepted before final demo packaging.

ZH: `blocker` 片段必须被抑制、重写或人工确认接受后，才能进入最终 demo 打包。

Generate a report / 生成报告：

```powershell
python reference/evaluation/tools/evaluate_commentary_quality.py `
  --input outputs/commentary_bilingual.json `
  --output-json reference/evaluation/commentary_quality_eval.json `
  --output-md reference/evaluation/commentary_quality_eval.md
```

Use it as a final-output gate / 作为终稿质量门禁：

```powershell
python reference/evaluation/tools/evaluate_commentary_quality.py `
  --input outputs/commentary_bilingual.json `
  --fail-on-gate
```

EN: Exit code `2` means the generated commentary should not be used as the final demo script without manual review.

ZH: 退出码 `2` 表示生成解说不应未经人工复核直接作为最终 demo 稿。

Align generated goals with verified score changes / 对齐生成进球与已核验比分变化：

```powershell
python reference/evaluation/tools/compare_goal_timeline.py `
  --input outputs/commentary_bilingual.json `
  --output-json reference/evaluation/goal_timeline_alignment.json `
  --output-md reference/evaluation/goal_timeline_alignment.md
```

Use it as a key-event gate / 作为关键事件门禁：

```powershell
python reference/evaluation/tools/compare_goal_timeline.py `
  --input outputs/commentary_bilingual.json `
  --fail-on-alignment
```

EN: Exit code `2` means generated goal/score assertions are missing, duplicated, or not aligned with verified scoreboard changes.

ZH: 退出码 `2` 表示生成的进球/比分声明存在漏报、重复或无法对齐已核验比分变化。

Audit identity wording and broadcast style / 审计身份措辞与解说风格：

```powershell
python reference/evaluation/tools/audit_identity_style.py `
  --input outputs/commentary_bilingual.json `
  --output-json reference/evaluation/identity_style_audit.json `
  --output-md reference/evaluation/identity_style_audit.md
```

Use it as an identity/style gate / 作为身份与风格门禁：

```powershell
python reference/evaluation/tools/audit_identity_style.py `
  --input outputs/commentary_bilingual.json `
  --fail-on-style
```

EN: Exit code `2` means unsupported names or wrong teams remain; warnings mean the output still sounds like raw visual description.

ZH: 退出码 `2` 表示仍有无依据姓名或错误球队；warning 表示文本仍偏向原始画面描述。

Python API / Python 接口：

```python
from reference.evaluation.tools.evaluate_commentary_quality import evaluate_commentary_quality

report = evaluate_commentary_quality("outputs/commentary_bilingual.json")
```
