"""
Weather display screen showing current conditions.
"""

from typing import Tuple
import pygame
from screens.base_screen import BaseScreen
from api.weather_api import WeatherAPIManager
from utils.constants import FONT_LARGE, FONT_MEDIUM, FONT_SMALL, WHITE, BLUE, GREEN, GRAY


class WeatherScreen(BaseScreen):
    """Screen displaying current weather conditions."""
    
    def __init__(self, app):
        """
        Initialize weather screen.
        
        Args:
            app: Main application instance
        """
        super().__init__(app)
        self.weather_api = WeatherAPIManager(app.config_manager)
    
    def update(self):
        """Update weather data."""
        self.weather_api.update()
    
    def draw(self, screen: pygame.Surface):
        """
        Draw weather information on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear screen
        screen.fill((0, 0, 0))
        
        try:
            # Get weather data
            data = self.weather_api.get_data()
            if not data:
                self.draw_error_message(screen, "No weather data available")
                return
            
            y_offset = 30
            
            # Title with data source indicator
            data_source = self.weather_api.get_data_source_info()
            title = f"Weather - {data_source}"
            self.draw_title(screen, title, y_offset, size=FONT_SMALL)
            y_offset += 40
            
            # Location
            city = data.get('city', 'Unknown')
            country = data.get('country', '')
            location = f"{city}, {country}" if country else city
            self.draw_text(screen, location, FONT_MEDIUM, WHITE, 
                          (self.screen_width // 2, y_offset), center=True)
            y_offset += 45
            
            # Main temperature and icon
            temp = self.weather_api.get_formatted_temperature()
            icon = self.weather_api.get_icon()
            temp_text = f"{icon} {temp}"
            self.draw_text(screen, temp_text, FONT_LARGE, WHITE,
                          (self.screen_width // 2, y_offset), center=True)
            y_offset += 60
            
            # Weather condition
            condition = self.weather_api.get_condition()
            self.draw_text(screen, condition, FONT_MEDIUM, BLUE,
                          (self.screen_width // 2, y_offset), center=True)
            y_offset += 40
            
            # Additional details in two columns
            self._draw_weather_details(screen, data, y_offset)
            
            # Status indicator
            self._draw_status_indicator(screen)
            
        except Exception as e:
            error_msg = f"Weather error: {str(e)}"
            self.draw_error_message(screen, error_msg)
    
    def _draw_weather_details(self, screen: pygame.Surface, data: dict, y_offset: int):
        """
        Draw detailed weather information in two columns.
        
        Args:
            screen: Pygame surface to draw on
            data: Weather data dictionary
            y_offset: Vertical offset to start drawing
        """
        # Left column
        left_x = 80
        right_x = 320
        
        # Humidity
        humidity = data.get('humidity', 0)
        self.draw_text(screen, f"Humidity: {humidity}%", FONT_SMALL, WHITE,
                      (left_x, y_offset))
        
        # Wind
        wind_info = self.weather_api.get_wind_info()
        wind_text = f"Wind: {wind_info['speed_formatted']}"
        self.draw_text(screen, wind_text, FONT_SMALL, WHITE,
                      (right_x, y_offset))
        
        y_offset += 30
        
        # Pressure
        pressure = data.get('pressure', 0)
        if pressure > 0:
            self.draw_text(screen, f"Pressure: {pressure} hPa", FONT_SMALL, WHITE,
                          (left_x, y_offset))
        
        # Visibility
        visibility = data.get('visibility', 0)
        if visibility > 0:
            self.draw_text(screen, f"Visibility: {visibility:.1f} km", FONT_SMALL, WHITE,
                          (right_x, y_offset))
    
    def _draw_status_indicator(self, screen: pygame.Surface):
        """
        Draw status indicator showing data freshness and source.
        
        Args:
            screen: Pygame surface to draw on
        """
        status = self.weather_api.get_status()
        age = self.weather_api.get_cache_age()
        
        # Determine status color and text
        if status == 'mock':
            status_color = BLUE
            status_text = f"🧪 DEMO MODE"
        elif status == 'success':
            status_color = GREEN
            status_text = f"✓ Live ({age:.0f}s ago)"
        elif status == 'cached':
            status_color = BLUE
            status_text = f"⏱ Cached ({age:.0f}s ago)"
        else:
            status_color = GRAY
            status_text = f"⚠ {status}"
        
        # Draw status in bottom right
        status_pos = (self.screen_width - 10, self.screen_height - 25)
        self.draw_text(screen, status_text, FONT_SMALL, status_color,
                      status_pos, align='right')
    
    def get_screen_name(self) -> str:
        """
        Get display name for this screen.
        
        Returns:
            Screen name string
        """
        return "Weather" 