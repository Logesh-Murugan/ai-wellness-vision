class ApiConfig {
  // Base URL for main API server
  // For mobile testing, replace 'localhost' with your computer's IP address
  // Example: 'http://192.168.1.100:8000'
  static const String baseUrl = 'http://10.98.177.214:8000';
  
  // Authentication endpoints
  static const String authRegister = '/api/v1/auth/register';
  static const String authLogin = '/api/v1/auth/login';
  static const String authMe = '/api/v1/auth/me';
  static const String authLogout = '/api/v1/auth/logout';
  
  // API Endpoints
  static const String chatMessage = '/api/v1/chat/message';
  static const String chatConversations = '/api/v1/chat/conversations';
  static const String imageAnalysis = '/api/v1/analysis/image';
  static const String imageHistory = '/api/v1/analysis/history';
  static const String voiceTTS = '/api/v1/voice/text-to-speech';
  static const String voiceSTT = '/api/v1/voice/speech-to-text';
  static const String health = '/api/v1/health';
  
  // Request timeout
  static const Duration timeout = Duration(seconds: 30);
  
  // Headers
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Headers with authentication
  static Map<String, String> getAuthHeaders(String token) => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer $token',
  };
}