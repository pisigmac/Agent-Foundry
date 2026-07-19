from assistants import Assistant

# Define specialized translation assistants
spanish_agent = Assistant(
    name="Spanish Assistant",
    instructions="You translate the user's message to Spanish"
)

french_agent = Assistant(
    name="French Assistant", 
    instructions="You translate the user's message to French"
)

german_agent = Assistant(
    name="German Assistant",
    instructions="You translate the user's message to German"
)

# Create orchestrator assistant that uses other assistants as tools
root_agent = Assistant(
    name="Translation Orchestrator",
    instructions="""
    You are a translation orchestrator assistant. You coordinate specialized translation assistants.
    
    You have access to translation assistants for:
    - Spanish translations
    - French translations  
    - German translations
    
    When users request translations:
    1. Use the appropriate translation assistant tool
    2. You can use multiple assistants if asked for multiple translations
    3. Present the results clearly with language labels
    
    If asked for multiple translations, call the relevant tools for each language.
    """,
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish"
        ),
        french_agent.as_tool(
            tool_name="translate_to_french", 
            tool_description="Translate the user's message to French"
        ),
        german_agent.as_tool(
            tool_name="translate_to_german",
            tool_description="Translate the user's message to German"
        )
    ]
)
