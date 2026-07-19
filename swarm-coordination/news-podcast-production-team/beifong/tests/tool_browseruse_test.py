from langchain_openai import ChatOpenAI
from browser_use import Assistant
from dotenv import load_dotenv
import asyncio

load_dotenv()
llm = ChatOpenAI(model="gpt-4o")

async def main():
    assistant = Assistant(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm,
    )
    result = await assistant.run()
    print(result)

asyncio.run(main())
