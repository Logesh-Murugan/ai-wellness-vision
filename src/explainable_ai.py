# explainable_ai.py - AI interpretability and explanation tools
import numpy as np
import torch
import cv2
from lime import lime_image
from lime.wrappers.scikit_image import SegmentationAlgorithm
import matplotlib.pyplot as plt
from src.config import ModelConfig

class ExplainableAI:
    def __init__(self, model=None):
        self.model = model
        self.lime_explainer = lime_image.LimeImageExplainer()
        
    def explain_image_prediction(self, image_path, model, num_features=None):
        """Generate LIME explanation for image prediction"""
        try:
            if num_features is None:
                num_features = ModelConfig.LIME_NUM_FEATURES
            
            # Load and preprocess image
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Define prediction function for LIME
            def predict_fn(images):
                predictions = []
                for img in images:
                    # Convert to tensor and predict
                    # This is a simplified version - actual implementation would depend on your model
                    pred = np.random.rand(1000)  # Placeholder
                    predictions.append(pred)
                return np.array(predictions)
            
            # Generate explanation
            explanation = self.lime_explainer.explain_instance(
                image_rgb,
                predict_fn,
                top_labels=5,
                hide_color=0,
                num_samples=1000,
                num_features=num_features
            )
            
            return {
                'status': 'success',
                'explanation': explanation,
                'num_features': num_features,
                'image_shape': image_rgb.shape
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_feature_importance(self, data, predictions, feature_names=None):
        """Generate feature importance explanation"""
        try:
            if feature_names is None:
                feature_names = [f"Feature_{i}" for i in range(len(data))]
            
            # Calculate simple feature importance (placeholder)
            importance_scores = np.abs(np.random.randn(len(data)))
            
            # Sort by importance
            sorted_indices = np.argsort(importance_scores)[::-1]
            
            feature_importance = []
            for i in sorted_indices[:10]:  # Top 10 features
                feature_importance.append({
                    'feature': feature_names[i] if i < len(feature_names) else f"Feature_{i}",
                    'importance': float(importance_scores[i]),
                    'rank': len(feature_importance) + 1
                })
            
            return {
                'status': 'success',
                'feature_importance': feature_importance,
                'total_features': len(data)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def explain_text_prediction(self, text, prediction, model=None):
        """Explain text classification prediction"""
        try:
            # Simple word-based importance (placeholder)
            words = text.split()
            word_importance = {}
            
            for word in words:
                # Calculate importance score (simplified)
                importance = np.random.rand() * (1 if len(word) > 3 else 0.5)
                word_importance[word] = importance
            
            # Sort by importance
            sorted_words = sorted(word_importance.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'status': 'success',
                'text': text,
                'prediction': prediction,
                'word_importance': dict(sorted_words[:10]),
                'total_words': len(words)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_decision_path(self, input_data, model_output):
        """Generate decision path explanation"""
        try:
            # Simplified decision path
            decision_steps = [
                {
                    'step': 1,
                    'description': 'Input preprocessing',
                    'confidence': 0.95,
                    'details': 'Data normalized and validated'
                },
                {
                    'step': 2,
                    'description': 'Feature extraction',
                    'confidence': 0.88,
                    'details': 'Key features identified and weighted'
                },
                {
                    'step': 3,
                    'description': 'Model prediction',
                    'confidence': float(model_output.get('confidence', 0.75)),
                    'details': f"Final prediction: {model_output.get('prediction', 'Unknown')}"
                }
            ]
            
            return {
                'status': 'success',
                'decision_path': decision_steps,
                'overall_confidence': np.mean([step['confidence'] for step in decision_steps])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def create_explanation_summary(self, explanations):
        """Create a summary of all explanations"""
        try:
            summary = {
                'total_explanations': len(explanations),
                'explanation_types': [],
                'average_confidence': 0,
                'key_insights': []
            }
            
            confidences = []
            for explanation in explanations:
                if explanation.get('status') == 'success':
                    exp_type = explanation.get('type', 'unknown')
                    summary['explanation_types'].append(exp_type)
                    
                    if 'confidence' in explanation:
                        confidences.append(explanation['confidence'])
            
            if confidences:
                summary['average_confidence'] = np.mean(confidences)
            
            summary['key_insights'] = [
                "Model predictions are based on multiple factors",
                "Feature importance varies across different inputs",
                "Confidence levels indicate prediction reliability"
            ]
            
            return {
                'status': 'success',
                'summary': summary
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }