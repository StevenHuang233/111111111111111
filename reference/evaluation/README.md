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
| `tools/audit_commentary_output.py` | Script that audits generated commentary against public facts and ASR weak signals. | 将生成解说与公开事实、ASR 弱信号对比的脚本。 |
