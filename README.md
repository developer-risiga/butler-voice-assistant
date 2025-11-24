# Butler Voice Assistant 🤖

A voice-first AI assistant for service discovery and booking.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Microphone and speakers
- OpenAI API key

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_COMPANY/butler-voice-assistant.git
cd butler-voice-assistant

# Run setup
chmod +x setup.sh
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Train AI model
./scripts/train_rasa_model.sh

# Run Butler
source butler_env/bin/activate
python src/main.py