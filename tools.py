"""Tool agents for validation and date extraction."""

import re
from datetime import datetime, timedelta
from dateutil import parser
from email_validator import validate_email, EmailNotValidError
from typing import Dict, Any
from langchain_community.llms import Ollama
from config import OLLAMA_MODEL, OLLAMA_BASE_URL


def validate_name(name: str) -> Dict[str, Any]:
    """Validate name field."""
    if not name or len(name.strip()) < 2:
        return {
            "valid": False,
            "error": "Name must be at least 2 characters long and non-empty."
        }

    # Check if name contains only letters, spaces, and common punctuation
    if not re.match(r"^[a-zA-Z\s\.\-\']+$", name):
        return {
            "valid": False,
            "error": "Name can only contain letters, spaces, and basic punctuation."
        }

    return {"valid": True, "value": name.strip()}


def validate_phone(phone: str) -> Dict[str, Any]:
    """Validate phone number format."""
    # Remove common separators
    cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)

    # Check if it's numeric and has reasonable length (10-15 digits)
    if not cleaned_phone.isdigit():
        return {
            "valid": False,
            "error": "Phone number must contain only digits."
        }

    if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
        return {
            "valid": False,
            "error": "Phone number must be between 10 and 15 digits."
        }

    return {"valid": True, "value": cleaned_phone}


def validate_email_address(email: str) -> Dict[str, Any]:
    """Validate email format."""
    try:
        # Validate email
        valid = validate_email(email)
        return {"valid": True, "value": valid.email}
    except EmailNotValidError as e:
        return {
            "valid": False,
            "error": f"Invalid email format: {str(e)}"
        }


def extract_date_from_natural_language(date_text: str) -> Dict[str, Any]:
    """Extract and convert natural language date to YYYY-MM-DD format."""
    try:
        date_text_lower = date_text.lower().strip()
        today = datetime.now()

        # Handle common relative dates
        if date_text_lower in ["today"]:
            target_date = today
        elif date_text_lower in ["tomorrow"]:
            target_date = today + timedelta(days=1)
        elif "next week" in date_text_lower:
            target_date = today + timedelta(weeks=1)
        elif "next month" in date_text_lower:
            # Add roughly 30 days
            target_date = today + timedelta(days=30)
        elif "next monday" in date_text_lower or "coming monday" in date_text_lower:
            days_ahead = 0 - today.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next tuesday" in date_text_lower or "coming tuesday" in date_text_lower:
            days_ahead = 1 - today.weekday()  # Tuesday is 1
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next wednesday" in date_text_lower or "coming wednesday" in date_text_lower:
            days_ahead = 2 - today.weekday()  # Wednesday is 2
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next thursday" in date_text_lower or "coming thursday" in date_text_lower:
            days_ahead = 3 - today.weekday()  # Thursday is 3
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next friday" in date_text_lower or "coming friday" in date_text_lower:
            days_ahead = 4 - today.weekday()  # Friday is 4
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next saturday" in date_text_lower or "coming saturday" in date_text_lower:
            days_ahead = 5 - today.weekday()  # Saturday is 5
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "next sunday" in date_text_lower or "coming sunday" in date_text_lower:
            days_ahead = 6 - today.weekday()  # Sunday is 6
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        elif "in" in date_text_lower and "day" in date_text_lower:
            # Handle "in X days"
            match = re.search(r'in\s+(\d+)\s+days?', date_text_lower)
            if match:
                days = int(match.group(1))
                target_date = today + timedelta(days=days)
            else:
                # Try using dateutil parser as fallback
                target_date = parser.parse(date_text, fuzzy=True)
        else:
            # Try using dateutil parser for other formats
            target_date = parser.parse(date_text, fuzzy=True)

        # Format as YYYY-MM-DD
        formatted_date = target_date.strftime("%Y-%m-%d")

        return {
            "valid": True,
            "value": formatted_date,
            "parsed_date": target_date.strftime("%B %d, %Y")  # Human readable
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"Could not parse date from '{date_text}'. Please try formats like 'next Monday', 'tomorrow', 'in 3 days', or 'YYYY-MM-DD'."
        }


def query_documents(query: str, documents_content: str = "") -> str:
    """
    Query documents using LLM for semantic understanding and relevance matching.
    Uses the configured Ollama model to intelligently extract relevant information.
    """
    if not documents_content:
        return "No documents available to query. Please upload documents first."

    # Initialize Ollama LLM
    try:
        llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3  # Lower temperature for more focused extraction
        )

        # Create a prompt for semantic information extraction
        extraction_prompt = f"""
        You are an intelligent document assistant. 
        Your task is to extract and return ONLY the relevant information from the document that answers the user's query.

        Document Content:
        {documents_content}
        
        User Query: {query}
        
        Instructions:
        1. Carefully read and understand the user's query
        2. Search through the entire document for information that is semantically related to the query
        3. Extract ALL relevant sections, paragraphs, or details that answer the query
        4. If multiple pieces of information are relevant, include them all
        5. Preserve the original text structure and details (prices, timelines, contact info, etc.)
        6. If no relevant information is found, respond with: "No relevant information found"
        
        Return only the extracted relevant information without adding explanations or commentary.
"""

        # Use LLM to extract relevant information
        relevant_info = llm.invoke(extraction_prompt).strip()

        # Check if information was found
        if "no relevant information found" in relevant_info.lower() and len(relevant_info) < 100:
            return "No relevant information found in the documents for your query."

        return relevant_info

    except Exception as e:
        # Fallback to keyword-based search if LLM fails
        print(f"LLM query failed, falling back to keyword search: {e}")
        query_lower = query.lower()
        lines = documents_content.split('\n')
        relevant_lines = [line for line in lines if any(word in line.lower() for word in query_lower.split())]

        if relevant_lines:
            return "\n".join(relevant_lines[:5])
        else:
            return "No relevant information found in the documents for your query."