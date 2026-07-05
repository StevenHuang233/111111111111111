from __future__ import annotations

from pathlib import Path

from PIL import Image


FIFA_REPLAY_BUMPER_EVIDENCE = (
    "FIFA replay bumper detected; relabeled as celebration_or_replay because this is replay packaging, "
    "not live scoring action."
)

_SAMPLE_SIZE = (240, 120)


def detect_fifa_replay_bumper(image_path: str | Path) -> bool:
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception:
        return False

    width, height = image.size
    if width < 100 or height < 80:
        return False

    crop = image.crop(
        (
            int(width * 0.30),
            int(height * 0.34),
            int(width * 0.70),
            int(height * 0.68),
        )
    ).resize(_SAMPLE_SIZE, Image.Resampling.BILINEAR)

    sample_width, sample_height = _SAMPLE_SIZE
    columns = [0] * sample_width
    rows = [0] * sample_height
    gold_pixels = 0
    data = crop.tobytes()
    for index in range(0, len(data), 3):
        pixel_index = index // 3
        x = pixel_index % sample_width
        y = pixel_index // sample_width
        red = data[index]
        green = data[index + 1]
        blue = data[index + 2]
        if _is_fifa_gold(red, green, blue):
            gold_pixels += 1
            columns[x] += 1
            rows[y] += 1

    density = gold_pixels / float(sample_width * sample_height)
    column_intervals = [item for item in _intervals(columns, threshold=18) if _interval_width(item) >= 3]
    row_intervals = [item for item in _intervals(rows, threshold=40) if _interval_width(item) >= 2]
    strong_columns = sum(1 for value in columns[40:200] if value >= 25)
    strong_rows = sum(1 for value in rows[20:100] if value >= 60)
    has_letter_band = any(
        start >= 8 and end <= 110 and 14 <= _interval_width((start, end)) <= 100
        for start, end in row_intervals
    )
    has_letter_columns = (
        sum(1 for start, end in column_intervals if end >= 35 and start <= 205) >= 2
    )

    return (
        density >= 0.15
        and strong_columns >= 70
        and strong_rows >= 12
        and has_letter_band
        and has_letter_columns
    )


def _is_fifa_gold(red: int, green: int, blue: int) -> bool:
    return (
        red > 145
        and green > 105
        and blue < 110
        and red > green * 1.02
        and green > blue * 1.35
        and max(red, green, blue) - min(red, green, blue) > 70
    )


def _intervals(values: list[int], threshold: int) -> list[tuple[int, int]]:
    intervals: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(values):
        if value >= threshold and start is None:
            start = index
        elif value < threshold and start is not None:
            intervals.append((start, index - 1))
            start = None
    if start is not None:
        intervals.append((start, len(values) - 1))
    return intervals


def _interval_width(interval: tuple[int, int]) -> int:
    return interval[1] - interval[0] + 1
