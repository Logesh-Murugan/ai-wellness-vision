import 'package:dio/dio.dart';
import 'lib/core/config/api_config.dart';

void main() async {
  print('🧪 Testing Flutter-PostgreSQL Integration');
  print('='*50);
  
  final dio = Dio();
  
  // Test 1: Health Check
  print('\n1️⃣ Testing Health Check...');
  try {
    final response = await dio.get('${ApiConfig.baseUrl}${ApiConfig.health}');
    if (response.statusCode == 200) {
      print('✅ Health check passed');
      print('   Version: ${response.data['version']}');
      print('   Database: ${response.data['database']}');
    } else {
      print('❌ Health check failed: ${response.statusCode}');
      return;
    }
  } catch (e) {
    print('❌ Health check error: $e');
    return;
  }
  
  // Test 2: Login
  print('\n2️⃣ Testing Login...');
  String? token;
  try {
    final response = await dio.post(
      '${ApiConfig.baseUrl}${ApiConfig.authLogin}',
      data: {
        'email': 'admin@wellnessvision.ai',
        'password': 'admin123',
      },
    );
    
    if (response.statusCode == 200) {
      token = response.data['access_token'];
      print('✅ Login successful');
      print('   Token: ${token!.substring(0, 20)}...');
    } else {
      print('❌ Login failed: ${response.statusCode}');
      return;
    }
  } catch (e) {
    print('❌ Login error: $e');
    return;
  }
  
  // Test 3: Get User Info
  print('\n3️⃣ Testing User Info...');
  try {
    final response = await dio.get(
      '${ApiConfig.baseUrl}${ApiConfig.authMe}',
      options: Options(
        headers: ApiConfig.getAuthHeaders(token!),
      ),
    );
    
    if (response.statusCode == 200) {
      print('✅ User info retrieved');
      print('   Name: ${response.data['name']}');
      print('   Email: ${response.data['email']}');
      print('   ID: ${response.data['id'].toString().substring(0, 8)}...');
    } else {
      print('❌ User info failed: ${response.statusCode}');
      return;
    }
  } catch (e) {
    print('❌ User info error: $e');
    return;
  }
  
  // Test 4: Send Chat Message
  print('\n4️⃣ Testing Chat...');
  try {
    final response = await dio.post(
      '${ApiConfig.baseUrl}${ApiConfig.chatMessage}',
      data: {
        'message': 'Hello from Flutter!',
        'mode': 'general',
      },
      options: Options(
        headers: ApiConfig.getAuthHeaders(token!),
      ),
    );
    
    if (response.statusCode == 200) {
      print('✅ Chat message sent');
      print('   Response: ${response.data['response'].toString().substring(0, 50)}...');
      print('   Mode: ${response.data['mode']}');
    } else {
      print('❌ Chat failed: ${response.statusCode}');
      return;
    }
  } catch (e) {
    print('❌ Chat error: $e');
    return;
  }
  
  // Test 5: Get Conversations
  print('\n5️⃣ Testing Conversations...');
  try {
    final response = await dio.get(
      '${ApiConfig.baseUrl}${ApiConfig.chatConversations}',
      options: Options(
        headers: ApiConfig.getAuthHeaders(token!),
      ),
    );
    
    if (response.statusCode == 200) {
      final conversations = response.data['conversations'] as List;
      print('✅ Conversations retrieved');
      print('   Count: ${conversations.length}');
      if (conversations.isNotEmpty) {
        print('   First: ${conversations[0]['title']}');
      }
    } else {
      print('❌ Conversations failed: ${response.statusCode}');
      return;
    }
  } catch (e) {
    print('❌ Conversations error: $e');
    return;
  }
  
  print('\n' + '='*50);
  print('🎉 ALL FLUTTER TESTS PASSED!');
  print('✅ Your Flutter app is ready to use PostgreSQL backend!');
  print('\n📱 Next steps:');
  print('   1. Run: flutter run');
  print('   2. Test login with: admin@wellnessvision.ai / admin123');
  print('   3. Try the chat functionality');
  print('   4. Explore all features!');
}