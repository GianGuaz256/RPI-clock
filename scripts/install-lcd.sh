#!/bin/bash

# Exit on any error
set -e

# Step 1: Update System and Enable Interfaces
echo "Updating system and enabling interfaces..."
sudo apt update && sudo apt upgrade -y || { echo "Update failed"; exit 1; }
sudo reboot

# Wait for reboot to complete (manual intervention or use a delay if automated)
echo "Please wait for the system to reboot and run the script again after login."
exit 0

# Note: Due to the reboot, the script will need to be rerun manually after this point.
# The following steps continue after the first reboot.

# Step 2: Configure raspi-config settings
echo "Configuring raspi-config settings..."
sudo raspi-config nonint do_spi 0  # Enable SPI
sudo raspi-config nonint do_gl_driver 2  # Select X11 (Legacy) to disable Wayland
sudo reboot

# Wait for reboot to complete (manual intervention or delay if automated)
echo "Please wait for the system to reboot and run the script again after login."
exit 0

# Note: Rerun the script after the second reboot to continue.

# Step 3: Configure Display in config.txt
echo "Configuring display in config.txt..."
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
else
    echo "Config file not found!"
    exit 1
fi

sudo sed -i '/^dtoverlay=vc4-kms-v3d/ s/^/#/' "$CONFIG_FILE"
sudo sed -i '/^dtoverlay=vc4-fkms-v3d/ s/^/#/' "$CONFIG_FILE"
echo "dtparam=spi=on" | sudo tee -a "$CONFIG_FILE" > /dev/null
echo "dtoverlay=piscreen,speed=18000000,drm" | sudo tee -a "$CONFIG_FILE" > /dev/null
echo "display_auto_detect=0" | sudo tee -a "$CONFIG_FILE" > /dev/null
sudo reboot

# Wait for reboot to complete (manual intervention or delay if automated)
echo "Please wait for the system to reboot and run the script again after login."
exit 0

# Note: Rerun the script after the third reboot to continue.

# Step 4: Set Up Touch Input
echo "Setting up touch input..."
sudo apt install xserver-xorg-input-evdev -y || { echo "evdev installation failed"; exit 1; }
sudo cp /usr/share/X11/xorg.conf.d/10-evdev.conf /usr/share/X11/xorg.conf.d/45-evdev.conf || { echo "Copy failed"; exit 1; }
sudo bash -c 'cat << EOF > /usr/share/X11/xorg.conf.d/45-evdev.conf
Section "InputClass"
    Identifier "evdev touchscreen catchall"
    MatchIsTouchscreen "on"
    MatchDevicePath "/dev/input/event*"
    Driver "evdev"
    Option "InvertX" "false"
    Option "InvertY" "true"
EndSection
EOF' || { echo "Touch config creation failed"; exit 1; }
sudo reboot

# Wait for reboot to complete (manual intervention or delay if automated)
echo "Please wait for the system to reboot and run the script again after login."
exit 0

# Note: Rerun the script after the fourth reboot to continue.

# Step 5: Calibrate Touch
echo "Calibrating touch input..."
sudo apt install xinput-calibrator -y || { echo "xinput-calibrator installation failed"; exit 1; }
echo "Please run 'DISPLAY=:0.0 xinput_calibrator' manually, follow the prompts, and note the calibration values."
echo "Then press Enter to continue after calibration is complete."
read -p "Press Enter to continue..."

# Create calibration config file with placeholder values (user to replace)
sudo bash -c 'cat << EOF > /usr/share/X11/xorg.conf.d/99-calibration.conf
Section "InputClass"
    Identifier "calibration"
    MatchProduct "ADS7846 Touchscreen"
    Option "Calibration" "3930 300 200 3720"  # Replace with your values
    Option "SwapAxes" "0"
EndSection
EOF' || { echo "Calibration config creation failed"; exit 1; }
sudo reboot

echo "Setup complete! The display should now work after reboot. If touch is inaccurate, adjust the calibration values in /usr/share/X11/xorg.conf.d/99-calibration.conf and reboot again."