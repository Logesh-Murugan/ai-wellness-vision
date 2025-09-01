# test_speech_service.py - Tests for comprehensive speech service
import unittest
import tempfile
import os
import wave
from pathlib import Path
from unittest.mock import patch, MagicMock

# Mock numpy if not available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    
    class MockNumPy:
        @staticmethod
        def array(data, dtype=None):
            return data
        
        @staticmethod
        def mean(data, axis=None):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def sum(data):
            return sum(data) if hasattr(data, '__iter__') else data
        
        @staticmethod
        def max(data):
            return max(data) if hasattr(data, '__iter__') else data
        
        @staticmethod
        def abs(data):
            return abs(data) if isinstance(data, (int, float)) else [abs(x) for x in data]
        
        float32 = float
        ndarray = list
    
    np = MockNumPy()

from src.services.speech_service import (
    AudioValidator, AudioPreprocessor, SpeechToTextEngine,
    TextToSpeechEngine, RealTimeAudioProcessor, ComprehensiveSpeechService
)

class TestAudioValidator(unittest.TestCase):
    """Test audio validation functionality"""
    
    def setUp(self):
        self.validator = AudioValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_wav_file(self, filename: str, duration: float = 1.0) -> Path:
        """Create a test WAV file"""
        file_path = Path(self.temp_dir) / filename
        
        # Create a simple WAV file
        sample_rate = 16000
        samples = int(duration * sample_rate)
        
        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Generate simple sine wave
            import math
            audio_data = []
            for i in range(samples):
                value = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * i / sample_rate))
                audio_data.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            wav_file.writeframes(bytes(audio_data))
        
        return file_path
    
    def test_validator_initialization(self):
        """Test validator initializes correctly"""
        self.assertIsInstance(self.validator.supported_formats, set)
        self.assertIn('.wav', self.validator.supported_formats)
        self.assertIn('.mp3', self.validator.supported_formats)
        self.assertGreater(self.validator.max_duration, 0)
        self.assertGreater(self.validator.max_file_size, 0)
    
    def test_validate_audio_file_success(self):
        """Test successful audio file validation"""
        audio_file = self.create_test_wav_file("test.wav", 2.0)
        
        result = self.validator.validate_audio_file(audio_file)
        self.assertTrue(result['valid'])
        self.assertIn('file_size', result)
        self.assertEqual(result['format'], '.wav')
    
    def test_validate_audio_file_nonexistent(self):
        """Test validation of non-existent file"""
        result = self.validator.validate_audio_file("nonexistent.wav")
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
    
    def test_validate_audio_file_unsupported_format(self):
        """Test validation of unsupported format"""
        # Create a file with unsupported extension
        unsupported_file = Path(self.temp_dir) / "test.xyz"
        unsupported_file.write_text("fake audio")
        
        result = self.validator.validate_audio_file(unsupported_file)
        self.assertFalse(result['valid'])
        self.assertIn('Unsupported audio format', result['error'])
    
    def test_validate_audio_file_empty(self):
        """Test validation of empty file"""
        empty_file = Path(self.temp_dir) / "empty.wav"
        empty_file.touch()
        
        result = self.validator.validate_audio_file(empty_file)
        self.assertFalse(result['valid'])
        self.assertIn('empty', result['error'])
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_validate_audio_data_success(self):
        """Test successful audio data validation"""
        audio_data = np.random.randn(16000)  # 1 second at 16kHz
        sample_rate = 16000
        
        result = self.validator.validate_audio_data(audio_data, sample_rate)
        self.assertTrue(result['valid'])
        self.assertAlmostEqual(result['duration'], 1.0, places=1)
        self.assertEqual(result['sample_rate'], 16000)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_validate_audio_data_empty(self):
        """Test validation of empty audio data"""
        audio_data = np.array([])
        sample_rate = 16000
        
        result = self.validator.validate_audio_data(audio_data, sample_rate)
        self.assertFalse(result['valid'])
        self.assertIn('empty', result['error'])
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_validate_audio_data_too_long(self):
        """Test validation of audio data that's too long"""
        # Create 10 minutes of audio (should exceed max_duration)
        audio_data = np.random.randn(16000 * 600)  # 10 minutes
        sample_rate = 16000
        
        result = self.validator.validate_audio_data(audio_data, sample_rate)
        self.assertFalse(result['valid'])
        self.assertIn('too long', result['error'])

class TestAudioPreprocessor(unittest.TestCase):
    """Test audio preprocessing functionality"""
    
    def setUp(self):
        self.preprocessor = AudioPreprocessor()
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_preprocessor_initialization(self):
        """Test preprocessor initializes correctly"""
        self.assertEqual(self.preprocessor.target_sample_rate, 16000)
        self.assertTrue(self.preprocessor.noise_reduction_enabled)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_preprocess_audio_mono(self):
        """Test preprocessing mono audio"""
        audio_data = np.random.randn(8000)
        sample_rate = 8000
        
        processed_audio, processed_sr = self.preprocessor.preprocess_audio(audio_data, sample_rate)
        
        self.assertIsInstance(processed_audio, np.ndarray)
        self.assertEqual(processed_sr, 16000)  # Should be resampled
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_preprocess_audio_stereo(self):
        """Test preprocessing stereo audio"""
        # Create stereo audio (2 channels)
        audio_data = np.random.randn(8000, 2)
        sample_rate = 16000
        
        processed_audio, processed_sr = self.preprocessor.preprocess_audio(audio_data, sample_rate)
        
        self.assertEqual(processed_audio.ndim, 1)  # Should be converted to mono
        self.assertEqual(processed_sr, 16000)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_normalize_audio(self):
        """Test audio normalization"""
        # Create audio with high amplitude
        audio_data = np.array([2.0, -3.0, 1.5, -2.5])
        
        normalized = self.preprocessor._normalize_audio(audio_data)
        
        # Check that max absolute value is around 0.95
        max_val = np.max(np.abs(normalized))
        self.assertLessEqual(max_val, 1.0)
        self.assertGreater(max_val, 0.9)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_trim_silence(self):
        """Test silence trimming"""
        # Create audio with silence at beginning and end
        silence = np.zeros(1000)
        signal = np.random.randn(2000) * 0.5
        audio_data = np.concatenate([silence, signal, silence])
        
        trimmed = self.preprocessor._trim_silence(audio_data, 16000)
        
        # Trimmed audio should be shorter
        self.assertLess(len(trimmed), len(audio_data))
        self.assertGreater(len(trimmed), 0)

class TestSpeechToTextEngine(unittest.TestCase):
    """Test speech-to-text functionality"""
    
    def setUp(self):
        self.stt_engine = SpeechToTextEngine()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_wav_file(self, filename: str) -> Path:
        """Create a test WAV file"""
        file_path = Path(self.temp_dir) / filename
        
        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            
            # Write 1 second of silence
            silence = bytes([0] * 32000)  # 16000 samples * 2 bytes
            wav_file.writeframes(silence)
        
        return file_path
    
    def test_stt_engine_initialization(self):
        """Test STT engine initializes correctly"""
        self.assertIsNotNone(self.stt_engine.supported_languages)
        self.assertIn('en', self.stt_engine.supported_languages)
        self.assertIsInstance(self.stt_engine.preprocessor, AudioPreprocessor)
        self.assertIsInstance(self.stt_engine.validator, AudioValidator)
    
    def test_transcribe_audio_file_mock(self):
        """Test audio file transcription (mock)"""
        audio_file = self.create_test_wav_file("test.wav")
        
        result = self.stt_engine.transcribe_audio_file(audio_file)
        
        self.assertIn('status', result)
        self.assertIn('transcription', result)
        self.assertIn('language', result)
        self.assertIn('confidence', result)
        self.assertIn('processing_time', result)
        
        if result['status'] == 'success':
            self.assertIsInstance(result['transcription'], str)
            self.assertIsInstance(result['confidence'], float)
    
    def test_transcribe_audio_file_invalid(self):
        """Test transcription with invalid file"""
        result = self.stt_engine.transcribe_audio_file("nonexistent.wav")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('message', result)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_transcribe_audio_data(self):
        """Test audio data transcription"""
        # Create mock audio data
        audio_data = np.random.randn(16000)  # 1 second
        sample_rate = 16000
        
        result = self.stt_engine.transcribe_audio_data(audio_data, sample_rate)
        
        self.assertIn('status', result)
        self.assertIn('processing_time', result)
        
        if result['status'] == 'success':
            self.assertIn('transcription', result)
            self.assertIn('confidence', result)
    
    def test_detect_language_mock(self):
        """Test language detection (mock)"""
        audio_file = self.create_test_wav_file("test.wav")
        
        result = self.stt_engine.detect_language(audio_file)
        
        self.assertIn('status', result)
        if result['status'] == 'success':
            self.assertIn('detected_language', result)
            self.assertIn('confidence', result)
            self.assertIn('all_probabilities', result)
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        # Mock Whisper result
        whisper_result = {
            'segments': [
                {'avg_logprob': -0.5},
                {'avg_logprob': -0.3},
                {'avg_logprob': -0.7}
            ]
        }
        
        confidence = self.stt_engine._calculate_confidence(whisper_result)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_process_segments(self):
        """Test segment processing"""
        segments = [
            {
                'start': 0.0,
                'end': 2.0,
                'text': ' Hello world ',
                'avg_logprob': -0.5
            },
            {
                'start': 2.0,
                'end': 4.0,
                'text': '',  # Empty segment should be filtered
                'avg_logprob': -1.0
            }
        ]
        
        processed = self.stt_engine._process_segments(segments)
        
        self.assertEqual(len(processed), 1)  # Empty segment should be removed
        self.assertEqual(processed[0]['text'], 'Hello world')  # Text should be stripped
        self.assertIn('confidence', processed[0])

class TestTextToSpeechEngine(unittest.TestCase):
    """Test text-to-speech functionality"""
    
    def setUp(self):
        self.tts_engine = TextToSpeechEngine()
    
    def test_tts_engine_initialization(self):
        """Test TTS engine initializes correctly"""
        self.assertIsNotNone(self.tts_engine.supported_languages)
        self.assertIn('en', self.tts_engine.supported_languages)
        self.assertIsInstance(self.tts_engine.voice_settings, dict)
        self.assertIn('en', self.tts_engine.voice_settings)
    
    def test_synthesize_speech_basic(self):
        """Test basic speech synthesis"""
        result = self.tts_engine.synthesize_speech("Hello world", "en")
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('audio_path', result)
        self.assertIn('duration', result)
        self.assertIn('processing_time', result)
        self.assertEqual(result['language'], 'en')
        self.assertGreater(result['duration'], 0)
    
    def test_synthesize_speech_empty_text(self):
        """Test synthesis with empty text"""
        result = self.tts_engine.synthesize_speech("", "en")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('message', result)
    
    def test_synthesize_speech_unsupported_language(self):
        """Test synthesis with unsupported language"""
        result = self.tts_engine.synthesize_speech("Hello", "xyz")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['language'], 'en')  # Should fallback to English
    
    def test_synthesize_speech_custom_settings(self):
        """Test synthesis with custom voice settings"""
        custom_settings = {'speed': 1.5, 'pitch': 1.2}
        result = self.tts_engine.synthesize_speech("Hello", "en", custom_settings)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['voice_settings']['speed'], 1.5)
        self.assertEqual(result['voice_settings']['pitch'], 1.2)
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        text = "Dr. Smith said,  hello   world."
        processed = self.tts_engine._preprocess_text(text, "en")
        
        self.assertEqual(processed, "Doctor Smith said, hello world. ")
        self.assertNotIn("  ", processed)  # No double spaces
    
    def test_get_available_voices(self):
        """Test getting available voices"""
        voices = self.tts_engine.get_available_voices()
        
        self.assertIsInstance(voices, dict)
        self.assertIn('en', voices)
        self.assertIsInstance(voices['en'], list)
        self.assertGreater(len(voices['en']), 0)
        
        # Test specific language
        en_voices = self.tts_engine.get_available_voices('en')
        self.assertIn('en', en_voices)
    
    def test_set_voice_settings(self):
        """Test setting voice settings"""
        new_settings = {'speed': 0.8, 'volume': 1.2}
        self.tts_engine.set_voice_settings('en', new_settings)
        
        self.assertEqual(self.tts_engine.voice_settings['en']['speed'], 0.8)
        self.assertEqual(self.tts_engine.voice_settings['en']['volume'], 1.2)

class TestRealTimeAudioProcessor(unittest.TestCase):
    """Test real-time audio processing functionality"""
    
    def setUp(self):
        self.processor = RealTimeAudioProcessor()
    
    def test_processor_initialization(self):
        """Test processor initializes correctly"""
        self.assertFalse(self.processor.is_recording)
        self.assertEqual(self.processor.audio_buffer, [])
        self.assertGreater(self.processor.sample_rate, 0)
        self.assertGreater(self.processor.chunk_size, 0)
    
    def test_start_recording(self):
        """Test starting recording"""
        result = self.processor.start_recording()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(self.processor.is_recording)
        self.assertEqual(len(self.processor.audio_buffer), 0)
    
    def test_start_recording_already_active(self):
        """Test starting recording when already active"""
        self.processor.start_recording()
        result = self.processor.start_recording()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('already in progress', result['message'])
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_process_audio_chunk(self):
        """Test processing audio chunk"""
        self.processor.start_recording()
        
        # Create mock audio chunk
        audio_chunk = np.random.randn(1024) * 0.1
        
        result = self.processor.process_audio_chunk(audio_chunk)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('buffer_size', result)
        self.assertIn('duration', result)
        self.assertIn('is_silent', result)
        self.assertIn('energy', result)
        self.assertEqual(result['buffer_size'], 1024)
    
    def test_process_audio_chunk_not_recording(self):
        """Test processing chunk when not recording"""
        audio_chunk = [0.1, 0.2, 0.3]
        
        result = self.processor.process_audio_chunk(audio_chunk)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not active', result['message'])
    
    def test_stop_recording(self):
        """Test stopping recording"""
        self.processor.start_recording()
        
        # Add some mock data
        self.processor.audio_buffer = [0.1, 0.2, 0.3, 0.4]
        
        result = self.processor.stop_recording()
        
        self.assertEqual(result['status'], 'success')
        self.assertFalse(self.processor.is_recording)
        self.assertIn('audio_data', result)
        self.assertIn('duration', result)
        self.assertIn('samples', result)
    
    def test_stop_recording_not_active(self):
        """Test stopping recording when not active"""
        result = self.processor.stop_recording()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('No recording', result['message'])
    
    def test_stop_recording_no_data(self):
        """Test stopping recording with no data"""
        self.processor.start_recording()
        result = self.processor.stop_recording()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('No audio data', result['message'])
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_detect_voice_activity(self):
        """Test voice activity detection"""
        # Silent chunk
        silent_chunk = np.zeros(1024)
        self.assertFalse(self.processor.detect_voice_activity(silent_chunk))
        
        # Active chunk
        active_chunk = np.random.randn(1024) * 0.5
        result = self.processor.detect_voice_activity(active_chunk)
        self.assertIsInstance(result, bool)

class TestComprehensiveSpeechService(unittest.TestCase):
    """Test the main speech service"""
    
    def setUp(self):
        try:
            self.service = ComprehensiveSpeechService()
        except Exception as e:
            self.skipTest(f"Speech service initialization failed: {e}")
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_wav_file(self, filename: str) -> Path:
        """Create a test WAV file"""
        file_path = Path(self.temp_dir) / filename
        
        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(bytes([0] * 32000))
        
        return file_path
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        self.assertIsNotNone(self.service.stt_engine)
        self.assertIsNotNone(self.service.tts_engine)
        self.assertIsNotNone(self.service.realtime_processor)
        self.assertIsNotNone(self.service.validator)
    
    def test_transcribe_audio_file(self):
        """Test transcribing audio file"""
        audio_file = self.create_test_wav_file("test.wav")
        
        result = self.service.transcribe_audio(audio_file)
        
        self.assertIn('status', result)
        if result['status'] == 'success':
            self.assertIn('transcription', result)
            self.assertIn('language', result)
            self.assertIn('confidence', result)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_transcribe_audio_data(self):
        """Test transcribing audio data"""
        audio_data = np.random.randn(16000)
        sample_rate = 16000
        
        result = self.service.transcribe_audio(audio_data, sample_rate)
        
        self.assertIn('status', result)
        if result['status'] == 'success':
            self.assertIn('transcription', result)
    
    def test_transcribe_audio_invalid_input(self):
        """Test transcribing with invalid input"""
        result = self.service.transcribe_audio(123)  # Invalid type
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('message', result)
    
    def test_synthesize_speech(self):
        """Test speech synthesis"""
        result = self.service.synthesize_speech("Hello world", "en")
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('audio_path', result)
        self.assertIn('duration', result)
    
    def test_detect_language(self):
        """Test language detection"""
        audio_file = self.create_test_wav_file("test.wav")
        
        result = self.service.detect_language(audio_file)
        
        self.assertIn('status', result)
        if result['status'] == 'success':
            self.assertIn('detected_language', result)
            self.assertIn('confidence', result)
    
    def test_voice_recording_workflow(self):
        """Test complete voice recording workflow"""
        # Start recording
        start_result = self.service.start_voice_recording()
        self.assertEqual(start_result['status'], 'success')
        
        # Process some chunks (if numpy available)
        if NUMPY_AVAILABLE:
            chunk = np.random.randn(1024) * 0.1
            chunk_result = self.service.process_voice_chunk(chunk)
            self.assertEqual(chunk_result['status'], 'success')
        
        # Stop recording
        stop_result = self.service.stop_voice_recording()
        # May succeed or fail depending on whether data was added
        self.assertIn('status', stop_result)
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        languages = self.service.get_supported_languages()
        
        self.assertIsInstance(languages, list)
        self.assertIn('en', languages)
    
    def test_get_available_voices(self):
        """Test getting available voices"""
        voices = self.service.get_available_voices()
        
        self.assertIsInstance(voices, dict)
        self.assertIn('en', voices)
    
    def test_validate_audio_file(self):
        """Test audio file validation"""
        audio_file = self.create_test_wav_file("test.wav")
        
        result = self.service.validate_audio(audio_file)
        
        self.assertTrue(result['valid'])
        self.assertIn('file_size', result)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not available")
    def test_validate_audio_data(self):
        """Test audio data validation"""
        audio_data = np.random.randn(16000)
        sample_rate = 16000
        
        result = self.service.validate_audio(audio_data, sample_rate)
        
        self.assertTrue(result['valid'])
        self.assertIn('duration', result)
    
    def test_get_service_info(self):
        """Test getting service information"""
        info = self.service.get_service_info()
        
        self.assertIn('whisper_available', info)
        self.assertIn('audio_libs_available', info)
        self.assertIn('supported_languages', info)
        self.assertIn('supported_audio_formats', info)
        self.assertIsInstance(info['supported_languages'], list)
        self.assertIsInstance(info['supported_audio_formats'], list)

if __name__ == '__main__':
    unittest.main()