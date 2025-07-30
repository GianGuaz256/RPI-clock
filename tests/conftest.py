"""
Pytest configuration and shared fixtures for the dashboard test suite.
"""

import os
import tempfile
import json
import pytest
from unittest.mock import Mock, patch
import pygame

# Test configuration and fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_env_file(temp_dir):
    """Create a mock .env file for testing."""
    env_content = """
# Test environment configuration
WEATHER_API_KEY=test_weather_key
WEATHER_CITY=TestCity,TC
WEATHER_UNITS=metric
WEATHER_MOCK_MODE=false
API_UPDATE_INTERVAL=60
SYSTEM_UPDATE_INTERVAL=2
TOUCH_SWIPE_THRESHOLD=50
APP_FPS=15
DEBUG_MODE=true
GOOGLE_CALENDAR_CREDENTIALS_FILE=test_credentials.json
"""
    env_path = os.path.join(temp_dir, '.env')
    with open(env_path, 'w') as f:
        f.write(env_content.strip())
    return env_path

@pytest.fixture
def mock_config_json(temp_dir):
    """Create a mock config.json file for testing."""
    config_data = {
        "weather": {
            "api_key": "json_weather_key",
            "city": "JsonCity,JC",
            "units": "imperial"
        },
        "display": {
            "brightness": 80,
            "timeout": 30
        },
        "app": {
            "fps": 25,
            "api_update_interval": 120
        },
        "google_calendar": {
            "credentials_file": "json_credentials.json",
            "token_file": "json_token.json"
        }
    }
    config_path = os.path.join(temp_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path

@pytest.fixture
def mock_credentials_json(temp_dir):
    """Create a mock Google credentials file."""
    credentials_data = {
        "installed": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    cred_path = os.path.join(temp_dir, 'test_credentials.json')
    with open(cred_path, 'w') as f:
        json.dump(credentials_data, f)
    return cred_path

@pytest.fixture
def mock_pygame():
    """Mock pygame to avoid display initialization in tests."""
    with patch('pygame.init'), \
         patch('pygame.display.set_mode') as mock_display, \
         patch('pygame.time.Clock'), \
         patch('pygame.event.get', return_value=[]), \
         patch('pygame.display.flip'), \
         patch('pygame.quit'):
        
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.fill = Mock()
        mock_surface.get_width.return_value = 480
        mock_surface.get_height.return_value = 320
        mock_display.return_value = mock_surface
        
        yield mock_surface

@pytest.fixture
def mock_requests():
    """Mock requests for API testing."""
    with patch('requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        yield mock_session

@pytest.fixture
def sample_weather_data():
    """Sample weather API response data."""
    return {
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "main": {
            "temp": 22.5,
            "humidity": 45,
            "pressure": 1015
        },
        "wind": {
            "speed": 3.2,
            "deg": 180
        },
        "visibility": 10000,
        "sys": {
            "country": "UK",
            "sunrise": 1234567890,
            "sunset": 1234567900
        },
        "name": "TestCity"
    }

@pytest.fixture
def sample_bitcoin_data():
    """Sample Bitcoin API response data."""
    return {
        "bitcoin": {
            "usd": 45000.50
        }
    }

@pytest.fixture
def sample_blockchain_data():
    """Sample blockchain API response data."""
    return {
        "height": 800000,
        "hash": "0000000000000000000a1b2c3d4e5f6789abcdef",
        "time": 1234567890
    }

@pytest.fixture
def mock_system_stats():
    """Mock system statistics data."""
    return {
        "cpu_temp": 45.2,
        "cpu_usage": 15.5,
        "memory_usage": 35.8,
        "disk_usage": 12.3,
        "uptime_seconds": 86400,
        "uptime_formatted": "1 day, 0:00:00"
    }

# Test environment setup
def pytest_configure(config):
    """Configure pytest environment."""
    # Ensure we don't accidentally initialize real pygame
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    # Store original env vars
    original_env = dict(os.environ)
    
    yield
    
    # Restore original env vars and clear test vars
    os.environ.clear()
    os.environ.update(original_env) 