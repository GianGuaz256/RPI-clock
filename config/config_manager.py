"""
Configuration management for the Raspberry Pi Dashboard.
Supports both environment variables (.env file) and JSON configuration.
"""

import json
import os
from typing import Dict, Any, Union, List
from pathlib import Path

# Import dotenv for environment variable loading
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not available. Install with: pip install python-dotenv")


class ConfigManager:
    """
    Manages application configuration with support for:
    1. Environment variables (preferred, loaded from .env file)
    2. JSON configuration file (fallback for backwards compatibility)
    """
    
    def __init__(self, config_file: str = 'config.json', env_file: str = '.env'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to JSON configuration file (fallback)
            env_file: Path to .env file (preferred)
        """
        self.config_file = config_file
        self.env_file = env_file
        
        # Load environment variables from .env file
        self._load_env_file()
        
        # Load configuration (env vars take precedence over JSON)
        self.config = self._load_config()
        
        print(f"Configuration loaded from: {self._get_config_sources()}")
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file if available."""
        if DOTENV_AVAILABLE and os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            print(f"Loaded environment variables from {self.env_file}")
        elif os.path.exists(self.env_file):
            print(f"Found {self.env_file} but python-dotenv not installed")
        else:
            print(f"No {self.env_file} file found")
    
    def _get_config_sources(self) -> str:
        """Get string describing configuration sources."""
        sources = []
        
        if DOTENV_AVAILABLE and os.path.exists(self.env_file):
            sources.append("environment variables")
        
        if os.path.exists(self.config_file):
            sources.append("config.json")
        
        if not sources:
            sources.append("defaults")
        
        return " -> ".join(sources)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables and JSON file.
        Environment variables take precedence over JSON configuration.
        
        Returns:
            Configuration dictionary
        """
        # Start with default configuration
        config = self._get_default_config()
        
        # Load from JSON file if it exists (backwards compatibility)
        json_config = self._load_json_config()
        if json_config:
            config = self._deep_merge(config, json_config)
        
        # Override with environment variables (preferred method)
        env_config = self._load_env_config()
        config = self._deep_merge(config, env_config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "weather": {
                "api_key": "",
                "city": "London,UK",
                "units": "metric"
            },
            "display": {
                "brightness": 100,
                "timeout": 0
            },
            "google_calendar": {
                "credentials_file": "credentials.json",
                "token_file": "token.json",
                "scopes": ["https://www.googleapis.com/auth/calendar.readonly"]
            },
            "app": {
                "api_update_interval": 300,
                "system_update_interval": 5,
                "touch_swipe_threshold": 100,
                "fps": 30,
                "debug_mode": False,
                "log_level": "INFO"
            }
        }
    
    def _load_json_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.config_file}: {e}")
            return {}
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Weather configuration
        weather_config = {}
        if os.getenv('WEATHER_API_KEY'):
            weather_config['api_key'] = os.getenv('WEATHER_API_KEY')
        if os.getenv('WEATHER_CITY'):
            weather_config['city'] = os.getenv('WEATHER_CITY')
        if os.getenv('WEATHER_UNITS'):
            weather_config['units'] = os.getenv('WEATHER_UNITS')
        
        if weather_config:
            config['weather'] = weather_config
        
        # Display configuration
        display_config = {}
        if os.getenv('DISPLAY_BRIGHTNESS'):
            try:
                display_config['brightness'] = int(os.getenv('DISPLAY_BRIGHTNESS'))
            except ValueError:
                print("Warning: Invalid DISPLAY_BRIGHTNESS value, using default")
        
        if os.getenv('DISPLAY_TIMEOUT'):
            try:
                display_config['timeout'] = int(os.getenv('DISPLAY_TIMEOUT'))
            except ValueError:
                print("Warning: Invalid DISPLAY_TIMEOUT value, using default")
        
        if display_config:
            config['display'] = display_config
        
        # Google Calendar configuration
        calendar_config = {}
        if os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE'):
            calendar_config['credentials_file'] = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE')
        if os.getenv('GOOGLE_CALENDAR_TOKEN_FILE'):
            calendar_config['token_file'] = os.getenv('GOOGLE_CALENDAR_TOKEN_FILE')
        if os.getenv('GOOGLE_CALENDAR_SCOPES'):
            scopes = os.getenv('GOOGLE_CALENDAR_SCOPES').split(',')
            calendar_config['scopes'] = [scope.strip() for scope in scopes]
        
        if calendar_config:
            config['google_calendar'] = calendar_config
        
        # Application configuration
        app_config = {}
        if os.getenv('API_UPDATE_INTERVAL'):
            try:
                app_config['api_update_interval'] = int(os.getenv('API_UPDATE_INTERVAL'))
            except ValueError:
                print("Warning: Invalid API_UPDATE_INTERVAL value, using default")
        
        if os.getenv('SYSTEM_UPDATE_INTERVAL'):
            try:
                app_config['system_update_interval'] = int(os.getenv('SYSTEM_UPDATE_INTERVAL'))
            except ValueError:
                print("Warning: Invalid SYSTEM_UPDATE_INTERVAL value, using default")
        
        if os.getenv('TOUCH_SWIPE_THRESHOLD'):
            try:
                app_config['touch_swipe_threshold'] = int(os.getenv('TOUCH_SWIPE_THRESHOLD'))
            except ValueError:
                print("Warning: Invalid TOUCH_SWIPE_THRESHOLD value, using default")
        
        if os.getenv('APP_FPS'):
            try:
                app_config['fps'] = int(os.getenv('APP_FPS'))
            except ValueError:
                print("Warning: Invalid APP_FPS value, using default")
        
        if os.getenv('DEBUG_MODE'):
            app_config['debug_mode'] = os.getenv('DEBUG_MODE').lower() in ('true', '1', 'yes', 'on')
        
        if os.getenv('LOG_LEVEL'):
            app_config['log_level'] = os.getenv('LOG_LEVEL').upper()
        
        if app_config:
            config['app'] = app_config
        
        return config
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            update: Dictionary to merge into base
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., 'weather.api_key')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        Note: This only affects the in-memory configuration.
        
        Args:
            path: Configuration path (e.g., 'weather.api_key')
            value: Value to set
        """
        keys = path.split('.')
        config = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Section configuration or empty dict
        """
        return self.config.get(section, {})
    
    def is_env_configured(self) -> bool:
        """
        Check if environment variables are being used for configuration.
        
        Returns:
            True if .env file exists and dotenv is available
        """
        return DOTENV_AVAILABLE and os.path.exists(self.env_file)
    
    def get_config_status(self) -> Dict[str, Any]:
        """
        Get configuration status and information.
        
        Returns:
            Dictionary with configuration status
        """
        return {
            'env_file_exists': os.path.exists(self.env_file),
            'json_file_exists': os.path.exists(self.config_file),
            'dotenv_available': DOTENV_AVAILABLE,
            'using_env_vars': self.is_env_configured(),
            'weather_api_configured': bool(self.get('weather.api_key')),
            'google_calendar_configured': os.path.exists(self.get('google_calendar.credentials_file', '')),
            'config_sources': self._get_config_sources()
        }
    
    def validate_configuration(self) -> List[str]:
        """
        Validate configuration and return list of warnings.
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check weather API key
        weather_key = self.get('weather.api_key')
        if not weather_key or weather_key == 'YOUR_OPENWEATHERMAP_API_KEY_HERE':
            warnings.append("Weather API key not configured. Weather screen will show errors.")
        
        # Check Google Calendar credentials
        credentials_file = self.get('google_calendar.credentials_file')
        if credentials_file and not os.path.exists(credentials_file):
            warnings.append(f"Google Calendar credentials file not found: {credentials_file}")
        
        # Check configuration method
        if not self.is_env_configured() and os.path.exists(self.config_file):
            warnings.append("Using JSON configuration. Consider migrating to .env file for better security.")
        
        # Check for sensitive data in JSON
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    json_data = json.load(f)
                    weather_section = json_data.get('weather', {})
                    if weather_section.get('api_key') and weather_section['api_key'] != 'YOUR_OPENWEATHERMAP_API_KEY_HERE':
                        warnings.append("API key found in config.json. Consider moving to .env file for security.")
            except:
                pass
        
        return warnings 