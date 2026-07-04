#!/usr/bin/env python
"""Build local contact sheets for goal-candidate frame verification.

The generated PNG files go under outputs/ and are intentionally ignored by Git.
They help humans or a later visual verifier inspect scoreboard state and nearby
action frames without opening thousands of extracted frames manually.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHECKLIST = REPO_ROOT / "reference" / "evaluation" / "goal_frame_checklist.json"
DEFAULT_FRAMES_DIR = Path(r"E:\worldcup_data\frames_4fps_q3")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "goal_frame_contact_sheets"
DEFAULT_SCOREBOARD_BBOX = (1220, 70, 1835, 155)


def parse_bbox(value: str) -> tuple[int, int, int, int]:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox must be x1,y1,x2,y2")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("bbox must have x2>x1 and y2>y1")
    return x1, y1, x2, y2


def load_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit("Pillow is required. Use the ailab-hackathon env where PIL is already available.") from exc
    return Image, ImageDraw, ImageFont


def unique_probes(item: dict[str, Any], include_dense: bool, max_dense: int) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    seen: set[int] = set()
    sources = [("coarse", item.get("coarse_scoreboard_probes", []))]
    if include_dense:
        sources.append(("dense", item.get("dense_action_probes", [])[:max_dense]))
    for kind, probe_list in sources:
        for probe in probe_list:
            frame_id = int(probe["frame_id"])
            if frame_id in seen:
                continue
            seen.add(frame_id)
            enriched = dict(probe)
            enriched["probe_kind"] = kind
            probes.append(enriched)
    return probes


def make_tile(Image, ImageDraw, ImageFont, frame_path: Path, label: str, bbox: tuple[int, int, int, int]):
    tile_w, tile_h = 420, 250
    image = Image.open(frame_path).convert("RGB")
    scoreboard = image.crop(bbox)
    scoreboard.thumbnail((tile_w - 20, 58))
    full = image.copy()
    full.thumbnail((tile_w - 20, 150))

    tile = Image.new("RGB", (tile_w, tile_h), "white")
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    draw.text((10, 8), label, fill=(0, 0, 0), font=font)
    tile.paste(scoreboard, (10, 34))
    tile.paste(full, (10, 100))
    return tile


def missing_tile(Image, ImageDraw, ImageFont, label: str, path: Path):
    tile_w, tile_h = 420, 250
    tile = Image.new("RGB", (tile_w, tile_h), (245, 245, 245))
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()
    draw.text((10, 8), label, fill=(0, 0, 0), font=font)
    draw.text((10, 40), "missing frame", fill=(180, 0, 0), font=font)
    draw.text((10, 62), str(path), fill=(60, 60, 60), font=font)
    return tile


def build_sheet(Image, ImageDraw, ImageFont, item: dict[str, Any], frames_dir: Path, output_dir: Path, args) -> dict[str, Any]:
    probes = unique_probes(item, args.include_dense, args.max_dense)
    cols = args.columns
    tile_w, tile_h = 420, 250
    rows = max(1, (len(probes) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), (235, 235, 235))

    missing: list[str] = []
    for index, probe in enumerate(probes):
        frame_path = frames_dir / probe["frame_name"]
        label = f"{item['candidate_id']} {probe['probe_kind']} {probe['video_time']} {probe['frame_name']}"
        if frame_path.exists():
            tile = make_tile(Image, ImageDraw, ImageFont, frame_path, label, args.scoreboard_bbox)
        else:
            tile = missing_tile(Image, ImageDraw, ImageFont, label, frame_path)
            missing.append(str(frame_path))
        x = (index % cols) * tile_w
        y = (index // cols) * tile_h
        sheet.paste(tile, (x, y))

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{item['candidate_id']}_{item['candidate_time'].replace(':', '').replace('-', '_')}.png"
    sheet.save(output_path)
    return {
        "candidate_id": item["candidate_id"],
        "candidate_time": item["candidate_time"],
        "sheet": str(output_path),
        "probe_count": len(probes),
        "missing_frames": missing,
    }


def write_index(results: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Goal Frame Contact Sheets / 进球候选帧拼图",
        "",
        "EN: Generated images are local verification artifacts under outputs/ and are not committed.",
        "",
        "ZH: 生成图片是 outputs/ 下的本地核验产物，不提交到 Git。",
        "",
        "| ID | Candidate Time | Probes | Sheet | Missing |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result['candidate_id']} | `{result['candidate_time']}` | {result['probe_count']} | "
            f"`{Path(result['sheet']).name}` | {len(result['missing_frames'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local contact sheets for goal-candidate frame probes.")
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST)
    parser.add_argument("--frames-dir", type=Path, default=DEFAULT_FRAMES_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scoreboard-bbox", type=parse_bbox, default=DEFAULT_SCOREBOARD_BBOX)
    parser.add_argument("--include-dense", action="store_true")
    parser.add_argument("--max-dense", type=int, default=12)
    parser.add_argument("--columns", type=int, default=3)
    args = parser.parse_args()

    if not args.checklist.exists():
        raise FileNotFoundError(f"Checklist not found: {args.checklist}")
    if not args.frames_dir.exists():
        raise FileNotFoundError(f"Frames directory not found: {args.frames_dir}")

    Image, ImageDraw, ImageFont = load_pillow()
    checklist = json.loads(args.checklist.read_text(encoding="utf-8"))
    results = [
        build_sheet(Image, ImageDraw, ImageFont, item, args.frames_dir, args.output_dir, args)
        for item in checklist
    ]
    write_index(results, args.output_dir / "README.md")
    print(json.dumps({"output_dir": str(args.output_dir), "sheet_count": len(results)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
