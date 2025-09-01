# health_models.py - Health analysis related data models
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseModel, add_validators, RequiredValidator, LengthValidator, ChoiceValidator

class AnalysisType(Enum):
    """Types of health analysis"""
    SKIN_CONDITION = "skin_condition"
    EYE_HEALTH = "eye_health"
    FOOD_RECOGNITION = "food_recognition"
    EMOTION_DETECTION = "emotion_detection"
    GENERAL_HEALTH = "general_health"

class AnalysisStatus(Enum):
    """Analysis processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConfidenceLevel(Enum):
    """Confidence level categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@add_validators({
    'analysis_id': [RequiredValidator(), LengthValidator(min_length=10)],
    'analysis_type': [RequiredValidator()],
    'status': [RequiredValidator()],
})
@dataclass
class HealthAnalysisResult(BaseModel):
    """Model for storing health analysis results"""
    
    analysis_id: str = field(default="")  # Will be validated as required
    analysis_type: AnalysisType = field(default=AnalysisType.GENERAL_HEALTH)  # Will be validated as required
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    explanation: Dict[str, Any] = field(default_factory=dict)
    status: AnalysisStatus = AnalysisStatus.PENDING
    processing_time: float = 0.0
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_prediction(self, label: str, confidence: float, details: Dict[str, Any] = None) -> None:
        """Add a prediction result"""
        prediction = {
            "label": label,
            "confidence": confidence,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.predictions.append(prediction)
        self.confidence_scores[label] = confidence
        self.updated_at = datetime.utcnow()
    
    def get_top_prediction(self) -> Optional[Dict[str, Any]]:
        """Get the prediction with highest confidence"""
        if not self.predictions:
            return None
        
        return max(self.predictions, key=lambda x: x.get('confidence', 0))
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get overall confidence level category"""
        if not self.confidence_scores:
            return ConfidenceLevel.LOW
        
        avg_confidence = sum(self.confidence_scores.values()) / len(self.confidence_scores)
        
        if avg_confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif avg_confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif avg_confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def set_completed(self, processing_time: float) -> None:
        """Mark analysis as completed"""
        self.status = AnalysisStatus.COMPLETED
        self.processing_time = processing_time
        self.updated_at = datetime.utcnow()
    
    def set_failed(self, error_message: str) -> None:
        """Mark analysis as failed"""
        self.status = AnalysisStatus.FAILED
        self.metadata["error_message"] = error_message
        self.updated_at = datetime.utcnow()

@add_validators({
    'condition_name': [RequiredValidator(), LengthValidator(min_length=2, max_length=100)],
    'severity': [RequiredValidator(), ChoiceValidator(['mild', 'moderate', 'severe', 'critical'])],
})
@dataclass
class HealthCondition(BaseModel):
    """Model for representing detected health conditions"""
    
    condition_name: str = field(default="")  # Will be validated as required
    category: str = field(default="")
    severity: str = field(default="")  # Will be validated as required
    confidence: float = field(default=0.0)
    description: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    follow_up_required: bool = False
    medical_attention_urgency: str = "routine"  # routine, urgent, emergency
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a health recommendation"""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
            self.updated_at = datetime.utcnow()
    
    def add_risk_factor(self, risk_factor: str) -> None:
        """Add a risk factor"""
        if risk_factor not in self.risk_factors:
            self.risk_factors.append(risk_factor)
            self.updated_at = datetime.utcnow()
    
    def requires_immediate_attention(self) -> bool:
        """Check if condition requires immediate medical attention"""
        return (self.severity in ['severe', 'critical'] or 
                self.medical_attention_urgency in ['urgent', 'emergency'])

@add_validators({
    'food_name': [RequiredValidator(), LengthValidator(min_length=2, max_length=100)],
    'confidence': [RequiredValidator()],
})
@dataclass
class FoodItem(BaseModel):
    """Model for recognized food items"""
    
    food_name: str = field(default="")  # Will be validated as required
    confidence: float = field(default=0.0)  # Will be validated as required
    category: Optional[str] = None
    nutritional_info: Dict[str, Any] = field(default_factory=dict)
    portion_size: Optional[str] = None
    calories_per_serving: Optional[float] = None
    health_benefits: List[str] = field(default_factory=list)
    allergens: List[str] = field(default_factory=list)
    dietary_tags: List[str] = field(default_factory=list)  # vegetarian, vegan, gluten-free, etc.
    
    def add_nutritional_info(self, nutrient: str, value: float, unit: str) -> None:
        """Add nutritional information"""
        self.nutritional_info[nutrient] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def add_health_benefit(self, benefit: str) -> None:
        """Add a health benefit"""
        if benefit not in self.health_benefits:
            self.health_benefits.append(benefit)
            self.updated_at = datetime.utcnow()
    
    def add_allergen(self, allergen: str) -> None:
        """Add an allergen"""
        if allergen not in self.allergens:
            self.allergens.append(allergen)
            self.updated_at = datetime.utcnow()
    
    def is_healthy_choice(self) -> bool:
        """Determine if this is generally considered a healthy food choice"""
        # Simple heuristic based on dietary tags and nutritional info
        healthy_tags = ['organic', 'whole-grain', 'low-sodium', 'high-fiber']
        unhealthy_tags = ['processed', 'high-sugar', 'high-sodium', 'trans-fat']
        
        healthy_score = sum(1 for tag in self.dietary_tags if tag in healthy_tags)
        unhealthy_score = sum(1 for tag in self.dietary_tags if tag in unhealthy_tags)
        
        return healthy_score > unhealthy_score

@add_validators({
    'emotion': [RequiredValidator(), LengthValidator(min_length=2, max_length=50)],
    'confidence': [RequiredValidator()],
})
@dataclass
class EmotionDetection(BaseModel):
    """Model for emotion detection results"""
    
    emotion: str = field(default="")  # Will be validated as required
    confidence: float = field(default=0.0)  # Will be validated as required
    intensity: float = 0.0  # 0.0 to 1.0
    facial_landmarks: Dict[str, Any] = field(default_factory=dict)
    additional_emotions: List[Dict[str, float]] = field(default_factory=list)
    context_factors: List[str] = field(default_factory=list)
    wellness_indicators: Dict[str, Any] = field(default_factory=dict)
    
    def add_secondary_emotion(self, emotion: str, confidence: float) -> None:
        """Add a secondary emotion detection"""
        self.additional_emotions.append({
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def get_dominant_emotion(self) -> str:
        """Get the most confident emotion"""
        if not self.additional_emotions:
            return self.emotion
        
        all_emotions = [{"emotion": self.emotion, "confidence": self.confidence}] + self.additional_emotions
        dominant = max(all_emotions, key=lambda x: x["confidence"])
        return dominant["emotion"]
    
    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the emotional state"""
        return {
            "primary_emotion": self.emotion,
            "confidence": self.confidence,
            "intensity": self.intensity,
            "secondary_emotions": len(self.additional_emotions),
            "overall_wellness": self.wellness_indicators.get("overall_score", 0.5),
            "timestamp": self.created_at.isoformat()
        }