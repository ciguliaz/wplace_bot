"""Configuration management for Place Bot"""

import json
import os
from typing import Dict, Any

class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        'ui': {
            'theme': 'clam',
            'window_size': '800x800',
            'remember_position': True,
            'auto_save_interval': 30  # seconds
        },
        'bot': {
            'default_pixel_limit': 50,
            'default_tolerance': 5,
            'default_delay': 50,
            'max_pixel_limit': 1000,
            'safety_checks': True
        },
        'logging': {
            'level': 'INFO',
            'max_log_files': 7,
            'log_to_file': True,
            'log_to_console': True
        },
        'analysis': {
            'auto_refresh_interval': 0,  # 0 = disabled
            'save_debug_images': True,
            'image_quality': 'high'
        }
    }
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self.config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'ui.theme')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def _merge_config(self, base: Dict, update: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

# Global config instance
_config_instance = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance