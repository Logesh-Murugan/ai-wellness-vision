"""
Image analysis service for AI WellnessVision.

Contains the AnalysisService which orchestrates:
  1. Local ML model inference (Skin, Food, Eye, Emotion)
  2. Redis Cache integration
  3. Prometheus metrics tracking
  4. Gemini Vision API fallback
"""

import logging
import os
import time
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import ML Models — optional (heavy deps like torch/transformers)
_ML_AVAILABLE = False
try:
    from src.ai_models.skin_classifier import SkinDiseaseClassifier
    from src.ai_models.food_analyzer import FoodAnalyzer
    from src.ai_models.eye_health_analyzer import EyeHealthAnalyzer
    from src.ai_models.emotion_analyzer import EmotionAnalyzer
    _ML_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).warning(
        "⚠️  ML model libraries not installed (torch/transformers) — "
        "will use Gemini API fallback for all analysis"
    )

# Import Infrastructure — optional (Redis cache)
try:
    from src.cache.cache_service import CacheService
    cache_service = CacheService()
except Exception:
    cache_service = None
    logging.getLogger(__name__).warning("⚠️  Redis cache service not available — caching disabled")

# Import Monitoring — optional (Prometheus)
try:
    from src.monitoring.metrics import MODEL_PREDICTION_DURATION
except Exception:
    MODEL_PREDICTION_DURATION = None
    logging.getLogger(__name__).warning("⚠️  Prometheus metrics not available — metrics disabled")

# Optional Gemini import
_client = None
_GEMINI_AVAILABLE = False

try:
    from google import genai
    _api_key = os.getenv("GEMINI_API_KEY")
    if _api_key:
        _client = genai.Client(api_key=_api_key)
        _GEMINI_AVAILABLE = True
except Exception as e:
    logging.getLogger(__name__).warning("Could not initialize google.genai in AnalysisService: %s", e)
    _GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._models_loaded = False
    
    async def initialize(self):
        """Load all 4 models at startup."""
        if not _ML_AVAILABLE:
            logger.info("ML libraries not installed — skipping local model loading (using Gemini fallback)")
            self._models_loaded = True
            return

        logger.info("Initializing AnalysisService models...")
        
        model_configs = [
            ("skin",    "models/skin_model.pth",  SkinDiseaseClassifier),
            ("food",    "models/food_model.pth",  FoodAnalyzer),
            ("eye",     "models/eye_model.pth",   EyeHealthAnalyzer),
            ("emotion", None,                     EmotionAnalyzer),
        ]
        
        for name, path, cls in model_configs:
            try:
                # EyeHealthAnalyzer and EmotionAnalyzer don't take model_path in __init__
                if name in ["eye", "emotion"]:
                    self._models[name] = cls()
                else:
                    self._models[name] = cls(model_path=path) if path else cls()
                logger.info(f"✅ Model loaded successfully: {name}")
            except Exception as e:
                logger.warning(f"⚠️ Model {name} not loaded: {e} — will use fallback")
        
        self._models_loaded = True

    async def analyze_image(self, image_bytes: bytes, analysis_type: str, user_id: str) -> Dict:
        """Run image analysis through the configured pipeline."""
        if not self._models_loaded:
            logger.warning("Models not initialized yet. Please call initialize() at startup.")

        # 1. Check Redis cache first
        if cache_service is not None:
            try:
                cached = await cache_service.get_cached_analysis(image_bytes, analysis_type)
                if cached:
                    logger.info(f"Returning cached result for {analysis_type}")
                    return {**cached, "from_cache": True}
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
        
        # 2. Start timer for Prometheus metric
        start_time = time.time()
        
        # 3. Route to correct model (running in thread to avoid blocking loop)
        try:
            if analysis_type == "skin":
                if "skin" in self._models:
                    result = await asyncio.to_thread(self._models["skin"].predict, image_bytes)
                else:
                    result = {"error": "Skin model not loaded"}
            
            elif analysis_type == "food":
                if "food" in self._models:
                    result = await asyncio.to_thread(self._models["food"].analyze, image_bytes)
                else:
                    result = {"error": "Food model not loaded"}
            
            elif analysis_type == "eye":
                if "eye" in self._models:
                    result = await asyncio.to_thread(self._models["eye"].analyze, image_bytes, analysis_type="general")
                else:
                    result = {"error": "Eye model not loaded"}
            
            elif analysis_type == "emotion":
                if "emotion" in self._models:
                    result = await asyncio.to_thread(self._models["emotion"].analyze, image_bytes)
                else:
                    result = {"error": "Emotion model not loaded"}
            
            else:
                raise ValueError(f"Unknown analysis_type: {analysis_type}")
        except Exception as e:
            logger.error(f"Error during {analysis_type} inference: {e}")
            result = {"error": str(e)}

        # 4. Record Prometheus metric
        duration = time.time() - start_time
        if MODEL_PREDICTION_DURATION is not None:
            try:
                MODEL_PREDICTION_DURATION.labels(model_type=analysis_type).observe(duration)
            except Exception as e:
                logger.warning(f"Failed to record metric: {e}")
        
        # 5. Keep Gemini as fallback ONLY if local model failed AND Gemini key exists
        if result.get("error") and _GEMINI_AVAILABLE:
            logger.info(f"Local {analysis_type} model failed or unavailable. Falling back to Gemini.")
            gemini_result = await self._gemini_fallback(image_bytes, analysis_type)
            if gemini_result:
                result = gemini_result

        # 6. Cache the result (only if successful)
        if not result.get("error") and cache_service is not None:
            try:
                await cache_service.cache_analysis(image_bytes, analysis_type, result)
            except Exception as e:
                logger.warning(f"Cache storage failed: {e}")
        
        # Standardize return format if missing fields
        if "id" not in result:
            result["id"] = str(uuid.uuid4())
        if "timestamp" not in result:
            result["timestamp"] = datetime.now().isoformat()
        if "disclaimer" not in result:
            result["disclaimer"] = "AI analysis is for informational purposes only. Consult a healthcare professional for medical advice."
            
        return result

    async def _gemini_fallback(self, image_bytes: bytes, analysis_type: str) -> Optional[Dict]:
        """Analyse an image using Gemini Vision API as a fallback."""
        if not _GEMINI_AVAILABLE or _client is None:
            return None

        try:
            import PIL.Image
            import io
            img = PIL.Image.open(io.BytesIO(image_bytes))

            prompts = {
                "skin": "Analyze this skin image for general health indicators. Provide wellness recommendations. Avoid medical diagnosis.",
                "food": "Analyze this food image. Estimate nutritional content and provide healthy eating suggestions.",
                "eye": "Look at this eye image for general wellness indicators. Provide eye health tips. Avoid medical diagnosis.",
                "emotion": "Analyze facial expressions for general mood indicators. Provide wellness and mental health tips.",
            }
            prompt = prompts.get(analysis_type, "Analyze this health-related image and provide general wellness advice.")

            logger.info(f"Sending fallback request to Gemini Vision for {analysis_type}...")
            models_to_try = ["gemini-flash-latest", "gemini-pro-latest"]
            response = None

            for model_name in models_to_try:
                try:
                    # Gemini inference blocks, so wrap in to_thread
                    response = await asyncio.to_thread(
                        _client.models.generate_content,
                        model=model_name,
                        contents=[prompt, img],
                    )
                    if response and response.text:
                        break
                except Exception as m_err:
                    logger.warning("Gemini Vision model %s failed: %s, trying fallback...", model_name, m_err)

            if response and response.text:
                logger.info("✅ Gemini Vision fallback successful")
                return {
                    "type": analysis_type,
                    "result": response.text,
                    "confidence": 0.90,
                    "recommendations": self._extract_recommendations(response.text),
                    "analysis_method": "Gemini Vision API (Fallback)",
                }
            return None
        except Exception as exc:
            logger.error("Gemini Vision fallback error: %s", exc)
            return None

    def _extract_recommendations(self, text: str) -> list[str]:
        """Parse bullet points / recommendation sentences from text."""
        recommendations = []
        for line in text.split("\n"):
            line = line.strip()
            if line and line[0] in ("•", "-", "*"):
                recommendations.append(line[1:].strip())
            elif len(line) > 20 and ("recommend" in line.lower() or "suggest" in line.lower()):
                recommendations.append(line)
        
        return recommendations[:4] if recommendations else [
            "Maintain healthy habits",
            "Consult healthcare professionals for specific concerns"
        ]

# Create singleton instance
analysis_service = AnalysisService()
