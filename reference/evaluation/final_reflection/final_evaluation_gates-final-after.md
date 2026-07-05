# Final Evaluation Gates / 终稿评测门禁

EN: This report aggregates quality, goal-timeline, and identity/style gates for the generated commentary.

ZH: 本报告汇总生成解说的质量、进球时间线、身份与风格三类门禁。

- `overall_status`: pass_with_warnings
- `input`: `outputs\commentary_bilingual-final-reflected.json`

## Gates / 门禁

| Gate | Status | Blockers | Warnings | Key Metrics |
| --- | --- | --- | --- | --- |
| quality | pass_with_warnings | - | mixed_language_segments | generated_goal_count=8, verified_goal_count=8, goal_overcount=0, score_claim_segments=5, wrong_entity_segments=0, style_color_identity_segments=6 |
| goal_alignment | pass | - | - | verified_score_changes=8, generated_goal_type_segments=8, generated_goal_assertion_segments=8, covered_verified_goals=8, missing_verified_goals=0, duplicate_verified_goal_groups=0, extra_goal_assertions=0 |
| identity_style | pass_with_warnings | - | raw_visual_segments | color_identity_segments=4, raw_visual_segments=42, wrong_entity_segments=0, unsupported_name_segments=0, color_identity_ratio=0.017, raw_visual_ratio=0.1787 |

## Recommendations / 建议

| Priority | Area | EN | ZH |
| --- | --- | --- | --- |
| Should | Manual review | Perform a short manual review of high-stakes events before packaging. | 打包前仍应对高风险事件做短人工复核。 |
