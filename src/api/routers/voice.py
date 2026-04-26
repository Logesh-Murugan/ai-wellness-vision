"""
Voice router – transcribe (STT) and synthesise (TTS).

All endpoints are prefixed with ``/api/v1/voice`` and tagged ``voice``.
"""

import logging
import random
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.api.dependencies import get_optional_user
from src.models.api_schemas import SynthesizeRequest, SynthesisResponse, TranscriptionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


# ──────────────────────────────────────────────
# POST /voice/transcribe
# ──────────────────────────────────────────────

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_voice(
    audio: UploadFile = File(...),
    current_user=Depends(get_optional_user),
) -> TranscriptionResponse:
    """Transcribe an uploaded audio file to text.

    Currently uses mock transcriptions.  In production, integrate
    OpenAI Whisper or another STT engine.
    """
    import tempfile

    # Save to a temp file so an STT engine could read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        temp_path = tmp.name

    try:
        # ── Mock transcription (replace with real Whisper call) ──
        mock_transcriptions = [
            "I have a headache and feel tired",
            "What are some healthy food options?",
            "I need advice about exercise",
            "How can I improve my sleep quality?",
            "I'm feeling stressed lately",
            "Can you help me with nutrition advice?",
            "I have been experiencing back pain",
            "What are the symptoms of flu?",
        ]
        transcription = random.choice(mock_transcriptions)

        return TranscriptionResponse(
            transcription=transcription,
            confidence=0.95,
            language="en",
            duration=3.5,
        )
    finally:
        try:
            Path(temp_path).unlink()
        except Exception as exc:
            logger.warning("Could not delete temp audio file: %s", exc)


# ──────────────────────────────────────────────
# POST /voice/synthesize
# ──────────────────────────────────────────────

@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user=Depends(get_optional_user),
) -> SynthesisResponse:
    """Convert text to speech and return an audio URL.

    Currently returns a mock URL.  In production, integrate
    Coqui TTS or another TTS engine.
    """
    audio_filename = f"tts_{uuid.uuid4()}.mp3"
    # In production, generate real audio and serve via cloud storage / static files
    audio_url = f"http://localhost:8000/audio/{audio_filename}"

    return SynthesisResponse(
        audio_url=audio_url,
        text=request.text,
        language=request.language,
        voice=request.voice,
        duration=len(request.text) / 10,  # rough estimate
    )
