# Audio Reference Notes / 音频参考说明

Last updated: 2026-07-04

## What Was Added / 已加入内容

EN: The repository now tracks an audio ASR reference package under `reference/audio_asr/germany_curacao/`. It contains 10-minute MP3 chunks, raw ASR JSON, SRT subtitles, structured segments, a timeline, weak goal-candidate windows, and an LLM judging rubric.

ZH: 仓库现在在 `reference/audio_asr/germany_curacao/` 下跟踪一份音频 ASR 参考包。它包含 10 分钟 MP3 分块、原始 ASR JSON、SRT 字幕、结构化片段、时间线、弱进球候选窗口和大模型评判 rubric。

## Why It Exists / 为什么需要

EN: The target agent is visual-first: it reads extracted frames and generates commentary for key visual events. The original broadcast audio is not the target output, but it can help evaluate whether important events were missed or whether generated timestamps are plausible.

ZH: 目标 Agent 是视觉优先：读取抽帧并针对关键视觉事件生成解说。原始转播音频不是目标输出，但它能帮助评估是否漏掉关键事件、生成时间戳是否合理。

## Evaluation Use / 评估用法

EN:

- Compare detected event windows against nearby audio references.
- Use `goal_candidate_windows.md` to prioritize visual verification of likely goals.
- Use ASR only as a weak signal because it has recognition errors.
- Let an LLM judge categorize differences into missed event, timestamp drift, hallucinated fact, style mismatch, or acceptable visual-only commentary.
- Feed these findings back into event detection prompts, verification rules, and commentary style settings.

ZH:

- 将检测到的事件窗口与附近音频参考对比。
- 使用 `goal_candidate_windows.md` 优先安排疑似进球的视觉核验。
- ASR 存在识别错误，只能作为弱信号。
- 让大模型把差异分类为漏事件、时间偏移、事实幻觉、风格不匹配或可接受的视觉独有解说。
- 将这些发现反馈到事件检测提示词、核验规则和解说风格配置。

## Environment Note / 环境说明

EN: The reference script copied into `reference/audio_asr/tools/` is dependency-light: Python standard library plus local `ffmpeg`. It does not require installing the full VideoCaptioner GUI stack. It uploads audio only with the explicit `--allow-upload` flag.

ZH: 复制到 `reference/audio_asr/tools/` 的参考脚本是轻依赖版本：只需 Python 标准库和本机 `ffmpeg`，不需要安装完整 VideoCaptioner GUI 依赖。只有显式传入 `--allow-upload` 才会上传音频。
