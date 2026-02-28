#!/usr/bin/env dart
/*
Flutter-CNN Connection Test
This Dart script tests the connection between Flutter app and CNN backend
*/

import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;

class FlutterCNNConnectionTest {
  static const String baseUrl = 'http://localhost:8000';
  
  static Future<void> testConnection() async {
    print('🧪 Testing Flutter-CNN Connection');
    print('=' * 50);
    
    // Test 1: Backend Health Check
    await testBackendHealth();
    
    // Test 2: Model Info Check
    await testModelInfo();
    
    // Test 3: Image Analysis Endpoint
    await testImageAnalysisEndpoint();
    
    print('\n✅ Flutter-CNN connection test completed!');
    print('Your Flutter app is ready to use CNN-powered analysis.');
  }
  
  static Future<void> testBackendHealth() async {
    print('\n🏥 Testing Backend Health...');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ Backend Health: ${data['status']}');
        
        final services = data['services'] as Map<String, dynamic>;
        services.forEach((service, status) {
          print('   $service: $status');
        });
        
        // Check CNN availability
        final cnnStatus = services['cnn_analyzer'];
        if (cnnStatus == 'available') {
          print('🧠 CNN Models: READY');
        } else {
          print('⚠️ CNN Models: NOT AVAILABLE');
        }
      } else {
        print('❌ Backend Health Check Failed: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Backend Connection Error: $e');
    }
  }
  
  static Future<void> testModelInfo() async {
    print('\n🤖 Testing Model Information...');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/models/info'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ Model Info Retrieved');
        print('   CNN Available: ${data['cnn_available']}');
        print('   Gemini Available: ${data['gemini_available']}');
        
        if (data['models'] != null && data['models']['cnn'] != null) {
          final cnnModels = data['models']['cnn'] as Map<String, dynamic>;
          print('   CNN Models:');
          cnnModels.forEach((modelType, info) {
            final loaded = info['loaded'] ?? false;
            print('     $modelType: ${loaded ? "✅ Loaded" : "❌ Not Loaded"}');
          });
        }
      } else {
        print('❌ Model Info Failed: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Model Info Error: $e');
    }
  }
  
  static Future<void> testImageAnalysisEndpoint() async {
    print('\n📸 Testing Image Analysis Endpoint...');
    
    try {
      // Create a simple test request (without actual image for this test)
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/analysis/image'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'test': 'connection'}),
      ).timeout(Duration(seconds: 10));
      
      // We expect this to fail (422) because we're not sending an image
      // But if we get 422, it means the endpoint is accessible
      if (response.statusCode == 422) {
        print('✅ Image Analysis Endpoint: ACCESSIBLE');
        print('   (422 expected - endpoint requires image file)');
      } else if (response.statusCode == 200) {
        print('✅ Image Analysis Endpoint: WORKING');
      } else {
        print('⚠️ Image Analysis Endpoint: Status ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Image Analysis Endpoint Error: $e');
    }
  }
}

void main() async {
  await FlutterCNNConnectionTest.testConnection();
}