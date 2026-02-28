#!/usr/bin/env python3
"""
Visual Question Answering (VQA) System
Combines image analysis with natural language processing for Q&A
"""

import google.generativeai as genai
import os
import logging
from PIL import Image
from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualQASystem:
    """Visual Question Answering system using multimodal AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and self.api_key != "your-gemini-api-key-here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.available = True
            logger.info("Visual QA System initialized with Gemini Vision")
        else:
            self.available = False
            logger.warning("Gemini API key not configured - VQA unavailable")
    
    def answer_question_about_image(self, image_path: str, question: str, 
                                  context: Optional[str] = None) -> Dict:
        """Answer a question about an image"""
        try:
            if not self.available:
                return self._generate_unavailable_response(question)
            
            # Load and validate image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create comprehensive prompt for VQA
            prompt = self._create_vqa_prompt(question, context)
            
            # Generate response using multimodal model
            response = self.model.generate_content([prompt, image])
            
            if response and response.text:
                return self._format_vqa_response(question, response.text, image_path)
            else:
                return self._generate_fallback_response(question)
                
        except Exception as e:
            logger.error(f"VQA error: {e}")
            return self._generate_error_response(question, str(e))
    
    def _create_vqa_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Create a comprehensive prompt for visual question answering"""
        
        base_prompt = f"""
You are an AI assistant specialized in analyzing images and answering questions about them.

USER QUESTION: {question}

Please analyze the image carefully and provide a detailed, helpful answer to the user's question.

INSTRUCTIONS:
1. Look at the image thoroughly before answering
2. Be specific and descriptive in your response
3. If the question is about health/medical topics, provide general information but remind users to consult healthcare professionals
4. If you cannot see certain details clearly, mention this limitation
5. Provide practical, actionable advice when appropriate
6. Be conversational and helpful in tone

RESPONSE FORMAT:
- Give a direct answer to the question
- Explain what you observe in the image that supports your answer
- Provide relevant recommendations or insights
- Include any important disclaimers if health-related

"""
        
        if context:
            base_prompt += f"\nADDITIONAL CONTEXT: {context}\n"
        
        return base_prompt
    
    def _format_vqa_response(self, question: str, response_text: str, image_path: str) -> Dict:
        """Format the VQA response"""
        return {
            "id": f"vqa_{int(datetime.now().timestamp())}",
            "type": "visual_qa",
            "question": question,
            "answer": response_text,
            "confidence": 0.85,  # Multimodal models generally have good confidence
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "processing_method": "Visual Question Answering (Multimodal AI)",
            "capabilities": [
                "Image understanding",
                "Natural language processing", 
                "Contextual reasoning",
                "Health guidance (general)"
            ]
        }
    
    def _generate_unavailable_response(self, question: str) -> Dict:
        """Generate response when VQA is unavailable"""
        return {
            "id": f"vqa_unavailable_{int(datetime.now().timestamp())}",
            "type": "visual_qa",
            "question": question,
            "answer": "I'm sorry, but the Visual Question Answering system is currently unavailable. This feature requires a configured Gemini API key to analyze images and answer questions about them.",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "processing_method": "System Unavailable",
            "error": "VQA system not configured"
        }
    
    def _generate_fallback_response(self, question: str) -> Dict:
        """Generate fallback response when analysis fails"""
        return {
            "id": f"vqa_fallback_{int(datetime.now().timestamp())}",
            "type": "visual_qa", 
            "question": question,
            "answer": "I wasn't able to analyze the image to answer your question. Please ensure the image is clear and try again. For health-related questions, consider consulting with a healthcare professional.",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "processing_method": "Fallback Response"
        }
    
    def _generate_error_response(self, question: str, error: str) -> Dict:
        """Generate error response"""
        return {
            "id": f"vqa_error_{int(datetime.now().timestamp())}",
            "type": "visual_qa",
            "question": question, 
            "answer": f"An error occurred while analyzing the image: {error}. Please try again with a different image or question.",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "processing_method": "Error Response",
            "error": error
        }
    
    def get_sample_questions(self, analysis_type: str = "general") -> List[str]:
        """Get sample questions users can ask about images"""
        
        sample_questions = {
            "skin": [
                "What do you see in this skin image?",
                "Does this look like a normal skin condition?",
                "What might be causing this skin issue?",
                "Are there any concerning features in this image?",
                "What skincare recommendations do you have?"
            ],
            "food": [
                "What food items do you see in this image?",
                "Is this a healthy meal?",
                "How many calories might this contain?",
                "What nutrients are present in this food?",
                "What are the ingredients in this dish?"
            ],
            "eye": [
                "How do these eyes look?",
                "Are there any signs of fatigue or strain?",
                "What might be causing any redness or irritation?",
                "Do you see any concerning symptoms?",
                "What eye care tips do you recommend?"
            ],
            "general": [
                "What do you see in this image?",
                "Can you describe what's happening here?",
                "What health-related observations can you make?",
                "Are there any concerns I should be aware of?",
                "What recommendations do you have based on this image?"
            ]
        }
        
        return sample_questions.get(analysis_type, sample_questions["general"])

# Global VQA instance
vqa_system = None

def get_vqa_system() -> VisualQASystem:
    """Get global VQA system instance"""
    global vqa_system
    if vqa_system is None:
        vqa_system = VisualQASystem()
    return vqa_system