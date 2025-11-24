#!/bin/bash

echo "🍓 Deploying Butler to Raspberry Pi..."

# Check if we're on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "❌ This script should only be run on Raspberry Pi"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo ./scripts/deploy_rpi.sh"
    exit 1
fi

echo "🔧 Optimizing system for Butler..."

# Set CPU governor to performance for better voice processing
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Increase audio buffer size for better performance
echo "🔊 Optimizing audio settings..."
cat > /etc/asound.conf << 'EOL'
pcm.!default {
    type asym
    playback.pcm "plug:dmix"
    capture.pcm "plug:dsnoop"
}
EOL

# Setup systemd service
echo "📦 Creating systemd service..."
cat > /etc/systemd/system/butler.service << 'EOL'
[Unit]
Description=Butler Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/butler-voice-assistant
Environment=PATH=/home/pi/butler-voice-assistant/butler_env/bin
ExecStart=/home/pi/butler-voice-assistant/butler_env/bin/python src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable butler.service

echo "✅ Butler deployed successfully!"
echo "🚀 To start Butler: sudo systemctl start butler"
echo "📊 To view logs: sudo journalctl -u butler -f"