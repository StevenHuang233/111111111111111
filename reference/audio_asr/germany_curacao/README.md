# Germany vs Curacao Audio Reference / 德国 vs 库拉索音频参考

Source video / 源视频：

```text
德国_库拉索.mp4
```

Generation time / 生成时间：

```text
2026-07-04 22:46:58 local
```

Summary / 摘要：

- EN: 2323 timestamped ASR subtitle segments were generated.
- ZH: 已生成 2323 条带时间戳 ASR 字幕段。
- EN: First segment is around `00:00:02-00:00:07`.
- ZH: 首段约 `00:00:02-00:00:07`。
- EN: Last segment is around `01:50:45-01:50:48`.
- ZH: 末段约 `01:50:45-01:50:48`。
- EN: The ASR has recognition errors, especially team/player names and some Chinese terms.
- ZH: ASR 存在识别错误，尤其是队名、人名和部分中文词。
- EN: `goal_candidate_windows.*` contains 9 weak ASR-derived candidate windows. Some may be live goals, while others may be replay, halftime summary, or historical commentary.
- ZH: `goal_candidate_windows.*` 包含 9 个由 ASR 弱信号提取的候选窗口。其中一部分可能是现场进球，另一部分可能是回放、中场总结或历史叙述。

Usage / 用法：

EN: Use this as a weak reference for evaluation, not as a gold answer. A good visual commentary harness should agree with key event timing and factual context, but it may produce different wording and may mention visual facts that the broadcast audio did not say.

ZH: 它只能作为弱参考，不是 gold answer。好的视觉解说 Harness 应该在关键事件时间和事实背景上与参考一致，但措辞可以不同，也可以描述音轨没有说出的画面事实。

Do not commit the full extracted audio file here. Keep only chunks and reference outputs.

不要把完整抽取音频提交到这里。只保留分块和参考输出。

Verification priority / 核验优先级：

EN: Start with strong direct phrases such as "球进了", then verify each window from frames and scoreboard. Do not treat the ASR candidate list as final goal truth.

ZH: 优先核验包含“球进了”等直接表述的强信号窗口，再用帧画面和比分牌确认。不要把 ASR 候选列表当成最终进球真值。
