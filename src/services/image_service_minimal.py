# image_service_minimal.py - Minimal image service for testing without dependencies
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from src.models import HealthAnalysisResult, AnalysisType, AnalysisStatus, FoodItem, EmotionDetection, HealthCondition
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

class MinimalImageService:
    """Minimal image service that works without external ML dependencies"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        logger.info("Minimal Image Service initialized (no ML dependencies)")
    
    def analyze_image(self, image_path: Union[str, Path], analysis_type: AnalysisType, 
                     analysis_id: str = None) -> HealthAnalysisResult:
        """Analyze image with mock results for testing"""
        start_time = time.time()
        
        try:
            # Create analysis result
            if analysis_id is None:
                analysis_id = f"analysis_{int(time.time())}"
            
            result = HealthAnalysisResult(
                analysis_id=analysis_id,
                analysis_type=analysis_type,
                status=AnalysisStatus.PROCESSING
            )
            
            # Validate image path exists
            image_path = Path(image_path)
            if not image_path.exists():
                raise ValueError(f"Image file does not exist: {image_path}")
            
            result.input_data = {
                'image_path': str(image_path),
                'analysis_type': analysis_type.value,
                'mock_analysis': True
            }
            
            # Generate mock results based on analysis type
            if analysis_type == AnalysisType.SKIN_CONDITION:
                result.add_prediction("healthy_skin", 0.85, {
                    "condition": "healthy_skin",
                    "severity": "normal",
                    "recommendations": ["Continue good skincare routine", "Use sunscreen daily"]
                })
                
            elif analysis_type == AnalysisType.EYE_HEALTH:
                result.add_prediction("healthy_eye", 0.92, {
                    "condition": "healthy_eye", 
                    "severity": "normal",
                    "recommendations": ["Regular eye exams", "Protect from UV exposure"]
                })
                
            elif analysis_type == AnalysisType.FOOD_RECOGNITION:
                result.add_prediction("apple", 0.78, {
                    "food": "apple",
                    "category": "fruit",
                    "calories": 52,
                    "health_benefits": ["High in fiber", "Rich in antioxidants"]
                })
                
            elif analysis_type == AnalysisType.EMOTION_DETECTION:
                result.add_prediction("happy", 0.73, {
                    "emotion": "happy",
                    "intensity": 0.7,
                    "wellness_score": 0.8
                })
                
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Complete the analysis
            processing_time = time.time() - start_time
            result.set_completed(processing_time)
            
            logger.info(f"Mock image analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Image analysis failed after {processing_time:.2f}s: {e}")
            
            if 'result' in locals():
                result.set_failed(str(e))
                return result
            else:
                # Create a failed result
                result = HealthAnalysisResult(
                    analysis_id=analysis_id or f"failed_{int(time.time())}",
                    analysis_type=analysis_type,
                    status=AnalysisStatus.FAILED
                )
                result.set_failed(str(e))
                return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return list(self.supported_formats)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        return {
            'device': 'cpu',
            'loaded_models': ['mock_model'],
            'current_model': 'MinimalImageService',
            'dependencies_available': False
        }

# Use minimal service when dependencies are not available
try:
    from .image_service import EnhancedImageRecognitionService
    ImageService = EnhancedImageRecognitionService
    logger.info("Using full EnhancedImageRecognitionService")
except ImportError as e:
    logger.warning(f"Using MinimalImageService due to missing dependencies: {e}")
    ImageService = MinimalImageService