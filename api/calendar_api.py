"""
Google Calendar API management with OAuth2 authentication.
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from api.base_api import BaseAPIManager
from config.config_manager import ConfigManager

# Google Calendar imports with fallback
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False


class CalendarAPIManager(BaseAPIManager):
    """Manages Google Calendar API integration with OAuth2."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize Calendar API manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(cache_key='calendar_events')
        self.config = config_manager
        self.service = None
        self.is_available = GOOGLE_CALENDAR_AVAILABLE
        
        if self.is_available:
            self._setup_calendar()
    
    def _setup_calendar(self) -> None:
        """
        Set up Google Calendar API authentication.
        
        Note:
            Requires credentials.json file in the application directory.
            See README.md for setup instructions.
        """
        try:
            creds = None
            token_file = self.config.get('google_calendar.token_file')
            credentials_file = self.config.get('google_calendar.credentials_file')
            scopes = self.config.get('google_calendar.scopes')
            
            # Load existing token
            if os.path.exists(token_file):
                try:
                    creds = Credentials.from_authorized_user_file(token_file, scopes)
                except Exception as e:
                    print(f"Error loading existing token: {e}")
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Error refreshing token: {e}")
                        creds = None
                
                if not creds:
                    if not os.path.exists(credentials_file):
                        print(f"Google Calendar credentials file {credentials_file} not found.")
                        print("Please follow setup instructions in README.md")
                        return
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        print(f"Error setting up Google Calendar OAuth: {e}")
                        return
                
                # Save credentials for next run
                try:
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Error saving token: {e}")
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=creds)
            print("Google Calendar API initialized successfully")
            
        except Exception as e:
            print(f"Error setting up Google Calendar: {e}")
            self.service = None
    
    def _fetch_data(self) -> Dict[str, Any]:
        """
        Fetch upcoming calendar events.
        
        Returns:
            Dictionary containing formatted calendar events
            
        Raises:
            Exception: On API failure or if service unavailable
        """
        if not self.service:
            raise Exception("Google Calendar service not available")
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,  # Fetch more than needed for filtering
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        formatted_events = []
        
        for event in events:
            try:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_data = self._format_event(event, start)
                formatted_events.append(event_data)
            except Exception as e:
                print(f"Error formatting event: {e}")
                continue
        
        return {
            'events': formatted_events,
            'total_events': len(formatted_events)
        }
    
    def _format_event(self, event: Dict[str, Any], start_time_str: str) -> Dict[str, Any]:
        """
        Format a calendar event for display.
        
        Args:
            event: Raw event data from API
            start_time_str: Start time string from event
            
        Returns:
            Formatted event dictionary
        """
        if 'T' in start_time_str:  # DateTime format
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            time_str = start_time.strftime('%H:%M')
            date_str = start_time.strftime('%d/%m')
            is_all_day = False
        else:  # Date only format (all-day event)
            start_time = datetime.fromisoformat(start_time_str)
            time_str = 'All day'
            date_str = start_time.strftime('%d/%m')
            is_all_day = True
        
        return {
            'title': event.get('summary', 'No title')[:50],  # Truncate long titles
            'description': event.get('description', '')[:100],  # Truncate long descriptions
            'time': time_str,
            'date': date_str,
            'start_datetime': start_time,
            'is_all_day': is_all_day,
            'location': event.get('location', ''),
            'url': event.get('htmlLink', '')
        }
    
    def get_upcoming_events(self, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of formatted event dictionaries
        """
        if not self.is_available or not self.service:
            return []
        
        data = self.get_data()
        events = data.get('events', [])
        return events[:max_results]
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """
        Get events for today only.
        
        Returns:
            List of today's events
        """
        events = self.get_upcoming_events(10)  # Get more events to filter
        today = datetime.now().date()
        
        today_events = []
        for event in events:
            event_date = event['start_datetime'].date()
            if event_date == today:
                today_events.append(event)
        
        return today_events
    
    def is_configured(self) -> bool:
        """
        Check if Google Calendar is properly configured.
        
        Returns:
            True if configured and working, False otherwise
        """
        return self.is_available and self.service is not None
    
    def get_status(self) -> str:
        """
        Get API status.
        
        Returns:
            Status string ('success', 'cached', 'error', 'unavailable')
        """
        if not self.is_available:
            return 'unavailable'
        
        if not self.service:
            return 'error'
        
        data = self.get_data()
        return data.get('status', 'unknown') 