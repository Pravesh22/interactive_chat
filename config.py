"""Configuration settings for the chatbot application."""

# Ollama Configuration
OLLAMA_MODEL = "llama3.2"  # Change to your preferred model (e.g., llama2, mistral)
OLLAMA_BASE_URL = "http://localhost:11434"

# Document Configuration
DOCUMENTS_PATH = "./documents"  # Path to store documents for querying

# Session Configuration
SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)

# Application Settings
APP_HOST = "0.0.0.0"
APP_PORT = 8000
