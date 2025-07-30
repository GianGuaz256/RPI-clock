"""
Main dashboard application for the Raspberry Pi Dashboard.
"""

import pygame
import sys
import threading
import time
import traceback
from typing import List, Optional

# Import core modules
from config.config_manager import ConfigManager
from core.touch_handler import TouchHandler
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, get_runtime_constants

# Import API managers
from api.bitcoin_api import BitcoinAPIManager
from api.weather_api import WeatherAPIManager
from api.calendar_api import CalendarAPIManager

# Import screens
from screens.clock_calendar_screen import ClockCalendarScreen
from screens.bitcoin_screen import BitcoinScreen
from screens.weather_screen import WeatherScreen
from screens.system_stats_screen import SystemStatsScreen


class DashboardApp:
    """Main application class for the Raspberry Pi Dashboard."""
    
    def __init__(self):
        """Initialize the dashboard application."""
        print("Initializing Raspberry Pi Dashboard...")
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        
        # Get runtime constants from configuration
        self.runtime_config = get_runtime_constants(self.config_manager)
        
        # Show configuration status
        self._show_config_status()
        
        # Initialize Pygame
        self._init_pygame()
        
        # Initialize core components
        self.clock = pygame.time.Clock()
        self.touch_handler = TouchHandler(self.config_manager)
        
        # Initialize API managers
        self._init_api_managers()
        
        # Initialize screens
        self._init_screens()
        
        # Application state
        self.running = True
        self.current_screen_index = 0
        self.last_api_update = 0
        
        # Start background update thread
        self._start_background_updates()
        
        print(f"Dashboard initialized successfully!")
        print(f"Screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"Available screens: {len(self.screens)}")
    
    def _show_config_status(self) -> None:
        """Display configuration status and warnings."""
        status = self.config_manager.get_config_status()
        warnings = self.config_manager.validate_configuration()
        
        print("\n" + "="*50)
        print("CONFIGURATION STATUS")
        print("="*50)
        print(f"Configuration source: {status['config_sources']}")
        print(f"Environment file (.env): {'✓' if status['env_file_exists'] else '✗'}")
        print(f"JSON config file: {'✓' if status['json_file_exists'] else '✗'}")
        print(f"python-dotenv available: {'✓' if status['dotenv_available'] else '✗'}")
        print(f"Weather API configured: {'✓' if status['weather_api_configured'] else '✗'}")
        print(f"Google Calendar configured: {'✓' if status['google_calendar_configured'] else '✗'}")
        
        # Show runtime configuration
        print(f"\nRuntime Settings:")
        print(f"  FPS: {self.runtime_config['FPS']}")
        print(f"  Swipe threshold: {self.runtime_config['SWIPE_THRESHOLD']}px")
        print(f"  API update interval: {self.runtime_config['UPDATE_INTERVAL']}s")
        print(f"  System update interval: {self.runtime_config['SYSTEM_UPDATE_INTERVAL']}s")
        print(f"  Debug mode: {self.runtime_config['DEBUG_MODE']}")
        
        # Show warnings
        if warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")
        
        # Show helpful information
        if not status['env_file_exists']:
            print(f"\n💡 TIP: Create a .env file for better configuration management.")
            print(f"    Copy .env.template to .env and add your API keys.")
        
        print("="*50 + "\n")
    
    def _init_pygame(self) -> None:
        """Initialize Pygame and display."""
        pygame.init()
        
        # Set up display (try fullscreen first, fallback to windowed)
        try:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), 
                pygame.FULLSCREEN
            )
            print("Display initialized in fullscreen mode")
        except pygame.error:
            # Fallback for development/testing
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Display initialized in windowed mode (fallback)")
        
        pygame.display.set_caption("Raspberry Pi Dashboard")
        pygame.mouse.set_visible(False)  # Hide mouse cursor for touch interface
    
    def _init_api_managers(self) -> None:
        """Initialize API managers for data fetching."""
        self.bitcoin_api = BitcoinAPIManager()
        self.weather_api = WeatherAPIManager(self.config_manager)
        self.calendar_api = CalendarAPIManager(self.config_manager)
        
        print("API managers initialized")
    
    def _init_screens(self) -> None:
        """Initialize all dashboard screens."""
        self.screens = [
            ClockCalendarScreen(self),
            BitcoinScreen(self),
            WeatherScreen(self),
            SystemStatsScreen(self)
        ]
        
        # Activate the first screen
        if self.screens:
            self.screens[0].activate()
        
        print(f"Initialized {len(self.screens)} screens")
    
    def _start_background_updates(self) -> None:
        """Start background thread for periodic API updates."""
        self.update_thread = threading.Thread(
            target=self._background_update_loop, 
            daemon=True
        )
        self.update_thread.start()
        print("Background update thread started")
    
    def _background_update_loop(self) -> None:
        """Background thread loop for updating API data."""
        while self.running:
            try:
                current_time = time.time()
                
                # Update API data based on configured interval
                update_interval = self.runtime_config['UPDATE_INTERVAL']
                if current_time - self.last_api_update > update_interval:
                    if self.runtime_config['DEBUG_MODE']:
                        print("Updating API data in background...")
                    
                    # Update all API data
                    self._update_api_data()
                    
                    self.last_api_update = current_time
                    if self.runtime_config['DEBUG_MODE']:
                        print("Background API update completed")
                
                # Sleep for 30 seconds before checking again
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in background update: {e}")
                if self.runtime_config['DEBUG_MODE']:
                    traceback.print_exc()
                time.sleep(60)  # Wait longer on error
    
    def _update_api_data(self) -> None:
        """Update data from all API sources."""
        try:
            # Update Bitcoin data
            self.bitcoin_api.get_data(force_refresh=True)
        except Exception as e:
            print(f"Error updating Bitcoin data: {e}")
            if self.runtime_config['DEBUG_MODE']:
                traceback.print_exc()
        
        try:
            # Update weather data
            self.weather_api.get_data(force_refresh=True)
        except Exception as e:
            print(f"Error updating weather data: {e}")
            if self.runtime_config['DEBUG_MODE']:
                traceback.print_exc()
        
        try:
            # Update calendar data
            if self.calendar_api.is_configured():
                self.calendar_api.get_data(force_refresh=True)
        except Exception as e:
            print(f"Error updating calendar data: {e}")
            if self.runtime_config['DEBUG_MODE']:
                traceback.print_exc()
    
    def handle_events(self) -> bool:
        """
        Handle Pygame events including touch input and keyboard.
        
        Returns:
            False if app should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                return self._handle_keyboard_input(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button (touch start)
                    self.touch_handler.handle_touch_start(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button (touch end)
                    swipe = self.touch_handler.handle_touch_end(event.pos)
                    if swipe:
                        self._handle_swipe(swipe)
        
        return True
    
    def _handle_keyboard_input(self, event) -> bool:
        """
        Handle keyboard input events.
        
        Args:
            event: Pygame keyboard event
            
        Returns:
            False if app should quit, True otherwise
        """
        if event.key == pygame.K_ESCAPE:
            # Emergency exit for development
            return False
        elif event.key == pygame.K_LEFT:
            # Navigate to previous screen
            self.previous_screen()
        elif event.key == pygame.K_RIGHT:
            # Navigate to next screen
            self.next_screen()
        elif event.key == pygame.K_r:
            # Force refresh current screen data
            self._force_refresh_current_screen()
        elif event.key == pygame.K_SPACE:
            # Show current screen info
            self._show_screen_info()
        elif event.key == pygame.K_c and self.runtime_config['DEBUG_MODE']:
            # Show configuration info (debug mode only)
            self._show_config_info()
        
        return True
    
    def _handle_swipe(self, swipe_direction: str) -> None:
        """
        Handle swipe gesture navigation.
        
        Args:
            swipe_direction: Direction of swipe ('swipe_left' or 'swipe_right')
        """
        if swipe_direction == 'swipe_left':
            self.next_screen()
        elif swipe_direction == 'swipe_right':
            self.previous_screen()
    
    def next_screen(self) -> None:
        """Navigate to the next screen."""
        if not self.screens:
            return
        
        # Deactivate current screen
        self.screens[self.current_screen_index].deactivate()
        
        # Move to next screen (wrap around)
        self.current_screen_index = (self.current_screen_index + 1) % len(self.screens)
        
        # Activate new screen
        self.screens[self.current_screen_index].activate()
        
        print(f"Switched to screen {self.current_screen_index + 1}/{len(self.screens)}: "
              f"{self.screens[self.current_screen_index].name}")
    
    def previous_screen(self) -> None:
        """Navigate to the previous screen."""
        if not self.screens:
            return
        
        # Deactivate current screen
        self.screens[self.current_screen_index].deactivate()
        
        # Move to previous screen (wrap around)
        self.current_screen_index = (self.current_screen_index - 1) % len(self.screens)
        
        # Activate new screen
        self.screens[self.current_screen_index].activate()
        
        print(f"Switched to screen {self.current_screen_index + 1}/{len(self.screens)}: "
              f"{self.screens[self.current_screen_index].name}")
    
    def _force_refresh_current_screen(self) -> None:
        """Force refresh data for the current screen."""
        current_screen = self.screens[self.current_screen_index]
        print(f"Force refreshing data for {current_screen.name}")
        
        # Trigger API data refresh based on screen type
        if isinstance(current_screen, BitcoinScreen):
            current_screen.force_refresh()
        elif isinstance(current_screen, WeatherScreen):
            current_screen.force_refresh()
        else:
            # For other screens, trigger general API update
            self._update_api_data()
    
    def _show_screen_info(self) -> None:
        """Show information about the current screen (development helper)."""
        current_screen = self.screens[self.current_screen_index]
        print(f"Current screen: {current_screen.name}")
        print(f"Screen {self.current_screen_index + 1} of {len(self.screens)}")
    
    def _show_config_info(self) -> None:
        """Show detailed configuration information (debug mode)."""
        print("\n" + "="*40)
        print("CURRENT CONFIGURATION")
        print("="*40)
        
        # Show all configuration sections
        for section in ['weather', 'display', 'google_calendar', 'app']:
            section_config = self.config_manager.get_section(section)
            if section_config:
                print(f"\n[{section}]")
                for key, value in section_config.items():
                    # Hide sensitive values
                    if 'key' in key.lower() or 'secret' in key.lower():
                        display_value = '***' if value else 'not set'
                    else:
                        display_value = value
                    print(f"  {key}: {display_value}")
        
        print("="*40)
    
    def update(self) -> None:
        """Update the current screen and application state."""
        if self.screens:
            current_screen = self.screens[self.current_screen_index]
            current_screen.update()
    
    def draw(self) -> None:
        """Draw the current screen and UI elements."""
        if not self.screens:
            return
        
        # Draw current screen
        current_screen = self.screens[self.current_screen_index]
        current_screen.draw(self.screen)
        
        # Draw screen navigation indicators
        self._draw_screen_indicators()
        
        # Update display
        pygame.display.flip()
    
    def _draw_screen_indicators(self) -> None:
        """Draw screen navigation indicators at bottom of screen."""
        if len(self.screens) <= 1:
            return
        
        dot_radius = 4
        dot_spacing = 20
        dot_y = SCREEN_HEIGHT - 15
        
        # Calculate starting position to center dots
        total_width = (len(self.screens) - 1) * dot_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Draw dots for each screen
        for i in range(len(self.screens)):
            x = start_x + i * dot_spacing
            
            if i == self.current_screen_index:
                # Current screen - filled white circle
                pygame.draw.circle(self.screen, (255, 255, 255), (x, dot_y), dot_radius)
            else:
                # Other screens - gray outline
                pygame.draw.circle(self.screen, (128, 128, 128), (x, dot_y), dot_radius, 1)
    
    def run(self) -> None:
        """Main application loop."""
        print("Starting dashboard main loop...")
        
        try:
            while self.running:
                # Handle events
                if not self.handle_events():
                    break
                
                # Update application state
                self.update()
                
                # Draw everything
                self.draw()
                
                # Control frame rate using configured FPS
                self.clock.tick(self.runtime_config['FPS'])
        
        except KeyboardInterrupt:
            print("\nShutdown requested by user...")
        
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            traceback.print_exc()
        
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Clean shutdown of the application."""
        print("Shutting down dashboard...")
        
        # Stop background thread
        self.running = False
        
        # Wait for background thread to finish
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            print("Waiting for background thread to finish...")
            self.update_thread.join(timeout=2)
        
        # Cleanup Pygame
        pygame.quit()
        print("Dashboard shutdown complete")
    
    def get_app_status(self) -> dict:
        """
        Get application status information.
        
        Returns:
            Dictionary with app status
        """
        return {
            'running': self.running,
            'current_screen': self.current_screen_index,
            'total_screens': len(self.screens),
            'current_screen_name': self.screens[self.current_screen_index].name if self.screens else None,
            'runtime_config': self.runtime_config,
            'config_status': self.config_manager.get_config_status(),
            'api_managers': {
                'bitcoin': self.bitcoin_api.get_cache_info(),
                'weather': self.weather_api.get_cache_info(),
                'calendar': self.calendar_api.get_cache_info() if self.calendar_api.is_configured() else None
            }
        } 