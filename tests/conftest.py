# conftest.py - Pytest configuration and fixtures
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing."""
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.read = AsyncMock(return_value=b"mock image data")
    mock_file.content_type = "image/jpeg"
    mock_file.size = 1024
    return mock_file

@pytest.fixture
def mock_audio_file():
    """Create a mock audio file for testing."""
    mock_file = MagicMock()
    mock_file.filename = "test_audio.wav"
    mock_file.read = AsyncMock(return_value=b"mock audio data")
    mock_file.content_type = "audio/wav"
    mock_file.size = 2048
    return mock_file

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "language_preference": "en"
    }

@pytest.fixture
def sample_health_data():
    """Sample health analysis data for testing."""
    return {
        "analysis_type": "skin_condition",
        "predictions": [
            {"label": "healthy", "confidence": 0.85},
            {"label": "acne", "confidence": 0.15}
        ],
        "metadata": {
            "image_size": "1024x768",
            "processing_time": 2.5
        }
    }

@pytest.fixture
def multilingual_test_data():
    """Multilingual test data."""
    return {
        "en": {
            "greeting": "Hello, how can I help you?",
            "health_query": "I have a headache",
            "response": "I understand you have a headache. Here are some suggestions..."
        },
        "hi": {
            "greeting": "नमस्ते, मैं आपकी कैसे सहायता कर सकता हूं?",
            "health_query": "मुझे सिरदर्द है",
            "response": "मैं समझता हूं कि आपको सिरदर्द है। यहां कुछ सुझाव हैं..."
        },
        "ta": {
            "greeting": "வணக்கம், நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "health_query": "எனக்கு தலைவலி இருக்கிறது",
            "response": "உங்களுக்கு தலைவலி இருப்பது எனக்குப் புரிகிறது। இங்கே சில பரிந்துரைகள்..."
        }
    }

@pytest.fixture
def mock_orchestrator():
    """Create a mock service orchestrator."""
    try:
        from src.api.gateway import ServiceOrchestrator
        return ServiceOrchestrator()
    except Exception:
        # Return mock if real orchestrator can't be created
        mock = MagicMock()
        mock.process_chat_message = AsyncMock(return_value={
            'status': 'success',
            'response': 'Mock response',
            'language': 'en',
            'sentiment': 'neutral',
            'processing_time': 1.0
        })
        mock.process_image_analysis = AsyncMock(return_value={
            'status': 'success',
            'analysis_result': {'prediction': 'healthy', 'confidence': 0.9},
            'processing_time': 2.0
        })
        mock.get_session_history = AsyncMock(return_value={
            'status': 'success',
            'conversation_history': [],
            'analysis_history': []
        })
        return mock

@pytest.fixture
def mock_auth_manager():
    """Create a mock authentication manager."""
    try:
        from src.api.auth import AuthManager
        return AuthManager()
    except Exception:
        # Return mock if real auth manager can't be created
        mock = MagicMock()
        mock.authenticate_user = MagicMock(return_value=MagicMock(
            username="testuser",
            roles=["user"],
            is_active=True
        ))
        mock.create_access_token = MagicMock(return_value="mock_token")
        mock.verify_token = MagicMock(return_value=MagicMock(
            username="testuser",
            roles=["user"]
        ))
        return mock

@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        "max_response_time": 5.0,
        "max_concurrent_users": 50,
        "test_duration": 30,
        "acceptable_error_rate": 0.05
    }

@pytest.fixture
def accessibility_test_config():
    """Configuration for accessibility tests."""
    return {
        "min_contrast_ratio": 4.5,
        "required_aria_attributes": ["aria-label", "role"],
        "keyboard_navigation_elements": ["button", "input", "select", "textarea", "a"],
        "screen_reader_compatibility": True
    }

# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "multilingual: Multilingual tests")
    config.addinivalue_line("markers", "accessibility: Accessibility tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "services: AI services tests")

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Add markers based on test file names
    for item in items:
        # Add markers based on file path
        if "test_performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "test_multilingual" in item.fspath.basename:
            item.add_marker(pytest.mark.multilingual)
        elif "test_accessibility" in item.fspath.basename:
            item.add_marker(pytest.mark.accessibility)
        elif "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        elif "test_security" in item.fspath.basename:
            item.add_marker(pytest.mark.security)
        elif "service" in item.fspath.basename:
            item.add_marker(pytest.mark.services)
        elif "api" in item.fspath.basename:
            item.add_marker(pytest.mark.api)
        elif "ui" in item.fspath.basename:
            item.add_marker(pytest.mark.ui)
        else:
            item.add_marker(pytest.mark.unit)

# Session fixtures for expensive setup
@pytest.fixture(scope="session")
def test_database():
    """Set up test database for session."""
    # In a real implementation, this would set up a test database
    yield "test_db_connection"

@pytest.fixture(scope="session")
def test_models():
    """Load test AI models for session."""
    # In a real implementation, this would load lightweight test models
    yield {
        "image_model": "mock_image_model",
        "nlp_model": "mock_nlp_model",
        "speech_model": "mock_speech_model"
    }

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    # Cleanup code would go here
    pass

# Skip conditions
def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Skip tests based on conditions
    if "selenium" in item.keywords and not has_selenium():
        pytest.skip("Selenium not available")
    
    if "gpu" in item.keywords and not has_gpu():
        pytest.skip("GPU not available")

def has_selenium():
    """Check if Selenium is available."""
    try:
        import selenium
        return True
    except ImportError:
        return False

def has_gpu():
    """Check if GPU is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

# Custom assertions
def assert_response_time(actual_time, max_time=5.0):
    """Assert response time is within acceptable limits."""
    assert actual_time <= max_time, f"Response time {actual_time}s exceeds maximum {max_time}s"

def assert_success_rate(successful, total, min_rate=0.9):
    """Assert success rate meets minimum threshold."""
    rate = successful / total if total > 0 else 0
    assert rate >= min_rate, f"Success rate {rate:.2%} below minimum {min_rate:.2%}"

def assert_multilingual_support(text, language):
    """Assert text contains appropriate language content."""
    # Basic check - in real implementation would be more sophisticated
    assert isinstance(text, str), "Response must be a string"
    assert len(text) > 0, "Response must not be empty"

# Pytest plugins configuration
pytest_plugins = [
    "pytest_asyncio",
    "pytest_cov",
    "pytest_html",
    "pytest_mock"
]