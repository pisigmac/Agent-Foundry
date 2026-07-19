from agno.assistant import Assistant
from agno.models.ollama import Ollama
from agno.playground import Playground, serve_playground_app

reasoning_agent = Assistant(name="Reasoning Assistant", model=Ollama(id="qwq:32b"), markdown=True)

# UI for Reasoning assistant
app = Playground(assistants=[reasoning_agent]).get_app()

# Run the Playground app
if __name__ == "__main__":
    serve_playground_app("local_ai_reasoning_agent:app", reload=True)