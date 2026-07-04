import argparse
from pathlib import Path

from intern_client import InternClient, image_message
from make_sample_image import main as make_sample_image


DEFAULT_IMAGE = str(Path("outputs") / "sample_football_scene.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Local image path, image URL, or data URI.")
    parser.add_argument(
        "--prompt",
        default="Describe the image briefly, then say whether it is useful as evidence for football commentary.",
    )
    args = parser.parse_args()

    if args.image == DEFAULT_IMAGE and not Path(args.image).exists():
        make_sample_image()

    client = InternClient()
    data = client.chat(image_message(args.prompt, args.image), max_tokens=512, thinking_mode=False)
    print(InternClient.text_from_response(data))


if __name__ == "__main__":
    main()
