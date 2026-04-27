enum LogLevel {
  debug,
  info,
  warning,
  error,
}

class AppLogger {
  static const bool _isDebugMode = true; // Set to false in production
  
  static void debug(String message, [Object? error, StackTrace? stackTrace]) {
    _log(LogLevel.debug, message, error, stackTrace);
  }
  
  static void info(String message, [Object? error, StackTrace? stackTrace]) {
    _log(LogLevel.info, message, error, stackTrace);
  }
  
  static void warning(String message, [Object? error, StackTrace? stackTrace]) {
    _log(LogLevel.warning, message, error, stackTrace);
  }
  
  static void error(String message, [Object? error, StackTrace? stackTrace]) {
    _log(LogLevel.error, message, error, stackTrace);
  }
  
  static void _log(LogLevel level, String message, Object? error, StackTrace? stackTrace) {
    if (!_isDebugMode && level == LogLevel.debug) return;
    
    final timestamp = DateTime.now().toIso8601String();
    final levelString = level.name.toUpperCase();
    
    print('[$timestamp] [$levelString] $message');
    
    if (error != null) {
      print('Error: $error');
    }
    
    if (stackTrace != null) {
      print('Stack trace: $stackTrace');
    }
  }
}