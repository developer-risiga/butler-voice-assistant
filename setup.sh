#!/bin/bash

echo "🚀 Setting up Butler Voice Assistant..."

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "📱 Detected Raspberry Pi"
    IS_RPI=true
else
    echo "💻 Detected regular Linux system"
    IS_RPI=false
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
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

# Setup audio (run audio setup script)
echo "🎵 Setting up audio..."
chmod +x scripts/setup_audio.sh
./scripts/setup_audio.sh

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv butler_env
source butler_env/bin/activate

# Upgrade pip and install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/cache data/audio data/logs models/rasa

# Download Whisper model
echo "🤖 Downloading Whisper model..."
python -c "import whisper; whisper.load_model('base')" || echo "Whisper model download failed, but continuing..."

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Copying environment template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Train initial Rasa model
echo "🧠 Training initial Rasa model..."
chmod +x scripts/train_rasa_model.sh
./scripts/train_rasa_model.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source butler_env/bin/activate"
echo "3. Run Butler: python src/main.py"
echo ""
echo "For hardware setup, see: docs/hardware_setup.md"