import httpx

from app.core.config import settings


class TelegramClient:
    async def send_message(self, payload: dict) -> dict:
        if not settings.telegram_bot_token:
            return {"status": "mock", "message": payload.get("text", "")}

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json={"chat_id": payload.get("chat_id"), "text": payload.get("text")})
            response.raise_for_status()
            return response.json()


telegram_client = TelegramClient()
