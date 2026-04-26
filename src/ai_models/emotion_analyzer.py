#!/usr/bin/env python3
"""
Emotion Detection & Wellness Analyzer
=====================================
Uses DeepFace as the primary emotion detection engine with FER as a robust fallback.
Maps universal human emotions to holistic wellness scores and actionable advice.
"""

import io
import logging
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image

# Suppress annoying TensorFlow logs
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
from deepface import DeepFace
from fer import FER

logger = logging.getLogger(__name__)

WELLNESS_MAP = {
    "happy":   {"score": 85, "insight": "Positive emotional state detected"},
    "sad":     {"score": 40, "insight": "Signs of low mood detected"},
    "angry":   {"score": 35, "insight": "Signs of stress or frustration"},
    "fear":    {"score": 30, "insight": "Signs of anxiety detected"},
    "disgust": {"score": 30, "insight": "Signs of discomfort detected"},
    "surprise":{"score": 65, "insight": "Alert, engaged state"},
    "neutral": {"score": 65, "insight": "Calm, neutral emotional state"},
}

class EmotionAnalyzer:
    """
    Offline local analyzer combining multiple computer vision libraries 
    to robustly detect emotions and generate health insights.
    """
    def __init__(self):
        logger.info("Initializing EmotionAnalyzer... Loading models.")
        # Load FER model with MTCNN as fallback detector
        self.fer_detector = FER(mtcnn=True)
        logger.info("✅ Emotion models loaded successfully.")

    def _bytes_to_cv2(self, image_bytes: bytes) -> np.ndarray:
        """Convert raw bytes to an OpenCV format image (BGR array)."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        # DeepFace and FER both expect BGR format
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_bgr

    def _get_recommendations(self, emotion: str) -> List[str]:
        """Generate tailored wellness tips based on detected emotion."""
        emotion = emotion.lower()
        if emotion == "happy":
            return [
                "Maintain your positive momentum with a gratitude journal.",
                "Share your good mood by connecting with friends or family.",
                "Use this high-energy state to tackle a challenging task."
            ]
        elif emotion == "sad":
            return [
                "Practice a 5-minute deep breathing exercise to center yourself.",
                "Reach out to a trusted friend or family member for a chat.",
                "Consider stepping outside for a brief walk in nature.",
                "If feelings persist, speaking with a professional therapist can be very helpful."
            ]
        elif emotion == "angry":
            return [
                "Step away from the situation for a 10-minute cool-down period.",
                "Try progressive muscle relaxation or guided meditation.",
                "Engage in physical exercise to safely burn off stress hormones.",
                "Write down what is frustrating you to process the emotion."
            ]
        elif emotion in ["fear", "surprise"]:
            return [
                "Use the 5-4-3-2-1 grounding technique to reconnect with the present.",
                "Focus on slow, rhythmic breathing (inhale for 4s, exhale for 6s).",
                "Reduce caffeine intake and prioritize quality sleep.",
                "Identify the specific trigger causing anxiety to address it rationally."
            ]
        elif emotion == "disgust":
            return [
                "Acknowledge the source of discomfort and set healthy boundaries.",
                "Engage in a pleasant, distracting activity like listening to favorite music.",
                "Focus on a comforting, familiar environment to regain balance."
            ]
        else: # Neutral
            return [
                "A great time for a brief mindfulness or body-scan meditation.",
                "Ensure you are staying hydrated throughout the day.",
                "Take a moment to stretch your neck and shoulders.",
                "Review your daily goals and prioritize tasks calmly."
            ]

    def analyze(self, image_bytes: bytes) -> Dict:
        """
        Extracts emotions from the image and maps them to a wellness context.
        Uses DeepFace first, falls back to FER if DeepFace fails to find a face.
        """
        try:
            image_cv2 = self._bytes_to_cv2(image_bytes)
        except Exception as e:
            logger.error(f"Image parsing failed: {e}")
            return {"error": "Invalid image format."}

        dominant_emotion = None
        emotion_scores = {}

        # ---------------------------------------------------------
        # Primary Engine: DeepFace
        # ---------------------------------------------------------
        try:
            # We enforce_detection=False so it doesn't instantly throw an exception,
            # but we will check if it actually found valid data.
            analysis = DeepFace.analyze(
                img_path=image_cv2,
                actions=["emotion"],
                enforce_detection=True, # Actually set True to trigger fallback if no face
                silent=True
            )
            
            # DeepFace returns a list of faces if multiple are detected, we take the primary one
            result = analysis[0] if isinstance(analysis, list) else analysis
            dominant_emotion = result.get("dominant_emotion", "neutral")
            emotion_scores = result.get("emotion", {})
            logger.info(f"DeepFace successfully detected emotion: {dominant_emotion}")

        except Exception as deepface_error:
            logger.warning(f"DeepFace failed to detect a face ({deepface_error}). Falling back to FER.")
            
            # ---------------------------------------------------------
            # Fallback Engine: FER
            # ---------------------------------------------------------
            try:
                fer_results = self.fer_detector.detect_emotions(image_cv2)
                if fer_results:
                    # Take the first face found
                    emotion_scores = fer_results[0].get("emotions", {})
                    if emotion_scores:
                        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
                        logger.info(f"FER successfully detected emotion: {dominant_emotion}")
                else:
                    logger.error("FER also failed to detect a face.")
            except Exception as fer_error:
                logger.error(f"FER fallback failed: {fer_error}")

        # ---------------------------------------------------------
        # Data Formatting & Wellness Mapping
        # ---------------------------------------------------------
        if not dominant_emotion:
            return {"error": "No human face detected clearly in the image."}

        # Normalize emotion name (DeepFace and FER both use similar lowercase labels)
        dominant_emotion = dominant_emotion.lower()
        
        # If DeepFace or FER output slightly different keys, map to safe default
        mapped_data = WELLNESS_MAP.get(dominant_emotion, WELLNESS_MAP["neutral"])

        return {
            "dominant_emotion": dominant_emotion,
            "emotion_scores": emotion_scores,
            "wellness_score": mapped_data["score"],
            "wellness_insight": mapped_data["insight"],
            "recommendations": self._get_recommendations(dominant_emotion),
            "disclaimer": (
                "Disclaimer: This analysis reflects momentary facial expressions "
                "and is NOT a clinical diagnosis of your internal mental health."
            )
        }

if __name__ == "__main__":
    # Simple smoke test
    analyzer = EmotionAnalyzer()
    print("Emotion Analyzer loaded and ready.")
