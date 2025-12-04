# Context-Aware Conversational Chatbot

A sophisticated chatbot system that can seamlessly handle document queries and appointment booking with context switching capabilities.

## Features

✨ **Dual Functionality**
- 📄 Document query system for answering questions from uploaded documents
- 📅 Conversational appointment booking with natural language date parsing

🤖 **Intelligent Agent System**
- LangGraph-based agent orchestration
- Automatic intent classification
- Context-aware conversation handling

🛠️ **Validation Tools**
- Email validation
- Phone number validation
- Name validation
- Natural language date extraction (e.g., "next Monday", "in 3 days")

🔄 **Context Switching**
- Seamlessly switch between document queries and appointment booking
- Maintains conversation history and state

## Tech Stack

- **Backend**: FastAPI
- **LLM**: Ollama (Local)
- **Agent Orchestration**: LangGraph
- **Validation**: email-validator, python-dateutil

## Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running locally
   - Install from: https://ollama.ai
   - Pull a model: `ollama pull llama3.2` (or your preferred model)
   - Verify it's running: `ollama list`

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Ollama model** (optional)
Edit `config.py` to change the model name:
```python
OLLAMA_MODEL = "llama3.2"  # Change to your preferred model
```

## Usage

### 1. Interactive CLI Mode (Recommended for Testing)

```bash
python main.py interactive
```

**Commands in interactive mode:**
- Type your message to chat with the bot
- `load_doc` - Load a sample document for testing queries
- `status` - View current session status
- `reset` - Reset the session
- `quit` or `exit` - Exit the program

**Example conversation:**
```
You: load_doc
✅ Sample document loaded!

You: What services do you offer?
Assistant: [Responds with document information]

You: I want to book an appointment
Assistant: [Starts appointment booking flow]

You: My name is John Doe
Assistant: Got it! I've recorded your name as John Doe.
         Could you please provide your phone number?
```

### 2. Automated Tests

Run all automated tests to verify functionality:
```bash
python main.py test
```

This will test:
- Document query capabilities
- Appointment booking flow
- Context switching between modes

### 3. FastAPI Server Mode

Start the REST API server:
```bash
python main.py api
```

Or use uvicorn directly:
```bash
uvicorn app:app --reload
```

**API will be available at:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### POST /chat
Chat with the bot (handles both document queries and appointment booking)

**Request:**
```json
{
  "message": "I want to book an appointment",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you book an appointment...",
  "session_id": "generated-session-id",
  "intent": "appointment_booking",
  "appointment_data": {
    "name": "John Doe",
    "phone": "5551234567"
  }
}
```

### POST /upload-document
Upload a text document for querying

**Request:** (multipart/form-data)
- `file`: Text file to upload
- `session_id`: Optional session ID

**Response:**
```json
{
  "message": "Document 'example.txt' uploaded successfully",
  "session_id": "session-id"
}
```

### GET /sessions/{session_id}
Get session data

### DELETE /sessions/{session_id}
Delete a session

### GET /sessions
List all active sessions

### GET /health
Health check endpoint

## Testing Examples

### Test Document Queries

```bash
# Start interactive mode
python main.py interactive

# Load sample document
> load_doc

# Ask questions
> What services do you offer?
> How much does web development cost?
> What are your business hours?
```

### Test Appointment Booking

```bash
# Start interactive mode
python main.py interactive

# Start booking
> I want to book an appointment
> My name is Alice Smith
> My phone is 555-123-4567
> alice@example.com
> Schedule it for next Monday
```

### Test Context Switching

```bash
# Start interactive mode
python main.py interactive

# Switch between contexts
> load_doc
> I want to book an appointment
> What services do you offer?  # Switch to document query
> My name is John Doe  # Back to appointment booking
> How much is web development?  # Switch again
> My phone is 555-987-6543  # Continue booking
```

## Natural Language Date Examples

The system understands various date formats:
- "today", "tomorrow"
- "next Monday", "next Tuesday", etc.
- "coming Friday", "coming Saturday"
- "in 3 days", "in 2 weeks"
- Standard formats: "2025-12-15", "Dec 15 2025"

## Project Structure

```
chatbot_test/
├── main.py              # Main entry point with CLI interface
├── app.py               # FastAPI application
├── agents.py            # LangGraph agent orchestration
├── tools.py             # Validation and utility tools
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Configuration

Edit `config.py` to customize:

```python
# Ollama settings
OLLAMA_MODEL = "llama3.2"  # Change model
OLLAMA_BASE_URL = "http://localhost:11434"

# Session settings
SESSION_TIMEOUT = 3600  # 1 hour

# Server settings
APP_HOST = "0.0.0.0"
APP_PORT = 8000
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service if needed
ollama serve
```

### Model Not Found
```bash
# Pull the required model
ollama pull llama3.2
```

### Port Already in Use
Change the port in `config.py` or specify when running:
```bash
uvicorn app:app --port 8001
```

## Development

### Adding New Validation Tools
Edit `tools.py` and add your validation function:
```python
def validate_custom_field(value: str) -> Dict[str, Any]:
    # Your validation logic
    return {"valid": True, "value": value}
```

### Modifying Agent Behavior
Edit `agents.py` to customize:
- Intent classification logic
- Document query handling
- Appointment booking flow

### Adding New API Endpoints
Edit `app.py` to add new FastAPI endpoints.

## System Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (app.py)           │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────┐
│  LangGraph Agent     │
│  (agents.py)         │
│                      │
│  ┌────────────────┐  │
│  │ Intent         │  │
│  │ Classifier     │  │
│  └───────┬────────┘  │
│          │           │
│    ┌─────┴─────┐     │
│    ▼           ▼     │
│ ┌────────┐ ┌────────┐│
│ │Document│ │Appoint-││
│ │Query   │ │ment    ││
│ │Handler │ │Booking ││
│ └────────┘ └────────┘│
└──────────────────────┘
          │
          ▼
┌──────────────────────┐
│   Validation Tools   │
│   (tools.py)         │
│                      │
│  - Email Validator   │
│  - Phone Validator   │
│  - Date Extractor    │
│  - Document Query    │
└──────────────────────┘
          │
          ▼
┌──────────────────────┐
│   Ollama LLM         │
│   (Local Model)      │
└──────────────────────┘
```

## License

MIT License

## Support

For issues or questions, please check:
1. Ollama is running: `ollama list`
2. Dependencies installed: `pip install -r requirements.txt`
3. Python version: `python --version` (3.9+ required)
