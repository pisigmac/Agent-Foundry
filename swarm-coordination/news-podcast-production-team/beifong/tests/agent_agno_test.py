from typing import Iterator
from agno.assistant import Assistant, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response
from dotenv import load_dotenv

load_dotenv()
assistant = Assistant(model=OpenAIChat(id="gpt-4o-mini"))
response: RunResponse = assistant.run("Tell me a 5 second short story about a robot")
response_stream: Iterator[RunResponse] = assistant.run("Tell me a 5 second short story about a lion", stream=True)
pprint_run_response(response, markdown=True)
pprint_run_response(response_stream, markdown=True)
