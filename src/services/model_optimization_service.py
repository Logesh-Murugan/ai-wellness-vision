# model_optimization_service.py - Model optimization and conversion service
import logging
import time
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json

# Optional imports with fallbacks
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow not available - TFLite conversion disabled")

try:
    import torch
    import torch.onnx
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - ONNX conversion disabled")

try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX not available - ONNX optimization disabled")

from src.config import ModelConfig, AppConfig
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

class OptimizationTarget(Enum):
    """Target platforms for model optimization"""
    MOBILE = "mobile"
    WEB = "web"
    EDGE = "edge"
    DESKTOP = "desktop"
    CLOUD = "cloud"

class ModelFormat(Enum):
    """Supported model formats"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    TFLITE = "tflite"
    ONNX = "onnx"
    TENSORRT = "tensorrt"

@dataclass
class OptimizationConfig:
    """Configuration for model optimization"""
    target_platform: OptimizationTarget
    target_format: ModelFormat
    quantization: bool = True
    pruning: bool = False
    compression_ratio: float = 0.5
    accuracy_threshold: float = 0.95
    max_model_size_mb: float = 50.0
    optimization_level: int = 2  # 1=basic, 2=standard, 3=aggressive

@dataclass
class OptimizationResult:
    """Result of model optimization"""
    success: bool
    original_size_mb: float
    optimized_size_mb: float
    compression_ratio: float
    accuracy_retained: float
    optimization_time: float
    output_path: Path
    format: ModelFormat
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class TensorFlowLiteConverter:
    """Converts models to TensorFlow Lite format"""
    
    def __init__(self):
        self.supported_input_formats = [ModelFormat.TENSORFLOW, ModelFormat.PYTORCH]
    
    @log_performance()
    def convert_to_tflite(self, model_path: Path, output_path: Path,
                         config: OptimizationConfig) -> OptimizationResult:
        """Convert model to TensorFlow Lite format"""
        start_time = time.time()
        
        if not TF_AVAILABLE:
            return OptimizationResult(
                success=False,
                original_size_mb=0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=time.time() - start_time,
                output_path=output_path,
                format=ModelFormat.TFLITE,
                errors=["TensorFlow not available"]
            )
        
        try:
            # Get original model size
            original_size = model_path.stat().st_size / (1024 * 1024)
            
            # Mock conversion for demonstration
            result = self._mock_tflite_conversion(model_path, output_path, config, original_size)
            result.optimization_time = time.time() - start_time
            
            logger.info(f"TFLite conversion completed: {original_size:.2f}MB -> {result.optimized_size_mb:.2f}MB")
            return result
            
        except Exception as e:
            logger.error(f"TFLite conversion failed: {e}")
            return OptimizationResult(
                success=False,
                original_size_mb=original_size if 'original_size' in locals() else 0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=time.time() - start_time,
                output_path=output_path,
                format=ModelFormat.TFLITE,
                errors=[str(e)]
            )
    
    def _mock_tflite_conversion(self, model_path: Path, output_path: Path,
                               config: OptimizationConfig, original_size: float) -> OptimizationResult:
        """Mock TFLite conversion for demonstration"""
        # Create mock TFLite file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate optimization based on config
        compression_factor = 0.3 if config.quantization else 0.7
        if config.pruning:
            compression_factor *= 0.8
        
        optimized_size = original_size * compression_factor
        
        # Create mock file with appropriate size
        mock_data = b'0' * int(optimized_size * 1024 * 1024)
        output_path.write_bytes(mock_data)
        
        # Simulate accuracy retention
        accuracy_retained = 0.98 if config.quantization else 0.99
        if config.pruning:
            accuracy_retained *= 0.95
        
        return OptimizationResult(
            success=True,
            original_size_mb=original_size,
            optimized_size_mb=optimized_size,
            compression_ratio=optimized_size / original_size,
            accuracy_retained=accuracy_retained,
            optimization_time=0.0,  # Will be set by caller
            output_path=output_path,
            format=ModelFormat.TFLITE,
            metadata={
                'quantization_applied': config.quantization,
                'pruning_applied': config.pruning,
                'target_platform': config.target_platform.value,
                'optimization_level': config.optimization_level
            }
        )
    
    def validate_tflite_model(self, model_path: Path) -> Dict[str, Any]:
        """Validate TensorFlow Lite model"""
        try:
            if not TF_AVAILABLE:
                return {'valid': False, 'error': 'TensorFlow not available'}
            
            # Mock validation
            return {
                'valid': True,
                'input_shape': [1, 224, 224, 3],
                'output_shape': [1, 1000],
                'model_size_mb': model_path.stat().st_size / (1024 * 1024),
                'quantized': True,
                'supported_ops': ['CONV_2D', 'DEPTHWISE_CONV_2D', 'FULLY_CONNECTED']
            }
            
        except Exception as e:
            logger.error(f"TFLite model validation failed: {e}")
            return {'valid': False, 'error': str(e)}

class ONNXConverter:
    """Converts models to ONNX format"""
    
    def __init__(self):
        self.supported_input_formats = [ModelFormat.PYTORCH, ModelFormat.TENSORFLOW]
    
    @log_performance()
    def convert_to_onnx(self, model_path: Path, output_path: Path,
                       config: OptimizationConfig) -> OptimizationResult:
        """Convert model to ONNX format"""
        start_time = time.time()
        
        if not ONNX_AVAILABLE:
            return OptimizationResult(
                success=False,
                original_size_mb=0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=time.time() - start_time,
                output_path=output_path,
                format=ModelFormat.ONNX,
                errors=["ONNX not available"]
            )
        
        try:
            # Get original model size
            original_size = model_path.stat().st_size / (1024 * 1024)
            
            # Mock conversion for demonstration
            result = self._mock_onnx_conversion(model_path, output_path, config, original_size)
            result.optimization_time = time.time() - start_time
            
            logger.info(f"ONNX conversion completed: {original_size:.2f}MB -> {result.optimized_size_mb:.2f}MB")
            return result
            
        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")
            return OptimizationResult(
                success=False,
                original_size_mb=original_size if 'original_size' in locals() else 0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=time.time() - start_time,
                output_path=output_path,
                format=ModelFormat.ONNX,
                errors=[str(e)]
            )
    
    def _mock_onnx_conversion(self, model_path: Path, output_path: Path,
                             config: OptimizationConfig, original_size: float) -> OptimizationResult:
        """Mock ONNX conversion for demonstration"""
        # Create mock ONNX file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate optimization
        compression_factor = 0.4 if config.quantization else 0.8
        optimized_size = original_size * compression_factor
        
        # Create mock file
        mock_data = b'0' * int(optimized_size * 1024 * 1024)
        output_path.write_bytes(mock_data)
        
        # Simulate accuracy retention
        accuracy_retained = 0.97 if config.quantization else 0.99
        
        return OptimizationResult(
            success=True,
            original_size_mb=original_size,
            optimized_size_mb=optimized_size,
            compression_ratio=optimized_size / original_size,
            accuracy_retained=accuracy_retained,
            optimization_time=0.0,
            output_path=output_path,
            format=ModelFormat.ONNX,
            metadata={
                'quantization_applied': config.quantization,
                'target_platform': config.target_platform.value,
                'optimization_level': config.optimization_level,
                'opset_version': 11
            }
        )
    
    def optimize_onnx_model(self, model_path: Path, output_path: Path,
                           config: OptimizationConfig) -> OptimizationResult:
        """Optimize existing ONNX model"""
        try:
            if not ONNX_AVAILABLE:
                return OptimizationResult(
                    success=False,
                    original_size_mb=0.0,
                    optimized_size_mb=0.0,
                    compression_ratio=0.0,
                    accuracy_retained=0.0,
                    optimization_time=0.0,
                    output_path=output_path,
                    format=ModelFormat.ONNX,
                    errors=["ONNX not available"]
                )
            
            # Mock optimization
            original_size = model_path.stat().st_size / (1024 * 1024)
            optimized_size = original_size * 0.6  # 40% reduction
            
            # Copy and modify file
            shutil.copy2(model_path, output_path)
            
            return OptimizationResult(
                success=True,
                original_size_mb=original_size,
                optimized_size_mb=optimized_size,
                compression_ratio=0.6,
                accuracy_retained=0.98,
                optimization_time=2.5,
                output_path=output_path,
                format=ModelFormat.ONNX,
                metadata={'optimization_passes': ['constant_folding', 'dead_code_elimination']}
            )
            
        except Exception as e:
            logger.error(f"ONNX optimization failed: {e}")
            return OptimizationResult(
                success=False,
                original_size_mb=0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=0.0,
                output_path=output_path,
                format=ModelFormat.ONNX,
                errors=[str(e)]
            )

class ModelCacheManager:
    """Manages model caching and lazy loading"""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("cache/models")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index = self._load_cache_index()
        self.loaded_models = {}
        self.max_cache_size_gb = 5.0
        self.max_loaded_models = 3
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index from disk"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache index: {e}")
        
        return {
            'models': {},
            'total_size_mb': 0.0,
            'last_updated': time.time()
        }
    
    def _save_cache_index(self) -> None:
        """Save cache index to disk"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            self.cache_index['last_updated'] = time.time()
            with open(index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save cache index: {e}")
    
    def cache_model(self, model_id: str, model_path: Path, 
                   metadata: Dict[str, Any] = None) -> bool:
        """Cache a model for faster loading"""
        try:
            # Check if we need to make space
            model_size_mb = model_path.stat().st_size / (1024 * 1024)
            if not self._ensure_cache_space(model_size_mb):
                logger.warning(f"Could not make space for model {model_id}")
                return False
            
            # Copy model to cache
            cached_path = self.cache_dir / f"{model_id}.model"
            shutil.copy2(model_path, cached_path)
            
            # Update cache index
            self.cache_index['models'][model_id] = {
                'path': str(cached_path),
                'size_mb': model_size_mb,
                'cached_at': time.time(),
                'access_count': 0,
                'last_accessed': time.time(),
                'metadata': metadata or {}
            }
            
            self.cache_index['total_size_mb'] += model_size_mb
            self._save_cache_index()
            
            logger.info(f"Cached model {model_id} ({model_size_mb:.2f}MB)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache model {model_id}: {e}")
            return False
    
    def get_cached_model_path(self, model_id: str) -> Optional[Path]:
        """Get path to cached model"""
        if model_id in self.cache_index['models']:
            model_info = self.cache_index['models'][model_id]
            cached_path = Path(model_info['path'])
            
            if cached_path.exists():
                # Update access statistics
                model_info['access_count'] += 1
                model_info['last_accessed'] = time.time()
                self._save_cache_index()
                
                return cached_path
            else:
                # Remove from index if file doesn't exist
                self._remove_from_cache(model_id)
        
        return None
    
    def lazy_load_model(self, model_id: str, loader_func, *args, **kwargs):
        """Lazy load model with caching"""
        # Check if already loaded in memory
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]
        
        # Check if we need to unload models to make space
        if len(self.loaded_models) >= self.max_loaded_models:
            self._unload_least_used_model()
        
        # Load model
        try:
            model = loader_func(*args, **kwargs)
            self.loaded_models[model_id] = {
                'model': model,
                'loaded_at': time.time(),
                'access_count': 1,
                'last_accessed': time.time()
            }
            
            logger.info(f"Lazy loaded model {model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to lazy load model {model_id}: {e}")
            raise
    
    def _ensure_cache_space(self, required_mb: float) -> bool:
        """Ensure there's enough cache space"""
        max_size_mb = self.max_cache_size_gb * 1024
        current_size = self.cache_index['total_size_mb']
        
        if current_size + required_mb <= max_size_mb:
            return True
        
        # Remove least recently used models
        models_by_access = sorted(
            self.cache_index['models'].items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        for model_id, model_info in models_by_access:
            if current_size + required_mb <= max_size_mb:
                break
            
            self._remove_from_cache(model_id)
            current_size -= model_info['size_mb']
        
        return current_size + required_mb <= max_size_mb
    
    def _remove_from_cache(self, model_id: str) -> None:
        """Remove model from cache"""
        if model_id in self.cache_index['models']:
            model_info = self.cache_index['models'][model_id]
            cached_path = Path(model_info['path'])
            
            # Remove file
            if cached_path.exists():
                cached_path.unlink()
            
            # Update index
            self.cache_index['total_size_mb'] -= model_info['size_mb']
            del self.cache_index['models'][model_id]
            
            logger.info(f"Removed model {model_id} from cache")
    
    def _unload_least_used_model(self) -> None:
        """Unload the least recently used model from memory"""
        if not self.loaded_models:
            return
        
        # Find least recently used
        lru_model_id = min(
            self.loaded_models.keys(),
            key=lambda x: self.loaded_models[x]['last_accessed']
        )
        
        del self.loaded_models[lru_model_id]
        logger.info(f"Unloaded model {lru_model_id} from memory")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_cached_models': len(self.cache_index['models']),
            'total_cache_size_mb': self.cache_index['total_size_mb'],
            'cache_size_limit_gb': self.max_cache_size_gb,
            'loaded_models_count': len(self.loaded_models),
            'loaded_models_limit': self.max_loaded_models,
            'cache_directory': str(self.cache_dir),
            'most_accessed_models': self._get_most_accessed_models(5)
        }
    
    def _get_most_accessed_models(self, limit: int) -> List[Dict[str, Any]]:
        """Get most accessed models"""
        models_by_access = sorted(
            self.cache_index['models'].items(),
            key=lambda x: x[1]['access_count'],
            reverse=True
        )
        
        return [
            {
                'model_id': model_id,
                'access_count': info['access_count'],
                'size_mb': info['size_mb'],
                'last_accessed': info['last_accessed']
            }
            for model_id, info in models_by_access[:limit]
        ]
    
    def cleanup_cache(self, max_age_days: int = 30) -> None:
        """Clean up old cached models"""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        models_to_remove = []
        
        for model_id, model_info in self.cache_index['models'].items():
            if model_info['last_accessed'] < cutoff_time:
                models_to_remove.append(model_id)
        
        for model_id in models_to_remove:
            self._remove_from_cache(model_id)
        
        self._save_cache_index()
        logger.info(f"Cleaned up {len(models_to_remove)} old cached models")

class ModelOptimizationService:
    """Main service for model optimization and management"""
    
    def __init__(self, cache_dir: Path = None):
        self.tflite_converter = TensorFlowLiteConverter()
        self.onnx_converter = ONNXConverter()
        self.cache_manager = ModelCacheManager(cache_dir)
        self.optimization_history = []
    
    @log_performance()
    def optimize_model(self, model_path: Path, target_config: OptimizationConfig,
                      output_dir: Path = None) -> OptimizationResult:
        """Optimize model for target platform"""
        try:
            if output_dir is None:
                output_dir = Path("optimized_models")
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine output filename
            model_name = model_path.stem
            if target_config.target_format == ModelFormat.TFLITE:
                output_path = output_dir / f"{model_name}_optimized.tflite"
                result = self.tflite_converter.convert_to_tflite(model_path, output_path, target_config)
            elif target_config.target_format == ModelFormat.ONNX:
                output_path = output_dir / f"{model_name}_optimized.onnx"
                result = self.onnx_converter.convert_to_onnx(model_path, output_path, target_config)
            else:
                raise ValueError(f"Unsupported target format: {target_config.target_format}")
            
            # Cache optimized model if successful
            if result.success:
                model_id = f"{model_name}_{target_config.target_format.value}_{target_config.target_platform.value}"
                self.cache_manager.cache_model(
                    model_id, 
                    result.output_path,
                    {
                        'optimization_config': {
                            'target_platform': target_config.target_platform.value,
                            'target_format': target_config.target_format.value,
                            'quantization': target_config.quantization,
                            'pruning': target_config.pruning
                        },
                        'optimization_result': {
                            'compression_ratio': result.compression_ratio,
                            'accuracy_retained': result.accuracy_retained,
                            'optimization_time': result.optimization_time
                        }
                    }
                )
            
            # Add to history
            self.optimization_history.append({
                'timestamp': time.time(),
                'model_path': str(model_path),
                'target_config': target_config,
                'result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
            return OptimizationResult(
                success=False,
                original_size_mb=0.0,
                optimized_size_mb=0.0,
                compression_ratio=0.0,
                accuracy_retained=0.0,
                optimization_time=0.0,
                output_path=Path(""),
                format=target_config.target_format,
                errors=[str(e)]
            )
    
    def batch_optimize_models(self, model_paths: List[Path], 
                             target_configs: List[OptimizationConfig],
                             output_dir: Path = None) -> List[OptimizationResult]:
        """Optimize multiple models with different configurations"""
        results = []
        
        for model_path in model_paths:
            for config in target_configs:
                try:
                    result = self.optimize_model(model_path, config, output_dir)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to optimize {model_path} with config {config}: {e}")
                    results.append(OptimizationResult(
                        success=False,
                        original_size_mb=0.0,
                        optimized_size_mb=0.0,
                        compression_ratio=0.0,
                        accuracy_retained=0.0,
                        optimization_time=0.0,
                        output_path=Path(""),
                        format=config.target_format,
                        errors=[str(e)]
                    ))
        
        return results
    
    def get_optimization_recommendations(self, model_path: Path,
                                       target_platform: OptimizationTarget) -> List[OptimizationConfig]:
        """Get recommended optimization configurations for a model"""
        recommendations = []
        
        # Get model size
        model_size_mb = model_path.stat().st_size / (1024 * 1024)
        
        if target_platform == OptimizationTarget.MOBILE:
            # Mobile-optimized configurations
            recommendations.extend([
                OptimizationConfig(
                    target_platform=OptimizationTarget.MOBILE,
                    target_format=ModelFormat.TFLITE,
                    quantization=True,
                    pruning=model_size_mb > 20,
                    max_model_size_mb=10.0,
                    optimization_level=3
                ),
                OptimizationConfig(
                    target_platform=OptimizationTarget.MOBILE,
                    target_format=ModelFormat.ONNX,
                    quantization=True,
                    pruning=False,
                    max_model_size_mb=15.0,
                    optimization_level=2
                )
            ])
        
        elif target_platform == OptimizationTarget.WEB:
            # Web-optimized configurations
            recommendations.append(
                OptimizationConfig(
                    target_platform=OptimizationTarget.WEB,
                    target_format=ModelFormat.ONNX,
                    quantization=True,
                    pruning=False,
                    max_model_size_mb=25.0,
                    optimization_level=2
                )
            )
        
        elif target_platform == OptimizationTarget.EDGE:
            # Edge device configurations
            recommendations.extend([
                OptimizationConfig(
                    target_platform=OptimizationTarget.EDGE,
                    target_format=ModelFormat.TFLITE,
                    quantization=True,
                    pruning=True,
                    max_model_size_mb=5.0,
                    optimization_level=3
                ),
                OptimizationConfig(
                    target_platform=OptimizationTarget.EDGE,
                    target_format=ModelFormat.ONNX,
                    quantization=True,
                    pruning=model_size_mb > 10,
                    max_model_size_mb=8.0,
                    optimization_level=3
                )
            ])
        
        return recommendations
    
    def validate_optimized_model(self, model_path: Path, 
                                format: ModelFormat) -> Dict[str, Any]:
        """Validate an optimized model"""
        try:
            if format == ModelFormat.TFLITE:
                return self.tflite_converter.validate_tflite_model(model_path)
            elif format == ModelFormat.ONNX:
                # Mock ONNX validation
                return {
                    'valid': True,
                    'input_shape': [1, 3, 224, 224],
                    'output_shape': [1, 1000],
                    'model_size_mb': model_path.stat().st_size / (1024 * 1024),
                    'opset_version': 11
                }
            else:
                return {'valid': False, 'error': f'Unsupported format: {format}'}
                
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {'valid': False, 'error': str(e)}
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {
                'total_optimizations': 0,
                'successful_optimizations': 0,
                'average_compression_ratio': 0.0,
                'average_accuracy_retained': 0.0,
                'total_size_saved_mb': 0.0
            }
        
        successful = [h for h in self.optimization_history if h['result'].success]
        
        total_size_saved = sum(
            h['result'].original_size_mb - h['result'].optimized_size_mb
            for h in successful
        )
        
        avg_compression = sum(h['result'].compression_ratio for h in successful) / len(successful) if successful else 0.0
        avg_accuracy = sum(h['result'].accuracy_retained for h in successful) / len(successful) if successful else 0.0
        
        return {
            'total_optimizations': len(self.optimization_history),
            'successful_optimizations': len(successful),
            'success_rate': len(successful) / len(self.optimization_history) if self.optimization_history else 0.0,
            'average_compression_ratio': avg_compression,
            'average_accuracy_retained': avg_accuracy,
            'total_size_saved_mb': total_size_saved,
            'cache_stats': self.cache_manager.get_cache_stats()
        }

# Global model optimization service instance
optimization_service = ModelOptimizationService()

def get_optimization_service() -> ModelOptimizationService:
    """Get the global model optimization service instance"""
    return optimization_service