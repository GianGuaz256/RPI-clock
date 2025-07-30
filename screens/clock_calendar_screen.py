"""
Clock and Calendar screen for the Raspberry Pi Dashboard.
"""

import time
from datetime import datetime
from typing import List, Dict, Any
from screens.base_screen import BaseScreen
from api.calendar_api import CalendarAPIManager
from utils.constants import WHITE, GREEN, GRAY, SCREEN_WIDTH


class ClockCalendarScreen(BaseScreen):
    """Display current time, date, and upcoming calendar events."""
    
    def __init__(self, app):
        """
        Initialize clock and calendar screen.
        
        Args:
            app: Reference to main application instance
        """
        super().__init__(app)
        self.calendar_manager = CalendarAPIManager(app.config_manager)
        self.last_calendar_update = 0
        self.calendar_update_interval = 300  # 5 minutes
        
    def update(self) -> None:
        """Update screen data (calendar events are updated via background thread)."""
        current_time = time.time()
        
        # Update calendar data periodically
        if current_time - self.last_calendar_update > self.calendar_update_interval:
            if self.calendar_manager.is_configured():
                try:
                    # Force refresh calendar data
                    self.calendar_manager.get_data(force_refresh=True)
                except Exception as e:
                    print(f"Error updating calendar: {e}")
            self.last_calendar_update = current_time
        
        self.last_update = current_time
    
    def draw(self, screen) -> None:
        """
        Draw clock and calendar screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.fill((0, 0, 0))  # Black background
        
        # Get current time and date
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%d/%m/%Y')
        day_str = now.strftime('%A')
        
        # Draw time (large, centered)
        self.draw_text(screen, time_str, (SCREEN_WIDTH // 2, 80), 
                      self.font_large, WHITE, center=True)
        
        # Draw date
        self.draw_text(screen, date_str, (SCREEN_WIDTH // 2, 130), 
                      self.font_medium, WHITE, center=True)
        
        # Draw day of week
        self.draw_text(screen, day_str, (SCREEN_WIDTH // 2, 155), 
                      self.font_small, GRAY, center=True)
        
        # Draw calendar events
        self._draw_calendar_events(screen)
        
        # Draw status indicator
        self._draw_calendar_status(screen)
    
    def _draw_calendar_events(self, screen) -> None:
        """
        Draw upcoming calendar events.
        
        Args:
            screen: Pygame surface to draw on
        """
        y_offset = 185
        
        if not self.calendar_manager.is_configured():
            self.draw_text(screen, "Google Calendar not configured", 
                          (20, y_offset), self.font_small, GRAY)
            return
        
        try:
            events = self.calendar_manager.get_upcoming_events(max_results=3)
            
            if events:
                # Title
                self.draw_text(screen, "Upcoming Events:", (20, y_offset), 
                              self.font_medium, GREEN)
                y_offset += 30
                
                # Draw events
                for event in events:
                    self._draw_single_event(screen, event, y_offset)
                    y_offset += 25
                    
                    # Stop if we're running out of space
                    if y_offset > 280:
                        break
            else:
                self.draw_text(screen, "No upcoming events", (20, y_offset), 
                              self.font_medium, GRAY)
        except Exception as e:
            self.draw_text(screen, f"Calendar error: {str(e)[:30]}...", 
                          (20, y_offset), self.font_small, (255, 100, 100))
    
    def _draw_single_event(self, screen, event: Dict[str, Any], y_pos: int) -> None:
        """
        Draw a single calendar event.
        
        Args:
            screen: Pygame surface to draw on
            event: Event data dictionary
            y_pos: Y position to draw at
        """
        # Format event text
        title = event.get('title', 'No title')
        time_str = event.get('time', '')
        date_str = event.get('date', '')
        
        # Truncate title if too long
        max_title_length = 35
        if len(title) > max_title_length:
            title = title[:max_title_length - 3] + "..."
        
        # Create event line
        if event.get('is_all_day'):
            event_text = f"{date_str} - {title}"
        else:
            event_text = f"{date_str} {time_str} - {title}"
        
        # Draw event
        self.draw_text(screen, event_text, (25, y_pos), self.font_small, WHITE)
        
        # Draw location if available
        location = event.get('location', '')
        if location and len(location) < 30:
            self.draw_text(screen, f"  @ {location}", (25, y_pos + 12), 
                          self.font_small, GRAY)
    
    def _draw_calendar_status(self, screen) -> None:
        """
        Draw calendar API status indicator.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.calendar_manager.is_configured():
            status = self.calendar_manager.get_status()
        else:
            status = 'error'
        
        self.draw_status_indicator(screen, status, (450, 20))
    
    def get_current_time_info(self) -> Dict[str, str]:
        """
        Get current time information.
        
        Returns:
            Dictionary with time information
        """
        now = datetime.now()
        return {
            'time': now.strftime('%H:%M:%S'),
            'date': now.strftime('%d/%m/%Y'),
            'day': now.strftime('%A'),
            'timestamp': now.isoformat()
        }
    
    def get_calendar_info(self) -> Dict[str, Any]:
        """
        Get calendar status and event information.
        
        Returns:
            Dictionary with calendar information
        """
        if not self.calendar_manager.is_configured():
            return {
                'configured': False,
                'status': 'not_configured',
                'events': []
            }
        
        events = self.calendar_manager.get_upcoming_events(max_results=5)
        return {
            'configured': True,
            'status': self.calendar_manager.get_status(),
            'events': events,
            'event_count': len(events)
        } 