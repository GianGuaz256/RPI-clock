"""
Weather API management for OpenWeatherMap integration.
"""

from typing import Dict, Any
from api.base_api import BaseAPIManager
from utils.constants import API_ENDPOINTS, WEATHER_ICONS
from config.config_manager import ConfigManager


class WeatherAPIManager(BaseAPIManager):
    """Manages weather data from OpenWeatherMap API."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize Weather API manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(cache_key='weather')
        self.config = config_manager
    
    def _fetch_data(self) -> Dict[str, Any]:
        """
        Fetch weather data from OpenWeatherMap.
        
        Returns:
            Dictionary containing weather information
            
        Raises:
            Exception: On API failure or missing configuration
        """
        api_key = self.config.get('weather.api_key')
        city = self.config.get('weather.city')
        units = self.config.get('weather.units', 'metric')
        
        if not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY_HERE":
            raise Exception('OpenWeatherMap API key not configured')
        
        # Build request parameters
        params = {
            'q': city,
            'appid': api_key,
            'units': units
        }
        
        # Make API request
        response = self._make_request(API_ENDPOINTS['weather'], params)
        data = response.json()
        
        # Extract and format weather data
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description'].title()
        
        return {
            'temperature': data['main']['temp'],
            'temperature_formatted': f"{data['main']['temp']:.1f}°{'C' if units == 'metric' else 'F'}",
            'condition': weather_desc,
            'condition_code': weather_main,
            'humidity': data['main']['humidity'],
            'pressure': data['main'].get('pressure', 0),
            'wind_speed': data['wind'].get('speed', 0),
            'wind_direction': data['wind'].get('deg', 0),
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'icon': self._get_weather_icon(weather_main),
            'units': units,
            'city': data['name'],
            'country': data['sys']['country'],
            'sunrise': data['sys']['sunrise'],
            'sunset': data['sys']['sunset']
        }
    
    def _get_weather_icon(self, condition: str) -> str:
        """
        Get Unicode weather icon for condition.
        
        Args:
            condition: Weather condition from API
            
        Returns:
            Unicode weather icon
        """
        return WEATHER_ICONS.get(condition, '🌤️')
    
    def get_temperature(self) -> float:
        """
        Get current temperature.
        
        Returns:
            Temperature value or 0 if unavailable
        """
        data = self.get_data()
        return data.get('temperature', 0)
    
    def get_formatted_temperature(self) -> str:
        """
        Get formatted temperature string.
        
        Returns:
            Formatted temperature string
        """
        data = self.get_data()
        return data.get('temperature_formatted', '0°C')
    
    def get_condition(self) -> str:
        """
        Get weather condition description.
        
        Returns:
            Weather condition string
        """
        data = self.get_data()
        return data.get('condition', 'Unknown')
    
    def get_icon(self) -> str:
        """
        Get weather icon.
        
        Returns:
            Unicode weather icon
        """
        data = self.get_data()
        return data.get('icon', '🌤️')
    
    def get_wind_info(self) -> Dict[str, Any]:
        """
        Get wind information.
        
        Returns:
            Dictionary with wind speed and direction
        """
        data = self.get_data()
        units = data.get('units', 'metric')
        speed_unit = 'm/s' if units == 'metric' else 'mph'
        
        return {
            'speed': data.get('wind_speed', 0),
            'direction': data.get('wind_direction', 0),
            'speed_formatted': f"{data.get('wind_speed', 0):.1f} {speed_unit}"
        }
    
    def get_status(self) -> str:
        """
        Get API status.
        
        Returns:
            Status string ('success', 'cached', 'error')
        """
        data = self.get_data()
        return data.get('status', 'unknown') 