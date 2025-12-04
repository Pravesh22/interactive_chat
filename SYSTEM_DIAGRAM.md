# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   CLI Mode   │  │   API Mode   │  │  Web Client  │         │
│  │ (main.py)    │  │  (FastAPI)   │  │  (Future)    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      SESSION MANAGEMENT             │
          │  ┌──────────────────────────┐       │
          │  │  Session Store           │       │
          │  │  - appointment_data      │       │
          │  │  - conversation_history  │       │
          │  │  - documents_content     │       │
          │  │  - session_timeout       │       │
          │  └──────────────────────────┘       │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │     LANGGRAPH AGENT ORCHESTRATION   │
          │                                      │
          │  ┌────────────────────────────┐     │
          │  │   INTENT CLASSIFIER        │     │
          │  │                            │
          │  │                            │     │
          │  │  Analyzes user input to    │     │
          │  │  determine intent:         │     │
          │  │  - document_query          │     │
          │  │  - appointment_booking     │     │
          │  └────────┬────────┬──────────┘     │
          │           │        │                 │
          │  ┌────────▼───┐  ┌▼─────────────┐   │
          │  │ Document   │  │ Appointment  │   │
          │  │ Query      │  │ Booking      │   │
          │  │ Handler    │  │ Handler      │   │
          │  └────────┬───┘  └┬─────────────┘   │
          └───────────┼───────┼─────────────────┘
                      │       │
          ┌───────────▼───────▼─────────────────┐
          │        TOOL AGENTS LAYER            │
          │                                      │
          │  ┌──────────────┐  ┌──────────────┐│
          │  │   Validation │  │  Date        ││
          │  │   Tools      │  │  Extraction  ││
          │  │              │  │              ││
          │  │ • Name       │  │ • Natural    ││
          │  │ • Email      │  │   Language   ││
          │  │ • Phone      │  │   Parsing    ││
          │  └──────────────┘  └──────────────┘│
          │                                      │
          │  ┌──────────────────────────────┐   │
          │  │   Document Query Tool        │   │
          │  │                              │   │
          │  │ • Keyword Matching           │   │
          │  │ • Content Retrieval          │   │
          │  │ • (Future: Vector Search)    │   │
          │  └──────────────────────────────┘   │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │       OLLAMA LLM (Local)            │
          │                                      │
          │  ┌────────────────────────────┐     │
          │  │  Model: llama3.2           │     │
          │  │  Base URL: localhost:11434 │     │
          │  │                            │     │
          │  │  Capabilities:             │     │
          │  │  • Intent Classification   │     │
          │  │  • Response Generation     │     │
          │  │  • Entity Extraction       │     │
          │  │  • Conversational Context  │     │
          │  └────────────────────────────┘     │
          └─────────────────────────────────────┘
```

## Detailed Component Flow

### 1. User Input Processing

```
User Input
    │
    ├─> CLI Mode (main.py)
    │   └─> Direct function call to run_agent()
    │
    └─> API Mode (app.py)
        └─> FastAPI endpoint /chat
            └─> Session management
                └─> run_agent() call
```

### 2. LangGraph Agent Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph State Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  START                                                      │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────┐                                   │
│  │ classify_intent     │                                   │
│  │                     │                                   │
│  │ • Analyzes input    │                                   │
│  │ • Checks keywords   │                                   │
│  │ • Uses LLM          │                                   │
│  │ • Sets intent       │                                   │
│  └──────┬──────────────┘                                   │
│         │                                                   │
│         │ (conditional routing)                             │
│         │                                                   │
│    ┌────┴──────┐                                           │
│    │           │                                           │
│    ▼           ▼                                           │
│  ┌─────────┐ ┌──────────────┐                             │
│  │document_│ │appointment_  │                             │
│  │query    │ │booking       │                             │
│  │         │ │              │                             │
│  │ Process │ │ Process      │                             │
│  │ query   │ │ booking      │                             │
│  │ with    │ │ form         │                             │
│  │ docs    │ │ collection   │                             │
│  └────┬────┘ └──────┬───────┘                             │
│       │             │                                      │
│       └──────┬──────┘                                      │
│              │                                             │
│              ▼                                             │
│            END                                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3. Document Query Flow

```
Document Query Intent Detected
    │
    ├─> 1. Extract query from user input
    │
    ├─> 2. Retrieve relevant document content
    │       └─> query_documents(query, documents_content)
    │           └─> Keyword matching (future: vector search)
    │
    ├─> 3. Build prompt with context
    │       └─> Document info + User question
    │
    ├─> 4. Send to Ollama LLM
    │       └─> llm.invoke(prompt)
    │
    └─> 5. Return formatted response
```

### 4. Appointment Booking Flow

```
Appointment Booking Intent Detected
    │
    ├─> 1. Check current appointment_data state
    │       └─> Required: name, phone, email, date
    │
    ├─> 2. Extract info from user input
    │   │
    │   ├─> Name Extraction
    │   │   └─> validate_name()
    │   │       ├─> Regex validation
    │   │       └─> Update appointment_data
    │   │
    │   ├─> Phone Extraction
    │   │   └─> validate_phone()
    │   │       ├─> Format normalization
    │   │       ├─> Length validation
    │   │       └─> Update appointment_data
    │   │
    │   ├─> Email Extraction
    │   │   └─> validate_email_address()
    │   │       ├─> Email-validator library
    │   │       └─> Update appointment_data
    │   │
    │   └─> Date Extraction
    │       └─> extract_date_from_natural_language()
    │           ├─> Parse natural language
    │           │   • "next Monday"
    │           │   • "tomorrow"
    │           │   • "in 3 days"
    │           ├─> Convert to YYYY-MM-DD
    │           └─> Update appointment_data
    │
    ├─> 3. Check for missing fields
    │
    ├─> 4. Generate appropriate response
    │   │
    │   ├─> If fields missing:
    │   │   └─> Ask for next required field
    │   │
    │   └─> If all complete:
    │       └─> Confirm booking
    │
    └─> 5. Update session state
```

### 5. Session Management

```
Session Structure:
{
    "session_id": "uuid-string",
    "appointment_data": {
        "name": "John Doe",
        "phone": "5551234567",
        "email": "john@example.com",
        "date": "2025-12-15"
    },
    "conversation_history": [
        {
            "user": "I want to book...",
            "assistant": "I'd be happy..."
        }
    ],
    "documents_content": "Full text content...",
    "created_at": "2025-12-01T10:00:00",
    "last_accessed": "2025-12-01T10:05:00"
}
```

## Data Flow Diagrams

### Scenario 1: Document Query

```
User: "What services do you offer?"
  │
  └─> FastAPI /chat endpoint
      │
      └─> Session retrieved/created
          │
          └─> run_agent(input, session_data)
              │
              └─> LangGraph: classify_intent
                  │ (intent: "document_query")
                  │
                  └─> handle_document_query
                      │
                      ├─> query_documents(input, docs)
                      │   └─> Returns relevant content
                      │
                      ├─> Build LLM prompt
                      │   └─> Context + Question
                      │
                      ├─> Ollama LLM generates response
                      │
                      └─> Return response to user
```

### Scenario 2: Appointment Booking

```
User: "I want to book an appointment"
  │
  └─> FastAPI /chat endpoint
      │
      └─> Session retrieved
          │ appointment_data: {}
          │
          └─> run_agent(input, session_data)
              │
              └─> LangGraph: classify_intent
                  │ (intent: "appointment_booking")
                  │
                  └─> handle_appointment_booking
                      │
                      ├─> Check required fields
                      │   └─> All empty
                      │
                      ├─> Try to extract from input
                      │   └─> None found in this message
                      │
                      └─> Ask for name
                          └─> "Could you please provide your full name?"

User: "John Doe"
  │
  └─> Same flow...
      └─> handle_appointment_booking
          │
          ├─> Extract name: "John Doe"
          ├─> validate_name("John Doe") ✓
          ├─> appointment_data.name = "John Doe"
          ├─> Check missing: phone, email, date
          └─> Ask for phone

[Process continues until all fields collected]

Final Message:
  │
  └─> All fields present
      └─> Generate confirmation message
          └─> "Your appointment has been successfully booked!"
```

### Scenario 3: Context Switching

```
User: "I want to book an appointment"
  └─> Intent: appointment_booking
      └─> Start collecting info...

User: "What are your services?"
  └─> Intent: document_query
      └─> Query documents
      └─> appointment_data preserved in session

User: "My name is Alice"
  └─> Intent: appointment_booking
      └─> Resume appointment flow
      └─> Continue from where we left off
```

## Technology Integration Points

### FastAPI Integration
- REST API endpoints for chat, document upload, session management
- Middleware for CORS
- Pydantic models for request/response validation
- In-memory session store (can be replaced with Redis)

### LangGraph Integration
- StateGraph for managing conversation flow
- TypedDict for state typing
- Conditional routing based on intent
- Node-based processing (classify → handle → end)

### Ollama Integration
- Local LLM running on port 11434
- langchain_community.llms.Ollama wrapper
- Temperature-controlled generation
- Used for intent classification and response generation

### Validation Tools
- email-validator: RFC-compliant email validation
- python-dateutil: Natural language date parsing
- Custom regex patterns for phone and name validation

## Scalability Considerations

### Current Implementation
- In-memory session storage
- Synchronous processing
- Single-threaded

### Production Recommendations
1. **Session Storage**: Redis or database
2. **Document Storage**: Vector database (Pinecone, Weaviate)
3. **Load Balancing**: Multiple FastAPI instances
4. **Async Processing**: Async/await for I/O operations
5. **Rate Limiting**: API rate limits per user/session
6. **Monitoring**: Logging, metrics, tracing

## Security Considerations

1. **Input Validation**: All inputs validated before processing
2. **Session Timeout**: Automatic cleanup of old sessions
3. **Data Sanitization**: XSS prevention in stored data
4. **Rate Limiting**: Prevent abuse (to be implemented)
5. **CORS**: Configurable origins
6. **Local LLM**: No data sent to external services

## Future Enhancements

1. **Vector Database**: Replace keyword search with semantic search
2. **Authentication**: User accounts and authorization
3. **Email Integration**: Send appointment confirmations
4. **Calendar Integration**: Google Calendar, Outlook
5. **Multi-language Support**: i18n for global users
6. **Voice Interface**: Speech-to-text integration
7. **Analytics Dashboard**: Usage metrics and insights
8. **Webhook Support**: Integrate with external systems