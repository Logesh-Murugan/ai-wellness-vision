import os
import tempfile
import asyncio
import logging
from typing import Dict, Optional, Any
import numpy as np

# Optional imports for lazy loading
try:
    import whisper
except ImportError:
    whisper = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

logger = logging.getLogger(__name__)

# Free Neural Voices mapping (Microsoft Edge TTS)
INDIAN_LANGUAGE_VOICES = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "gu": "gu-IN-DhwaniNeural",
    "mr": "mr-IN-AarohiNeural",
    # Fallback default
    "default": "en-US-AriaNeural"
}

class SpeechService:
    def __init__(self, model_size="small"):
        self.model_size = model_size
        self._whisper_model = None

    def _load_model(self):
        """Lazy load the Whisper model to save RAM until needed."""
        if whisper is None:
            raise RuntimeError("openai-whisper is not installed.")
            
        if self._whisper_model is None:
            logger.info(f"Loading local Whisper model ({self.model_size})...")
            # fp16 is False to avoid warnings on CPU
            self._whisper_model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully.")
        return self._whisper_model

    def _validate_audio_duration(self, audio_np: np.ndarray, sample_rate: int = 16000):
        """Validate audio is not longer than 60 seconds to prevent CPU exhaustion."""
        duration_seconds = len(audio_np) / sample_rate
        if duration_seconds > 60:
            raise ValueError(f"Audio duration ({duration_seconds:.1f}s) exceeds the maximum limit of 60 seconds.")
        return duration_seconds

    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Convert speech to text using local Whisper model."""
        model = self._load_model()
        
        # Whisper requires a file path, so we use a secure temporary file
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(audio_data)
                
            # Load audio to numpy array to check duration
            audio_np = whisper.load_audio(tmp_path)
            duration = self._validate_audio_duration(audio_np)
            
            # Run transcription (this blocks, so we run in thread pool if needed, but async is ok for now)
            # whisper's transcribe method is synchronous, so we run it using asyncio.to_thread
            options = {"fp16": False}
            if language:
                options["language"] = language
                
            result = await asyncio.to_thread(model.transcribe, tmp_path, **options)
            
            # Get language probability if available
            detected_lang = result.get("language", language or "unknown")
            
            return {
                "text": result["text"].strip(),
                "language": detected_lang,
                "duration_seconds": round(duration, 2),
                "segments": len(result.get("segments", [])),
                "provider": "openai-whisper-local"
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise e
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def detect_language(self, audio_data: bytes) -> str:
        """Detect the language of the audio file using the first 30 seconds."""
        model = self._load_model()
        
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(audio_data)
                
            audio = whisper.load_audio(tmp_path)
            audio = whisper.pad_or_trim(audio)
            
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            
            _, probs = model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            return detected_lang
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech using free Microsoft Edge TTS neural voices."""
        if edge_tts is None:
            raise RuntimeError("edge-tts is not installed.")
            
        voice_name = INDIAN_LANGUAGE_VOICES.get(language, INDIAN_LANGUAGE_VOICES["default"])
        
        # Edge TTS generates an MP3 file
        fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd) # Close immediately, let edge_tts write to it
        
        try:
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(tmp_path)
            
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()
                
            return audio_bytes
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise e
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def get_available_voices(self) -> Dict[str, str]:
        """Return the dictionary of configured neural voices."""
        return INDIAN_LANGUAGE_VOICES

# Global service instance
speech_service = SpeechService()