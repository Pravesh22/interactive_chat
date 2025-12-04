# Quick Start Guide

## Prerequisites

1. **Install Python 3.9+**
2. **Install Ollama**: https://ollama.ai
3. **Pull an Ollama model**: `ollama pull llama3.2`

## Setup

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run the Chatbot

### Interactive Mode (Recommended for first-time users)
```bash
python main.py interactive
```

**Try these commands:**
1. Type `load_doc` to load a sample document
2. Ask: "What services do you offer?"
3. Say: "I want to book an appointment"
4. Follow the conversation to complete booking

### Run All Tests
```bash
python main.py test
```

### Start API Server
```bash
python main.py api
```
Then visit: http://localhost:8000/docs

## Quick Test

```bash
# Start interactive mode
python main.py interactive

# In the chatbot:
> load_doc
> What are your business hours?
> I want to book an appointment
> My name is John Doe
> 555-123-4567
> john@example.com
> tomorrow
```

## Troubleshooting

**"Ollama connection error"**
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

**"Model not found"**
```bash
ollama pull llama3.2
```

**"Port 8000 already in use"**
```bash
# Use a different port
uvicorn app:app --port 8001
```

## Project Files

- `main.py` - Run this file to test everything
- `app.py` - FastAPI server
- `agents.py` - LangGraph agent logic
- `tools.py` - Validation functions
- `config.py` - Configuration settings

## Need Help?

Check the full [README.md](README.md) for detailed documentation.