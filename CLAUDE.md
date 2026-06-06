# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the agent:**
```bash
python agent.py <search query>
# e.g. python agent.py latest python version
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
```

`agent.py` calls `load_dotenv()` at startup — no manual export needed.

## Architecture

`agent.py` is the entire application: a single script with no modules, classes, or helper functions. At invocation it:

1. Reads the query from CLI args (`sys.argv[1:]` joined with spaces)
2. Wraps `GoogleSerperAPIWrapper` as a LangChain `Tool`
3. Instantiates `ChatOpenAI` (GPT-4o-mini, temperature=0)
4. Runs a `ZERO_SHOT_REACT_DESCRIPTION` ReAct agent loop via `initialize_agent`
5. Injects today's date into the prompt and requests a 2–3 sentence answer
6. Prints `result["output"]` to stdout

The agent iterates Think → Search → Observe until it has enough information, using only search results (not pre-trained knowledge) to answer.

**Note:** `agent.py` imports from `langchain_classic.agents`, but `requirements.txt` lists `langchain` (not `langchain-classic`). If `initialize_agent` is missing after install, add `langchain-classic` to `requirements.txt`.

## Testing Approach

Tests in `tests/test_agent.py` execute `agent.py` in two ways:

- **CLI guard tests** — run the script as a subprocess with no args; assert exit code 1 and usage message.
- **Happy-path tests** — use `runpy.run_path` to execute the script in-process with `sys.argv` patched and all LangChain components mocked (`GoogleSerperAPIWrapper`, `ChatOpenAI`, `initialize_agent`). No real API calls are made.

`starter.py` is an incomplete reference snippet for the Serper HTTP API (has a syntax error on line 9) and is not part of the application.
