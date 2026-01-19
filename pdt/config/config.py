"""
Configuration Management - Environment-based configs.
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file
        """
        self.config: Dict[str, Any] = {}
        
        # Load from file if provided
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Model config
        if os.getenv('MODEL_DEVICE'):
            self.config['model'] = self.config.get('model', {})
            self.config['model']['device'] = os.getenv('MODEL_DEVICE')
        
        # API config
        if os.getenv('API_HOST'):
            self.config['api'] = self.config.get('api', {})
            self.config['api']['host'] = os.getenv('API_HOST')
        
        if os.getenv('API_PORT'):
            self.config['api'] = self.config.get('api', {})
            self.config['api']['port'] = int(os.getenv('API_PORT'))
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Configuration value
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value


# Global config instance
config = Config()



