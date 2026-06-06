import sys
import os
import asyncio

from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from tavily import TavilyClient
from agents import Agent, Runner, function_tool

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python openai_agent.py <search query>")
    sys.exit(1)

query = " ".join(sys.argv[1:])

tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@function_tool
def web_search(query: str) -> str:
    """Searches the live web to find up-to-date information for answering questions."""
    try:
        response = tavily_client.search(query=query, max_results=3, topic="general")
        results = []
        for item in response.get("results", []):
            results.append(f"Source: {item['url']}\nContent: {item['content']}\n")
        return "\n---\n".join(results) if results else "No relevant results found."
    except Exception as e:
        return f"Error executing search: {str(e)}"


search_agent = Agent(
    name="FastWebSearcher",
    model="gpt-4o-mini",
    instructions=(
        "You are a lightning-fast web research assistant. Your goal is to give accurate, "
        "concise answers using the provided web_search tool. "
        "Always cite your sources using markdown links. Do not waste words on pleasantries; "
        "get straight to the facts."
    ),
    tools=[web_search],
)


async def main():
    print("\n[Thinking and Searching...]\n")
    result = Runner.run_streamed(search_agent, input=query)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
        elif event.type == "run_item_stream_event" and event.item.type == "tool_call_item":
            print(f"\n[Invoking tool: {event.item.raw_item.name}...]", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
