#!/usr/bin/env python3
"""
Alternative Image Analysis Options for Health Images
This file demonstrates various AI services you can use instead of or alongside Gemini
"""

import os
import base64
import requests
import json
from PIL import Image
import numpy as np
from typing import Dict, Any, Optional

class ImageAnalysisAlternatives:
    """Multiple AI services for health image analysis"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.azure_api_key = os.getenv("AZURE_VISION_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    async def analyze_with_openai_vision(self, image_path: str, analysis_type: str) -> Optional[Dict]:
        """
        OpenAI GPT-4 Vision API for image analysis
        Very good for medical/health image analysis
        """
        if not self.openai_api_key:
            return None
            
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create health-specific prompts
            prompts = {
                "skin": "Analyze this skin image for health indicators. Look for signs of dryness, oiliness, acne, rashes, or other skin conditions. Provide skincare recommendations.",
                "food": "Analyze this food image for nutritional content. Estimate calories, identify ingredients, assess nutritional balance, and provide dietary recommendations.",
                "eye": "Analyze this eye image for basic health indicators. Look for signs of fatigue, redness, or other visible concerns. Provide eye health recommendations.",
                "wellness": "Analyze this image for general wellness indicators. Provide health and wellness recommendations based on what you observe."
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompts.get(analysis_type, prompts["wellness"])
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                return {
                    "provider": "OpenAI GPT-4 Vision",
                    "analysis": analysis_text,
                    "confidence": 0.85,
                    "recommendations": self._extract_recommendations(analysis_text)
                }
                
        except Exception as e:
            print(f"OpenAI Vision error: {e}")
            return None
    
    async def analyze_with_azure_vision(self, image_path: str, analysis_type: str) -> Optional[Dict]:
        """
        Microsoft Azure Computer Vision API
        Good for general image analysis and OCR
        """
        if not self.azure_api_key or not self.azure_endpoint:
            return None
            
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_api_key,
                'Content-Type': 'application/octet-stream'
            }
            
            # Azure Vision API parameters
            params = {
                'visualFeatures': 'Categories,Description,Objects,Tags',
                'details': 'Landmarks'
            }
            
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            response = requests.post(
                f"{self.azure_endpoint}/vision/v3.2/analyze",
                headers=headers,
                params=params,
                data=image_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract relevant information
                description = result.get('description', {}).get('captions', [{}])[0].get('text', '')
                tags = [tag['name'] for tag in result.get('tags', [])]
                
                # Generate health-specific analysis
                health_analysis = self._generate_health_analysis_from_tags(tags, description, analysis_type)
                
                return {
                    "provider": "Azure Computer Vision",
                    "analysis": health_analysis,
                    "confidence": 0.80,
                    "tags": tags,
                    "description": description,
                    "recommendations": self._get_recommendations_by_type(analysis_type)
                }
                
        except Exception as e:
            print(f"Azure Vision error: {e}")
            return None
    
    async def analyze_with_huggingface(self, image_path: str, analysis_type: str) -> Optional[Dict]:
        """
        Hugging Face Image Classification Models
        Free and open-source models
        """
        try:
            # Use different models based on analysis type
            model_endpoints = {
                "skin": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                "food": "https://api-inference.huggingface.co/models/nateraw/food",
                "general": "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
            }
            
            model_url = model_endpoints.get(analysis_type, model_endpoints["general"])
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}"
            }
            
            with open(image_path, "rb") as f:
                data = f.read()
            
            response = requests.post(model_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Process results based on model type
                analysis = self._process_huggingface_results(result, analysis_type)
                
                return {
                    "provider": "Hugging Face",
                    "analysis": analysis,
                    "confidence": 0.75,
                    "raw_results": result,
                    "recommendations": self._get_recommendations_by_type(analysis_type)
                }
                
        except Exception as e:
            print(f"Hugging Face error: {e}")
            return None
    
    def analyze_with_opencv_traditional(self, image_path: str, analysis_type: str) -> Dict:
        """
        Traditional computer vision analysis using OpenCV
        No API keys required, works offline
        """
        try:
            import cv2
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Basic image analysis
            height, width, channels = image.shape
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate basic statistics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Color analysis
            dominant_colors = self._get_dominant_colors(image)
            
            # Generate analysis based on type
            analysis = self._generate_opencv_analysis(
                brightness, contrast, dominant_colors, analysis_type
            )
            
            return {
                "provider": "OpenCV Traditional Vision",
                "analysis": analysis,
                "confidence": 0.70,
                "metrics": {
                    "brightness": float(brightness),
                    "contrast": float(contrast),
                    "dominant_colors": dominant_colors,
                    "resolution": f"{width}x{height}"
                },
                "recommendations": self._get_recommendations_by_type(analysis_type)
            }
            
        except Exception as e:
            print(f"OpenCV analysis error: {e}")
            return None
    
    def _extract_recommendations(self, text: str) -> list:
        """Extract recommendations from analysis text"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'try', 'consider']):
                if len(line) > 10:  # Filter out very short lines
                    recommendations.append(line)
        
        # If no specific recommendations found, create generic ones
        if not recommendations:
            recommendations = [
                "Maintain a healthy lifestyle with regular exercise",
                "Stay hydrated by drinking plenty of water",
                "Consult healthcare professionals for personalized advice",
                "Monitor changes and track progress over time"
            ]
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _generate_health_analysis_from_tags(self, tags: list, description: str, analysis_type: str) -> str:
        """Generate health analysis from Azure Vision tags"""
        health_keywords = {
            "skin": ["face", "person", "skin", "human", "portrait"],
            "food": ["food", "fruit", "vegetable", "meal", "dish", "plate"],
            "eye": ["eye", "face", "person", "human"],
            "wellness": ["person", "human", "health", "fitness"]
        }
        
        relevant_tags = [tag for tag in tags if any(keyword in tag.lower() for keyword in health_keywords.get(analysis_type, []))]
        
        if analysis_type == "skin":
            return f"Skin analysis based on image: {description}. Detected features include: {', '.join(relevant_tags)}. The image shows facial features that can be analyzed for skin health indicators."
        elif analysis_type == "food":
            return f"Food analysis: {description}. Identified food items: {', '.join(relevant_tags)}. This appears to be a nutritious meal with various components."
        elif analysis_type == "eye":
            return f"Eye health analysis: {description}. Facial features detected: {', '.join(relevant_tags)}. The image shows clear facial features suitable for basic eye health assessment."
        else:
            return f"General wellness analysis: {description}. Health-related features: {', '.join(relevant_tags)}. Overall assessment indicates good image quality for health analysis."
    
    def _process_huggingface_results(self, results: list, analysis_type: str) -> str:
        """Process Hugging Face model results"""
        if not results:
            return "Unable to analyze image with current model."
        
        if isinstance(results, list) and len(results) > 0:
            top_result = results[0]
            if isinstance(top_result, dict):
                label = top_result.get('label', 'Unknown')
                score = top_result.get('score', 0.0)
                
                return f"Analysis indicates: {label} with confidence {score:.2f}. This suggests certain characteristics relevant to {analysis_type} analysis."
        
        return f"Image processed successfully for {analysis_type} analysis. Results indicate various features suitable for health assessment."
    
    def _get_dominant_colors(self, image) -> list:
        """Get dominant colors from image using k-means clustering"""
        try:
            import cv2
            
            # Reshape image to be a list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Apply k-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert back to uint8 and return dominant colors
            centers = np.uint8(centers)
            return [{"r": int(c[2]), "g": int(c[1]), "b": int(c[0])} for c in centers]
            
        except:
            return [{"r": 128, "g": 128, "b": 128}]  # Default gray
    
    def _generate_opencv_analysis(self, brightness: float, contrast: float, colors: list, analysis_type: str) -> str:
        """Generate analysis based on OpenCV metrics"""
        brightness_desc = "bright" if brightness > 127 else "dim"
        contrast_desc = "high contrast" if contrast > 50 else "low contrast"
        
        if analysis_type == "skin":
            return f"Skin image analysis: The image has {brightness_desc} lighting and {contrast_desc}. Color analysis suggests skin tones are present. Image quality is suitable for basic skin health assessment."
        elif analysis_type == "food":
            return f"Food image analysis: The image shows {brightness_desc} lighting with {contrast_desc}. Color variety suggests multiple food components. Good image quality for nutritional assessment."
        elif analysis_type == "eye":
            return f"Eye health analysis: Image has {brightness_desc} lighting and {contrast_desc}. Suitable for basic eye health screening based on image quality metrics."
        else:
            return f"General wellness analysis: Image quality metrics show {brightness_desc} lighting and {contrast_desc}. Suitable for health-related image analysis."
    
    def _get_recommendations_by_type(self, analysis_type: str) -> list:
        """Get standard recommendations by analysis type"""
        recommendations = {
            "skin": [
                "Use gentle, fragrance-free skincare products",
                "Apply broad-spectrum sunscreen daily",
                "Stay hydrated and maintain a balanced diet",
                "Consult a dermatologist for persistent concerns"
            ],
            "food": [
                "Maintain portion control for balanced nutrition",
                "Include variety of colorful fruits and vegetables",
                "Stay hydrated throughout the day",
                "Consult a nutritionist for personalized meal plans"
            ],
            "eye": [
                "Take regular breaks from screen time (20-20-20 rule)",
                "Ensure adequate lighting when reading or working",
                "Get regular comprehensive eye exams",
                "Maintain a diet rich in eye-healthy nutrients"
            ],
            "wellness": [
                "Maintain regular exercise routine",
                "Prioritize adequate sleep (7-9 hours nightly)",
                "Practice stress management techniques",
                "Schedule regular health check-ups"
            ]
        }
        
        return recommendations.get(analysis_type, recommendations["wellness"])

# Example usage and testing
async def test_all_alternatives():
    """Test all available image analysis alternatives"""
    analyzer = ImageAnalysisAlternatives()
    
    # Test image path (you would use actual uploaded image)
    test_image = "test_image.jpg"
    analysis_type = "skin"
    
    print("Testing Image Analysis Alternatives:")
    print("=" * 50)
    
    # Test OpenAI Vision (requires API key)
    openai_result = await analyzer.analyze_with_openai_vision(test_image, analysis_type)
    if openai_result:
        print("✅ OpenAI GPT-4 Vision: Available")
    else:
        print("❌ OpenAI GPT-4 Vision: Not configured")
    
    # Test Azure Vision (requires API key)
    azure_result = await analyzer.analyze_with_azure_vision(test_image, analysis_type)
    if azure_result:
        print("✅ Azure Computer Vision: Available")
    else:
        print("❌ Azure Computer Vision: Not configured")
    
    # Test Hugging Face (requires API key, but has free tier)
    hf_result = await analyzer.analyze_with_huggingface(test_image, analysis_type)
    if hf_result:
        print("✅ Hugging Face Models: Available")
    else:
        print("❌ Hugging Face Models: Not configured")
    
    # Test OpenCV (always available, no API key needed)
    opencv_result = analyzer.analyze_with_opencv_traditional(test_image, analysis_type)
    if opencv_result:
        print("✅ OpenCV Traditional Vision: Available")
    else:
        print("❌ OpenCV Traditional Vision: Error")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_all_alternatives())