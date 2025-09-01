#!/usr/bin/env python3
"""
Demo script for AI WellnessVision API Gateway
Demonstrates the complete functionality of the unified API gateway and service orchestration.
"""

import asyncio
import time
from unittest.mock import MagicMock, AsyncMock

from src.api.gateway import APIGateway, ServiceOrchestrator, AnalysisRequest, ChatRequest, SpeechRequest
from src.api.auth import AuthManager

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(operation, result):
    """Print operation result"""
    status = result.get('status', 'unknown')
    processing_time = result.get('processing_time', 0)
    print(f"✓ {operation}: {status} (took {processing_time:.3f}s)")
    
    if status == 'success' and 'response' in result:
        print(f"  Response: {result['response'][:100]}...")
    elif status == 'error':
        print(f"  Error: {result.get('message', 'Unknown error')}")

async def demo_authentication():
    """Demonstrate authentication functionality"""
    print_section("Authentication & Authorization Demo")
    
    auth_manager = AuthManager()
    
    # Test user authentication
    print("1. Testing user authentication...")
    try:
        user = auth_manager.authenticate_user("testuser", "user123")
        print(f"✓ User authenticated: {user.username} (roles: {user.roles})")
        
        # Create access token
        token = auth_manager.create_access_token(user)
        print(f"✓ Access token created: {token[:30]}...")
        
        # Verify token
        token_data = auth_manager.verify_token(token)
        print(f"✓ Token verified: {token_data.username} (expires: {token_data.exp})")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
    
    # Test admin authentication
    print("\n2. Testing admin authentication...")
    try:
        admin = auth_manager.authenticate_user("admin", "admin123")
        print(f"✓ Admin authenticated: {admin.username} (roles: {admin.roles})")
        
        # Test permissions
        has_admin_perm = auth_manager.check_permission(admin.roles, ["admin"])
        has_user_perm = auth_manager.check_permission(admin.roles, ["user"])
        print(f"✓ Admin permissions - admin: {has_admin_perm}, user: {has_user_perm}")
        
    except Exception as e:
        print(f"✗ Admin authentication failed: {e}")
    
    # Test invalid authentication
    print("\n3. Testing invalid authentication...")
    try:
        auth_manager.authenticate_user("invalid", "wrong")
        print("✗ Should have failed!")
    except Exception:
        print("✓ Invalid authentication properly rejected")

async def demo_service_orchestration():
    """Demonstrate service orchestration"""
    print_section("Service Orchestration Demo")
    
    orchestrator = ServiceOrchestrator()
    
    # Test chat processing
    print("1. Testing chat message processing...")
    chat_request = ChatRequest(
        message="I have been feeling tired lately and have a headache. Can you help?",
        session_id="demo_session_001",
        user_id="demo_user",
        language="en"
    )
    
    result = await orchestrator.process_chat_message(chat_request)
    print_result("Chat processing", result)
    
    # Test image analysis
    print("\n2. Testing image analysis...")
    mock_file = MagicMock()
    mock_file.filename = "skin_condition.jpg"
    mock_file.read = AsyncMock(return_value=b"mock image data representing skin condition")
    
    analysis_request = AnalysisRequest(
        analysis_type="skin_condition",
        session_id="demo_session_001",
        user_id="demo_user",
        language="en"
    )
    
    result = await orchestrator.process_image_analysis(mock_file, analysis_request)
    print_result("Image analysis", result)
    
    # Test speech synthesis
    print("\n3. Testing speech synthesis...")
    speech_request = SpeechRequest(
        text="Based on your symptoms, I recommend consulting with a healthcare professional.",
        language="en"
    )
    
    result = await orchestrator.process_speech_synthesis(speech_request)
    print_result("Speech synthesis", result)
    
    # Test session history
    print("\n4. Testing session history...")
    history = await orchestrator.get_session_history("demo_session_001")
    if history['status'] == 'success':
        conv_count = len(history['conversation_history'])
        analysis_count = len(history['analysis_history'])
        print(f"✓ Session history retrieved: {conv_count} conversations, {analysis_count} analyses")
    else:
        print(f"✗ Session history failed: {history.get('message')}")

async def demo_concurrent_operations():
    """Demonstrate concurrent operations"""
    print_section("Concurrent Operations Demo")
    
    orchestrator = ServiceOrchestrator()
    
    print("Testing concurrent chat requests...")
    
    # Create multiple concurrent requests
    tasks = []
    messages = [
        "I have a headache",
        "My skin looks irritated", 
        "I'm feeling anxious",
        "Can you analyze this food?",
        "I need health advice"
    ]
    
    start_time = time.time()
    
    for i, message in enumerate(messages):
        chat_request = ChatRequest(
            message=message,
            session_id=f"concurrent_session_{i}",
            user_id=f"user_{i}",
            language="en"
        )
        tasks.append(orchestrator.process_chat_message(chat_request))
    
    # Execute all requests concurrently
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r['status'] == 'success')
    avg_processing_time = sum(r.get('processing_time', 0) for r in results) / len(results)
    
    print(f"✓ Processed {len(messages)} concurrent requests in {total_time:.3f}s")
    print(f"✓ Success rate: {successful}/{len(messages)} ({successful/len(messages)*100:.1f}%)")
    print(f"✓ Average processing time: {avg_processing_time:.3f}s")
    print(f"✓ Active sessions: {len(orchestrator.active_sessions)}")

async def demo_error_handling():
    """Demonstrate error handling"""
    print_section("Error Handling Demo")
    
    orchestrator = ServiceOrchestrator()
    
    # Test invalid analysis type
    print("1. Testing invalid analysis type...")
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.read = AsyncMock(return_value=b"mock data")
    
    invalid_request = AnalysisRequest(
        analysis_type="invalid_analysis_type",
        session_id="error_test_session",
        language="en"
    )
    
    result = await orchestrator.process_image_analysis(mock_file, invalid_request)
    print_result("Invalid analysis type", result)
    
    # Test empty message
    print("\n2. Testing empty chat message...")
    empty_chat = ChatRequest(
        message="",
        session_id="error_test_session_2",
        language="en"
    )
    
    result = await orchestrator.process_chat_message(empty_chat)
    print_result("Empty message", result)
    
    # Test nonexistent session history
    print("\n3. Testing nonexistent session...")
    result = await orchestrator.get_session_history("nonexistent_session")
    print_result("Nonexistent session", result)

def demo_service_status():
    """Demonstrate service status reporting"""
    print_section("Service Status Demo")
    
    orchestrator = ServiceOrchestrator()
    status = orchestrator.get_service_status()
    
    print("Service availability status:")
    for service_name, service_info in status.items():
        available = service_info.get('available', False)
        status_icon = "✓" if available else "✗"
        print(f"  {status_icon} {service_name}: {'Available' if available else 'Unavailable'}")
        
        # Show additional info if available
        if 'supported_languages' in service_info:
            langs = service_info['supported_languages'][:3]  # Show first 3
            print(f"    Languages: {', '.join(langs)}{'...' if len(service_info['supported_languages']) > 3 else ''}")

def demo_api_gateway():
    """Demonstrate API gateway functionality"""
    print_section("API Gateway Demo")
    
    gateway = APIGateway()
    
    print("1. API Gateway initialization...")
    print(f"✓ Gateway initialized: {type(gateway).__name__}")
    print(f"✓ Orchestrator available: {gateway.orchestrator is not None}")
    
    print("\n2. Mock server demonstration...")
    result = gateway.run_mock_server("localhost", 8000)
    print(f"✓ Mock server status: {result['status']}")
    print(f"✓ Host: {result['host']}, Port: {result['port']}")
    print(f"✓ FastAPI available: {result['fastapi_available']}")

async def main():
    """Main demo function"""
    print("🏥 AI WellnessVision API Gateway Demo")
    print("=====================================")
    print("This demo showcases the unified API gateway and service orchestration system.")
    
    try:
        # Run all demonstrations
        await demo_authentication()
        await demo_service_orchestration()
        await demo_concurrent_operations()
        await demo_error_handling()
        demo_service_status()
        demo_api_gateway()
        
        print_section("Demo Complete")
        print("✅ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Authentication and authorization with JWT tokens")
        print("• Service orchestration across AI services")
        print("• Request/response validation and error handling")
        print("• Concurrent request processing")
        print("• Session management and history tracking")
        print("• Comprehensive error handling and recovery")
        print("• Service status monitoring")
        print("• Mock mode operation for development")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())