#!/bin/bash

echo "=========================================="
echo "  Context-Aware Chatbot Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    echo "After installation, run:"
    echo "  ollama pull llama3.2"
    exit 1
fi

echo "✅ Ollama found: $(ollama --version)"

# Check if Ollama is running
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "⚠️  Ollama service is not running."
    echo "Please start Ollama with: ollama serve"
    echo "Or it will start automatically when you use it."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "=========================================="
    echo "  Next Steps:"
    echo "=========================================="
    echo ""
    echo "1. Ensure Ollama is running with a model:"
    echo "   ollama pull llama3.2"
    echo ""
    echo "2. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Run the chatbot in interactive mode:"
    echo "   python main.py interactive"
    echo ""
    echo "4. Or run automated tests:"
    echo "   python main.py test"
    echo ""
    echo "5. Or start the API server:"
    echo "   python main.py api"
    echo ""
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
