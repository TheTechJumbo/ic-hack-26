import os
import httpx
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Use a calm, supportive voice
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice


def generate_voice_message(text: str, voice_id: str = None) -> bytes:
    """Generate speech audio from text using ElevenLabs."""
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id or DEFAULT_VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
    )

    # Collect all audio chunks into bytes
    audio_bytes = b"".join(audio_generator)
    return audio_bytes


async def create_voice_clone(audio_bytes: bytes, name: str) -> str:
    """
    Create an instant voice clone from audio bytes.
    Returns the voice_id of the cloned voice.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "https://api.elevenlabs.io/v1/voices/add",
            headers={"xi-api-key": api_key},
            data={
                "name": name,
                "remove_background_noise": "true",
            },
            files={
                "files": ("voice_sample.ogg", audio_bytes, "audio/ogg"),
            },
            timeout=60.0,
        )

        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["voice_id"]
