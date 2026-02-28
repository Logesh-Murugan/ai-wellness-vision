import 'dart:io';
import 'package:dio/dio.dart';

void main() async {
  print('🔍 Testing backend connection...');
  
  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  
  try {
    // Test health endpoint
    print('📡 Testing health endpoint...');
    final healthResponse = await dio.get('/api/v1/health');
    print('✅ Health check: ${healthResponse.data}');
    
    // Test login endpoint
    print('📡 Testing login endpoint...');
    final loginResponse = await dio.post('/api/v1/auth/login', data: {
      'email': 'test@example.com',
      'password': 'password123',
    });
    print('✅ Login test: ${loginResponse.data['user']['name']}');
    
    // Test chat endpoint
    print('📡 Testing chat endpoint...');
    final chatResponse = await dio.post('/api/v1/chat/message', data: {
      'message': 'Hello, how are you?',
      'conversation_id': 'test_conversation',
    });
    print('✅ Chat test: ${chatResponse.data['content']}');
    
    print('🎉 All backend connections successful!');
    
  } catch (e) {
    print('❌ Backend connection failed: $e');
    if (e is DioException) {
      print('   Status: ${e.response?.statusCode}');
      print('   Data: ${e.response?.data}');
    }
  }
}