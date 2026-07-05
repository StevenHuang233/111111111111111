# Final Source Package Guide / 最终源码包指南

EN: This guide explains what should be included in the source-code submission and how to validate the repository before packaging.

中文：本指南说明最终源码提交应包含哪些内容，以及打包前如何验证仓库。

## What This Repository Contains / 仓库包含内容

- Harness source code / Harness 源码：`harness/`, `intern_client.py`, pipeline runners, SRT exporter.
- Configuration / 配置：`configs/event_types.json`, `configs/styles.json`, `configs/match_contexts.json`, `configs/pipeline_presets.json`.
- Evaluation and reflection tools / 评测与反思工具：`reference/evaluation/tools/`.
- Final V11 acceptance record / V11 最终验收记录：`reference/evaluation/final_reflection_v11/`.
- Planning and pitch notes / 规划与汇报材料：`docs/`, `submission/`.
- Unit tests / 单元测试：`tests/`.

## What Must Stay Out / 不应进入源码包的内容

- `.env`, API keys, passwords, private credentials.
- Raw videos, extracted frames, contact sheets, demo videos, generated zips.
- `outputs/`, `runs/`, `artifacts/`, `logs/`, `.venv/`, `__pycache__/`.
- Audio chunk files and raw ASR upload responses. Keep only compact reference summaries and regeneration scripts.

中文：源码包只交代码、配置、说明和小型验收记录；大视频、抽帧、运行输出、密钥和音频块不要进入 Git 或源码 zip。

## Current Final Baseline / 当前最终基线

- Branch / 分支：`team/worldcup-commentary`.
- Latest integrated work / 已合入内容：nightwork core harness updates, match context injection, replay/goal verification, final V11 evaluation records.
- Final V11 input / V11 输入：`outputs/commentary_bilingual-final-V11-unreflected.json` local ignored output.
- Final V11 reflected output / V11 反思后输出：`outputs/commentary_bilingual-final-V11-reflected.json` local ignored output.
- Final V11 acceptance / V11 验收：`reference/evaluation/final_reflection_v11/README.md`.

Key V11 metrics / V11 关键指标：

| Metric / 指标 | Before / 反思前 | After / 反思后 |
| --- | ---: | ---: |
| Overall gate / 总门禁 | fail | pass_with_warnings |
| Goal type segments / goal 类型段 | 23 | 8 |
| Verified goals / 已核验真实进球 | 8 | 8 |
| Extra goal assertions / 额外进球断言 | 30 | 0 |
| Missing verified goals / 漏掉真实进球 | 0 | 0 |

## Validation Commands / 验证命令

Run unit tests / 运行单元测试：

```powershell
python -B -m unittest discover -s tests -v
```

Expected current result / 当前预期结果：

```text
Ran 36 tests
OK (skipped=1)
```

Run the final V11 evaluation loop manually / 手动运行 V11 最终评测闭环：

```powershell
# See full command sequence:
# 查看完整命令：
Get-Content reference/evaluation/final_reflection_v11/README.md
```

Export final V11 SRT from local ignored output / 从本地忽略输出导出 V11 SRT：

```powershell
python -B scripts/export_commentary_srt.py `
  --input outputs/commentary_bilingual-final-V11-reflected.json `
  --output-dir outputs/srt/final_V11_reflected `
  --text-source both `
  --languages all
```

## Packaging Procedure / 打包步骤

1. Confirm the working tree is clean except intentionally ignored local outputs.
   中文：确认工作树干净，只允许存在被忽略的本地运行输出。
2. Run unit tests.
   中文：运行单元测试。
3. Confirm V11 acceptance record is present.
   中文：确认 V11 验收记录已存在。
4. Build the source zip from tracked files only.
   中文：从 Git 跟踪文件构建源码 zip。

Recommended command / 推荐命令：

```powershell
git archive --format=zip --output submission/source_code.zip HEAD
```

EN: `git archive` only packages tracked files, so ignored videos, frames, `.env`, and `outputs/` are excluded automatically.

中文：`git archive` 只打包 Git 跟踪文件，因此会自动排除视频、抽帧、`.env` 和 `outputs/`。

## Runtime Notes / 运行说明

- The judged model API should be Intern-S2-Preview.
- The source code keeps configurable API URL, key, frame root, event paths, and output paths outside committed secrets.
- The V11 reflection step uses verified scoreboard/event evidence to downgrade false goals into shots, dangerous attacks, or replay commentary while keeping the wording as commentary instead of internal notes.

中文：

- 验收模型 API 应使用 Intern-S2-Preview。
- API URL、Key、抽帧路径、事件路径、输出路径都通过配置或命令行传入，不写入仓库密钥。
- V11 反思步骤基于已核验比分/事件证据，将误判进球降级为射门、威胁进攻或回放解说，同时保持解说口吻，不输出内部处理说明。
