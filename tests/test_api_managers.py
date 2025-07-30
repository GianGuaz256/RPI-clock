"""
Tests for API managers (Weather, Bitcoin, Calendar).
"""

import time
import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
from config.config_manager import ConfigManager
from api.weather_api import WeatherAPIManager
from api.bitcoin_api import BitcoinAPIManager
from api.calendar_api import CalendarAPIManager
from api.base_api import BaseAPIManager
import os


class TestBaseAPIManager:
    """Test the base API manager functionality."""
    
    def test_init(self):
        """Test BaseAPIManager initialization."""
        api = BaseAPIManager('test_cache_key')
        assert api.cache_key == 'test_cache_key'
        assert api.update_interval == 300  # Default
        assert api.cache is not None
        assert api.session is not None
    
    def test_custom_update_interval(self):
        """Test BaseAPIManager with custom update interval."""
        api = BaseAPIManager('test_cache_key', update_interval=60)
        assert api.update_interval == 60
    
    def test_get_data_not_implemented(self):
        """Test that _fetch_data raises NotImplementedError in base class."""
        api = BaseAPIManager('test_cache_key')
        with pytest.raises(NotImplementedError):
            api._fetch_data()
    
    def test_cache_operations(self):
        """Test cache-related operations."""
        api = BaseAPIManager('test_cache_key')
        
        # Test cache info
        cache_info = api.get_cache_info()
        assert 'cache_key' in cache_info
        assert 'age_seconds' in cache_info
        assert 'is_expired' in cache_info
        
        # Test cache clearing
        api.clear_cache()  # Should not raise exception


class TestWeatherAPIManager:
    """Test the Weather API manager."""
    
    def test_init(self, temp_dir, mock_env_file):
        """Test WeatherAPIManager initialization."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            assert weather.config == config
            assert weather.cache_key == 'weather'
    
    def test_mock_mode_enabled(self, temp_dir):
        """Test weather API in mock mode."""
        # Create config with mock mode enabled
        env_content = "WEATHER_MOCK_MODE=true\nWEATHER_CITY=TestCity,TC"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            
            data = weather.get_data()
            assert data['data_source'] == 'mock_data'
            assert data['status'] == 'mock'
            assert 'temperature' in data
            assert 'condition' in data
            assert weather.is_using_mock_data() is True
    
    def test_mock_mode_customization(self, temp_dir):
        """Test customizing mock weather data."""
        env_content = """
        WEATHER_MOCK_MODE=true
        WEATHER_MOCK_TEMPERATURE=25.5
        WEATHER_MOCK_CONDITION=Sunny
        WEATHER_MOCK_HUMIDITY=70
        WEATHER_CITY=CustomCity,CC
        """
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            
            data = weather.get_data()
            # Should be close to configured values (within random variation)
            assert abs(data['temperature'] - 25.5) < 2.0
            assert data['condition'] == 'Sunny'
            assert data['city'] == 'CustomCity'
    
    @responses.activate
    def test_real_api_mode(self, temp_dir, sample_weather_data):
        """Test weather API with real API calls."""
        env_content = """
        WEATHER_API_KEY=real_api_key
        WEATHER_MOCK_MODE=false
        WEATHER_CITY=TestCity,TC
        """
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        # Mock the API response
        responses.add(
            responses.GET,
            'https://api.openweathermap.org/data/2.5/weather',
            json=sample_weather_data,
            status=200
        )
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            
            data = weather.get_data()
            assert data['data_source'] == 'openweathermap_api'
            assert data['status'] == 'success'
            assert data['temperature'] == 22.5
            assert data['city'] == 'TestCity'
            assert weather.is_using_mock_data() is False
    
    def test_api_fallback_to_mock(self, temp_dir):
        """Test fallback to mock data when API fails."""
        env_content = """
        WEATHER_API_KEY=real_api_key
        WEATHER_MOCK_MODE=false
        """
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('requests.Session.get', side_effect=Exception("API Error")):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            
            data = weather.get_data()
            # Should fall back to mock data
            assert data['data_source'] == 'mock_data'
            assert data['status'] == 'mock'
    
    def test_helper_methods(self, temp_dir):
        """Test weather API helper methods."""
        env_content = "WEATHER_MOCK_MODE=true"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather = WeatherAPIManager(config)
            
            # Test helper methods
            temp = weather.get_temperature()
            assert isinstance(temp, (int, float))
            
            formatted_temp = weather.get_formatted_temperature()
            assert isinstance(formatted_temp, str)
            assert '°' in formatted_temp
            
            condition = weather.get_condition()
            assert isinstance(condition, str)
            
            icon = weather.get_icon()
            assert isinstance(icon, str)
            
            wind_info = weather.get_wind_info()
            assert 'speed' in wind_info
            assert 'direction' in wind_info
            
            source_info = weather.get_data_source_info()
            assert 'Mock' in source_info or 'API' in source_info


class TestBitcoinAPIManager:
    """Test the Bitcoin API manager."""
    
    def test_init(self, temp_dir):
        """Test BitcoinAPIManager initialization."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            bitcoin = BitcoinAPIManager(config)
            assert bitcoin.config == config
            assert bitcoin.cache_key == 'bitcoin'
    
    @responses.activate
    def test_fetch_bitcoin_data(self, temp_dir, sample_bitcoin_data, sample_blockchain_data):
        """Test fetching Bitcoin price and blockchain data."""
        # Mock API responses
        responses.add(
            responses.GET,
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            json=sample_bitcoin_data,
            status=200
        )
        responses.add(
            responses.GET,
            'https://blockchain.info/latestblock',
            json=sample_blockchain_data,
            status=200
        )
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            bitcoin = BitcoinAPIManager(config)
            
            data = bitcoin.get_data()
            assert data['status'] == 'success'
            assert data['price'] == 45000.50
            assert data['block_height'] == 800000
            assert 'formatted_price' in data
    
    @responses.activate
    def test_api_error_handling(self, temp_dir):
        """Test Bitcoin API error handling."""
        # Mock API error
        responses.add(
            responses.GET,
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            json={'error': 'API Error'},
            status=500
        )
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            bitcoin = BitcoinAPIManager(config)
            
            data = bitcoin.get_data()
            assert data['status'] == 'error'
            assert 'error' in data


class TestCalendarAPIManager:
    """Test the Calendar API manager."""
    
    def test_init(self, temp_dir):
        """Test CalendarAPIManager initialization."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            calendar = CalendarAPIManager(config)
            assert calendar.config == config
            assert calendar.cache_key == 'calendar'
    
    def test_no_credentials_handling(self, temp_dir):
        """Test calendar API without credentials."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            calendar = CalendarAPIManager(config)
            
            data = calendar.get_data()
            # Should handle missing credentials gracefully
            assert 'status' in data
    
    @patch('api.calendar_api.build')
    @patch('api.calendar_api.InstalledAppFlow')
    def test_mock_calendar_events(self, mock_flow, mock_build, temp_dir, mock_credentials_json):
        """Test calendar API with mocked Google API."""
        env_content = f"GOOGLE_CALENDAR_CREDENTIALS_FILE={mock_credentials_json}"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        # Mock Google API service
        mock_service = Mock()
        mock_events = Mock()
        mock_events.list().execute.return_value = {
            'items': [
                {
                    'summary': 'Test Event',
                    'start': {'dateTime': '2023-12-25T10:00:00Z'},
                    'end': {'dateTime': '2023-12-25T11:00:00Z'}
                }
            ]
        }
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.path.exists', return_value=True):
            config = ConfigManager()
            calendar = CalendarAPIManager(config)
            
            data = calendar.get_data()
            assert 'events' in data or 'status' in data 