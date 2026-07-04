from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "sample_football_scene.png"

    img = Image.new("RGB", (640, 360), "#2f8f46")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, 639, 359), outline="white", width=6)
    draw.line((320, 0, 320, 360), fill="white", width=4)
    draw.ellipse((260, 80, 380, 200), outline="white", width=4)
    draw.rectangle((0, 90, 90, 270), outline="white", width=4)
    draw.rectangle((550, 90, 639, 270), outline="white", width=4)

    ball_box = (286, 216, 354, 284)
    draw.ellipse(ball_box, fill="white", outline="black", width=3)
    draw.polygon([(320, 235), (337, 248), (330, 270), (310, 270), (303, 248)], fill="black")
    draw.line((320, 235, 320, 216), fill="black", width=2)
    draw.line((337, 248, 354, 238), fill="black", width=2)
    draw.line((330, 270, 342, 284), fill="black", width=2)
    draw.line((310, 270, 298, 284), fill="black", width=2)
    draw.line((303, 248, 286, 238), fill="black", width=2)

    img.save(out_path)
    print(out_path)


if __name__ == "__main__":
    main()
