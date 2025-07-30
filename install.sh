#!/bin/bash

# Raspberry Pi Dashboard Installation Script
# Version 1.1 - Now with mock weather support for easy testing

set -e

echo "=========================================="
echo "Raspberry Pi Digital Dashboard Installer"
echo "Version 1.1"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi. Continuing anyway..."
fi

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-pygame \
    python3-requests \
    python3-psutil \
    git \
    build-essential \
    python3-dev

# Install Python packages
echo "Installing Python packages..."
pip3 install -r requirements.txt --break-system-packages

echo "✓ Dependencies installed"

# Create configuration from template
echo ""
echo "🔧 Setting up configuration..."

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "Creating .env file from template..."
        cp .env.template .env
        echo "✓ .env file created from template"
        echo ""
        echo "🧪 DEMO MODE ENABLED:"
        echo "   The app will use mock weather data by default"
        echo "   No API keys required for initial testing!"
        echo ""
        echo "📝 To use real weather data later:"
        echo "   1. Get a free API key from openweathermap.org"
        echo "   2. Edit .env and set: WEATHER_API_KEY=your_key_here"
        echo "   3. Set: WEATHER_MOCK_MODE=false"
    else
        echo "Warning: .env.template not found, creating basic .env..."
        cat > .env << 'EOF'
# Basic configuration for testing
WEATHER_MOCK_MODE=true
WEATHER_CITY=London,UK
WEATHER_UNITS=metric
DEBUG_MODE=false
EOF
        echo "✓ Basic .env file created"
    fi
else
    echo "✓ .env file already exists"
fi

# Backup existing config.json if it exists
if [ -f "config.json" ]; then
    echo "Backing up existing config.json..."
    cp config.json config.json.backup
    echo "✓ config.json backed up to config.json.backup"
    
    # Check if it contains API keys
    if grep -q "YOUR_OPENWEATHERMAP_API_KEY_HERE" config.json; then
        echo "📝 Note: config.json contains placeholder values"
    else
        echo "⚠️  Consider migrating API keys from config.json to .env for better security"
        echo "   Your existing config.json will still work as fallback"
    fi
fi

# Make the app executable
chmod +x app.py

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore file..."
    cat > .gitignore << 'GITEOF'
# Environment variables (contains sensitive API keys)
.env

# Google Calendar OAuth credentials and tokens
credentials.json
token.json

# Python cache files
__pycache__/
*.py[cod]
*$py.class

# Backup files
*.backup
*.bak
config.json.backup
GITEOF
    echo "✓ .gitignore created"
fi

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "🚀 READY TO RUN:"
echo "   python3 app.py"
echo ""
echo "🧪 DEMO MODE:"
echo "   • Mock weather data is enabled by default"
echo "   • No API keys required for testing"
echo "   • Perfect for development and demos"
echo ""
echo "🔐 FOR PRODUCTION USE:"
echo "1. Get a free OpenWeatherMap API key:"
echo "   https://openweathermap.org/api"
echo ""
echo "2. Edit .env file:"
echo "   nano .env"
echo ""
echo "3. Set your API key:"
echo "   WEATHER_API_KEY=your_actual_key_here"
echo "   WEATHER_MOCK_MODE=false"
echo ""
echo "4. Optional: Setup Google Calendar (see README.md)"
echo ""

# Check if --service flag is provided
if [[ "$1" == "--service" ]]; then
    echo "Setting up systemd service..."
    
    # Get current directory and user
    CURRENT_DIR=$(pwd)
    USER=$(whoami)
    
    # Create systemd service file
    sudo tee /etc/systemd/system/rpi-dashboard.service > /dev/null <<EOF
[Unit]
Description=Raspberry Pi Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable rpi-dashboard.service
    
    echo ""
    echo "✓ Service installed! You can now:"
    echo "  Start: sudo systemctl start rpi-dashboard"
    echo "  Stop:  sudo systemctl stop rpi-dashboard"
    echo "  Status: sudo systemctl status rpi-dashboard"
    echo "  Logs: journalctl -u rpi-dashboard -f"
    echo ""
    echo "⚠️  Make sure to configure .env before starting the service!"
fi

echo ""
echo "📖 For detailed setup instructions, see README.md"
echo "🔧 For troubleshooting, run with DEBUG_MODE=true in .env"
echo ""
echo "🎉 Happy dashboarding!"
echo ""
echo "💡 TIP: The app works immediately with mock data!"
echo "    Just run: python3 app.py" 