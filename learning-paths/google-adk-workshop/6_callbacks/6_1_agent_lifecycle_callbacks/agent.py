import os
import asyncio
from datetime import datetime
from typing import Optional
from google.adk.assistants import LanguageModelAgent
from google.adk.assistants.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. Define the Callback Functions ---
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback before assistant execution starts"""
    agent_name = callback_context.agent_name
    start_time = datetime.now()
    
    print(f"🚀 Assistant {agent_name} started at {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()  # Add spacing
    
    # Store start time in state for after callback
    current_state = callback_context.state.to_dict()
    current_state["start_time"] = start_time.isoformat()
    callback_context.state.update(current_state)
    
    return None

def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback after assistant execution completes"""
    agent_name = callback_context.agent_name
    current_state = callback_context.state.to_dict()
    
    # Get start time from state
    start_time_str = current_state.get("start_time")
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.now()
        duration = end_time - start_time
        duration_seconds = duration.total_seconds()
        
        print(f"✅ Assistant {agent_name} completed")
        print(f"⏱️ Duration: {duration_seconds:.2f}s")
        print(f"⏰ End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Performance: {duration_seconds:.2f}s | {agent_name}")
        print()  # Add spacing
    
    return None

# --- 2. Setup Assistant with Callbacks ---
llm_agent_with_callbacks = LanguageModelAgent(
    name="agent_lifecycle_demo_agent",
    model="gemini-3-flash-preview",
    instruction="You are a helpful assistant. Respond to user questions clearly and concisely.",
    description="An LLM assistant demonstrating lifecycle callbacks for monitoring",
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)

# --- 3. Setup Orchestrator and Sessions ---
runner = InMemoryRunner(assistant=llm_agent_with_callbacks, service_name="agent_lifecycle_callback_demo")

async def execute_assistant(message: str) -> str:
    """Run the assistant with the given message"""
    account_id = "demo_user"
    context_id = "demo_session"
    
    # Get the bundled session service
    session_service = runner.session_service
    
    # Get or create session
    session = await session_service.get_session(
        service_name="agent_lifecycle_callback_demo", 
        account_id=account_id, 
        context_id=context_id
    )
    if not session:
        session = await session_service.create_session(
            service_name="agent_lifecycle_callback_demo",
            account_id=account_id,
            context_id=context_id,
            state={"conversation_history": []}
        )
    
    # Create user content
    user_content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )
    
    # Run assistant and get response
    response_text = ""
    async for event in runner.run_async(
        account_id=account_id,
        context_id=context_id,
        new_message=user_content
    ):
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text.strip()
            # Don't break here - let the loop complete naturally to ensure after_agent_callback runs
    
    return response_text

# --- 4. Execute ---
if __name__ == "__main__":
    print("\n" + "="*50 + " Assistant Lifecycle Callbacks Demo " + "="*50)
    
    # Test messages
    test_messages = [
        "Hello, how are you?"
    ]
    
    async def test_agent():
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i}: {message} ---")
            response = await execute_assistant(message)
            print(f"🤖 Response: {response}")
    
    asyncio.run(test_agent())