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
| `commentary_quality_eval.md` | Latest quality metrics, issue samples, and improvement suggestions for `outputs/commentary_bilingual.json`. | 对 `outputs/commentary_bilingual.json` 的最新质量指标、问题样例和改进建议。 |
| `tools/audit_commentary_output.py` | Script that audits generated commentary against public facts and ASR weak signals. | 将生成解说与公开事实、ASR 弱信号对比的脚本。 |
| `tools/evaluate_commentary_quality.py` | General quality evaluator for bilingual commentary JSON. | 面向双语解说 JSON 的通用质量评测脚本。 |
| `tools/build_goal_frame_checklist.py` | Converts ASR goal candidates into 4fps frame probes and bisection protocol. | 将 ASR 进球候选转成 4fps 帧探针和二分核验流程。 |
| `tools/build_frame_contact_sheets.py` | Builds local ignored PNG contact sheets from extracted frames. | 从本地抽帧生成被 Git 忽略的 PNG 拼图，方便人工核验。 |

## Teacher-Testable Entry / 老师可测试入口

```powershell
python reference/evaluation/tools/evaluate_commentary_quality.py `
  --input outputs/commentary_bilingual.json `
  --output-json reference/evaluation/commentary_quality_eval.json `
  --output-md reference/evaluation/commentary_quality_eval.md
```

Python API / Python 接口：

```python
from reference.evaluation.tools.evaluate_commentary_quality import evaluate_commentary_quality

report = evaluate_commentary_quality("outputs/commentary_bilingual.json")
```
