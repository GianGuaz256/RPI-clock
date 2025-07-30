#!/usr/bin/env python3
"""
Raspberry Pi Digital Dashboard - Main Entry Point
================================================

A modular, multi-screen touchscreen dashboard for Raspberry Pi with 480x320 LCD display.
Features clock/calendar, Bitcoin info, weather, and system stats with swipe navigation.

This is the main entry point that uses the new modular architecture for better
maintainability and extensibility.

Hardware Requirements:
- Raspberry Pi (4 or 5 recommended)
- 480x320 touchscreen LCD (Waveshare or similar)
- Internet connection for API data

Software Requirements:
- Python 3.7+
- pygame, requests, google-api-python-client, oauth2client, psutil

Usage:
    python3 app.py

For installation and setup instructions, see README.md
"""

import sys
import traceback
from core.dashboard_app import DashboardApp


def main():
    """
    Main entry point for the Raspberry Pi Dashboard application.
    
    This function initializes and runs the dashboard application with proper
    error handling and graceful shutdown.
    """
    print("=" * 60)
    print("Raspberry Pi Digital Dashboard")
    print("Version: 2.0 (Modular Architecture)")
    print("=" * 60)
    
    try:
        # Create and run the dashboard application
        app = DashboardApp()
        app.run()
        
    except ImportError as e:
        print(f"Import Error: Missing required dependency")
        print(f"Error details: {e}")
        print("\nPlease install required dependencies:")
        print("  pip3 install -r requirements.txt")
        print("\nOr run the installation script:")
        print("  ./install.sh")
        sys.exit(1)
        
    except PermissionError as e:
        print(f"Permission Error: {e}")
        print("\nThis may be due to:")
        print("- Missing permissions for display access")
        print("- GPIO access restrictions")
        print("\nTry running with appropriate permissions or check your setup.")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
        print("\nThis may be due to:")
        print("- Missing configuration files")
        print("- Missing API credentials")
        print("\nCheck README.md for setup instructions.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user (Ctrl+C)")
        print("Dashboard stopped gracefully.")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        print("\nIf this error persists, please check:")
        print("1. All dependencies are installed")
        print("2. Configuration files are properly set up")
        print("3. Hardware connections are correct")
        print("4. System has sufficient resources")
        sys.exit(1)


def show_help():
    """Display help information about the application."""
    help_text = """
Raspberry Pi Digital Dashboard
=============================

A touch-enabled dashboard with multiple information screens.

NAVIGATION:
  Touch:     Swipe left/right to change screens
  Keyboard:  Arrow keys to navigate, ESC to exit
  
SCREENS:
  1. Clock & Calendar - Time, date, and upcoming Google Calendar events
  2. Bitcoin Info     - Current BTC price and blockchain statistics  
  3. Weather          - Current weather conditions for your location
  4. System Stats     - Raspberry Pi CPU, memory, temperature, uptime

CONFIGURATION:
  Edit config.json to customize:
  - Weather location and API key
  - Google Calendar settings
  - Display preferences

FILES:
  config.json       - Main configuration file
  credentials.json  - Google Calendar credentials (optional)
  requirements.txt  - Python dependencies

For detailed setup instructions, see README.md
"""
    print(help_text)


if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    # Run the main application
    main() 