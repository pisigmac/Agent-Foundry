from assistants import Assistant, Orchestrator, SQLiteSession

# Create an assistant for session demonstrations
root_agent = Assistant(
    name="Session Demo Assistant",
    instructions="""
    You are a helpful assistant that demonstrates session memory.
    
    Remember previous conversation context and reference it when relevant.
    Reply concisely but show that you remember previous interactions.
    """
)

# Example 1: In-memory session (temporary)
async def in_memory_session_example():
    """Demonstrates in-memory SQLite session that doesn't persist"""
    
    # In-memory session - lost when process ends
    session = SQLiteSession("temp_conversation")
    
    print("=== In-Memory Session Example ===")
    
    # First turn
    result = await Orchestrator.run(
        root_agent,
        "My name is Alice and I live in San Francisco.",
        session=session
    )
    print(f"Turn 1: {result.final_output}")
    
    # Second turn - assistant remembers automatically
    result = await Orchestrator.run(
        root_agent, 
        "What city do I live in?",
        session=session
    )
    print(f"Turn 2: {result.final_output}")
    
    return session

# Example 2: Persistent session (survives restarts)
async def persistent_session_example():
    """Demonstrates persistent SQLite session that saves to file"""
    
    # Persistent session - saves to database file
    session = SQLiteSession("user_123", "conversation_history.db")
    
    print("\n=== Persistent Session Example ===")
    
    # First conversation
    result = await Orchestrator.run(
        root_agent,
        "I'm a software developer working on AI projects.",
        session=session
    )
    print(f"First message: {result.final_output}")
    
    # Second conversation - context preserved
    result = await Orchestrator.run(
        root_agent,
        "What kind of work do I do?", 
        session=session
    )
    print(f"Follow-up: {result.final_output}")
    
    return session

# Example 3: Multi-turn conversation (mimicking OpenAI SDK docs example)
async def multi_turn_conversation():
    """Demonstrates extended conversation with automatic memory like SDK docs"""
    
    session = SQLiteSession("conversation_123", "conversations.db")
    
    print("\n=== Multi-Turn Conversation (like SDK docs) ===")
    
    # Similar to the OpenAI SDK documentation example
    print("🌉 First turn:")
    result = await Orchestrator.run(root_agent, "What city is the Golden Gate Bridge in?", session=session)
    print(f"User: What city is the Golden Gate Bridge in?")
    print(f"Assistant: {result.final_output}")
    
    print("\n🏛️ Second turn (assistant remembers automatically):")
    result = await Orchestrator.run(root_agent, "What state is it in?", session=session) 
    print(f"User: What state is it in?")
    print(f"Assistant: {result.final_output}")
    
    print("\n👥 Third turn (continuing context):")
    result = await Orchestrator.run(root_agent, "What's the population of that state?", session=session)
    print(f"User: What's the population of that state?")
    print(f"Assistant: {result.final_output}")
    
    print("\n💡 Notice how the assistant remembers context automatically!")
    print("   Sessions handle conversation history without manual .to_input_list()")
    
    return session

# Example 4: Session comparison - with vs without sessions 
async def session_comparison():
    """Demonstrates the difference between using sessions vs no sessions"""
    
    print("\n=== Session vs No Session Comparison ===")
    
    # Without session (no memory)
    print("🚫 WITHOUT Sessions (no memory):")
    result1 = await Orchestrator.run(root_agent, "My name is Alice")
    print(f"Turn 1: {result1.final_output}")
    
    result2 = await Orchestrator.run(root_agent, "What's my name?")
    print(f"Turn 2: {result2.final_output}")
    print("   ↪️  Assistant doesn't remember - no session used")
    
    # With session (automatic memory)
    print(f"\n✅ WITH Sessions (automatic memory):")
    session = SQLiteSession("comparison_demo", "comparison.db")
    
    result3 = await Orchestrator.run(root_agent, "My name is Alice", session=session)
    print(f"Turn 1: {result3.final_output}")
    
    result4 = await Orchestrator.run(root_agent, "What's my name?", session=session)
    print(f"Turn 2: {result4.final_output}")
    print("   ↪️  Assistant remembers - session automatically handles history!")
    
    return session

# Main execution function
async def main():
    """Run all basic session examples"""
    print("🧠 OpenAI Agents SDK - Basic Sessions Examples")
    print("=" * 60)
    
    await in_memory_session_example()
    await persistent_session_example()
    await multi_turn_conversation()
    await session_comparison()
    
    print("\n✅ Basic sessions examples completed!")
    print("Key concepts demonstrated:")
    print("  • In-memory sessions: SQLiteSession('context_id')")
    print("  • Persistent sessions: SQLiteSession('context_id', 'file.db')")
    print("  • Automatic memory: No manual .to_input_list() needed")
    print("  • Session vs no session: Memory comparison")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
