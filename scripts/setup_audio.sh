#!/bin/bash

echo "🎵 Configuring audio system..."

# Configure PulseAudio for better performance
if command -v pulseaudio >/dev/null 2>&1; then
    echo "Configuring PulseAudio..."
    # Start PulseAudio if not running
    pulseaudio --check || pulseaudio --start
    
    # Set better latency settings
    echo "default-fragments = 8" | tee -a ~/.config/pulse/daemon.conf
    echo "default-fragment-size-msec = 10" | tee -a ~/.config/pulse/daemon.conf
fi

# Test audio devices
echo "Testing audio devices..."
echo "Input devices:"
arecord -l || echo "arecord not available"

echo "Output devices:"
aplay -l || echo "aplay not available"

# Create asoundrc configuration
if [ ! -f ~/.asoundrc ]; then
    echo "Creating ALSA configuration..."
    cat > ~/.asoundrc << 'EOL'
pcm.!default {
    type asym
    playback.pcm "plug:dmix"
    capture.pcm "plug:dsnoop"
}
EOL
fi

echo "✅ Audio setup complete!"