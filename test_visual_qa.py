#!/usr/bin/env python3
"""
Test Visual Question Answering (VQA) System
Demonstrates image + text question answering capabilities
"""

import requests
import json
from pathlib import Path
import time

def test_vqa_system():
    """Test the Visual QA system with sample questions"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Visual Question Answering System")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   python main_api_server_cnn.py")
        return
    
    # Test 2: Get sample questions
    print("\n📝 Getting sample VQA questions...")
    try:
        response = requests.get(f"{base_url}/api/v1/analysis/visual-qa/samples?analysis_type=general")
        if response.status_code == 200:
            samples = response.json()
            print("✅ Sample questions retrieved:")
            for i, question in enumerate(samples.get('sample_questions', []), 1):
                print(f"   {i}. {question}")
        else:
            print(f"❌ Failed to get samples: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting samples: {e}")
    
    # Test 3: Test VQA with a sample image (if available)
    print("\n🖼️ Testing Visual Question Answering...")
    
    # Look for test images in uploads directory
    uploads_dir = Path("uploads")
    test_images = []
    
    if uploads_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']:
            test_images.extend(uploads_dir.glob(ext))
    
    if test_images:
        test_image = test_images[0]
        print(f"📸 Using test image: {test_image.name}")
        
        # Sample questions to test
        test_questions = [
            "What do you see in this image?",
            "Can you describe the main elements in this picture?",
            "Are there any health-related observations you can make?",
            "What recommendations do you have based on this image?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🤔 Question {i}: {question}")
            
            try:
                with open(test_image, 'rb') as img_file:
                    files = {'image': (test_image.name, img_file, 'image/jpeg')}
                    data = {'question': question}
                    
                    response = requests.post(
                        f"{base_url}/api/v1/analysis/visual-qa",
                        files=files,
                        data=data,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Answer: {result.get('answer', 'No answer provided')}")
                    print(f"   Confidence: {result.get('confidence', 0):.2f}")
                    print(f"   Method: {result.get('processing_method', 'Unknown')}")
                else:
                    print(f"❌ VQA failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing VQA: {e}")
            
            # Small delay between requests
            time.sleep(1)
    
    else:
        print("📸 No test images found in uploads directory")
        print("   To test VQA:")
        print("   1. Upload an image through the Flutter app")
        print("   2. Or manually place an image in the 'uploads' directory")
        print("   3. Then run this test again")
    
    # Test 4: Test VQA with different analysis types
    print("\n🔍 Testing sample questions for different analysis types...")
    analysis_types = ['skin', 'food', 'eye', 'general']
    
    for analysis_type in analysis_types:
        try:
            response = requests.get(f"{base_url}/api/v1/analysis/visual-qa/samples?analysis_type={analysis_type}")
            if response.status_code == 200:
                samples = response.json()
                questions = samples.get('sample_questions', [])
                print(f"✅ {analysis_type.title()} questions ({len(questions)} available)")
            else:
                print(f"❌ Failed to get {analysis_type} samples")
        except Exception as e:
            print(f"❌ Error getting {analysis_type} samples: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 VQA System Test Complete!")
    print("\n💡 How to use VQA in your Flutter app:")
    print("   1. Upload an image")
    print("   2. Ask a question about the image")
    print("   3. Get an AI-powered answer with visual understanding")
    print("\n🔗 VQA Endpoint: POST /api/v1/analysis/visual-qa")
    print("   Parameters: image (file), question (text), context (optional)")

def create_sample_vqa_requests():
    """Create sample VQA request examples"""
    
    print("\n📋 Sample VQA Request Examples:")
    print("-" * 30)
    
    examples = [
        {
            "question": "What food items do you see in this image?",
            "context": "I'm trying to track my nutrition",
            "expected_use": "Food analysis and nutrition tracking"
        },
        {
            "question": "Does this skin condition look concerning?",
            "context": "I noticed this spot recently",
            "expected_use": "Skin health assessment"
        },
        {
            "question": "How do my eyes look? Any signs of fatigue?",
            "context": "I've been working long hours",
            "expected_use": "Eye health and wellness check"
        },
        {
            "question": "What exercise equipment do you see here?",
            "context": "Planning my home workout",
            "expected_use": "Fitness and exercise planning"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['expected_use']}:")
        print(f"   Question: \"{example['question']}\"")
        print(f"   Context: \"{example['context']}\"")
    
    print("\n🚀 Try these questions with your own images!")

if __name__ == "__main__":
    test_vqa_system()
    create_sample_vqa_requests()