import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.elevenlabs import generate_voice_message
from services.telegram_service import (
    send_voice_message,
    send_text_message,
    send_chat_action,
    set_webhook,
    delete_webhook,
    get_updates,
)

# Default supportive response for general messages
DEFAULT_RESPONSE = """Hey, I hear you. Whatever you're going through right now, I want you to know that reaching out takes courage. You're not alone in this journey. Take a moment to breathe - in through your nose, out through your mouth. Remember, every step forward, no matter how small, is progress. I'm here for you, and I believe in your strength. You've got this."""

# Keyword-based responses
KEYWORD_RESPONSES = {
    "alcohol": """Hey, it's me - your support companion. I just wanted to reach out and remind you how far you've come. Every single day you choose sobriety is a victory, and you should be proud of yourself. The path isn't always easy, but you have the strength to walk it. Remember, it's okay to have tough moments - what matters is that you keep going. You are not defined by your past, but by the choices you make today. I believe in you, and I'm here whenever you need me. Take a deep breath, and know that you're doing amazing.""",
    "drink": """Hey, it's me - your support companion. I just wanted to reach out and remind you how far you've come. Every single day you choose sobriety is a victory, and you should be proud of yourself. The path isn't always easy, but you have the strength to walk it. Remember, it's okay to have tough moments - what matters is that you keep going. You are not defined by your past, but by the choices you make today. I believe in you, and I'm here whenever you need me. Take a deep breath, and know that you're doing amazing.""",
    "drug": """Hey friend, I'm checking in because I care about you. Recovery takes incredible courage, and the fact that you're on this journey shows just how strong you are. Your cravings don't define you - your determination to overcome them does. Each moment you stay on this path, you're building a better future for yourself. It's okay to struggle sometimes; what matters is that you don't give up. You have people who believe in you, and most importantly, you should believe in yourself. You've got this. One day at a time, one moment at a time.""",
    "gambl": """Hi there, just wanted to send you some encouragement. Taking control of your relationship with gambling shows real self-awareness and strength. Every time you resist the urge, you're proving to yourself that you're in control of your own life. Financial peace of mind is within your reach, and you're already taking steps toward it. Remember, your worth isn't measured by wins or losses - it's measured by your character and the effort you put into becoming better. I'm proud of you for making this choice. Keep going.""",
    "smok": """Hey, I wanted to remind you how amazing you're doing. Each cigarette you don't smoke is a gift you're giving to your future self - cleaner lungs, better health, and more time with the people you love. The cravings will pass, they always do. Your body is healing with every smoke-free day, and that's something to celebrate. When the urge hits, take a deep breath of that fresh air and remember why you started this journey. You're stronger than any craving. I'm rooting for you.""",
    "crav": """I know cravings can feel overwhelming, but remember - they always pass. You are stronger than any urge. This feeling is temporary, but your commitment to yourself is lasting. Take a deep breath, drink some water, and remind yourself why you started this journey. You've already proven your strength by fighting this battle. I'm so proud of you.""",
    "stress": """I can hear that you're feeling stressed. That's completely valid - recovery isn't easy, and life throws challenges at us. But you're handling it by reaching out, and that's exactly the right thing to do. Take a moment to breathe deeply. Remember that stress is temporary, and you have the tools to get through this. You're doing better than you think.""",
    "anxi": """Anxiety can feel so heavy, but you're not carrying it alone. I want you to try something with me - breathe in for 4 counts, hold for 4, and out for 4. You are safe. You are strong. This feeling will pass. Your journey has already shown how resilient you are. Keep going, one moment at a time.""",
    "help": """I'm here for you. Whatever you're facing right now, you don't have to face it alone. Take a deep breath and remember - asking for help is a sign of strength, not weakness. You've already shown incredible courage on your recovery journey. Tell me what's on your mind, and let's work through it together.""",
    "struggling": """I hear you, and I want you to know that struggling doesn't mean failing. Recovery is not a straight line - it has ups and downs, and that's completely normal. The fact that you're reaching out right now shows your commitment to getting better. You are stronger than you know. Let's take this moment by moment together.""",
}

WELCOME_MESSAGE = """Welcome to Kalm - your 24/7 recovery companion.

I'm here to support you on your journey. You can message me anytime you need encouragement, and I'll respond with a supportive voice note.

Just tell me how you're feeling or what you're struggling with, and I'll be here for you.

You're not alone. 💚"""


def get_response_for_message(text: str) -> str:
    """Determine the appropriate response based on message content."""
    text_lower = text.lower()

    for keyword, response in KEYWORD_RESPONSES.items():
        if keyword in text_lower:
            return response

    return DEFAULT_RESPONSE


async def process_telegram_message(chat_id: int, text: str, first_name: str = "friend"):
    """Process incoming message and send voice response."""
    try:
        # Send "recording voice" action to show the bot is working
        await send_chat_action(chat_id, "record_voice")

        # Handle /start command
        if text.startswith("/start"):
            await send_text_message(chat_id, WELCOME_MESSAGE)
            return

        # Get appropriate response
        response_text = get_response_for_message(text)

        # Personalize with first name if available
        if first_name and first_name != "friend":
            response_text = response_text.replace("Hey,", f"Hey {first_name},", 1)
            response_text = response_text.replace("Hi there,", f"Hi {first_name},", 1)

        # Generate voice message
        audio_bytes = generate_voice_message(response_text)

        # Send voice message
        await send_voice_message(
            chat_id=str(chat_id),
            audio_bytes=audio_bytes,
        )

    except Exception as e:
        # If voice fails, send text as fallback
        print(f"Error processing message: {e}")
        await send_text_message(
            chat_id,
            "I'm here for you. Technical difficulties, but know that you're doing great. 💚"
        )


# Polling task
polling_task = None


async def poll_telegram():
    """Long polling loop to get Telegram updates."""
    print("🤖 Starting Telegram bot polling...")
    offset = None

    while True:
        try:
            result = await get_updates(offset=offset, timeout=30)

            if result.get("ok") and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        first_name = message.get("from", {}).get("first_name", "friend")

                        if text:
                            print(f"📩 Message from {first_name}: {text[:50]}...")
                            # Process message (don't await to handle multiple messages)
                            asyncio.create_task(
                                process_telegram_message(chat_id, text, first_name)
                            )

        except Exception as e:
            print(f"Polling error: {e}")
            await asyncio.sleep(5)  # Wait before retrying


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start polling on startup, stop on shutdown."""
    global polling_task

    # Delete any existing webhook so polling works
    print("🔄 Clearing webhook for polling mode...")
    await delete_webhook()

    # Start polling in background
    polling_task = asyncio.create_task(poll_telegram())

    yield

    # Cleanup on shutdown
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
    print("👋 Bot stopped")


app = FastAPI(title="Kalm API", version="1.0.0", lifespan=lifespan)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SupportRequest(BaseModel):
    addiction_type: str
    telegram_chat_id: str


class SupportResponse(BaseModel):
    success: bool
    message: str


@app.get("/")
async def root():
    return {"message": "Kalm API is running"}


@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming Telegram updates (for production with webhook)."""
    try:
        data = await request.json()

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            first_name = message.get("from", {}).get("first_name", "friend")

            if text:
                background_tasks.add_task(
                    process_telegram_message,
                    chat_id,
                    text,
                    first_name
                )

        return {"ok": True}

    except Exception as e:
        print(f"Webhook error: {e}")
        return {"ok": True}


@app.post("/api/telegram/set-webhook")
async def set_telegram_webhook(webhook_url: str):
    """Set the Telegram webhook URL (stops polling, enables webhook mode)."""
    global polling_task
    if polling_task:
        polling_task.cancel()
    result = await set_webhook(webhook_url)
    return result


@app.post("/api/send-support", response_model=SupportResponse)
async def send_support(request: SupportRequest):
    """Send a supportive voice message via Telegram (manual trigger from web form)."""
    try:
        addiction_key = request.addiction_type.lower()
        support_text = KEYWORD_RESPONSES.get(addiction_key, DEFAULT_RESPONSE)
        audio_bytes = generate_voice_message(support_text)

        await send_voice_message(
            chat_id=request.telegram_chat_id,
            audio_bytes=audio_bytes,
            caption="Your Kalm support message"
        )

        return SupportResponse(
            success=True,
            message="Voice message sent to your Telegram!",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
