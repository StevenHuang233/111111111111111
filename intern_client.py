from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


DEFAULT_BASE_URL = "https://chat.intern-ai.org.cn/api/v1"
DEFAULT_MODEL = "intern-s2-preview"


class InternAPIError(RuntimeError):
    pass


class InternClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 120,
    ) -> None:
        self.api_key = api_key or os.getenv("INTERN_API_KEY")
        self.base_url = (base_url or os.getenv("INTERN_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.getenv("INTERN_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

        if not self.api_key:
            raise InternAPIError("Missing INTERN_API_KEY. Set it in the environment or a local .env file.")

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.3,
        top_p: float = 0.95,
        max_tokens: int = 1024,
        thinking_mode: bool = True,
        **extra: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "thinking_mode": thinking_mode,
            **extra,
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        try:
            data = response.json()
        except ValueError as exc:
            raise InternAPIError(f"Non-JSON response ({response.status_code}): {response.text[:500]}") from exc

        if response.status_code >= 400:
            raise InternAPIError(f"HTTP {response.status_code}: {data}")

        if "choices" not in data:
            raise InternAPIError(f"Unexpected response shape: {data}")

        return data

    @staticmethod
    def text_from_response(data: dict[str, Any]) -> str:
        message = data["choices"][0]["message"]
        return message.get("content") or ""


def image_source_to_url(source: str) -> str:
    if source.startswith(("http://", "https://", "data:")):
        return source

    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)

    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def image_message(prompt: str, image_source: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_source_to_url(image_source)}},
            ],
        }
    ]
