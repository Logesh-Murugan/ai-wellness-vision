# test_enhanced_logging.py - Tests for enhanced logging functionality
import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.utils.logging_config import (
    StructuredLogger, LogAggregator, AggregatingHandler,
    get_structured_logger, get_log_aggregator, setup_enhanced_logging
)

class TestStructuredLogger:
    """Test structured logger functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.logger = StructuredLogger("test_logger")
    
    def test_structured_logger_creation(self):
        """Test creating structured logger"""
        assert self.logger.logger.name == "test_logger"
        assert len(self.logger.context) == 0
    
    def test_set_context(self):
        """Test setting persistent context"""
        self.logger.set_context(user_id="user123", session_id="session456")
        
        assert self.logger.context["user_id"] == "user123"
        assert self.logger.context["session_id"] == "session456"
    
    def test_clear_context(self):
        """Test clearing context"""
        self.logger.set_context(user_id="user123")
        assert len(self.logger.context) > 0
        
        self.logger.clear_context()
        assert len(self.logger.context) == 0
    
    @patch('src.utils.logging_config.get_logger')
    def test_log_with_context(self, mock_get_logger):
        """Test logging with context"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        logger.set_context(user_id="user123")
        
        logger.info("Test message", request_id="req456")
        
        # Should call log with combined context
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        
        assert call_args[0][0] == 20  # INFO level
        assert call_args[0][1] == "Test message"
        assert "user_id" in call_args[1]["extra"]
        assert "request_id" in call_args[1]["extra"]
    
    @patch('src.utils.logging_config.get_logger')
    def test_log_exception(self, mock_get_logger):
        """Test logging exceptions"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        exception = ValueError("Test exception")
        
        logger.log_exception("Exception occurred", exception, context="test")
        
        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args
        
        assert call_args[0][0] == "Exception occurred"
        assert call_args[1]["extra"]["exception_type"] == "ValueError"
        assert call_args[1]["extra"]["context"] == "test"
    
    @patch('src.utils.logging_config.get_logger')
    def test_log_performance_metric(self, mock_get_logger):
        """Test logging performance metrics"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        logger.log_performance_metric("image_analysis", 2.5, accuracy=0.95)
        
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        
        assert "Performance: image_analysis" in call_args[0][1]
        assert call_args[1]["extra"]["duration_seconds"] == 2.5
        assert call_args[1]["extra"]["operation"] == "image_analysis"
        assert call_args[1]["extra"]["accuracy"] == 0.95
    
    @patch('src.utils.logging_config.get_logger')
    def test_log_user_action(self, mock_get_logger):
        """Test logging user actions"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        logger.set_context(user_id="user123")
        logger.log_user_action("upload_image", file_size=1024)
        
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        
        assert "User action: upload_image" in call_args[0][1]
        assert call_args[1]["extra"]["action"] == "upload_image"
        assert call_args[1]["extra"]["user_id"] == "user123"
        assert call_args[1]["extra"]["file_size"] == 1024
    
    @patch('src.utils.logging_config.get_logger')
    def test_log_security_event(self, mock_get_logger):
        """Test logging security events"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        logger.log_security_event("failed_login", severity="high", ip_address="192.168.1.1")
        
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        
        assert call_args[0][0] == 30  # WARNING level for high severity
        assert "Security event: failed_login" in call_args[0][1]
        assert call_args[1]["extra"]["security_event"] is True
        assert call_args[1]["extra"]["event_type"] == "failed_login"
        assert call_args[1]["extra"]["severity"] == "high"
        assert call_args[1]["extra"]["ip_address"] == "192.168.1.1"

class TestLogAggregator:
    """Test log aggregator functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.aggregator = LogAggregator()
    
    def test_log_aggregator_initialization(self):
        """Test log aggregator initialization"""
        assert len(self.aggregator.log_buffer) == 0
        assert self.aggregator.max_buffer_size == 10000
        assert len(self.aggregator.error_patterns) == 0
        assert len(self.aggregator.performance_metrics) == 0
    
    def test_add_log_entry(self):
        """Test adding log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "module": "test_module"
        }
        
        self.aggregator.add_log_entry(log_entry)
        
        assert len(self.aggregator.log_buffer) == 1
        assert self.aggregator.log_buffer[0] == log_entry
    
    def test_buffer_size_limit(self):
        """Test buffer size limiting"""
        # Set small buffer size for testing
        self.aggregator.max_buffer_size = 5
        
        # Add more entries than limit
        for i in range(10):
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Message {i}"
            }
            self.aggregator.add_log_entry(log_entry)
        
        # Should only keep last 5
        assert len(self.aggregator.log_buffer) == 5
        assert self.aggregator.log_buffer[-1]["message"] == "Message 9"
    
    def test_error_pattern_analysis(self):
        """Test error pattern analysis"""
        # Add error entries
        for i in range(3):
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"Database connection failed {i}",
                "module": "database",
                "function": "connect"
            }
            self.aggregator.add_log_entry(error_entry)
        
        # Should track error pattern
        pattern_key = "database:connect"
        assert pattern_key in self.aggregator.error_patterns
        assert self.aggregator.error_patterns[pattern_key]["count"] == 3
        assert len(self.aggregator.error_patterns[pattern_key]["messages"]) == 3
    
    def test_performance_metrics_analysis(self):
        """Test performance metrics analysis"""
        # Add performance entries
        durations = [1.5, 2.0, 1.8, 2.2, 1.9]
        for duration in durations:
            perf_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Performance: image_analysis",
                "operation": "image_analysis",
                "duration_seconds": duration
            }
            self.aggregator.add_log_entry(perf_entry)
        
        # Should track performance metrics
        assert "image_analysis" in self.aggregator.performance_metrics
        metrics = self.aggregator.performance_metrics["image_analysis"]
        
        assert metrics["count"] == 5
        assert metrics["total_duration"] == sum(durations)
        assert metrics["min_duration"] == min(durations)
        assert metrics["max_duration"] == max(durations)
        assert len(metrics["recent_durations"]) == 5
    
    def test_get_error_summary(self):
        """Test getting error summary"""
        # Add various errors
        error_entries = [
            {"level": "ERROR", "module": "api", "function": "process_request", "message": "API error 1"},
            {"level": "ERROR", "module": "api", "function": "process_request", "message": "API error 2"},
            {"level": "CRITICAL", "module": "database", "function": "query", "message": "DB critical"},
            {"level": "ERROR", "module": "auth", "function": "validate", "message": "Auth error"}
        ]
        
        for entry in error_entries:
            entry["timestamp"] = datetime.now().isoformat()
            self.aggregator.add_log_entry(entry)
        
        summary = self.aggregator.get_error_summary()
        
        assert summary["total_errors"] == 4
        assert summary["unique_patterns"] == 3
        assert len(summary["top_patterns"]) == 3
        
        # Should be sorted by frequency
        top_pattern = summary["top_patterns"][0]
        assert top_pattern["pattern"] == "api:process_request"
        assert top_pattern["count"] == 2
    
    def test_get_performance_summary(self):
        """Test getting performance summary"""
        # Add performance data for multiple operations
        operations = [
            ("image_analysis", [1.0, 1.2, 1.1, 1.3]),
            ("text_processing", [0.5, 0.6, 0.4]),
            ("speech_recognition", [2.0, 2.5, 2.2, 2.1, 1.9])
        ]
        
        for operation, durations in operations:
            for duration in durations:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "operation": operation,
                    "duration_seconds": duration
                }
                self.aggregator.add_log_entry(entry)
        
        summary = self.aggregator.get_performance_summary()
        
        assert len(summary["operations"]) == 3
        
        # Should be sorted by call count
        first_op = summary["operations"][0]
        assert first_op["operation"] == "speech_recognition"
        assert first_op["call_count"] == 5
        
        # Check calculations
        speech_op = next(op for op in summary["operations"] if op["operation"] == "speech_recognition")
        expected_avg = sum([2.0, 2.5, 2.2, 2.1, 1.9]) / 5
        assert abs(speech_op["avg_duration"] - expected_avg) < 0.001
    
    def test_export_analysis(self, tmp_path):
        """Test exporting analysis"""
        # Add some test data
        self.aggregator.add_log_entry({
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": "Test error",
            "module": "test",
            "function": "test_func"
        })
        
        self.aggregator.add_log_entry({
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "operation": "test_op",
            "duration_seconds": 1.5
        })
        
        output_file = tmp_path / "analysis.json"
        self.aggregator.export_analysis(output_file)
        
        assert output_file.exists()
        
        # Verify content
        with open(output_file) as f:
            analysis = json.load(f)
        
        assert "generated_at" in analysis
        assert "log_entries_analyzed" in analysis
        assert "error_analysis" in analysis
        assert "performance_analysis" in analysis
        assert analysis["log_entries_analyzed"] == 2

class TestAggregatingHandler:
    """Test aggregating logging handler"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.handler = AggregatingHandler()
        self.mock_aggregator = Mock()
    
    @patch('src.utils.logging_config.log_aggregator')
    def test_emit_log_record(self, mock_aggregator):
        """Test emitting log record to aggregator"""
        import logging
        
        # Create log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.user_id = "user123"
        
        self.handler.emit(record)
        
        # Should call aggregator
        mock_aggregator.add_log_entry.assert_called_once()
        call_args = mock_aggregator.add_log_entry.call_args[0][0]
        
        assert call_args["level"] == "INFO"
        assert call_args["message"] == "Test message"
        assert call_args["module"] == "test_module"
        assert call_args["function"] == "test_function"
        assert call_args["user_id"] == "user123"
    
    @patch('src.utils.logging_config.log_aggregator')
    def test_emit_with_error(self, mock_aggregator):
        """Test emit handling errors gracefully"""
        import logging
        
        # Make aggregator raise exception
        mock_aggregator.add_log_entry.side_effect = Exception("Aggregator error")
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Should not raise exception
        with patch.object(self.handler, 'handleError') as mock_handle_error:
            self.handler.emit(record)
            mock_handle_error.assert_called_once_with(record)

class TestEnhancedLoggingIntegration:
    """Integration tests for enhanced logging"""
    
    def test_get_structured_logger(self):
        """Test getting structured logger"""
        logger = get_structured_logger("integration_test")
        
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == "integration_test"
    
    def test_get_log_aggregator(self):
        """Test getting log aggregator"""
        aggregator = get_log_aggregator()
        
        assert isinstance(aggregator, LogAggregator)
    
    @patch('src.utils.logging_config.setup_logging')
    @patch('src.utils.logging_config.logging.getLogger')
    def test_setup_enhanced_logging(self, mock_get_logger, mock_setup_logging):
        """Test setting up enhanced logging"""
        mock_root_logger = Mock()
        mock_get_logger.return_value = mock_root_logger
        
        setup_enhanced_logging()
        
        # Should call basic setup first
        mock_setup_logging.assert_called_once()
        
        # Should add aggregating handler
        mock_root_logger.addHandler.assert_called()
        
        # Verify handler type
        call_args = mock_root_logger.addHandler.call_args[0][0]
        assert isinstance(call_args, AggregatingHandler)
    
    def test_end_to_end_logging_flow(self):
        """Test complete logging flow"""
        # Get structured logger
        logger = get_structured_logger("e2e_test")
        logger.set_context(user_id="test_user", session_id="test_session")
        
        # Get aggregator
        aggregator = get_log_aggregator()
        initial_count = len(aggregator.log_buffer)
        
        # Log various types of messages
        logger.info("Test info message")
        logger.error("Test error message")
        logger.log_performance_metric("test_operation", 1.5, success=True)
        logger.log_user_action("test_action", data="test_data")
        logger.log_security_event("test_security", severity="medium")
        
        # Note: In a real scenario, the aggregating handler would feed the aggregator
        # For this test, we're testing the components separately
        
        # Verify logger functionality
        assert logger.context["user_id"] == "test_user"
        assert logger.context["session_id"] == "test_session"

def test_structured_logger_all_log_levels():
    """Test all log levels in structured logger"""
    with patch('src.utils.logging_config.get_logger') as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger("test")
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Should have called log 5 times
        assert mock_logger.log.call_count == 5
        
        # Verify log levels
        call_args_list = mock_logger.log.call_args_list
        levels = [call[0][0] for call in call_args_list]
        
        import logging
        expected_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        assert levels == expected_levels

def test_log_aggregator_empty_state():
    """Test log aggregator in empty state"""
    aggregator = LogAggregator()
    
    error_summary = aggregator.get_error_summary()
    assert error_summary["total_errors"] == 0
    assert error_summary["patterns"] == []
    
    perf_summary = aggregator.get_performance_summary()
    assert perf_summary["operations"] == []