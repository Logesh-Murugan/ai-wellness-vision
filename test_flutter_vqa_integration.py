#!/usr/bin/env python3
"""
Test Flutter Visual Q&A Integration
Verifies that the VQA system works with Flutter app
"""

import requests
import json
import time
from pathlib import Path

def test_flutter_vqa_integration():
    """Test the complete Flutter VQA integration"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Flutter Visual Q&A Integration")
    print("=" * 50)
    
    # Test 1: Check backend server
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Please start: python main_api_server_cnn.py")
        return False
    
    # Test 2: Test VQA endpoints
    print("\n🔍 Testing VQA API endpoints...")
    
    # Test sample questions endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/analysis/visual-qa/samples")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample questions endpoint working ({len(data.get('sample_questions', []))} questions)")
        else:
            print(f"❌ Sample questions endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sample questions endpoint error: {e}")
        return False
    
    # Test 3: Check for test images
    uploads_dir = Path("uploads")
    test_images = []
    
    if uploads_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']:
            test_images.extend(uploads_dir.glob(ext))
    
    if not test_images:
        print("\n📸 No test images found")
        print("   To fully test VQA:")
        print("   1. Upload an image through your Flutter app")
        print("   2. Or place a test image in the 'uploads' directory")
        return True
    
    # Test 4: Test VQA with actual image
    test_image = test_images[0]
    print(f"\n🖼️ Testing VQA with image: {test_image.name}")
    
    test_question = "What do you see in this image?"
    
    try:
        with open(test_image, 'rb') as img_file:
            files = {'image': (test_image.name, img_file, 'image/jpeg')}
            data = {'question': test_question}
            
            response = requests.post(
                f"{base_url}/api/v1/analysis/visual-qa",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ VQA endpoint working successfully")
            print(f"   Question: {result.get('question', 'N/A')}")
            print(f"   Answer: {result.get('answer', 'N/A')[:100]}...")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            return True
        else:
            print(f"❌ VQA endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ VQA endpoint error: {e}")
        return False

def check_flutter_files():
    """Check if Flutter VQA files are properly configured"""
    
    print("\n📁 Checking Flutter VQA files...")
    
    files_to_check = [
        "flutter_app/lib/features/image_analysis/presentation/pages/visual_qa_page.dart",
        "flutter_app/lib/core/services/visual_qa_service.dart",
        "flutter_app/lib/core/router/app_router.dart"
    ]
    
    all_files_exist = True
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_exist = False
    
    return all_files_exist

def provide_flutter_testing_guide():
    """Provide guide for testing VQA in Flutter app"""
    
    print("\n" + "=" * 50)
    print("🚀 Flutter VQA Testing Guide")
    print("=" * 50)
    
    print("\n📱 To test Visual Q&A in your Flutter app:")
    print("1. Start your backend server:")
    print("   python main_api_server_cnn.py")
    
    print("\n2. Start your Flutter app:")
    print("   cd flutter_app")
    print("   flutter run -d web-server --web-port 3000")
    
    print("\n3. Open your app:")
    print("   http://localhost:3000")
    
    print("\n4. Navigate to Visual Q&A:")
    print("   - Click 'Visual Q&A' on the home page")
    print("   - Or go directly to: http://localhost:3000/visual-qa")
    
    print("\n5. Test the functionality:")
    print("   - Upload an image (camera or gallery)")
    print("   - Enter a question like 'What do you see?'")
    print("   - Click 'Ask Question'")
    print("   - View the AI response")
    
    print("\n🔧 If Visual Q&A page is not showing:")
    print("   - Check browser console for errors")
    print("   - Verify backend is running on port 8000")
    print("   - Check network tab for API calls")
    
    print("\n💡 Sample questions to try:")
    sample_questions = [
        "What do you see in this image?",
        "Are there any health concerns visible?",
        "What recommendations do you have?",
        "Is this a healthy choice?",
        "Can you describe the main elements?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        print(f"   {i}. {question}")

if __name__ == "__main__":
    # Test backend integration
    backend_working = test_flutter_vqa_integration()
    
    # Check Flutter files
    files_exist = check_flutter_files()
    
    # Provide testing guide
    provide_flutter_testing_guide()
    
    print("\n" + "=" * 50)
    if backend_working and files_exist:
        print("🎉 VQA Integration Status: READY TO TEST")
        print("   Your Visual Q&A system is properly configured!")
    elif backend_working:
        print("⚠️  VQA Integration Status: BACKEND OK, CHECK FLUTTER FILES")
    elif files_exist:
        print("⚠️  VQA Integration Status: FLUTTER OK, CHECK BACKEND")
    else:
        print("❌ VQA Integration Status: NEEDS CONFIGURATION")
    
    print("=" * 50)