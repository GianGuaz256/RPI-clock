"""
Integration tests for the Raspberry Pi Dashboard.

These tests verify that components work together correctly and test
the complete application workflow.
"""

import os
import time
import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
import pygame
from config.config_manager import ConfigManager
from core.dashboard_app import DashboardApp
from api.weather_api import WeatherAPIManager
from api.bitcoin_api import BitcoinAPIManager


class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    def test_config_priority_chain(self, temp_dir):
        """Test configuration priority: env vars > JSON > defaults."""
        # Create JSON config
        json_content = '''
        {
            "weather": {
                "api_key": "json_key",
                "city": "JsonCity,JC"
            },
            "app": {
                "fps": 25
            }
        }
        '''
        with open(os.path.join(temp_dir, 'config.json'), 'w') as f:
            f.write(json_content)
        
        # Create .env file that overrides some JSON values
        env_content = """
        WEATHER_API_KEY=env_key
        WEATHER_CITY=EnvCity,EC
        # Note: fps not set in env, should come from JSON
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            
            # Env should override JSON
            assert config.get('weather.api_key') == 'env_key'
            assert config.get('weather.city') == 'EnvCity,EC'
            
            # JSON should be used when env doesn't have the value
            assert config.get('app.fps') == 25
            
            # Defaults should be used when neither has the value
            assert config.get('weather.units') == 'metric'
    
    def test_complete_configuration_workflow(self, temp_dir, mock_credentials_json):
        """Test complete configuration setup with all components."""
        env_content = f"""
        # Weather configuration
        WEATHER_API_KEY=test_weather_key
        WEATHER_CITY=TestCity,TC
        WEATHER_MOCK_MODE=false
        
        # Google Calendar
        GOOGLE_CALENDAR_CREDENTIALS_FILE={mock_credentials_json}
        
        # App settings
        API_UPDATE_INTERVAL=60
        DEBUG_MODE=true
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            
            # Verify all configurations are loaded correctly
            status = config.get_config_status()
            assert status['env_file_exists'] is True
            assert status['weather_api_configured'] is True
            
            # Verify runtime constants
            from utils.constants import get_runtime_constants
            runtime = get_runtime_constants(config)
            assert runtime['UPDATE_INTERVAL'] == 60
            assert runtime['DEBUG_MODE'] is True


class TestAPIIntegration:
    """Test API managers working together."""
    
    def test_weather_api_with_config_integration(self, temp_dir):
        """Test WeatherAPI with ConfigManager integration."""
        env_content = """
        WEATHER_MOCK_MODE=true
        WEATHER_MOCK_TEMPERATURE=20.5
        WEATHER_CITY=IntegrationCity,IC
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather_api = WeatherAPIManager(config)
            
            data = weather_api.get_data()
            
            assert data['data_source'] == 'mock_data'
            assert data['city'] == 'IntegrationCity'
            assert abs(data['temperature'] - 20.5) < 2.0  # Within variation range
    
    @responses.activate
    def test_multiple_api_managers(self, temp_dir, sample_weather_data, sample_bitcoin_data):
        """Test multiple API managers working simultaneously."""
        env_content = """
        WEATHER_API_KEY=test_key
        WEATHER_MOCK_MODE=false
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        # Mock both API responses
        responses.add(
            responses.GET,
            'https://api.openweathermap.org/data/2.5/weather',
            json=sample_weather_data,
            status=200
        )
        responses.add(
            responses.GET,
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            json=sample_bitcoin_data,
            status=200
        )
        responses.add(
            responses.GET,
            'https://blockchain.info/latestblock',
            json={'height': 800000, 'hash': 'abcd1234'},
            status=200
        )
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather_api = WeatherAPIManager(config)
            bitcoin_api = BitcoinAPIManager(config)
            
            weather_data = weather_api.get_data()
            bitcoin_data = bitcoin_api.get_data()
            
            assert weather_data['status'] == 'success'
            assert bitcoin_data['status'] == 'success'
            assert weather_data['temperature'] == 22.5
            assert bitcoin_data['price'] == 45000.50
    
    def test_api_caching_integration(self, temp_dir):
        """Test API caching across multiple requests."""
        env_content = "WEATHER_MOCK_MODE=true"
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            weather_api = WeatherAPIManager(config)
            
            # First request
            data1 = weather_api.get_data()
            
            # Second request (should be cached)
            data2 = weather_api.get_data()
            
            # Should get the same exact data (including timestamp)
            assert data1['last_updated'] == data2['last_updated']
            assert data1['temperature'] == data2['temperature']
            
            # Cache info should indicate data is fresh
            cache_info = weather_api.get_cache_info()
            assert cache_info['is_expired'] is False


class TestScreenIntegration:
    """Test screen components integration."""
    
    def test_screen_with_api_integration(self, temp_dir, mock_pygame):
        """Test screens working with their respective APIs."""
        env_content = """
        WEATHER_MOCK_MODE=true
        WEATHER_CITY=ScreenTest,ST
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.font.Font'):
            
            # Create mock app
            mock_app = Mock()
            mock_app.screen = mock_pygame
            mock_app.config_manager = ConfigManager()
            
            from screens.weather_screen import WeatherScreen
            weather_screen = WeatherScreen(mock_app)
            
            # Update should fetch data
            weather_screen.update()
            
            # Should be able to draw without errors
            weather_screen.draw(mock_pygame)
            
            # Verify API data is accessible
            data = weather_screen.weather_api.get_data()
            assert data['city'] == 'ScreenTest'
    
    def test_all_screens_initialization(self, temp_dir, mock_pygame):
        """Test that all screens can be initialized together."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.font.Font'):
            
            # Create mock app
            mock_app = Mock()
            mock_app.screen = mock_pygame
            mock_app.config_manager = ConfigManager()
            
            # Import all screen classes
            from screens.clock_calendar_screen import ClockCalendarScreen
            from screens.weather_screen import WeatherScreen
            from screens.bitcoin_screen import BitcoinScreen
            from screens.system_stats_screen import SystemStatsScreen
            
            # Initialize all screens
            screens = [
                ClockCalendarScreen(mock_app),
                WeatherScreen(mock_app),
                BitcoinScreen(mock_app),
                SystemStatsScreen(mock_app)
            ]
            
            # All screens should initialize without errors
            assert len(screens) == 4
            
            # All screens should have required methods
            for screen in screens:
                assert hasattr(screen, 'update')
                assert hasattr(screen, 'draw')
                assert hasattr(screen, 'get_screen_name')
                assert callable(screen.update)
                assert callable(screen.draw)


class TestFullApplicationIntegration:
    """Test the complete application workflow."""
    
    def test_app_initialization_workflow(self, temp_dir, mock_pygame):
        """Test complete application initialization."""
        env_content = """
        WEATHER_MOCK_MODE=true
        DEBUG_MODE=true
        APP_FPS=15
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            # Verify initialization
            assert app.config_manager is not None
            assert app.runtime_config is not None
            assert len(app.screens) == 4
            assert len(app.api_managers) > 0
            
            # Verify configuration loaded correctly
            assert app.runtime_config['DEBUG_MODE'] is True
            assert app.runtime_config['FPS'] == 15
    
    def test_screen_navigation_integration(self, temp_dir, mock_pygame):
        """Test screen navigation with touch events."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            initial_screen = app.current_screen_index
            
            # Simulate swipe right
            app._handle_swipe('swipe_right')
            new_screen = app.current_screen_index
            
            assert new_screen == (initial_screen + 1) % len(app.screens)
            
            # Get current screen and verify it's functional
            current_screen = app.get_current_screen()
            assert current_screen is not None
            
            # Screen should be able to update and draw
            current_screen.update()
            current_screen.draw(mock_pygame)
    
    def test_error_recovery_integration(self, temp_dir, mock_pygame):
        """Test application error recovery mechanisms."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            # Simulate API error in weather
            with patch.object(app.weather_api, 'get_data', 
                            return_value={'status': 'error', 'error': 'Test error'}):
                
                # Should still be able to get current screen and draw
                current_screen = app.get_current_screen()
                current_screen.update()
                current_screen.draw(mock_pygame)
                
                # App should still be functional
                app_status = app.get_app_status()
                assert app_status['running'] is True
    
    def test_configuration_reload_integration(self, temp_dir, mock_pygame):
        """Test configuration changes during runtime."""
        env_content = """
        WEATHER_MOCK_MODE=true
        TOUCH_SWIPE_THRESHOLD=100
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            # Initial threshold
            initial_threshold = app.touch_handler.swipe_threshold
            
            # Update configuration
            app.config_manager.set('app.touch_swipe_threshold', 150)
            app.touch_handler.update_config()
            
            # Should reflect new configuration
            new_threshold = app.touch_handler.swipe_threshold
            assert new_threshold != initial_threshold


class TestDataFlowIntegration:
    """Test data flow between components."""
    
    def test_config_to_api_to_screen_flow(self, temp_dir, mock_pygame):
        """Test data flowing from config through API to screen."""
        env_content = """
        WEATHER_MOCK_MODE=true
        WEATHER_MOCK_TEMPERATURE=25.0
        WEATHER_CITY=FlowTest,FT
        """
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.font.Font'):
            
            # Create config
            config = ConfigManager()
            
            # Create API with config
            weather_api = WeatherAPIManager(config)
            data = weather_api.get_data()
            
            # Create screen with API
            mock_app = Mock()
            mock_app.screen = mock_pygame
            mock_app.config_manager = config
            
            from screens.weather_screen import WeatherScreen
            screen = WeatherScreen(mock_app)
            
            # Data should flow through: config -> API -> screen
            screen_data = screen.weather_api.get_data()
            
            assert screen_data['city'] == 'FlowTest'
            assert abs(screen_data['temperature'] - 25.0) < 2.0
    
    def test_cache_persistence_across_components(self, temp_dir):
        """Test that cache persists across different component instances."""
        env_content = "WEATHER_MOCK_MODE=true"
        with open(os.path.join(temp_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            
            # Create first API instance and get data
            api1 = WeatherAPIManager(config)
            data1 = api1.get_data()
            
            # Create second API instance
            api2 = WeatherAPIManager(config)
            data2 = api2.get_data()
            
            # Should get cached data (same timestamp)
            assert data1['last_updated'] == data2['last_updated'] 