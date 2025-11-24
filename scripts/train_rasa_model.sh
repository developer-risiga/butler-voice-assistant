#!/bin/bash

echo "🧠 Training Rasa NLU model..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual environment not activated. Please run: source butler_env/bin/activate"
    exit 1
fi

# Check if Rasa is installed
if ! command -v rasa &> /dev/null; then
    echo "❌ Rasa not found. Installing..."
    pip install rasa
fi

# Create models directory if it doesn't exist
mkdir -p models/rasa

# Train the model
echo "📚 Training model from src/nlu/rasa_config/"
rasa train --data src/nlu/rasa_config/ --domain src/nlu/rasa_config/domain.yml --out models/rasa/

if [ $? -eq 0 ]; then
    echo "✅ Rasa model trained successfully!"
    echo "📁 Model saved to: models/rasa/"
else
    echo "❌ Rasa model training failed!"
    exit 1
fi