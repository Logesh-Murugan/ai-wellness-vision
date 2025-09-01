# Services package for AI WellnessVision
import logging

logger = logging.getLogger(__name__)

# Try to import full service, fall back to minimal service
try:
    from .image_service import (
        EnhancedImageRecognitionService,
        ModelManager,
        ImagePreprocessor,
        SkinAnalyzer,
        EyeHealthAnalyzer,
        FoodRecognizer,
        EmotionAnalyzer
    )
    ImageService = EnhancedImageRecognitionService
    FULL_SERVICE_AVAILABLE = True
    
    __all__ = [
        'EnhancedImageRecognitionService',
        'ImageService',
        'ModelManager',
        'ImagePreprocessor', 
        'SkinAnalyzer',
        'EyeHealthAnalyzer',
        'FoodRecognizer',
        'EmotionAnalyzer'
    ]
    
except ImportError:
    from .image_service_minimal import MinimalImageService
    ImageService = MinimalImageService
    FULL_SERVICE_AVAILABLE = False
    
    # Create placeholder classes for compatibility
    class ModelManager: pass
    class ImagePreprocessor: pass
    class SkinAnalyzer: pass
    class EyeHealthAnalyzer: pass
    class FoodRecognizer: pass
    class EmotionAnalyzer: pass
    
    EnhancedImageRecognitionService = MinimalImageService
    
    __all__ = [
        'ImageService',
        'MinimalImageService',
        'EnhancedImageRecognitionService',
        'ModelManager',
        'ImagePreprocessor', 
        'SkinAnalyzer',
        'EyeHealthAnalyzer',
        'FoodRecognizer',
        'EmotionAnalyzer'
    ]

# Import NLP service
try:
    from .nlp_service import (
        ComprehensiveNLPService,
        HealthKnowledgeBase,
        SentimentAnalyzer,
        MultilingualProcessor,
        ConversationManager,
        HealthQASystem
    )
    NLPService = ComprehensiveNLPService
    NLP_SERVICE_AVAILABLE = True
    
    __all__.extend([
        'NLPService',
        'ComprehensiveNLPService',
        'HealthKnowledgeBase',
        'SentimentAnalyzer',
        'MultilingualProcessor',
        'ConversationManager',
        'HealthQASystem'
    ])
    
except ImportError as e:
    logger.warning(f"NLP service not available: {e}")
    
    class MockNLPService:
        def __init__(self):
            pass
        
        def process_message(self, message, user_id, session_id, language=None):
            return {
                'response': 'NLP service not available - mock response',
                'confidence': 0.5,
                'language': language or 'en',
                'sentiment': {'sentiment': 'neutral', 'confidence': 0.5},
                'entities': [],
                'context_topic': 'general',
                'processing_time': 0.0,
                'turn_count': 1
            }
    
    NLPService = MockNLPService
    NLP_SERVICE_AVAILABLE = False
    
    __all__.extend(['NLPService'])

# Import Speech service
try:
    from .speech_service import (
        ComprehensiveSpeechService,
        SpeechToTextEngine,
        TextToSpeechEngine,
        AudioValidator,
        AudioPreprocessor,
        RealTimeAudioProcessor
    )
    SpeechService = ComprehensiveSpeechService
    SPEECH_SERVICE_AVAILABLE = True
    
    __all__.extend([
        'SpeechService',
        'ComprehensiveSpeechService',
        'SpeechToTextEngine',
        'TextToSpeechEngine',
        'AudioValidator',
        'AudioPreprocessor',
        'RealTimeAudioProcessor'
    ])
    
except ImportError as e:
    logger.warning(f"Speech service not available: {e}")
    
    class MockSpeechService:
        def __init__(self):
            pass
        
        def transcribe_audio(self, audio_input, sample_rate=None, language=None):
            return {
                'status': 'success',
                'transcription': 'Mock transcription - speech service not available',
                'language': language or 'en',
                'confidence': 0.5,
                'method': 'mock'
            }
        
        def synthesize_speech(self, text, language='en', voice_settings=None):
            return {
                'status': 'success',
                'audio_path': 'mock_audio.wav',
                'duration': len(text) * 0.1,
                'method': 'mock'
            }
        
        def get_supported_languages(self):
            return ['en', 'hi', 'ta', 'te', 'bn', 'gu', 'mr']
        
        def get_service_info(self):
            return {
                'whisper_available': False,
                'audio_libs_available': False,
                'supported_languages': self.get_supported_languages(),
                'method': 'mock'
            }
    
    SpeechService = MockSpeechService
    SPEECH_SERVICE_AVAILABLE = False
    
    __all__.extend(['SpeechService'])

# Import Explainable AI service
try:
    from .explainable_ai_service import (
        ComprehensiveExplainableAIService,
        GradCAMGenerator,
        LIMEExplainer,
        DecisionPathGenerator,
        VisualizationEngine
    )
    ExplainableAIService = ComprehensiveExplainableAIService
    EXPLAINABLE_AI_SERVICE_AVAILABLE = True
    
    __all__.extend([
        'ExplainableAIService',
        'ComprehensiveExplainableAIService',
        'GradCAMGenerator',
        'LIMEExplainer',
        'DecisionPathGenerator',
        'VisualizationEngine'
    ])
    
except ImportError as e:
    logger.warning(f"Explainable AI service not available: {e}")
    
    class MockExplainableAIService:
        def __init__(self):
            pass
        
        def explain_prediction(self, analysis_result, model=None, image_data=None, explanation_types=None):
            return {
                'status': 'success',
                'analysis_id': analysis_result.analysis_id if analysis_result else 'mock',
                'analysis_type': analysis_result.analysis_type.value if analysis_result else 'unknown',
                'explanations': {
                    'mock': {
                        'status': 'success',
                        'method': 'mock',
                        'message': 'Explainable AI service not available - mock explanation'
                    }
                },
                'summary': {
                    'analysis_type': 'mock',
                    'prediction_confidence': 0.5,
                    'explanation_methods': ['mock'],
                    'key_insights': ['Mock explanation generated'],
                    'reliability_score': 0.5
                },
                'processing_time': 0.1
            }
        
        def get_explanation_capabilities(self):
            return {
                'gradcam_available': False,
                'lime_available': False,
                'visualization_available': False,
                'supported_analysis_types': [],
                'explanation_methods': ['mock'],
                'method': 'mock'
            }
    
    ExplainableAIService = MockExplainableAIService
    EXPLAINABLE_AI_SERVICE_AVAILABLE = False
    
    __all__.extend(['ExplainableAIService'])