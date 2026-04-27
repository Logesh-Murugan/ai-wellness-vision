from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from typing import Optional, Dict
from src.services.speech_service import speech_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcribe audio to text using locally-run Whisper AI.
    Accepts an audio file and an optional ISO language code (e.g., 'en', 'hi').
    Enforces a strict 60-second limit.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file provided.")
            
        result = await speech_service.transcribe(audio_bytes, language)
        return result
        
    except ValueError as ve:
        # Catch the 60-second validation limit explicitly
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /voice/transcribe: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during transcription.")

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    language: str = Form("en")
):
    """
    Convert text to speech using Microsoft Edge Neural TTS.
    Returns the generated audio as an MP3 byte stream.
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
            
        # Get MP3 bytes from Edge TTS
        audio_bytes = await speech_service.synthesize(text, language)
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="synthesis_{language}.mp3"'}
        )
        
    except Exception as e:
        logger.error(f"Error in /voice/synthesize: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during synthesis.")

@router.get("/voices")
async def get_voices() -> Dict[str, str]:
    """
    Return a list of available Neural Voices mapped to language codes.
    """
    return speech_service.get_available_voices()
