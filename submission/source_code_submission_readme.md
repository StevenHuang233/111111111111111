# Source Code Submission README / 源码提交说明

EN: Submit this repository as source code. Use `git archive` or an equivalent tracked-file-only zip process.

中文：最终提交源码时请提交本仓库的源码包。建议使用 `git archive`，只打包 Git 跟踪文件。

## Package Command / 打包命令

```powershell
git archive --format=zip --output submission/source_code.zip HEAD
```

Do not manually add ignored runtime outputs unless the competition form explicitly asks for them as separate deliverables.

中文：不要手动把被忽略的运行产物塞进源码 zip；如果比赛表单要求结果文件、视频或 PPT，应作为单独提交物处理。

## Include / 应包含

- Source code and scripts / 源码和脚本
- Harness configs / Harness 配置
- Evaluation and reflection tools / 评测与反思工具
- Small acceptance reports / 小型验收报告
- Documentation / 说明文档
- Tests / 测试

## Exclude / 不包含

- `.env` and keys / `.env` 和密钥
- Raw video and frames / 原始视频和抽帧
- `outputs/`, `runs/`, `artifacts/`, `logs/`
- Audio chunks and raw ASR responses / 音频切块和 raw ASR 响应
- Demo video, PPT, cover image, generated zip / Demo 视频、PPT、封面图、生成 zip

## Verification Snapshot / 验证快照

- Latest branch / 最新分支：`team/worldcup-commentary`
- Nightwork core integrated / 已合入 nightwork 核心代码：yes
- Unit tests / 单元测试：`36` passed, `1` skipped real API smoke
- V11 final gate / V11 最终门禁：`pass_with_warnings`
- V11 true goals covered / V11 真实进球覆盖：`8/8`
- V11 extra goal assertions / V11 额外进球断言：`0`

Detailed V11 record / V11 详细记录：

- `reference/evaluation/final_reflection_v11/README.md`
- `reference/evaluation/final_reflection_v11/final_evaluation_gates-v11-after.md`
- `reference/evaluation/final_reflection_v11/goal_reflection_report-v11.md`

## Separate Deliverables / 另行提交材料

- Code zip / 代码 zip：`submission/source_code.zip`
- Cover image / 封面图
- Project title / 作品标题
- Short introduction / 作品简介
- Markdown documentation / 说明文档
- Demo video / Demo 视频
- Individual contribution PPT / 个人贡献 PPT
- Pitch script / 路演稿
- Q&A notes / 答辩问题
- Intern-S2-Preview feedback table / Intern-S2-Preview 反馈表
