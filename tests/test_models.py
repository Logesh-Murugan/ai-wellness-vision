# test_models.py - Comprehensive tests for data models
import unittest
from datetime import datetime, timedelta
import json

from src.models.base import BaseModel, ValidationError, RequiredValidator, LengthValidator, ChoiceValidator
from src.models.user_models import UserSession, User, UserRole, SessionStatus
from src.models.health_models import HealthAnalysisResult, HealthCondition, FoodItem, EmotionDetection, AnalysisType, AnalysisStatus
from src.models.conversation_models import ConversationContext, MultilingualContent, ConversationMessage, MessageType, SentimentType

class TestBaseModel(unittest.TestCase):
    """Test base model functionality"""
    
    def test_base_model_creation(self):
        """Test basic model creation and validation"""
        model = BaseModel()
        
        # Check that ID and timestamps are set
        self.assertIsNotNone(model.id)
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)
    
    def test_model_serialization(self):
        """Test model to_dict and to_json methods"""
        model = BaseModel()
        
        # Test to_dict
        data = model.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        
        # Test to_json
        json_str = model.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test round-trip
        parsed_data = json.loads(json_str)
        self.assertEqual(data['id'], parsed_data['id'])
    
    def test_model_deserialization(self):
        """Test model from_dict and from_json methods"""
        original = BaseModel()
        data = original.to_dict()
        
        # Test from_dict
        restored = BaseModel.from_dict(data)
        self.assertEqual(original.id, restored.id)
        
        # Test from_json
        json_str = original.to_json()
        restored_from_json = BaseModel.from_json(json_str)
        self.assertEqual(original.id, restored_from_json.id)

class TestValidators(unittest.TestCase):
    """Test validation functionality"""
    
    def test_required_validator(self):
        """Test required field validation"""
        validator = RequiredValidator()
        
        self.assertTrue(validator.validate("test"))
        self.assertFalse(validator.validate(None))
        self.assertFalse(validator.validate(""))
    
    def test_length_validator(self):
        """Test length validation"""
        validator = LengthValidator(min_length=3, max_length=10)
        
        self.assertTrue(validator.validate("test"))
        self.assertFalse(validator.validate("ab"))  # Too short
        self.assertFalse(validator.validate("this is too long"))  # Too long
    
    def test_choice_validator(self):
        """Test choice validation"""
        validator = ChoiceValidator(['option1', 'option2', 'option3'])
        
        self.assertTrue(validator.validate('option1'))
        self.assertFalse(validator.validate('invalid_option'))

class TestUserModels(unittest.TestCase):
    """Test user-related models"""
    
    def test_user_session_creation(self):
        """Test UserSession model creation and validation"""
        session = UserSession(
            session_id="test_session_123",
            language_preference="en"
        )
        
        self.assertEqual(session.session_id, "test_session_123")
        self.assertEqual(session.language_preference, "en")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
    
    def test_user_session_conversation_history(self):
        """Test conversation history management"""
        session = UserSession(
            session_id="test_session_123",
            language_preference="en"
        )
        
        # Add conversation entry
        session.add_conversation_entry("Hello", "Hi there!", "text")
        
        self.assertEqual(len(session.conversation_history), 1)
        self.assertEqual(session.conversation_history[0]["message"], "Hello")
        self.assertEqual(session.conversation_history[0]["response"], "Hi there!")
    
    def test_user_session_analysis_history(self):
        """Test analysis history management"""
        session = UserSession(
            session_id="test_session_123",
            language_preference="en"
        )
        
        # Add analysis entry
        result = {"prediction": "healthy", "confidence": 0.85}
        session.add_analysis_entry("skin_condition", result)
        
        self.assertEqual(len(session.analysis_history), 1)
        self.assertEqual(session.analysis_history[0]["analysis_type"], "skin_condition")
    
    def test_user_model(self):
        """Test User model functionality"""
        user = User(
            user_id="user123",
            email="test@example.com",
            role=UserRole.USER
        )
        
        self.assertEqual(user.user_id, "user123")
        self.assertEqual(user.role, UserRole.USER)
        self.assertTrue(user.is_active)
        
        # Test feature access
        self.assertTrue(user.can_access_feature("chat"))
        self.assertFalse(user.can_access_feature("priority_support"))

class TestHealthModels(unittest.TestCase):
    """Test health analysis models"""
    
    def test_health_analysis_result(self):
        """Test HealthAnalysisResult model"""
        analysis = HealthAnalysisResult(
            analysis_id="analysis_123",
            analysis_type=AnalysisType.SKIN_CONDITION
        )
        
        self.assertEqual(analysis.analysis_id, "analysis_123")
        self.assertEqual(analysis.analysis_type, AnalysisType.SKIN_CONDITION)
        self.assertEqual(analysis.status, AnalysisStatus.PENDING)
    
    def test_health_analysis_predictions(self):
        """Test prediction management in health analysis"""
        analysis = HealthAnalysisResult(
            analysis_id="analysis_123",
            analysis_type=AnalysisType.SKIN_CONDITION
        )
        
        # Add predictions
        analysis.add_prediction("acne", 0.85, {"severity": "mild"})
        analysis.add_prediction("healthy", 0.15)
        
        self.assertEqual(len(analysis.predictions), 2)
        
        # Test top prediction
        top_prediction = analysis.get_top_prediction()
        self.assertEqual(top_prediction["label"], "acne")
        self.assertEqual(top_prediction["confidence"], 0.85)
    
    def test_food_item_model(self):
        """Test FoodItem model"""
        food = FoodItem(
            food_name="apple",
            confidence=0.95,
            category="fruit"
        )
        
        self.assertEqual(food.food_name, "apple")
        self.assertEqual(food.confidence, 0.95)
        
        # Test nutritional info
        food.add_nutritional_info("vitamin_c", 14.0, "mg")
        self.assertIn("vitamin_c", food.nutritional_info)
        self.assertEqual(food.nutritional_info["vitamin_c"]["value"], 14.0)
    
    def test_emotion_detection_model(self):
        """Test EmotionDetection model"""
        emotion = EmotionDetection(
            emotion="happy",
            confidence=0.88,
            intensity=0.7
        )
        
        self.assertEqual(emotion.emotion, "happy")
        self.assertEqual(emotion.confidence, 0.88)
        
        # Test secondary emotions
        emotion.add_secondary_emotion("excited", 0.65)
        self.assertEqual(len(emotion.additional_emotions), 1)
        
        # Test dominant emotion
        dominant = emotion.get_dominant_emotion()
        self.assertEqual(dominant, "happy")  # Should still be primary

class TestConversationModels(unittest.TestCase):
    """Test conversation and multilingual models"""
    
    def test_conversation_context(self):
        """Test ConversationContext model"""
        context = ConversationContext(
            context_id="context_123",
            user_id="user_123",
            language="en"
        )
        
        self.assertEqual(context.context_id, "context_123")
        self.assertEqual(context.user_id, "user_123")
        self.assertEqual(context.turn_count, 0)
    
    def test_conversation_context_entities(self):
        """Test entity management in conversation context"""
        context = ConversationContext(
            context_id="context_123",
            user_id="user_123",
            language="en"
        )
        
        # Add entities
        context.add_entity("health_condition", "headache")
        context.add_entity("health_condition", "fever")
        context.add_entity("body_part", "head")
        
        self.assertEqual(len(context.entities_mentioned["health_condition"]), 2)
        self.assertEqual(len(context.entities_mentioned["body_part"]), 1)
        
        # Test recent entities
        recent = context.get_recent_entities("health_condition", 1)
        self.assertEqual(recent, ["fever"])
    
    def test_multilingual_content(self):
        """Test MultilingualContent model"""
        content = MultilingualContent(
            content_id="content_123",
            content_type="response",
            original_language="en"
        )
        
        # Add translations
        content.add_translation("en", "Hello, how can I help you?")
        content.add_translation("hi", "नमस्ते, मैं आपकी कैसे सहायता कर सकता हूं?")
        content.add_translation("ta", "வணக்கம், நான் உங்களுக்கு எப்படி உதவ முடியும்?")
        
        self.assertEqual(len(content.translations), 3)
        
        # Test translation retrieval
        english_text = content.get_translation("en")
        self.assertEqual(english_text, "Hello, how can I help you?")
        
        hindi_text = content.get_translation("hi")
        self.assertIsNotNone(hindi_text)
    
    def test_conversation_message(self):
        """Test ConversationMessage model"""
        message = ConversationMessage(
            message_id="msg_123",
            session_id="session_123",
            content="I have a headache",
            message_type=MessageType.TEXT
        )
        
        self.assertEqual(message.message_id, "msg_123")
        self.assertEqual(message.content, "I have a headache")
        self.assertTrue(message.is_user_message)
        
        # Test question detection
        question_msg = ConversationMessage(
            message_id="msg_124",
            session_id="session_123",
            content="What should I do for my headache?",
            message_type=MessageType.TEXT
        )
        self.assertTrue(question_msg.is_question())
        
        # Test keyword extraction
        keywords = message.extract_keywords()
        self.assertIn("headache", keywords)

class TestModelIntegration(unittest.TestCase):
    """Test integration between different models"""
    
    def test_session_with_analysis_integration(self):
        """Test integration between UserSession and HealthAnalysisResult"""
        # Create session
        session = UserSession(
            session_id="integration_test_123",
            language_preference="en"
        )
        
        # Create analysis
        analysis = HealthAnalysisResult(
            analysis_id="analysis_integration_123",
            analysis_type=AnalysisType.SKIN_CONDITION,
            session_id=session.session_id
        )
        
        analysis.add_prediction("healthy_skin", 0.92)
        analysis.set_completed(1.5)
        
        # Add analysis to session
        session.add_analysis_entry(
            analysis.analysis_type.value,
            analysis.to_dict()
        )
        
        self.assertEqual(len(session.analysis_history), 1)
        self.assertEqual(session.analysis_history[0]["analysis_type"], "skin_condition")
    
    def test_conversation_with_multilingual_integration(self):
        """Test integration between conversation and multilingual content"""
        # Create conversation context
        context = ConversationContext(
            context_id="multilingual_test_123",
            user_id="user_123",
            language="hi"
        )
        
        # Create multilingual content
        content = MultilingualContent(
            content_id="greeting_content",
            content_type="greeting",
            original_language="en"
        )
        
        content.add_translation("en", "Welcome to AI WellnessVision!")
        content.add_translation("hi", "AI वेलनेसविज़न में आपका स्वागत है!")
        
        # Get appropriate translation based on context language
        greeting = content.get_translation(context.language)
        self.assertIsNotNone(greeting)
        self.assertIn("वेलनेसविज़न", greeting)

if __name__ == '__main__':
    unittest.main()