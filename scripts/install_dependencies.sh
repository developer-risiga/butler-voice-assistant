#!/bin/bash

echo "📦 Installing Butler dependencies..."

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "📱 Detected Raspberry Pi"
    IS_RPI=true
else
    echo "💻 Detected regular Linux system"
    IS_RPI=false
fi

# Install system dependencies
echo "🔧 Installing system packages..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    pulseaudio \
    pulseaudio-utils

# For Raspberry Pi, install additional dependencies
if [ "$IS_RPI" = true ]; then
    echo "🍓 Installing Raspberry Pi specific dependencies..."
    sudo apt install -y \
        python3-rpi.gpio \
        python3-gpiozero
fi

echo "✅ System dependencies installed successfully!"