#!/bin/bash

# Raspberry Pi Dashboard Installation Script
# Automates the setup process for the digital dashboard

set -e

echo "=========================================="
echo "Raspberry Pi Digital Dashboard Installer"
echo "Version 2.0 - Environment Variable Support"
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
sudo apt install python3-pip python3-pygame python3-dev python3-setuptools git -y

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Handle configuration setup
echo ""
echo "Setting up configuration..."

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "Creating .env file from template..."
        cp .env.template .env
        echo "✓ .env file created from template"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
        echo "   nano .env"
    else
        echo "Warning: .env.template not found"
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
        echo "📝 Note: config.json contains placeholder API key"
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
    cat > .gitignore << 'EOF'
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
EOF
    echo "✓ .gitignore created"
fi

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "🔐 CONFIGURATION SETUP:"
echo "1. Edit .env file and add your API keys:"
echo "   nano .env"
echo ""
echo "   Required: WEATHER_API_KEY (get from openweathermap.org)"
echo "   Optional: WEATHER_CITY, API_UPDATE_INTERVAL, etc."
echo ""
echo "2. For Google Calendar (optional):"
echo "   - Follow instructions in README.md"
echo "   - Place credentials.json in this directory"
echo "   - Set GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json in .env"
echo ""
echo "🚀 TESTING:"
echo "   python3 app.py"
echo ""
echo "📊 The app will show configuration status on startup"
echo ""

# Check if --service flag is provided
if [[ "$1" == "--service" ]]; then
    echo "Setting up systemd service..."
    
    # Get current directory
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