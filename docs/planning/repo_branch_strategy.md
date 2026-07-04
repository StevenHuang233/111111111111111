# Repository And Branch Strategy / 仓库与分支策略

Last updated: 2026-07-04

Remote repository / 远程仓库:

```text
git@github.com:StevenHuang233/111111111111111.git
```

## Principles / 原则

EN:

- Do not touch remote `main` directly.
- Use a simple public-safe neutral branch for harmless demo or placeholder content.
- Use our own work branch for World Cup harness materials.
- Do not commit videos, extracted frames, API keys, passwords, private notes, or large outputs.

ZH:

- 不直接动远程 `main`。
- 使用一个简单的 public-safe neutral branch，只放无害 demo 或占位内容。
- 我们自己的世界杯 Harness 内容放工作分支。
- 不提交视频、抽帧、API Key、密码、私密笔记或大输出。

## Recommended Branches / 推荐分支

| Branch | Purpose | Content |
| --- | --- | --- |
| `public/demo-placeholder` | Public-safe neutral branch. / 中性公开分支。 | Minimal unrelated development demo, basic README, no contest material. Prepared and pushed on 2026-07-04. / 简单无关 demo，不放赛题材料。已于 2026-07-04 准备并推送。 |
| `team/worldcup-commentary` | Our main work branch. / 我们的主要工作分支。 | Docs, harness code, configs, manifests, submission materials. Rebase from `origin/main` frequently; never push to `main`. / 文档、Harness 代码、配置、manifest、提交材料。频繁从 `origin/main` rebase，但绝不推送 `main`。 |
| `team/worldcup-docs-night` | Optional overnight docs branch. / 夜间文档分支。 | Text-only docs and presentation materials that do not need local video. / 不依赖本地视频的纯文档和汇报材料。 |

## Main Tracking / main 跟踪策略

EN: `main` may keep receiving teammate updates such as smoke tests, resume, progress runner, and concurrency work. Our rule is: fetch and inspect `origin/main`, rebase `team/worldcup-commentary` when needed, record new capabilities in planning docs, but never commit or push directly to `main`.

ZH: `main` 可能持续收到队友更新，例如 smoke 测试、续跑、进度 runner 和并发等。我们的规则是：拉取并检查 `origin/main`，必要时把 `team/worldcup-commentary` rebase 到最新，更新规划文档中的能力记录，但绝不直接向 `main` commit 或 push。

## Safe Public Branch Content / 公开分支可放内容

EN: Keep it intentionally simple and unrelated to harness, such as a tiny generic development demo or placeholder README. The goal is to avoid exposing private contest work early, not to mislead judges or violate rules.

ZH: 公开分支保持简单、与 Harness 无关，例如很小的通用开发 demo 或占位 README。目的只是避免过早暴露内部赛题工作，不用于误导评审或违反规则。

## Commands For Later / 后续命令参考

Do not run these until the team is ready.

团队准备好之前不要执行这些命令。

```powershell
git remote add origin git@github.com:StevenHuang233/111111111111111.git
git fetch origin
git switch -c team/worldcup-commentary
```

For public-safe placeholder branch:

公开安全占位分支：

```powershell
git switch -c public/demo-placeholder
```

## Merge Policy / 合并策略

EN:

- Work through PRs when possible.
- Keep large data outside Git and reference it through `.env` and manifests.
- Before any PR, run a large-file check.

ZH:

- 尽量通过 PR 协作。
- 大数据放 Git 外，通过 `.env` 和 manifest 引用。
- 每次 PR 前做大文件检查。

