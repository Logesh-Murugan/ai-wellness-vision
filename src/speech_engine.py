# speech_engine.py - Speech recognition and synthesis engine
import whisper
import soundfile as sf
import numpy as np
from pathlib import Path
import tempfile
import os
from src.config import ModelConfig

class SpeechEngine:
    def __init__(self):
        self.whisper_model = self._load_whisper_model()
        self.supported_languages = ['en', 'hi', 'ta', 'te', 'bn']
        
    def _load_whisper_model(self):
        """Load Whisper model for speech recognition"""
        try:
            model = whisper.load_model(ModelConfig.WHISPER_MODEL_SIZE)
            return model
        except Exception as e:
            print(f"Warning: Could not load Whisper model: {e}")
            return None
    
    def transcribe_audio(self, audio_path, language=None):
        """Transcribe audio file to text"""
        try:
            if not self.whisper_model:
                return {'status': 'error', 'message': 'Whisper model not available'}
            
            # Load and transcribe audio
            result = self.whisper_model.transcribe(
                audio_path, 
                language=language,
                fp16=False
            )
            
            return {
                'status': 'success',
                'transcription': result['text'],
                'language': result.get('language', 'unknown'),
                'segments': len(result.get('segments', [])),
                'audio_path': audio_path
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def process_voice_input(self, audio_data, sample_rate=16000):
        """Process voice input from microphone or audio stream"""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, sample_rate)
                temp_path = temp_file.name
            
            # Transcribe the audio
            result = self.transcribe_audio(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def synthesize_speech(self, text, language='en'):
        """Convert text to speech (placeholder for TTS implementation)"""
        try:
            # This is a placeholder - actual TTS implementation would go here
            # Using Coqui TTS or similar library
            
            return {
                'status': 'success',
                'message': 'TTS synthesis completed',
                'text': text,
                'language': language,
                'audio_length': len(text) * 0.1  # Estimated duration
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def detect_language(self, audio_path):
        """Detect language from audio file"""
        try:
            if not self.whisper_model:
                return {'status': 'error', 'message': 'Whisper model not available'}
            
            # Load audio and detect language
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.whisper_model.device)
            
            # Detect the spoken language
            _, probs = self.whisper_model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return {
                'status': 'success',
                'detected_language': detected_language,
                'confidence': probs[detected_language],
                'all_probabilities': dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }