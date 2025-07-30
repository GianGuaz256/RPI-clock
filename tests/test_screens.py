"""
Tests for screen components (BaseScreen and all derived screens).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pygame
from config.config_manager import ConfigManager
from screens.base_screen import BaseScreen
from screens.clock_calendar_screen import ClockCalendarScreen
from screens.weather_screen import WeatherScreen
from screens.bitcoin_screen import BitcoinScreen
from screens.system_stats_screen import SystemStatsScreen
import os


class TestBaseScreen:
    """Test the base screen functionality."""
    
    def test_init(self, mock_pygame):
        """Test BaseScreen initialization."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        mock_app.config_manager = Mock()
        
        screen = BaseScreen(mock_app)
        assert screen.app == mock_app
        assert screen.screen_width == 480
        assert screen.screen_height == 320
    
    def test_font_initialization(self, mock_pygame):
        """Test font initialization in BaseScreen."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        mock_app.config_manager = Mock()
        
        with patch('pygame.font.Font') as mock_font:
            screen = BaseScreen(mock_app)
            # Should initialize fonts
            assert mock_font.called
    
    def test_abstract_methods(self, mock_pygame):
        """Test that abstract methods raise NotImplementedError."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        mock_app.config_manager = Mock()
        
        screen = BaseScreen(mock_app)
        
        with pytest.raises(NotImplementedError):
            screen.update()
        
        with pytest.raises(NotImplementedError):
            screen.draw(mock_pygame)
    
    def test_helper_methods(self, mock_pygame):
        """Test BaseScreen helper methods."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        mock_app.config_manager = Mock()
        
        with patch('pygame.font.Font'):
            screen = BaseScreen(mock_app)
            
            # Test draw_text method
            screen.draw_text(mock_pygame, "Test", 24, (255, 255, 255), (100, 100))
            
            # Test draw_title method
            screen.draw_title(mock_pygame, "Title", 50)
            
            # Test draw_error_message method
            screen.draw_error_message(mock_pygame, "Error message")
    
    def test_lifecycle_methods(self, mock_pygame):
        """Test screen lifecycle methods."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        mock_app.config_manager = Mock()
        
        screen = BaseScreen(mock_app)
        
        # These should not raise exceptions
        screen.activate()
        screen.deactivate()


class TestClockCalendarScreen:
    """Test the Clock and Calendar screen."""
    
    def test_init(self, mock_pygame, temp_dir):
        """Test ClockCalendarScreen initialization."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = ClockCalendarScreen(mock_app)
                assert screen.app == mock_app
                assert screen.calendar_api is not None
    
    def test_update(self, mock_pygame, temp_dir):
        """Test clock/calendar screen update logic."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = ClockCalendarScreen(mock_app)
                
                # Should not raise exception
                screen.update()
    
    def test_draw(self, mock_pygame, temp_dir):
        """Test clock/calendar screen drawing."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'), \
                 patch('time.strftime', return_value='12:34:56'), \
                 patch('time.time', return_value=1234567890):
                screen = ClockCalendarScreen(mock_app)
                
                # Should not raise exception
                screen.draw(mock_pygame)
                
                # Verify screen.fill was called
                mock_pygame.fill.assert_called()
    
    def test_get_screen_name(self, mock_pygame, temp_dir):
        """Test getting screen name."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = ClockCalendarScreen(mock_app)
                assert screen.get_screen_name() == "Clock & Calendar"


class TestWeatherScreen:
    """Test the Weather screen."""
    
    def test_init(self, mock_pygame, temp_dir):
        """Test WeatherScreen initialization."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = WeatherScreen(mock_app)
                assert screen.app == mock_app
                assert screen.weather_api is not None
    
    def test_update(self, mock_pygame, temp_dir):
        """Test weather screen update logic."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = WeatherScreen(mock_app)
                
                # Should not raise exception
                screen.update()
    
    def test_draw_with_mock_data(self, mock_pygame, temp_dir):
        """Test weather screen drawing with mock data."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        # Set up mock weather data
        env_content = "WEATHER_MOCK_MODE=true\nWEATHER_CITY=TestCity,TC"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = WeatherScreen(mock_app)
                
                # Should not raise exception
                screen.draw(mock_pygame)
                
                # Verify screen.fill was called
                mock_pygame.fill.assert_called()
    
    def test_get_screen_name(self, mock_pygame, temp_dir):
        """Test getting screen name."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = WeatherScreen(mock_app)
                assert screen.get_screen_name() == "Weather"


class TestBitcoinScreen:
    """Test the Bitcoin screen."""
    
    def test_init(self, mock_pygame, temp_dir):
        """Test BitcoinScreen initialization."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = BitcoinScreen(mock_app)
                assert screen.app == mock_app
                assert screen.bitcoin_api is not None
    
    def test_update(self, mock_pygame, temp_dir):
        """Test bitcoin screen update logic."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = BitcoinScreen(mock_app)
                
                # Should not raise exception
                screen.update()
    
    def test_draw(self, mock_pygame, temp_dir):
        """Test bitcoin screen drawing."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = BitcoinScreen(mock_app)
                
                # Should not raise exception
                screen.draw(mock_pygame)
                
                # Verify screen.fill was called
                mock_pygame.fill.assert_called()
    
    def test_get_screen_name(self, mock_pygame, temp_dir):
        """Test getting screen name."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = BitcoinScreen(mock_app)
                assert screen.get_screen_name() == "Bitcoin"


class TestSystemStatsScreen:
    """Test the System Stats screen."""
    
    def test_init(self, mock_pygame, temp_dir):
        """Test SystemStatsScreen initialization."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = SystemStatsScreen(mock_app)
                assert screen.app == mock_app
    
    def test_update(self, mock_pygame, temp_dir):
        """Test system stats screen update logic."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'), \
                 patch('utils.system_monitor.SystemMonitor.get_cpu_temperature', return_value=45.2), \
                 patch('utils.system_monitor.SystemMonitor.get_cpu_usage', return_value=15.5):
                screen = SystemStatsScreen(mock_app)
                
                # Should not raise exception
                screen.update()
    
    def test_draw(self, mock_pygame, temp_dir, mock_system_stats):
        """Test system stats screen drawing."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'), \
                 patch('utils.system_monitor.SystemMonitor.get_complete_stats', 
                       return_value=mock_system_stats):
                screen = SystemStatsScreen(mock_app)
                
                # Should not raise exception
                screen.draw(mock_pygame)
                
                # Verify screen.fill was called
                mock_pygame.fill.assert_called()
    
    def test_get_screen_name(self, mock_pygame, temp_dir):
        """Test getting screen name."""
        mock_app = Mock()
        mock_app.screen = mock_pygame
        
        with patch('os.getcwd', return_value=temp_dir):
            mock_app.config_manager = ConfigManager()
            
            with patch('pygame.font.Font'):
                screen = SystemStatsScreen(mock_app)
                assert screen.get_screen_name() == "System Stats" 