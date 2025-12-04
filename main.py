"""Main test file for the context-aware chatbot."""

import sys
from agents import run_agent


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def print_response(response_data: dict):
    """Print the chatbot response in a formatted way."""
    print(f"Intent: {response_data['intent']}")
    print(f"\nAssistant: {response_data['response']}")

    # Show appointment data if available
    appointment_data = response_data['session_data'].get('appointment_data', {})
    if appointment_data:
        print("\n--- Current Appointment Data ---")
        for key, value in appointment_data.items():
            print(f"  {key.capitalize()}: {value}")


def load_sample_document() -> str:
    """Load a sample document for testing."""
    sample_doc = """
    Product Information Document

    Our company offers the following services:

    1. Web Development: We create modern, responsive websites using the latest technologies.
       Price: Starting from $2000
       Timeline: 4-6 weeks

    2. Mobile App Development: Native and cross-platform mobile applications.
       Price: Starting from $5000
       Timeline: 8-12 weeks

    3. Cloud Solutions: AWS, Azure, and Google Cloud infrastructure setup and management.
       Price: Custom pricing based on requirements
       Timeline: 2-4 weeks

    4. AI/ML Solutions: Machine learning models and AI integration.
       Price: Starting from $10000
       Timeline: 12-16 weeks

    Business Hours: Monday to Friday, 9 AM - 6 PM
    Contact: support@company.com
    Phone: +1-555-0123
    """
    return sample_doc


def test_document_queries(session_data: dict):
    """Test document query functionality."""
    print("\n📄 Testing Document Query Feature")
    print_separator()

    # Load sample document
    session_data['documents_content'] = load_sample_document()
    print("✅ Sample document loaded into session.\n")

    # Test queries
    test_queries = [
        "What services do you offer?",
        "How much does web development cost?",
        "What are your business hours?"
    ]

    for query in test_queries:
        print(f"User: {query}")
        result = run_agent(query, session_data)
        print_response(result)
        session_data = result['session_data']
        print_separator()

    return session_data


def test_appointment_booking(session_data: dict):
    """Test appointment booking functionality."""
    print("\n📅 Testing Appointment Booking Feature")
    print_separator()

    # Test appointment booking conversation
    booking_inputs = [
        "I want to book an appointment",
        "My name is John Doe",
        "My phone is 555-123-4567",
        "Email is john.doe@example.com",
        "Next Monday would be great"
    ]

    for user_input in booking_inputs:
        print(f"User: {user_input}")
        result = run_agent(user_input, session_data)
        print_response(result)
        session_data = result['session_data']
        print_separator()

    return session_data


def test_context_switching(session_data: dict):
    """Test switching between document queries and appointment booking."""
    print("\n🔄 Testing Context Switching")
    print_separator()

    # Switch between contexts
    mixed_inputs = [
        "I'd like to book an appointment",
        "Actually, first tell me about your AI services",
        "Ok, let me continue booking. My name is Alice Smith",
        "What's the timeline for mobile app development?",
        "Back to booking - my phone is 555-987-6543",
        "My email is alice@example.com",
        "Schedule it for tomorrow"
    ]

    for user_input in mixed_inputs:
        print(f"User: {user_input}")
        result = run_agent(user_input, session_data)
        print_response(result)
        session_data = result['session_data']
        print_separator()

    return session_data


def interactive_mode():
    """Run in interactive mode for manual testing."""
    print("\n🤖 Context-Aware Chatbot - Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  - Type your message to chat")
    print("  - Type 'load_doc' to load a sample document")
    print("  - Type 'status' to see current session data")
    print("  - Type 'reset' to reset the session")
    print("  - Type 'quit' or 'exit' to exit")
    print_separator()

    # Initialize session
    session_data = {
        "appointment_data": {},
        "conversation_history": [],
        "documents_content": ""
    }

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == 'reset':
                session_data = {
                    "appointment_data": {},
                    "conversation_history": [],
                    "documents_content": ""
                }
                print("\n✅ Session reset successfully!")
                continue

            if user_input.lower() == 'load_doc':
                session_data['documents_content'] = load_sample_document()
                print("\n✅ Sample document loaded! You can now ask questions about it.")
                continue

            if user_input.lower() == 'status':
                print("\n📊 Current Session Status:")
                print(f"  - Documents loaded: {'Yes' if session_data.get('documents_content') else 'No'}")
                print(f"  - Appointment data: {session_data.get('appointment_data', {})}")
                print(f"  - Conversation turns: {len(session_data.get('conversation_history', []))}")
                continue

            # Process user input
            result = run_agent(user_input, session_data)
            session_data = result['session_data']

            print(f"\n🤖 Assistant [{result['intent']}]: {result['response']}")

            # Show appointment progress
            appointment_data = session_data.get('appointment_data', {})
            if appointment_data and result['intent'] == 'appointment_booking':
                filled_fields = [k for k, v in appointment_data.items() if v]
                if filled_fields and len(filled_fields) < 4:
                    print(f"\n   📋 Progress: {len(filled_fields)}/4 fields completed")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'reset' to start over.")


def run_all_tests():
    """Run all automated tests."""
    print("\n🚀 Starting Automated Tests for Context-Aware Chatbot")
    print("=" * 70)

    # Initialize session
    session_data = {
        "appointment_data": {},
        "conversation_history": [],
        "documents_content": ""
    }

    try:
        # Test 1: Document Queries
        session_data = test_document_queries(session_data)

        # Test 2: Appointment Booking
        # Reset appointment data for clean test
        session_data['appointment_data'] = {}
        session_data = test_appointment_booking(session_data)

        # Test 3: Context Switching
        # Reset for clean test
        session_data['appointment_data'] = {}
        session_data = test_context_switching(session_data)

        print("\n✅ All tests completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("  Context-Aware Chatbot Test Suite")
    print("=" * 70)

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'test':
            run_all_tests()
        elif mode == 'interactive':
            interactive_mode()
        elif mode == 'api':
            print("\n🌐 Starting FastAPI server...")
            print("Run: uvicorn app:app --reload")
            print("\nAPI will be available at: http://localhost:8000")
            print("API docs at: http://localhost:8000/docs")
            import uvicorn
            from app import app
            from config import APP_HOST, APP_PORT
            uvicorn.run(app, host=APP_HOST, port=APP_PORT)
        else:
            print(f"\n❌ Unknown mode: {mode}")
            print("\nUsage: python main.py [mode]")
            print("Modes:")
            print("  test        - Run automated tests")
            print("  interactive - Interactive CLI mode")
            print("  api         - Start FastAPI server")
    else:
        print("\nUsage: python main.py [mode]")
        print("\nAvailable modes:")
        print("  test        - Run automated tests")
        print("  interactive - Interactive CLI chat")
        print("  api         - Start FastAPI server")
        print("\nExample: python main.py interactive")


if __name__ == "__main__":
    main()