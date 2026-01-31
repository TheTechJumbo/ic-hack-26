import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_api_url():
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_voice_message(chat_id: str, audio_bytes: bytes, caption: str = None) -> dict:
    """Send a voice message via Telegram Bot API."""
    async with httpx.AsyncClient() as client:
        files = {"voice": ("message.mp3", audio_bytes, "audio/mpeg")}
        data = {"chat_id": chat_id}

        if caption:
            data["caption"] = caption

        response = await client.post(
            f"{get_api_url()}/sendVoice",
            files=files,
            data=data,
            timeout=60.0
        )

        result = response.json()

        if not result.get("ok"):
            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")

        return result


async def send_text_message(chat_id: str, text: str) -> dict:
    """Send a text message via Telegram Bot API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_api_url()}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=30.0
        )

        result = response.json()

        if not result.get("ok"):
            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")

        return result


async def send_chat_action(chat_id: str, action: str = "record_voice") -> dict:
    """Send a chat action (typing indicator, recording voice, etc.)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_api_url()}/sendChatAction",
            json={
                "chat_id": chat_id,
                "action": action,
            },
            timeout=10.0
        )
        return response.json()


async def set_webhook(webhook_url: str) -> dict:
    """Set the webhook URL for receiving updates."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_api_url()}/setWebhook",
            json={"url": webhook_url},
            timeout=30.0
        )
        return response.json()


async def delete_webhook() -> dict:
    """Delete the webhook (required for polling mode)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_api_url()}/deleteWebhook",
            timeout=30.0
        )
        return response.json()


async def get_updates(offset: int = None, timeout: int = 30) -> dict:
    """Get updates using long polling."""
    async with httpx.AsyncClient() as client:
        params = {"timeout": timeout}
        if offset:
            params["offset"] = offset

        response = await client.post(
            f"{get_api_url()}/getUpdates",
            json=params,
            timeout=timeout + 10  # Add buffer for network latency
        )
        return response.json()
