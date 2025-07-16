"""
Configuration management for the Voice Practice application.
Centralizes all configuration values and provides easy access.
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    """Manages application configuration from config.json and settings.json"""
    
    def __init__(self):
        self.config = {}
        self.settings = {}
        self.load_config()
        self.load_settings()
    
    def load_config(self):
        """Load main configuration from config.json"""
        config_path = 'config.json'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"[Config] Error loading config.json: {e}")
                self.config = self._get_default_config()
        else:
            print("[Config] config.json not found, using defaults")
            self.config = self._get_default_config()
    
    def load_settings(self):
        """Load user settings from settings.json"""
        settings_path = 'settings.json'
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"[Config] Error loading settings.json: {e}")
                self.settings = self._get_default_settings()
        else:
            print("[Config] settings.json not found, using defaults")
            self.settings = self._get_default_settings()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration values"""
        return {
            "audio": {
                "sample_rate": 22050,
                "buffer_size": 1024,
                "channels": 1
            },
            "pitch": {
                "target_min": 165.0,
                "target_max": 255.0,
                "rolling_window_seconds": 60
            },
            "resonance": {
                "target_centroid_min": 2500,
                "target_centroid_max": 3500,
                "rolling_window_seconds": 60
            },
            "intonation": {
                "min_std": 15.0,
                "max_std": 25.0,
                "window_duration": 5.0,
                "rolling_window_seconds": 60
            },
            "gui": {
                "max_history": 100,
                "update_interval_ms": 100,
                "poll_interval_ms": 200
            },
            "analysis": {
                "buffer_duration": 5,
                "min_clip_duration": 1,
                "volume_threshold": 0.02
            }
        }
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Return default user settings"""
        return {
            "dev": True,
            "logs": "./logs/",
            "recordings": "./rec/"
        }
    
    def get(self, path: str, default=None):
        """
        Get configuration value using dot notation.
        Example: get('audio.sample_rate') returns 22050
        """
        keys = path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_setting(self, key: str, default=None):
        """Get user setting value"""
        return self.settings.get(key, default)
    
    def save_settings(self):
        """Save current settings to settings.json"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")
    
    def update_setting(self, key: str, value: Any):
        """Update a setting value and save"""
        self.settings[key] = value
        self.save_settings()

# Global configuration instance
config = ConfigManager()