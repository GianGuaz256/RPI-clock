"""
Weather API management for OpenWeatherMap integration with mock data support.
"""

import time
import random
from typing import Dict, Any
from api.base_api import BaseAPIManager
from utils.constants import API_ENDPOINTS, WEATHER_ICONS, MOCK_WEATHER_DATA
from config.config_manager import ConfigManager


class WeatherAPIManager(BaseAPIManager):
    """Manages weather data from OpenWeatherMap API with mock data fallback."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize Weather API manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(cache_key='weather')
        self.config = config_manager
        self._mock_data_index = 0
        self._last_mock_change = time.time()
    
    def _fetch_data(self) -> Dict[str, Any]:
        """
        Fetch weather data from OpenWeatherMap or return mock data.
        
        Returns:
            Dictionary containing weather information
            
        Raises:
            Exception: On API failure (unless using mock mode)
        """
        api_key = self.config.get('weather.api_key')
        use_mock = self.config.get('weather.mock_mode', True)
        
        # Use mock data if no API key or mock mode is explicitly enabled
        if not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY_HERE" or use_mock:
            return self._get_mock_weather_data()
        
        # Try real API
        try:
            return self._fetch_real_weather_data()
        except Exception as e:
            # Fall back to mock data if real API fails
            print(f"Weather API failed, using mock data: {e}")
            return self._get_mock_weather_data()
    
    def _fetch_real_weather_data(self) -> Dict[str, Any]:
        """
        Fetch weather data from OpenWeatherMap API.
        
        Returns:
            Dictionary containing real weather information
            
        Raises:
            Exception: On API failure or missing configuration
        """
        api_key = self.config.get('weather.api_key')
        city = self.config.get('weather.city', 'London,UK')
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
            'sunset': data['sys']['sunset'],
            'status': 'success',
            'data_source': 'openweathermap_api'
        }
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """
        Generate mock weather data for testing purposes.
        
        Returns:
            Dictionary containing mock weather information
        """
        # Change mock data every 2 minutes to simulate variety
        current_time = time.time()
        if current_time - self._last_mock_change > 120:  # 2 minutes
            self._mock_data_index = (self._mock_data_index + 1) % len(MOCK_WEATHER_DATA)
            self._last_mock_change = current_time
        
        # Get base mock data
        mock_data = MOCK_WEATHER_DATA[self._mock_data_index].copy()
        
        # Add some configuration-based customization
        city = self.config.get('weather.city', 'Demo City,UK')
        units = self.config.get('weather.units', 'metric')
        
        # Allow customization via environment variables
        temperature = float(self.config.get('weather.mock_temperature', mock_data['temperature']))
        condition = self.config.get('weather.mock_condition', mock_data['condition'])
        humidity = int(self.config.get('weather.mock_humidity', mock_data['humidity']))
        wind_speed = float(self.config.get('weather.mock_wind_speed', mock_data['wind_speed']))
        
        # Add some random variation to make it more realistic
        temp_variation = random.uniform(-1.5, 1.5)
        humidity_variation = random.randint(-5, 5)
        wind_variation = random.uniform(-0.5, 0.5)
        
        final_temp = temperature + temp_variation
        final_humidity = max(0, min(100, humidity + humidity_variation))
        final_wind = max(0, wind_speed + wind_variation)
        
        return {
            'temperature': final_temp,
            'temperature_formatted': f"{final_temp:.1f}°{'C' if units == 'metric' else 'F'}",
            'condition': condition,
            'condition_code': condition,
            'humidity': final_humidity,
            'pressure': random.randint(1010, 1020),
            'wind_speed': final_wind,
            'wind_direction': random.randint(0, 360),
            'visibility': random.uniform(8, 15),
            'icon': self._get_weather_icon(condition),
            'units': units,
            'city': city.split(',')[0],
            'country': city.split(',')[1] if ',' in city else 'XX',
            'sunrise': int(time.time()) - 3600,  # 1 hour ago
            'sunset': int(time.time()) + 7200,   # 2 hours from now
            'status': 'mock',
            'data_source': 'mock_data'
        }
    
    def _get_weather_icon(self, condition: str) -> str:
        """
        Get Unicode weather icon for condition.
        
        Args:
            condition: Weather condition from API or mock data
            
        Returns:
            Unicode weather icon
        """
        return WEATHER_ICONS.get(condition, '🌤️')
    
    def is_using_mock_data(self) -> bool:
        """
        Check if currently using mock data.
        
        Returns:
            True if using mock data, False if using real API
        """
        data = self.get_data()
        return data.get('data_source') == 'mock_data'
    
    def get_data_source_info(self) -> str:
        """
        Get information about the current data source.
        
        Returns:
            Human-readable string about data source
        """
        if self.is_using_mock_data():
            return "🧪 Mock Weather Data"
        else:
            return "🌐 OpenWeatherMap API"
    
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
            Status string ('success', 'cached', 'error', 'mock')
        """
        data = self.get_data()
        return data.get('status', 'unknown') 