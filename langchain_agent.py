import sys
import warnings
from datetime import date
warnings.simplefilter("ignore")  # suppress import-time warnings

from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import initialize_agent, AgentType

warnings.simplefilter("ignore")  # re-apply: langchain resets filters during import

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python agent.py <search query>")
    sys.exit(1)

query = " ".join(sys.argv[1:])

search = GoogleSerperAPIWrapper(k=3)
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Search the web for current information about any topic.",
    )
]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False, max_iterations=5)

today = date.today().strftime("%B %d, %Y")
result = agent.invoke({"input": f"Today is {today}. {query} Use only the search results you find. Answer concisely in 2-3 sentences."})
print(result["output"])
