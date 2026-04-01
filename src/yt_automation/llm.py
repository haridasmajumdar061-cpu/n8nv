from __future__ import annotations

import os
from typing import Any

import requests


class LLMClient:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_s: int = 60,
    ) -> None:
        self.provider = provider.lower().strip()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1/responses"
        self.timeout_s = timeout_s

    def generate(self, prompt: str, max_tokens: int | None = None, temperature: float = 0.6) -> str:
        if self.provider != "openai":
            raise ValueError("Only 'openai' provider is wired. Use mock mode or implement your own.")
        if not self.api_key:
            raise ValueError("Missing API key. Set OPENAI_API_KEY.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "input": prompt,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_output_tokens"] = max_tokens

        response = requests.post(self.base_url, json=payload, headers=headers, timeout=self.timeout_s)
        response.raise_for_status()
        data = response.json()

        # Best-effort parsing across common response shapes.
        if isinstance(data, dict):
            if "output_text" in data and isinstance(data["output_text"], str):
                return data["output_text"]
            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if isinstance(content, str):
                    return content
            if "output" in data:
                parts = []
                for item in data["output"]:
                    for content in item.get("content", []):
                        text = content.get("text")
                        if text:
                            parts.append(text)
                if parts:
                    return "\n".join(parts)

        raise ValueError("Could not parse LLM response.")
