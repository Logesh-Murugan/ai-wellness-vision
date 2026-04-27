import 'package:flutter/material.dart';

class AppConstants {
  // App Information
  static const String appName = 'AI WellnessVision';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'AI-powered health and wellness analysis platform';
  
  // API Configuration - PostgreSQL Backend
  static const String baseUrl = 'http://localhost:8003';
  static const String websocketUrl = 'ws://localhost:8003/ws';
  
  // Storage Keys
  static const String authTokenKey = 'auth_token';
  static const String userDataKey = 'user_data';
  static const String settingsKey = 'app_settings';
  static const String conversationHistoryKey = 'conversation_history';
  static const String analysisHistoryKey = 'analysis_history';
  
  // Supported Languages
  static const List<Locale> supportedLocales = [
    Locale('en', 'US'), // English
    Locale('hi', 'IN'), // Hindi
    Locale('ta', 'IN'), // Tamil
    Locale('te', 'IN'), // Telugu
    Locale('bn', 'IN'), // Bengali
    Locale('gu', 'IN'), // Gujarati
    Locale('mr', 'IN'), // Marathi
  ];
  
  // Language Names
  static const Map<String, String> languageNames = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'bn': 'বাংলা',
    'gu': 'ગુજરાતી',
    'mr': 'मराठी',
  };
  
  // Analysis Types
  static const List<String> analysisTypes = [
    'skin_condition',
    'eye_health',
    'food_recognition',
    'emotion_detection',
  ];
  
  // Analysis Type Names
  static const Map<String, String> analysisTypeNames = {
    'skin_condition': 'Skin Condition Detection',
    'eye_health': 'Eye Health Assessment',
    'food_recognition': 'Food Recognition',
    'emotion_detection': 'Emotion Detection',
  };
  
  // Chat Modes
  static const List<String> chatModes = [
    'general',
    'symptom_checker',
    'wellness',
    'mental_health',
  ];
  
  // Chat Mode Names
  static const Map<String, String> chatModeNames = {
    'general': 'General Health',
    'symptom_checker': 'Symptom Analysis',
    'wellness': 'Wellness Tips',
    'mental_health': 'Mental Health',
  };
  
  // File Upload Limits
  static const int maxImageSizeMB = 10;
  static const int maxAudioDurationSeconds = 300; // 5 minutes
  static const List<String> supportedImageFormats = ['jpg', 'jpeg', 'png'];
  static const List<String> supportedAudioFormats = ['mp3', 'wav', 'm4a'];
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double borderRadius = 12.0;
  static const double smallBorderRadius = 8.0;
  static const double largeBorderRadius = 20.0;
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
  
  // Network Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Voice Settings
  static const double defaultSpeechRate = 0.5;
  static const double defaultPitch = 1.0;
  static const double defaultVolume = 1.0;
  
  // Health Tips
  static const List<String> healthTips = [
    'Stay hydrated! Aim for 8 glasses of water daily.',
    'Take regular breaks to walk and stretch.',
    'Maintain a consistent sleep schedule.',
    'Include colorful fruits and vegetables in your meals.',
    'Practice mindfulness or meditation for mental well-being.',
    'Get some sunlight exposure for vitamin D.',
    'Stay connected with friends and family.',
  ];
  
  // Emergency Contacts
  static const Map<String, String> emergencyContacts = {
    'emergency': '911',
    'poison_control': '1-800-222-1222',
    'suicide_prevention': '988',
    'crisis_text': 'Text HOME to 741741',
  };
  
  // Medical Disclaimer
  static const String medicalDisclaimer = 
    'This platform provides general health information and is not intended to '
    'replace professional medical advice, diagnosis, or treatment. Always '
    'consult with qualified healthcare providers for medical concerns.';
}