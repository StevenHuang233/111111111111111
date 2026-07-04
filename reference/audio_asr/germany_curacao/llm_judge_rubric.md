# LLM Judge Rubric / 大模型分级评判指南

Reference files / 参考文件:

- `德国_库拉索.audio_reference.srt`
- `德国_库拉索.audio_reference.segments.json`

Audio ASR is a reference signal, not the sole gold answer.

中文：音频字幕是参考信号，不是唯一标准答案。目标 agent 是通过抽帧图片识别关键事件并生成解说，所以评判必须区分：

- visual-evident facts / 画面可见事实
- audio-only hints / 只有音轨中出现的信息
- unsupported hallucinations / agent 自己虚构的信息

## Suggested Dimensions / 建议维度

Score each from 0 to 5:

1. visual_event_grounding / 画面事件扎根度
2. audio_reference_consistency / 音频参考一致性
3. timestamp_usefulness / 时间戳可用性
4. commentary_quality / 中文解说质量
5. factual_safety / 事实安全
6. harness_improvement_signal / 对 harness 改进的帮助

## Failure Categories / 失败类别

- missed_key_event
- timestamp_drift
- hallucinated_entity
- weak_scene_type
- style_too_flat
- audio_only_gap
- verifier_gap
