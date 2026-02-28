#!/usr/bin/env python3
"""
Setup script for CNN health analysis models
This script initializes and prepares the CNN models for health image analysis
"""

import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'tensorflow',
        'numpy',
        'opencv-python',
        'PIL',
        'sklearn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            logger.info(f"✓ {package} is available")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} is missing")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    logger.info("Installing CNN dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_cnn.txt'
        ], check=True, capture_output=True, text=True)
        
        logger.info("✓ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to install dependencies: {e}")
        return False

def setup_model_directories():
    """Create necessary directories for models"""
    directories = [
        'models/cnn_health',
        'uploads',
        'src/ai_models',
        'data/training',
        'data/validation'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def initialize_cnn_models():
    """Initialize CNN models"""
    try:
        from src.ai_models.cnn_health_analyzer import CNNHealthAnalyzer
        
        logger.info("Initializing CNN Health Analyzer...")
        analyzer = CNNHealthAnalyzer()
        
        # Get model info
        model_info = analyzer.get_model_info()
        
        logger.info("✓ CNN models initialized successfully")
        logger.info("Available models:")
        
        for model_type, info in model_info.items():
            status = "✓ Loaded" if info.get('loaded') else "✗ Not loaded"
            logger.info(f"  {model_type}: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize CNN models: {e}")
        return False

def create_sample_data():
    """Create sample data structure for training (optional)"""
    sample_structure = {
        'data/training/skin': ['healthy', 'acne', 'eczema', 'dry_skin'],
        'data/training/eye': ['healthy', 'red_eye', 'dark_circles', 'tired'],
        'data/training/food': ['healthy', 'processed', 'high_calorie', 'balanced'],
        'data/validation/skin': ['healthy', 'acne', 'eczema', 'dry_skin'],
        'data/validation/eye': ['healthy', 'red_eye', 'dark_circles', 'tired'],
        'data/validation/food': ['healthy', 'processed', 'high_calorie', 'balanced']
    }
    
    for base_path, categories in sample_structure.items():
        for category in categories:
            full_path = Path(base_path) / category
            full_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("✓ Sample data structure created")

def test_cnn_functionality():
    """Test CNN functionality with a simple test"""
    try:
        from src.ai_models.cnn_health_analyzer import get_cnn_analyzer
        
        logger.info("Testing CNN analyzer...")
        analyzer = get_cnn_analyzer()
        
        # Test model info retrieval
        model_info = analyzer.get_model_info()
        
        if model_info:
            logger.info("✓ CNN analyzer is working correctly")
            return True
        else:
            logger.error("✗ CNN analyzer test failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ CNN test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("CNN HEALTH ANALYZER SETUP")
    print("=" * 60)
    print()
    
    # Step 1: Check dependencies
    logger.info("Step 1: Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        logger.info(f"Missing packages: {missing}")
        logger.info("Installing dependencies...")
        if not install_dependencies():
            logger.error("Failed to install dependencies. Please install manually:")
            logger.error("pip install -r requirements_cnn.txt")
            return False
    
    # Step 2: Setup directories
    logger.info("Step 2: Setting up directories...")
    setup_model_directories()
    
    # Step 3: Create sample data structure
    logger.info("Step 3: Creating data structure...")
    create_sample_data()
    
    # Step 4: Initialize CNN models
    logger.info("Step 4: Initializing CNN models...")
    if not initialize_cnn_models():
        logger.error("Failed to initialize CNN models")
        return False
    
    # Step 5: Test functionality
    logger.info("Step 5: Testing CNN functionality...")
    if not test_cnn_functionality():
        logger.error("CNN functionality test failed")
        return False
    
    print()
    print("=" * 60)
    print("✓ CNN HEALTH ANALYZER SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run the enhanced API server: python main_api_server_cnn.py")
    print("2. Test image analysis with CNN models")
    print("3. Optionally train models with your own data")
    print()
    print("Available analysis types:")
    print("  • skin - Skin condition analysis")
    print("  • eye - Eye health assessment") 
    print("  • food - Nutritional analysis")
    print("  • general - General health screening")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)