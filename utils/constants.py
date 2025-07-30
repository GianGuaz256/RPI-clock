"""
Constants and configuration values for the Raspberry Pi Dashboard.
"""

# Display Settings (these are defaults, can be overridden via config)
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
DEFAULT_FPS = 30

# Touch and Navigation (defaults, configurable via env vars)
DEFAULT_SWIPE_THRESHOLD = 100

# Update Intervals in seconds (defaults, configurable via env vars)
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes for API data
DEFAULT_CLOCK_UPDATE_INTERVAL = 1  # 1 second for clock updates
DEFAULT_SYSTEM_UPDATE_INTERVAL = 5  # 5 seconds for system stats
DEFAULT_AUTO_SWIPE_INTERVAL = 10  # 10 seconds for auto screen switching

# Colors (RGB tuples) - these remain constant
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Font Sizes - these remain constant
FONT_LARGE = 48
FONT_MEDIUM = 36
FONT_SMALL = 24

# Status Colors mapping
STATUS_COLORS = {
    'success': GREEN,
    'cached': BLUE,
    'error': RED,
    'unknown': GRAY,
    'warning': ORANGE,
    'critical': RED
}

# API Endpoints - these remain constant
API_ENDPOINTS = {
    'bitcoin_price': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
    'blockchain_info': 'https://blockchain.info/latestblock',
    'weather': 'https://api.openweathermap.org/data/2.5/weather',
    # Mempool.space API endpoints for comprehensive Bitcoin data
    'mempool_price': 'https://mempool.space/api/v1/prices',
    'mempool_difficulty': 'https://mempool.space/api/v1/difficulty-adjustment',
    'mempool_fees': 'https://mempool.space/api/v1/fees/recommended',
    'mempool_hashrate': 'https://mempool.space/api/v1/mining/hashrate/3d',
    'mempool_blocks': 'https://mempool.space/api/v1/blocks',
    'mempool_mempool': 'https://mempool.space/api/mempool',
    'mempool_lightning': 'https://mempool.space/api/v1/lightning/statistics/latest'
}

# Weather Icons Mapping - these remain constant
WEATHER_ICONS = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧️',
    'Drizzle': '🌦️',
    'Thunderstorm': '⛈️',
    'Snow': '❄️',
    'Mist': '��️',
    'Fog': '🌫️',
    'Partly Cloudy': '⛅',
    'Overcast': '☁️'
}

# Mock Weather Data for testing without API keys
MOCK_WEATHER_DATA = [
    {
        'condition': 'Clear',
        'temperature': 22.5,
        'humidity': 45,
        'wind_speed': 2.1,
        'description': 'Sunny and clear'
    },
    {
        'condition': 'Partly Cloudy',
        'temperature': 19.8,
        'humidity': 65,
        'wind_speed': 3.2,
        'description': 'Partly cloudy with light breeze'
    },
    {
        'condition': 'Clouds',
        'temperature': 16.4,
        'humidity': 78,
        'wind_speed': 4.5,
        'description': 'Cloudy with moderate wind'
    },
    {
        'condition': 'Rain',
        'temperature': 15.2,
        'humidity': 85,
        'wind_speed': 5.8,
        'description': 'Light rain showers'
    }
]

def get_runtime_constants(config_manager):
    """
    Get runtime constants from configuration manager.
    These values can be overridden by environment variables or config files.
    
    Args:
        config_manager: ConfigManager instance
        
    Returns:
        Dictionary with runtime configuration values
    """
    return {
        'FPS': config_manager.get('app.fps', DEFAULT_FPS),
        'SWIPE_THRESHOLD': config_manager.get('app.touch_swipe_threshold', DEFAULT_SWIPE_THRESHOLD),
        'UPDATE_INTERVAL': config_manager.get('app.api_update_interval', DEFAULT_UPDATE_INTERVAL),
        'CLOCK_UPDATE_INTERVAL': DEFAULT_CLOCK_UPDATE_INTERVAL,  # This stays at 1 second
        'SYSTEM_UPDATE_INTERVAL': config_manager.get('app.system_update_interval', DEFAULT_SYSTEM_UPDATE_INTERVAL),
        'AUTO_SWIPE_ENABLED': config_manager.get('app.auto_swipe_enabled', False),
        'AUTO_SWIPE_INTERVAL': config_manager.get('app.auto_swipe_interval', DEFAULT_AUTO_SWIPE_INTERVAL),
        'DEBUG_MODE': config_manager.get('app.debug_mode', False),
        'LOG_LEVEL': config_manager.get('app.log_level', 'INFO')
    } 