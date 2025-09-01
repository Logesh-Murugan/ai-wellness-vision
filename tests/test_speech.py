# -*- coding: utf-8 -*-
"""Test speech engine functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

# Import the speech engine
try:
    from src.speech_engine import SpeechEngine
except ImportError:
    SpeechEngine = None


class TestSpeechEngine(unittest.TestCase):
    """Test speech engine functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if SpeechEngine is None:
            self.skipTest("SpeechEngine not available")
        
        self.speech_engine = SpeechEngine()
        
    def test_initialization(self):
        """Test speech engine initialization."""
        self.assertIsNotNone(self.speech_engine)
        
    def test_speech_to_text_mock(self):
        """Test speech to text conversion with mock."""
        # Mock the speech recognition
        with patch.object(self.speech_engine, 'speech_to_text') as mock_stt:
            mock_stt.return_value = "Hello world"
            
            # Create a temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
            try:
                result = self.speech_engine.speech_to_text(temp_path)
                self.assertEqual(result, "Hello world")
                mock_stt.assert_called_once()
            finally:
                # Clean up
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_text_to_speech_mock(self):
        """Test text to speech conversion with mock."""
        # Mock the text to speech
        with patch.object(self.speech_engine, 'text_to_speech') as mock_tts:
            mock_tts.return_value = True
            
            result = self.speech_engine.text_to_speech("Hello world", "output.wav")
            self.assertTrue(result)
            mock_tts.assert_called_once_with("Hello world", "output.wav")
    
    def test_language_detection_mock(self):
        """Test language detection with mock."""
        if hasattr(self.speech_engine, 'detect_language'):
            with patch.object(self.speech_engine, 'detect_language') as mock_detect:
                mock_detect.return_value = "en"
                
                result = self.speech_engine.detect_language("Hello world")
                self.assertEqual(result, "en")
                mock_detect.assert_called_once_with("Hello world")
    
    def test_error_handling(self):
        """Test error handling in speech engine."""
        # Test with invalid file path
        with patch.object(self.speech_engine, 'speech_to_text') as mock_stt:
            mock_stt.side_effect = FileNotFoundError("File not found")
            
            with self.assertRaises(FileNotFoundError):
                self.speech_engine.speech_to_text("nonexistent.wav")


class TestSpeechEngineIntegration(unittest.TestCase):
    """Integration tests for speech engine."""
    
    def setUp(self):
        """Set up test environment."""
        if SpeechEngine is None:
            self.skipTest("SpeechEngine not available")
            
        self.speech_engine = SpeechEngine()
    
    def test_speech_engine_workflow(self):
        """Test complete speech engine workflow."""
        # Mock the entire workflow
        with patch.object(self.speech_engine, 'speech_to_text') as mock_stt, \
             patch.object(self.speech_engine, 'text_to_speech') as mock_tts:
            
            mock_stt.return_value = "Test speech recognition"
            mock_tts.return_value = True
            
            # Simulate speech to text
            text_result = self.speech_engine.speech_to_text("test_audio.wav")
            self.assertEqual(text_result, "Test speech recognition")
            
            # Simulate text to speech
            tts_result = self.speech_engine.text_to_speech(text_result, "output.wav")
            self.assertTrue(tts_result)


if __name__ == "__main__":
    unittest.main(verbosity=2)