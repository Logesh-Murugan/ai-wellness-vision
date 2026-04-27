import 'package:flutter/foundation.dart';

class AppConfig {
  static const String appName = 'AI Wellness Vision';
  static const String appVersion = '1.0.0';
  
  // API Configuration - Updated for PostgreSQL backend
  static String get baseUrl {
    if (kDebugMode) {
      return 'http://localhost:8003';
    } else {
      return 'https://api.aiwellnessvision.com';
    }
  }
  
  // API Endpoints
  static const String authEndpoint = '/auth';
  static const String userEndpoint = '/users';
  static const String imageAnalysisEndpoint = '/analysis/image';
  static const String chatEndpoint = '/chat';
  static const String voiceEndpoint = '/voice';
  static const String healthDataEndpoint = '/health-data';
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  static const String settingsKey = 'app_settings';
  
  // Feature Flags
  static const bool enableBiometricAuth = true;
  static const bool enablePushNotifications = true;
  static const bool enableAnalytics = true;
  static const bool enableCrashReporting = true;
  
  // Limits
  static const int maxImageSize = 10 * 1024 * 1024; // 10MB
  static const int maxAudioDuration = 300; // 5 minutes
  static const int chatHistoryLimit = 1000;
  static const int analysisHistoryLimit = 500;
}