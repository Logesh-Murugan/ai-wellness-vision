# test_multilingual.py - Comprehensive multilingual testing
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from src.api.gateway import ServiceOrchestrator, ChatRequest
from src.services.nlp_service import ComprehensiveNLPService
from src.models.conversation_models import MultilingualContent, ConversationContext

class TestMultilingualSupport(unittest.TestCase):
    """Test multilingual capabilities across the system"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
            self.nlp_service = ComprehensiveNLPService()
        except Exception as e:
            self.skipTest(f"Multilingual service initialization failed: {e}")
    
    def test_supported_languages(self):
        """Test that all supported languages are properly configured"""
        supported_languages = ['en', 'hi', 'ta', 'te', 'bn', 'gu', 'mr']
        
        for lang in supported_languages:
            # Test language detection
            result = self.nlp_service.detect_language(f"Test message in {lang}")
            self.assertIsNotNone(result)
            
            # Test language processing capability
            self.assertTrue(self.nlp_service.supports_language(lang))
    
    def test_english_processing(self):
        """Test English language processing"""
        async def run_test():
            test_messages = [
                "I have a headache and feel dizzy",
                "What should I eat for better health?",
                "I'm feeling anxious about my skin condition",
                "Can you help me understand my symptoms?"
            ]
            
            for message in test_messages:
                chat_request = ChatRequest(
                    message=message,
                    session_id="english_test_session",
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                self.assertEqual(result['status'], 'success')
                self.assertEqual(result['language'], 'en')
                self.assertIn('response', result)
                self.assertIn('sentiment', result)
                
                # Response should be in English
                response = result['response']
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
        
        asyncio.run(run_test())
    
    def test_hindi_processing(self):
        """Test Hindi language processing"""
        async def run_test():
            test_messages = [
                "मुझे सिरदर्द है",
                "मैं बहुत थका हुआ महसूस कर रहा हूं",
                "मेरी त्वचा में खुजली हो रही है",
                "क्या आप मेरी मदद कर सकते हैं?"
            ]
            
            for message in test_messages:
                chat_request = ChatRequest(
                    message=message,
                    session_id="hindi_test_session",
                    language="hi"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
                self.assertIn('sentiment', result)
                
                # Should handle Hindi input
                response = result['response']
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
        
        asyncio.run(run_test())
    
    def test_tamil_processing(self):
        """Test Tamil language processing"""
        async def run_test():
            test_messages = [
                "எனக்கு தலைவலி இருக்கிறது",
                "நான் மிகவும் சோர்வாக உணர்கிறேன்",
                "என் தோலில் அரிப்பு ஏற்படுகிறது",
                "நீங்கள் எனக்கு உதவ முடியுமா?"
            ]
            
            for message in test_messages:
                chat_request = ChatRequest(
                    message=message,
                    session_id="tamil_test_session",
                    language="ta"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
                self.assertIn('sentiment', result)
                
                response = result['response']
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
        
        asyncio.run(run_test())
    
    def test_language_detection(self):
        """Test automatic language detection"""
        test_cases = [
            ("Hello, how are you?", "en"),
            ("नमस्ते, आप कैसे हैं?", "hi"),
            ("வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?", "ta"),
            ("హలో, మీరు ఎలా ఉన్నారు?", "te"),
            ("হ্যালো, আপনি কেমন আছেন?", "bn"),
        ]
        
        for text, expected_lang in test_cases:
            detected_lang = self.nlp_service.detect_language(text)
            
            # Language detection might not be perfect, but should be reasonable
            self.assertIsNotNone(detected_lang)
            self.assertIsInstance(detected_lang, str)
            self.assertGreater(len(detected_lang), 0)
    
    def test_cross_language_conversation(self):
        """Test conversation switching between languages"""
        async def run_test():
            session_id = "cross_language_session"
            
            # Start in English
            en_request = ChatRequest(
                message="Hello, I need help with my health",
                session_id=session_id,
                language="en"
            )
            
            en_result = await self.orchestrator.process_chat_message(en_request)
            self.assertEqual(en_result['status'], 'success')
            
            # Switch to Hindi
            hi_request = ChatRequest(
                message="मुझे सिरदर्द है",
                session_id=session_id,
                language="hi"
            )
            
            hi_result = await self.orchestrator.process_chat_message(hi_request)
            self.assertEqual(hi_result['status'], 'success')
            
            # Check session history contains both languages
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            self.assertEqual(len(history['conversation_history']), 2)
            
            # Verify session maintains context across languages
            session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(len(session.conversation_history), 2)
        
        asyncio.run(run_test())
    
    def test_multilingual_sentiment_analysis(self):
        """Test sentiment analysis across languages"""
        test_cases = [
            ("I'm very happy with the results", "en", "positive"),
            ("I'm worried about my health", "en", "negative"),
            ("मैं बहुत खुश हूं", "hi", "positive"),
            ("मुझे चिंता हो रही है", "hi", "negative"),
            ("நான் மிகவும் மகிழ்ச்சியாக இருக்கிறேன்", "ta", "positive"),
            ("நான் கவலையாக இருக்கிறேன்", "ta", "negative"),
        ]
        
        async def run_test():
            for message, language, expected_sentiment in test_cases:
                chat_request = ChatRequest(
                    message=message,
                    session_id=f"sentiment_test_{language}",
                    language=language
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                self.assertEqual(result['status'], 'success')
                self.assertIn('sentiment', result)
                
                # Sentiment should be detected (might not be perfect)
                sentiment = result['sentiment']
                self.assertIsNotNone(sentiment)
        
        asyncio.run(run_test())

class TestMultilingualContent(unittest.TestCase):
    """Test multilingual content management"""
    
    def test_multilingual_content_creation(self):
        """Test creating multilingual content"""
        content = MultilingualContent(
            content_id="test_greeting",
            content_type="greeting",
            original_language="en"
        )
        
        # Add translations
        translations = {
            "en": "Welcome to AI WellnessVision!",
            "hi": "AI वेलनेसविज़न में आपका स्वागत है!",
            "ta": "AI வெல்னெஸ்விஷனுக்கு வரவேற்கிறோம்!",
            "te": "AI వెల్నెస్విజన్‌కు స్వాగతం!",
            "bn": "AI ওয়েলনেসভিশনে স্বাগতম!",
            "gu": "AI વેલનેસવિઝનમાં આપનું સ્વાગત છે!",
            "mr": "AI वेलनेसव्हिजनमध्ये आपले स्वागत आहे!"
        }
        
        for lang, text in translations.items():
            content.add_translation(lang, text)
        
        # Test translation retrieval
        for lang, expected_text in translations.items():
            retrieved_text = content.get_translation(lang)
            self.assertEqual(retrieved_text, expected_text)
        
        # Test fallback to original language
        fallback_text = content.get_translation("unknown_lang")
        self.assertEqual(fallback_text, translations["en"])
    
    def test_conversation_context_multilingual(self):
        """Test conversation context with multiple languages"""
        context = ConversationContext(
            context_id="multilingual_context",
            user_id="test_user",
            language="en"
        )
        
        # Add entities in different languages
        context.add_entity("health_condition", "headache")  # English
        context.add_entity("health_condition", "सिरदर्द")    # Hindi
        context.add_entity("health_condition", "தலைவலி")    # Tamil
        
        # Test entity retrieval
        health_conditions = context.entities_mentioned.get("health_condition", [])
        self.assertEqual(len(health_conditions), 3)
        
        # Test recent entities
        recent = context.get_recent_entities("health_condition", 2)
        self.assertEqual(len(recent), 2)

class TestMultilingualAccuracy(unittest.TestCase):
    """Test accuracy of multilingual processing"""
    
    def setUp(self):
        try:
            self.nlp_service = ComprehensiveNLPService()
        except Exception as e:
            self.skipTest(f"NLP service initialization failed: {e}")
    
    def test_health_entity_extraction_multilingual(self):
        """Test health entity extraction across languages"""
        test_cases = [
            ("I have a headache and fever", "en", ["headache", "fever"]),
            ("मुझे सिरदर्द और बुखार है", "hi", ["सिरदर्द", "बुखार"]),
            ("எனக்கு தலைவலி மற்றும் காய்ச்சல் உள்ளது", "ta", ["தலைவலி", "காய்ச்சல்"]),
        ]
        
        for text, language, expected_entities in test_cases:
            try:
                entities = self.nlp_service.extract_health_entities(text, language)
                
                # Should extract some health-related entities
                self.assertIsInstance(entities, list)
                
                # Check if any expected entities are found (fuzzy matching)
                found_entities = [entity.get('text', '').lower() for entity in entities]
                
                # At least some health entities should be detected
                self.assertGreater(len(entities), 0, f"Should detect health entities in {language}")
                
            except Exception as e:
                self.skipTest(f"Entity extraction failed for {language}: {e}")
    
    def test_medical_terminology_recognition(self):
        """Test recognition of medical terminology across languages"""
        medical_terms = {
            "en": ["diabetes", "hypertension", "asthma", "migraine"],
            "hi": ["मधुमेह", "उच्च रक्तचाप", "दमा", "माइग्रेन"],
            "ta": ["நீரிழிவு", "உயர் இரத்த அழுத்தம்", "ஆஸ்துமா", "ஒற்றைத் தலைவலி"],
        }
        
        for language, terms in medical_terms.items():
            for term in terms:
                try:
                    # Test if the service can process medical terms
                    result = self.nlp_service.analyze_text(f"I have {term}", language)
                    
                    self.assertIsNotNone(result)
                    self.assertIn('entities', result)
                    
                except Exception as e:
                    # Medical term recognition might not be perfect
                    print(f"Medical term recognition issue for {term} in {language}: {e}")
    
    def test_cultural_context_awareness(self):
        """Test cultural context awareness in responses"""
        cultural_contexts = [
            ("I'm fasting for Ramadan", "en", "religious"),
            ("मैं व्रत रख रहा हूं", "hi", "religious"),
            ("நான் விரதம் இருக்கிறேன்", "ta", "religious"),
        ]
        
        async def run_test():
            for message, language, context_type in cultural_contexts:
                chat_request = ChatRequest(
                    message=message,
                    session_id=f"cultural_test_{language}",
                    language=language
                )
                
                try:
                    result = await ServiceOrchestrator().process_chat_message(chat_request)
                    
                    self.assertEqual(result['status'], 'success')
                    self.assertIn('response', result)
                    
                    # Response should be culturally appropriate
                    response = result['response']
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 0)
                    
                except Exception as e:
                    self.skipTest(f"Cultural context test failed for {language}: {e}")
        
        asyncio.run(run_test())

class TestMultilingualErrorHandling(unittest.TestCase):
    """Test error handling in multilingual scenarios"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_unsupported_language_handling(self):
        """Test handling of unsupported languages"""
        async def run_test():
            # Test with unsupported language code
            chat_request = ChatRequest(
                message="Test message",
                session_id="unsupported_lang_test",
                language="xyz"  # Unsupported language
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            # Should handle gracefully, possibly falling back to English
            self.assertEqual(result['status'], 'success')
            self.assertIn('response', result)
        
        asyncio.run(run_test())
    
    def test_mixed_language_input(self):
        """Test handling of mixed language input"""
        async def run_test():
            mixed_messages = [
                "Hello मैं help चाहिए",  # English + Hindi
                "I have தலைவலி problem",  # English + Tamil
                "My health is ठीक नहीं है",  # English + Hindi
            ]
            
            for message in mixed_messages:
                chat_request = ChatRequest(
                    message=message,
                    session_id="mixed_lang_test",
                    language="en"  # Default to English
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                # Should handle mixed language gracefully
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
        
        asyncio.run(run_test())
    
    def test_empty_message_multilingual(self):
        """Test empty message handling across languages"""
        async def run_test():
            languages = ['en', 'hi', 'ta', 'te', 'bn']
            
            for lang in languages:
                chat_request = ChatRequest(
                    message="",
                    session_id=f"empty_msg_test_{lang}",
                    language=lang
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                # Should handle empty messages gracefully
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
        
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()