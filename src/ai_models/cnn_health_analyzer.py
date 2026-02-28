#!/usr/bin/env python3
"""
CNN-based Health Image Analysis System
Advanced deep learning models for health image processing
"""

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CNNHealthAnalyzer:
    """Advanced CNN-based health image analyzer"""
    
    def __init__(self, models_dir: str = "models/cnn_health"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self.skin_model = None
        self.eye_model = None
        self.food_model = None
        self.general_health_model = None
        
        # Model configurations
        self.model_configs = {
            'skin': {
                'input_shape': (224, 224, 3),
                'classes': ['healthy', 'acne', 'eczema', 'rash', 'dry_skin', 'oily_skin'],
                'preprocessing': self._preprocess_skin_image
            },
            'eye': {
                'input_shape': (224, 224, 3),
                'classes': ['healthy', 'red_eye', 'dark_circles', 'puffy', 'tired'],
                'preprocessing': self._preprocess_eye_image
            },
            'food': {
                'input_shape': (224, 224, 3),
                'classes': ['healthy', 'processed', 'high_calorie', 'low_nutrition', 'balanced'],
                'preprocessing': self._preprocess_food_image
            },
            'general': {
                'input_shape': (224, 224, 3),
                'classes': ['normal', 'concerning', 'requires_attention'],
                'preprocessing': self._preprocess_general_image
            }
        }
        
        # Load or create models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load pre-trained CNN models"""
        try:
            # Try to load existing models
            self._load_existing_models()
        except Exception as e:
            logger.info(f"No existing models found, creating new ones: {e}")
            self._create_new_models()
    
    def _load_existing_models(self):
        """Load pre-trained models if they exist"""
        model_files = {
            'skin': self.models_dir / 'skin_analyzer.h5',
            'eye': self.models_dir / 'eye_analyzer.h5',
            'food': self.models_dir / 'food_analyzer.h5',
            'general': self.models_dir / 'general_health_analyzer.h5'
        }
        
        for model_type, model_path in model_files.items():
            if model_path.exists():
                try:
                    model = tf.keras.models.load_model(str(model_path))
                    setattr(self, f'{model_type}_model', model)
                    logger.info(f"Loaded {model_type} model from {model_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {model_type} model: {e}")
                    self._create_model(model_type)
            else:
                self._create_model(model_type)
    
    def _create_new_models(self):
        """Create new CNN models for each analysis type"""
        for model_type in self.model_configs.keys():
            self._create_model(model_type)
    
    def _create_model(self, model_type: str) -> tf.keras.Model:
        """Create a CNN model for specific health analysis"""
        config = self.model_configs[model_type]
        input_shape = config['input_shape']
        num_classes = len(config['classes'])
        
        # Create CNN architecture
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=input_shape),
            
            # First convolutional block
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Second convolutional block
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Third convolutional block
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Fourth convolutional block
            tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Global average pooling instead of flatten
            tf.keras.layers.GlobalAveragePooling2D(),
            
            # Dense layers
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            # Output layer
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Store model
        setattr(self, f'{model_type}_model', model)
        
        # Save model architecture
        model_path = self.models_dir / f'{model_type}_analyzer.h5'
        model.save(str(model_path))
        
        logger.info(f"Created and saved {model_type} CNN model")
        return model
    
    def _preprocess_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """General image preprocessing"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(target_size)
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Normalize pixel values
            img_array = img_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            raise
    
    def _preprocess_skin_image(self, image_path: str) -> np.ndarray:
        """Specialized preprocessing for skin images"""
        img_array = self._preprocess_image(image_path)
        
        # Additional skin-specific preprocessing
        # Enhance contrast for better skin feature detection
        img_array = tf.image.adjust_contrast(img_array, contrast_factor=1.2)
        
        return img_array.numpy()
    
    def _preprocess_eye_image(self, image_path: str) -> np.ndarray:
        """Specialized preprocessing for eye images"""
        img_array = self._preprocess_image(image_path)
        
        # Additional eye-specific preprocessing
        # Enhance brightness for better eye feature detection
        img_array = tf.image.adjust_brightness(img_array, delta=0.1)
        
        return img_array.numpy()
    
    def _preprocess_food_image(self, image_path: str) -> np.ndarray:
        """Specialized preprocessing for food images"""
        img_array = self._preprocess_image(image_path)
        
        # Additional food-specific preprocessing
        # Enhance saturation for better food recognition
        img_array = tf.image.adjust_saturation(img_array, saturation_factor=1.1)
        
        return img_array.numpy()
    
    def _preprocess_general_image(self, image_path: str) -> np.ndarray:
        """General health image preprocessing"""
        return self._preprocess_image(image_path)
    
    def analyze_image(self, image_path: str, analysis_type: str) -> Dict:
        """Analyze image using appropriate CNN model"""
        try:
            if analysis_type not in self.model_configs:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Get model and config
            model = getattr(self, f'{analysis_type}_model')
            config = self.model_configs[analysis_type]
            
            if model is None:
                raise ValueError(f"Model for {analysis_type} not loaded")
            
            # Preprocess image
            preprocessor = config['preprocessing']
            processed_image = preprocessor(image_path)
            
            # Make prediction
            predictions = model.predict(processed_image, verbose=0)
            
            # Get class probabilities
            class_probabilities = predictions[0]
            classes = config['classes']
            
            # Find top prediction
            top_class_idx = np.argmax(class_probabilities)
            top_class = classes[top_class_idx]
            confidence = float(class_probabilities[top_class_idx])
            
            # Generate detailed analysis
            analysis_result = self._generate_detailed_analysis(
                analysis_type, top_class, confidence, class_probabilities, classes
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return self._generate_fallback_analysis(analysis_type)
    
    def _generate_detailed_analysis(self, analysis_type: str, top_class: str, 
                                  confidence: float, probabilities: np.ndarray, 
                                  classes: List[str]) -> Dict:
        """Generate detailed analysis results"""
        
        # Create probability distribution
        prob_dict = {classes[i]: float(probabilities[i]) for i in range(len(classes))}
        
        # Generate recommendations based on analysis type and result
        recommendations = self._generate_recommendations(analysis_type, top_class, confidence)
        
        # Generate health insights
        insights = self._generate_health_insights(analysis_type, top_class, confidence)
        
        return {
            'analysis_type': analysis_type,
            'primary_finding': top_class,
            'confidence': confidence,
            'probability_distribution': prob_dict,
            'recommendations': recommendations,
            'health_insights': insights,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0',
            'processing_method': 'CNN Deep Learning'
        }
    
    def _generate_recommendations(self, analysis_type: str, finding: str, confidence: float) -> List[str]:
        """Generate health recommendations based on CNN analysis"""
        
        recommendations_db = {
            'skin': {
                'healthy': [
                    "Your skin appears healthy! Continue your current skincare routine",
                    "Apply broad-spectrum SPF 30+ sunscreen daily",
                    "Maintain hydration with 8-10 glasses of water daily",
                    "Use a gentle moisturizer suitable for your skin type"
                ],
                'acne': [
                    "Consider using salicylic acid or benzoyl peroxide products",
                    "Avoid touching or picking at affected areas",
                    "Use non-comedogenic skincare products",
                    "Consult a dermatologist if condition persists"
                ],
                'eczema': [
                    "Use fragrance-free, hypoallergenic moisturizers",
                    "Avoid known triggers and harsh chemicals",
                    "Consider cool compresses for inflamed areas",
                    "Consult a dermatologist for proper treatment"
                ],
                'dry_skin': [
                    "Use a rich, hydrating moisturizer twice daily",
                    "Avoid hot water and harsh soaps",
                    "Consider using a humidifier in dry environments",
                    "Look for products with ceramides or hyaluronic acid"
                ]
            },
            'eye': {
                'healthy': [
                    "Your eyes appear healthy and well-rested",
                    "Continue getting 7-9 hours of quality sleep",
                    "Take regular breaks from screen time (20-20-20 rule)",
                    "Maintain a diet rich in omega-3 fatty acids"
                ],
                'red_eye': [
                    "Avoid rubbing your eyes",
                    "Use preservative-free artificial tears",
                    "Remove contact lenses if wearing them",
                    "Consult an eye doctor if redness persists"
                ],
                'dark_circles': [
                    "Ensure adequate sleep (7-9 hours nightly)",
                    "Use a cold compress to reduce puffiness",
                    "Consider eye creams with caffeine or retinol",
                    "Stay hydrated and reduce salt intake"
                ]
            },
            'food': {
                'healthy': [
                    "Great choice! This appears to be a nutritious meal",
                    "Continue incorporating variety in your diet",
                    "Maintain portion control for optimal health",
                    "Pair with adequate water intake"
                ],
                'processed': [
                    "Try to limit processed foods in your diet",
                    "Look for whole food alternatives",
                    "Check nutrition labels for hidden sugars and sodium",
                    "Consider meal prepping with fresh ingredients"
                ],
                'high_calorie': [
                    "Consider smaller portions of high-calorie foods",
                    "Balance with low-calorie, nutrient-dense options",
                    "Increase physical activity to offset caloric intake",
                    "Focus on foods that provide sustained energy"
                ]
            }
        }
        
        # Get recommendations for the specific finding
        type_recommendations = recommendations_db.get(analysis_type, {})
        finding_recommendations = type_recommendations.get(finding, [
            "Maintain a healthy lifestyle with balanced nutrition",
            "Stay hydrated and get adequate sleep",
            "Consult healthcare professionals for personalized advice"
        ])
        
        # Add confidence-based recommendations
        if confidence < 0.7:
            finding_recommendations.append("Consider taking another photo with better lighting for more accurate analysis")
        
        return finding_recommendations
    
    def _generate_health_insights(self, analysis_type: str, finding: str, confidence: float) -> Dict:
        """Generate health insights based on CNN analysis"""
        
        insights = {
            'severity_level': self._assess_severity(finding, confidence),
            'follow_up_needed': confidence > 0.8 and finding not in ['healthy', 'normal'],
            'confidence_interpretation': self._interpret_confidence(confidence),
            'next_steps': self._suggest_next_steps(analysis_type, finding, confidence)
        }
        
        return insights
    
    def _assess_severity(self, finding: str, confidence: float) -> str:
        """Assess severity level of findings"""
        concerning_findings = ['eczema', 'rash', 'red_eye', 'concerning', 'requires_attention']
        
        if finding in concerning_findings and confidence > 0.8:
            return 'moderate'
        elif finding in concerning_findings and confidence > 0.6:
            return 'mild'
        elif finding in ['healthy', 'normal'] and confidence > 0.7:
            return 'none'
        else:
            return 'uncertain'
    
    def _interpret_confidence(self, confidence: float) -> str:
        """Interpret confidence level"""
        if confidence >= 0.9:
            return 'Very high confidence in analysis'
        elif confidence >= 0.8:
            return 'High confidence in analysis'
        elif confidence >= 0.7:
            return 'Moderate confidence in analysis'
        elif confidence >= 0.6:
            return 'Low confidence - consider retaking photo'
        else:
            return 'Very low confidence - photo quality may be insufficient'
    
    def _suggest_next_steps(self, analysis_type: str, finding: str, confidence: float) -> List[str]:
        """Suggest next steps based on analysis"""
        steps = []
        
        if confidence < 0.7:
            steps.append("Retake photo with better lighting and focus")
        
        if finding not in ['healthy', 'normal'] and confidence > 0.7:
            steps.append(f"Monitor {analysis_type} condition over the next few days")
            steps.append("Consider consulting a healthcare professional")
        
        if confidence > 0.8:
            steps.append("Analysis results are reliable for general guidance")
        
        steps.append("Remember: This is not a substitute for professional medical advice")
        
        return steps
    
    def _generate_fallback_analysis(self, analysis_type: str) -> Dict:
        """Generate fallback analysis when CNN fails"""
        return {
            'analysis_type': analysis_type,
            'primary_finding': 'analysis_unavailable',
            'confidence': 0.0,
            'recommendations': [
                "Unable to analyze image with CNN model",
                "Please ensure image is clear and well-lit",
                "Try taking another photo",
                "Consult healthcare professionals for accurate assessment"
            ],
            'health_insights': {
                'severity_level': 'unknown',
                'follow_up_needed': False,
                'confidence_interpretation': 'Analysis failed',
                'next_steps': ['Retake photo', 'Seek professional medical advice']
            },
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0',
            'processing_method': 'Fallback Analysis'
        }
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        info = {}
        
        for model_type in self.model_configs.keys():
            model = getattr(self, f'{model_type}_model')
            if model:
                info[model_type] = {
                    'loaded': True,
                    'input_shape': self.model_configs[model_type]['input_shape'],
                    'classes': self.model_configs[model_type]['classes'],
                    'parameters': model.count_params() if hasattr(model, 'count_params') else 'unknown'
                }
            else:
                info[model_type] = {'loaded': False}
        
        return info

# Global instance
cnn_analyzer = None

def get_cnn_analyzer() -> CNNHealthAnalyzer:
    """Get global CNN analyzer instance"""
    global cnn_analyzer
    if cnn_analyzer is None:
        cnn_analyzer = CNNHealthAnalyzer()
    return cnn_analyzer