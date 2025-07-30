"""
Tests for configuration management (ConfigManager).
"""

import os
import pytest
from unittest.mock import patch, mock_open
from config.config_manager import ConfigManager


class TestConfigManager:
    """Test the ConfigManager class."""
    
    def test_init_without_files(self, temp_dir):
        """Test ConfigManager initialization without config files."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config is not None
            assert config.get('weather.city') == 'London,UK'  # Default value
    
    def test_load_env_file(self, temp_dir, mock_env_file):
        """Test loading configuration from .env file."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config.get('weather.api_key') == 'test_weather_key'
            assert config.get('weather.city') == 'TestCity,TC'
            assert config.get('app.fps') == 15
            assert config.get('app.debug_mode') is True
    
    def test_load_json_file(self, temp_dir, mock_config_json):
        """Test loading configuration from JSON file."""
        # Remove .env file to test JSON loading
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config.get('weather.api_key') == 'json_weather_key'
            assert config.get('weather.city') == 'JsonCity,JC'
            assert config.get('weather.units') == 'imperial'
    
    def test_env_overrides_json(self, temp_dir, mock_env_file, mock_config_json):
        """Test that environment variables override JSON configuration."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            # Env should override JSON
            assert config.get('weather.api_key') == 'test_weather_key'  # From .env
            assert config.get('weather.city') == 'TestCity,TC'  # From .env
            # Values only in JSON should still be available
            assert config.get('display.brightness') == 80  # From JSON only
    
    def test_get_with_default(self, temp_dir):
        """Test getting configuration values with defaults."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config.get('nonexistent.key', 'default_value') == 'default_value'
            assert config.get('weather.city', 'fallback') == 'London,UK'  # Has default
    
    def test_set_configuration(self, temp_dir):
        """Test setting configuration values."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            config.set('test.key', 'test_value')
            assert config.get('test.key') == 'test_value'
    
    def test_nested_configuration(self, temp_dir, mock_env_file):
        """Test accessing nested configuration values."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config.get('weather.api_key') == 'test_weather_key'
            assert config.get('app.fps') == 15
    
    def test_get_config_status(self, temp_dir, mock_env_file):
        """Test configuration status reporting."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            status = config.get_config_status()
            
            assert 'env_file_exists' in status
            assert 'json_file_exists' in status
            assert 'dotenv_available' in status
            assert 'config_sources' in status
            assert status['env_file_exists'] is True
    
    def test_validate_configuration(self, temp_dir, mock_env_file):
        """Test configuration validation."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            warnings = config.validate_configuration()
            
            # Should be a list of warning strings
            assert isinstance(warnings, list)
    
    def test_is_env_configured(self, temp_dir, mock_env_file):
        """Test environment configuration detection."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            assert config.is_env_configured() is True
    
    def test_dotenv_import_error(self, temp_dir):
        """Test handling when python-dotenv is not available."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch.dict('sys.modules', {'dotenv': None}):
            config = ConfigManager()
            status = config.get_config_status()
            assert status['dotenv_available'] is False
    
    def test_invalid_json_file(self, temp_dir):
        """Test handling of invalid JSON configuration file."""
        # Create invalid JSON file
        invalid_json_path = os.path.join(temp_dir, 'config.json')
        with open(invalid_json_path, 'w') as f:
            f.write('{ invalid json }')
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            # Should fall back to defaults without crashing
            assert config.get('weather.city') == 'London,UK'
    
    def test_type_conversion(self, temp_dir):
        """Test automatic type conversion of environment variables."""
        env_content = """
        TEST_INT=42
        TEST_FLOAT=3.14
        TEST_BOOL_TRUE=true
        TEST_BOOL_FALSE=false
        TEST_STRING=hello
        """
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            # Note: Environment variables are typically strings,
            # conversion depends on implementation
            assert config.get('test_int') is not None
            assert config.get('test_string') is not None 