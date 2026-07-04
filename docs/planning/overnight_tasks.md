# Overnight Tasks / 夜间任务

Last updated: 2026-07-04 19:00

## Context / 背景

EN: Humans leave around 22:00 and resume around 09:00. Overnight work should avoid local video dependencies and avoid risky repository operations.

ZH: 人约 22:00 离开，第二天 09:00 恢复。夜间任务应避免依赖本地视频，避免高风险仓库操作。

## Good Overnight Tasks / 适合夜间远端做的任务

| Task | Output | Why Suitable |
| --- | --- | --- |
| Harness story draft / Harness 叙事草稿 | `docs/harness_story.md` improvements | Text-only, no local data. / 纯文本，不依赖本地数据。 |
| Presentation outline / 汇报大纲 | 30-second and 10-15 minute scripts | Text-only and useful for morning review. / 纯文本，早上可审。 |
| Intern-S2 feedback draft / Intern-S2 反馈草稿 | Filled template with placeholders | Can be refined after real runs. / 可先占位，实际运行后修订。 |
| Evaluation rubric / 评估 rubric | Script quality and fact-check rubric | No video processing required. / 不需要视频处理。 |
| README cleanup / README 整理 | Bilingual quickstart | Low risk. / 风险低。 |

## Tasks Not Suitable Overnight / 不适合夜间远端做的任务

| Task | Reason |
| --- | --- |
| Full video processing / 全量视频处理 | Requires local 7GB video and extracted frames. / 依赖本地视频和抽帧。 |
| Event annotation from frames / 从帧中标注事件 | Needs visual inspection and local frame directory. / 需要看本地帧。 |
| Git remote restructuring / 远程仓库结构调整 | Risky without human supervision. / 无人监督风险高。 |
| API-key integration / API Key 接入 | Secrets should not be exposed to remote agents. / 密钥不应暴露给远端 agent。 |

## Suggested Cloud Branch / 建议远端分支

EN: If cloud agents are used, give them a separate branch and text-only scope.

ZH: 如果使用云端 agent，给它单独分支，并限制为纯文本范围。

```text
team/worldcup-docs-night
```

Allowed paths / 允许修改路径:

- `docs/`
- `submission/`
- `README.md`

Blocked paths / 禁止修改路径:

- `.git/`
- `vedio/`
- `source/raw/`
- `source/frames/`
- API keys or `.env`

