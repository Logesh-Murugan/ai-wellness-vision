# image_recognition.py - Computer vision module for health-related image analysis
import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from src.config import ModelConfig

class ImageRecognitionEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        self.transform = self._get_transforms()
        
    def _load_model(self):
        """Load pre-trained ResNet50 model"""
        model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        model.eval()
        model.to(self.device)
        return model
    
    def _get_transforms(self):
        """Get image preprocessing transforms"""
        return transforms.Compose([
            transforms.Resize(ModelConfig.IMAGE_INPUT_SIZE),
            transforms.CenterCrop(ModelConfig.IMAGE_INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            image = Image.open(image_path).convert('RGB')
            return self.transform(image).unsqueeze(0).to(self.device)
        except Exception as e:
            raise ValueError(f"Error preprocessing image: {str(e)}")
    
    def analyze_image(self, image_path):
        """Analyze image and return predictions"""
        try:
            # Preprocess image
            input_tensor = self.preprocess_image(image_path)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Get top 5 predictions
            top5_prob, top5_indices = torch.topk(probabilities, 5)
            
            results = []
            for i in range(5):
                results.append({
                    'class_id': top5_indices[i].item(),
                    'confidence': top5_prob[i].item(),
                    'description': f"Class {top5_indices[i].item()}"
                })
            
            return {
                'status': 'success',
                'predictions': results,
                'device_used': str(self.device)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def detect_objects(self, image_path):
        """Basic object detection using OpenCV"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Simple edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            return {
                'status': 'success',
                'objects_detected': len(contours),
                'image_shape': image.shape
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }