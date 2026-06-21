import sys
import os
import requests
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python claude_agent.py <search query>")
    sys.exit(1)

query = " ".join(sys.argv[1:])

client = anthropic.Anthropic()

tools = [
    {
        "name": "web_search",
        "description": "Search the web for current information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    }
]


def serper_search(q):
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"], "Content-Type": "application/json"},
        json={"q": q, "num": 5},
    )
    data = response.json()
    lines = []
    if data.get("answerBox"):
        ab = data["answerBox"]
        answer = ab.get("answer") or ab.get("snippet") or ""
        if answer:
            lines.append(f"Answer box: {answer}")
    for r in data.get("organic", [])[:5]:
        title = r.get("title", "")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        lines.append(f"- {title} ({link}): {snippet}")
    return "\n".join(lines) if lines else "No results found."


today = date.today().strftime("%B %d, %Y")
system_prompt = (
    f"Today is {today}. Use only the web search results to answer. "
    "Answer concisely in 2-3 sentences."
)
messages = [{"role": "user", "content": query}]

MAX_ITERATIONS = 5
iterations = 0

while iterations < MAX_ITERATIONS:
    iterations += 1
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "end_turn":
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break
    elif response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = serper_search(block.input["query"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})
else:
    print("Could not complete the search within the iteration limit.")
