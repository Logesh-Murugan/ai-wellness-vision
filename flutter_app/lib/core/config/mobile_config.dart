class MobileConfig {
  // Network configuration for mobile deployment
  static const String computerIP = '192.168.1.100'; // Replace with your computer's IP
  static const String port = '8000';
  static const String baseUrl = 'http://$computerIP:$port';
  
  // API endpoints
  static const String visualQA = '$baseUrl/api/v1/analysis/visual-qa';
  static const String imageAnalysis = '$baseUrl/api/v1/analysis/image';
  static const String chatMessage = '$baseUrl/api/v1/chat/send';
  static const String health = '$baseUrl/health';
  
  // Network settings
  static const Duration timeout = Duration(seconds: 30);
  static const int maxRetries = 3;
  
  // Check if running on mobile
  static bool get isMobile => 
      const bool.fromEnvironment('dart.library.io') && 
      !const bool.fromEnvironment('dart.library.html');
  
  // Get appropriate base URL based on platform
  static String getBaseUrl() {
    if (isMobile) {
      return baseUrl; // Use computer IP for mobile
    } else {
      return 'http://localhost:8000'; // Use localhost for web
    }
  }
}