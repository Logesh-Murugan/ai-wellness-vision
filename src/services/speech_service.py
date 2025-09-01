# speech_service.py - Enhanced speech processing service
import logging
import time
import tempfile
import os
import io
import wave
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime

# Optional imports with fallbacks
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available - using mock implementations")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logging.warning("Soundfile not available - using mock implementations")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available - using mock implementations")
    
    # Mock numpy for basic operations
    class MockNumPy:
        ndarray = list  # Mock ndarray type
        float32 = float
        
        @staticmethod
        def array(data, dtype=None):
            return list(data) if hasattr(data, '__iter__') else [data]
        
        @staticmethod
        def zeros(size):
            return [0.0] * size
        
        @staticmethod
        def mean(data, axis=None):
            if hasattr(data, '__iter__'):
                return sum(data) / len(data) if data else 0
            return data
        
        @staticmethod
        def sum(data):
            if hasattr(data, '__iter__'):
                return sum(data)
            return data
        
        @staticmethod
        def max(data):
            if hasattr(data, '__iter__'):
                return max(data) if data else 0
            return data
        
        @staticmethod
        def abs(data):
            if hasattr(data, '__iter__'):
                return [abs(x) for x in data]
            return abs(data)
        
        @staticmethod
        def concatenate(arrays):
            result = []
            for arr in arrays:
                result.extend(arr)
            return result
        
        @staticmethod
        def linspace(start, stop, num):
            if num <= 1:
                return [start]
            step = (stop - start) / (num - 1)
            return [start + i * step for i in range(num)]
        
        @staticmethod
        def interp(x, xp, fp):
            # Simple linear interpolation
            result = []
            for xi in x:
                # Find surrounding points
                for i in range(len(xp) - 1):
                    if xp[i] <= xi <= xp[i + 1]:
                        # Linear interpolation
                        t = (xi - xp[i]) / (xp[i + 1] - xp[i])
                        yi = fp[i] + t * (fp[i + 1] - fp[i])
                        result.append(yi)
                        break
                else:
                    # Outside range, use nearest
                    if xi <= xp[0]:
                        result.append(fp[0])
                    else:
                        result.append(fp[-1])
            return result
        
        @staticmethod
        def ones(size):
            return [1.0] * size
        
        @staticmethod
        def exp(x):
            import math
            if hasattr(x, '__iter__'):
                return [math.exp(xi) for xi in x]
            return math.exp(x)
    
    np = MockNumPy()

AUDIO_LIBS_AVAILABLE = SOUNDFILE_AVAILABLE and NUMPY_AVAILABLE

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - using mock implementations")

from src.config import ModelConfig, AppConfig
from src.models import ConversationMessage, MessageType, UserSession
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

class AudioValidator:
    """Validates audio files and data"""
    
    def __init__(self):
        self.supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}
        self.max_duration = 300  # 5 minutes max
        self.min_duration = 0.1  # 0.1 seconds min
        self.max_file_size = 50 * 1024 * 1024  # 50MB max
    
    def validate_audio_file(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate audio file format and properties"""
        try:
            audio_path = Path(audio_path)
            
            # Check if file exists
            if not audio_path.exists():
                raise ValueError(f"Audio file does not exist: {audio_path}")
            
            # Check file extension
            if audio_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
            
            # Check file size
            file_size = audio_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"Audio file too large: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError("Audio file is empty")
            
            # Try to get audio info if libraries are available
            audio_info = {}
            if AUDIO_LIBS_AVAILABLE:
                try:
                    with sf.SoundFile(audio_path) as f:
                        duration = len(f) / f.samplerate
                        audio_info = {
                            'duration': duration,
                            'sample_rate': f.samplerate,
                            'channels': f.channels,
                            'frames': len(f),
                            'format': f.format,
                            'subtype': f.subtype
                        }
                        
                        # Check duration limits
                        if duration > self.max_duration:
                            raise ValueError(f"Audio too long: {duration:.1f}s (max {self.max_duration}s)")
                        
                        if duration < self.min_duration:
                            raise ValueError(f"Audio too short: {duration:.1f}s (min {self.min_duration}s)")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze audio file: {e}")
                    # Still allow the file if basic checks passed
            
            return {
                'valid': True,
                'file_size': file_size,
                'format': audio_path.suffix.lower(),
                **audio_info
            }
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def validate_audio_data(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Validate raw audio data"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                # Basic validation without libraries
                if len(audio_data) == 0:
                    raise ValueError("Audio data is empty")
                return {'valid': True, 'duration': len(audio_data) / sample_rate}
            
            # Check data type and shape
            if not isinstance(audio_data, np.ndarray):
                raise ValueError("Audio data must be numpy array")
            
            if audio_data.size == 0:
                raise ValueError("Audio data is empty")
            
            # Calculate duration
            duration = len(audio_data) / sample_rate
            
            # Check duration limits
            if duration > self.max_duration:
                raise ValueError(f"Audio too long: {duration:.1f}s")
            
            if duration < self.min_duration:
                raise ValueError(f"Audio too short: {duration:.1f}s")
            
            # Check sample rate
            if sample_rate < 8000 or sample_rate > 48000:
                logger.warning(f"Unusual sample rate: {sample_rate}Hz")
            
            return {
                'valid': True,
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': 1 if audio_data.ndim == 1 else audio_data.shape[1],
                'samples': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Audio data validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }

class AudioPreprocessor:
    """Preprocesses audio for better recognition quality"""
    
    def __init__(self):
        self.target_sample_rate = 16000  # Whisper's preferred sample rate
        self.noise_reduction_enabled = True
    
    def preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, int]:
        """Preprocess audio data for better recognition"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                # Return as-is if libraries not available
                return audio_data, sample_rate
            
            # Convert to mono if stereo
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Normalize audio
            audio_data = self._normalize_audio(audio_data)
            
            # Resample if needed
            if sample_rate != self.target_sample_rate:
                audio_data = self._resample_audio(audio_data, sample_rate, self.target_sample_rate)
                sample_rate = self.target_sample_rate
            
            # Apply noise reduction if enabled
            if self.noise_reduction_enabled:
                audio_data = self._reduce_noise(audio_data)
            
            # Remove silence from beginning and end
            audio_data = self._trim_silence(audio_data, sample_rate)
            
            logger.debug(f"Audio preprocessed: {len(audio_data)} samples at {sample_rate}Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            # Return original data on error
            return audio_data, sample_rate
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95  # Prevent clipping
        return audio_data
    
    def _resample_audio(self, audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        # Simple resampling - in production, use librosa or scipy
        if orig_sr == target_sr:
            return audio_data
        
        # Basic linear interpolation resampling
        ratio = target_sr / orig_sr
        new_length = int(len(audio_data) * ratio)
        
        # Create new time indices
        old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
        new_indices = np.linspace(0, len(audio_data) - 1, new_length)
        
        # Interpolate
        resampled = np.interp(new_indices, old_indices, audio_data)
        
        logger.debug(f"Resampled from {orig_sr}Hz to {target_sr}Hz")
        return resampled
    
    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply basic noise reduction"""
        # Simple high-pass filter to remove low-frequency noise
        # In production, use more sophisticated noise reduction
        if len(audio_data) < 100:
            return audio_data
        
        # Simple moving average filter
        window_size = min(5, len(audio_data) // 10)
        if window_size > 1:
            kernel = np.ones(window_size) / window_size
            filtered = np.convolve(audio_data, kernel, mode='same')
            return filtered
        
        return audio_data
    
    def _trim_silence(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Remove silence from beginning and end"""
        # Simple energy-based silence detection
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        energy_threshold = 0.01
        
        if len(audio_data) < frame_length * 2:
            return audio_data
        
        # Calculate frame energies
        energies = []
        for i in range(0, len(audio_data) - frame_length, frame_length):
            frame = audio_data[i:i + frame_length]
            energy = np.sum(frame ** 2) / len(frame)
            energies.append(energy)
        
        if not energies:
            return audio_data
        
        # Find start and end of speech
        start_frame = 0
        end_frame = len(energies) - 1
        
        for i, energy in enumerate(energies):
            if energy > energy_threshold:
                start_frame = max(0, i - 1)  # Include one frame before
                break
        
        for i in range(len(energies) - 1, -1, -1):
            if energies[i] > energy_threshold:
                end_frame = min(len(energies) - 1, i + 1)  # Include one frame after
                break
        
        # Convert back to sample indices
        start_sample = start_frame * frame_length
        end_sample = min(len(audio_data), (end_frame + 1) * frame_length)
        
        trimmed = audio_data[start_sample:end_sample]
        
        if len(trimmed) > 0:
            logger.debug(f"Trimmed silence: {len(audio_data)} -> {len(trimmed)} samples")
            return trimmed
        
        return audio_data

class SpeechToTextEngine:
    """Enhanced speech-to-text engine with Whisper integration"""
    
    def __init__(self):
        self.whisper_model = self._load_whisper_model()
        self.supported_languages = AppConfig.SUPPORTED_LANGUAGES
        self.preprocessor = AudioPreprocessor()
        self.validator = AudioValidator()
    
    def _load_whisper_model(self):
        """Load Whisper model for speech recognition"""
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available - using mock implementation")
            return None
        
        try:
            model_size = ModelConfig.WHISPER_MODEL_SIZE
            model = whisper.load_model(model_size)
            logger.info(f"Loaded Whisper model: {model_size}")
            return model
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return None
    
    @log_performance()
    def transcribe_audio_file(self, audio_path: Union[str, Path], 
                             language: str = None) -> Dict[str, Any]:
        """Transcribe audio file to text"""
        try:
            start_time = time.time()
            
            # Validate audio file
            validation = self.validator.validate_audio_file(audio_path)
            if not validation['valid']:
                return {
                    'status': 'error',
                    'message': f"Audio validation failed: {validation['error']}",
                    'processing_time': time.time() - start_time
                }
            
            # Use Whisper if available
            if self.whisper_model:
                result = self._whisper_transcribe(audio_path, language)
            else:
                result = self._mock_transcribe(audio_path, language)
            
            result['processing_time'] = time.time() - start_time
            result['audio_info'] = validation
            
            logger.info(f"Audio transcription completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0
            }
    
    def _whisper_transcribe(self, audio_path: Union[str, Path], language: str = None) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        try:
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                str(audio_path),
                language=language,
                fp16=False,
                verbose=False
            )
            
            return {
                'status': 'success',
                'transcription': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'confidence': self._calculate_confidence(result),
                'segments': self._process_segments(result.get('segments', [])),
                'method': 'whisper'
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'status': 'error',
                'message': f"Whisper transcription failed: {str(e)}",
                'method': 'whisper'
            }
    
    def _mock_transcribe(self, audio_path: Union[str, Path], language: str = None) -> Dict[str, Any]:
        """Mock transcription for when Whisper is not available"""
        # Generate mock transcription based on file properties
        audio_path = Path(audio_path)
        mock_texts = [
            "Hello, I have a question about my health.",
            "I'm feeling tired and have a headache.",
            "Can you help me with nutrition advice?",
            "I want to improve my wellness routine.",
            "What should I do about my skin condition?"
        ]
        
        import random
        mock_text = random.choice(mock_texts)
        
        return {
            'status': 'success',
            'transcription': mock_text,
            'language': language or 'en',
            'confidence': 0.85,
            'segments': [
                {
                    'start': 0.0,
                    'end': 3.0,
                    'text': mock_text,
                    'confidence': 0.85
                }
            ],
            'method': 'mock'
        }
    
    def _calculate_confidence(self, whisper_result: Dict[str, Any]) -> float:
        """Calculate overall confidence from Whisper segments"""
        segments = whisper_result.get('segments', [])
        if not segments:
            return 0.5
        
        # Average the confidence scores from segments
        confidences = []
        for segment in segments:
            # Whisper doesn't always provide confidence, estimate from other factors
            if 'avg_logprob' in segment:
                # Convert log probability to confidence (rough approximation)
                confidence = max(0.0, min(1.0, np.exp(segment['avg_logprob'])))
                confidences.append(confidence)
            else:
                confidences.append(0.8)  # Default confidence
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _process_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and clean up Whisper segments"""
        processed_segments = []
        
        for segment in segments:
            processed_segment = {
                'start': segment.get('start', 0.0),
                'end': segment.get('end', 0.0),
                'text': segment.get('text', '').strip(),
                'confidence': max(0.0, min(1.0, np.exp(segment.get('avg_logprob', -1.0))))
            }
            
            if processed_segment['text']:  # Only include non-empty segments
                processed_segments.append(processed_segment)
        
        return processed_segments
    
    @log_performance()
    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int,
                             language: str = None) -> Dict[str, Any]:
        """Transcribe raw audio data"""
        try:
            start_time = time.time()
            
            # Validate audio data
            validation = self.validator.validate_audio_data(audio_data, sample_rate)
            if not validation['valid']:
                return {
                    'status': 'error',
                    'message': f"Audio validation failed: {validation['error']}",
                    'processing_time': time.time() - start_time
                }
            
            # Preprocess audio
            processed_audio, processed_sr = self.preprocessor.preprocess_audio(audio_data, sample_rate)
            
            # Save to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
                if AUDIO_LIBS_AVAILABLE:
                    sf.write(temp_path, processed_audio, processed_sr)
                else:
                    # Create a minimal WAV file without soundfile
                    self._write_wav_file(temp_path, processed_audio, processed_sr)
            
            try:
                # Transcribe the temporary file
                result = self.transcribe_audio_file(temp_path, language)
                result['preprocessing_applied'] = True
                result['original_sample_rate'] = sample_rate
                result['processed_sample_rate'] = processed_sr
                
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
            
        except Exception as e:
            logger.error(f"Audio data transcription failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0
            }
    
    def _write_wav_file(self, filename: str, audio_data: np.ndarray, sample_rate: int):
        """Write WAV file without soundfile library"""
        try:
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
                
        except Exception as e:
            logger.error(f"Failed to write WAV file: {e}")
            raise
    
    def detect_language(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        """Detect language from audio file"""
        try:
            if not self.whisper_model:
                # Mock language detection
                return {
                    'status': 'success',
                    'detected_language': 'en',
                    'confidence': 0.7,
                    'all_probabilities': {'en': 0.7, 'hi': 0.2, 'ta': 0.1},
                    'method': 'mock'
                }
            
            # Load audio for language detection
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.whisper_model.device)
            
            # Detect language
            _, probs = self.whisper_model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return {
                'status': 'success',
                'detected_language': detected_language,
                'confidence': probs[detected_language],
                'all_probabilities': dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]),
                'method': 'whisper'
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

class TextToSpeechEngine:
    """Text-to-speech engine with multiple synthesis options"""
    
    def __init__(self):
        self.supported_languages = AppConfig.SUPPORTED_LANGUAGES
        self.tts_models = {}
        self.voice_settings = self._load_voice_settings()
    
    def _load_voice_settings(self) -> Dict[str, Dict[str, Any]]:
        """Load voice settings for different languages"""
        return {
            'en': {
                'voice_id': 'en_us_female',
                'speed': 1.0,
                'pitch': 1.0,
                'volume': 1.0
            },
            'hi': {
                'voice_id': 'hi_in_female',
                'speed': 0.9,
                'pitch': 1.1,
                'volume': 1.0
            },
            'ta': {
                'voice_id': 'ta_in_female',
                'speed': 0.9,
                'pitch': 1.0,
                'volume': 1.0
            }
        }
    
    @log_performance()
    def synthesize_speech(self, text: str, language: str = 'en',
                         voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert text to speech"""
        try:
            start_time = time.time()
            
            # Validate input
            if not text or not text.strip():
                return {
                    'status': 'error',
                    'message': 'Text is empty',
                    'processing_time': time.time() - start_time
                }
            
            if language not in self.supported_languages:
                logger.warning(f"Unsupported language: {language}, using English")
                language = 'en'
            
            # Get voice settings
            settings = self.voice_settings.get(language, self.voice_settings['en'])
            if voice_settings:
                settings.update(voice_settings)
            
            # Preprocess text
            processed_text = self._preprocess_text(text, language)
            
            # Generate speech (mock implementation)
            result = self._mock_synthesize(processed_text, language, settings)
            
            result['processing_time'] = time.time() - start_time
            result['original_text'] = text
            result['processed_text'] = processed_text
            result['language'] = language
            result['voice_settings'] = settings
            
            logger.info(f"Speech synthesis completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0
            }
    
    def _preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for better synthesis"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Handle abbreviations and numbers (basic preprocessing)
        if language == 'en':
            text = text.replace('Dr.', 'Doctor')
            text = text.replace('Mr.', 'Mister')
            text = text.replace('Mrs.', 'Missus')
            text = text.replace('&', 'and')
        
        # Add pauses for better speech flow
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace(';', '; ')
        
        return text.strip()
    
    def _mock_synthesize(self, text: str, language: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Mock speech synthesis"""
        # Calculate estimated duration based on text length and speed
        words_per_minute = 150 * settings.get('speed', 1.0)
        word_count = len(text.split())
        estimated_duration = (word_count / words_per_minute) * 60
        
        # Generate mock audio file path
        timestamp = int(time.time())
        mock_audio_path = f"mock_audio_{timestamp}_{language}.wav"
        
        return {
            'status': 'success',
            'audio_path': mock_audio_path,
            'duration': estimated_duration,
            'word_count': word_count,
            'character_count': len(text),
            'method': 'mock_tts'
        }
    
    def get_available_voices(self, language: str = None) -> Dict[str, List[str]]:
        """Get available voices for languages"""
        voices = {
            'en': ['en_us_female', 'en_us_male', 'en_uk_female', 'en_uk_male'],
            'hi': ['hi_in_female', 'hi_in_male'],
            'ta': ['ta_in_female', 'ta_in_male'],
            'te': ['te_in_female', 'te_in_male'],
            'bn': ['bn_in_female', 'bn_in_male']
        }
        
        if language:
            return {language: voices.get(language, [])}
        
        return voices
    
    def set_voice_settings(self, language: str, settings: Dict[str, Any]) -> None:
        """Update voice settings for a language"""
        if language in self.voice_settings:
            self.voice_settings[language].update(settings)
        else:
            self.voice_settings[language] = settings
        
        logger.info(f"Updated voice settings for {language}: {settings}")

class RealTimeAudioProcessor:
    """Handles real-time audio processing for voice interactions"""
    
    def __init__(self):
        self.is_recording = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.silence_threshold = 0.01
        self.silence_duration = 2.0  # seconds of silence to stop recording
    
    def start_recording(self) -> Dict[str, Any]:
        """Start real-time audio recording"""
        try:
            if self.is_recording:
                return {
                    'status': 'error',
                    'message': 'Recording already in progress'
                }
            
            self.is_recording = True
            self.audio_buffer = []
            
            logger.info("Started real-time audio recording")
            return {
                'status': 'success',
                'message': 'Recording started',
                'sample_rate': self.sample_rate,
                'chunk_size': self.chunk_size
            }
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> Dict[str, Any]:
        """Process a chunk of real-time audio"""
        try:
            if not self.is_recording:
                return {
                    'status': 'error',
                    'message': 'Recording not active'
                }
            
            # Add chunk to buffer
            self.audio_buffer.extend(audio_chunk)
            
            # Check for silence
            energy = np.sum(audio_chunk ** 2) / len(audio_chunk)
            is_silent = energy < self.silence_threshold
            
            # Calculate current duration
            current_duration = len(self.audio_buffer) / self.sample_rate
            
            return {
                'status': 'success',
                'buffer_size': len(self.audio_buffer),
                'duration': current_duration,
                'is_silent': is_silent,
                'energy': float(energy)
            }
            
        except Exception as e:
            logger.error(f"Audio chunk processing failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def stop_recording(self) -> Dict[str, Any]:
        """Stop recording and return audio data"""
        try:
            if not self.is_recording:
                return {
                    'status': 'error',
                    'message': 'No recording in progress'
                }
            
            self.is_recording = False
            
            if not self.audio_buffer:
                return {
                    'status': 'error',
                    'message': 'No audio data recorded'
                }
            
            # Convert buffer to numpy array
            audio_data = np.array(self.audio_buffer, dtype=np.float32)
            duration = len(audio_data) / self.sample_rate
            
            logger.info(f"Stopped recording: {duration:.2f}s, {len(audio_data)} samples")
            
            return {
                'status': 'success',
                'audio_data': audio_data,
                'sample_rate': self.sample_rate,
                'duration': duration,
                'samples': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def detect_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """Detect if audio chunk contains voice activity"""
        try:
            # Simple energy-based voice activity detection
            energy = np.sum(audio_chunk ** 2) / len(audio_chunk)
            return energy > self.silence_threshold
            
        except Exception as e:
            logger.error(f"Voice activity detection failed: {e}")
            return False

class ComprehensiveSpeechService:
    """Main speech service that orchestrates all speech processing capabilities"""
    
    def __init__(self):
        self.stt_engine = SpeechToTextEngine()
        self.tts_engine = TextToSpeechEngine()
        self.realtime_processor = RealTimeAudioProcessor()
        self.validator = AudioValidator()
        
        logger.info("Comprehensive Speech Service initialized")
    
    def transcribe_audio(self, audio_input: Union[str, Path, np.ndarray],
                        sample_rate: int = None, language: str = None) -> Dict[str, Any]:
        """Transcribe audio from file or data"""
        try:
            if isinstance(audio_input, (str, Path)):
                # File path input
                return self.stt_engine.transcribe_audio_file(audio_input, language)
            elif isinstance(audio_input, np.ndarray):
                # Audio data input
                if sample_rate is None:
                    raise ValueError("Sample rate required for audio data")
                return self.stt_engine.transcribe_audio_data(audio_input, sample_rate, language)
            else:
                raise ValueError("Invalid audio input type")
                
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def synthesize_speech(self, text: str, language: str = 'en',
                         voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert text to speech"""
        return self.tts_engine.synthesize_speech(text, language, voice_settings)
    
    def detect_language(self, audio_input: Union[str, Path]) -> Dict[str, Any]:
        """Detect language from audio"""
        return self.stt_engine.detect_language(audio_input)
    
    def start_voice_recording(self) -> Dict[str, Any]:
        """Start real-time voice recording"""
        return self.realtime_processor.start_recording()
    
    def process_voice_chunk(self, audio_chunk: np.ndarray) -> Dict[str, Any]:
        """Process real-time audio chunk"""
        return self.realtime_processor.process_audio_chunk(audio_chunk)
    
    def stop_voice_recording(self) -> Dict[str, Any]:
        """Stop voice recording and get audio data"""
        return self.realtime_processor.stop_recording()
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.stt_engine.supported_languages
    
    def get_available_voices(self, language: str = None) -> Dict[str, List[str]]:
        """Get available TTS voices"""
        return self.tts_engine.get_available_voices(language)
    
    def validate_audio(self, audio_input: Union[str, Path, np.ndarray],
                      sample_rate: int = None) -> Dict[str, Any]:
        """Validate audio input"""
        if isinstance(audio_input, (str, Path)):
            return self.validator.validate_audio_file(audio_input)
        elif isinstance(audio_input, np.ndarray):
            if sample_rate is None:
                raise ValueError("Sample rate required for audio data validation")
            return self.validator.validate_audio_data(audio_input, sample_rate)
        else:
            return {
                'valid': False,
                'error': 'Invalid audio input type'
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the speech service"""
        return {
            'whisper_available': WHISPER_AVAILABLE,
            'audio_libs_available': AUDIO_LIBS_AVAILABLE,
            'torch_available': TORCH_AVAILABLE,
            'supported_languages': self.get_supported_languages(),
            'supported_audio_formats': list(self.validator.supported_formats),
            'max_audio_duration': self.validator.max_duration,
            'max_file_size': self.validator.max_file_size
        }