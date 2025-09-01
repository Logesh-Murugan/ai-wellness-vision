# test_model_optimization.py - Tests for model optimization functionality
import pytest
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.services.model_optimization_service import (
    ModelOptimizationService, TensorFlowLiteConverter, ONNXConverter, ModelCacheManager,
    OptimizationConfig, OptimizationResult, OptimizationTarget, ModelFormat
)

class TestOptimizationConfig:
    """Test optimization configuration"""
    
    def test_optimization_config_creation(self):
        """Test creating optimization configuration"""
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE,
            quantization=True,
            pruning=False,
            max_model_size_mb=10.0
        )
        
        assert config.target_platform == OptimizationTarget.MOBILE
        assert config.target_format == ModelFormat.TFLITE
        assert config.quantization
        assert not config.pruning
        assert config.max_model_size_mb == 10.0
    
    def test_optimization_config_defaults(self):
        """Test optimization configuration defaults"""
        config = OptimizationConfig(
            target_platform=OptimizationTarget.WEB,
            target_format=ModelFormat.ONNX
        )
        
        assert config.quantization  # Default True
        assert not config.pruning  # Default False
        assert config.compression_ratio == 0.5
        assert config.accuracy_threshold == 0.95

class TestTensorFlowLiteConverter:
    """Test TensorFlow Lite conversion functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.converter = TensorFlowLiteConverter()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_supported_formats(self):
        """Test supported input formats"""
        assert ModelFormat.TENSORFLOW in self.converter.supported_input_formats
        assert ModelFormat.PYTORCH in self.converter.supported_input_formats
    
    def test_convert_to_tflite_mock(self):
        """Test TFLite conversion with mock model"""
        # Create mock input model
        input_model = self.temp_dir / "test_model.pb"
        input_model.write_bytes(b"0" * (10 * 1024 * 1024))  # 10MB mock model
        
        output_path = self.temp_dir / "optimized.tflite"
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE,
            quantization=True
        )
        
        result = self.converter.convert_to_tflite(input_model, output_path, config)
        
        # Should succeed with mock implementation
        assert result.success
        assert result.original_size_mb == 10.0
        assert result.optimized_size_mb < result.original_size_mb
        assert result.format == ModelFormat.TFLITE
        assert output_path.exists()
    
    def test_convert_to_tflite_quantization_effect(self):
        """Test that quantization affects compression"""
        input_model = self.temp_dir / "test_model.pb"
        input_model.write_bytes(b"0" * (10 * 1024 * 1024))
        
        # Test with quantization
        config_quantized = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE,
            quantization=True
        )
        result_quantized = self.converter.convert_to_tflite(
            input_model, self.temp_dir / "quantized.tflite", config_quantized
        )
        
        # Test without quantization
        config_no_quant = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE,
            quantization=False
        )
        result_no_quant = self.converter.convert_to_tflite(
            input_model, self.temp_dir / "no_quant.tflite", config_no_quant
        )
        
        # Quantized should be smaller
        assert result_quantized.optimized_size_mb < result_no_quant.optimized_size_mb
    
    def test_validate_tflite_model(self):
        """Test TFLite model validation"""
        # Create mock TFLite model
        tflite_model = self.temp_dir / "test.tflite"
        tflite_model.write_bytes(b"0" * (5 * 1024 * 1024))
        
        validation = self.converter.validate_tflite_model(tflite_model)
        
        assert validation['valid']
        assert 'input_shape' in validation
        assert 'output_shape' in validation
        assert validation['model_size_mb'] == 5.0

class TestONNXConverter:
    """Test ONNX conversion functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.converter = ONNXConverter()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_supported_formats(self):
        """Test supported input formats"""
        assert ModelFormat.PYTORCH in self.converter.supported_input_formats
        assert ModelFormat.TENSORFLOW in self.converter.supported_input_formats
    
    def test_convert_to_onnx_mock(self):
        """Test ONNX conversion with mock model"""
        # Create mock input model
        input_model = self.temp_dir / "test_model.pth"
        input_model.write_bytes(b"0" * (15 * 1024 * 1024))  # 15MB mock model
        
        output_path = self.temp_dir / "optimized.onnx"
        config = OptimizationConfig(
            target_platform=OptimizationTarget.WEB,
            target_format=ModelFormat.ONNX,
            quantization=True
        )
        
        result = self.converter.convert_to_onnx(input_model, output_path, config)
        
        assert result.success
        assert result.original_size_mb == 15.0
        assert result.optimized_size_mb < result.original_size_mb
        assert result.format == ModelFormat.ONNX
        assert output_path.exists()
    
    def test_optimize_onnx_model(self):
        """Test ONNX model optimization"""
        # Create mock ONNX model
        onnx_model = self.temp_dir / "test.onnx"
        onnx_model.write_bytes(b"0" * (20 * 1024 * 1024))
        
        output_path = self.temp_dir / "optimized.onnx"
        config = OptimizationConfig(
            target_platform=OptimizationTarget.CLOUD,
            target_format=ModelFormat.ONNX
        )
        
        result = self.converter.optimize_onnx_model(onnx_model, output_path, config)
        
        assert result.success
        assert result.compression_ratio < 1.0
        assert 'optimization_passes' in result.metadata

class TestModelCacheManager:
    """Test model caching functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_manager = ModelCacheManager(self.temp_dir / "cache")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_cache_index_creation(self):
        """Test cache index creation"""
        assert self.cache_manager.cache_dir.exists()
        assert 'models' in self.cache_manager.cache_index
        assert 'total_size_mb' in self.cache_manager.cache_index
    
    def test_cache_model(self):
        """Test caching a model"""
        # Create mock model
        model_file = self.temp_dir / "test_model.pth"
        model_file.write_bytes(b"0" * (5 * 1024 * 1024))  # 5MB
        
        success = self.cache_manager.cache_model(
            "test_model", 
            model_file,
            {"format": "pytorch", "version": "1.0"}
        )
        
        assert success
        assert "test_model" in self.cache_manager.cache_index['models']
        
        cached_path = self.cache_manager.get_cached_model_path("test_model")
        assert cached_path is not None
        assert cached_path.exists()
    
    def test_cache_size_limit(self):
        """Test cache size limiting"""
        # Set small cache limit
        self.cache_manager.max_cache_size_gb = 0.01  # 10MB
        
        # Create models that exceed limit
        for i in range(3):
            model_file = self.temp_dir / f"model_{i}.pth"
            model_file.write_bytes(b"0" * (5 * 1024 * 1024))  # 5MB each
            
            self.cache_manager.cache_model(f"model_{i}", model_file)
        
        # Should have removed older models
        assert len(self.cache_manager.cache_index['models']) <= 2
    
    def test_lazy_loading(self):
        """Test lazy model loading"""
        load_count = 0
        
        def mock_loader():
            nonlocal load_count
            load_count += 1
            return f"model_instance_{load_count}"
        
        # First load
        model1 = self.cache_manager.lazy_load_model("test_model", mock_loader)
        assert model1 == "model_instance_1"
        assert load_count == 1
        
        # Second access should return cached
        model2 = self.cache_manager.lazy_load_model("test_model", mock_loader)
        assert model2 == "model_instance_1"
        assert load_count == 1  # Should not increment
    
    def test_memory_limit(self):
        """Test memory limit for loaded models"""
        self.cache_manager.max_loaded_models = 2
        
        def mock_loader(name):
            return f"model_{name}"
        
        # Load models up to limit
        for i in range(3):
            self.cache_manager.lazy_load_model(f"model_{i}", mock_loader, f"model_{i}")
        
        # Should only keep 2 models in memory
        assert len(self.cache_manager.loaded_models) == 2
    
    def test_cache_stats(self):
        """Test cache statistics"""
        # Add some cached models
        for i in range(2):
            model_file = self.temp_dir / f"model_{i}.pth"
            model_file.write_bytes(b"0" * (3 * 1024 * 1024))
            self.cache_manager.cache_model(f"model_{i}", model_file)
        
        stats = self.cache_manager.get_cache_stats()
        
        assert stats['total_cached_models'] == 2
        assert stats['total_cache_size_mb'] > 0
        assert 'cache_directory' in stats
        assert 'most_accessed_models' in stats
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality"""
        # Create old cached model
        model_file = self.temp_dir / "old_model.pth"
        model_file.write_bytes(b"0" * (1024 * 1024))
        
        self.cache_manager.cache_model("old_model", model_file)
        
        # Manually set old access time
        import time
        old_time = time.time() - (40 * 24 * 3600)  # 40 days ago
        self.cache_manager.cache_index['models']['old_model']['last_accessed'] = old_time
        
        initial_count = len(self.cache_manager.cache_index['models'])
        self.cache_manager.cleanup_cache(max_age_days=30)
        
        # Should have removed old model
        assert len(self.cache_manager.cache_index['models']) < initial_count

class TestModelOptimizationService:
    """Test main model optimization service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ModelOptimizationService(self.temp_dir / "cache")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_optimize_model_tflite(self):
        """Test model optimization to TFLite"""
        # Create mock model
        model_file = self.temp_dir / "test_model.pb"
        model_file.write_bytes(b"0" * (10 * 1024 * 1024))
        
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE,
            quantization=True
        )
        
        result = self.service.optimize_model(model_file, config, self.temp_dir / "output")
        
        assert result.success
        assert result.format == ModelFormat.TFLITE
        assert result.output_path.exists()
    
    def test_optimize_model_onnx(self):
        """Test model optimization to ONNX"""
        # Create mock model
        model_file = self.temp_dir / "test_model.pth"
        model_file.write_bytes(b"0" * (15 * 1024 * 1024))
        
        config = OptimizationConfig(
            target_platform=OptimizationTarget.WEB,
            target_format=ModelFormat.ONNX,
            quantization=True
        )
        
        result = self.service.optimize_model(model_file, config, self.temp_dir / "output")
        
        assert result.success
        assert result.format == ModelFormat.ONNX
        assert result.output_path.exists()
    
    def test_batch_optimization(self):
        """Test batch model optimization"""
        # Create multiple mock models
        model_files = []
        for i in range(2):
            model_file = self.temp_dir / f"model_{i}.pth"
            model_file.write_bytes(b"0" * (5 * 1024 * 1024))
            model_files.append(model_file)
        
        configs = [
            OptimizationConfig(
                target_platform=OptimizationTarget.MOBILE,
                target_format=ModelFormat.TFLITE
            ),
            OptimizationConfig(
                target_platform=OptimizationTarget.WEB,
                target_format=ModelFormat.ONNX
            )
        ]
        
        results = self.service.batch_optimize_models(
            model_files, configs, self.temp_dir / "output"
        )
        
        # Should have 4 results (2 models × 2 configs)
        assert len(results) == 4
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0
    
    def test_optimization_recommendations(self):
        """Test getting optimization recommendations"""
        # Create mock model
        model_file = self.temp_dir / "large_model.pth"
        model_file.write_bytes(b"0" * (50 * 1024 * 1024))  # 50MB
        
        recommendations = self.service.get_optimization_recommendations(
            model_file, OptimizationTarget.MOBILE
        )
        
        assert len(recommendations) > 0
        
        # Should recommend aggressive optimization for mobile
        mobile_configs = [r for r in recommendations if r.target_platform == OptimizationTarget.MOBILE]
        assert len(mobile_configs) > 0
        
        # Should recommend quantization for large models
        quantized_configs = [r for r in recommendations if r.quantization]
        assert len(quantized_configs) > 0
    
    def test_model_validation(self):
        """Test model validation"""
        # Create mock TFLite model
        tflite_model = self.temp_dir / "test.tflite"
        tflite_model.write_bytes(b"0" * (5 * 1024 * 1024))
        
        validation = self.service.validate_optimized_model(tflite_model, ModelFormat.TFLITE)
        
        assert validation['valid']
        assert 'model_size_mb' in validation
    
    def test_optimization_stats(self):
        """Test optimization statistics"""
        # Perform some optimizations
        model_file = self.temp_dir / "test_model.pth"
        model_file.write_bytes(b"0" * (10 * 1024 * 1024))
        
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE
        )
        
        self.service.optimize_model(model_file, config)
        
        stats = self.service.get_optimization_stats()
        
        assert stats['total_optimizations'] == 1
        assert stats['successful_optimizations'] >= 0
        assert 'average_compression_ratio' in stats
        assert 'cache_stats' in stats
    
    def test_unsupported_format_error(self):
        """Test error handling for unsupported formats"""
        model_file = self.temp_dir / "test_model.pth"
        model_file.write_bytes(b"0" * (1024 * 1024))
        
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TENSORRT  # Unsupported
        )
        
        result = self.service.optimize_model(model_file, config)
        
        assert not result.success
        assert len(result.errors) > 0

class TestOptimizationIntegration:
    """Integration tests for model optimization"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ModelOptimizationService(self.temp_dir / "cache")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_optimization_workflow(self):
        """Test complete optimization workflow"""
        # Create mock model
        model_file = self.temp_dir / "original_model.pth"
        model_file.write_bytes(b"0" * (20 * 1024 * 1024))  # 20MB
        
        # Get recommendations
        recommendations = self.service.get_optimization_recommendations(
            model_file, OptimizationTarget.MOBILE
        )
        
        assert len(recommendations) > 0
        
        # Optimize with first recommendation
        config = recommendations[0]
        result = self.service.optimize_model(model_file, config, self.temp_dir / "output")
        
        assert result.success
        assert result.optimized_size_mb < result.original_size_mb
        
        # Validate optimized model
        validation = self.service.validate_optimized_model(result.output_path, result.format)
        assert validation['valid']
        
        # Check that model was cached
        cached_path = self.service.cache_manager.get_cached_model_path(
            f"original_model_{config.target_format.value}_{config.target_platform.value}"
        )
        assert cached_path is not None
    
    def test_optimization_with_caching(self):
        """Test optimization with model caching"""
        model_file = self.temp_dir / "test_model.pth"
        model_file.write_bytes(b"0" * (10 * 1024 * 1024))
        
        config = OptimizationConfig(
            target_platform=OptimizationTarget.MOBILE,
            target_format=ModelFormat.TFLITE
        )
        
        # First optimization
        result1 = self.service.optimize_model(model_file, config)
        assert result1.success
        
        # Check cache stats
        cache_stats = self.service.cache_manager.get_cache_stats()
        assert cache_stats['total_cached_models'] > 0
        
        # Optimization stats should include cache info
        opt_stats = self.service.get_optimization_stats()
        assert 'cache_stats' in opt_stats

def test_optimization_result_dataclass():
    """Test OptimizationResult dataclass"""
    result = OptimizationResult(
        success=True,
        original_size_mb=10.0,
        optimized_size_mb=3.0,
        compression_ratio=0.3,
        accuracy_retained=0.98,
        optimization_time=5.2,
        output_path=Path("test.tflite"),
        format=ModelFormat.TFLITE
    )
    
    assert result.success
    assert result.compression_ratio == 0.3
    assert result.format == ModelFormat.TFLITE
    assert len(result.errors) == 0  # Default empty list

def test_model_optimization_service_singleton():
    """Test model optimization service singleton"""
    from src.services.model_optimization_service import get_optimization_service
    
    service1 = get_optimization_service()
    service2 = get_optimization_service()
    
    assert service1 is service2