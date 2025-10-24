#!/bin/bash

echo "Setting up Local LLM on Apple Silicon..."


# Install Ollama, if not on your system
# curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models for Apple Silicon
ollama pull llama3.1:8b
ollama pull llama3.1:70b  # For higher quality when needed
ollama pull mistral:7b

echo "Local LLM setup complete!"
echo "Available models:"
ollama list