# Agent Web Search

Three minimal CLI agents that answer questions using live web search results — no pre-trained knowledge used for the answer.

## Agents

| File | Framework | Search API | LLM |
|------|-----------|------------|-----|
| `langchain_agent.py` | LangChain (ReAct / ZERO_SHOT_REACT_DESCRIPTION) | Serper | GPT-4o-mini |
| `openai_agent.py` | OpenAI Agents SDK | Tavily | GPT-4o-mini |
| `claude_agent.py` | Anthropic SDK | Serper | claude-sonnet-4-6 |

All agents read a query from the command line, search the web, and print a concise answer to stdout.

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

> `langchain_agent.py` also requires `langchain-classic` (provides `initialize_agent`). If it's missing after install, add it manually:
> ```bash
> pip install langchain-classic
> ```

**2. Create a `.env` file** in the project root:

```
OPENAI_API_KEY=...
SERPER_API_KEY=...
TAVILY_API_KEY=...
ANTHROPIC_API_KEY=...
```

- `SERPER_API_KEY` — used by `langchain_agent.py` and `claude_agent.py` ([serper.dev](https://serper.dev))
- `TAVILY_API_KEY` — used by `openai_agent.py` ([tavily.com](https://tavily.com))
- `OPENAI_API_KEY` — used by `langchain_agent.py` and `openai_agent.py`
- `ANTHROPIC_API_KEY` — used by `claude_agent.py` ([console.anthropic.com](https://console.anthropic.com))

## Usage

**LangChain agent:**

```bash
python langchain_agent.py <search query>
# e.g.
python langchain_agent.py latest python version
```

**OpenAI Agents SDK agent** (streams output token-by-token):

```bash
python openai_agent.py <search query>
# e.g.
python openai_agent.py who won the last world cup
```

**Anthropic SDK agent:**

```bash
python claude_agent.py <search query>
# e.g.
python claude_agent.py latest python version
```

All scripts exit with code 1 and print a usage message if no query is provided.

## Running Tests

Tests cover `langchain_agent.py` only (CLI guard and mocked happy-path; no real API calls made).

```bash
# Run all tests
pytest tests/test_agent.py

# Run a single test
pytest tests/test_agent.py::test_agent_output_is_printed_to_stdout
```

## How It Works

### `langchain_agent.py` — LangChain ReAct loop

1. Reads query from `sys.argv`
2. Wraps `GoogleSerperAPIWrapper` as a LangChain `Tool`
3. Runs a `ZERO_SHOT_REACT_DESCRIPTION` agent loop (Think → Search → Observe) until it has enough information
4. Injects today's date into the prompt and requests a 2–3 sentence answer
5. Prints `result["output"]` to stdout

### `openai_agent.py` — OpenAI Agents SDK

1. Reads query from `sys.argv`
2. Defines a `web_search` tool using `@function_tool` backed by the Tavily API
3. Runs the agent with `Runner.run_streamed()` and streams output token-by-token via `stream_events()`
4. Prints tool invocations and the final answer to stdout as they arrive

### `claude_agent.py` — Anthropic SDK native tool-use loop

1. Reads query from `sys.argv`
2. Declares a `web_search` tool with a JSON schema accepted by the Anthropic API
3. Loops: on `stop_reason == "tool_use"`, calls the Serper search API via `requests` and feeds the result back into `messages`; on `stop_reason == "end_turn"`, prints the text response
4. Uses `claude-sonnet-4-6` with no framework abstraction

## Project Structure

```
agent-web-search/
├── langchain_agent.py  # LangChain + Serper agent
├── openai_agent.py     # OpenAI Agents SDK + Tavily agent
├── claude_agent.py     # Anthropic SDK + Serper agent
├── requirements.txt
└── tests/
    └── test_agent.py   # pytest tests for langchain_agent.py
```
