# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the LangChain agent:**
```bash
python langchain_agent.py <search query>
# e.g. python langchain_agent.py latest python version
```

**Run the OpenAI Agents SDK agent:**
```bash
python openai_agent.py <search query>
# e.g. python openai_agent.py latest python version
```

**Run the Anthropic SDK agent:**
```bash
python claude_agent.py <search query>
# e.g. python claude_agent.py latest python version
```

**Run all tests:**
```bash
pytest tests/test_agent.py
```

**Run a single test:**
```bash
pytest tests/test_agent.py::test_agent_output_is_printed_to_stdout
```

## Environment Setup

Requires a `.env` file (git-ignored) with:
```
OPENAI_API_KEY=...
SERPER_API_KEY=...
TAVILY_API_KEY=...
ANTHROPIC_API_KEY=...
```

All agents call `load_dotenv()` at startup — no manual export needed. `SERPER_API_KEY` is used by `langchain_agent.py` and `claude_agent.py`; `TAVILY_API_KEY` is used by `openai_agent.py`; `ANTHROPIC_API_KEY` is used by `claude_agent.py`.

## Architecture

`langchain_agent.py` is the entire application: a single script with no modules, classes, or helper functions. At invocation it:

1. Reads the query from CLI args (`sys.argv[1:]` joined with spaces)
2. Wraps `GoogleSerperAPIWrapper` as a LangChain `Tool`
3. Instantiates `ChatOpenAI` (GPT-4o-mini, temperature=0)
4. Runs a `ZERO_SHOT_REACT_DESCRIPTION` ReAct agent loop via `initialize_agent`
5. Injects today's date into the prompt and requests a 2–3 sentence answer
6. Prints `result["output"]` to stdout

The agent iterates Think → Search → Observe until it has enough information, using only search results (not pre-trained knowledge) to answer.

**Note:** `langchain_agent.py` imports from `langchain_classic.agents`, but `requirements.txt` lists `langchain` (not `langchain-classic`). If `initialize_agent` is missing after install, add `langchain-classic` to `requirements.txt`.

`openai_agent.py` is a second single-file agent using the OpenAI Agents SDK and Tavily for web search. It reads the query from CLI args, defines a `web_search` tool with `@function_tool`, and streams output token-by-token via `Runner.run_streamed()` + `result.stream_events()`. PyPI install name: `openai-agents`; import name: `agents` (i.e. `from agents import Agent, Runner`). The reference code uses `from openai_agents import ...` which is incorrect for the official package.

`claude_agent.py` is a third single-file agent using the Anthropic SDK (`claude-sonnet-4-6`) and Serper for web search. It runs a native tool-use agentic loop: on `stop_reason == "tool_use"`, it calls the Serper `/search` endpoint via `requests`, appends the result to `messages`, and loops; on `stop_reason == "end_turn"`, it prints the text response and exits.

## Testing Approach

Tests in `tests/test_agent.py` execute `langchain_agent.py` in two ways:

- **CLI guard tests** — run the script as a subprocess with no args; assert exit code 1 and usage message.
- **Happy-path tests** — use `runpy.run_path` to execute the script in-process with `sys.argv` patched and all LangChain components mocked (`GoogleSerperAPIWrapper`, `ChatOpenAI`, `initialize_agent`). No real API calls are made.

`AGENT_PATH` in `tests/test_agent.py` points to `langchain_agent.py`.
