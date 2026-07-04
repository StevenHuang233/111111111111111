from intern_client import InternClient


def main() -> None:
    client = InternClient()
    data = client.chat(
        [
            {
                "role": "user",
                "content": "Say hello in Chinese, then summarize what you can do for football video commentary in 3 bullets.",
            }
        ],
        max_tokens=512,
        thinking_mode=False,
    )
    print(InternClient.text_from_response(data))


if __name__ == "__main__":
    main()
