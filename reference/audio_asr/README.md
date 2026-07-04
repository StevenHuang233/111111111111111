# Audio ASR Reference / 音频字幕参考

This directory stores audio-transcription reference material for evaluating the World Cup commentary harness.

本目录存放世界杯解说 Harness 的音频字幕参考材料。

## Policy / 使用口径

EN: Audio ASR is only a reference signal. The target harness generates commentary from video frames and visual event evidence, so its output does not need to match the original broadcast audio line by line.

ZH: 音频 ASR 只是参考信号。目标 Harness 是从视频帧和视觉事件证据生成解说，因此输出不需要逐句对齐原始转播音频。

Use it mainly to check:

主要用于检查：

- whether important match events were missed;
- 是否漏掉关键比赛事件；
- whether generated timestamps are near plausible broadcast moments;
- 生成时间戳是否接近合理转播时刻；
- whether generated claims conflict with audio-visible context;
- 生成内容是否与音频可参考上下文冲突；
- where the harness should improve event detection, verification, or commentary style.
- Harness 应该在哪些事件检测、核验或解说风格上改进。

## Contents / 内容

| Path | EN | ZH |
| --- | --- | --- |
| `germany_curacao/chunks/` | 10-minute MP3 chunks used for ASR. | 用于 ASR 的 10 分钟 MP3 分块。 |
| `germany_curacao/raw_asr/` | Raw Bcut/Bijian ASR JSON responses. | Bcut/Bijian ASR 原始 JSON 响应。 |
| `germany_curacao/audio_reference.srt` | Timestamped subtitle reference. | 带时间戳字幕参考。 |
| `germany_curacao/audio_reference.segments.json` | Structured subtitle segments. | 结构化字幕段。 |
| `germany_curacao/audio_reference.timeline.md` | Human-readable timeline. | 可读时间线。 |
| `germany_curacao/llm_judge_rubric.md` | Rubric for later LLM-assisted evaluation. | 后续大模型辅助评判 rubric。 |
| `tools/worldcup_bcut_reference.py` | Reproduction script copied from the VideoCaptioner experiment. | 从 VideoCaptioner 实验复制来的复现脚本。 |

## Safety / 安全说明

EN: The included script follows the VideoCaptioner Bcut/Bijian ASR route and uploads audio chunks to a third-party cloud ASR service only when `--allow-upload` is explicitly supplied. Do not use it on private media without permission.

ZH: 这里的脚本沿用 VideoCaptioner 的 Bcut/Bijian ASR 路线，只有显式传入 `--allow-upload` 时才会把音频分块上传到第三方云端 ASR。未经允许不要用于私密媒体。

The full extracted audio file is intentionally not committed. Only small chunks and reference outputs are tracked.

完整抽取音频文件有意不入库。仓库只跟踪小分块和参考输出。
