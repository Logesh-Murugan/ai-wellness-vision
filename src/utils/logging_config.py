# logging_config.py - Centralized logging configuration
import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from src.config import LoggingConfig, AppConfig, Environment

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry)

def setup_logging() -> None:
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    LoggingConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LoggingConfig.LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LoggingConfig.LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LoggingConfig.LOG_FILE,
        maxBytes=LoggingConfig.MAX_BYTES,
        backupCount=LoggingConfig.BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, LoggingConfig.LEVEL))
    
    # Choose formatter based on environment
    if LoggingConfig.USE_JSON_LOGGING or AppConfig.ENVIRONMENT == Environment.PRODUCTION:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            LoggingConfig.FORMAT,
            datefmt=LoggingConfig.DATE_FORMAT
        )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_library_loggers()
    
    logging.info("Logging configuration completed")

def configure_library_loggers() -> None:
    """Configure logging levels for third-party libraries"""
    
    # Reduce noise from third-party libraries
    library_loggers = {
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'transformers': logging.WARNING,
        'torch': logging.WARNING,
        'tensorflow': logging.WARNING,
        'PIL': logging.WARNING,
        'matplotlib': logging.WARNING,
    }
    
    for logger_name, level in library_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context information"""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message and add extra context"""
        return msg, {**kwargs, **self.extra}

def get_contextual_logger(name: str, **context) -> LoggerAdapter:
    """Get a logger with additional context information"""
    logger = get_logger(name)
    return LoggerAdapter(logger, context)

# Performance logging decorator
def log_performance(logger: logging.Logger = None):
    """Decorator to log function execution time"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger is None:
                log = get_logger(func.__module__)
            else:
                log = logger
            
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                log.info(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                log.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

class StructuredLogger:
    """Enhanced structured logger with additional features"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context = {}
    
    def set_context(self, **context) -> None:
        """Set persistent context for all log messages"""
        self.context.update(context)
    
    def clear_context(self) -> None:
        """Clear persistent context"""
        self.context.clear()
    
    def _log_with_context(self, level: int, message: str, **extra) -> None:
        """Log message with context"""
        combined_extra = {**self.context, **extra}
        self.logger.log(level, message, extra=combined_extra)
    
    def debug(self, message: str, **extra) -> None:
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **extra)
    
    def info(self, message: str, **extra) -> None:
        """Log info message"""
        self._log_with_context(logging.INFO, message, **extra)
    
    def warning(self, message: str, **extra) -> None:
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **extra)
    
    def error(self, message: str, **extra) -> None:
        """Log error message"""
        self._log_with_context(logging.ERROR, message, **extra)
    
    def critical(self, message: str, **extra) -> None:
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **extra)
    
    def log_exception(self, message: str, exception: Exception, **extra) -> None:
        """Log exception with full traceback"""
        self.logger.exception(message, extra={**self.context, **extra, 'exception_type': type(exception).__name__})
    
    def log_performance_metric(self, operation: str, duration: float, **metrics) -> None:
        """Log performance metrics"""
        self.info(f"Performance: {operation}", 
                 duration_seconds=duration, 
                 operation=operation,
                 **metrics)
    
    def log_user_action(self, action: str, user_id: str = None, **details) -> None:
        """Log user actions for audit trail"""
        self.info(f"User action: {action}",
                 action=action,
                 user_id=user_id or self.context.get('user_id'),
                 **details)
    
    def log_security_event(self, event: str, severity: str = "medium", **details) -> None:
        """Log security-related events"""
        log_level = logging.WARNING if severity in ["medium", "high"] else logging.INFO
        self._log_with_context(log_level, f"Security event: {event}",
                              security_event=True,
                              event_type=event,
                              severity=severity,
                              **details)

class LogAggregator:
    """Aggregates and analyzes log data"""
    
    def __init__(self):
        self.log_buffer = []
        self.max_buffer_size = 10000
        self.error_patterns = {}
        self.performance_metrics = {}
    
    def add_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """Add log entry to buffer"""
        self.log_buffer.append(log_entry)
        
        # Maintain buffer size
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
        
        # Analyze entry
        self._analyze_log_entry(log_entry)
    
    def _analyze_log_entry(self, entry: Dict[str, Any]) -> None:
        """Analyze log entry for patterns"""
        level = entry.get('level', '')
        message = entry.get('message', '')
        
        # Track error patterns
        if level in ['ERROR', 'CRITICAL']:
            pattern_key = f"{entry.get('module', 'unknown')}:{entry.get('function', 'unknown')}"
            if pattern_key not in self.error_patterns:
                self.error_patterns[pattern_key] = {
                    'count': 0,
                    'first_seen': entry.get('timestamp'),
                    'last_seen': entry.get('timestamp'),
                    'messages': []
                }
            
            self.error_patterns[pattern_key]['count'] += 1
            self.error_patterns[pattern_key]['last_seen'] = entry.get('timestamp')
            
            # Keep sample messages
            if len(self.error_patterns[pattern_key]['messages']) < 5:
                self.error_patterns[pattern_key]['messages'].append(message)
        
        # Track performance metrics
        if 'duration_seconds' in entry:
            operation = entry.get('operation', 'unknown')
            duration = entry.get('duration_seconds', 0)
            
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = {
                    'count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'recent_durations': []
                }
            
            metrics = self.performance_metrics[operation]
            metrics['count'] += 1
            metrics['total_duration'] += duration
            metrics['min_duration'] = min(metrics['min_duration'], duration)
            metrics['max_duration'] = max(metrics['max_duration'], duration)
            
            # Keep recent durations for trend analysis
            metrics['recent_durations'].append(duration)
            if len(metrics['recent_durations']) > 100:
                metrics['recent_durations'] = metrics['recent_durations'][-100:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error patterns"""
        if not self.error_patterns:
            return {"total_errors": 0, "patterns": []}
        
        # Sort patterns by frequency
        sorted_patterns = sorted(
            self.error_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return {
            "total_errors": sum(p['count'] for p in self.error_patterns.values()),
            "unique_patterns": len(self.error_patterns),
            "top_patterns": [
                {
                    "pattern": pattern,
                    "count": data['count'],
                    "first_seen": data['first_seen'],
                    "last_seen": data['last_seen'],
                    "sample_messages": data['messages'][:3]
                }
                for pattern, data in sorted_patterns[:10]
            ]
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        if not self.performance_metrics:
            return {"operations": []}
        
        summary = []
        for operation, metrics in self.performance_metrics.items():
            avg_duration = metrics['total_duration'] / metrics['count']
            
            # Calculate recent average (last 20 calls)
            recent_durations = metrics['recent_durations'][-20:]
            recent_avg = sum(recent_durations) / len(recent_durations) if recent_durations else 0
            
            summary.append({
                "operation": operation,
                "call_count": metrics['count'],
                "avg_duration": avg_duration,
                "min_duration": metrics['min_duration'],
                "max_duration": metrics['max_duration'],
                "recent_avg_duration": recent_avg,
                "performance_trend": "improving" if recent_avg < avg_duration else "degrading" if recent_avg > avg_duration else "stable"
            })
        
        # Sort by call count
        summary.sort(key=lambda x: x['call_count'], reverse=True)
        
        return {"operations": summary}
    
    def export_analysis(self, output_file: Path) -> None:
        """Export log analysis to file"""
        analysis = {
            "generated_at": datetime.utcnow().isoformat(),
            "log_entries_analyzed": len(self.log_buffer),
            "error_analysis": self.get_error_summary(),
            "performance_analysis": self.get_performance_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dumps(analysis, f, indent=2, default=str)

# Global instances
log_aggregator = LogAggregator()

def get_structured_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    return StructuredLogger(name)

def get_log_aggregator() -> LogAggregator:
    """Get log aggregator instance"""
    return log_aggregator

# Enhanced logging handler that feeds the aggregator
class AggregatingHandler(logging.Handler):
    """Logging handler that feeds log aggregator"""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to aggregator"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra fields
            for attr in ['user_id', 'session_id', 'request_id', 'duration_seconds', 'operation']:
                if hasattr(record, attr):
                    log_entry[attr] = getattr(record, attr)
            
            log_aggregator.add_log_entry(log_entry)
            
        except Exception:
            self.handleError(record)

def setup_enhanced_logging() -> None:
    """Setup enhanced logging with aggregation"""
    # Setup basic logging first
    setup_logging()
    
    # Add aggregating handler
    root_logger = logging.getLogger()
    aggregating_handler = AggregatingHandler()
    aggregating_handler.setLevel(logging.INFO)  # Only aggregate INFO and above
    root_logger.addHandler(aggregating_handler)
    
    logging.info("Enhanced logging with aggregation configured")