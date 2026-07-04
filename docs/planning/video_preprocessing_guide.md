# Video Preprocessing Guide / 视频预处理记录

Last updated: 2026-07-04

## Current Extraction / 当前抽帧结果

Input video / 输入视频:

```text
D:\JediXing\Documents\personal\研究\BaoYan_Application_Materials_2026\projects\Shanghai_Artificial_Intelligence_Laboratory_2026\hackathon\vedio\德国_库拉索.mp4
```

Metadata / 元数据:

| Item | Value |
| --- | --- |
| Duration / 时长 | 01:50:53.08 |
| Resolution / 分辨率 | 1920x1080 |
| Frame rate / 原帧率 | 25 fps |
| Codec / 编码 | HEVC |
| Input size / 输入大小 | ~7.96GB |

Extraction / 抽帧:

| Item | Value |
| --- | --- |
| Output path / 输出目录 | `E:\worldcup_data\frames_4fps_q3` |
| Extracted FPS / 抽帧帧率 | 4 fps |
| Image format / 图片格式 | JPEG |
| Quality / 质量 | `q=3` |
| Frame count / 帧数 | 26612 |
| Output size / 输出大小 | ~6.996GB |
| Runtime / 用时 | ~24m38s |

Command / 命令:

```powershell
& "D:\software\tools\Doxent\platform\win\ffmpeg.exe" -hide_banner -stats `
  -i "D:\JediXing\Documents\personal\研究\BaoYan_Application_Materials_2026\projects\Shanghai_Artificial_Intelligence_Laboratory_2026\hackathon\vedio\德国_库拉索.mp4" `
  -map 0:v:0 -an -vf "fps=4" -q:v 3 -start_number 0 `
  "E:\worldcup_data\frames_4fps_q3\frame_%06d.jpg"
```

## Time Mapping / 时间映射

EN: Current extracted frames are 4fps, so:

ZH: 当前抽帧为 4fps，因此：

```text
video_seconds = frame_id / 4
```

Example / 示例:

```text
frame_013306.jpg -> 13306 / 4 = 3326.5s -> 55:26.5 video time
```

Important / 重要：

- EN: Video time is not always the same as match clock shown on the scoreboard.
- ZH: 视频时间不一定等于转播比分牌上的比赛计时。
- EN: Commentary should store both when possible.
- ZH: 解说稿应尽量同时保存两种时间。

## Data Safety / 数据安全

EN:

- Keep `E:\worldcup_data` outside Git.
- Do not copy frames into `docs/`, `source/`, or the repository root.
- Only commit scripts, manifests, and small public-safe samples.

ZH:

- `E:\worldcup_data` 必须保持在 Git 仓库外。
- 不要把抽帧复制到 `docs/`、`source/` 或仓库根目录。
- Git 只提交脚本、manifest 和少量可公开小样例。

## Next Data Steps / 后续数据步骤

EN:

1. Build a frame manifest with frame id, video time, and image path.
2. Sample frames around scoreboard changes and visual highlights.
3. Annotate scene types: opening, attack, defense, replay, close-up, referee decision, goal, injury, and summary.
4. Use verified evidence to generate timestamped commentary.

ZH:

1. 建立帧 manifest，包含帧号、视频时间和图片路径。
2. 围绕比分牌变化和视觉高光抽样。
3. 标注场景类型：开场、进攻、防守、回放、特写、判罚、进球、受伤、总结。
4. 基于已核验证据生成带时间戳解说稿。
