#!/usr/bin/env python3
"""
AI WellnessVision - Demo Application
Interactive demonstration of all AI services and capabilities
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import core services
try:
    from src.config import get_config, validate_config, AppConfig
    from src.utils.logging_config import get_logger, setup_logging
    from src.services import (
        ImageService, NLPService, SpeechService, ExplainableAIService
    )
    from src.models import (
        HealthAnalysisResult, AnalysisType, AnalysisStatus,
        HealthCondition, FoodItem, EmotionDetection
    )
    from src.ui.utils.session_manager import SessionManager
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    SERVICES_AVAILABLE = False

# Initialize logger
logger = get_logger(__name__)

class AIWellnessVisionDemo:
    """Demo application showcasing AI WellnessVision capabilities"""
    
    def __init__(self):
        self.services = {}
        self.session_manager = None
        self.is_initialized = False
        self.demo_data = self._load_demo_data()
        
    def _load_demo_data(self) -> Dict[str, Any]:
        """Load demo data for testing"""
        return {
            "sample_images": {
                "skin_condition": "data/images/skin/sample_skin.jpg",
                "eye_health": "data/images/eye/sample_eye.jpg", 
                "food_recognition": "data/images/food/sample_food.jpg",
                "emotion_detection": "data/images/emotion/sample_face.jpg"
            },
            "sample_texts": {
                "health_questions": [
                    "I have a headache, what should I do?",
                    "What are the symptoms of high blood pressure?",
                    "How can I improve my sleep quality?",
                    "What foods are good for heart health?",
                    "I feel tired all the time, what could be the cause?"
                ],
                "multilingual": {
                    "en": "Hello, I need help with my health",
                    "hi": "नमस्ते, मुझे अपने स्वास्थ्य के लिए मदद चाहिए",
                    "ta": "வணக்கம், எனக்கு என் உடல்நலத்திற்கு உதவி தேவை"
                }
            },
            "sample_audio": {
                "health_question": "data/audio/sample_health_question.wav",
                "voice_note": "data/audio/sample_voice_note.wav"
            }
        }
    
    def initialize(self) -> bool:
        """Initialize the demo application"""
        try:
            print("🚀 Initializing AI WellnessVision Demo...")
            
            # Load configuration
            self.config = get_config()
            if not validate_config():
                print("❌ Configuration validation failed")
                return False
            
            # Setup logging
            setup_logging()
            logger.info("AI WellnessVision Demo starting")
            
            # Initialize services
            self._initialize_services()
            
            # Initialize session manager
            self.session_manager = SessionManager()
            
            self.is_initialized = True
            print("🎉 Demo application initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Demo initialization failed: {e}")
            print(f"❌ Demo initialization failed: {e}")
            return False
    
    def _initialize_services(self):
        """Initialize all AI services for demo"""
        print("🔧 Initializing AI services for demo...")
        
        # Initialize Image Service
        try:
            self.services['image'] = ImageService()
            print("  ✅ Image Recognition Service ready")
        except Exception as e:
            print(f"  ❌ Image service failed: {e}")
        
        # Initialize NLP Service
        try:
            self.services['nlp'] = NLPService()
            print("  ✅ NLP Service ready")
        except Exception as e:
            print(f"  ❌ NLP service failed: {e}")
        
        # Initialize Speech Service
        try:
            self.services['speech'] = SpeechService()
            print("  ✅ Speech Service ready")
        except Exception as e:
            print(f"  ❌ Speech service failed: {e}")
        
        # Initialize Explainable AI Service
        try:
            self.services['explainable_ai'] = ExplainableAIService()
            print("  ✅ Explainable AI Service ready")
        except Exception as e:
            print(f"  ❌ Explainable AI service failed: {e}")
    
    def demo_image_analysis(self):
        """Demonstrate image analysis capabilities"""
        print("\n🖼️  IMAGE ANALYSIS DEMO")
        print("=" * 50)
        
        if "image" not in self.services:
            print("❌ Image service not available")
            return
        
        # Demo different types of image analysis
        analysis_types = [
            (AnalysisType.SKIN_CONDITION, "Skin Condition Analysis"),
            (AnalysisType.EYE_HEALTH, "Eye Health Screening"),
            (AnalysisType.FOOD_RECOGNITION, "Food Recognition"),
            (AnalysisType.EMOTION_DETECTION, "Emotion Detection")
        ]
        
        for analysis_type, description in analysis_types:
            print(f"\n📋 {description}")
            print("-" * 30)
            
            try:
                # Create demo analysis result
                demo_result = self._create_demo_analysis_result(analysis_type)
                
                print(f"  Analysis ID: {demo_result.analysis_id}")
                print(f"  Type: {demo_result.analysis_type.value}")
                print(f"  Status: {demo_result.status.value}")
                
                if demo_result.predictions:
                    top_prediction = demo_result.get_top_prediction()
                    print(f"  Top Prediction: {top_prediction['label']}")
                    print(f"  Confidence: {top_prediction['confidence']:.2f}")
                    
                    if 'details' in top_prediction:
                        details = top_prediction['details']
                        if 'description' in details:
                            print(f"  Description: {details['description']}")
                        if 'recommendations' in details:
                            print(f"  Recommendations: {', '.join(details['recommendations'][:2])}")
                
                print(f"  Processing Time: {demo_result.processing_time:.2f}s")
                print("  ✅ Demo completed successfully")
                
            except Exception as e:
                print(f"  ❌ Demo failed: {e}")
    
    def _create_demo_analysis_result(self, analysis_type: AnalysisType) -> HealthAnalysisResult:
        """Create a demo analysis result for the given type"""
        demo_results = {
            AnalysisType.SKIN_CONDITION: {
                "label": "healthy_skin",
                "confidence": 0.87,
                "details": {
                    "description": "No significant skin conditions detected. Skin appears healthy with good texture and tone.",
                    "recommendations": [
                        "Continue current skincare routine",
                        "Use sunscreen daily (SPF 30+)",
                        "Stay hydrated",
                        "Regular skin self-examinations"
                    ]
                }
            },
            AnalysisType.EYE_HEALTH: {
                "label": "healthy_eye",
                "confidence": 0.92,
                "details": {
                    "description": "No signs of diabetic retinopathy, glaucoma, or other eye conditions detected.",
                    "recommendations": [
                        "Continue regular eye exams",
                        "Protect eyes from UV exposure",
                        "Maintain healthy diet rich in vitamins",
                        "Take regular breaks from screen time"
                    ]
                }
            },
            AnalysisType.FOOD_RECOGNITION: {
                "label": "apple",
                "confidence": 0.94,
                "details": {
                    "description": "Fresh apple detected with good nutritional value.",
                    "recommendations": [
                        "Excellent source of fiber and vitamin C",
                        "Good for heart health",
                        "Helps with digestion",
                        "Low calorie, high nutrition"
                    ]
                }
            },
            AnalysisType.EMOTION_DETECTION: {
                "label": "happy",
                "confidence": 0.78,
                "details": {
                    "description": "Positive emotional state detected with good wellness indicators.",
                    "recommendations": [
                        "Maintain positive outlook",
                        "Continue current wellness practices",
                        "Regular social interactions",
                        "Adequate sleep and exercise"
                    ]
                }
            }
        }
        
        result = HealthAnalysisResult(
            analysis_id=f"demo_{analysis_type.value}_{int(time.time())}",
            analysis_type=analysis_type,
            status=AnalysisStatus.COMPLETED,
            processing_time=1.2 + (hash(analysis_type.value) % 100) / 100
        )
        
        demo_data = demo_results.get(analysis_type, {
            "label": "unknown",
            "confidence": 0.5,
            "details": {"description": "Demo analysis completed", "recommendations": []}
        })
        
        result.add_prediction(
            demo_data["label"],
            demo_data["confidence"],
            demo_data["details"]
        )
        
        return result
    
    def demo_nlp_processing(self):
        """Demonstrate NLP processing capabilities"""
        print("\n💬 NLP PROCESSING DEMO")
        print("=" * 50)
        
        if "nlp" not in self.services:
            print("❌ NLP service not available")
            return
        
        # Demo health questions
        print("\n📋 Health Question Processing")
        print("-" * 30)
        
        for i, question in enumerate(self.demo_data["sample_texts"]["health_questions"], 1):
            print(f"\n{i}. Question: {question}")
            
            try:
                result = self.services['nlp'].process_message(
                    question,
                    user_id="demo_user",
                    session_id="demo_session"
                )
                
                print(f"   Response: {result['response']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Language: {result['language']}")
                print(f"   Sentiment: {result['sentiment']['sentiment']} ({result['sentiment']['confidence']:.2f})")
                print(f"   Processing Time: {result['processing_time']:.3f}s")
                print("   ✅ Processed successfully")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
        
        # Demo multilingual support
        print("\n🌐 Multilingual Processing Demo")
        print("-" * 30)
        
        for lang, text in self.demo_data["sample_texts"]["multilingual"].items():
            print(f"\nLanguage: {lang.upper()}")
            print(f"Text: {text}")
            
            try:
                result = self.services['nlp'].process_message(
                    text,
                    user_id="demo_user",
                    session_id="demo_session",
                    language=lang
                )
                
                print(f"Response: {result['response']}")
                print(f"Detected Language: {result['language']}")
                print("✅ Multilingual processing successful")
                
            except Exception as e:
                print(f"❌ Multilingual processing failed: {e}")
    
    def demo_speech_processing(self):
        """Demonstrate speech processing capabilities"""
        print("\n🎤 SPEECH PROCESSING DEMO")
        print("=" * 50)
        
        if "speech" not in self.services:
            print("❌ Speech service not available")
            return
        
        # Get service information
        try:
            service_info = self.services['speech'].get_service_info()
            print(f"\n📊 Speech Service Information:")
            print(f"  Whisper Available: {service_info['whisper_available']}")
            print(f"  Audio Libraries Available: {service_info['audio_libs_available']}")
            print(f"  Supported Languages: {', '.join(service_info['supported_languages'])}")
            print(f"  Supported Formats: {', '.join(service_info['supported_audio_formats'])}")
            print(f"  Max Duration: {service_info['max_audio_duration']}s")
            print(f"  Max File Size: {service_info['max_file_size'] / (1024*1024):.1f}MB")
        except Exception as e:
            print(f"❌ Failed to get service info: {e}")
        
        # Demo text-to-speech
        print(f"\n🔊 Text-to-Speech Demo")
        print("-" * 30)
        
        demo_texts = [
            "Hello, I'm your AI health assistant. How can I help you today?",
            "Based on your analysis, I recommend consulting with a healthcare professional.",
            "Your health data shows positive trends. Keep up the good work!"
        ]
        
        for i, text in enumerate(demo_texts, 1):
            print(f"\n{i}. Text: {text}")
            
            try:
                result = self.services['speech'].synthesize_speech(
                    text,
                    language='en',
                    voice_settings={'speed': 1.0, 'pitch': 1.0}
                )
                
                if result['status'] == 'success':
                    print(f"   Audio Generated: {result['audio_path']}")
                    print(f"   Duration: {result['duration']:.2f}s")
                    print(f"   Word Count: {result['word_count']}")
                    print("   ✅ TTS successful")
                else:
                    print(f"   ❌ TTS failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ TTS failed: {e}")
        
        # Demo available voices
        try:
            voices = self.services['speech'].get_available_voices()
            print(f"\n🎭 Available Voices:")
            for lang, voice_list in voices.items():
                print(f"  {lang.upper()}: {', '.join(voice_list)}")
        except Exception as e:
            print(f"❌ Failed to get voices: {e}")
    
    def demo_explainable_ai(self):
        """Demonstrate explainable AI capabilities"""
        print("\n🔍 EXPLAINABLE AI DEMO")
        print("=" * 50)
        
        if "explainable_ai" not in self.services:
            print("❌ Explainable AI service not available")
            return
        
        # Get capabilities
        try:
            capabilities = self.services['explainable_ai'].get_explanation_capabilities()
            print(f"\n📊 Explainable AI Capabilities:")
            print(f"  Grad-CAM Available: {capabilities['gradcam_available']}")
            print(f"  LIME Available: {capabilities['lime_available']}")
            print(f"  Visualization Available: {capabilities['visualization_available']}")
            print(f"  Supported Analysis Types: {', '.join(capabilities['supported_analysis_types'])}")
            print(f"  Explanation Methods: {', '.join(capabilities['explanation_methods'])}")
            print(f"  Visualization Formats: {', '.join(capabilities['visualization_formats'])}")
        except Exception as e:
            print(f"❌ Failed to get capabilities: {e}")
        
        # Demo explanation generation
        print(f"\n🧠 Explanation Generation Demo")
        print("-" * 30)
        
        # Create a demo analysis result
        demo_result = self._create_demo_analysis_result(AnalysisType.SKIN_CONDITION)
        
        try:
            explanation_result = self.services['explainable_ai'].explain_prediction(
                demo_result,
                explanation_types=['gradcam', 'lime', 'decision_path', 'visualization']
            )
            
            if explanation_result['status'] == 'success':
                print(f"  Analysis ID: {explanation_result['analysis_id']}")
                print(f"  Analysis Type: {explanation_result['analysis_type']}")
                print(f"  Explanation Types: {', '.join(explanation_result['explanation_types'])}")
                print(f"  Processing Time: {explanation_result['processing_time']:.3f}s")
                
                # Show summary
                if 'summary' in explanation_result:
                    summary = explanation_result['summary']
                    print(f"\n  📋 Explanation Summary:")
                    print(f"    Prediction Confidence: {summary.get('prediction_confidence', 0):.2f}")
                    print(f"    Reliability Score: {summary.get('reliability_score', 0):.2f}")
                    print(f"    Key Insights: {len(summary.get('key_insights', []))}")
                    print(f"    Recommendations: {len(summary.get('recommendations', []))}")
                
                print("  ✅ Explanation generated successfully")
            else:
                print(f"  ❌ Explanation failed: {explanation_result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Explanation failed: {e}")
    
    def demo_integration_workflow(self):
        """Demonstrate integrated workflow using multiple services"""
        print("\n🔄 INTEGRATED WORKFLOW DEMO")
        print("=" * 50)
        
        print("\n📋 Scenario: Complete Health Analysis Workflow")
        print("-" * 40)
        
        # Step 1: User asks a health question
        print("\n1️⃣ User Input (Text)")
        user_question = "I've been having headaches and feeling tired. What should I do?"
        print(f"   Question: {user_question}")
        
        # Step 2: NLP processing
        if "nlp" in self.services:
            print("\n2️⃣ NLP Processing")
            try:
                nlp_result = self.services['nlp'].process_message(
                    user_question,
                    user_id="demo_user",
                    session_id="demo_session"
                )
                print(f"   Response: {nlp_result['response']}")
                print(f"   Sentiment: {nlp_result['sentiment']['sentiment']}")
                print(f"   Confidence: {nlp_result['confidence']:.2f}")
            except Exception as e:
                print(f"   ❌ NLP processing failed: {e}")
        
        # Step 3: Image analysis (if user uploads image)
        if "image" in self.services:
            print("\n3️⃣ Image Analysis (Simulated)")
            try:
                image_result = self._create_demo_analysis_result(AnalysisType.SKIN_CONDITION)
                print(f"   Analysis Type: {image_result.analysis_type.value}")
                print(f"   Top Prediction: {image_result.get_top_prediction()['label']}")
                print(f"   Confidence: {image_result.get_top_prediction()['confidence']:.2f}")
            except Exception as e:
                print(f"   ❌ Image analysis failed: {e}")
        
        # Step 4: Explainable AI
        if "explainable_ai" in self.services and "image" in self.services:
            print("\n4️⃣ Explainable AI Analysis")
            try:
                explanation = self.services['explainable_ai'].explain_prediction(
                    image_result,
                    explanation_types=['decision_path']
                )
                if explanation['status'] == 'success':
                    print(f"   Explanation Generated: ✅")
                    print(f"   Methods Used: {', '.join(explanation['explanation_types'])}")
                else:
                    print(f"   ❌ Explanation failed")
            except Exception as e:
                print(f"   ❌ Explanation failed: {e}")
        
        # Step 5: Voice response
        if "speech" in self.services and "nlp" in self.services:
            print("\n5️⃣ Voice Response Generation")
            try:
                response_text = nlp_result['response']
                tts_result = self.services['speech'].synthesize_speech(
                    response_text,
                    language='en'
                )
                if tts_result['status'] == 'success':
                    print(f"   Audio Generated: ✅")
                    print(f"   Duration: {tts_result['duration']:.2f}s")
                else:
                    print(f"   ❌ TTS failed")
            except Exception as e:
                print(f"   ❌ TTS failed: {e}")
        
        print("\n🎉 Integrated workflow completed!")
        print("   This demonstrates how all AI services work together")
        print("   to provide comprehensive health analysis and support.")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        if not self.is_initialized:
            print("❌ Demo not initialized")
            return
        
        print("\n🎬 AI WELLNESSVISION - COMPLETE DEMONSTRATION")
        print("=" * 70)
        print("This demo showcases all the AI capabilities of the platform:")
        print("• Image Recognition & Analysis")
        print("• Natural Language Processing")
        print("• Speech Recognition & Synthesis")
        print("• Explainable AI & Decision Transparency")
        print("• Integrated Multi-Modal Workflows")
        print("=" * 70)
        
        # Run all demos
        self.demo_image_analysis()
        self.demo_nlp_processing()
        self.demo_speech_processing()
        self.demo_explainable_ai()
        self.demo_integration_workflow()
        
        print("\n🎊 DEMONSTRATION COMPLETE!")
        print("=" * 70)
        print("Thank you for exploring AI WellnessVision!")
        print("This platform combines cutting-edge AI technologies")
        print("to provide intelligent health and wellness support.")
        print("=" * 70)
    
    def run_interactive_demo(self):
        """Run interactive demo mode"""
        if not self.is_initialized:
            print("❌ Demo not initialized")
            return
        
        print("\n🎮 INTERACTIVE DEMO MODE")
        print("=" * 50)
        print("Available demos:")
        print("  1 - Image Analysis Demo")
        print("  2 - NLP Processing Demo")
        print("  3 - Speech Processing Demo")
        print("  4 - Explainable AI Demo")
        print("  5 - Integrated Workflow Demo")
        print("  all - Run complete demonstration")
        print("  quit - Exit demo")
        print("=" * 50)
        
        while True:
            try:
                choice = input("\n🎯 Choose demo (1-5, all, quit): ").strip().lower()
                
                if choice == "quit" or choice == "exit":
                    print("👋 Thanks for trying AI WellnessVision Demo!")
                    break
                elif choice == "1":
                    self.demo_image_analysis()
                elif choice == "2":
                    self.demo_nlp_processing()
                elif choice == "3":
                    self.demo_speech_processing()
                elif choice == "4":
                    self.demo_explainable_ai()
                elif choice == "5":
                    self.demo_integration_workflow()
                elif choice == "all":
                    self.run_complete_demo()
                elif choice == "help":
                    print("\nAvailable options: 1, 2, 3, 4, 5, all, quit")
                else:
                    print("❓ Invalid choice. Type 'help' for options.")
                    
            except KeyboardInterrupt:
                print("\n👋 Thanks for trying AI WellnessVision Demo!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main demo application entry point"""
    print("🧠💚 AI WellnessVision - Interactive Demo")
    print("=" * 60)
    
    if not SERVICES_AVAILABLE:
        print("❌ Required services not available. Please check your installation.")
        return 1
    
    # Create and initialize demo
    demo = AIWellnessVisionDemo()
    
    if not demo.initialize():
        print("❌ Failed to initialize demo")
        return 1
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "complete":
            demo.run_complete_demo()
            return 0
        elif command == "interactive":
            demo.run_interactive_demo()
            return 0
        else:
            print(f"❓ Unknown command: {command}")
            print("Available commands: complete, interactive")
            return 1
    
    # Default: run interactive demo
    demo.run_interactive_demo()
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
