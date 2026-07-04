# Lessons / 经验教训

Last updated: 2026-07-04

## Issue Log / 问题记录

| Date | Issue | Impact | Lesson | Next Prevention |
| --- | --- | --- | --- | --- |
| 2026-07-04 | `.git/objects` in the earlier local workspace grew abnormally large. / 早期本地工作区 `.git/objects` 异常膨胀。 | Disk pressure and broken local Git state after cleanup. / 磁盘压力大，清理后本地 Git 状态损坏。 | Large videos, frames, generated outputs, zips, and media must stay outside Git from the start. / 大视频、抽帧、生成产物、压缩包和媒体从一开始就必须在 Git 外。 | Keep strong `.gitignore`; run large-file checks before staging; use external data paths. / 保持严格 `.gitignore`；stage 前跑大文件检查；使用外部数据路径。 |
| 2026-07-04 | Relative PowerShell file reads did not always resolve to the intended cloned repo path in tool execution. / 工具执行时，相对路径的 PowerShell 读取不总是落到目标 clone 目录。 | A file query looked under `C:\` and failed. / 查询跑到 `C:\` 下导致失败。 | For urgent repo maintenance, use absolute paths for inspection and patch only known files. / 紧急维护仓库时，用绝对路径检查，只修改已确认文件。 | Prefer explicit `-LiteralPath` or absolute paths when paths include spaces or non-ASCII segments. / 路径包含空格或中文时，优先用 `-LiteralPath` 或绝对路径。 |
| 2026-07-04 | Local no-API unit test was blocked by environment dependency. / 本地无 API 单测被环境依赖阻塞。 | `unittest` first imported the wrong `tests` namespace because the tool cwd was `C:\`; after adding `tests/__init__.py` and using absolute `-s/-t`, the test reached repo code but failed because Pillow was not installed. / 起初由于工具 cwd 是 `C:\`，`unittest` 导入了错误的 `tests` namespace；补 `tests/__init__.py` 并使用绝对 `-s/-t` 后能进入仓库测试，但因为未安装 Pillow 失败。 | Test failures must be separated into command/cwd issues, missing dependency issues, and real code regressions. / 测试失败要区分命令/cwd 问题、缺依赖问题和真实代码回归。 | Run `pip install -r requirements.txt` in the intended venv before judging test health. / 在目标 venv 中先执行 `pip install -r requirements.txt`，再判断测试健康度。 |
| 2026-07-04 | PowerShell pip command looked like it hung and created an empty `2.32.0` file. / PowerShell 中 pip 命令看起来卡住，并生成了空的 `2.32.0` 文件。 | Bare version constraints such as `pip install requests>=2.32.0` can be parsed as output redirection by Windows PowerShell. / 裸写 `pip install requests>=2.32.0` 会被 Windows PowerShell 把 `>` 解析为输出重定向。 | Use `python -m pip install -r requirements.txt` or quote constraints, for example `python -m pip install "requests>=2.32.0"`. / 使用 `python -m pip install -r requirements.txt`，或给约束加引号，例如 `python -m pip install "requests>=2.32.0"`。 | Prefer the explicit environment Python path `E:\conda\envs\ailab-hackathon\python.exe`; avoid `conda run` when it tries to write C drive AppData. / 优先使用明确环境解释器 `E:\conda\envs\ailab-hackathon\python.exe`；当 `conda run` 试图写 C 盘 AppData 时避免使用。 |
| 2026-07-04 | Harness claims can outrun evidence. / Harness 叙事容易跑在证据前面。 | Risk of overclaiming concurrency, full automation, or tactical analysis. / 可能过度宣称并发、全自动或战术分析。 | Mark unverified capabilities as verification targets, not completed features. / 未验证能力要标为验证目标，而不是已完成功能。 | Pair each pitch claim with a file, trace, test, or demo clip. / 每个路演主张都对应文件、trace、测试或 demo 片段。 |

## Reusable Practices / 可复用做法

EN:

- Use small smoke manifests before full-video runs.
- Keep video time, match clock, and generated commentary timestamps separate.
- Cache model calls and checkpoint stage outputs for interruption recovery.
- Treat missing names, scores, and facts as unknown until verified from video evidence, official notes, reliable search, or user-provided metadata.

ZH:

- 全片运行前先用小 smoke manifest。
- 区分视频时间、比赛计时和生成解说的时间戳。
- 缓存模型调用和阶段产物，用于中断恢复。
- 人名、比分和事实在视频证据、官方说明、可靠搜索或用户元数据确认前，一律视为未知。
