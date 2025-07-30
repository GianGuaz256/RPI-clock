"""
Weather information screen for the Raspberry Pi Dashboard.
"""

from typing import Dict, Any
from screens.base_screen import BaseScreen
from api.weather_api import WeatherAPIManager
from utils.constants import WHITE, GREEN, GRAY, RED, SCREEN_WIDTH


class WeatherScreen(BaseScreen):
    """Display current weather conditions and forecast."""
    
    def __init__(self, app):
        """
        Initialize weather screen.
        
        Args:
            app: Reference to main application instance
        """
        super().__init__(app)
        self.weather_manager = WeatherAPIManager(app.config_manager)
    
    def update(self) -> None:
        """Update weather data (data is updated via background thread)."""
        # Data is updated automatically by the API manager's caching system
        pass
    
    def draw(self, screen) -> None:
        """
        Draw weather information screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.fill((0, 0, 0))  # Black background
        
        # Get weather data
        weather_data = self.weather_manager.get_data()
        status = weather_data.get('status', 'unknown')
        
        # Draw title (city name if available)
        city = weather_data.get('city', 'Weather')
        self.draw_title(screen, city, 30)
        
        if status in ['success', 'cached']:
            self._draw_weather_data(screen, weather_data)
        else:
            self._draw_error_state(screen, weather_data)
        
        # Draw status indicator
        self.draw_status_indicator(screen, status, (450, 20))
    
    def _draw_weather_data(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw weather conditions and information.
        
        Args:
            screen: Pygame surface to draw on
            data: Weather data dictionary
        """
        # Weather icon and condition
        icon = data.get('icon', '🌤️')
        condition = data.get('condition', 'Unknown')
        
        # Draw weather icon (large)
        try:
            # Try to render the emoji icon
            icon_surface = self.font_large.render(icon, True, WHITE)
            icon_rect = icon_surface.get_rect(center=(SCREEN_WIDTH // 2 - 60, 85))
            screen.blit(icon_surface, icon_rect)
        except:
            # Fallback if emoji rendering fails
            self.draw_text(screen, "☀", (SCREEN_WIDTH // 2 - 60, 85), 
                          self.font_large, WHITE, center=True)
        
        # Draw condition
        self.draw_text(screen, condition, (SCREEN_WIDTH // 2, 125), 
                      self.font_medium, WHITE, center=True)
        
        # Temperature (large, prominent)
        temp = data.get('temperature', 0)
        units = data.get('units', 'metric')
        temp_unit = '°C' if units == 'metric' else '°F'
        temp_text = f"{temp:.1f}{temp_unit}"
        
        self.draw_text(screen, temp_text, (SCREEN_WIDTH // 2, 170), 
                      self.font_large, WHITE, center=True)
        
        # Additional weather information
        self._draw_weather_details(screen, data)
        
        # Location and time info
        self._draw_location_info(screen, data)
    
    def _draw_weather_details(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw detailed weather information.
        
        Args:
            screen: Pygame surface to draw on
            data: Weather data dictionary
        """
        y_offset = 220
        
        # Humidity
        humidity = data.get('humidity', 0)
        self.draw_text(screen, f"Humidity: {humidity}%", (20, y_offset), 
                      self.font_small, WHITE)
        
        # Wind information
        wind_info = self._get_wind_info(data)
        self.draw_text(screen, f"Wind: {wind_info}", (20, y_offset + 20), 
                      self.font_small, WHITE)
        
        # Pressure (if available)
        pressure = data.get('pressure', 0)
        if pressure > 0:
            self.draw_text(screen, f"Pressure: {pressure} hPa", (20, y_offset + 40), 
                          self.font_small, WHITE)
        
        # Visibility (if available)
        visibility = data.get('visibility', 0)
        if visibility > 0:
            self.draw_text(screen, f"Visibility: {visibility:.1f} km", (250, y_offset), 
                          self.font_small, WHITE)
    
    def _get_wind_info(self, data: Dict[str, Any]) -> str:
        """
        Format wind information string.
        
        Args:
            data: Weather data dictionary
            
        Returns:
            Formatted wind information string
        """
        wind_speed = data.get('wind_speed', 0)
        wind_direction = data.get('wind_direction', 0)
        units = data.get('units', 'metric')
        
        # Format speed with appropriate units
        speed_unit = 'm/s' if units == 'metric' else 'mph'
        speed_text = f"{wind_speed:.1f} {speed_unit}"
        
        # Convert wind direction to compass direction
        direction = self._degrees_to_compass(wind_direction)
        
        return f"{speed_text} {direction}"
    
    def _degrees_to_compass(self, degrees: float) -> str:
        """
        Convert wind direction degrees to compass direction.
        
        Args:
            degrees: Wind direction in degrees
            
        Returns:
            Compass direction string
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        
        # Calculate index based on degrees
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]
    
    def _draw_location_info(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw location and update information.
        
        Args:
            screen: Pygame surface to draw on
            data: Weather data dictionary
        """
        # Country info
        country = data.get('country', '')
        if country:
            location_text = f"{data.get('city', '')}, {country}"
            self.draw_text(screen, location_text, (SCREEN_WIDTH // 2, 55), 
                          self.font_small, GRAY, center=True)
        
        # Last update time
        last_updated = data.get('last_updated', 0)
        if last_updated:
            import time
            age_seconds = int(time.time() - last_updated)
            
            if age_seconds < 60:
                age_text = f"Updated {age_seconds}s ago"
            elif age_seconds < 3600:
                age_text = f"Updated {age_seconds // 60}m ago"
            else:
                age_text = f"Updated {age_seconds // 3600}h ago"
            
            self.draw_text(screen, age_text, (SCREEN_WIDTH // 2, 300), 
                          self.font_small, GRAY, center=True)
    
    def _draw_error_state(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw error state when weather data is unavailable.
        
        Args:
            screen: Pygame surface to draw on
            data: Weather data dictionary with error information
        """
        # Error message
        self.draw_text(screen, "Weather Unavailable", (SCREEN_WIDTH // 2, 120), 
                      self.font_medium, RED, center=True)
        
        # Error details
        error_msg = data.get('error', 'Unknown error')
        
        # Truncate long error messages
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."
        
        self.draw_text(screen, error_msg, (SCREEN_WIDTH // 2, 160), 
                      self.font_small, RED, center=True)
        
        # Helpful messages
        if 'API key' in error_msg:
            self.draw_text(screen, "Check API key configuration", (SCREEN_WIDTH // 2, 200), 
                          self.font_small, GRAY, center=True)
        else:
            self.draw_text(screen, "Check internet connection", (SCREEN_WIDTH // 2, 200), 
                          self.font_small, GRAY, center=True)
    
    def get_weather_summary(self) -> Dict[str, Any]:
        """
        Get weather data summary.
        
        Returns:
            Dictionary with weather information summary
        """
        data = self.weather_manager.get_data()
        
        return {
            'temperature': data.get('temperature', 0),
            'temperature_formatted': data.get('temperature_formatted', '0°C'),
            'condition': data.get('condition', 'Unknown'),
            'humidity': data.get('humidity', 0),
            'wind_speed': data.get('wind_speed', 0),
            'city': data.get('city', 'Unknown'),
            'status': data.get('status', 'unknown'),
            'last_updated': data.get('last_updated', 0),
            'is_available': data.get('status') in ['success', 'cached']
        }
    
    def force_refresh(self) -> bool:
        """
        Force refresh of weather data.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            data = self.weather_manager.get_data(force_refresh=True)
            return data.get('status') == 'success'
        except Exception as e:
            print(f"Error forcing weather data refresh: {e}")
            return False 