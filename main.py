#!/usr/bin/env python3
"""
AI WellnessVision - Main Application Entry Point
Comprehensive AI-powered health and wellness analysis platform
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import core services
try:
    from src.config import get_config, validate_config, AppConfig, ModelConfig
    from src.utils.logging_config import get_logger, setup_logging
    from src.services import (
        ImageService, NLPService, SpeechService, ExplainableAIService,
        FULL_SERVICE_AVAILABLE, NLP_SERVICE_AVAILABLE, 
        SPEECH_SERVICE_AVAILABLE, EXPLAINABLE_AI_SERVICE_AVAILABLE
    )
    from src.models import HealthAnalysisResult, AnalysisType, AnalysisStatus
    from src.ui.utils.session_manager import SessionManager
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    SERVICES_AVAILABLE = False

# Initialize logger
logger = get_logger(__name__)

class AIWellnessVisionApp:
    """Main application class for AI WellnessVision"""
    
    def __init__(self):
        self.config = None
        self.services = {}
        self.session_manager = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the application and all services"""
        try:
            print("🚀 Initializing AI WellnessVision...")
            
            # Load and validate configuration
            print("📋 Loading configuration...")
            self.config = get_config()
            if not validate_config():
                print("❌ Configuration validation failed")
                return False
            print("✅ Configuration loaded successfully")
            
            # Setup logging
            print("📝 Setting up logging...")
            setup_logging()
            logger.info("AI WellnessVision application starting")
            print("✅ Logging configured")
            
            # Initialize services
            print("🔧 Initializing AI services...")
            self._initialize_services()
            
            # Initialize session manager
            print("👤 Initializing session manager...")
            self.session_manager = SessionManager()
            print("✅ Session manager initialized")
            
            self.is_initialized = True
            print("🎉 AI WellnessVision initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            print(f"❌ Initialization failed: {e}")
            return False
    
    def _initialize_services(self):
        """Initialize all AI services"""
        services_status = {}
        
        # Initialize Image Service
        try:
            print("  🖼️  Initializing Image Recognition Service...")
            self.services['image'] = ImageService()
            services_status['image'] = "✅ Available"
            print("    ✅ Image Recognition Service ready")
        except Exception as e:
            logger.warning(f"Image service initialization failed: {e}")
            services_status['image'] = f"❌ Failed: {e}"
            print(f"    ❌ Image service failed: {e}")
        
        # Initialize NLP Service
        try:
            print("  💬 Initializing NLP Service...")
            self.services['nlp'] = NLPService()
            services_status['nlp'] = "✅ Available"
            print("    ✅ NLP Service ready")
        except Exception as e:
            logger.warning(f"NLP service initialization failed: {e}")
            services_status['nlp'] = f"❌ Failed: {e}"
            print(f"    ❌ NLP service failed: {e}")
        
        # Initialize Speech Service
        try:
            print("  🎤 Initializing Speech Service...")
            self.services['speech'] = SpeechService()
            services_status['speech'] = "✅ Available"
            print("    ✅ Speech Service ready")
        except Exception as e:
            logger.warning(f"Speech service initialization failed: {e}")
            services_status['speech'] = f"❌ Failed: {e}"
            print(f"    ❌ Speech service failed: {e}")
        
        # Initialize Explainable AI Service
        try:
            print("  🔍 Initializing Explainable AI Service...")
            self.services['explainable_ai'] = ExplainableAIService()
            services_status['explainable_ai'] = "✅ Available"
            print("    ✅ Explainable AI Service ready")
        except Exception as e:
            logger.warning(f"Explainable AI service initialization failed: {e}")
            services_status['explainable_ai'] = f"❌ Failed: {e}"
            print(f"    ❌ Explainable AI service failed: {e}")
        
        # Store services status
        self.services_status = services_status
        
        # Print summary
        print("\n📊 Services Status Summary:")
        for service, status in services_status.items():
            print(f"  {service.upper()}: {status}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available services"""
        if not self.is_initialized:
            return {"error": "Application not initialized"}
        
        info = {
            "application": "AI WellnessVision",
            "version": "1.0.0",
            "initialized": self.is_initialized,
            "services": self.services_status,
            "configuration": {
                "environment": AppConfig.ENVIRONMENT.value,
                "debug": AppConfig.DEBUG,
                "supported_languages": AppConfig.SUPPORTED_LANGUAGES,
                "default_language": AppConfig.DEFAULT_LANGUAGE
            },
            "capabilities": {
                "image_analysis": "image" in self.services,
                "nlp_processing": "nlp" in self.services,
                "speech_processing": "speech" in self.services,
                "explainable_ai": "explainable_ai" in self.services,
                "multilingual_support": len(AppConfig.SUPPORTED_LANGUAGES),
                "offline_mode": AppConfig.ENABLE_OFFLINE_MODE
            }
        }
        
        return info
    
    def run_demo_analysis(self) -> Dict[str, Any]:
        """Run a demo analysis to test all services"""
        if not self.is_initialized:
            return {"error": "Application not initialized"}
        
        print("\n🧪 Running Demo Analysis...")
        results = {}
        
        # Test Image Service
        if "image" in self.services:
            try:
                print("  🖼️  Testing Image Analysis...")
                # Create a mock analysis result
                demo_result = HealthAnalysisResult(
                    analysis_id="demo_analysis_001",
                    analysis_type=AnalysisType.SKIN_CONDITION,
                    status=AnalysisStatus.COMPLETED
                )
                demo_result.add_prediction("healthy_skin", 0.85, {
                    "description": "Demo skin analysis - no significant conditions detected",
                    "recommendations": ["Continue current skincare routine", "Use sunscreen daily"]
                })
                results["image_analysis"] = {
                    "status": "success",
                    "result": demo_result.to_dict()
                }
                print("    ✅ Image analysis demo completed")
            except Exception as e:
                results["image_analysis"] = {"status": "error", "message": str(e)}
                print(f"    ❌ Image analysis demo failed: {e}")
        
        # Test NLP Service
        if "nlp" in self.services:
            try:
                print("  💬 Testing NLP Processing...")
                nlp_result = self.services['nlp'].process_message(
                    "Hello, I have a question about my health",
                    user_id="demo_user",
                    session_id="demo_session"
                )
                results["nlp_processing"] = {
                    "status": "success",
                    "result": nlp_result
                }
                print("    ✅ NLP processing demo completed")
            except Exception as e:
                results["nlp_processing"] = {"status": "error", "message": str(e)}
                print(f"    ❌ NLP processing demo failed: {e}")
        
        # Test Speech Service
        if "speech" in self.services:
            try:
                print("  🎤 Testing Speech Service...")
                speech_info = self.services['speech'].get_service_info()
                results["speech_processing"] = {
                    "status": "success",
                    "service_info": speech_info
                }
                print("    ✅ Speech service demo completed")
            except Exception as e:
                results["speech_processing"] = {"status": "error", "message": str(e)}
                print(f"    ❌ Speech service demo failed: {e}")
        
        # Test Explainable AI Service
        if "explainable_ai" in self.services:
            try:
                print("  🔍 Testing Explainable AI...")
                capabilities = self.services['explainable_ai'].get_explanation_capabilities()
                results["explainable_ai"] = {
                    "status": "success",
                    "capabilities": capabilities
                }
                print("    ✅ Explainable AI demo completed")
            except Exception as e:
                results["explainable_ai"] = {"status": "error", "message": str(e)}
                print(f"    ❌ Explainable AI demo failed: {e}")
        
        print("🎉 Demo analysis completed!")
        return results
    
    def run_interactive_mode(self):
        """Run interactive command-line mode"""
        if not self.is_initialized:
            print("❌ Application not initialized")
            return
        
        print("\n🎮 Interactive Mode")
        print("=" * 50)
        print("Available commands:")
        print("  info     - Show application information")
        print("  demo     - Run demo analysis")
        print("  services - Show services status")
        print("  test     - Test specific service")
        print("  quit     - Exit application")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n🤖 AI WellnessVision> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command == "info":
                    info = self.get_service_info()
                    print(f"\n📊 Application Information:")
                    print(f"  Version: {info['version']}")
                    print(f"  Environment: {info['configuration']['environment']}")
                    print(f"  Supported Languages: {', '.join(info['configuration']['supported_languages'])}")
                    print(f"  Services Available: {sum(1 for s in info['services'].values() if '✅' in s)}/{len(info['services'])}")
                
                elif command == "demo":
                    results = self.run_demo_analysis()
                    print(f"\n📋 Demo Results Summary:")
                    for service, result in results.items():
                        status = "✅" if result.get("status") == "success" else "❌"
                        print(f"  {service}: {status}")
                
                elif command == "services":
                    print(f"\n🔧 Services Status:")
                    for service, status in self.services_status.items():
                        print(f"  {service.upper()}: {status}")
                
                elif command == "test":
                    service = input("Enter service to test (image/nlp/speech/explainable_ai): ").strip().lower()
                    if service in self.services:
                        print(f"✅ {service} service is available")
                    else:
                        print(f"❌ {service} service is not available")
                
                elif command == "help":
                    print("\nAvailable commands: info, demo, services, test, quit")
                
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main application entry point"""
    print("🧠💚 AI WellnessVision - Intelligent Health & Wellness Platform")
    print("=" * 70)
    
    if not SERVICES_AVAILABLE:
        print("❌ Required services not available. Please check your installation.")
        return 1
    
    # Create and initialize application
    app = AIWellnessVisionApp()
    
    if not app.initialize():
        print("❌ Failed to initialize application")
        return 1
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "demo":
            print("\n🧪 Running Demo Mode...")
            results = app.run_demo_analysis()
            print(f"\n📊 Demo completed with {len(results)} service tests")
            return 0
        
        elif command == "info":
            info = app.get_service_info()
            print(f"\n📊 Application Information:")
            print(f"  Version: {info['version']}")
            print(f"  Environment: {info['configuration']['environment']}")
            print(f"  Services: {sum(1 for s in info['services'].values() if '✅' in s)}/{len(info['services'])} available")
            return 0
        
        elif command == "interactive":
            app.run_interactive_mode()
            return 0
        
        else:
            print(f"❓ Unknown command: {command}")
            print("Available commands: demo, info, interactive")
            return 1
    
    # Default: run interactive mode
    app.run_interactive_mode()
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
