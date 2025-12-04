"""LangGraph agent orchestration system for context-aware chatbot."""

from typing import TypedDict, Sequence, Literal

from langchain.schema import HumanMessage, AIMessage
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, END

from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from tools import (
    validate_name,
    validate_phone,
    validate_email_address,
    extract_date_from_natural_language,
    query_documents
)

# Initialize Ollama LLM
llm = Ollama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7
)


# Define the state for our agent
class AgentState(TypedDict):
    messages: Sequence[HumanMessage | AIMessage]
    user_input: str
    intent: str  # "document_query" or "appointment_booking"
    appointment_data: dict
    conversation_history: list
    documents_content: str
    response: str
    next_action: str


def classify_intent(state: AgentState) -> AgentState:
    """Classify user intent as document query or appointment booking."""
    user_input = state["user_input"].lower()

    # Intent classification prompt
    prompt = f"""
    You are an expert intent classifier. Classify the user's input into one of these categories:
        - "appointment_booking": If the user wants to book an appointment, schedule, make a reservation, or provide booking details
        - "document_query": If the user is asking questions about documents, information, or general queries
        
        User input: "{state['user_input']}"
        
        Respond with only one word: either "appointment_booking" or "document_query".
    """

    try:
        intent_response = llm.invoke(prompt).strip().lower()

        # Parse the response
        if "appointment" in intent_response or "booking" in intent_response:
            state["intent"] = "appointment_booking"
        elif "document" in intent_response or "query" in intent_response:
            state["intent"] = "document_query"
        else:
            # Default fallback: check keywords in user input
            appointment_keywords = ["appointment", "book", "schedule", "reservation", "meeting"]
            if any(keyword in user_input for keyword in appointment_keywords):
                state["intent"] = "appointment_booking"
            else:
                state["intent"] = "document_query"
    except Exception as e:
        print(f"Intent classification error: {e}")
        # Default to document query
        state["intent"] = "document_query"

    return state


def handle_document_query(state: AgentState) -> AgentState:
    """Handle document query using Ollama and document search."""
    user_query = state["user_input"]
    documents_content = state.get("documents_content", "")

    # Query documents
    relevant_info = query_documents(user_query, documents_content)

    # Generate response using LLM
    prompt = f"""You are a helpful assistant. Answer the user's question based on the following document information.
        Document Information:
        {relevant_info}
        
        User Question: {user_query}
        
        Provide a clear and concise answer. If the information is not available in the documents, say so politely.
"""

    try:
        response = llm.invoke(prompt)
        state["response"] = response
    except Exception as e:
        state["response"] = f"I apologize, but I encountered an error: {str(e)}"

    state["next_action"] = "complete"
    return state


def handle_appointment_booking(state: AgentState) -> AgentState:
    """Handle appointment booking with conversational form filling."""
    user_input = state["user_input"]
    appointment_data = state.get("appointment_data", {})

    # Check what fields are missing
    required_fields = ["name", "phone", "email", "date"]
    missing_fields = [field for field in required_fields if
                      field not in appointment_data or not appointment_data[field]]

    if not missing_fields:
        # All fields collected, confirm booking
        state["response"] = f"""Great! I have all the information needed for your appointment:
            Name: {appointment_data['name']}
            Phone: {appointment_data['phone']}
            Email: {appointment_data['email']}
            Date: {appointment_data['date']}
            
            Your appointment has been successfully booked! You will receive a confirmation email shortly.
        """
        state["next_action"] = "complete"
        return state

    # Try to extract information from user input
    response_parts = []

    # Check for name
    if "name" not in appointment_data or not appointment_data["name"]:
        # Try to extract name using LLM
        name_prompt = f"""
        Extract the person's name from this text. If no name is present, respond with "NOT_FOUND".
        Text: "{user_input}"
        Name:
        """
        try:
            extracted_name = llm.invoke(name_prompt).strip()
            if extracted_name != "NOT_FOUND" and len(extracted_name) > 0:
                validation = validate_name(extracted_name)
                if validation["valid"]:
                    appointment_data["name"] = validation["value"]
                    response_parts.append(f"Got it! I've recorded your name as {validation['value']}.")
        except:
            pass

    # Check for phone
    if "phone" not in appointment_data or not appointment_data["phone"]:
        # Look for phone patterns
        import re
        phone_pattern = r'[\+\(]?[0-9][0-9\s\-\(\)]{8,}[0-9]'
        phone_matches = re.findall(phone_pattern, user_input)
        if phone_matches:
            validation = validate_phone(phone_matches[0])
            if validation["valid"]:
                appointment_data["phone"] = validation["value"]
                response_parts.append(f"Phone number recorded: {validation['value']}")

    # Check for email
    if "email" not in appointment_data or not appointment_data["email"]:
        # Look for email patterns
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, user_input)
        if email_matches:
            validation = validate_email_address(email_matches[0])
            if validation["valid"]:
                appointment_data["email"] = validation["value"]
                response_parts.append(f"Email recorded: {validation['value']}")

    # Check for date
    if "date" not in appointment_data or not appointment_data["date"]:
        # Try to extract date
        date_result = extract_date_from_natural_language(user_input)
        if date_result["valid"]:
            appointment_data["date"] = date_result["value"]
            response_parts.append(f"Date recorded: {date_result.get('parsed_date', date_result['value'])}")

    # Update state
    state["appointment_data"] = appointment_data

    # Check again for missing fields
    missing_fields = [field for field in required_fields if
                      field not in appointment_data or not appointment_data[field]]

    if response_parts:
        response = "\n".join(response_parts) + "\n\n"
    else:
        response = ""

    # Ask for missing fields
    if missing_fields:
        if "name" in missing_fields:
            response += "Could you please provide your full name?"
        elif "phone" in missing_fields:
            response += "Could you please provide your phone number?"
        elif "email" in missing_fields:
            response += "Could you please provide your email address?"
        elif "date" in missing_fields:
            response += "When would you like to schedule your appointment? (You can say things like 'next Monday', 'tomorrow', 'in 3 days', etc.)"

        state["next_action"] = "continue"
    else:
        # All fields collected
        response = f"""Perfect! I have all the information needed:

        Name: {appointment_data['name']}
        Phone: {appointment_data['phone']}
        Email: {appointment_data['email']}
        Date: {appointment_data['date']}
        
        Your appointment has been successfully booked!
        """
        state["next_action"] = "complete"

    state["response"] = response
    return state


def route_intent(state: AgentState) -> Literal["document_query", "appointment_booking"]:
    """Route to appropriate handler based on intent."""
    return state["intent"]


# Build the LangGraph
def create_agent_graph():
    """Create and return the LangGraph agent."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("document_query", handle_document_query)
    workflow.add_node("appointment_booking", handle_appointment_booking)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "document_query": "document_query",
            "appointment_booking": "appointment_booking"
        }
    )

    # Add edges to END
    workflow.add_edge("document_query", END)
    workflow.add_edge("appointment_booking", END)

    # Compile the graph
    app = workflow.compile()
    return app


# Create the agent
agent_graph = create_agent_graph()


def run_agent(user_input: str, session_data: dict = None) -> dict:
    """Run the agent with user input and session data."""
    if session_data is None:
        session_data = {
            "appointment_data": {},
            "conversation_history": [],
            "documents_content": ""
        }

    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "user_input": user_input,
        "intent": "",
        "appointment_data": session_data.get("appointment_data", {}),
        "conversation_history": session_data.get("conversation_history", []),
        "documents_content": session_data.get("documents_content", ""),
        "response": "",
        "next_action": ""
    }

    # Run the agent
    result = agent_graph.invoke(initial_state)

    # Update session data
    session_data["appointment_data"] = result.get("appointment_data", {})
    session_data["conversation_history"].append({
        "user": user_input,
        "assistant": result.get("response", "")
    })

    return {
        "response": result.get("response", ""),
        "intent": result.get("intent", ""),
        "session_data": session_data
    }
