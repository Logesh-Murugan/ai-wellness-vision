# conversation_models.py - Conversation and multilingual data models
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseModel, add_validators, RequiredValidator, LengthValidator, ChoiceValidator

class MessageType(Enum):
    """Types of conversation messages"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    SYSTEM = "system"
    ERROR = "error"

class ConversationStatus(Enum):
    """Conversation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class SentimentType(Enum):
    """Sentiment analysis types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@add_validators({
    'context_id': [RequiredValidator(), LengthValidator(min_length=10)],
    'user_id': [RequiredValidator()],
    'language': [RequiredValidator(), ChoiceValidator(['en', 'hi', 'ta', 'te', 'bn', 'gu', 'mr'])],
})
@dataclass
class ConversationContext(BaseModel):
    """Model for managing conversation context and memory"""
    
    context_id: str = field(default="")  # Will be validated as required
    user_id: str = field(default="")  # Will be validated as required
    language: str = "en"
    session_id: Optional[str] = None
    current_topic: str = "general"
    entities_mentioned: Dict[str, List[str]] = field(default_factory=dict)
    sentiment_history: List[Dict[str, Any]] = field(default_factory=list)
    language: str = "en"
    turn_count: int = 0
    status: ConversationStatus = ConversationStatus.ACTIVE
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_entity(self, entity_type: str, entity_value: str) -> None:
        """Add an entity to the conversation context"""
        if entity_type not in self.entities_mentioned:
            self.entities_mentioned[entity_type] = []
        
        if entity_value not in self.entities_mentioned[entity_type]:
            self.entities_mentioned[entity_type].append(entity_value)
            self.updated_at = datetime.utcnow()
    
    def add_sentiment_entry(self, sentiment: SentimentType, confidence: float, text: str) -> None:
        """Add a sentiment analysis entry"""
        entry = {
            "sentiment": sentiment.value,
            "confidence": confidence,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "turn": self.turn_count
        }
        self.sentiment_history.append(entry)
        self.updated_at = datetime.utcnow()
    
    def increment_turn(self) -> None:
        """Increment conversation turn counter"""
        self.turn_count += 1
        self.updated_at = datetime.utcnow()
    
    def get_recent_entities(self, entity_type: str, limit: int = 5) -> List[str]:
        """Get recently mentioned entities of a specific type"""
        entities = self.entities_mentioned.get(entity_type, [])
        return entities[-limit:] if entities else []
    
    def get_sentiment_trend(self, recent_turns: int = 5) -> Dict[str, Any]:
        """Get recent sentiment trend"""
        recent_sentiments = self.sentiment_history[-recent_turns:] if self.sentiment_history else []
        
        if not recent_sentiments:
            return {"trend": "neutral", "confidence": 0.0, "count": 0}
        
        sentiment_counts = {}
        total_confidence = 0
        
        for entry in recent_sentiments:
            sentiment = entry["sentiment"]
            confidence = entry["confidence"]
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_confidence += confidence
        
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        avg_confidence = total_confidence / len(recent_sentiments)
        
        return {
            "trend": dominant_sentiment,
            "confidence": avg_confidence,
            "count": len(recent_sentiments),
            "distribution": sentiment_counts
        }
    
    def update_topic(self, new_topic: str) -> None:
        """Update current conversation topic"""
        self.current_topic = new_topic
        self.updated_at = datetime.utcnow()

@add_validators({
    'content_id': [RequiredValidator(), LengthValidator(min_length=5)],
    'content_type': [RequiredValidator()],
    'original_language': [RequiredValidator()],
})
@dataclass
class MultilingualContent(BaseModel):
    """Model for managing multilingual content"""
    
    content_id: str = field(default="")  # Will be validated as required
    content_type: str = field(default="")  # Will be validated as required
    original_language: str = "en"
    translations: Dict[str, str] = field(default_factory=dict)
    health_domain: str = "general"
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    context_tags: List[str] = field(default_factory=list)
    usage_count: Dict[str, int] = field(default_factory=dict)
    
    def add_translation(self, language: str, translation: str, confidence: float = 1.0) -> None:
        """Add a translation for a specific language"""
        self.translations[language] = translation
        self.confidence_scores[language] = confidence
        self.usage_count[language] = self.usage_count.get(language, 0)
        self.updated_at = datetime.utcnow()
    
    def get_translation(self, language: str) -> Optional[str]:
        """Get translation for a specific language"""
        # Try exact language match first
        if language in self.translations:
            self.usage_count[language] = self.usage_count.get(language, 0) + 1
            return self.translations[language]
        
        # Try language family match (e.g., 'en' for 'en-US')
        base_language = language.split('-')[0]
        if base_language in self.translations:
            self.usage_count[base_language] = self.usage_count.get(base_language, 0) + 1
            return self.translations[base_language]
        
        # Fallback to original language or English
        fallback_lang = self.original_language if self.original_language in self.translations else 'en'
        if fallback_lang in self.translations:
            return self.translations[fallback_lang]
        
        return None
    
    def get_best_translation(self, preferred_languages: List[str]) -> Optional[str]:
        """Get the best available translation from a list of preferred languages"""
        for language in preferred_languages:
            translation = self.get_translation(language)
            if translation:
                return translation
        return None
    
    def add_context_tag(self, tag: str) -> None:
        """Add a context tag for better content categorization"""
        if tag not in self.context_tags:
            self.context_tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def get_translation_quality_score(self, language: str) -> float:
        """Get quality score for a specific translation"""
        if language not in self.confidence_scores:
            return 0.0
        
        base_confidence = self.confidence_scores[language]
        usage_factor = min(self.usage_count.get(language, 0) / 100, 0.2)  # Max 0.2 bonus
        
        return min(base_confidence + usage_factor, 1.0)

@add_validators({
    'message_id': [RequiredValidator(), LengthValidator(min_length=10)],
    'content': [RequiredValidator(), LengthValidator(min_length=1, max_length=10000)],
    'message_type': [RequiredValidator()],
})
@dataclass
class ConversationMessage(BaseModel):
    """Model for individual conversation messages"""
    
    message_id: str = field(default="")  # Will be validated as required
    session_id: str = field(default="")  # Will be validated as required
    content: str = field(default="")  # Will be validated as required
    message_type: MessageType = MessageType.TEXT
    context_id: Optional[str] = None
    language: str = "en"
    is_user_message: bool = True
    response_to: Optional[str] = None  # ID of message this is responding to
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    confidence: float = 1.0
    
    def set_response_metadata(self, processing_time: float, model_used: str, confidence: float = 1.0) -> None:
        """Set metadata for AI response messages"""
        self.processing_time = processing_time
        self.confidence = confidence
        self.metadata.update({
            "model_used": model_used,
            "generated_at": datetime.utcnow().isoformat(),
            "is_ai_response": True
        })
        self.updated_at = datetime.utcnow()
    
    def add_attachment(self, attachment_type: str, attachment_data: Dict[str, Any]) -> None:
        """Add attachment data to the message"""
        if "attachments" not in self.metadata:
            self.metadata["attachments"] = []
        
        attachment = {
            "type": attachment_type,
            "data": attachment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.metadata["attachments"].append(attachment)
        self.updated_at = datetime.utcnow()
    
    def get_word_count(self) -> int:
        """Get word count of the message content"""
        return len(self.content.split())
    
    def is_question(self) -> bool:
        """Check if the message appears to be a question"""
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would', 'should']
        content_lower = self.content.lower()
        
        return (content_lower.endswith('?') or 
                any(indicator in content_lower for indicator in question_indicators))
    
    def extract_keywords(self) -> List[str]:
        """Extract potential keywords from the message content"""
        # Simple keyword extraction - in practice, this would use NLP
        import re
        
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', self.content.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return list(set(keywords))  # Remove duplicates