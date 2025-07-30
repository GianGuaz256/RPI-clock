# Raspberry Pi Digital Dashboard

A modular, multi-screen touchscreen dashboard for Raspberry Pi featuring clock/calendar, Bitcoin info, weather, and system stats with swipe navigation.

## 🏗️ **New Modular Architecture (v2.0)**

The codebase has been completely refactored into a maintainable, extensible modular structure:

```
RPI-screen-util/
├── app.py                 # Main entry point
├── .env.template          # Environment variables template
├── config/
│   └── config_manager.py  # Configuration management
├── core/
│   ├── dashboard_app.py   # Main application class
│   ├── cache.py          # Thread-safe data caching
│   └── touch_handler.py  # Touch input and gesture handling
├── api/
│   ├── base_api.py       # Base API manager class
│   ├── bitcoin_api.py    # Bitcoin price and blockchain API
│   ├── weather_api.py    # OpenWeatherMap API integration
│   └── calendar_api.py   # Google Calendar API with OAuth
├── screens/
│   ├── base_screen.py    # Base screen class with common functionality
│   ├── clock_calendar_screen.py  # Time, date, and calendar events
│   ├── bitcoin_screen.py         # Bitcoin price and blockchain info
│   ├── weather_screen.py         # Weather conditions and forecast
│   └── system_stats_screen.py    # Raspberry Pi system monitoring
├── utils/
│   ├── constants.py      # Configuration constants and settings
│   └── system_monitor.py # Hardware monitoring utilities
└── config.json          # Fallback configuration (deprecated)
```

### 🚀 **Benefits of the New Architecture:**

- **🔧 Maintainable**: Each component has a single responsibility
- **📈 Extensible**: Easy to add new screens, APIs, or features
- **🧪 Testable**: Modular components can be tested independently
- **🔒 Robust**: Better error handling and data caching
- **📚 Documented**: Comprehensive docstrings and type hints
- **🔐 Secure**: Environment variable configuration for sensitive data

## 🔐 **Environment Variable Configuration (Recommended)**

The dashboard now supports secure configuration via environment variables, which is the **preferred method** for managing API keys and sensitive settings.

### **Quick Start with Environment Variables:**

1. **Copy the template**:
   ```bash
   cp .env.template .env
   ```

2. **Edit your `.env` file**:
   ```bash
   nano .env
   ```

3. **Add your API keys**:
   ```env
   # Weather API (required)
   WEATHER_API_KEY=your_actual_openweathermap_key
   WEATHER_CITY=YourCity,CountryCode
   
   # Optional: Customize behavior
   API_UPDATE_INTERVAL=300
   TOUCH_SWIPE_THRESHOLD=100
   DEBUG_MODE=false
   ```

4. **Run the dashboard**:
   ```bash
   python3 app.py
   ```

### **Available Environment Variables:**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `WEATHER_API_KEY` | OpenWeatherMap API key | - | `abc123def456` |
| `WEATHER_CITY` | City for weather data | `London,UK` | `New York,US` |
| `WEATHER_UNITS` | Temperature units | `metric` | `imperial` |
| `API_UPDATE_INTERVAL` | Data refresh interval (seconds) | `300` | `600` |
| `SYSTEM_UPDATE_INTERVAL` | System stats interval (seconds) | `5` | `10` |
| `TOUCH_SWIPE_THRESHOLD` | Swipe sensitivity (pixels) | `100` | `150` |
| `APP_FPS` | Application frame rate | `30` | `60` |
| `DEBUG_MODE` | Enable debug logging | `false` | `true` |

**Complete list in `.env.template`**

## Hardware Requirements

- Raspberry Pi 4 or 5 (recommended)
- 480x320 touchscreen LCD display (Waveshare or similar)
- Internet connection for API data
- MicroSD card (16GB+ recommended)

## Software Requirements

- Raspberry Pi OS (Debian-based)
- Python 3.7+
- Internet connection for API services

## Installation

### 1. Update your Raspberry Pi
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install system dependencies
```bash
sudo apt install python3-pip python3-pygame git -y
```

### 3. Clone and setup the application
```bash
git clone <your-repo-url>
cd RPI-screen-util
pip3 install -r requirements.txt
```

### 4. Configure your display (if needed)
For some displays, you may need to edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add display-specific configuration (consult your display's documentation).

### 5. 🔐 **Configuration Setup (New Method)**

#### **Option A: Environment Variables (Recommended)**

1. **Create your `.env` file**:
   ```bash
   cp .env.template .env
   ```

2. **Get your OpenWeatherMap API key**:
   - Sign up for free at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your API key

3. **Edit `.env` with your settings**:
   ```bash
   nano .env
   ```
   
   Update these essential settings:
   ```env
   WEATHER_API_KEY=your_actual_api_key_here
   WEATHER_CITY=YourCity,CountryCode
   WEATHER_UNITS=metric
   ```

4. **Optional: Google Calendar** (see Google Calendar setup below)

#### **Option B: JSON Configuration (Legacy)**
If you prefer the old method or need compatibility:
- Edit `config.json` and replace `YOUR_OPENWEATHERMAP_API_KEY_HERE` with your key
- Update the city in `config.json` to your location

#### **Google Calendar Setup (Optional)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` and place in the app directory
6. **For .env users**: Set `GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json`
7. Run the app for first-time authorization

## Usage

### Run the application
```bash
python3 app.py
```

**The app will show you the configuration status on startup:**
```
==================================================
CONFIGURATION STATUS
==================================================
Configuration source: environment variables
Environment file (.env): ✓
Weather API configured: ✓
Google Calendar configured: ✓
...
```

### Navigation
- **Touch**: Swipe left/right to change screens
- **Keyboard** (development): Use arrow keys, ESC to exit, R to refresh
- **Debug mode**: Press C to show configuration (when `DEBUG_MODE=true`)

### Screens
1. **Clock & Calendar**: Current time, date, and upcoming Google Calendar events
2. **Bitcoin Info**: Current BTC price and blockchain stats
3. **Weather**: Current weather conditions for your location
4. **System Stats**: Raspberry Pi CPU, memory, temperature, and uptime

### Auto-start on boot (optional)
Create a systemd service:
```bash
sudo nano /etc/systemd/system/rpi-dashboard.service
```

Add:
```ini
[Unit]
Description=Raspberry Pi Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RPI-screen-util
ExecStart=/usr/bin/python3 /home/pi/RPI-screen-util/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rpi-dashboard.service
sudo systemctl start rpi-dashboard.service
```

## 🎯 **Features**

- **🎮 Touch Navigation**: Intuitive swipe gestures for screen navigation
- **⏰ Real-time Updates**: Clock updates every second, data every 5 minutes
- **🛡️ Error Handling**: Graceful fallbacks when APIs are unavailable
- **💾 Smart Caching**: Displays last known data when offline
- **⚡ Low Power**: Optimized for continuous operation
- **📊 Status Indicators**: Visual indicators for data freshness
- **🔧 Extensible**: Easy to add new screens and features
- **🔐 Secure Configuration**: Environment variables for sensitive data
- **🐞 Debug Mode**: Comprehensive logging and diagnostics

## 🔄 **Migration from config.json to .env**

If you're currently using `config.json`, here's how to migrate:

### **Automatic Migration Helper:**
```bash
# The app will warn you about JSON configuration
python3 app.py
# Look for: "⚠️ Using JSON configuration. Consider migrating to .env file"
```

### **Manual Migration:**

1. **Create `.env` from template**:
   ```bash
   cp .env.template .env
   ```

2. **Transfer your settings**:
   ```bash
   # From config.json
   {
     "weather": {
       "api_key": "abc123",
       "city": "Paris,FR",
       "units": "metric"
     }
   }
   
   # To .env
   WEATHER_API_KEY=abc123
   WEATHER_CITY=Paris,FR
   WEATHER_UNITS=metric
   ```

3. **Test the migration**:
   ```bash
   python3 app.py
   # Should show: "Configuration source: environment variables"
   ```

4. **Remove old config** (optional):
   ```bash
   mv config.json config.json.backup
   ```

### **Configuration Priority:**
The system loads configuration in this order (later sources override earlier):
1. **Default values** (hardcoded)
2. **JSON file** (`config.json`) - for backwards compatibility
3. **Environment variables** (`.env` file) - **takes precedence**

## 🎨 **Adding New Screens**

The modular architecture makes it easy to add new screens:

1. **Create a new screen class** in `screens/`:
```python
from screens.base_screen import BaseScreen

class MyNewScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
    
    def update(self):
        # Update screen data
        pass
    
    def draw(self, screen):
        # Draw screen content
        screen.fill((0, 0, 0))
        self.draw_title(screen, "My New Screen", 30)
```

2. **Add to the main app** in `core/dashboard_app.py`:
```python
from screens.my_new_screen import MyNewScreen

# In _init_screens method:
self.screens = [
    ClockCalendarScreen(self),
    BitcoinScreen(self),
    WeatherScreen(self),
    SystemStatsScreen(self),
    MyNewScreen(self)  # Add your new screen
]
```

## 🔧 **Adding New APIs**

To add new API integrations:

1. **Create API manager** in `api/`:
```python
from api.base_api import BaseAPIManager

class MyAPIManager(BaseAPIManager):
    def __init__(self, config_manager):
        super().__init__(cache_key='my_api')
        self.config = config_manager
    
    def _fetch_data(self):
        # Implement API fetching logic
        return {"status": "success", "data": "..."}
```

2. **Add environment variables** to `.env.template`:
```env
# My New API Configuration
MY_API_KEY=your_api_key_here
MY_API_ENDPOINT=https://api.example.com
```

3. **Use in screens** as needed

## Troubleshooting

### Configuration Issues
- **Check configuration status**: The app shows detailed config info on startup
- **Missing .env**: Copy from `.env.template` and fill in your values
- **API keys**: Ensure your weather API key is valid and not expired
- **Debug mode**: Set `DEBUG_MODE=true` in `.env` for detailed logging

### Display Issues
- Ensure your display drivers are properly installed
- Check `/boot/config.txt` for display configuration
- Try running with `DISPLAY=:0 python3 app.py`

### API Issues
- Check internet connection
- Verify API keys in `.env` file (not `config.json`)
- Check console output for error messages

### Performance Issues
- Ensure adequate cooling for your Pi
- Monitor system stats screen for resource usage
- Adjust `APP_FPS` in `.env` to lower value for better performance
- Increase `API_UPDATE_INTERVAL` to reduce network requests

### Touch Issues
- Calibrate your touchscreen if needed
- Adjust `TOUCH_SWIPE_THRESHOLD` in `.env` for sensitivity
- Enable `DEBUG_MODE=true` to see touch events in console
- Try using keyboard navigation for testing

## Development

### Project Structure
The modular architecture separates concerns:

- **`core/`**: Core application logic and utilities
- **`screens/`**: Individual screen implementations
- **`api/`**: API managers for external data sources
- **`utils/`**: Utility functions and constants
- **`config/`**: Configuration management

### Configuration Development
- **Environment variables**: Preferred for all new settings
- **Runtime configuration**: Values can be changed via `.env` without code changes
- **Debug mode**: Set `DEBUG_MODE=true` for development
- **Configuration validation**: App checks and warns about missing settings

### Code Quality
- **Type Hints**: Full type annotations for better development experience
- **Docstrings**: Comprehensive documentation for all classes and methods
- **Error Handling**: Robust error handling with graceful fallbacks
- **Thread Safety**: Safe concurrent access to shared resources

## Migration from v1.0

If you're upgrading from the previous monolithic version:

1. **Backup your config**: `cp config.json config.json.backup`
2. **Update code**: The new modular version is in `app.py`
3. **Old version**: Available as `app_old.py` for reference
4. **Migrate to .env**: Use `cp .env.template .env` and migrate your settings
5. **Same APIs**: All existing functionality is preserved

## Security Best Practices

- **Never commit `.env`**: Your actual environment file contains sensitive API keys
- **Use `.env.template`**: Commit this template without real values
- **Migrate from JSON**: Move API keys from `config.json` to `.env`
- **Check warnings**: The app will warn about insecure configurations

## License

MIT License - feel free to modify and distribute.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository. 