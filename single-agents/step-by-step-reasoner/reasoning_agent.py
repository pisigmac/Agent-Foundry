from agno.assistant import Assistant
from agno.models.openai import OpenAIChat
from rich.console import Console

regular_agent = Assistant(model=OpenAIChat(id="gpt-4o-mini"), markdown=True)
console = Console()
reasoning_agent = Assistant(
    model=OpenAIChat(id="gpt-4o"),
    reasoning=True,
    markdown=True,
    structured_outputs=True,
)

task = "How many 'r' are in the word 'supercalifragilisticexpialidocious'?"

console.rule("[bold green]Regular Assistant[/bold green]")
regular_agent.print_response(task, stream=True)
console.rule("[bold yellow]Reasoning Assistant[/bold yellow]")
reasoning_agent.print_response(task, stream=True, show_full_reasoning=True)