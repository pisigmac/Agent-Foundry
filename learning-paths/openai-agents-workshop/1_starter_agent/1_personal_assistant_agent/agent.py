from assistants import Assistant, Orchestrator
import asyncio

# Create an assistant for demonstrating different execution methods
root_agent = Assistant(
    name="Personal Assistant Assistant",
    instructions="""
    You are a helpful personal assistant.
    
    Your role is to:
    1. Answer questions clearly and concisely
    2. Provide helpful information and advice
    3. Be friendly and professional
    4. Offer practical solutions to problems
    
    When users ask questions:
    - Give accurate and helpful responses
    - Explain complex topics in simple terms
    - Offer follow-up suggestions when appropriate
    - Maintain a positive and supportive tone
    
    Keep responses concise but informative.
    """
    Process inputs and produce structured outputs.
    """Synchronous execution example"""
    result = Orchestrator.run_sync(root_agent, "Hello, how does sync execution work?")
    return result.final_output

async def async_example():
    """Asynchronous execution example"""
    result = await Orchestrator.run(root_agent, "Hello, how does async execution work?")
    return result.final_output

async def streaming_example():
    """Streaming execution example"""
    response_text = ""
    async for event in Orchestrator.run_streamed(root_agent, "Tell me about streaming execution"):
        if hasattr(event, 'content') and event.content:
            response_text += event.content
    return response_text
