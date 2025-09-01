# app_initializer.py - Application initialization utilities
import logging
import sys
from pathlib import Path
from typing import Optional

from src.utils.logging_config import setup_logging
from src.utils.config_manager import config_manager
from src.config import validate_config, AppConfig, Environment

logger = logging.getLogger(__name__)

class AppInitializer:
    """Handles application initialization and setup"""
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self, config_override: Optional[dict] = None) -> bool:
        """Initialize the application with proper setup"""
        try:
            print("Initializing AI WellnessVision...")
            
            # Step 1: Setup logging
            setup_logging()
            logger.info("Starting AI WellnessVision initialization")
            
            # Step 2: Load and validate configuration
            if config_override:
                for key, value in config_override.items():
                    config_manager.set(key, value)
            
            if not validate_config():
                raise RuntimeError("Configuration validation failed")
            
            # Step 3: Log environment information
            env_info = config_manager.get_environment_info()
            logger.info(f"Environment: {env_info['environment']}")
            logger.info(f"Debug mode: {env_info['debug']}")
            logger.info(f"Python version: {env_info['python_version']}")
            
            # Step 4: Create necessary directories
            self._create_directories()
            
            # Step 5: Validate system requirements
            self._validate_system_requirements()
            
            self.initialized = True
            logger.info("AI WellnessVision initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def _create_directories(self) -> None:
        """Create necessary application directories"""
        directories = [
            config_manager.get('paths.data_dir'),
            config_manager.get('paths.models_dir'),
            config_manager.get('paths.logs_dir'),
            config_manager.get('paths.cache_dir'),
            config_manager.get('paths.temp_dir'),
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
    
    def _validate_system_requirements(self) -> None:
        """Validate system requirements and dependencies"""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                raise RuntimeError("Python 3.8 or higher is required")
            
            # Check critical imports
            critical_imports = [
                'torch',
                'transformers',
                'whisper',
                'streamlit',
                'fastapi',
            ]
            
            missing_imports = []
            for module_name in critical_imports:
                try:
                    __import__(module_name)
                except ImportError:
                    missing_imports.append(module_name)
            
            if missing_imports:
                logger.warning(f"Missing optional dependencies: {missing_imports}")
            
            logger.info("System requirements validation completed")
            
        except Exception as e:
            logger.error(f"System requirements validation failed: {e}")
            raise
    
    def shutdown(self) -> None:
        """Graceful application shutdown"""
        try:
            logger.info("Shutting down AI WellnessVision...")
            
            # Cleanup temporary files
            temp_dir = Path(config_manager.get('paths.temp_dir'))
            if temp_dir.exists():
                for temp_file in temp_dir.glob('*'):
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        logger.warning(f"Could not remove temp file {temp_file}: {e}")
            
            self.initialized = False
            logger.info("Shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def get_status(self) -> dict:
        """Get current application status"""
        return {
            "initialized": self.initialized,
            "environment": AppConfig.ENVIRONMENT.value,
            "debug": AppConfig.DEBUG,
            "config_valid": validate_config(),
        }

# Global initializer instance
app_initializer = AppInitializer()

def initialize_app(config_override: Optional[dict] = None) -> bool:
    """Convenience function to initialize the application"""
    return app_initializer.initialize(config_override)

def shutdown_app() -> None:
    """Convenience function to shutdown the application"""
    app_initializer.shutdown()

def get_app_status() -> dict:
    """Convenience function to get application status"""
    return app_initializer.get_status()