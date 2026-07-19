import asyncio
import os
from google.adk.assistants import LanguageModelAgent
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Orchestrator
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database session service for persistent storage
session_service = DatabaseSessionService(
    db_url="sqlite:///sessions.db"
)

# Create a simple assistant with persistent memory
assistant = LanguageModelAgent(
    name="persistent_agent",
    model="gemini-3-flash-preview",
    description="A simple assistant that remembers conversations in a database",
    instruction="You are a helpful assistant. Remember what users tell you and reference it in future conversations. Your memory persists across program restarts."
)

# Create runner with database session service
runner = Orchestrator(
    assistant=assistant,
    service_name="demo",
    session_service=session_service
)

async def chat(account_id: str, message: str) -> str:
    """Simple chat function with persistent database memory"""
    context_id = f"session_{account_id}"
    
    # Get or create session
    session = await session_service.get_session(
        service_name="demo", 
        account_id=account_id, 
        context_id=context_id
    )
    if not session:
        # Create new session with initial state
        session = await session_service.create_session(
            service_name="demo",
            account_id=account_id,
            context_id=context_id,
            state={"conversation_history": []}
        )
    
    # Create user content
    user_content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )
    
    # Run the assistant with session
    response_text = ""
    async for event in runner.run_async(
        account_id=account_id,
        context_id=context_id,
        new_message=user_content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
            break
    
    return response_text

# Test the persistent memory
if __name__ == "__main__":
    async def test():
        # Initialize database
        await session_service.initialize()
        print("✅ Database initialized")
        
        account_id = "test_user"
        messages = ["My name is Bob", "What's my name?", "I love coding", "What do I love?"]
        
        for msg in messages:
            print(f"\nUser: {msg}")
            response = await chat(account_id, msg)
            print(f"Assistant: {response}")
    
    asyncio.run(test()) 