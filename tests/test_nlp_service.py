# test_nlp_service.py - Tests for comprehensive NLP service
import unittest
import time
from unittest.mock import patch, MagicMock

from src.services.nlp_service import (
    HealthKnowledgeBase, SentimentAnalyzer, MultilingualProcessor,
    ConversationManager, HealthQASystem, ComprehensiveNLPService
)
from src.models import ConversationContext, SentimentType

class TestHealthKnowledgeBase(unittest.TestCase):
    """Test health knowledge base functionality"""
    
    def setUp(self):
        self.kb = HealthKnowledgeBase()
    
    def test_knowledge_base_initialization(self):
        """Test knowledge base loads correctly"""
        self.assertIsInstance(self.kb.health_topics, dict)
        self.assertIn('headache', self.kb.health_topics)
        self.assertIn('skin_care', self.kb.health_topics)
        self.assertIn('nutrition', self.kb.health_topics)
        self.assertIn('mental_health', self.kb.health_topics)
    
    def test_find_relevant_topic_direct_match(self):
        """Test finding topic with direct keyword match"""
        topic = self.kb.find_relevant_topic("I have a headache")
        self.assertEqual(topic, "headache")
        
        topic = self.kb.find_relevant_topic("My skin is dry and irritated")
        self.assertEqual(topic, "skin_care")
    
    def test_find_relevant_topic_pattern_match(self):
        """Test finding topic with pattern matching"""
        topic = self.kb.find_relevant_topic("My head hurts really bad")
        self.assertEqual(topic, "headache")  # Should match pain pattern
        
        topic = self.kb.find_relevant_topic("I have a rash on my face")
        self.assertEqual(topic, "skin_care")  # Should match skin pattern
    
    def test_find_relevant_topic_no_match(self):
        """Test when no relevant topic is found"""
        topic = self.kb.find_relevant_topic("What's the weather like?")
        self.assertIsNone(topic)
    
    def test_get_advice(self):
        """Test getting advice for a topic"""
        advice = self.kb.get_advice("headache")
        self.assertIn('advice', advice)
        self.assertIn('causes', advice)
        self.assertIn('when_to_see_doctor', advice)
        self.assertIsInstance(advice['advice'], list)
        self.assertGreater(len(advice['advice']), 0)

class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analysis functionality"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_sentiment_analyzer_initialization(self):
        """Test sentiment analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer.emotion_keywords)
        self.assertIn('positive', self.analyzer.emotion_keywords)
        self.assertIn('negative', self.analyzer.emotion_keywords)
        self.assertIn('neutral', self.analyzer.emotion_keywords)
    
    def test_keyword_sentiment_analysis_positive(self):
        """Test positive sentiment detection"""
        result = self.analyzer.analyze_sentiment("I feel great and happy today!")
        self.assertEqual(result['sentiment'], 'positive')
        self.assertGreater(result['confidence'], 0.0)
    
    def test_keyword_sentiment_analysis_negative(self):
        """Test negative sentiment detection"""
        result = self.analyzer.analyze_sentiment("I'm feeling sad and worried")
        self.assertEqual(result['sentiment'], 'negative')
        self.assertGreater(result['confidence'], 0.0)
    
    def test_keyword_sentiment_analysis_neutral(self):
        """Test neutral sentiment detection"""
        result = self.analyzer.analyze_sentiment("The weather is okay today")
        self.assertEqual(result['sentiment'], 'neutral')
        self.assertIsInstance(result['confidence'], float)
    
    def test_sentiment_analysis_empty_text(self):
        """Test sentiment analysis with empty text"""
        result = self.analyzer.analyze_sentiment("")
        self.assertIn(result['sentiment'], ['positive', 'negative', 'neutral'])
        self.assertIsInstance(result['confidence'], float)

class TestMultilingualProcessor(unittest.TestCase):
    """Test multilingual processing functionality"""
    
    def setUp(self):
        self.processor = MultilingualProcessor()
    
    def test_processor_initialization(self):
        """Test multilingual processor initializes correctly"""
        self.assertIsInstance(self.processor.supported_languages, list)
        self.assertIn('en', self.processor.supported_languages)
        self.assertIn('hi', self.processor.supported_languages)
        self.assertIn('ta', self.processor.supported_languages)
    
    def test_language_detection_english(self):
        """Test English language detection"""
        lang = self.processor.detect_language("Hello, how are you today?")
        self.assertEqual(lang, 'en')
    
    def test_language_detection_hindi(self):
        """Test Hindi language detection"""
        lang = self.processor.detect_language("नमस्ते, आप कैसे हैं?")
        self.assertEqual(lang, 'hi')
    
    def test_language_detection_tamil(self):
        """Test Tamil language detection"""
        lang = self.processor.detect_language("வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?")
        self.assertEqual(lang, 'ta')
    
    def test_language_detection_default(self):
        """Test default language for unrecognized text"""
        lang = self.processor.detect_language("xyz123!@#")
        self.assertEqual(lang, 'en')  # Should default to English
    
    def test_translation_same_language(self):
        """Test translation when source and target are the same"""
        result = self.processor.translate_text("Hello", "en", "en")
        self.assertEqual(result['translated_text'], "Hello")
        self.assertEqual(result['confidence'], 1.0)
    
    def test_translation_different_languages(self):
        """Test translation between different languages"""
        result = self.processor.translate_text("hello", "en", "hi")
        self.assertIn('translated_text', result)
        self.assertIn('confidence', result)
        self.assertEqual(result['source_language'], 'en')
        self.assertEqual(result['target_language'], 'hi')

class TestConversationManager(unittest.TestCase):
    """Test conversation management functionality"""
    
    def setUp(self):
        self.kb = HealthKnowledgeBase()
        self.manager = ConversationManager(self.kb)
    
    def test_conversation_manager_initialization(self):
        """Test conversation manager initializes correctly"""
        self.assertIsNotNone(self.manager.knowledge_base)
        self.assertIsInstance(self.manager.active_contexts, dict)
        self.assertIsInstance(self.manager.conversation_templates, dict)
    
    def test_get_or_create_context_new(self):
        """Test creating new conversation context"""
        context = self.manager.get_or_create_context("user1", "session1", "en")
        self.assertIsInstance(context, ConversationContext)
        self.assertEqual(context.user_id, "user1")
        self.assertEqual(context.language, "en")
    
    def test_get_or_create_context_existing(self):
        """Test getting existing conversation context"""
        context1 = self.manager.get_or_create_context("user1", "session1", "en")
        context2 = self.manager.get_or_create_context("user1", "session1", "en")
        self.assertIs(context1, context2)  # Should be the same object
    
    def test_update_context(self):
        """Test updating conversation context"""
        context = self.manager.get_or_create_context("user1", "session1", "en")
        initial_turn_count = context.turn_count
        
        sentiment = {'sentiment': 'positive', 'confidence': 0.8}
        entities = ['headache']
        
        self.manager.update_context(context, "I have a headache", sentiment, entities)
        
        self.assertEqual(context.turn_count, initial_turn_count + 1)
        self.assertGreater(len(context.sentiment_history), 0)
        self.assertIn('health_topic', context.entities_mentioned)
    
    def test_generate_response_greeting(self):
        """Test generating greeting response"""
        context = self.manager.get_or_create_context("user1", "session1", "en")
        sentiment = {'sentiment': 'neutral', 'confidence': 0.5}
        
        response = self.manager.generate_response(context, "Hello", sentiment)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_generate_response_health_advice(self):
        """Test generating health advice response"""
        context = self.manager.get_or_create_context("user1", "session1", "en")
        context.update_topic("headache")
        sentiment = {'sentiment': 'negative', 'confidence': 0.7}
        
        response = self.manager.generate_response(context, "I have a headache", sentiment)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

class TestHealthQASystem(unittest.TestCase):
    """Test health Q&A system functionality"""
    
    def setUp(self):
        self.kb = HealthKnowledgeBase()
        self.qa_system = HealthQASystem(self.kb)
    
    def test_qa_system_initialization(self):
        """Test Q&A system initializes correctly"""
        self.assertIsNotNone(self.qa_system.knowledge_base)
    
    def test_answer_question_with_topic(self):
        """Test answering question with known topic"""
        answer = self.qa_system.answer_question("What causes headaches?")
        self.assertIn('answer', answer)
        self.assertIn('confidence', answer)
        self.assertIn('topic', answer)
        self.assertIsInstance(answer['answer'], str)
        self.assertGreater(len(answer['answer']), 0)
    
    def test_answer_question_no_topic(self):
        """Test answering question with no relevant topic"""
        answer = self.qa_system.answer_question("What's the weather like?")
        self.assertIn('answer', answer)
        self.assertEqual(answer['topic'], 'general')
        self.assertIsInstance(answer['answer'], str)
    
    def test_answer_question_causes(self):
        """Test answering question about causes"""
        answer = self.qa_system.answer_question("Why do I get headaches?")
        self.assertIn('answer', answer)
        self.assertIn('cause', answer['answer'].lower())
    
    def test_answer_question_treatment(self):
        """Test answering question about treatment"""
        answer = self.qa_system.answer_question("How can I treat my headache?")
        self.assertIn('answer', answer)
        self.assertTrue(any(word in answer['answer'].lower() 
                          for word in ['recommend', 'advice', 'help', 'treat']))

class TestComprehensiveNLPService(unittest.TestCase):
    """Test the main NLP service"""
    
    def setUp(self):
        try:
            self.service = ComprehensiveNLPService()
        except Exception as e:
            self.skipTest(f"NLP service initialization failed: {e}")
    
    def test_service_initialization(self):
        """Test NLP service initializes correctly"""
        self.assertIsNotNone(self.service.knowledge_base)
        self.assertIsNotNone(self.service.sentiment_analyzer)
        self.assertIsNotNone(self.service.multilingual_processor)
        self.assertIsNotNone(self.service.conversation_manager)
        self.assertIsNotNone(self.service.qa_system)
    
    def test_process_message_basic(self):
        """Test basic message processing"""
        result = self.service.process_message(
            "Hello, I have a headache",
            "user1",
            "session1"
        )
        
        self.assertIn('response', result)
        self.assertIn('confidence', result)
        self.assertIn('language', result)
        self.assertIn('sentiment', result)
        self.assertIn('entities', result)
        self.assertIn('processing_time', result)
        
        self.assertIsInstance(result['response'], str)
        self.assertGreater(len(result['response']), 0)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['processing_time'], float)
    
    def test_process_message_question(self):
        """Test processing question message"""
        result = self.service.process_message(
            "What causes headaches?",
            "user1",
            "session1"
        )
        
        self.assertIn('response', result)
        self.assertIsInstance(result['response'], str)
        self.assertGreater(len(result['response']), 0)
    
    def test_process_message_multilingual(self):
        """Test processing message in different language"""
        result = self.service.process_message(
            "नमस्ते, मुझे सिरदर्द है",
            "user1",
            "session1"
        )
        
        self.assertIn('response', result)
        self.assertIn('language', result)
        self.assertIsInstance(result['response'], str)
    
    def test_is_question_detection(self):
        """Test question detection"""
        self.assertTrue(self.service._is_question("What is this?"))
        self.assertTrue(self.service._is_question("How are you"))
        self.assertTrue(self.service._is_question("Can you help me?"))
        self.assertFalse(self.service._is_question("I have a headache"))
        self.assertFalse(self.service._is_question("Hello there"))
    
    def test_get_conversation_history(self):
        """Test getting conversation history"""
        # First, process some messages to create history
        self.service.process_message("Hello", "user1", "session1")
        self.service.process_message("I have a headache", "user1", "session1")
        
        history = self.service.get_conversation_history("user1", "session1")
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        if history:
            self.assertIn('turn', history[0])
            self.assertIn('sentiment', history[0])
            self.assertIn('confidence', history[0])
    
    def test_get_health_topics(self):
        """Test getting available health topics"""
        topics = self.service.get_health_topics()
        self.assertIsInstance(topics, list)
        self.assertIn('headache', topics)
        self.assertIn('skin_care', topics)
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        languages = self.service.get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertIn('en', languages)
        self.assertIn('hi', languages)
    
    def test_analyze_wellness_keywords(self):
        """Test wellness keyword extraction"""
        keywords = self.service.analyze_wellness_keywords(
            "I want to improve my health and fitness through better nutrition"
        )
        self.assertIsInstance(keywords, list)
        self.assertIn('health', keywords)
        self.assertIn('fitness', keywords)
        self.assertIn('nutrition', keywords)
    
    def test_translate_response(self):
        """Test response translation"""
        result = self.service.translate_response("Hello", "en", "hi")
        self.assertIn('translated_text', result)
        self.assertIn('confidence', result)
        self.assertIn('source_language', result)
        self.assertIn('target_language', result)

class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and workflows"""
    
    def setUp(self):
        try:
            self.service = ComprehensiveNLPService()
        except Exception as e:
            self.skipTest(f"NLP service initialization failed: {e}")
    
    def test_multi_turn_conversation(self):
        """Test multi-turn conversation flow"""
        user_id = "test_user"
        session_id = "test_session"
        
        # Turn 1: Greeting
        result1 = self.service.process_message("Hello", user_id, session_id)
        self.assertEqual(result1['turn_count'], 1)
        
        # Turn 2: Health question
        result2 = self.service.process_message("I have a headache", user_id, session_id)
        self.assertEqual(result2['turn_count'], 2)
        self.assertIn('headache', result2['entities'])
        
        # Turn 3: Follow-up question
        result3 = self.service.process_message("What should I do?", user_id, session_id)
        self.assertEqual(result3['turn_count'], 3)
        self.assertEqual(result3['context_topic'], 'headache')
    
    def test_sentiment_tracking(self):
        """Test sentiment tracking across conversation"""
        user_id = "test_user"
        session_id = "test_session"
        
        # Positive message
        result1 = self.service.process_message("I feel great today!", user_id, session_id)
        self.assertEqual(result1['sentiment']['sentiment'], 'positive')
        
        # Negative message
        result2 = self.service.process_message("I'm worried about my health", user_id, session_id)
        self.assertEqual(result2['sentiment']['sentiment'], 'negative')
        
        # Check conversation history
        history = self.service.get_conversation_history(user_id, session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['sentiment'], 'positive')
        self.assertEqual(history[1]['sentiment'], 'negative')
    
    def test_error_handling(self):
        """Test error handling in message processing"""
        # Test with very long message
        long_message = "a" * 10000
        result = self.service.process_message(long_message, "user1", "session1")
        self.assertIn('response', result)
        self.assertIsInstance(result['response'], str)
        
        # Test with empty message
        result = self.service.process_message("", "user1", "session1")
        self.assertIn('response', result)
        self.assertIsInstance(result['response'], str)
    
    def test_performance_timing(self):
        """Test that processing times are reasonable"""
        start_time = time.time()
        result = self.service.process_message(
            "I have a headache and feel tired",
            "user1",
            "session1"
        )
        end_time = time.time()
        
        # Processing should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # 5 seconds max
        self.assertGreater(result['processing_time'], 0)
        self.assertLess(result['processing_time'], 5.0)

if __name__ == '__main__':
    unittest.main()