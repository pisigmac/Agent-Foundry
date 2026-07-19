from agno.assistant import Assistant
from agno.squad import Team
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.os import AgentOS

# Setup database for storage
db = SqliteDb(db_file="assistants.db")

web_agent = Assistant(
    name="Web Assistant",
    role="Search the web for information",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    db=db,
    add_history_to_context=True,
    markdown=True,
)

finance_agent = Assistant(
    name="Finance Assistant",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(include_tools=["get_current_stock_price", "get_analyst_recommendations", "get_company_info", "get_company_news"])],
    instructions=["Always use tables to display data"],
    db=db,
    add_history_to_context=True,
    markdown=True,
)

agent_team = Team(
    name="Assistant Team (Web+Finance)",
    model=OpenAIChat(id="gpt-4o"),
    members=[web_agent, finance_agent],
    debug_mode=True,
    markdown=True,
)

agent_os = AgentOS(teams=[agent_team])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="finance_agent_team:app", reload=True)