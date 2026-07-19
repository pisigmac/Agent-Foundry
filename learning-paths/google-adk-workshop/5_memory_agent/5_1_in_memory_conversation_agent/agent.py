import asyncio
import os
import uuid
from google.adk.assistants import LanguageModelAgent
from google.adk.sessions import SessionManager
from google.adk.runners import Orchestrator
from google.genai import types
from dotenv import load_dotenv

# Load environment variables (for API key)
load_dotenv()

# Create session service and assistant
session_service = SessionManager()
assistant = LanguageModelAgent(
    name="memory_agent",
    model="gemini-3-flash-preview",
    description="A simple assistant that remembers conversations",
    instruction="You are a helpful assistant. Remember what users tell you and reference it in future conversations."
)

# Create runner with session service
runner = Orchestrator(
    assistant=assistant,
    service_name="demo",
    session_service=session_service
)

async def chat(account_id: str, message: str) -> str:
    """Simple chat function with memory using Orchestrator"""
    context_id = f"session_{account_id}"
    
    # Create or get session
    session = await session_service.get_session(service_name="demo", account_id=account_id, context_id=context_id)
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

# Test the memory
if __name__ == "__main__":
    async def test():
        account_id = "test_user"
        messages = ["My name is Alice", "What's my name?", "I love pizza", "What do I love?"]
        
        for msg in messages:
            print(f"\nUser: {msg}")
            response = await chat(account_id, msg)
            print(f"Assistant: {response}")
    
    asyncio.run(test()) 