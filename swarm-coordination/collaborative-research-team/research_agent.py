# Import the required libraries
import streamlit as st
from agno.assistant import Assistant
from agno.run.assistant import RunOutput
from agno.models.openai import OpenAIChat
from agno.squad import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
import os

# Initialize the web interface
st.title("Multi-Assistant AI Researcher 🔍🤖")
st.caption("This app allows you to research top stories and users on HackerNews and write blogs, reports and social posts.")

# Prompt for authentication credentials
openai_api_key = st.text_input("OpenAI API Key", type="password")
os.environ["OPENAI_API_KEY"] = openai_api_key

if openai_api_key:
    hn_researcher = Assistant(
        name="HackerNews Researcher",
        model=OpenAIChat(id="gpt-4o-mini"),
        role="Gets top stories from hackernews.",
        tools=[HackerNewsTools()],
    )

    web_searcher = Assistant(
        name="Web Searcher",
        model=OpenAIChat(id="gpt-4o-mini"),
        role="Searches the web for information on a topic",
        tools=[DuckDuckGoTools()],
        add_datetime_to_context=True,
    )

    article_reader = Assistant(
        name="Article Reader",
        model=OpenAIChat(id="gpt-4o-mini"),
        role="Reads articles from URLs.",
        tools=[Newspaper4kTools()],
    )

    hackernews_team = Team(
        name="HackerNews Team",
        model=OpenAIChat(id="gpt-4o-mini"),
        members=[hn_researcher, web_searcher, article_reader],
        instructions=[
            "First, search hackernews for what the user is asking about.",
            "Then, ask the article reader to read the links for the stories to get more information.",
            "Important: you must provide the article reader with the links to read.",
            "Then, ask the web searcher to search for each story to get more information.",
            "Finally, provide a thoughtful and engaging summary.",
        ],
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
    )

    # Input field for the report query
    query = st.text_input("Enter your report query")

    if query:
        # Get the response from the assistant
        response: RunOutput = hackernews_team.run(query, stream=False)
        st.write(response.content)