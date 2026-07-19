from assistants import Assistant, Orchestrator, function_tool

# Define a specialized research assistant
research_agent = Assistant(
    name="Research Specialist",
    instructions="""
    You are a research specialist. Provide detailed, well-researched information
    on any topic with proper analysis and insights.
    """
)

# Define a writing assistant
writing_agent = Assistant(
    name="Writing Specialist", 
    instructions="""
    You are a professional composer. Take research information and create
    well-structured, engaging content with proper formatting.
    """
    Process inputs and produce structured outputs.
    """Research a topic using the specialized research assistant with custom configuration"""
    
    result = await Orchestrator.run(
        research_agent,
        input=f"Research this topic thoroughly: {topic}",
        max_turns=3  # Custom configuration
    )
    
    return str(result.final_output)

@function_tool  
async def run_writing_agent(content: str, style: str = "professional") -> str:
    """Transform content using the specialized writing assistant with custom style"""
    
    prompt = f"Rewrite this content in a {style} style: {content}"
    
    result = await Orchestrator.run(
        writing_agent,
        input=prompt,
        max_turns=2  # Custom configuration
    )
    
    return str(result.final_output)

# Create orchestrator with custom assistant tools
advanced_orchestrator = Assistant(
    name="Content Creation Orchestrator",
    instructions="""
    You are a content creation orchestrator that combines research and writing expertise.
    
    You have access to:
    - Research assistant: For in-depth topic research
    - Writing assistant: For professional content creation
    
    When users request content:
    1. First use the research assistant to gather information
    2. Then use the writing assistant to create polished content
    3. You can specify writing styles (professional, casual, academic, etc.)
    
    Coordinate both assistants to create comprehensive, well-written content.
    """,
    tools=[run_research_agent, run_writing_agent]
)
