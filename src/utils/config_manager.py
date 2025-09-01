# config_manager.py - Configuration management utilities
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict
from src.config import get_config, validate_config, Environment, AppConfig

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self._config = None
        self._environment_file = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and files"""
        try:
            # Load base configuration
            self._config = get_config()
            
            # Load environment-specific configuration file if exists
            env_config_file = Path(f"config/{AppConfig.ENVIRONMENT.value}.json")
            if env_config_file.exists():
                self.load_environment_config(env_config_file)
            
            # Validate configuration
            if not validate_config():
                raise ValueError("Configuration validation failed")
            
            logger.info(f"Configuration loaded for environment: {AppConfig.ENVIRONMENT.value}")
            return self._config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def load_environment_config(self, config_file: Path) -> None:
        """Load environment-specific configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                env_config = json.load(f)
            
            # Merge environment config with base config
            self._merge_config(self._config, env_config)
            logger.info(f"Loaded environment config from {config_file}")
            
        except Exception as e:
            logger.warning(f"Could not load environment config from {config_file}: {e}")
    
    def _merge_config(self, base_config: Dict, env_config: Dict) -> None:
        """Recursively merge environment config into base config"""
        for key, value in env_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = getattr(value, k, None)
                
                if value is None:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            config = self._config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            logger.debug(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set configuration {key}: {e}")
            raise
    
    def export_config(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export current configuration to file or return as dict"""
        try:
            # Convert config to serializable format
            serializable_config = self._make_serializable(self._config)
            
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w') as f:
                    json.dump(serializable_config, f, indent=2)
                logger.info(f"Configuration exported to {output_file}")
            
            return serializable_config
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert configuration objects to JSON-serializable format"""
        if hasattr(obj, '__dict__'):
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        else:
            return obj
    
    def reload_config(self) -> None:
        """Reload configuration from sources"""
        logger.info("Reloading configuration...")
        self.load_config()
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the current environment"""
        return {
            "environment": AppConfig.ENVIRONMENT.value,
            "debug": AppConfig.DEBUG,
            "python_version": os.sys.version,
            "platform": os.sys.platform,
            "working_directory": str(Path.cwd()),
            "config_loaded": self._config is not None,
        }

# Global configuration manager instance
config_manager = ConfigManager()

def get_config_value(key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value"""
    return config_manager.get(key, default)

def set_config_value(key: str, value: Any) -> None:
    """Convenience function to set configuration value"""
    config_manager.set(key, value)

def reload_configuration() -> None:
    """Convenience function to reload configuration"""
    config_manager.reload_config()