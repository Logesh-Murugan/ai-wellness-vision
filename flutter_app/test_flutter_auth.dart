import 'package:dio/dio.dart';

void main() async {
  print('🧪 Testing Flutter Authentication Flow');
  print('='*50);
  
  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8003',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  
  // Test 1: Health Check
  print('\n1️⃣ Testing Backend Connection...');
  try {
    final response = await dio.get('/health');
    if (response.statusCode == 200) {
      print('✅ Backend is running');
      print('   Version: ${response.data['version']}');
    } else {
      print('❌ Backend health check failed');
      return;
    }
  } catch (e) {
    print('❌ Cannot connect to backend: $e');
    print('\n💡 Make sure to start the backend first:');
    print('   python working_postgres_server.py');
    return;
  }
  
  // Test 2: Login Test
  print('\n2️⃣ Testing Login...');
  try {
    final response = await dio.post(
      '/auth/login',
      data: {
        'email': 'admin@wellnessvision.ai',
        'password': 'admin123',
      },
    );
    
    if (response.statusCode == 200) {
      print('✅ Login successful');
      print('   Token received: ${response.data['access_token'].toString().substring(0, 20)}...');
    } else {
      print('❌ Login failed: ${response.statusCode}');
    }
  } catch (e) {
    print('❌ Login error: $e');
  }
  
  print('\n' + '='*50);
  print('🎉 Flutter Authentication Setup Complete!');
  print('\n📱 Next steps:');
  print('   1. Make sure backend is running: python working_postgres_server.py');
  print('   2. Run Flutter app: flutter run');
  print('   3. Use demo login or admin@wellnessvision.ai / admin123');
}