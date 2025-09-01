# nlp_service.py - Comprehensive NLP and conversation service
import logging
import time
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Optional imports with fallbacks
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - using mock implementations")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - using mock implementations")

from src.config import ModelConfig, AppConfig
from src.models import (
    ConversationContext, ConversationMessage, MultilingualContent, 
    MessageType, SentimentType, UserSession
)
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

class HealthKnowledgeBase:
    """Health domain knowledge base for Q&A"""
    
    def __init__(self):
        self.health_topics = self._load_health_knowledge()
        self.symptom_patterns = self._load_symptom_patterns()
        self.wellness_advice = self._load_wellness_advice()
    
    def _load_health_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Load health knowledge base"""
        return {
            "headache": {
                "symptoms": ["head pain", "migraine", "tension headache"],
                "causes": ["stress", "dehydration", "lack of sleep", "eye strain"],
                "advice": [
                    "Stay hydrated by drinking plenty of water",
                    "Get adequate rest and sleep",
                    "Practice stress management techniques",
                    "Consider over-the-counter pain relief if needed"
                ],
                "when_to_see_doctor": [
                    "Severe or sudden onset headache",
                    "Headache with fever, stiff neck, or vision changes",
                    "Frequent or worsening headaches"
                ]
            },
            "skin_care": {
                "symptoms": ["acne", "dry skin", "rash", "irritation"],
                "causes": ["hormones", "diet", "stress", "environmental factors"],
                "advice": [
                    "Maintain a consistent skincare routine",
                    "Use gentle, non-comedogenic products",
                    "Protect skin from sun exposure",
                    "Stay hydrated and eat a balanced diet"
                ],
                "when_to_see_doctor": [
                    "Persistent or worsening skin conditions",
                    "Signs of infection (pus, spreading redness)",
                    "Unusual moles or skin changes"
                ]
            },
            "nutrition": {
                "symptoms": ["fatigue", "digestive issues", "weight changes"],
                "causes": ["poor diet", "food sensitivities", "lifestyle factors"],
                "advice": [
                    "Eat a balanced diet with fruits and vegetables",
                    "Stay hydrated throughout the day",
                    "Practice portion control",
                    "Consider consulting a nutritionist"
                ],
                "when_to_see_doctor": [
                    "Unexplained weight loss or gain",
                    "Persistent digestive problems",
                    "Signs of nutritional deficiencies"
                ]
            },
            "mental_health": {
                "symptoms": ["anxiety", "depression", "stress", "mood changes"],
                "causes": ["life events", "chemical imbalances", "genetics", "environment"],
                "advice": [
                    "Practice mindfulness and meditation",
                    "Maintain social connections",
                    "Exercise regularly",
                    "Seek professional help when needed"
                ],
                "when_to_see_doctor": [
                    "Persistent feelings of sadness or anxiety",
                    "Thoughts of self-harm",
                    "Significant impact on daily functioning"
                ]
            }
        }
    
    def _load_symptom_patterns(self) -> Dict[str, List[str]]:
        """Load symptom recognition patterns"""
        return {
            "pain": [
                r"\b(hurt|pain|ache|sore|tender)\b",
                r"\b(headache|backache|stomachache)\b",
                r"\b(painful|aching|throbbing)\b"
            ],
            "skin": [
                r"\b(rash|acne|pimple|spot|blemish)\b",
                r"\b(dry|oily|irritated|red|itchy)\b",
                r"\b(skin|face|complexion)\b"
            ],
            "digestive": [
                r"\b(stomach|belly|tummy|gut)\b",
                r"\b(nausea|vomit|diarrhea|constipation)\b",
                r"\b(bloated|gassy|indigestion)\b"
            ],
            "mental": [
                r"\b(anxious|worried|stressed|depressed)\b",
                r"\b(sad|down|low|mood|emotional)\b",
                r"\b(sleep|tired|fatigue|energy)\b"
            ]
        }
    
    def _load_wellness_advice(self) -> Dict[str, List[str]]:
        """Load general wellness advice"""
        return {
            "general": [
                "Maintain a balanced diet with plenty of fruits and vegetables",
                "Stay hydrated by drinking adequate water daily",
                "Get regular exercise appropriate for your fitness level",
                "Ensure adequate sleep (7-9 hours for adults)",
                "Practice stress management techniques",
                "Schedule regular health check-ups"
            ],
            "preventive": [
                "Wash hands frequently to prevent infections",
                "Use sunscreen to protect against UV damage",
                "Don't smoke and limit alcohol consumption",
                "Maintain good posture, especially when working",
                "Take breaks from screen time to rest your eyes"
            ]
        }
    
    def find_relevant_topic(self, text: str) -> Optional[str]:
        """Find the most relevant health topic for the given text"""
        text_lower = text.lower()
        
        # Check for direct topic matches
        for topic in self.health_topics.keys():
            if topic in text_lower:
                return topic
        
        # Check symptom patterns
        topic_scores = {}
        for category, patterns in self.symptom_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                topic_scores[category] = score
        
        if topic_scores:
            # Map symptom categories to topics
            category_to_topic = {
                "pain": "headache",
                "skin": "skin_care", 
                "digestive": "nutrition",
                "mental": "mental_health"
            }
            
            best_category = max(topic_scores, key=topic_scores.get)
            return category_to_topic.get(best_category)
        
        return None
    
    def get_advice(self, topic: str) -> Dict[str, Any]:
        """Get advice for a specific health topic"""
        if topic in self.health_topics:
            return self.health_topics[topic]
        return {}

class SentimentAnalyzer:
    """Analyzes sentiment and emotional content of text"""
    
    def __init__(self):
        self.sentiment_pipeline = self._load_sentiment_model()
        self.emotion_keywords = self._load_emotion_keywords()
    
    def _load_sentiment_model(self):
        """Load sentiment analysis model"""
        if TRANSFORMERS_AVAILABLE:
            try:
                return pipeline("sentiment-analysis", 
                              model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                              return_all_scores=True)
            except Exception as e:
                logger.warning(f"Could not load sentiment model: {e}")
                return None
        return None
    
    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """Load emotion keyword mappings"""
        return {
            "positive": [
                "happy", "joy", "excited", "great", "wonderful", "amazing", 
                "good", "better", "excellent", "fantastic", "love", "like"
            ],
            "negative": [
                "sad", "angry", "frustrated", "upset", "worried", "anxious",
                "bad", "terrible", "awful", "hate", "dislike", "concerned"
            ],
            "neutral": [
                "okay", "fine", "normal", "average", "usual", "regular"
            ]
        }
    
    @log_performance()
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            # Try using transformer model first
            if self.sentiment_pipeline:
                results = self.sentiment_pipeline(text)
                if results and len(results) > 0:
                    # Convert to our format
                    sentiment_map = {
                        "LABEL_0": "negative",
                        "LABEL_1": "neutral", 
                        "LABEL_2": "positive",
                        "NEGATIVE": "negative",
                        "NEUTRAL": "neutral",
                        "POSITIVE": "positive"
                    }
                    
                    best_result = max(results[0], key=lambda x: x['score'])
                    sentiment = sentiment_map.get(best_result['label'], 'neutral')
                    confidence = best_result['score']
                    
                    return {
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'method': 'transformer'
                    }
            
            # Fallback to keyword-based analysis
            return self._keyword_sentiment_analysis(text)
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._keyword_sentiment_analysis(text)
    
    def _keyword_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based sentiment analysis"""
        text_lower = text.lower()
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for sentiment, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[sentiment] += 1
        
        # Determine dominant sentiment
        if scores["positive"] > scores["negative"]:
            sentiment = "positive"
            confidence = min(scores["positive"] / (sum(scores.values()) + 1), 1.0)
        elif scores["negative"] > scores["positive"]:
            sentiment = "negative"
            confidence = min(scores["negative"] / (sum(scores.values()) + 1), 1.0)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'method': 'keyword',
            'scores': scores
        }

class MultilingualProcessor:
    """Handles multilingual text processing and translation"""
    
    def __init__(self):
        self.supported_languages = AppConfig.SUPPORTED_LANGUAGES
        self.language_patterns = self._load_language_patterns()
        self.translation_cache = {}
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load language detection patterns"""
        return {
            "en": [
                r"\b(the|and|or|but|in|on|at|to|for|of|with|by)\b",
                r"\b(hello|hi|how|what|when|where|why|who)\b"
            ],
            "hi": [
                r"[\u0900-\u097F]+",  # Devanagari script
                r"\b(और|या|में|से|के|की|को|है|हैं|था|थे)\b"
            ],
            "ta": [
                r"[\u0B80-\u0BFF]+",  # Tamil script
                r"\b(மற்றும்|அல்லது|இல்|இன்|க்கு|ஆகும்|உள்ளது)\b"
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of input text"""
        if not text.strip():
            return AppConfig.DEFAULT_LANGUAGE
        
        text_lower = text.lower()
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                language_scores[lang] = score
        
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            logger.debug(f"Detected language: {detected_lang}")
            return detected_lang
        
        # Default to English if no patterns match
        return AppConfig.DEFAULT_LANGUAGE
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text between languages (mock implementation)"""
        # In production, this would use a real translation service
        cache_key = f"{source_lang}_{target_lang}_{hash(text)}"
        
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Mock translation for demonstration
        if source_lang == target_lang:
            translated_text = text
            confidence = 1.0
        else:
            # Simple mock translation
            translations = {
                ("en", "hi"): {
                    "hello": "नमस्ते",
                    "how are you": "आप कैसे हैं",
                    "thank you": "धन्यवाद"
                },
                ("en", "ta"): {
                    "hello": "வணக்கம்",
                    "how are you": "நீங்கள் எப்படி இருக்கிறீர்கள்",
                    "thank you": "நன்றி"
                }
            }
            
            translation_dict = translations.get((source_lang, target_lang), {})
            translated_text = translation_dict.get(text.lower(), f"[{target_lang}] {text}")
            confidence = 0.7 if text.lower() in translation_dict else 0.3
        
        result = {
            'translated_text': translated_text,
            'source_language': source_lang,
            'target_language': target_lang,
            'confidence': confidence,
            'method': 'mock_translation'
        }
        
        self.translation_cache[cache_key] = result
        return result

class ConversationManager:
    """Manages conversation context and multi-turn dialogue"""
    
    def __init__(self, knowledge_base: HealthKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.active_contexts = {}
        self.conversation_templates = self._load_conversation_templates()
    
    def _load_conversation_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load conversation response templates"""
        return {
            "greeting": {
                "en": [
                    "Hello! I'm here to help with your health and wellness questions.",
                    "Hi there! How can I assist you with your wellness journey today?",
                    "Welcome! I'm ready to help you with health-related questions."
                ],
                "hi": [
                    "नमस्ते! मैं आपके स्वास्थ्य और कल्याण के सवालों में मदद के लिए यहाँ हूँ।",
                    "आपका स्वागत है! आज मैं आपकी कैसे सहायता कर सकता हूँ?"
                ],
                "ta": [
                    "வணக்கம்! உங்கள் உடல்நலம் மற்றும் நல்வாழ்வு கேள்விகளுக்கு உதவ நான் இங்கே இருக்கிறேன்।",
                    "வரவேற்கிறேன்! இன்று உங்கள் நல்வாழ்வு பயணத்தில் நான் எப்படி உதவ முடியும்?"
                ]
            },
            "health_advice": {
                "en": [
                    "Based on what you've described, here are some suggestions:",
                    "I understand your concern. Here's what I recommend:",
                    "Thank you for sharing. Here are some helpful tips:"
                ],
                "hi": [
                    "आपने जो बताया है, उसके आधार पर यहाँ कुछ सुझाव हैं:",
                    "मैं आपकी चिंता समझता हूँ। यहाँ मेरी सिफारिश है:"
                ],
                "ta": [
                    "நீங்கள் விவரித்ததின் அடிப்படையில், இங்கே சில பரிந்துரைகள்:",
                    "உங்கள் கவலையை நான் புரிந்துகொள்கிறேன். இதோ என் பரிந்துரை:"
                ]
            },
            "clarification": {
                "en": [
                    "Could you tell me more about your symptoms?",
                    "Can you provide more details about what you're experiencing?",
                    "I'd like to help better. Could you describe your situation more?"
                ],
                "hi": [
                    "क्या आप अपने लक्षणों के बारे में और बता सकते हैं?",
                    "क्या आप अपने अनुभव के बारे में और विवरण दे सकते हैं?"
                ],
                "ta": [
                    "உங்கள் அறிகுறிகளைப் பற்றி மேலும் சொல்ல முடியுமா?",
                    "நீங்கள் அனுபவிப்பதைப் பற்றி மேலும் விவரங்களை வழங்க முடியுமா?"
                ]
            }
        }
    
    def get_or_create_context(self, user_id: str, session_id: str, language: str = "en") -> ConversationContext:
        """Get existing context or create new one"""
        context_key = f"{user_id}_{session_id}"
        
        if context_key not in self.active_contexts:
            context = ConversationContext(
                context_id=context_key,
                user_id=user_id,
                language=language,
                session_id=session_id
            )
            self.active_contexts[context_key] = context
        
        return self.active_contexts[context_key]
    
    def update_context(self, context: ConversationContext, message: str, 
                      sentiment: Dict[str, Any], entities: List[str]) -> None:
        """Update conversation context with new information"""
        # Add sentiment
        sentiment_value = sentiment['sentiment'].upper()
        if sentiment_value == 'NEUTRAL':
            sentiment_type = SentimentType.NEUTRAL
        elif sentiment_value == 'POSITIVE':
            sentiment_type = SentimentType.POSITIVE
        elif sentiment_value == 'NEGATIVE':
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL  # Default fallback
        
        context.add_sentiment_entry(sentiment_type, sentiment['confidence'], message)
        
        # Add entities
        for entity in entities:
            context.add_entity("health_topic", entity)
        
        # Increment turn counter
        context.increment_turn()
        
        # Update topic if health-related
        topic = self.knowledge_base.find_relevant_topic(message)
        if topic:
            context.update_topic(topic)
    
    def generate_response(self, context: ConversationContext, message: str, 
                         sentiment: Dict[str, Any]) -> str:
        """Generate contextual response"""
        language = context.language
        
        # Determine response type
        if context.turn_count == 0 or any(greeting in message.lower() 
                                        for greeting in ["hello", "hi", "hey", "नमस्ते", "வணக்கம்"]):
            response_type = "greeting"
        elif context.current_topic != "general":
            response_type = "health_advice"
        else:
            response_type = "clarification"
        
        # Get template
        templates = self.conversation_templates.get(response_type, {})
        language_templates = templates.get(language, templates.get("en", []))
        
        if not language_templates:
            return "I'm here to help with your health questions."
        
        import random
        base_response = random.choice(language_templates)
        
        # Add specific advice if health topic identified
        if response_type == "health_advice" and context.current_topic != "general":
            advice = self.knowledge_base.get_advice(context.current_topic)
            if advice and "advice" in advice:
                advice_text = "\n• " + "\n• ".join(advice["advice"][:3])
                base_response += advice_text
                
                if "when_to_see_doctor" in advice:
                    if language == "en":
                        base_response += "\n\nConsider seeing a healthcare professional if you experience:"
                    elif language == "hi":
                        base_response += "\n\nयदि आप निम्नलिखित अनुभव करते हैं तो स्वास्थ्य पेशेवर से मिलने पर विचार करें:"
                    elif language == "ta":
                        base_response += "\n\nநீங்கள் பின்வருவனவற்றை அனுபவித்தால் சுகாதார நிபுணரைப் பார்க்க வேண்டும்:"
                    
                    doctor_advice = "\n• " + "\n• ".join(advice["when_to_see_doctor"])
                    base_response += doctor_advice
        
        return base_response

class HealthQASystem:
    """Health-specific question answering system"""
    
    def __init__(self, knowledge_base: HealthKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.qa_pipeline = self._load_qa_model()
    
    def _load_qa_model(self):
        """Load question answering model"""
        if TRANSFORMERS_AVAILABLE:
            try:
                return pipeline("question-answering", 
                              model="distilbert-base-cased-distilled-squad")
            except Exception as e:
                logger.warning(f"Could not load QA model: {e}")
                return None
        return None
    
    def answer_question(self, question: str, context_topic: str = None) -> Dict[str, Any]:
        """Answer health-related questions"""
        try:
            # Find relevant topic
            topic = context_topic or self.knowledge_base.find_relevant_topic(question)
            
            if not topic:
                return {
                    'answer': "I'd be happy to help with health questions. Could you tell me more about what you're experiencing?",
                    'confidence': 0.5,
                    'topic': 'general',
                    'method': 'fallback'
                }
            
            # Get knowledge base information
            topic_info = self.knowledge_base.get_advice(topic)
            
            if not topic_info:
                return {
                    'answer': "I don't have specific information about that topic, but I recommend consulting with a healthcare professional.",
                    'confidence': 0.3,
                    'topic': topic,
                    'method': 'fallback'
                }
            
            # Try using QA model if available
            if self.qa_pipeline and topic_info:
                context_text = self._build_context_text(topic_info)
                try:
                    result = self.qa_pipeline(question=question, context=context_text)
                    return {
                        'answer': result['answer'],
                        'confidence': result['score'],
                        'topic': topic,
                        'method': 'transformer_qa'
                    }
                except Exception as e:
                    logger.warning(f"QA model failed: {e}")
            
            # Fallback to knowledge base response
            return self._knowledge_base_response(question, topic, topic_info)
            
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return {
                'answer': "I'm sorry, I encountered an error. Please try rephrasing your question.",
                'confidence': 0.1,
                'topic': 'error',
                'method': 'error'
            }
    
    def _build_context_text(self, topic_info: Dict[str, Any]) -> str:
        """Build context text for QA model"""
        context_parts = []
        
        if 'advice' in topic_info:
            context_parts.append("Advice: " + " ".join(topic_info['advice']))
        
        if 'causes' in topic_info:
            context_parts.append("Common causes: " + " ".join(topic_info['causes']))
        
        if 'when_to_see_doctor' in topic_info:
            context_parts.append("See a doctor if: " + " ".join(topic_info['when_to_see_doctor']))
        
        return " ".join(context_parts)
    
    def _knowledge_base_response(self, question: str, topic: str, topic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response from knowledge base"""
        question_lower = question.lower()
        
        # Check what type of information is being asked
        if any(word in question_lower for word in ["cause", "why", "reason"]):
            if 'causes' in topic_info:
                answer = f"Common causes of {topic} include: " + ", ".join(topic_info['causes'])
                return {'answer': answer, 'confidence': 0.8, 'topic': topic, 'method': 'knowledge_base'}
        
        elif any(word in question_lower for word in ["treat", "help", "do", "advice"]):
            if 'advice' in topic_info:
                answer = f"For {topic}, I recommend: " + "; ".join(topic_info['advice'])
                return {'answer': answer, 'confidence': 0.8, 'topic': topic, 'method': 'knowledge_base'}
        
        elif any(word in question_lower for word in ["doctor", "medical", "serious"]):
            if 'when_to_see_doctor' in topic_info:
                answer = f"Consider seeing a healthcare professional if you have: " + "; ".join(topic_info['when_to_see_doctor'])
                return {'answer': answer, 'confidence': 0.8, 'topic': topic, 'method': 'knowledge_base'}
        
        # Default response with general advice
        if 'advice' in topic_info:
            answer = f"For {topic}, here are some general recommendations: " + "; ".join(topic_info['advice'][:2])
            return {'answer': answer, 'confidence': 0.7, 'topic': topic, 'method': 'knowledge_base'}
        
        return {
            'answer': f"I have some information about {topic}. Could you be more specific about what you'd like to know?",
            'confidence': 0.5,
            'topic': topic,
            'method': 'knowledge_base'
        }

class ComprehensiveNLPService:
    """Main NLP service that orchestrates all NLP capabilities"""
    
    def __init__(self):
        self.knowledge_base = HealthKnowledgeBase()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.multilingual_processor = MultilingualProcessor()
        self.conversation_manager = ConversationManager(self.knowledge_base)
        self.qa_system = HealthQASystem(self.knowledge_base)
        
        logger.info("Comprehensive NLP Service initialized")
    
    @log_performance()
    def process_message(self, message: str, user_id: str, session_id: str, 
                       language: str = None) -> Dict[str, Any]:
        """Process a user message and generate response"""
        try:
            start_time = time.time()
            
            # Detect language if not provided
            if not language:
                language = self.multilingual_processor.detect_language(message)
            
            # Get or create conversation context
            context = self.conversation_manager.get_or_create_context(user_id, session_id, language)
            
            # Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze_sentiment(message)
            
            # Extract health-related entities/topics
            health_topic = self.knowledge_base.find_relevant_topic(message)
            entities = [health_topic] if health_topic else []
            
            # Update conversation context
            self.conversation_manager.update_context(context, message, sentiment, entities)
            
            # Generate response
            if self._is_question(message):
                # Use QA system for questions
                qa_result = self.qa_system.answer_question(message, context.current_topic)
                response_text = qa_result['answer']
                confidence = qa_result['confidence']
            else:
                # Use conversation manager for general dialogue
                response_text = self.conversation_manager.generate_response(context, message, sentiment)
                confidence = 0.8
            
            processing_time = time.time() - start_time
            
            result = {
                'response': response_text,
                'confidence': confidence,
                'language': language,
                'sentiment': sentiment,
                'entities': entities,
                'context_topic': context.current_topic,
                'processing_time': processing_time,
                'turn_count': context.turn_count
            }
            
            logger.info(f"Message processed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return {
                'response': "I'm sorry, I encountered an error processing your message. Please try again.",
                'confidence': 0.1,
                'language': language or 'en',
                'sentiment': {'sentiment': 'neutral', 'confidence': 0.5},
                'entities': [],
                'context_topic': 'error',
                'processing_time': 0.0,
                'turn_count': 0,
                'error': str(e)
            }
    
    def _is_question(self, message: str) -> bool:
        """Determine if message is a question"""
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would', 'should']
        message_lower = message.lower()
        
        return (message.endswith('?') or 
                any(indicator in message_lower for indicator in question_indicators))
    
    def get_conversation_history(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a user session"""
        context_key = f"{user_id}_{session_id}"
        
        if context_key in self.conversation_manager.active_contexts:
            context = self.conversation_manager.active_contexts[context_key]
            return [
                {
                    'turn': i,
                    'sentiment': entry['sentiment'],
                    'confidence': entry['confidence'],
                    'timestamp': entry['timestamp']
                }
                for i, entry in enumerate(context.sentiment_history)
            ]
        
        return []
    
    def get_health_topics(self) -> List[str]:
        """Get list of available health topics"""
        return list(self.knowledge_base.health_topics.keys())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.multilingual_processor.supported_languages
    
    def translate_response(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate response to target language"""
        return self.multilingual_processor.translate_text(text, source_lang, target_lang)
    
    def analyze_wellness_keywords(self, text: str) -> List[str]:
        """Extract wellness-related keywords from text"""
        wellness_keywords = [
            'health', 'wellness', 'fitness', 'nutrition', 'diet', 'exercise',
            'sleep', 'stress', 'mental', 'physical', 'emotional', 'wellbeing',
            'meditation', 'mindfulness', 'therapy', 'self-care'
        ]
        
        text_lower = text.lower()
        found_keywords = [keyword for keyword in wellness_keywords if keyword in text_lower]
        
        return found_keywords