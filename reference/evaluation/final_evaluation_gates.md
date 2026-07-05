# Final Evaluation Gates / 终稿评测门禁

EN: This report aggregates quality, goal-timeline, and identity/style gates for the generated commentary.

ZH: 本报告汇总生成解说的质量、进球时间线、身份与风格三类门禁。

- `overall_status`: fail
- `input`: `outputs\commentary_bilingual.json`

## Gates / 门禁

| Gate | Status | Blockers | Warnings | Key Metrics |
| --- | --- | --- | --- | --- |
| quality | fail | wrong_entity_segments, goal_overcount, score_claim_segments | style_color_identity_segments, mixed_language_segments, prematch_action_segments | generated_goal_count=21, verified_goal_count=8, goal_overcount=13, score_claim_segments=37, wrong_entity_segments=9, style_color_identity_segments=44 |
| goal_alignment | fail | extra_goal_assertions | duplicate_verified_goal_groups | verified_score_changes=8, generated_goal_type_segments=21, generated_goal_assertion_segments=37, covered_verified_goals=8, missing_verified_goals=0, duplicate_verified_goal_groups=5, extra_goal_assertions=21 |
| identity_style | fail | wrong_entity_segments, unsupported_name_segments | color_identity_segments, raw_visual_segments | color_identity_segments=43, raw_visual_segments=44, wrong_entity_segments=9, unsupported_name_segments=13, color_identity_ratio=0.1673, raw_visual_ratio=0.1712 |

## Recommendations / 建议

| Priority | Area | EN | ZH |
| --- | --- | --- | --- |
| Must | Goal precision | Enable goal verification plus score-state suppression before accepting final narration. | 接受最终解说前，必须启用进球验证与比分状态抑制，降低假进球。 |
| Must | Fact safety | Block wrong teams and unsupported names, then rewrite identity wording through the verified-name cascade. | 拦截错误球队和无依据姓名，再通过已验证姓名级联重写身份措辞。 |
| Must | Final output audit | Do not use this generated file directly for the demo video or route speech. | 不要把当前生成文件直接用于 demo 视频或路演解说稿。 |
